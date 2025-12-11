"""
Agente especializado em soft skills e coaching.
"""
from typing import Dict, Any
from python_a2a import agent, skill
from app.agents.base_agent import BaseAgent
from app.mcp.agents_data import AGENTS_DB


@agent(
    name="Soft Skills Coach",
    description="Especialista em preparação para entrevistas comportamentais usando método STAR."
)
class SoftSkillsCoachAgent(BaseAgent):
    """Agente coach de soft skills."""
    
    def __init__(self, **kwargs):
        agent_data = AGENTS_DB["soft_skills_coach"]
        super().__init__(
            name=agent_data["display_name"],
            description=agent_data["description"],
            prompt=agent_data["prompt"],
            **kwargs
        )
    
    @skill(name="coach_interview", description="Prepara candidatos para entrevistas comportamentais.")
    def coach_interview(self, user_message: str) -> str:
        """Processa mensagem do usuário e responde como coach."""
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
        
        response = self.coach_interview(user_message)
        
        task.artifacts = [{
            "parts": [{"type": "text", "text": response}]
        }]
        return task

