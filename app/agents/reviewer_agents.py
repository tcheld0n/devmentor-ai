"""
Agente especializado em code review.
"""
from typing import Dict, Any
from python_a2a import agent, skill
from app.agents.base_agent import BaseAgent
from app.mcp.agents_data import AGENTS_DB


@agent(
    name="Code Reviewer",
    description="Especialista em revisão de código focada em Clean Code e PEP8."
)
class CodeReviewerAgent(BaseAgent):
    """Agente revisor de código."""
    
    def __init__(self, **kwargs):
        agent_data = AGENTS_DB["code_reviewer"]
        super().__init__(
            name=agent_data["display_name"],
            description=agent_data["description"],
            prompt=agent_data["prompt"],
            **kwargs
        )
    
    @skill(name="review_code", description="Revisa código focando em estilo, PEP8 e boas práticas.")
    def review_code(self, user_message: str) -> str:
        """Processa mensagem do usuário e responde como revisor."""
        messages = [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": user_message}
        ]
        
        return self.call_llm(messages, use_mcp_tools=True)
    
    def handle_task(self, task):
        """Processa tarefa A2A."""
        message_data = task.message or {}
        content = message_data.get("content", {})
        user_message = content.get("text", "") if isinstance(content, dict) else str(content)
        
        response = self.review_code(user_message)
        
        task.artifacts = [{
            "parts": [{"type": "text", "text": response}]
        }]
        return task

