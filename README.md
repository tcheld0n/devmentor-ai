# DevMentor AI

Plataforma de mentoria técnica multi-agente construída sobre **MCP (Model Context Protocol)** e **A2A (Agent-to-Agent Protocol)**, com interface web em **Streamlit**. Cada agente roda como um microserviço independente, podendo consumir ferramentas MCP expostas via HTTP.

## Visão Geral da Arquitetura

```
┌──────────────────────┐          ┌───────────────────────────────┐
│      Usuário         │          │       Interface Streamlit     │
│ (navegador/Chat UI)  │◄────────►│        (app.py, porta 8501)   │
└──────────────────────┘          └──────────────┬────────────────┘
                                                A2A (HTTP/JSON)
                                     ┌───────────┴───────────┐
                                     │ Coordenador A2A       │
                                     │ (porta 8000)          │
                                     └───────────┬───────────┘
                                 A2A (HTTP/JSON)│ fan-out
        ┌───────────────────────┬───────────────┼───────────────────────┐
        │                       │               │                       │
┌───────────────┐      ┌───────────────┐  ┌───────────────┐     ┌───────────────┐
│ Algo Int.     │      │ ML/System Int.│  │ Concept Tutor │ ... │ Soft Skills    │
│ (porta 8001)  │      │ (porta 8002)  │  │ (porta 8003)  │     │ (porta 8005)  │
└───────────────┘      └───────────────┘  └───────────────┘     └───────────────┘
        │                       │               │                       │
        └───────────────┬───────┴───────┬───────┴───────────────┬───────┘
                        │ Ferramentas MCP (HTTP)
                        │
                ┌───────────────────────────────┐
                │  Servidor MCP (porta 5000)    │
                │  Tools: quiz, code snippet,   │
                │  doc search                   │
                └───────────────────────────────┘
```

### Componentes-chave
- **Interface (app.py)**: UI em Streamlit; seleciona persona, envia mensagens e mostra respostas. Faz diagnóstico automático de portas/saúde antes de enviar mensagens.
- **Coordenador (porta 8000)**: orquestra a chamada entre agentes especializados (instanciado em `start_servers.py` via `CoordinatorAgent`).
- **Agentes A2A (portas 8001-8005)**: servidores HTTP independentes, cada um com prompt e persona específicos definidos em `app/mcp/agents_data.py`.
- **Servidor MCP (porta 5000)**: expõe ferramentas via FastMCP para uso pelos agentes.

### Ferramentas MCP disponíveis (`app/mcp/server.py`)
- `generate_quiz_json(topic, difficulty, num_questions)`: gera template estruturado de quiz.
- `read_file_snippet(file_path, start_line, end_line)`: lê trecho seguro de arquivos locais.
- `search_docs(query)`: busca simulada em documentação técnica (placeholder para integração real).

## Funcionalidades Atuais
- Seleção de mentor/persona pela UI (lado esquerdo) com descrição e porta alvo.
- Chat com histórico persistente em sessão e limpeza rápida do histórico.
- Diagnóstico automático de disponibilidade dos agentes antes de enviar mensagens (`diagnose_agent_server`).
- Execução paralela dos servidores: MCP + 5 agentes + coordenador, todos iniciados por `start_servers.py`.
- Integração com **OpenRouter** para chamadas LLM (via `openai` client).
- Uso de ferramentas MCP para gerar quizzes, ler snippets e trazer contexto de docs.

## Fluxo de Requisição
1. Usuário envia mensagem pelo Streamlit.
2. UI identifica o agente ativo (porta) a partir de `AGENTS_DB`.
3. A UI valida saúde da porta/endpoint; se ok, envia via `python-a2a` (`A2AClient`).
4. Agente especializado usa `BaseAgent.call_llm` para consultar o LLM e pode acionar ferramentas MCP via HTTP.
5. Resposta volta ao Streamlit, que a apresenta no chat.

## Pré-requisitos
- Python 3.11+ recomendado.
- Conta e chave da **OpenRouter** (`OPENROUTER_API_KEY`).
- Portas livres: 5000 (MCP), 8000-8005 (agentes/coordenador), 8501 (Streamlit).

## Instalação

```bash
pip install -r requirements.txt
```

Crie um `.env` (opcional) ou exporte a variável:

```bash
export OPENROUTER_API_KEY="sua-chave-aqui"
```

No Windows (PowerShell):
```powershell
$env:OPENROUTER_API_KEY="sua-chave-aqui"
```

## Execução Local
1) **Subir servidores (MCP + agentes + coordenador)**  
```bash
python start_servers.py
```
O script inicia cada servidor em threads dedicadas e roda diagnósticos automáticos.  

2) **Rodar a interface web** (outro terminal):  
```bash
streamlit run app.py
```
Abra `http://localhost:8501`.

## Estrutura de Pastas
```
devmentor-ai/
├── app/
│   ├── agents/              # Agentes A2A
│   │   ├── base_agent.py    # Classe base (LLM + MCP tools)
│   │   ├── interviewer_agents.py
│   │   ├── tutor_agents.py
│   │   ├── reviewer_agents.py
│   │   ├── coach_agents.py
│   │   └── coordinator.py
│   ├── mcp/
│   │   ├── server.py        # Servidor MCP e ferramentas
│   │   └── agents_data.py   # Metadata das personas/portas
│   ├── services/
│   │   └── llm_service.py   # Abstrações de LLM (quando aplicável)
│   └── utils/
│       ├── diagnostics.py   # Health-check de portas/serviços
│       └── logger.py        # Configuração de logging
├── app.py                   # UI Streamlit
├── start_servers.py         # Boot de MCP + agentes + coordenador
└── requirements.txt         # Dependências
```

## Portas e Serviços
- 5000: Servidor MCP.
- 8001: Algo Interviewer (LeetCode/Big O).
- 8002: ML & Engineering Interviewer.
- 8003: Concept Tutor (socrático).
- 8004: Code Reviewer (Clean Code/PEP8).
- 8005: Soft Skills Coach (STAR).
- 8000: Coordenador A2A.
- 8501: Interface Streamlit (padrão do Streamlit).

## Testes

```bash
pytest/ app.py
```


## Implementações Futuras
- Persistência de conversas e histórico multi-sessão.
- Busca web real (Tavily/Google API) no `search_docs`.
- Métricas, tracing e observabilidade centralizada.
- Tratamento de erros mais rico e mensagens orientativas na UI.
- Autenticação e autorização entre agentes (mTLS / tokens de serviço).
- Melhorar integração entre agentes
- Implementar RAG
- 


