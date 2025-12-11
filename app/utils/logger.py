"""
Sistema de logging centralizado para DevMentor AI.
Fornece logging estruturado com diferentes níveis e formatação consistente.
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Formatter com cores para terminal."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(
    name: str = "devmentor",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    console: bool = True
) -> logging.Logger:
    """
    Configura logger com handlers para console e arquivo.
    
    Args:
        name: Nome do logger
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Caminho do arquivo de log (opcional)
        console: Se True, adiciona handler para console
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Formato de log
    detailed_format = (
        '%(asctime)s | %(levelname)-8s | %(name)s | '
        '%(filename)s:%(lineno)d | %(message)s'
    )
    simple_format = '%(asctime)s | %(levelname)-8s | %(message)s'
    
    # Handler para console (com cores)
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = ColoredFormatter(simple_format, datefmt='%H:%M:%S')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # Handler para arquivo (sem cores, mais detalhado)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Arquivo sempre DEBUG
        file_formatter = logging.Formatter(detailed_format, datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Obtém logger configurado. Se não existir, cria um novo.
    
    Args:
        name: Nome do logger (padrão: 'devmentor')
    
    Returns:
        Logger configurado
    """
    if name is None:
        name = "devmentor"
    
    logger = logging.getLogger(name)
    
    # Se logger não tem handlers, configura um padrão
    if not logger.handlers:
        setup_logger(name)
    
    return logger


# Logger padrão do sistema
default_logger = setup_logger("devmentor", level=logging.INFO)

