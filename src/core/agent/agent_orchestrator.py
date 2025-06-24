import json
import os
from typing import Dict, Any, List

from src.core.tools import DocumentParserTool, ContentFillerTool, StyleGeneratorTool, VirtualReviewerTool, MeetingReviewTool, DocumentOutputTool
from src.core.guidance import ScenarioInferenceModule

class MockLLMClient:
    def generate(self, prompt: str) -> str:
        print(f"--- Orchestrator LLM Prompt ---\n{prompt}\n--- End Orchestrator LLM Prompt ---")
        if "You are acting as a 'Technical Reviewer'" in prompt:
            return json.dumps({
                "comments": [
                    {"severity": "high", "comment": "The proposed solution for component X is overly complex.", "area": "Technical Design"},
                    {"severity": "medium", "comment": "Consider adding unit test cases for module Y.", "area": "Testing"}
                ]
            })
        elif "You are a facilitator for a document review meeting." in prompt:
            return json.dumps({
                "meeting_summary": "The review highlighted concerns about component X's complexity and the need for more unit tests.",
                "discussion_points": ["Complexity of component X", "Unit testing coverage"],
                "action_items": [{"assignee": "Lead Engineer", "task": "Refactor component X"}]
            })
        elif "Rephrase the following text" in prompt:
            return "This is a rephrased text in a professional style."
        else:
            return "Simulated LLM Response"

class AgentOrchestrator:
    def __init__(self, llm_client, kb_path: str = "src/core/knowledge_base"):
        self.llm_client = llm_client
        self.scenario_inference_module = ScenarioInferenceModule(self.llm_client, kb_path)
        self.knowledge_base = self.scenario_inference_module._load_kb("role_profiles.yaml")
        self.knowledge_base.update(self.scenario_inference_module._load_kb("scenario_definitions.yaml"))
        self.knowledge_base.update(self.scenario_inference_module._load_kb("style_templates.yaml"))

        self.tools = {
            "document_parser": DocumentParserTool(),
            "content_filler": ContentFillerTool(),
            "style_generator": StyleGeneratorTool(self.llm_client, os.path.join(kb_path, "style_templates.yaml")),
            "virtual_reviewer": VirtualReviewerTool(self.llm_client, self.knowledge_base),
            "meeting_review": MeetingReviewTool(self.llm_client),
            "document_output": DocumentOutputTool()
        }
        self.current_state = {
            "document_path": None,
            "document_content": None,
            "inferred_scenario": None,
            "confirmed_scenario": None,
            "selected_reviewers": [],
            "review_results": [],
            "final_output_path": None
        }

    def process_document(self, file_path: str, initial_action: str = None) -> Dict[str, Any]:
        self.current_state["document_path"] = file_path
        parse_result = self._execute_tool("document_parser", file_path=file_path)
        if "error" in parse_result:
            return {"error": f"Failed to parse document: {parse_result['error']}"}
        self.current_state["document_content"] = parse_result.get("text_content", "")

        if not self.current_state["document_content"]:
            return {"warning": "Document parsed but content is empty."}

        inference_result = self.scenario_inference_module.infer_scenario_and_roles(self.current_state["document_content"])
        user_prompt = self.scenario_inference_module.generate_user_confirmation_prompt(inference_result)

        print("\n--- User Guidance Prompt ---\n" + user_prompt + "\n--- End User Guidance Prompt ---\n")

        if "error" in inference_result:
            return {"error": f"Scenario inference failed: {inference_result['error']}. Please provide details manually."}

        self.current_state["inferred_scenario"] = inference_result.get("inferred_scenario")
        self.current_state["confirmed_scenario"] = self.current_state["inferred_scenario"]

        scenario_suggestion = self.scenario_inference_module.suggest_next_steps_and_roles(self.current_state["confirmed_scenario"])
        print(f"\nScenario confirmed as: {self.current_state['confirmed_scenario']}")
        print(f"Suggestion: {scenario_suggestion['suggestion']}")
        print(f"Suggested Reviewers: {', '.join(scenario_suggestion.get('suggested_roles', ['None']))}")

        self.current_state["selected_reviewers"] = [role['role_name'] for role in self.knowledge_base.get('roles', []) if role.get('role_name') in scenario_suggestion.get('suggested_roles', [])]

        if self.current_state["selected_reviewers"]:
            print(f"\nInitiating reviews for: {', '.join(self.current_state['selected_reviewers'])}")
            review_results = []
            for reviewer_role in self.current_state["selected_reviewers"]:
                review_output = self._execute_tool("virtual_reviewer",
                                                   document_content=self.current_state["document_content"],
                                                   reviewer_role_name=reviewer_role,
                                                   review_focus=scenario_suggestion.get('default_review_focus'))
                if "error" not in review_output:
                    review_results.append(review_output)
                else:
                    print(f"Warning: Review failed for {reviewer_role}: {review_output['error']}")
            self.current_state["review_results"] = review_results

            if self.current_state["review_results"]:
                meeting_summary = self._execute_tool("meeting_review", review_outputs=self.current_state["review_results"])
                print("\n--- Meeting Review Summary ---")
                print(f"Summary: {meeting_summary.get('summary', 'N/A')}")
                print(f"Discussion Points: {meeting_summary.get('discussion_points', 'N/A')}")
                print(f"Action Items: {meeting_summary.get('action_items', 'N/A')}")
                print("--- End Meeting Review Summary ---\n")

                final_text_content = f"Document: {self.current_state['document_path']}\n"
                final_text_content += f"Scenario: {self.current_state['confirmed_scenario']}\n\n"
                final_text_content += "Reviewer Feedback Summary:\n"
                for res in self.current_state["review_results"]:
                    final_text_content += f"  - {res.get('reviewer', 'Unknown Reviewer')}:\n"
                    for comment in res.get('review_comments', {}).get('comments', []):
                        final_text_content += f"    - [{comment.get('severity', 'N/A')}] {comment.get('area', 'N/A')}: {comment.get('comment', 'N/A')}\n"
                final_text_content += "\nMeeting Simulation Summary:\n"
                final_text_content += f"  Summary: {meeting_summary.get('summary', 'N/A')}\n"
                final_text_content += f"  Discussion Points: {', '.join(meeting_summary.get('discussion_points', []))}\n"
                final_text_content += f"  Action Items: {json.dumps(meeting_summary.get('action_items', []))}\n"

                self.current_state["final_output_path"] = f"output/processed_{os.path.basename(file_path).split('.')[0]}"
                output_result = self._execute_tool("document_output",
                                                   content=final_text_content,
                                                   output_path=self.current_state["final_output_path"],
                                                   file_format="txt")
                if "error" in output_result:
                    print(f"Error saving final output: {output_result['error']}")
                else:
                    print(f"Final processed summary saved to: {self.current_state['final_output_path']}.txt")

        else:
            print("No reviewers selected, skipping review and meeting simulation.")

        return self.current_state

    def _execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found."}
        tool = self.tools[tool_name]
        try:
            print(f"Executing tool: {tool_name} with args: {kwargs}")
            result = tool.execute(**kwargs)
            print(f"Tool '{tool_name}' result: {result}")
            return result
        except Exception as e:
            print(f"Error executing tool {tool_name}: {e}")
            return {"error": f"Execution error for {tool_name}: {e}"} 