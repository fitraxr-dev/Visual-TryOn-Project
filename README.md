# Visual TryOn Project

Real-time virtual try-on system menggunakan webcam dengan head detection dan hat overlay. Dibangun dengan Python WebSocket server dan Godot client.

## 🎯 Features

### Core Features
- **Real-time Webcam Streaming**: Stream video dari webcam melalui WebSocket
- **Head Detection**: Deteksi kepala menggunakan cascade classifiers trained dengan BIWI dataset
- **Virtual Hat Try-On**: Overlay topi virtual pada kepala dengan alpha blending
- **Skin Detection**: Deteksi dan tracking tangan (optional)
- **Dynamic Controls**: Switch cascade dan hat models secara real-time

### Technical Features
- WebSocket-based communication
- JPEG compression untuk efficient streaming
- Multiple cascade classifiers (HAAR, LBP, OpenCV default)
- Godot 4.x client dengan interactive UI
- Extensible architecture untuk additional features

## 📁 Project Structure

```
Visual-TryOn-Project/
├── webcam-server/              # Python WebSocket Server
│   ├── server/
│   │   ├── server.py          # Main WebSocket server
│   │   ├── camera.py          # Camera capture & processing
│   │   ├── head_detector.py   # Head detection & hat overlay
│   │   ├── skin_detector.py   # Skin detection (optional)
│   │   ├── config.py          # Configuration
│   │   └── utils.py           # Utilities
│   ├── models/                # Cascade classifiers
│   │   ├── haar_biwi_cascade.xml
│   │   └── lbp_biwi_cascade.xml
│   ├── assets/
│   │   └── hats/              # Hat images (PNG with alpha)
│   ├── requirements.txt       # Python dependencies
│   └── DATASET_INFO.md        # Dataset documentation
│
├── godot_virtual_tryon/       # Godot Client
│   ├── Scenes/
│   │   └── webcam_view.tscn  # Main scene
│   ├── Scripts/
│   │   ├── WebcamClient.gd           # WebSocket client
│   │   └── WebcamViewController.gd   # UI controller
│   └── project.godot
│
└── Documentation/
    ├── QUICK_START.md                    # Quick start guide
    ├── WEBSOCKET_PROTOCOL.md             # Protocol documentation
    ├── HEAD_DETECTION_INTEGRATION.md     # Head detection guide
    ├── INTEGRATION_SUMMARY.md            # Integration summary
    └── GODOT_INTEGRATION_GUIDE.md        # Godot integration guide
```

## 🚀 Quick Start

### Prerequisites

**Python Server:**
- Python 3.8+
- OpenCV (`opencv-python`)
- WebSockets (`websockets`)
- NumPy

**Godot Client:**
- Godot Engine 4.x

### Installation

#### 1. Setup Python Server

```bash
cd webcam-server
pip install -r requirements.txt
```

#### 2. Start Server

```bash
python server/server.py
```

Server akan berjalan di `localhost:8765`

#### 3. Launch Godot Client

1. Open Godot Engine
2. Import project: `godot_virtual_tryon/project.godot`
3. Run `Scenes/webcam_view.tscn`
4. Click "Connect" button

### Basic Usage

1. **Connect to Server**
   - Launch server terlebih dahulu
   - Click "Connect" di Godot UI
   - Webcam stream akan muncul

2. **Enable Head Detection**
   - Check "Enable Head Detection" checkbox
   - Kepala akan terdeteksi dan topi akan di-overlay

3. **Switch Cascade**
   - Select cascade dari dropdown:
     - HAAR Biwi (akurasi tinggi)
     - LBP Biwi (performa cepat)
     - OpenCV Default (fallback)

4. **Change Hat**
   - Click "< Previous" atau "Next >" untuk ganti topi
   - Hat akan langsung berganti

## 📖 Documentation

- **[QUICK_START.md](QUICK_START.md)**: Panduan lengkap quick start
- **[HEAD_DETECTION_INTEGRATION.md](HEAD_DETECTION_INTEGRATION.md)**: Detail integrasi head detection
- **[INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)**: Summary integrasi complete
- **[WEBSOCKET_PROTOCOL.md](WEBSOCKET_PROTOCOL.md)**: WebSocket protocol specification
- **[GODOT_INTEGRATION_GUIDE.md](GODOT_INTEGRATION_GUIDE.md)**: Godot integration guide
- **[DATASET_INFO.md](webcam-server/DATASET_INFO.md)**: Dataset & training information

## 🎓 Dataset & Training

Head detection menggunakan cascade classifiers yang telah dilatih dengan **BIWI Kinect Head Pose Database**.

- **Dataset Source**: https://www.kaggle.com/datasets/kmader/biwi-kinect-head-pose-database
- **Training Method**: OpenCV traincascade
- **Models**: HAAR features & LBP features

Lihat [DATASET_INFO.md](webcam-server/DATASET_INFO.md) untuk detail lengkap.

## 🔧 Configuration

### Server Configuration

Edit `webcam-server/server/config.py`:

```python
# Server settings
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8765

# Camera settings
DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480
JPEG_QUALITY = 85

# Head detection
ENABLE_HEAD_DETECTION = True
```

### Detection Parameters

Edit `webcam-server/server/head_detector.py`:

```python
# Detection sensitivity
self.scale_factor = 1.1      # Smaller = more sensitive
self.min_neighbors = 3       # Higher = fewer false positives
self.min_size = (60, 60)     # Minimum head size

# Hat positioning
hat_width = int(w * 1.5)     # Width multiplier
hat_height = int(h * 1.5)    # Height multiplier
hat_y = int(y - hat_height * 0.6)  # Vertical offset
```

## 🎩 Adding Custom Hats

1. Prepare PNG image dengan alpha channel (transparency)
2. Place di folder `webcam-server/assets/hats/`
3. Restart server
4. Hat baru akan otomatis ter-load

**Rekomendasi**:
- Format: PNG with alpha channel
- Size: 512x512 pixels atau lebih
- Orientation: Front-facing

## 🐛 Troubleshooting

### Head tidak terdeteksi
- Pastikan lighting cukup
- Wajah menghadap kamera (frontal)
- Coba cascade berbeda (HAAR/LBP)
- Reduce `min_neighbors` parameter

### Performance lambat
- Switch ke LBP cascade (lebih cepat)
- Reduce resolusi webcam
- Increase `scale_factor`

### Connection failed
- Pastikan server sudah running
- Check firewall settings
- Verify port 8765 tidak digunakan

Lihat [HEAD_DETECTION_INTEGRATION.md](HEAD_DETECTION_INTEGRATION.md) untuk troubleshooting lengkap.

## 🏗️ Architecture

### System Flow

```
Webcam → Camera Capture → Head Detection → Hat Overlay → JPEG Encode → WebSocket → Godot Display
```

### Communication Protocol

Client → Server:
```json
{
  "type": "config",
  "data": {
    "head_detection": true,
    "cascade_type": "haar_biwi",
    "next_hat": true
  }
}
```

Server → Client:
- Binary frames (JPEG)
- JSON metadata

Lihat [WEBSOCKET_PROTOCOL.md](WEBSOCKET_PROTOCOL.md) untuk detail protokol.

## 🛠️ Development

### Running Tests

```bash
cd webcam-server
python -m pytest tests/
```

### Adding New Features

1. Backend: Extend `camera.py` atau create new module
2. Frontend: Update `WebcamClient.gd` dan `WebcamViewController.gd`
3. Protocol: Update WebSocket message handlers

### Code Structure

- **Modular design**: Each component independent
- **Event-driven**: WebSocket + Godot signals
- **Extensible**: Easy to add new features

## 📊 Performance

- **Streaming FPS**: Up to 30 FPS (configurable)
- **Detection latency**: ~30-50ms (depending on cascade)
- **Network latency**: <10ms (local)
- **Memory usage**: ~200-300MB

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the project
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## 📝 License

[Specify your license here]

## 👥 Credits

- **Dataset**: BIWI Kinect Head Pose Database (Kaggle)
- **Framework**: OpenCV, Godot Engine
- **Development**: [Your team/name]

## 📞 Contact

[Your contact information]

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: November 1, 2025
