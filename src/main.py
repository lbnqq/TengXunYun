import os
import sys
import json
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import necessary modules from our project
from core.agent.agent_orchestrator import AgentOrchestrator
from llm_clients.xingcheng_llm import XingchengLLMClient

# Load environment variables from .env file
load_dotenv()

def main():
    """Main function to run the document agent."""
    print("Initializing Office Document Agent...")

    # Configuration
    XINGCHENG_API_KEY = os.getenv("XINGCHENG_API_KEY")
    XINGCHENG_API_SECRET = os.getenv("XINGCHENG_API_SECRET")
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "x1")
    KB_PATH = "src/core/knowledge_base"

    if not XINGCHENG_API_KEY:
        print("Warning: Xingcheng API key not found. Please configure XINGCHENG_API_KEY in .env file")
        print("You can get your API key from: https://console.xfyun.cn/services/bmx1")
        return

    try:
        # Initialize Xingcheng X1 LLM Client
        print(f"Initializing with LLM Model: {LLM_MODEL_NAME}")
        llm_client = XingchengLLMClient(
            api_key=XINGCHENG_API_KEY,
            api_secret=XINGCHENG_API_SECRET,
            model_name=LLM_MODEL_NAME
        )

        # Initialize the Agent Orchestrator
        orchestrator = AgentOrchestrator(llm_client=llm_client, kb_path=KB_PATH)

        # Create a dummy document file to test the parser
        dummy_doc_path = "sample_document.txt"
        with open(dummy_doc_path, "w", encoding="utf-8") as f:
            f.write("This is a sample document to test the agent.\n")
            f.write("It contains some general text that needs analysis and processing.\n")
            f.write("It's a crucial piece of information for the team.\n")

        print(f"\nStarting document processing for: {dummy_doc_path}")
        processing_result = orchestrator.process_document(file_path=dummy_doc_path)

        print("\n--- Overall Processing Result ---")
        print(json.dumps(processing_result, indent=2))
        print("--- End Overall Processing Result ---")

        # Clean up dummy file
        if os.path.exists(dummy_doc_path):
            os.remove(dummy_doc_path)
            print(f"\nCleaned up dummy file: {dummy_doc_path}")

    except Exception as e:
        print(f"Error initializing or running the agent: {e}")
        print("Please check your API configuration and network connection.")

if __name__ == "__main__":
    # Ensure output directory exists for document_output_tool
    if not os.path.exists("output"):
        os.makedirs("output")
    main() 