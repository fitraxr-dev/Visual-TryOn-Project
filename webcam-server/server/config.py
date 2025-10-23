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

# Skin Detection Configuration
ENABLE_SKIN_DETECTION = True  # Enable/disable skin detection feature
SKIN_LOWER_HSV = [0, 40, 60]  # Lower bound for skin color in HSV
SKIN_UPPER_HSV = [20, 150, 255]  # Upper bound for skin color in HSV

# Morphological Operations Configuration
MORPH_KERNEL_SIZE = 5  # Kernel size for morphological operations
MORPH_OPEN_ITERATIONS = 2  # Number of iterations for morphological opening
MORPH_DILATE_ITERATIONS = 1  # Number of iterations for dilation

# Contour Detection Configuration
MIN_CONTOUR_AREA = 1000  # Minimum area for a valid hand contour
DRAW_CONTOURS = True  # Draw contours on the frame
CONTOUR_COLOR = [0, 255, 0]  # Color for drawing contours (BGR: Green)
CONTOUR_THICKNESS = 2  # Thickness of contour lines

# Skin Detection Display Options
SHOW_MASK = False  # Show binary mask alongside original frame
SHOW_BOUNDING_BOX = True  # Show bounding box around detected hand