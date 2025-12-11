"""
Utilitário de diagnóstico para verificar status dos servidores e conectividade.
"""
import requests
import socket
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse
from app.utils.logger import get_logger

logger = get_logger(__name__)


def check_port_open(host: str, port: int, timeout: float = 2.0) -> Tuple[bool, Optional[str]]:
    """
    Verifica se uma porta está aberta e aceitando conexões.
    
    Args:
        host: Hostname ou IP
        port: Número da porta
        timeout: Timeout em segundos
    
    Returns:
        Tupla (is_open, error_message)
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return True, None
        else:
            return False, f"Porta {port} não está aceitando conexões (código: {result})"
    except socket.gaierror as e:
        return False, f"Erro de DNS: {str(e)}"
    except socket.timeout:
        return False, f"Timeout ao conectar em {host}:{port}"
    except Exception as e:
        return False, f"Erro inesperado: {type(e).__name__}: {str(e)}"


def check_http_endpoint(
    url: str, 
    timeout: float = 2.0,
    expected_status: int = 200,
    headers: Optional[Dict[str, str]] = None
) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Verifica se um endpoint HTTP está respondendo.
    
    Args:
        url: URL completa do endpoint
        timeout: Timeout em segundos
        expected_status: Status HTTP esperado (padrão: 200)
        headers: Headers HTTP opcionais
    
    Returns:
        Tupla (is_ok, error_message, status_code)
    """
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=False, headers=headers)
        if response.status_code == expected_status:
            return True, None, response.status_code
        else:
            # 406 Not Acceptable geralmente indica problema de headers, não que o servidor está down
            if response.status_code == 406:
                return False, f"Status HTTP {response.status_code} - Servidor requer headers específicos (ex: Accept: text/event-stream)", response.status_code
            return False, f"Status HTTP {response.status_code} (esperado {expected_status})", response.status_code
    except requests.exceptions.ConnectionError as e:
        return False, f"Erro de conexão: {str(e)}", None
    except requests.exceptions.Timeout:
        return False, f"Timeout ao conectar em {url}", None
    except requests.exceptions.RequestException as e:
        return False, f"Erro na requisição: {type(e).__name__}: {str(e)}", None
    except Exception as e:
        return False, f"Erro inesperado: {type(e).__name__}: {str(e)}", None


def diagnose_agent_server(port: int, base_url: Optional[str] = None) -> Dict:
    """
    Diagnostica um servidor de agente A2A.
    
    Args:
        port: Porta do servidor
        base_url: URL base (padrão: http://localhost:{port})
    
    Returns:
        Dicionário com resultados do diagnóstico
    """
    if base_url is None:
        base_url = f"http://localhost:{port}"
    
    parsed = urlparse(base_url)
    host = parsed.hostname or "localhost"
    
    logger.info(f"🔍 Diagnosticando servidor em {base_url} (porta {port})")
    
    results = {
        "url": base_url,
        "port": port,
        "host": host,
        "port_open": False,
        "port_error": None,
        "endpoints": {},
        "overall_status": "unknown"
    }
    
    # 1. Verificar se porta está aberta
    port_open, port_error = check_port_open(host, port)
    results["port_open"] = port_open
    results["port_error"] = port_error
    
    if not port_open:
        results["overall_status"] = "port_closed"
        logger.warning(f"❌ Porta {port} não está aberta: {port_error}")
        return results
    
    logger.info(f"✅ Porta {port} está aberta")
    
    # 2. Testar endpoints comuns do A2A
    endpoints_to_test = [
        ("/", "root"),
        ("/health", "health"),
        ("/api/health", "api_health"),
        ("/v1/health", "v1_health"),
    ]
    
    for endpoint, name in endpoints_to_test:
        url = f"{base_url.rstrip('/')}{endpoint}"
        is_ok, error, status_code = check_http_endpoint(url, timeout=1.0)
        
        results["endpoints"][name] = {
            "url": url,
            "ok": is_ok,
            "error": error,
            "status_code": status_code
        }
        
        if is_ok:
            logger.info(f"✅ Endpoint {endpoint} respondeu (status {status_code})")
            results["overall_status"] = "healthy"
        else:
            logger.debug(f"⚠️  Endpoint {endpoint} não respondeu: {error}")
    
    # Se nenhum endpoint respondeu, mas porta está aberta
    if results["overall_status"] == "unknown":
        results["overall_status"] = "port_open_but_no_endpoint"
        logger.warning(f"⚠️  Porta {port} está aberta mas nenhum endpoint HTTP respondeu")
    
    return results


def diagnose_mcp_server(port: int = 5000, base_url: Optional[str] = None) -> Dict:
    """
    Diagnostica o servidor MCP (protocolo diferente, requer headers específicos).
    
    Args:
        port: Porta do servidor MCP (padrão: 5000)
        base_url: URL base (padrão: http://localhost:{port})
    
    Returns:
        Dicionário com resultados do diagnóstico
    """
    if base_url is None:
        base_url = f"http://localhost:{port}"
    
    parsed = urlparse(base_url)
    host = parsed.hostname or "localhost"
    
    logger.info(f"🔍 Diagnosticando servidor MCP em {base_url} (porta {port})")
    
    results = {
        "url": base_url,
        "port": port,
        "host": host,
        "port_open": False,
        "port_error": None,
        "overall_status": "unknown",
        "note": "MCP server requer headers específicos (Accept: text/event-stream) para funcionar corretamente"
    }
    
    # 1. Verificar se porta está aberta
    port_open, port_error = check_port_open(host, port)
    results["port_open"] = port_open
    results["port_error"] = port_error
    
    if not port_open:
        results["overall_status"] = "port_closed"
        logger.warning(f"❌ Porta MCP {port} não está aberta: {port_error}")
        return results
    
    logger.info(f"✅ Porta MCP {port} está aberta")
    
    # 2. Testar endpoint raiz (sem headers específicos - pode retornar 406, mas indica que servidor está rodando)
    try:
        response = requests.get(base_url, timeout=1.0, allow_redirects=False)
        # MCP pode retornar 404 ou 406, mas isso indica que o servidor está respondendo
        # 406 Not Acceptable é esperado quando não há headers Accept: text/event-stream
        if response.status_code in [200, 404, 406]:
            results["overall_status"] = "healthy"
            if response.status_code == 406:
                logger.info(f"✅ Servidor MCP está respondendo (status {response.status_code} - esperado sem headers corretos)")
            else:
                logger.info(f"✅ Servidor MCP está respondendo (status {response.status_code})")
        else:
            results["overall_status"] = "port_open_but_unexpected_response"
            logger.warning(f"⚠️  Servidor MCP respondeu com status inesperado: {response.status_code}")
    except Exception as e:
        results["overall_status"] = "port_open_but_no_response"
        logger.warning(f"⚠️  Porta MCP {port} está aberta mas não respondeu: {str(e)}")
    
    return results


def diagnose_all_servers(agents_config: List[Tuple[str, int]]) -> Dict:
    """
    Diagnostica todos os servidores configurados.
    
    Args:
        agents_config: Lista de tuplas (nome, porta)
    
    Returns:
        Dicionário com resultados de todos os servidores
    """
    logger.info("🔍 Iniciando diagnóstico completo de servidores...")
    
    results = {
        "servers": {},
        "summary": {
            "total": len(agents_config),
            "healthy": 0,
            "port_closed": 0,
            "port_open_but_no_endpoint": 0,
            "unknown": 0
        }
    }
    
    for name, port in agents_config:
        server_result = diagnose_agent_server(port)
        results["servers"][name] = server_result
        
        status = server_result["overall_status"]
        if status == "healthy":
            results["summary"]["healthy"] += 1
        elif status == "port_closed":
            results["summary"]["port_closed"] += 1
        elif status == "port_open_but_no_endpoint":
            results["summary"]["port_open_but_no_endpoint"] += 1
        else:
            results["summary"]["unknown"] += 1
    
    # Log resumo
    logger.info("📊 Resumo do diagnóstico:")
    logger.info(f"   ✅ Saudáveis: {results['summary']['healthy']}")
    logger.info(f"   ❌ Porta fechada: {results['summary']['port_closed']}")
    logger.info(f"   ⚠️  Porta aberta mas sem endpoint: {results['summary']['port_open_but_no_endpoint']}")
    logger.info(f"   ❓ Desconhecido: {results['summary']['unknown']}")
    
    return results


def format_diagnostic_report(results: Dict) -> str:
    """
    Formata resultados de diagnóstico em string legível.
    
    Args:
        results: Resultados do diagnóstico
    
    Returns:
        String formatada
    """
    lines = ["\n" + "=" * 80]
    lines.append("📋 RELATÓRIO DE DIAGNÓSTICO")
    lines.append("=" * 80)
    
    for name, server_result in results["servers"].items():
        lines.append(f"\n🔹 {name} (porta {server_result['port']})")
        lines.append(f"   URL: {server_result['url']}")
        lines.append(f"   Porta aberta: {'✅ Sim' if server_result['port_open'] else '❌ Não'}")
        
        if server_result['port_error']:
            lines.append(f"   Erro: {server_result['port_error']}")
        
        if server_result['endpoints']:
            lines.append("   Endpoints testados:")
            for ep_name, ep_result in server_result['endpoints'].items():
                status_icon = "✅" if ep_result['ok'] else "❌"
                lines.append(f"      {status_icon} {ep_result['url']}")
                if ep_result['status_code']:
                    lines.append(f"         Status: {ep_result['status_code']}")
                if ep_result['error']:
                    lines.append(f"         Erro: {ep_result['error']}")
        
        status = server_result['overall_status']
        status_map = {
            "healthy": "✅ Saudável",
            "port_closed": "❌ Porta fechada",
            "port_open_but_no_endpoint": "⚠️  Porta aberta mas sem endpoint HTTP",
            "unknown": "❓ Status desconhecido"
        }
        lines.append(f"   Status geral: {status_map.get(status, status)}")
    
    lines.append("\n" + "=" * 80)
    return "\n".join(lines)

