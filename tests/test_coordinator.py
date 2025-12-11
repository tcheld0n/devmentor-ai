"""
Testes para o agente coordenador.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.agents.coordinator import CoordinatorAgent


class TestCoordinatorAgent:
    """Testes para o agente coordenador."""
    
    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Mock da variável de ambiente."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-key-123456789")
    
    def test_coordinator_initialization(self, mock_env):
        """Deve inicializar coordenador corretamente."""
        coordinator = CoordinatorAgent(port=8000, url="http://localhost:8000")
        
        assert coordinator.name == "DevMentor Coordinator"
        assert coordinator.description == "Coordenador do sistema DevMentor AI"
        assert len(coordinator._agent_ports) == 5
        assert coordinator._agent_ports["algo_interviewer"] == 8001
        assert coordinator._agent_ports["soft_skills_coach"] == 8005
    
    def test_get_agent_client_creates_new(self, mock_env):
        """Deve criar novo cliente A2A quando não existir."""
        coordinator = CoordinatorAgent(port=8000, url="http://localhost:8000")
        
        with patch('app.agents.coordinator.A2AClient') as mock_client:
            client = coordinator._get_agent_client("algo_interviewer")
            
            mock_client.assert_called_once_with("http://localhost:8001")
            assert "algo_interviewer" in coordinator._agent_clients
    
    def test_get_agent_client_reuses_existing(self, mock_env):
        """Deve reutilizar cliente existente."""
        coordinator = CoordinatorAgent(port=8000, url="http://localhost:8000")
        
        with patch('app.agents.coordinator.A2AClient') as mock_client:
            # Primeira chamada
            client1 = coordinator._get_agent_client("code_reviewer")
            # Segunda chamada
            client2 = coordinator._get_agent_client("code_reviewer")
            
            # Deve ter criado apenas uma vez
            assert mock_client.call_count == 1
            assert client1 == client2
    
    @patch('app.agents.coordinator.A2AClient')
    def test_route_to_agent_success(self, mock_client_class, mock_env):
        """Deve rotear mensagem com sucesso."""
        coordinator = CoordinatorAgent(port=8000, url="http://localhost:8000")
        
        # Mock do cliente e resposta
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content.text = "Resposta do agente"
        mock_client.send_message.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        result = coordinator.route_to_agent("algo_interviewer", "Hello")
        
        assert result == "Resposta do agente"
        mock_client.send_message.assert_called_once()
    
    @patch('app.agents.coordinator.A2AClient')
    def test_route_to_agent_exception(self, mock_client_class, mock_env):
        """Deve retornar mensagem de erro em caso de exceção."""
        coordinator = CoordinatorAgent(port=8000, url="http://localhost:8000")
        
        mock_client = MagicMock()
        mock_client.send_message.side_effect = Exception("Connection failed")
        mock_client_class.return_value = mock_client
        
        result = coordinator.route_to_agent("algo_interviewer", "Hello")
        
        assert "❌ Erro ao comunicar com agente" in result
        assert "Connection failed" in result
    
    @patch('app.agents.coordinator.A2AClient')
    def test_handle_task_with_default_agent(self, mock_client_class, mock_env):
        """Deve usar agente padrão quando não especificado."""
        coordinator = CoordinatorAgent(port=8000, url="http://localhost:8000")
        
        # Mock do cliente
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content.text = "Resposta"
        mock_client.send_message.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        # Mock da task
        task = Mock()
        task.message = {"content": {"text": "Teste de mensagem"}}
        
        result = coordinator.handle_task(task)
        
        assert result == task
        assert task.artifacts[0]["parts"][0]["text"] == "Resposta"
    
    @patch('app.agents.coordinator.A2AClient')
    def test_handle_task_with_specified_agent(self, mock_client_class, mock_env):
        """Deve usar agente especificado no formato 'agent_key:mensagem'."""
        coordinator = CoordinatorAgent(port=8000, url="http://localhost:8000")
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content.text = "Coach response"
        mock_client.send_message.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        task = Mock()
        task.message = {"content": {"text": "soft_skills_coach:Como me preparar?"}}
        
        coordinator.handle_task(task)
        
        # Verificar que criou cliente para o coach (porta 8005)
        mock_client_class.assert_called_with("http://localhost:8005")
    
    @patch('app.agents.coordinator.A2AClient')
    def test_handle_task_with_non_dict_content(self, mock_client_class, mock_env):
        """Deve lidar com conteúdo não-dict."""
        coordinator = CoordinatorAgent(port=8000, url="http://localhost:8000")
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content.text = "Response"
        mock_client.send_message.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        task = Mock()
        task.message = {"content": "Mensagem simples"}
        
        result = coordinator.handle_task(task)
        
        assert result == task
        assert len(task.artifacts) == 1
