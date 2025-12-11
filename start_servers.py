"""
Script para iniciar todos os servidores da aplicação DevMentor AI.
Inicializa na ordem correta:
  1. MCP Server (porta 5000) - Ferramentas e utilitários
  2. Agentes Especializados (portas 8001-8005) - Agentes independentes
     - Entrevistador de Algoritmos (8001)
     - Entrevistador de ML & Eng. Software (8002)
     - Professor Universitário (8003)
     - Code Reviewer (8004)
     - Soft Skills Coach (8005)
  3. Coordenador A2A (porta 8000) - Orquestra agentes especializados
     (deve ser iniciado após os agentes, pois depende deles)

Executar ANTES de rodar o Streamlit (streamlit run app.py).
"""
import os
import sys
import time
import logging
import threading
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

from app.mcp.server import run_mcp_server
from app.agents.coordinator import CoordinatorAgent
from app.agents.interviewer_agents import AlgoInterviewerAgent, MLSystemInterviewerAgent
from app.agents.tutor_agents import ConceptTutorAgent
from app.agents.reviewer_agents import CodeReviewerAgent
from app.agents.coach_agents import SoftSkillsCoachAgent
from app.utils.logger import setup_logger
from app.utils.diagnostics import diagnose_all_servers, diagnose_mcp_server, format_diagnostic_report
from python_a2a.server.http import run_server

# Configurar logging
logger = setup_logger("devmentor.servers", level=logging.INFO)


def check_environment():
    """Verifica variáveis de ambiente essenciais."""
    print("\n" + "=" * 80)
    print("🔍 VERIFICANDO AMBIENTE")
    print("=" * 80)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        masked_key = api_key[:10] + "..." + api_key[-4:]
        print(f"✅ OPENROUTER_API_KEY configurada: {masked_key}")
    else:
        print("⚠️  OPENROUTER_API_KEY não configurada!")
        print("   Configure via variável de ambiente para que os agentes funcionem.")
    
    print(f"✅ Python {sys.version.split()[0]} executando")
    print("=" * 80)


def run_mcp_server_thread():
    """Executa servidor MCP em thread separada usando asyncio."""
    import asyncio
    import traceback
    
    logger.info("📡 Iniciando Servidor MCP (porta 5000)...")
    logger.info("   Ferramentas disponíveis:")
    logger.info("   • generate_quiz_json(topic, difficulty, num_questions)")
    logger.info("   • read_file_snippet(file_path, start_line, end_line)")
    logger.info("   • search_docs(query)")
    
    try:
        # Executa a função assíncrona em um novo event loop na thread
        logger.debug("Criando event loop para servidor MCP")
        asyncio.run(run_mcp_server("0.0.0.0", 5000))
    except KeyboardInterrupt:
        logger.warning("Servidor MCP interrompido pelo usuário")
        raise
    except Exception as e:
        logger.critical(f"ERRO CRÍTICO ao iniciar MCP Server na thread: {type(e).__name__}: {str(e)}")
        logger.debug(f"Traceback completo:\n{traceback.format_exc()}")
        print(f"\n{'='*80}")
        print(f"❌ ERRO CRÍTICO ao iniciar MCP Server na thread")
        print(f"{'='*80}")
        print(f"Tipo do erro: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        print(f"\n📋 Traceback completo:")
        print(f"{'='*80}")
        traceback.print_exc()
        print(f"{'='*80}")
        print(f"\n💡 Possíveis soluções:")
        print(f"   1. Verifique se a porta 5000 está disponível")
        print(f"   2. Verifique se as dependências estão instaladas: pip install fastmcp")
        print(f"   3. Verifique se há outro processo usando a porta 5000")
        print(f"   4. Tente executar diretamente: python -m app.mcp.server")
        print(f"{'='*80}\n")
        # Não re-raise para não parar toda a aplicação, mas loga o erro


def run_coordinator_server(port: int = 8000):
    """Executa servidor coordenador em thread separada."""
    logger.info(f"🎯 Iniciando Coordenador A2A (porta {port})...")
    
    try:
        logger.debug(f"Criando instância do CoordinatorAgent na porta {port}")
        coordinator = CoordinatorAgent(url=f"http://localhost:{port}")
        logger.info("✓ Coordenador instanciado, iniciando servidor...")
        # Usar run_server() com host e port corretos
        run_server(coordinator, host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        import traceback
        logger.error(f"Erro ao iniciar Coordenador: {type(e).__name__}: {str(e)}")
        logger.debug(f"Traceback completo:\n{traceback.format_exc()}")
        print(f"❌ Erro ao iniciar Coordenador: {e}")
        print(f"Traceback: {traceback.format_exc()}")


def run_agent_server(agent_class, agent_name: str, port: int):
    """Executa servidor de agente em thread separada."""
    logger.info(f"Iniciando {agent_name} (porta {port})...")
    
    try:
        logger.debug(f"Criando instância de {agent_name} na porta {port}")
        agent = agent_class(url=f"http://localhost:{port}")
        logger.info(f"✓ {agent_name} instanciado, iniciando servidor...")
        # Usar run_server() com host e port corretos
        run_server(agent, host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        import traceback
        logger.error(f"Erro ao iniciar {agent_name}: {type(e).__name__}: {str(e)}")
        logger.debug(f"Traceback completo:\n{traceback.format_exc()}")
        print(f"   ❌ Erro ao iniciar {agent_name}: {e}")
        print(f"   Traceback: {traceback.format_exc()}")


def start_agents_servers():
    """Inicia todos os servidores de agentes em threads separadas."""
    print("\n👥 Iniciando Agentes Especializados:")
    
    agents_config = [
        (AlgoInterviewerAgent, "Entrevistador de Algoritmos", 8001),
        (MLSystemInterviewerAgent, "Entrevistador de ML & Eng. Software", 8002),
        (ConceptTutorAgent, "Professor Universitário", 8003),
        (CodeReviewerAgent, "Code Reviewer", 8004),
        (SoftSkillsCoachAgent, "Soft Skills Coach", 8005),
    ]
    
    # Iniciar cada agente em uma thread separada
    threads = []
    for agent_class, agent_name, port in agents_config:
        thread = threading.Thread(
            target=run_agent_server, 
            args=(agent_class, agent_name, port),
            daemon=True # Mantém a thread rodando em background
        )
        thread.start()
        threads.append(thread)
        time.sleep(0.5)  # Pequeno delay para evitar race conditions
    
    return threads


def main():
    """Inicializa toda a aplicação."""
    print("\n" * 2)
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "🚀 DEVMENTOR AI - INICIALIZANDO APLICAÇÃO" + " " * 15 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # 1. Verificar ambiente
    check_environment()
    
    # 2. Iniciar MCP Server (thread separada)
    print("\n" + "-" * 80)
    print("ETAPA 1: Servidor MCP")
    print("-" * 80)
    mcp_thread = threading.Thread(target=run_mcp_server_thread, daemon=True)
    mcp_thread.start()
    time.sleep(2)  # Aguardar inicialização do MCP
    
    # 3. Iniciar todos os agentes especializados (threads separadas)
    # IMPORTANTE: Agentes devem ser iniciados ANTES do coordenador
    # pois o coordenador depende deles para funcionar
    print("\n" + "-" * 80)
    print("ETAPA 2: Agentes Especializados")
    print("-" * 80)
    agent_threads = start_agents_servers()
    time.sleep(3)  # Aguardar inicialização de todos os agentes
    
    # 4. Iniciar Coordenador (thread separada)
    # Coordenador é iniciado por último pois depende dos agentes estarem prontos
    print("\n" + "-" * 80)
    print("ETAPA 3: Coordenador A2A")
    print("-" * 80)
    coordinator_thread = threading.Thread(target=run_coordinator_server, daemon=True)
    coordinator_thread.start()
    time.sleep(2)  # Aguardar inicialização do coordenador
    
    # 5. Status final e diagnóstico
    print("\n" + "=" * 80)
    print("✅ APLICAÇÃO DEVMENTOR AI INICIALIZADA!")
    print("=" * 80)
    
    logger.info("Aguardando servidores estabilizarem antes do diagnóstico...")
    time.sleep(2)  # Aguardar servidores estabilizarem
    
    # Executar diagnóstico do MCP server (protocolo diferente)
    logger.info("Executando diagnóstico do servidor MCP...")
    mcp_diagnostic = diagnose_mcp_server(5000)
    
    # Executar diagnóstico dos servidores A2A
    agents_config = [
        ("Algo Interviewer", 8001),
        ("ML & Eng. Interviewer", 8002),
        ("Concept Tutor", 8003),
        ("Code Reviewer", 8004),
        ("Soft Skills Coach", 8005),
        ("Coordinator", 8000),
    ]
    
    logger.info("Executando diagnóstico dos servidores A2A...")
    diagnostic_results = diagnose_all_servers(agents_config)
    
    print("\n📊 SERVIDORES ATIVOS:")
    print("   • MCP Server:           http://localhost:5000")
    print("   • Coordenador A2A:      http://localhost:8000")
    print("   • Algo Interviewer:     http://localhost:8001")
    print("   • ML & Eng. Interviewer: http://localhost:8002")
    print("   • Concept Tutor:        http://localhost:8003")
    print("   • Code Reviewer:        http://localhost:8004")
    print("   • Soft Skills Coach:    http://localhost:8005")
    
    # Mostrar status do MCP server
    mcp_status = "✅ Saudável" if mcp_diagnostic["overall_status"] == "healthy" else "⚠️  Verificar"
    print(f"\n📡 Status MCP Server: {mcp_status}")
    if mcp_diagnostic["port_open"]:
        logger.info(f"MCP Server: Porta {mcp_diagnostic['port']} está aberta")
    else:
        logger.warning(f"MCP Server: Porta {mcp_diagnostic['port']} não está aberta - {mcp_diagnostic['port_error']}")
    
    # Mostrar resumo do diagnóstico dos servidores A2A
    summary = diagnostic_results["summary"]
    healthy_count = summary["healthy"]
    total_count = summary["total"]
    
    if healthy_count == total_count:
        print(f"\n✅ Todos os servidores A2A estão saudáveis ({healthy_count}/{total_count})")
        logger.info(f"Diagnóstico A2A: Todos os {total_count} servidores estão saudáveis")
    else:
        print(f"\n⚠️  Status dos servidores A2A: {healthy_count}/{total_count} saudáveis")
        logger.warning(f"Diagnóstico A2A: Apenas {healthy_count}/{total_count} servidores estão saudáveis")
        if summary["port_closed"] > 0:
            logger.warning(f"{summary['port_closed']} servidor(es) A2A com porta fechada")
        if summary["port_open_but_no_endpoint"] > 0:
            logger.warning(f"{summary['port_open_but_no_endpoint']} servidor(es) A2A com porta aberta mas sem endpoint")
    
    print("\n💡 PRÓXIMO PASSO:")
    print("   Execute em outro terminal:")
    print("   $ streamlit run app.py")
    print("\n" + "=" * 80 + "\n")
    
    # Manter aplicação rodando
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⛔ Encerrando aplicação DevMentor AI...")
        print("=" * 80)
        sys.exit(0)


if __name__ == "__main__":
    main()
