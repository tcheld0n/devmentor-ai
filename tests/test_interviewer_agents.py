"""
Testes para agentes entrevistadores.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.agents.interviewer_agents import AlgoInterviewerAgent, MLSystemInterviewerAgent


class TestAlgoInterviewerAgent:
    """Testes para o agente entrevistador de algoritmos."""
    
    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Mock da variável de ambiente."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-key-123456789")
    
    def test_algo_interviewer_initialization(self, mock_env):
        """Deve inicializar com dados corretos."""
        agent = AlgoInterviewerAgent(port=8001, url="http://localhost:8001")
        
        assert "Algoritmos" in agent.name
        assert agent.description
        assert len(agent.prompt) > 0
    
    @patch('app.agents.base_agent.OpenAI')
    def test_conduct_interview(self, mock_openai, mock_env):
        """Deve conduzir entrevista chamando LLM."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Vamos começar com arrays..."
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = AlgoInterviewerAgent(port=8001, url="http://localhost:8001")
        result = agent.conduct_interview("Quero praticar algoritmos")
        
        assert result == "Vamos começar com arrays..."
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('app.agents.base_agent.OpenAI')
    def test_handle_task_with_text_content(self, mock_openai, mock_env):
        """Deve processar tarefa com conteúdo de texto."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Resposta do entrevistador"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = AlgoInterviewerAgent(port=8001, url="http://localhost:8001")
        
        task = Mock()
        task.message = {"content": {"text": "Qual a complexidade de bubble sort?"}}
        
        result = agent.handle_task(task)
        
        assert result == task
        assert task.artifacts[0]["parts"][0]["text"] == "Resposta do entrevistador"
    
    @patch('app.agents.base_agent.OpenAI')
    def test_handle_task_with_string_content(self, mock_openai, mock_env):
        """Deve processar tarefa com conteúdo string."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Resposta"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = AlgoInterviewerAgent(port=8001, url="http://localhost:8001")
        
        task = Mock()
        task.message = {"content": "Mensagem simples"}
        
        result = agent.handle_task(task)
        
        assert result == task
        assert len(task.artifacts) == 1


class TestMLSystemInterviewerAgent:
    """Testes para o agente entrevistador de ML e System Design."""
    
    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Mock da variável de ambiente."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-key-123456789")
    
    def test_ml_interviewer_initialization(self, mock_env):
        """Deve inicializar com dados corretos."""
        agent = MLSystemInterviewerAgent(port=8002, url="http://localhost:8002")
        
        assert "ML" in agent.name or "Machine Learning" in agent.name
        assert agent.description
        assert len(agent.prompt) > 0
    
    @patch('app.agents.base_agent.OpenAI')
    def test_conduct_interview(self, mock_openai, mock_env):
        """Deve conduzir entrevista chamando LLM."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Vamos discutir ML..."
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = MLSystemInterviewerAgent(port=8002, url="http://localhost:8002")
        result = agent.conduct_interview("Como funciona gradient descent?")
        
        assert result == "Vamos discutir ML..."
    
    @patch('app.agents.base_agent.OpenAI')
    def test_handle_task(self, mock_openai, mock_env):
        """Deve processar tarefa A2A."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Resposta ML"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = MLSystemInterviewerAgent(port=8002, url="http://localhost:8002")
        
        task = Mock()
        task.message = {"content": {"text": "Explique overfitting"}}
        
        result = agent.handle_task(task)
        
        assert result == task
        assert task.artifacts[0]["parts"][0]["text"] == "Resposta ML"
