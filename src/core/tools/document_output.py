from .base_tool import BaseTool

class DocumentOutputTool(BaseTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(self, content: str, output_path: str, file_format: str = "txt") -> dict:
        try:
            full_path = f"{output_path}.{file_format}"
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"success": True, "message": f"Content saved to {full_path}"}
        except Exception as e:
            return {"error": f"Failed to save content to {output_path}.{file_format}: {e}"} 