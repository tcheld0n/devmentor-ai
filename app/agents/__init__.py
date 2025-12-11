"""Agentes A2A especializados."""
from app.agents.base_agent import BaseAgent
from app.agents.interviewer_agents import AlgoInterviewerAgent, MLSystemInterviewerAgent
from app.agents.tutor_agents import ConceptTutorAgent
from app.agents.reviewer_agents import CodeReviewerAgent
from app.agents.coach_agents import SoftSkillsCoachAgent
from app.agents.coordinator import CoordinatorAgent

__all__ = [
    "BaseAgent",
    "AlgoInterviewerAgent",
    "MLSystemInterviewerAgent",
    "ConceptTutorAgent",
    "CodeReviewerAgent",
    "SoftSkillsCoachAgent",
    "CoordinatorAgent",
]

# Mapeamento de agentes por porta
AGENT_CLASSES = {
    "algo_interviewer": AlgoInterviewerAgent,
    "ml_system_interviewer": MLSystemInterviewerAgent,
    "concept_tutor": ConceptTutorAgent,
    "code_reviewer": CodeReviewerAgent,
    "soft_skills_coach": SoftSkillsCoachAgent,
}

