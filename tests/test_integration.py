"""
Testes de integração para a aplicação DevMentor AI.
"""
import pytest
import os


class TestEnvironmentSetup:
    """Testes essenciais de configuração do ambiente."""
    
    def test_env_file_exists(self):
        """Deve ter arquivo .env no projeto."""
        env_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            ".env"
        )
        assert os.path.exists(env_path)
    
    def test_required_packages_in_requirements(self):
        """Deve conter pacotes essenciais em requirements.txt."""
        req_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "requirements.txt"
        )
        
        with open(req_path, 'r') as f:
            requirements = f.read()
        
        required_packages = ["streamlit", "python-a2a", "python-dotenv", "openai"]
        
        for package in required_packages:
            assert package in requirements


class TestAgentImports:
    """Testes essenciais de importação dos agentes."""
    
    def test_import_base_agent(self):
        """Deve importar BaseAgent sem erros."""
        from app.agents.base_agent import BaseAgent
        assert BaseAgent is not None
    
    def test_import_all_specialized_agents(self):
        """Deve importar todos os agentes especializados."""
        from app.agents.coordinator import CoordinatorAgent
        from app.agents.interviewer_agents import AlgoInterviewerAgent, MLSystemInterviewerAgent
        from app.agents.tutor_agents import ConceptTutorAgent
        from app.agents.reviewer_agents import CodeReviewerAgent
        from app.agents.coach_agents import SoftSkillsCoachAgent
        
        assert all([
            CoordinatorAgent,
            AlgoInterviewerAgent,
            MLSystemInterviewerAgent,
            ConceptTutorAgent,
            CodeReviewerAgent,
            SoftSkillsCoachAgent
        ])


class TestApplicationStructure:
    """Testes essenciais da estrutura da aplicação."""
    
    def test_main_directories_exist(self):
        """Deve ter diretórios principais da aplicação."""
        base_path = os.path.dirname(os.path.dirname(__file__))
        
        directories = ["app", "app/agents", "app/mcp", "app/services", "tests"]
        
        for directory in directories:
            dir_path = os.path.join(base_path, directory)
            assert os.path.exists(dir_path)
    
    def test_main_files_exist(self):
        """Deve ter arquivos principais da aplicação."""
        base_path = os.path.dirname(os.path.dirname(__file__))
        
        files = ["app.py", "start_servers.py", "README.md"]
        
        for filename in files:
            filepath = os.path.join(base_path, filename)
            assert os.path.exists(filepath)
