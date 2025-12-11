"""
DevMentor AI - Interface Streamlit
Sistema multi-agente usando A2A e MCP.
"""
import os
import logging
import streamlit as st
from app.mcp.agents_data import AGENTS_DB
from app.services.llm_service import get_llm_response
from python_a2a import A2AClient, Message, TextContent, MessageRole, ErrorContent
from app.utils.logger import setup_logger
from app.utils.diagnostics import diagnose_agent_server, format_diagnostic_report

# Configurar logging
logger = setup_logger("devmentor.app", level=logging.INFO)

# Configuração da página
st.set_page_config(page_title="DevMentor AI", page_icon="🚀", layout="wide")

# Sidebar
with st.sidebar:
    st.title("🔌 Configuração")
    api_key = st.text_input("OpenRouter API Key", type="password", value=os.getenv("OPENROUTER_API_KEY", ""))
    
    if api_key:
        os.environ["OPENROUTER_API_KEY"] = api_key
        st.success("✅ OpenRouter configurado!")
    else:
        st.info("ℹ️ Insira sua OpenRouter API Key")
    
    st.markdown("---")
    st.subheader("Seleção de Mentor")
    
    options = [data["display_name"] for data in AGENTS_DB.values()]
    selected_option = st.radio("Mentor Ativo:", options)
    
    current_agent = next(data for data in AGENTS_DB.values() if data["display_name"] == selected_option)
    st.info(f"{current_agent['description']}")
    
    st.markdown("---")
    st.caption("**Arquitetura:**")
    st.caption("• MCP Server (porta 5000)")
    st.caption("• Agentes A2A (portas 8001-8005)")
    st.caption("• Coordenador (porta 8000)")
    
    if st.button("Limpar Chat"):
        st.session_state.messages = []
        st.rerun()

# Main area
st.title("🚀 DevMentor AI")
st.caption(f"**Mentor:** {selected_option}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Renderizar histórico
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input e resposta
if prompt := st.chat_input("Sua mensagem..."):
    if not api_key:
        st.warning("Por favor, insira a API Key na barra lateral.")
        st.stop()
    
    # Adicionar mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Determinar agente baseado na seleção
    agent_key = next(key for key, data in AGENTS_DB.items() if data["display_name"] == selected_option)
    agent_port = current_agent["port"]
    
    # Chamar agente via A2A
    with st.chat_message("assistant"):
        agent_url = f"http://localhost:{agent_port}"
        logger.info(f"Tentando conectar ao agente {agent_key} em {agent_url}")
        
        try:
            # Diagnóstico prévio do servidor
            diagnostic = diagnose_agent_server(agent_port, agent_url)
            logger.debug(f"Diagnóstico do servidor: {diagnostic}")
            
            if not diagnostic["port_open"]:
                logger.error(f"Porta {agent_port} não está aberta: {diagnostic['port_error']}")
                error_msg = f"❌ **Servidor não está rodando**\n\n"
                error_msg += f"O agente na porta {agent_port} não está respondendo.\n\n"
                error_msg += f"**Causa:** {diagnostic['port_error']}\n\n"
                error_msg += "**Solução:**\n"
                error_msg += "1. Execute `python start_servers.py` em um terminal separado\n"
                error_msg += "2. Aguarde alguns segundos para os servidores iniciarem\n"
                error_msg += "3. Verifique se não há erros no terminal do start_servers.py"
                st.error(error_msg)
                st.session_state.messages.pop()
                st.stop()
            
            if diagnostic["overall_status"] != "healthy":
                logger.warning(f"Servidor em {agent_url} não está saudável: {diagnostic['overall_status']}")
                # Ainda tenta conectar, mas loga o aviso
            
            # Tentar conectar via A2A
            logger.info(f"Criando cliente A2A para {agent_url}")
            client = A2AClient(agent_url, timeout=60)
            
            msg = Message(
                content=TextContent(text=prompt),
                role=MessageRole.USER
            )
            
            logger.info(f"Enviando mensagem para agente {agent_key}")
            response = client.send_message(msg)
            
            # Verificar se a resposta contém erro
            if isinstance(response.content, ErrorContent):
                error_content = response.content
                logger.error(f"Resposta de erro do agente: {error_content.message}")
                error_msg = f"❌ **Erro na comunicação com o agente**\n\n"
                error_msg += f"**Mensagem de erro:** {error_content.message}\n\n"
                error_msg += "**Possíveis causas:**\n"
                error_msg += "1. Servidor A2A não está configurado corretamente\n"
                error_msg += "2. Endpoint A2A não está disponível\n"
                error_msg += "3. Timeout na comunicação\n\n"
                error_msg += "**Solução:**\n"
                error_msg += "Verifique os logs do servidor em `start_servers.py`"
                st.error(error_msg)
                
                with st.expander("🔍 Diagnóstico detalhado"):
                    st.code(format_diagnostic_report({"servers": {agent_key: diagnostic}}))
                
                st.session_state.messages.pop()
                st.stop()
            
            # Extrair texto da resposta
            if hasattr(response.content, 'text'):
                response_text = response.content.text
            elif hasattr(response.content, 'message'):
                response_text = response.content.message
            else:
                response_text = str(response.content)
            
            logger.info(f"Resposta recebida do agente {agent_key} (tamanho: {len(response_text)} chars)")
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_type = type(e).__name__
            
            logger.error(f"Erro ao comunicar com agente {agent_key} em {agent_url}: {error_type}: {str(e)}")
            logger.debug(f"Traceback completo:\n{error_details}")
            
            # Mensagem de erro mais informativa
            error_msg = f"❌ **Erro ao comunicar com agente na porta {agent_port}**\n\n"
            error_msg += f"**Tipo de erro:** `{error_type}`\n\n"
            error_msg += f"**Mensagem:** {str(e)}\n\n"
            
            # Diagnóstico automático
            diagnostic = diagnose_agent_server(agent_port, agent_url)
            
            error_msg += "**Status do servidor:**\n"
            if diagnostic["port_open"]:
                error_msg += f"✅ Porta {agent_port} está aberta\n"
                if diagnostic["overall_status"] == "healthy":
                    error_msg += "✅ Servidor está respondendo\n"
                else:
                    error_msg += f"⚠️ Servidor não está respondendo corretamente ({diagnostic['overall_status']})\n"
            else:
                error_msg += f"❌ Porta {agent_port} não está aberta\n"
                error_msg += f"   Causa: {diagnostic['port_error']}\n"
            
            error_msg += "\n**Solução:**\n"
            error_msg += "1. Execute `python start_servers.py` em um terminal separado\n"
            error_msg += "2. Aguarde alguns segundos para os servidores iniciarem completamente\n"
            error_msg += "3. Verifique os logs do servidor para erros de inicialização\n"
            
            st.error(error_msg)
            
            # Mostrar detalhes do erro e diagnóstico
            with st.expander("🔍 Detalhes técnicos do erro"):
                st.code(error_details)
            
            with st.expander("📊 Diagnóstico do servidor"):
                st.code(format_diagnostic_report({"servers": {agent_key: diagnostic}}))
            
            st.session_state.messages.pop()  # Remove mensagem do usuário em caso de erro
