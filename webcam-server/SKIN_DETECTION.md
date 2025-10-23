# Skin Detection Feature

## Overview

Fitur skin detection/segmentation untuk mendeteksi area tangan secara real-time menggunakan computer vision. Fitur ini menggunakan color space HSV untuk mendeteksi warna kulit dan menampilkan kontur tangan secara real-time di webcam stream.

## Fitur Utama

### 1. Skin Detection / Segmentation
- **Tujuan**: Mendapatkan binary mask area tangan
- **Metode**: Color thresholding dalam HSV color space
- **Output**: Binary mask dengan area kulit bernilai 255

### 2. Morphological Operations
- **Opening**: Menghilangkan noise kecil
- **Dilation**: Memperbesar area yang terdeteksi
- **Kernel Size**: Configurable (default: 5x5)

### 3. Contour Detection
- **Metode**: Deteksi kontur eksternal
- **Filter**: Berdasarkan minimum area
- **Output**: Kontur tangan terbesar

### 4. Real-time Visualization
- Kontur tangan digambar langsung di frame webcam
- Bounding box dengan informasi area
- Overlay berwarna hijau (default)

## Konfigurasi

### File: `server/config.py`

```python
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
```

## Cara Kerja

### 1. Skin Detection Process

```python
# Konversi ke HSV color space
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# Threshold untuk mendapatkan area kulit
lower_skin = np.array([0, 40, 60], dtype=np.uint8)
upper_skin = np.array([20, 150, 255], dtype=np.uint8)
mask = cv2.inRange(hsv, lower_skin, upper_skin)
```

### 2. Cleaning Mask

```python
# Morphological opening untuk menghilangkan noise
kernel = np.ones((5, 5), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)

# Dilasi untuk memperbesar area
mask = cv2.dilate(mask, kernel, iterations=1)
```

### 3. Contour Detection

```python
# Temukan semua kontur
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Pilih kontur terbesar (tangan)
if contours:
    cnt = max(contours, key=cv2.contourArea)
    
    # Filter berdasarkan minimum area
    if cv2.contourArea(cnt) >= MIN_CONTOUR_AREA:
        # Gambar kontur
        cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
```

## API Usage

### Camera Class

```python
from camera import Camera

camera = Camera()
await camera.initialize()

# Toggle skin detection
camera.toggle_skin_detection(True)

# Update skin range untuk kalibrasi
camera.update_skin_range(
    lower_hsv=[0, 40, 60],
    upper_hsv=[20, 150, 255]
)

# Set minimum contour area
camera.set_min_contour_area(1000)

# Get contour info
contour_info = await camera.get_contour_info()
```

### SkinDetector Class

```python
from skin_detector import SkinDetector

detector = SkinDetector()

# Process single frame
processed_frame, mask, contour = detector.process_frame(frame)

# Get contour information
if contour is not None:
    info = detector.get_contour_info(contour)
    print(f"Area: {info['area']}")
    print(f"Centroid: {info['centroid']}")
    print(f"Bounding Box: {info['bounding_box']}")
```

## WebSocket Protocol

### Client -> Server

#### Toggle Skin Detection
```json
{
  "type": "config",
  "skin_detection": true
}
```

#### Calibrate Skin Range
```json
{
  "type": "config",
  "skin_range": {
    "lower": [0, 40, 60],
    "upper": [20, 150, 255]
  }
}
```

#### Set Minimum Contour Area
```json
{
  "type": "config",
  "min_contour_area": 1000
}
```

### Server -> Client

#### Contour Information
```json
{
  "type": "contour_info",
  "data": {
    "area": 15000.5,
    "perimeter": 500.2,
    "bounding_box": {
      "x": 100,
      "y": 150,
      "width": 200,
      "height": 250
    },
    "centroid": {
      "x": 200,
      "y": 275
    }
  }
}
```

## Kalibrasi Warna Kulit

### Menggunakan Literatur (Default)
Nilai HSV yang umum digunakan untuk deteksi kulit:
- **Lower**: [0, 40, 60]
- **Upper**: [20, 150, 255]

### Kalibrasi Manual
Untuk hasil yang lebih akurat sesuai kondisi pencahayaan:

1. **Hue (H)**: 0-20 (merah-kuning untuk kulit)
2. **Saturation (S)**: 40-150 (cukup jenuh tapi tidak terlalu)
3. **Value (V)**: 60-255 (brightness)

### Tips Kalibrasi
- **Pencahayaan terang**: Tingkatkan lower V
- **Pencahayaan redup**: Turunkan lower V
- **Kulit lebih gelap**: Turunkan upper H, turunkan lower V
- **Kulit lebih terang**: Naikkan upper H, naikkan lower V

## Troubleshooting

### Tangan Tidak Terdeteksi
1. **Periksa pencahayaan**: Pastikan ruangan cukup terang
2. **Kalibrasi warna**: Sesuaikan HSV range dengan kondisi lighting
3. **Minimum area**: Turunkan `MIN_CONTOUR_AREA` jika tangan terlalu kecil
4. **Jarak kamera**: Posisikan tangan lebih dekat ke kamera

### Terlalu Banyak Noise
1. **Tingkatkan iterations**: Naikkan `MORPH_OPEN_ITERATIONS`
2. **Kernel size**: Perbesar `MORPH_KERNEL_SIZE`
3. **Minimum area**: Naikkan `MIN_CONTOUR_AREA`

### Performa Lambat
1. **Disable features**: Set `DRAW_CONTOURS = False`
2. **Lower resolution**: Turunkan resolusi webcam
3. **Iterations**: Kurangi morphological iterations

## Contoh Penggunaan

### Basic Usage
```python
import asyncio
from camera import Camera

async def main():
    camera = Camera()
    
    # Initialize camera
    if await camera.initialize():
        # Enable skin detection
        camera.toggle_skin_detection(True)
        
        # Start capture loop
        await camera.start_capture_loop()

asyncio.run(main())
```

### Advanced Usage with Custom Configuration
```python
from skin_detector import SkinDetector
import cv2

# Create detector with custom settings
detector = SkinDetector()
detector.update_skin_range([0, 50, 70], [20, 140, 245])
detector.set_min_contour_area(2000)
detector.toggle_bounding_box(True)

# Process video
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Process frame
    processed, mask, contour = detector.process_frame(frame)
    
    # Get contour info
    if contour is not None:
        info = detector.get_contour_info(contour)
        print(f"Hand detected - Area: {info['area']:.0f}, "
              f"Center: ({info['centroid']['x']}, {info['centroid']['y']})")
    
    # Display
    cv2.imshow('Processed', processed)
    cv2.imshow('Mask', mask)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

## Performance Metrics

### Typical Performance (640x480 @ 15 FPS)
- **Processing Time**: ~10-15ms per frame
- **CPU Usage**: ~10-15% (single core)
- **Memory**: ~50MB additional

### Optimization Recommendations
- Use lower resolution for faster processing
- Reduce morphological iterations if speed is critical
- Disable bounding box drawing for marginal performance gain

## Future Enhancements

1. **Multiple Hand Detection**: Support untuk mendeteksi kedua tangan
2. **Gesture Recognition**: Deteksi gesture berdasarkan kontur
3. **Hand Tracking**: Track movement tangan antar frame
4. **Adaptive Thresholding**: Auto-calibration berdasarkan kondisi lighting
5. **Machine Learning**: Integrasi dengan ML models untuk deteksi lebih akurat

## References

- OpenCV Documentation: https://docs.opencv.org/
- HSV Color Space: https://en.wikipedia.org/wiki/HSL_and_HSV
- Morphological Transformations: https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html
- Contour Detection: https://docs.opencv.org/4.x/d3/d05/tutorial_py_table_of_contents_contours.html
