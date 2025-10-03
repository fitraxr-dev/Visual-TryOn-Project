"""
Konfigurasi untuk Webcam WebSocket Server
"""

# Server Configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8765

# Camera Configuration
CAMERA_INDEX = 0  # Default camera (0 = primary camera)
DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480
TARGET_FPS = 15

# JPEG Encoding Configuration
JPEG_QUALITY = 80  # 1-100, higher = better quality but larger file size

# Server Behavior
MAX_CLIENTS = 10  # Maximum simultaneous clients
FRAME_BUFFER_SIZE = 1  # Number of frames to buffer

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Performance Settings
CAMERA_LOOP_DELAY = 0.01  # Delay between camera reads (seconds)
BROADCAST_DELAY = 1.0 / TARGET_FPS  # Delay between broadcasts to clients