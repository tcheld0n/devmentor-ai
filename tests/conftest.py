"""
Configuração do pytest e fixtures compartilhados.
"""
import pytest
import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


@pytest.fixture(scope="session")
def project_root():
    """Retorna o caminho raiz do projeto."""
    return root_dir


@pytest.fixture
def mock_api_key(monkeypatch):
    """Mock da API key para testes."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-mock-key-123456789")
    return "sk-test-mock-key-123456789"


@pytest.fixture
def sample_messages():
    """Mensagens de exemplo para testes."""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]


@pytest.fixture
def sample_quiz_data():
    """Dados de exemplo para quiz."""
    return {
        "topic": "Python Basics",
        "difficulty": "Mid",
        "num_questions": 3
    }
