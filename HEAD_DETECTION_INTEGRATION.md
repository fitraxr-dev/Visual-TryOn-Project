# Head Detection Integration Guide

## Overview

Proyek Virtual TryOn ini telah diintegrasikan dengan sistem head detection menggunakan cascade classifiers yang telah dilatih dengan dataset BIWI Kinect Head Pose Database. Sistem ini memungkinkan deteksi kepala secara real-time dan overlay topi virtual melalui webcam.

## Features

### 🎯 Head Detection
- **Multiple Cascade Classifiers**:
  - **HAAR Biwi**: Cascade classifier trained dengan HAAR features untuk akurasi tinggi
  - **LBP Biwi**: Cascade classifier trained dengan LBP features untuk performa lebih cepat
  - **OpenCV Default**: Fallback menggunakan haarcascade_frontalface_default dari OpenCV
  
### 🎩 Virtual Hat Try-On
- Real-time hat overlay pada kepala yang terdeteksi
- Multiple hat models yang dapat diganti secara dinamis
- Alpha blending untuk hasil overlay yang natural
- Automatic positioning dan scaling berdasarkan ukuran kepala

### 🎮 Interactive Controls
- Toggle head detection on/off
- Switch cascade classifier secara real-time
- Navigate through different hat models
- Real-time feedback di UI Godot

## Architecture

```
Visual-TryOn-Project/
├── webcam-server/
│   ├── server/
│   │   ├── server.py          # WebSocket server dengan head detection config handler
│   │   ├── camera.py          # Camera module dengan head detection integration
│   │   ├── head_detector.py   # Head detection & hat overlay logic (NEW)
│   │   └── ...
│   ├── models/                # Cascade classifiers (NEW)
│   │   ├── haar_biwi_cascade.xml
│   │   └── lbp_biwi_cascade.xml
│   ├── assets/                # Hat images (NEW)
│   │   └── hats/
│   │       ├── hat_1.png
│   │       └── hat_2.png
│   └── DATASET_INFO.md        # Dataset documentation (NEW)
└── godot_virtual_tryon/
    └── Scripts/
        ├── WebcamClient.gd            # Extended dengan head detection controls
        └── WebcamViewController.gd    # UI dengan head detection controls
```

## How It Works

### Backend (Python WebSocket Server)

1. **HeadDetector Class** (`head_detector.py`):
   - Load cascade classifiers dari folder `models/`
   - Load hat images dari folder `assets/hats/`
   - Provide methods untuk detect heads dan overlay hats
   - Support switching cascade dan hat secara dinamis

2. **Camera Integration** (`camera.py`):
   - HeadDetector instance dibuat saat camera initialization
   - Setiap frame dari webcam diproses melalui HeadDetector
   - Frame dengan hat overlay di-encode ke JPEG dan dikirim ke clients

3. **Server Config Handler** (`server.py`):
   - Menerima config messages dari Godot client
   - Handle commands: `head_detection`, `cascade_type`, `hat_index`, `next_hat`, `previous_hat`
   - Forward commands ke Camera/HeadDetector instances

### Frontend (Godot Client)

1. **WebcamClient Extension** (`WebcamClient.gd`):
   - Methods untuk send head detection config: `toggle_head_detection()`, `set_cascade()`, `next_hat()`, dll
   - Send config via JSON messages ke WebSocket server

2. **UI Controls** (`WebcamViewController.gd`):
   - CheckButton untuk enable/disable head detection
   - OptionButton untuk select cascade classifier
   - Buttons untuk navigate hat models
   - Real-time info display

## Usage

### Starting the Server

```bash
cd webcam-server
python server/server.py
```

Server akan:
- Load cascade classifiers dari `models/`
- Load hat images dari `assets/hats/`
- Start WebSocket server di `localhost:8765`

### Using Godot Client

1. **Connect to Server**:
   - Click "Connect" button di Godot UI
   - Webcam stream akan mulai ditampilkan

2. **Enable Head Detection**:
   - Check "Enable Head Detection" checkbox
   - Kepala akan terdeteksi dan ditandai dengan bounding box
   - Topi akan otomatis di-overlay

3. **Switch Cascade Classifier**:
   - Select cascade dari dropdown:
     - "HAAR Biwi" - Akurasi tinggi, sedikit lebih lambat
     - "LBP Biwi" - Lebih cepat, akurasi sedikit menurun
     - "OpenCV Default" - Fallback option

4. **Change Hat Model**:
   - Click "Next >" untuk topi berikutnya
   - Click "< Previous" untuk topi sebelumnya
   - Hat akan langsung berganti di preview

## WebSocket Protocol Extension

### Head Detection Config Messages

Client mengirim config message dengan format:

```json
{
  "type": "config",
  "data": {
    "head_detection": true,
    "cascade_type": "haar_biwi",
    "hat_index": 0,
    "next_hat": false,
    "previous_hat": false
  }
}
```

**Parameters**:
- `head_detection` (bool): Enable/disable head detection
- `cascade_type` (string): "haar_biwi" | "lbp_biwi" | "opencv_default"
- `hat_index` (int): Index topi (0-based)
- `next_hat` (bool): Trigger switch ke topi berikutnya
- `previous_hat` (bool): Trigger switch ke topi sebelumnya

## Adding New Hats

Untuk menambahkan topi baru:

1. Prepare gambar topi dalam format PNG dengan alpha channel (transparency)
2. Copy file ke folder `webcam-server/assets/hats/`
3. Restart server
4. Hat baru akan otomatis ter-load dan bisa dipilih

**Rekomendasi format hat image**:
- Format: PNG dengan alpha channel
- Resolusi: Minimal 512x512 pixels
- Background: Transparent
- Konten: Topi menghadap depan (front view)

## Training Custom Cascade Classifiers

Jika ingin training cascade classifier sendiri:

1. Download BIWI dataset dari: https://www.kaggle.com/datasets/kmader/biwi-kinect-head-pose-database
2. Prepare positive samples dari dataset
3. Prepare negative samples (background images)
4. Use OpenCV's `opencv_traincascade` tool
5. Copy hasil cascade.xml ke `webcam-server/models/`

Lihat dokumentasi di `DATASET_INFO.md` untuk detail lebih lanjut.

## Performance Tips

### Cascade Selection
- **HAAR Biwi**: Gunakan untuk akurasi maksimal, cocok untuk hardware yang powerful
- **LBP Biwi**: Gunakan untuk real-time performance di hardware terbatas
- **OpenCV Default**: Fallback option, sudah pre-trained di OpenCV

### Detection Parameters
Edit di `head_detector.py`:
```python
self.scale_factor = 1.1      # Smaller = more detections, slower
self.min_neighbors = 3       # Higher = fewer false positives
self.min_size = (60, 60)     # Minimum head size to detect
```

## Troubleshooting

### Head tidak terdeteksi
- Pastikan lighting cukup terang
- Wajah menghadap kamera (frontal view)
- Coba cascade classifier berbeda
- Adjust `min_neighbors` parameter lebih rendah

### Performance lambat
- Switch ke LBP cascade
- Turunkan resolusi webcam
- Increase `scale_factor` parameter

### Hat tidak pas di kepala
- Edit multiplier di `head_detector.py`:
  ```python
  hat_width = int(w * 1.5)   # Adjust width multiplier
  hat_height = int(h * 1.5)  # Adjust height multiplier
  hat_y = int(y - hat_height * 0.6)  # Adjust vertical position
  ```

## Credits

- **Dataset**: BIWI Kinect Head Pose Database (Kaggle)
- **Cascade Training**: OpenCV traincascade
- **Integration**: Visual TryOn Project Team

## License

Lihat file LICENSE di root project untuk informasi lisensi.
