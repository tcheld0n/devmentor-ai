"""
Agentes especializados em entrevistas técnicas.
"""
from typing import Dict, Any
from python_a2a import agent, skill
from app.agents.base_agent import BaseAgent
from app.mcp.agents_data import AGENTS_DB


@agent(
    name="Algo Interviewer",
    description="Especialista em entrevistas de algoritmos e estruturas de dados."
)
class AlgoInterviewerAgent(BaseAgent):
    """Agente entrevistador de algoritmos."""
    
    def __init__(self, **kwargs):
        agent_data = AGENTS_DB["algo_interviewer"]
        super().__init__(
            name=agent_data["display_name"],
            description=agent_data["description"],
            prompt=agent_data["prompt"],
            **kwargs
        )
    
    @skill(name="conduct_interview", description="Conduz entrevista técnica focada em algoritmos.")
    def conduct_interview(self, user_message: str) -> str:
        """Processa mensagem do usuário e responde como entrevistador."""
        messages = [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Obter ferramentas MCP disponíveis
        return self.call_llm(messages, use_mcp_tools=True)
    
    def handle_task(self, task):
        """Processa tarefa A2A."""
        message_data = task.message or {}
        content = message_data.get("content", {})
        user_message = content.get("text", "") if isinstance(content, dict) else str(content)
        
        response = self.conduct_interview(user_message)
        
        task.artifacts = [{
            "parts": [{"type": "text", "text": response}]
        }]
        return task


@agent(
    name="ML System Interviewer",
    description="Especialista em entrevistas de ML e System Design."
)
class MLSystemInterviewerAgent(BaseAgent):
    """Agente entrevistador de ML e System Design."""
    
    def __init__(self, **kwargs):
        agent_data = AGENTS_DB["ml_system_interviewer"]
        super().__init__(
            name=agent_data["display_name"],
            description=agent_data["description"],
            prompt=agent_data["prompt"],
            **kwargs
        )
    
    @skill(name="conduct_interview", description="Conduz entrevista técnica focada em ML e System Design.")
    def conduct_interview(self, user_message: str) -> str:
        """Processa mensagem do usuário e responde como entrevistador."""
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
        
        response = self.conduct_interview(user_message)
        
        task.artifacts = [{
            "parts": [{"type": "text", "text": response}]
        }]
        return task

