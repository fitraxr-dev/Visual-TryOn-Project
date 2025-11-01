"""
Utility functions untuk Webcam WebSocket Server
"""

import json
import logging
from typing import Dict, Any

def setup_logging(level: str = "INFO", format_str: str = None) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_str: Log format string
    
    Returns:
        Logger instance
    """
    if format_str is None:
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_str,
        handlers=[
            logging.StreamHandler(),
        ]
    )
    
    return logging.getLogger(__name__)

def create_metadata_message(width: int, height: int, fps: int) -> str:
    """
    Buat pesan metadata dalam format JSON
    
    Args:
        width: Lebar frame
        height: Tinggi frame
        fps: Frame per second
    
    Returns:
        JSON string metadata
    """
    metadata = {
        "type": "meta",
        "width": width,
        "height": height,
        "fps": fps
    }
    return json.dumps(metadata)

def parse_client_message(message: str) -> Dict[str, Any]:
    """
    Parse pesan JSON dari client
    
    Args:
        message: Raw message dari client
    
    Returns:
        Dictionary berisi parsed message, atau None jika parsing gagal
    """
    try:
        return json.loads(message)
    except json.JSONDecodeError as e:
        logging.warning(f"Failed to parse client message: {e}")
        return None

def validate_resolution(width: int, height: int) -> tuple[int, int]:
    """
    Validasi dan perbaiki resolusi video
    
    Args:
        width: Lebar yang diminta
        height: Tinggi yang diminta
    
    Returns:
        Tuple (width, height) yang valid
    """
    # Minimum resolution
    min_width, min_height = 160, 120
    # Maximum resolution
    max_width, max_height = 1920, 1080
    
    width = max(min_width, min(max_width, width))
    height = max(min_height, min(max_height, height))
    
    return width, height

def validate_fps(fps: int) -> int:
    """
    Validasi dan perbaiki FPS
    
    Args:
        fps: FPS yang diminta
    
    Returns:
        FPS yang valid (1-60)
    """
    return max(1, min(60, fps))

def bytes_to_mb(bytes_size: int) -> float:
    """
    Convert bytes ke megabytes
    
    Args:
        bytes_size: Size dalam bytes
    
    Returns:
        Size dalam MB
    """
    return bytes_size / (1024 * 1024)