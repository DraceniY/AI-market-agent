from functools import lru_cache
import os
import sys
import configparser
from typing import Callable
from strands import Agent
from strands_tools import calculator
from strands.models import BedrockModel
from strands.handlers.callback_handler import PrintingCallbackHandler
from strands.agent.conversation_manager import SummarizingConversationManager
from strands.session.file_session_manager import FileSessionManager
import logging

logging.basicConfig(level=logging.INFO)

# Configure the root strands logger
logging.getLogger("strands").setLevel(logging.DEBUG)
# Enable DEBUG logs for the tool registry only
logging.getLogger("strands.tools.registry").setLevel(logging.DEBUG)
# Set WARNING level for model interactions
logging.getLogger("strands.models").setLevel(logging.WARNING)
# Add a handler to see the logs
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def _get_config():
    """
    Parse config and get the fields.
    Returns:
        config object containing fields to parse.
    """
    src_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
    config = configparser.ConfigParser()
    config.read(f"{src_directory}/config.ini")
    return config


@lru_cache(maxsize=None)
def _get_bedrock_model():
    """Initialize Bedrock model with config parameters"""
    model_id = os.getenv(
        "BEDROCK_MODEL_ID", str(_get_config()["MODEL_PARAM"]["BEDROCK_MODEL_ID"])
    )
    region = os.getenv(
        "AWS_DEFAULT_REGION", str(_get_config()["MODEL_PARAM"]["MODEL_REGION"])
    )

    try:
        bedrock_model = BedrockModel(
            model_id=model_id,
            region_name=region,
            temperature=float(_get_config()["MODEL_PARAM"]["MODEL_TEMPERATURE"]),
            max_tokens=int(_get_config()["MODEL_PARAM"]["MAXIMUM_TOKENS"]),
        )
        logger.info(
            f"Successfully initialized Bedrock model: {model_id} in region: {region}"
        )
        return bedrock_model
    except Exception as e:
        logger.error(f"Failed to initialize Bedrock model: {str(e)}")
        logger.error(
            "Please ensure you have proper AWS credentials configured and access to the Bedrock model"
        )
        raise


# Initialize the model (cached)
bedrock_model = _get_bedrock_model()


@lru_cache(maxsize=None)
def _call_agent(
    agent_name: str, advanced_search: Callable[[str], str], session_id: str
) -> Agent:
    """Initialize specialized agents with specific prompts - Fixed function name and return type"""

    return Agent(
        model=bedrock_model,
        system_prompt=str(_get_config()["PROMPT"][agent_name]),
        tools=[advanced_search, calculator],
        conversation_manager=SummarizingConversationManager(
            summary_ratio=float(_get_config()["MODEL_PARAM"]["SUMMARY_RATIO"])
        ),
        callback_handler=PrintingCallbackHandler(),
        trace_attributes={
            "user.id": f"{agent_name}_YD",
            "tags": ["Strands", "Observability"],
        },
        session_manager=FileSessionManager(
            session_id=session_id, storage_dir="./sessions"
        ),
    )


@lru_cache(maxsize=None)
def _initialize_orchestrator() -> Agent:
    """Initialize orchestrator agent - Fixed function name"""

    return Agent(
        model=bedrock_model,
        system_prompt=str(_get_config()["PROMPT"]["ORCHESTRATOR_PROMPT"]),
        callback_handler=PrintingCallbackHandler(),  # this is for real-time monitoring during an agent's lifecycle
        conversation_manager=SummarizingConversationManager(
            summary_ratio=float(_get_config()["MODEL_PARAM"]["SUMMARY_RATIO"])
        ),
        tools=[calculator],
        session_manager=FileSessionManager(
            session_id="orchestrator", storage_dir="./sessions"
        ),
    )


# Convenience functions for external use
def call_agent(
    agent_name: str, advanced_search: Callable[[str], str], session_id: str
) -> Agent:
    """Public interface for creating agents"""
    return _call_agent(agent_name, advanced_search, session_id)


def initialize_orchestrator() -> Agent:
    """Public interface for creating orchestrator"""
    return _initialize_orchestrator()


def run_orchestrator_query(query: str) -> str:
    """Run orchestrator with a direct query"""
    orchestrator = _initialize_orchestrator()
    response = orchestrator(query)

    # Extract response text
    if hasattr(response, "content"):
        return response.content
    elif hasattr(response, "text"):
        return response.text
    else:
        return str(response)
