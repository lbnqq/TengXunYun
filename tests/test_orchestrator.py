import pytest
import os
import json

# Import necessary components from our project
from src.core.agent.agent_orchestrator import AgentOrchestrator
from src.core.guidance.scenario_inference import MockLLMClient

# Mock LLM Client for testing orchestrator logic specifically
class MockLLMClientForTests(MockLLMClient):
    def generate(self, prompt: str) -> str:
        print(f"--- Test LLM Generating Response ---\nPrompt: {prompt[:100]}...\n---")
        if "You are a smart document analysis assistant." in prompt:
            return json.dumps({
                "inferred_scenario": "Technical Report",
                "supporting_evidence": "contains 'performance metrics', 'algorithm analysis'",
                "inferred_reporter_role": "Lead Engineer",
                "inferred_reader_role": "Technical Team & CTO"
            })
        elif "You are acting as a 'Technical Reviewer'" in prompt:
            return json.dumps({
                "comments": [
                    {"severity": "high", "comment": "Performance issue found.", "area": "Performance"},
                    {"severity": "medium", "comment": "Code clarity could be improved.", "area": "Code Style"}
                ]
            })
        elif "You are a facilitator for a document review meeting." in prompt:
            return json.dumps({
                "meeting_summary": "Key performance issues were discussed.",
                "discussion_points": ["Performance bottlenecks"],
                "action_items": [{"assignee": "Lead Engineer", "task": "Optimize performance."}]
            })
        else:
            return json.dumps({"message": "Mock LLM response for tests"})

@pytest.fixture(scope="module")
def mock_llm_client():
    return MockLLMClientForTests()

@pytest.fixture(scope="module")
def orchestrator(mock_llm_client):
    kb_path = "src/core/knowledge_base"
    return AgentOrchestrator(llm_client=mock_llm_client, kb_path=kb_path)

@pytest.fixture(autouse=True)
def setup_dummy_doc(tmp_path):
    # Create a dummy document for tests
    dummy_doc_path = tmp_path / "sample_test_doc.txt"
    dummy_doc_path.write_text("This is a sample document for testing purposes.\nIt contains relevant keywords.\n")
    return str(dummy_doc_path)

def test_orchestrator_init(orchestrator):
    """Test if the orchestrator initializes correctly."""
    assert isinstance(orchestrator, AgentOrchestrator)
    assert hasattr(orchestrator, 'tools')
    assert hasattr(orchestrator, 'scenario_inference_module')

def test_process_document_workflow(orchestrator, setup_dummy_doc):
    """
    Test the end-to-end processing workflow of the orchestrator.
    This test simulates the main flow: parse -> infer -> review -> meeting -> output.
    """
    result = orchestrator.process_document(file_path=setup_dummy_doc)

    # Assertions on the result
    assert "error" not in result, f"Processing failed: {result.get('error')}"
    assert "document_path" in result and result["document_path"] == setup_dummy_doc
    assert "confirmed_scenario" in result and result["confirmed_scenario"] == "Technical Report"
    assert "review_results" in result and isinstance(result["review_results"], list)
    assert len(result["review_results"]) > 0
    assert "final_output_path" in result and result["final_output_path"].startswith("output/")

    # Clean up generated output file if it exists from this test run
    output_file = result["final_output_path"] + ".txt"
    if os.path.exists(output_file):
        os.remove(output_file) 