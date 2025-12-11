"""
Testes para agente coach de soft skills.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.agents.coach_agents import SoftSkillsCoachAgent


class TestSoftSkillsCoachAgent:
    """Testes para o agente coach de soft skills."""
    
    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Mock da variável de ambiente."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-key-123456789")
    
    def test_coach_initialization(self, mock_env):
        """Deve inicializar com dados corretos."""
        agent = SoftSkillsCoachAgent(port=8005, url="http://localhost:8005")
        
        assert "Soft Skills" in agent.name or "Coach" in agent.name
        assert agent.description
        assert len(agent.prompt) > 0
    
    @patch('app.agents.base_agent.OpenAI')
    def test_coach_interview(self, mock_openai, mock_env):
        """Deve preparar candidato chamando LLM."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Use o método STAR..."
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = SoftSkillsCoachAgent(port=8005, url="http://localhost:8005")
        result = agent.coach_interview("Como responder sobre conflitos?")
        
        assert result == "Use o método STAR..."
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('app.agents.base_agent.OpenAI')
    def test_handle_task_with_text_content(self, mock_openai, mock_env):
        """Deve processar tarefa com conteúdo de texto."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Resposta do coach"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = SoftSkillsCoachAgent(port=8005, url="http://localhost:8005")
        
        task = Mock()
        task.message = {"content": {"text": "Como falar de liderança?"}}
        
        result = agent.handle_task(task)
        
        assert result == task
        assert task.artifacts[0]["parts"][0]["text"] == "Resposta do coach"
    
    @patch('app.agents.base_agent.OpenAI')
    def test_handle_task_with_string_content(self, mock_openai, mock_env):
        """Deve processar tarefa com conteúdo string."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Resposta"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = SoftSkillsCoachAgent(port=8005, url="http://localhost:8005")
        
        task = Mock()
        task.message = {"content": "Mensagem simples"}
        
        result = agent.handle_task(task)
        
        assert result == task
        assert len(task.artifacts) == 1
    
    @patch('app.agents.base_agent.OpenAI')
    def test_handle_task_empty_message(self, mock_openai, mock_env):
        """Deve processar tarefa com mensagem vazia."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Olá, como posso ajudar?"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = SoftSkillsCoachAgent(port=8005, url="http://localhost:8005")
        
        task = Mock()
        task.message = None
        
        result = agent.handle_task(task)
        
        assert result == task
