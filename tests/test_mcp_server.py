"""
Testes para o servidor MCP e suas ferramentas.
"""
import pytest
import json
from pathlib import Path
from unittest.mock import mock_open, patch
from app.mcp.server import generate_quiz_json, read_file_snippet, search_docs


class TestGenerateQuizJson:
    """Testes essenciais para a ferramenta generate_quiz_json."""
    
    def test_generate_quiz_with_defaults(self):
        """Deve gerar quiz com valores padrão."""
        result = generate_quiz_json("Python Basics")
        quiz = json.loads(result)
        
        assert quiz["meta"]["topic"] == "Python Basics"
        assert len(quiz["questions"]) == 3
    
    def test_generate_quiz_structure(self):
        """Deve ter a estrutura correta de quiz."""
        result = generate_quiz_json("Testing", num_questions=1)
        quiz = json.loads(result)
        
        assert "meta" in quiz
        assert "instructions" in quiz
        assert "questions" in quiz
        
        question = quiz["questions"][0]
        assert "id" in question
        assert "question" in question
        assert "options" in question
        assert "correct_option" in question


class TestReadFileSnippet:
    """Testes essenciais para a ferramenta read_file_snippet."""
    
    def test_read_file_snippet_success(self, tmp_path):
        """Deve ler snippet de arquivo com sucesso."""
        test_file = tmp_path / "test.py"
        content = "\n".join([f"line {i}" for i in range(1, 101)])
        test_file.write_text(content)
        
        result = read_file_snippet(str(test_file), start_line=10, end_line=15)
        
        assert "line 10" in result
        assert "line 15" in result
    
    def test_read_file_snippet_file_not_found(self):
        """Deve retornar mensagem de erro quando arquivo não existir."""
        result = read_file_snippet("/caminho/inexistente/arquivo.py")
        assert "Erro" in result or "não encontrado" in result.lower()


class TestSearchDocs:
    """Testes essenciais para a ferramenta search_docs."""
    
    def test_search_docs_basic(self):
        """Deve retornar resultado de busca."""
        result = search_docs("python decorators")
        assert isinstance(result, str)
        assert len(result) > 0
