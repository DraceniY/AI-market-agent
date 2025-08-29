import json
import logging
from functools import partial
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from typing import Dict, Any, Optional
import os

from web_search import (
    advanced_competitor_search,
    advanced_sentiment_search,
    advanced_product_search,
)
from settings import call_agent, run_orchestrator_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#  OpenTelemetry imports is oprional if not set
try:
    from opentelemetry import baggage, context

    OPENTELEMETRY_AVAILABLE = True
    logger.info("OpenTelemetry available ")
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    logger.info("OpenTelemetry not available, we are running without telemetry")


def simple_extract_json(text: str) -> Dict[str, Any]:
    """
    Simplified JSON extraction - much easier to understand
    """
    try:
        # we look for ```json blocks
        if "```json" in text.lower():
            start = text.lower().find("```json") + 7
            end = text.find("```", start)
            if end != -1:
                json_text = text[start:end].strip()
            else:
                json_text = text[start:].strip()

            return json.loads(json_text)

        # or we find any JSON-like structure
        start = text.find("{")
        if start == -1:
            return {"error": "No JSON found", "raw_text": text}

        brace_count = 0
        for i, char in enumerate(text[start:], start):
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0:
                    json_text = text[start : i + 1]
                    return json.loads(json_text)

        return {"error": "Could not parse JSON", "raw_text": text}

    except json.JSONDecodeError as e:
        return {"error": f"JSON decode error: {str(e)}", "raw_text": text}
    except Exception as e:
        return {"error": f"Extraction error: {str(e)}", "raw_text": text}


def _initialize_agents() -> Dict[str, Any]:
    """Initialize specialized agents with specialized prompts"""

    try:
        # Product Intelligence Agent
        product_agent = call_agent(
            "PRODUCT_DATA_PROMPT", advanced_product_search, "product-agent"
        )

        # Competitive Intelligence Agent
        competitor_agent = call_agent(
            "COMPETITOR_ANALYST_PROMPT", advanced_competitor_search, "competitor-agent"
        )

        # Customer Sentiment Agent
        sentiment_agent = call_agent(
            "SENTIMENT_ANALYST_PROMPT", advanced_sentiment_search, "sentiment-agent"
        )

        return {
            "product": product_agent,
            "competitor": competitor_agent,
            "sentiment": sentiment_agent,
        }
    except Exception as e:
        logger.error(f"Failed to initialize agents: {str(e)}")
        raise


def _execute_agent(agent_name: str, query: str, agents_dict: Dict) -> Dict[str, Any]:
    """Execute individual agent and extract JSON"""

    try:
        agent = agents_dict[agent_name]
        response = agent(query)

        # Extract content or text is there is attribut on the outpur
        if hasattr(response, "content"):
            response_text = response.content
        elif hasattr(response, "text"):
            response_text = response.text
        else:
            response_text = str(response)

        logger.debug(f"{agent_name} raw response: {response_text[:200]}...")

        # Extract JSON using simplified method
        extracted_json = simple_extract_json(response_text)

        # Add metadata
        extracted_json["agent_name"] = agent_name
        extracted_json["raw_response"] = (
            response_text if len(response_text) < 1000 else response_text[:1000] + "..."
        )

        return extracted_json

    except Exception as e:
        logger.error(f"Error executing {agent_name} agent: {str(e)}")
        return {
            "error": str(e),
            "agent": agent_name,
            "raw_response": "Failed to get response",
        }


def _run_specialist_agents(product_query: str) -> Dict[str, Any]:
    """Run specialist agents in parallel using partial functions"""

    # Initialize agents once
    agents_dict = _initialize_agents()

    # Create partial function with agents_dict
    execute_agent_with_agents = partial(_execute_agent, agents_dict=agents_dict)

    tasks = [
        (
            "product",
            f"Analyze product data for {product_query}. Focus on pricing, availability, and popularity.",
        ),
        (
            "competitor",
            f"Analyze competitive landscape for {product_query}. Identify competitors and market positioning.",
        ),
        (
            "sentiment",
            f"Analyze customer sentiment for {product_query}. Extract themes from reviews and feedback.",
        ),
    ]

    results = {}

    with ThreadPoolExecutor(max_workers=3) as executor:
       
        future_to_agent = {
            executor.submit(execute_agent_with_agents, agent_name, query): agent_name
            for agent_name, query in tasks
        }

        for future in as_completed(future_to_agent):
            agent_name = future_to_agent[future]
            try:
                result = future.result()
                results[agent_name] = result
                logger.info(f"✅ {agent_name.title()} agent completed successfully")
            except Exception as e:
                logger.error(f"❌ {agent_name.title()} agent failed: {str(e)}")
                results[agent_name] = {"error": str(e), "agent": agent_name}

    return results


def _run_orchestrator(
    product_query: str, specialist_results: Dict[str, Any]
) -> Dict[str, Any]:
    """Run orchestrator agent to synthesize results"""

    logger.info("🔄 Running orchestrator synthesis...")

    # Prepare orchestrator input
    orchestrator_input = f"""
MULTI-AGENT ANALYSIS SYNTHESIS REQUEST

PRODUCT: {product_query}

SPECIALIST AGENT RESULTS:

=== PRODUCT INTELLIGENCE ===
{json.dumps(specialist_results.get('product', {}), indent=2)}

=== COMPETITIVE INTELLIGENCE ===
{json.dumps(specialist_results.get('competitor', {}), indent=2)}

=== CUSTOMER SENTIMENT ===
{json.dumps(specialist_results.get('sentiment', {}), indent=2)}

Please synthesize these specialist findings into a comprehensive strategic analysis.
"""

    try:
        # Use the orchestrator function from settings
        response_text = run_orchestrator_query(orchestrator_input)

        # Extract JSON using simplified method
        orchestrated_json = simple_extract_json(response_text)
        orchestrated_json["orchestrator_raw_response"] = (
            response_text[:1000] + "..." if len(response_text) > 1000 else response_text
        )

        logger.info("✅ Orchestrator synthesis completed")
        return orchestrated_json

    except Exception as e:
        logger.error(f"❌ Orchestrator failed: {str(e)}")
        return {"error": str(e), "agent": "orchestrator"}


def set_session_context(session_id: str) -> Optional[object]:
    """Set the session ID in OpenTelemetry baggage for trace correlation (optional)"""

    if not OPENTELEMETRY_AVAILABLE:
        logger.debug(
            f"OpenTelemetry not available for the session ID '{session_id}' logged only"
        )
        return None

    try:
        ctx = baggage.set_baggage("session.id", session_id)
        ctx = baggage.set_baggage("experiment.id", "ecommerce-agent-v2")
        ctx = baggage.set_baggage("conversation.topic", "business-ecommerce")
        token = context.attach(ctx)
        logger.info(f"Session ID '{session_id}' attached to telemetry context")
        return token
    except Exception as e:
        logger.warning(
            f"Failed to set telemetry context: {str(e)}. Continuing without telemetry."
        )
        return None


def detach_session_context(context_token: Optional[object], session_id: str) -> None:
    """Detach OpenTelemetry context (optional)"""

    if not OPENTELEMETRY_AVAILABLE or context_token is None:
        logger.debug(f"Session context for '{session_id}' - no telemetry to detach")
        return

    try:
        context.detach(context_token)
        logger.info(f"Session context for '{session_id}' detached")
    except Exception as e:
        logger.warning(f"Failed to detach telemetry context: {str(e)}")


def run_orchestrated_analysis(
    product_query: str, session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Run coordinated multi-agent analysis - Main function"""

    if session_id is None:
        session_id = f"session-{pd.Timestamp.now().strftime('%Y%m%d-%H%M%S')}"

    logger.info(
        f"🚀 Starting orchestrated analysis for: {product_query} (Session: {session_id})"
    )

    # Set telemetry context (optional)
    context_token = set_session_context(session_id)

    try:
        # Step 1: Run specialist agents in parallel
        specialist_results = _run_specialist_agents(product_query)

        # Step 2: Run orchestrator with specialist results
        orchestrated_result = _run_orchestrator(product_query, specialist_results)

        # Step 3: Combine all results
        comprehensive_report = {
            "query": product_query,
            "session_id": session_id,
            "timestamp": pd.Timestamp.now().isoformat(),
            "specialist_agents": specialist_results,
            "orchestrated_analysis": orchestrated_result,
            "execution_summary": {
                "agents_completed": len(
                    [
                        result
                        for result in specialist_results.values()
                        if not result.get("error")
                    ]
                ),
                "total_agents": len(specialist_results),
                "orchestration_success": not orchestrated_result.get("error", False),
                "telemetry_enabled": OPENTELEMETRY_AVAILABLE,
                "telemetry_context_set": context_token is not None,
            },
        }

        logger.info("✅ Orchestrated analysis completed successfully")
        return comprehensive_report

    except Exception as e:
        logger.error(f"❌ Analysis failed: {str(e)}")
        return {
            "query": product_query,
            "session_id": session_id,
            "timestamp": pd.Timestamp.now().isoformat(),
            "error": str(e),
            "execution_summary": {
                "agents_completed": 0,
                "total_agents": 3,
                "orchestration_success": False,
                "telemetry_enabled": OPENTELEMETRY_AVAILABLE,
                "telemetry_context_set": False,
            },
        }
    finally:
        # Detach context when done (if it was set)
        detach_session_context(context_token, session_id)


# Test function without telemetry
def run_analysis_simple(product_query: str) -> Dict[str, Any]:
    """Simple analysis runner without telemetry requirements"""

    logger.info(f"🚀 Starting simple analysis for: {product_query}")

    try:
        # Step 1: Run specialist agents
        specialist_results = _run_specialist_agents(product_query)

        # Step 2: Run orchestrator
        orchestrated_result = _run_orchestrator(product_query, specialist_results)

        # Step 3: Combine results
        return {
            "query": product_query,
            "timestamp": pd.Timestamp.now().isoformat(),
            "specialist_agents": specialist_results,
            "orchestrated_analysis": orchestrated_result,
            "execution_summary": {
                "agents_completed": len(
                    [
                        result
                        for result in specialist_results.values()
                        if not result.get("error")
                    ]
                ),
                "total_agents": len(specialist_results),
                "orchestration_success": not orchestrated_result.get("error", False),
                "execution_mode": "simple",
            },
        }

    except Exception as e:
        logger.error(f"❌ Simple analysis failed: {str(e)}")
        return {
            "query": product_query,
            "timestamp": pd.Timestamp.now().isoformat(),
            "error": str(e),
            "execution_summary": {
                "agents_completed": 0,
                "total_agents": 3,
                "orchestration_success": False,
                "execution_mode": "simple_failed",
            },
        }


# Environment variable configuration for OpenTelemetry
def configure_telemetry_environment():
    """Configure environment variables for OpenTelemetry (optional)"""

    # Set default values if not already set
    telemetry_config = {
        "OTEL_TRACES_EXPORTER": "console",  # Export to console instead of HTTP
        "OTEL_METRICS_EXPORTER": "console",
        "OTEL_LOGS_EXPORTER": "console",
        "OTEL_SERVICE_NAME": "ecommerce-multi-agent",
        "OTEL_RESOURCE_ATTRIBUTES": "service.version=1.0.0,deployment.environment=development",
    }

    for key, value in telemetry_config.items():
        if key not in os.environ:
            os.environ[key] = value

    logger.info("Telemetry environment configured for console output")


if __name__ == "__main__":
    # Test the system
    configure_telemetry_environment()

    # Test both modes
    print("Testing simple mode (no telemetry):")
    result1 = run_analysis_simple("Test Product")
    print(f"Simple mode result: {result1['execution_summary']}")

    print("\nTesting with optional telemetry:")
    result2 = run_orchestrated_analysis("Test Product", "test-session-123")
    print(f"Telemetry mode result: {result2['execution_summary']}")
