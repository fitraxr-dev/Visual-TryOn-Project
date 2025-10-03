# Panduan Integrasi Godot dengan Python Webcam Server

## Overview

Sistem ini terdiri dari:

1. **Python WebSocket Server** - Menangkap video dari webcam dan mengirim via WebSocket
2. **Godot Client** - Menerima dan menampilkan video stream dalam real-time

## Arsitektur Sistem

```
[Webcam] → [Python Server] → [WebSocket] → [Godot Client] → [Display]
         OpenCV            ws://localhost:8765      TextureRect
```

## Mekanisme Komunikasi

### 1. Protocol WebSocket

- **URL**: `ws://localhost:8765`
- **Port**: 8765 (dapat dikonfigurasi di `config.py`)
- **Format Data**:
  - **Text Messages**: JSON metadata (resolusi, FPS, format)
  - **Binary Messages**: JPEG frames dari webcam

### 2. Alur Data

1. **Server Startup**: Python server mulai menangkap webcam
2. **Client Connection**: Godot client connect ke WebSocket server
3. **Metadata Exchange**: Server mengirim info stream (resolusi, FPS)
4. **Frame Streaming**: Server mengirim JPEG frames secara kontinyu
5. **Client Processing**: Godot decode JPEG → Image → Texture → Display

## Cara Menjalankan Sistem

### Langkah 1: Menjalankan Python Server

```bash
cd webcam-server
pip install -r requirements.txt
python server/server.py
```

Output yang diharapkan:

```
[INFO] Camera initialized successfully
[INFO] Starting WebSocket server on 0.0.0.0:8765
[INFO] WebSocket server started successfully
```

### Langkah 2: Menjalankan Godot Client

1. Buka Godot project: `godot_virtual_tryon/`
2. Run scene: `Scenes/webcam_view.tscn`
3. Klik tombol "Connect to Webcam Server"

## Struktur File Godot

```
godot_virtual_tryon/
├── Scenes/
│   └── webcam_view.tscn          # Main scene untuk video display
├── Scripts/
│   ├── WebcamClient.gd           # WebSocket client implementation
│   └── WebcamViewController.gd   # UI controller untuk webcam view
└── project.godot
```

## Komponen Utama

### 1. WebcamClient.gd

**Fungsi Utama:**

- Mengelola koneksi WebSocket ke Python server
- Memproses metadata JSON dan binary JPEG frames
- Auto-reconnect jika koneksi terputus
- FPS monitoring dan statistik

**Signals:**

- `connected()` - Ketika koneksi berhasil
- `disconnected()` - Ketika koneksi terputus
- `frame_received(texture)` - Ketika frame baru diterima
- `metadata_received(metadata)` - Ketika metadata diterima
- `connection_error(error)` - Ketika terjadi error

**Methods:**

- `connect_to_server(url)` - Connect ke server
- `disconnect_from_server()` - Disconnect dari server
- `get_stream_info()` - Info stream (FPS, frame count, dll)

### 2. WebcamViewController.gd

**Fungsi Utama:**

- Controller untuk UI webcam view
- Menampilkan video stream di TextureRect
- Status monitoring dan informasi koneksi
- Button handling untuk connect/disconnect

**UI Elements:**

- `VideoDisplay` - TextureRect untuk menampilkan video
- `StatusLabel` - Label status koneksi
- `ConnectButton` - Button untuk connect
- `DisconnectButton` - Button untuk disconnect
- `InfoLabel` - Informasi stream (FPS, frame count, dll)

## Troubleshooting

### Common Issues

1. **Connection Failed**

```
Error: Failed to connect
```

**Solusi:**

- Pastikan Python server sudah berjalan
- Check port 8765 tidak digunakan aplikasi lain
- Pastikan firewall tidak memblokir koneksi

2. **JPEG Decode Error**

```
Error: Failed to decode JPEG frame
```

**Solusi:**

- Check kualitas koneksi network
- Verify webcam berfungsi dengan baik
- Restart server jika webcam bermasalah

3. **No Video Display**

```
Status: Connected, tapi tidak ada video
```

**Solusi:**

- Check webcam tidak digunakan aplikasi lain
- Verify `CAMERA_INDEX` di `config.py`
- Check log server untuk error messages

### Debug Mode

Untuk enable logging lebih detail:

**Di WebcamClient.gd:**

```gdscript
var enable_logging: bool = true
var log_frames: bool = true  # Log setiap frame
```

**Di Python server:**

```python
LOG_LEVEL = "DEBUG"  # di config.py
```

## Konfigurasi

### Server Configuration (config.py)

```python
# Server settings
SERVER_HOST = "0.0.0.0"    # Host server
SERVER_PORT = 8765         # Port server

# Camera settings
CAMERA_INDEX = 0           # Index webcam (0 = default)
DEFAULT_WIDTH = 640        # Resolusi width
DEFAULT_HEIGHT = 480       # Resolusi height
TARGET_FPS = 15           # Target FPS

# Quality settings
JPEG_QUALITY = 80         # Kualitas JPEG (1-100)
```

### Client Configuration (WebcamClient.gd)

```gdscript
# Server URL
var server_url: String = "ws://localhost:8765"

# Reconnection settings
var max_reconnect_attempts: int = 5
var reconnect_delay: float = 3.0

# Debug settings
var enable_logging: bool = true
var log_frames: bool = false
```

## Performance Optimization

### 1. Network Optimization

- **JPEG Quality**: Turunkan `JPEG_QUALITY` untuk koneksi lambat
- **Resolution**: Gunakan resolusi lebih kecil jika perlu
- **FPS**: Kurangi `TARGET_FPS` untuk mengurangi bandwidth

### 2. Client Optimization

- **Texture Reuse**: Consider reuse `ImageTexture` object
- **Frame Skipping**: Skip frames jika processing lambat
- **Memory Management**: Monitor memory usage untuk long sessions

### 3. Server Optimization

- **Buffer Management**: Adjust `FRAME_BUFFER_SIZE`
- **CPU Usage**: Monitor CPU usage webcam capture
- **Multiple Clients**: Server support hingga `MAX_CLIENTS`

## Extension Ideas

### 1. Computer Vision Integration

- Tambahkan face detection di server
- Kirim bounding box data ke client
- Implement virtual try-on effects

### 2. Recording Features

- Record video stream di client
- Save frames sebagai images
- Playback recorded sessions

### 3. Multiple Camera Support

- Support multiple webcam
- Camera switching di runtime
- Different resolutions per camera

## API Reference

### WebcamClient Methods

```gdscript
# Connection management
connect_to_server(url: String = "") -> bool
disconnect_from_server()

# Configuration
send_config_message(config: Dictionary)

# Status & Info
get_connection_status() -> String
get_stream_info() -> Dictionary
get_current_fps() -> float
```

### WebcamClient Signals

```gdscript
signal connected()
signal disconnected()
signal frame_received(texture: ImageTexture)
signal metadata_received(metadata: Dictionary)
signal connection_error(error: String)
```

### Metadata Format

```json
{
  "width": 640,
  "height": 480,
  "fps": 30,
  "format": "MJPEG",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Kesimpulan

Sistem ini menyediakan foundation yang solid untuk streaming webcam real-time antara Python server dan Godot client. Dengan arsitektur WebSocket yang fleksibel, sistem ini dapat dikembangkan lebih lanjut untuk berbagai aplikasi computer vision dan virtual try-on.
