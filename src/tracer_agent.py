import os
import sys
from strands import Agent
from strands.models import BedrockModel
from pathlib import Path 
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO)

# Add a handler to see the logs
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
def get_run_file():
    src_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
    folder = Path(f"{src_directory}/../logs/") 
    files = [f for f in folder.iterdir() if f.is_file()]

    if not files:
        print("No files found in folder.")
    else:
        # Pick the most recently modified file
        latest_file = max(files, key=lambda f: f.stat().st_mtime)

    # Read its contents (text mode)
    with latest_file.open("r", encoding="utf-8") as f:
        contents = f.read()

    return contents
def get_bedrock_model():
    model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")
    region = os.getenv("AWS_DEFAULT_REGION", "us-west-2")

    try:
        bedrock_model = BedrockModel(
            model_id=model_id,
            region_name=region,
            temperature=0.0,
            max_tokens=1024
        )
        logger.info(f"Successfully initialized Bedrock model: {model_id} in region: {region}")
        return bedrock_model
    except Exception as e:
        logger.error(f"Failed to initialize Bedrock model: {str(e)}")
        logger.error("Please ensure you have proper AWS credentials configured and access to the Bedrock model")
        raise
def get_evaluation():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Initialize the model
    bedrock_model = get_bedrock_model()
    # Create agent (tracing will be enabled automatically)
    log_info = get_run_file()
    agent = Agent(
        model=bedrock_model,
        system_prompt="You are a helpful AI assistant that : - Track the entire agent lifecycle: From initial prompt to final response \n- Analyze tool execution\nMeasure performance\n-Debug complex workflows",
        tools=[log_info]
    )

    response = agent("Give me insights on monitoring, observability, and scaling a multi-agent system in production.")

    if hasattr(response, "content"):
        result= response.content
    elif hasattr(response, "text"):
        result= response.text
    else:
        result= str(response)
    
    output_dir = Path("evaluation")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"evaluation_{timestamp}.txt"

    with output_file.open("w", encoding="utf-8") as f:
        f.write(result)

    print(f"✅ Saved evaluation to {output_file}")
    return result


def main():
    _ = get_evaluation()
    print("\n--- Agent Result ---\n")
    

if __name__ == "__main__":
    main()
