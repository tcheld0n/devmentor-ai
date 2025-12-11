"""
Servidor MCP HTTP independente expondo ferramentas via FastMCP.
Roda em porta separada (5000) e pode ser consumido por qualquer cliente.
"""
import asyncio
import json
from pathlib import Path
from fastmcp import FastMCP

# Inicializa servidor MCP
mcp = FastMCP("DevMentorMCP")


@mcp.tool()
def generate_quiz_json(
    topic: str,
    difficulty: str = "Medium",
    num_questions: int = 3
) -> str:
    """
    Gera um template estruturado (JSON) para um simulado técnico.
    
    Args:
        topic: Assunto do quiz (ex: 'Big O', 'Python Decorators').
        difficulty: Nível - 'Junior', 'Mid' ou 'Senior'. Padrão: 'Medium'.
        num_questions: Quantidade de perguntas. Padrão: 3.
    
    Returns:
        String contendo JSON formatado com o template de quiz.
    """
    if difficulty not in ["Junior", "Mid", "Senior"]:
        difficulty = "Medium"
    
    skeleton = {
        "meta": {
            "topic": topic,
            "difficulty": difficulty,
            "total_questions": num_questions,
            "format": "Multiple Choice"
        },
        "instructions": f"Preencha as perguntas abaixo sobre '{topic}' em nível '{difficulty}'.",
        "questions": [
            {
                "id": i + 1,
                "question": f"[Pergunta {i+1}: Preencha uma questão relevante sobre {topic}]",
                "options": {
                    "A": "[Opção A]",
                    "B": "[Opção B]",
                    "C": "[Opção C]",
                    "D": "[Opção D]"
                },
                "correct_option": "[Letra correta: A, B, C ou D]",
                "explanation": "[Explique por que é a correta e por que outras estão erradas]"
            }
            for i in range(num_questions)
        ]
    }
    
    return json.dumps(skeleton, indent=2, ensure_ascii=False)


@mcp.tool()
def read_file_snippet(
    file_path: str,
    start_line: int = 1,
    end_line: int = 50
) -> str:
    """
    Lê um trecho seguro de código de um arquivo local para análise.
    
    Args:
        file_path: Caminho relativo ou absoluto do arquivo.
        start_line: Linha inicial (1-based). Padrão: 1.
        end_line: Linha final (1-based, inclusiva). Padrão: 50.
    
    Returns:
        String contendo o trecho do arquivo ou mensagem de erro.
    """
    try:
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            return f"❌ Erro: Arquivo '{file_path}' não encontrado."
        
        if not file_path_obj.is_file():
            return f"❌ Erro: '{file_path}' não é um arquivo."
        
        with open(file_path_obj, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        if start_line < 1:
            start_line = 1
        if end_line > total_lines:
            end_line = total_lines
        if start_line > total_lines:
            return f"❌ Erro: start_line ({start_line}) excede total de linhas ({total_lines})."
        
        snippet = lines[start_line - 1:end_line]
        result = "".join(snippet)
        
        header = f"📄 Arquivo: {file_path} (linhas {start_line}-{end_line} de {total_lines})\n"
        header += "=" * 70 + "\n"
        
        return header + result
    
    except UnicodeDecodeError:
        return f"❌ Erro: Não foi possível decodificar '{file_path}' como UTF-8."
    except PermissionError:
        return f"❌ Erro: Sem permissão para ler '{file_path}'."
    except Exception as e:
        return f"❌ Erro inesperado ao ler arquivo: {type(e).__name__}: {str(e)}"


@mcp.tool()
def search_docs(query: str) -> str:
    """
    Busca na documentação técnica ou web para verificar conceitos.
    
    Args:
        query: Termo ou frase a buscar (ex: 'Python async/await', 'SOLID principles').
    
    Returns:
        String contendo resultados da busca.
    """
    mock_results = {
        "python async": "Python async/await permite programação assíncrona com corrotinas...",
        "solid principles": "SOLID é um acrônimo para 5 princípios de design: Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion...",
        "big o notation": "Big O descreve a complexidade de tempo/espaço de algoritmos. O(1) constante, O(n) linear, O(n²) quadrática, O(log n) logarítmica...",
        "transformer architecture": "Transformers usam mecanismo de attention para processar sequências em paralelo, base do BERT, GPT e modelos modernos...",
    }
    
    query_lower = query.lower()
    
    for key, value in mock_results.items():
        if key in query_lower:
            return f"📚 Resultados para '{query}':\n\n{value}\n\n[Resultado simulado - integrar API real em produção]"
    
    return f"""📚 Resultados para '{query}':

Nenhum resultado específico encontrado. 
Sugestões:
- Tente buscar por palavras-chave diferentes
- Consulte documentação oficial (docs.python.org, papers de ML, etc.)
- Use ferramentas como Stack Overflow, GitHub Discussions ou papers acadêmicos

[Implementar integração com Tavily/Google API para resultados reais]"""


async def run_mcp_server(host: str = "0.0.0.0", port: int = 5000):
    """Executa o servidor MCP em modo assíncrono conforme documentação oficial."""
    print(f"🚀 Iniciando DevMentorMCP Server em http://{host}:{port}")
    print("📋 Ferramentas disponíveis:")
    print("   1. generate_quiz_json(topic, difficulty, num_questions)")
    print("   2. read_file_snippet(file_path, start_line, end_line)")
    print("   3. search_docs(query)")
    
    # Usa o método run_async() nativo do FastMCP conforme documentação
    # https://gofastmcp.com/getting-started/quickstart
    await mcp.run_async(transport="http", host=host, port=port)


if __name__ == "__main__":
    asyncio.run(run_mcp_server())
