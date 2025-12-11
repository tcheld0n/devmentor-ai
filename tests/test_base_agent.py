"""
Testes para o agente base.
"""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from app.agents.base_agent import BaseAgent


class TestBaseAgent:
    """Testes essenciais para a classe BaseAgent."""
    
    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Mock da variável de ambiente OPENROUTER_API_KEY."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-key-123456789")
    
    def test_base_agent_initialization(self):
        """Deve inicializar agente base com parâmetros corretos."""
        agent = BaseAgent(
            name="Test Agent",
            description="Test Description",
            prompt="Test Prompt",
            port=9000,
            url="http://localhost:9000"
        )
        
        assert agent.name == "Test Agent"
        assert agent.description == "Test Description"
        assert agent.prompt == "Test Prompt"
        assert agent.mcp_url == "http://localhost:5000"
    
    @patch('app.agents.base_agent.OpenAI')
    def test_call_llm_basic(self, mock_openai, mock_env):
        """Deve chamar LLM com mensagens básicas."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = BaseAgent(
            name="Test",
            description="Test",
            prompt="Test",
            port=9000,
            url="http://localhost:9000"
        )
        
        messages = [{"role": "user", "content": "Hello"}]
        response = agent.call_llm(messages)
        
        assert response == "Test response"
    
    @patch('app.agents.base_agent.requests.post')
    def test_execute_mcp_tool_success(self, mock_post):
        """Deve executar ferramenta MCP com sucesso."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": "Tool result"}]
        }
        mock_post.return_value = mock_response
        
        agent = BaseAgent(
            name="Test",
            description="Test",
            prompt="Test",
            port=9000,
            url="http://localhost:9000"
        )
        
        result = agent._execute_mcp_tool("test_tool", {"arg": "value"})
        assert result == "Tool result"
