"""
Agente A2A base que todos os agentes especializados herdam.
Fornece funcionalidades comuns como acesso ao LLM e ferramentas MCP.
"""
import os
import json
import requests
from typing import Dict, Any, Optional, List
from openai import OpenAI
from python_a2a import A2AServer


class BaseAgent(A2AServer):
    """Agente base com acesso a LLM e ferramentas MCP."""
    
    def __init__(self, name: str, description: str, prompt: str, mcp_url: str = "http://localhost:5000", **kwargs):
        self.name = name
        self.description = description
        self.prompt = prompt
        self.mcp_url = mcp_url
        self._llm_client = None
        super().__init__(**kwargs)
    
    @property
    def llm_client(self) -> OpenAI:
        """Lazy initialization do cliente LLM."""
        if self._llm_client is None:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY não configurada")
            self._llm_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
        return self._llm_client
    
    def get_mcp_tools_schema(self) -> Optional[List[Dict]]:
        """Obtém schema das ferramentas MCP para passar ao LLM."""
        # TODO: Implementar obtenção de schema via FastMCP quando disponível
        return None
    
    def call_llm(self, messages: list, use_mcp_tools: bool = True, model: str = "openai/gpt-4o-mini") -> str:
        """Chama o LLM via OpenRouter com suporte a ferramentas MCP."""
        kwargs = {
            "model": model,
            "messages": messages,
        }
        
        # TODO: Implementar integração completa quando FastMCP expuser schema
        
        response = self.llm_client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    def _execute_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Executa uma ferramenta MCP via HTTP."""
        try:
            # FastMCP expõe ferramentas via endpoint /tools/{tool_name}
            response = requests.post(
                f"{self.mcp_url}/tools/{tool_name}",
                json=arguments or {},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                # FastMCP retorna no formato MCP
                if isinstance(result, dict) and 'content' in result:
                    content = result['content']
                    if isinstance(content, list) and len(content) > 0:
                        return content[0].get('text', str(result))
                return str(result)
            return f"❌ Erro HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return f"❌ Erro ao chamar ferramenta MCP {tool_name}: {str(e)}"

