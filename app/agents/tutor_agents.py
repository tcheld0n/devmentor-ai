"""
Agente especializado em ensino e tutoria.
"""
from typing import Dict, Any
from python_a2a import agent, skill
from app.agents.base_agent import BaseAgent
from app.mcp.agents_data import AGENTS_DB


@agent(
    name="Concept Tutor",
    description="Professor especializado em ensino socrático de conceitos complexos."
)
class ConceptTutorAgent(BaseAgent):
    """Agente tutor de conceitos."""
    
    def __init__(self, **kwargs):
        agent_data = AGENTS_DB["concept_tutor"]
        super().__init__(
            name=agent_data["display_name"],
            description=agent_data["description"],
            prompt=agent_data["prompt"],
            **kwargs
        )
    
    @skill(name="teach_concept", description="Ensina conceitos de forma socrática e didática.")
    def teach_concept(self, user_message: str) -> str:
        """Processa mensagem do usuário e responde como tutor."""
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
        
        response = self.teach_concept(user_message)
        
        task.artifacts = [{
            "parts": [{"type": "text", "text": response}]
        }]
        return task

