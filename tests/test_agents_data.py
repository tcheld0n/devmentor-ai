"""
Testes para dados dos agentes.
"""
import pytest
from app.mcp.agents_data import AGENTS_DB


class TestAgentsData:
    """Testes essenciais para a estrutura de dados dos agentes."""
    
    def test_all_agents_present(self):
        """Deve conter todos os agentes esperados."""
        expected_agents = [
            "algo_interviewer",
            "ml_system_interviewer",
            "concept_tutor",
            "code_reviewer",
            "soft_skills_coach"
        ]
        
        for agent_key in expected_agents:
            assert agent_key in AGENTS_DB
    
    def test_agent_structure(self):
        """Cada agente deve ter campos obrigatórios."""
        required_fields = ["display_name", "description", "prompt", "port"]
        
        for agent_key, agent_data in AGENTS_DB.items():
            for field in required_fields:
                assert field in agent_data
                assert agent_data[field]
    
    def test_unique_ports(self):
        """Cada agente deve ter uma porta única."""
        ports = [agent["port"] for agent in AGENTS_DB.values()]
        assert len(ports) == len(set(ports))
