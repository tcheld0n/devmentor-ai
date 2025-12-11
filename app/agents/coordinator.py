"""
Agente coordenador que orquestra os outros agentes especializados.
"""
from typing import Dict, Any
from python_a2a import A2AServer, agent, skill, A2AClient, Message, TextContent, MessageRole, ErrorContent
from app.agents.base_agent import BaseAgent
from app.mcp.agents_data import AGENTS_DB
from app.utils.logger import get_logger

logger = get_logger(__name__)


@agent(
    name="DevMentor Coordinator",
    description="Coordenador que roteia mensagens para agentes especializados."
)
class CoordinatorAgent(BaseAgent):
    """Agente coordenador que orquestra os outros agentes."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="DevMentor Coordinator",
            description="Coordenador do sistema DevMentor AI",
            prompt="Você é o coordenador do sistema DevMentor AI.",
            **kwargs
        )
        self._agent_clients = {}
        self._agent_ports = {
            "algo_interviewer": 8001,
            "ml_system_interviewer": 8002,
            "concept_tutor": 8003,
            "code_reviewer": 8004,
            "soft_skills_coach": 8005,
        }
    
    def _get_agent_client(self, agent_key: str) -> A2AClient:
        """Obtém ou cria cliente A2A para um agente."""
        if agent_key not in self._agent_clients:
            port = self._agent_ports.get(agent_key, 8001)
            agent_url = f"http://localhost:{port}"
            logger.info(f"Criando cliente A2A para agente {agent_key} em {agent_url}")
            self._agent_clients[agent_key] = A2AClient(agent_url)
            logger.debug(f"Cliente A2A criado para {agent_key}")
        return self._agent_clients[agent_key]
    
    @skill(name="route_to_agent", description="Roteia mensagem para agente especializado.")
    def route_to_agent(self, agent_key: str, user_message: str) -> str:
        """Roteia mensagem para agente especializado via A2A."""
        port = self._agent_ports.get(agent_key, 8001)
        agent_url = f"http://localhost:{port}"
        
        logger.info(f"Roteando mensagem para agente {agent_key} (porta {port})")
        logger.debug(f"Mensagem: {user_message[:100]}...")
        
        try:
            client = self._get_agent_client(agent_key)
            msg = Message(
                content=TextContent(text=user_message),
                role=MessageRole.USER
            )
            
            logger.debug(f"Enviando mensagem via A2A para {agent_key}")
            response = client.send_message(msg)
            
            # Verificar se resposta contém erro
            if isinstance(response.content, ErrorContent):
                error_msg = response.content.message
                logger.error(f"Erro recebido do agente {agent_key}: {error_msg}")
                return f"❌ Erro ao comunicar com agente {agent_key}: {error_msg}"
            
            # Extrair texto da resposta
            if hasattr(response.content, 'text'):
                response_text = response.content.text
            elif hasattr(response.content, 'message'):
                response_text = response.content.message
            else:
                response_text = str(response.content)
            
            logger.info(f"Resposta recebida do agente {agent_key} (tamanho: {len(response_text)} chars)")
            return response_text
            
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Exceção ao comunicar com agente {agent_key}: {error_type}: {str(e)}")
            logger.debug(f"Traceback completo:\n{__import__('traceback').format_exc()}")
            return f"❌ Erro ao comunicar com agente {agent_key}: {error_type}: {str(e)}"
    
    def handle_task(self, task):
        """Processa tarefa roteando para agente apropriado."""
        logger.debug("Processando tarefa no coordenador")
        
        message_data = task.message or {}
        content = message_data.get("content", {})
        user_message = content.get("text", "") if isinstance(content, dict) else str(content)
        
        logger.debug(f"Mensagem recebida: {user_message[:100]}...")
        
        # Extrair agente da mensagem ou usar padrão
        # Formato: "agent_key:mensagem" ou apenas "mensagem" (usa agente padrão)
        agent_key = "algo_interviewer"  # padrão
        
        if ":" in user_message and user_message.split(":")[0] in self._agent_ports:
            parts = user_message.split(":", 1)
            agent_key = parts[0]
            user_message = parts[1].strip()
            logger.info(f"Agente especificado na mensagem: {agent_key}")
        else:
            logger.info(f"Usando agente padrão: {agent_key}")
        
        response = self.route_to_agent(agent_key, user_message)
        
        task.artifacts = [{
            "parts": [{"type": "text", "text": response}]
        }]
        
        logger.debug("Tarefa processada com sucesso")
        return task

