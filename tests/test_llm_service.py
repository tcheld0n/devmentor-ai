"""
Testes para o serviço de LLM.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.llm_service import get_llm_response


class TestLLMService:
    """Testes essenciais para o serviço de LLM."""
    
    def test_get_llm_response_without_api_key(self):
        """Deve retornar None quando API key não for fornecida."""
        result = get_llm_response(
            messages=[{"role": "user", "content": "Hello"}],
            api_key=""
        )
        assert result is None
    
    @patch('app.services.llm_service.OpenAI')
    def test_get_llm_response_success(self, mock_openai):
        """Deve retornar stream quando API key for válida."""
        mock_client = MagicMock()
        mock_stream = MagicMock()
        mock_client.chat.completions.create.return_value = mock_stream
        mock_openai.return_value = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        api_key = "sk-or-v1-validapikey123456789"
        
        result = get_llm_response(messages, api_key)
        
        assert result is not None
        mock_openai.assert_called_once()
    
    @patch('app.services.llm_service.OpenAI')
    def test_get_llm_response_handles_exception(self, mock_openai):
        """Deve retornar None quando ocorrer exceção."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        result = get_llm_response(
            messages=[{"role": "user", "content": "Test"}],
            api_key="sk-or-v1-validapikey123456789"
        )
        
        assert result is None
