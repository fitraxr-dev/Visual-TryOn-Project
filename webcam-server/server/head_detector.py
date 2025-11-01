"""
Head Detector module untuk deteksi kepala dan overlay topi
"""

import cv2
import numpy as np
import os
import glob
import logging
from typing import Optional, List, Tuple

class HeadDetector:
    """
    Class untuk deteksi kepala menggunakan cascade classifier dan overlay topi
    """
    
    # Cascade types
    CASCADE_HAAR_BIWI = "haar_biwi"
    CASCADE_LBP_BIWI = "lbp_biwi"
    CASCADE_OPENCV_DEFAULT = "opencv_default"
    
    def __init__(self):
        """
        Initialize HeadDetector
        """
        self.logger = logging.getLogger(__name__)
        self.cascades = {}
        self.current_cascade_type = self.CASCADE_HAAR_BIWI
        self.current_cascade = None
        
        # Hat images
        self.hat_images = []
        self.current_hat_idx = 0
        self.current_hat = None
        
        # Detection parameters
        self.scale_factor = 1.1
        self.min_neighbors = 3
        self.min_size = (60, 60)
        
        # Enable/disable detection - DEFAULT TRUE untuk langsung jalan!
        self.enabled = True
        
        # Load cascades and hats
        self._load_cascades()
        self._load_hats()
    
    def _load_cascades(self):
        """
        Load semua cascade classifiers
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(base_dir, "..", "models")
        
        # Load HAAR Biwi
        haar_path = os.path.join(models_dir, "haar_biwi_cascade.xml")
        if os.path.exists(haar_path):
            self.cascades[self.CASCADE_HAAR_BIWI] = cv2.CascadeClassifier(haar_path)
            self.logger.info(f"✓ HAAR Biwi cascade loaded from {haar_path}")
        else:
            self.logger.warning(f"✗ HAAR Biwi cascade not found at {haar_path}")
        
        # Load LBP Biwi
        lbp_path = os.path.join(models_dir, "lbp_biwi_cascade.xml")
        if os.path.exists(lbp_path):
            self.cascades[self.CASCADE_LBP_BIWI] = cv2.CascadeClassifier(lbp_path)
            self.logger.info(f"✓ LBP Biwi cascade loaded from {lbp_path}")
        else:
            self.logger.warning(f"✗ LBP Biwi cascade not found at {lbp_path}")
        
        # Load OpenCV default (haarcascade_frontalface_default)
        opencv_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        if os.path.exists(opencv_path):
            self.cascades[self.CASCADE_OPENCV_DEFAULT] = cv2.CascadeClassifier(opencv_path)
            self.logger.info(f"✓ OpenCV default cascade loaded")
        else:
            self.logger.warning(f"✗ OpenCV default cascade not found")
        
        # Set current cascade
        if self.current_cascade_type in self.cascades:
            self.current_cascade = self.cascades[self.current_cascade_type]
            self.logger.info(f"Current cascade: {self.current_cascade_type}")
        else:
            self.logger.error("No cascade loaded!")
    
    def _load_hats(self):
        """
        Load semua gambar topi dari folder assets/hats
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        hats_dir = os.path.join(base_dir, "..", "assets", "hats")
        
        if not os.path.exists(hats_dir):
            self.logger.warning(f"Hats directory not found: {hats_dir}")
            return
        
        # Load semua file PNG
        hat_files = sorted(glob.glob(os.path.join(hats_dir, "*.png")))
        
        for hat_file in hat_files:
            hat_img = cv2.imread(hat_file, cv2.IMREAD_UNCHANGED)
            if hat_img is not None:
                self.hat_images.append({
                    "name": os.path.basename(hat_file),
                    "image": hat_img
                })
                self.logger.info(f"✓ Hat loaded: {os.path.basename(hat_file)}")
        
        if self.hat_images:
            self.current_hat = self.hat_images[0]
            self.logger.info(f"Current hat: {self.current_hat['name']}")
        else:
            self.logger.warning("No hat images found")
    
    def set_cascade(self, cascade_type: str) -> bool:
        """
        Set cascade classifier yang akan digunakan
        
        Args:
            cascade_type: Tipe cascade (haar_biwi, lbp_biwi, opencv_default)
            
        Returns:
            True jika berhasil, False jika gagal
        """
        if cascade_type not in self.cascades:
            self.logger.error(f"Cascade type not found: {cascade_type}")
            return False
        
        self.current_cascade_type = cascade_type
        self.current_cascade = self.cascades[cascade_type]
        self.logger.info(f"Cascade changed to: {cascade_type}")
        return True
    
    def set_hat(self, hat_index: int) -> bool:
        """
        Set topi yang akan digunakan
        
        Args:
            hat_index: Index topi (0-based)
            
        Returns:
            True jika berhasil, False jika gagal
        """
        if not self.hat_images:
            self.logger.error("No hat images available")
            return False
        
        if hat_index < 0 or hat_index >= len(self.hat_images):
            self.logger.error(f"Invalid hat index: {hat_index}")
            return False
        
        self.current_hat_idx = hat_index
        self.current_hat = self.hat_images[hat_index]
        self.logger.info(f"Hat changed to: {self.current_hat['name']}")
        return True
    
    def next_hat(self) -> bool:
        """
        Switch ke topi berikutnya
        
        Returns:
            True jika berhasil, False jika tidak ada topi
        """
        if not self.hat_images:
            return False
        
        self.current_hat_idx = (self.current_hat_idx + 1) % len(self.hat_images)
        self.current_hat = self.hat_images[self.current_hat_idx]
        self.logger.info(f"Hat changed to: {self.current_hat['name']}")
        return True
    
    def previous_hat(self) -> bool:
        """
        Switch ke topi sebelumnya
        
        Returns:
            True jika berhasil, False jika tidak ada topi
        """
        if not self.hat_images:
            return False
        
        self.current_hat_idx = (self.current_hat_idx - 1) % len(self.hat_images)
        self.current_hat = self.hat_images[self.current_hat_idx]
        self.logger.info(f"Hat changed to: {self.current_hat['name']}")
        return True
    
    def detect_heads(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Deteksi kepala pada frame
        
        Args:
            frame: Frame RGB/BGR dari kamera
            
        Returns:
            List of (x, y, w, h) untuk setiap kepala yang terdeteksi
        """
        if self.current_cascade is None:
            return []
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect heads
        heads = self.current_cascade.detectMultiScale(
            gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=self.min_size
        )
        
        return heads
    
    def overlay_hat(self, frame: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
        """
        Overlay topi pada kepala yang terdeteksi
        
        Args:
            frame: Frame BGR
            x, y, w, h: Koordinat dan ukuran kepala
            
        Returns:
            Frame dengan topi yang di-overlay
        """
        if self.current_hat is None:
            return frame
        
        hat_img = self.current_hat["image"]
        
        if hat_img is None or hat_img.shape[2] != 4:
            return frame
        
        # Ukuran topi relatif terhadap ukuran kepala
        hat_width = int(w * 1.5)  # Topi lebih lebar dari kepala
        hat_height = int(h * 1.5)  # Tinggi topi
        
        # Resize topi
        hat_resized = cv2.resize(hat_img, (hat_width, hat_height))
        
        # Posisi topi di atas kepala
        hat_x = int(x + (w - hat_width) / 2)  # Center horizontally
        hat_y = int(y - hat_height * 0.6)  # Di atas kepala
        
        # Pastikan topi tidak keluar dari frame
        hat_x = max(0, hat_x)
        hat_y = max(0, hat_y)
        
        # Hitung ROI di frame
        hat_x_end = min(frame.shape[1], hat_x + hat_width)
        hat_y_end = min(frame.shape[0], hat_y + hat_height)
        
        # Hitung ukuran topi yang valid
        valid_hat_width = hat_x_end - hat_x
        valid_hat_height = hat_y_end - hat_y
        
        if valid_hat_width <= 0 or valid_hat_height <= 0:
            return frame
        
        # Extract alpha channel
        hat_bgr = hat_resized[:valid_hat_height, :valid_hat_width, :3]
        hat_alpha = hat_resized[:valid_hat_height, :valid_hat_width, 3:4] / 255.0
        
        # Ambil ROI dari frame
        frame_roi = frame[hat_y:hat_y_end, hat_x:hat_x_end]
        
        # Overlay dengan alpha blending
        frame[hat_y:hat_y_end, hat_x:hat_x_end] = (
            hat_bgr * hat_alpha + frame_roi * (1 - hat_alpha)
        ).astype(np.uint8)
        
        return frame
    
    def process_frame(self, frame: np.ndarray, draw_bbox: bool = True) -> Tuple[np.ndarray, List]:
        """
        Process frame: deteksi kepala dan overlay topi
        
        Args:
            frame: Frame BGR dari kamera
            draw_bbox: Jika True, gambar bounding box pada kepala (default True)
            
        Returns:
            Tuple of (processed_frame, detected_heads)
        """
        if not self.enabled:
            return frame, []
        
        # Detect heads
        heads = self.detect_heads(frame)
        
        # Process setiap kepala yang terdeteksi
        for (x, y, w, h) in heads:
            # Overlay topi
            frame = self.overlay_hat(frame, x, y, w, h)
            
            # Draw bounding box - SELALU digambar by default seperti webcam_detection.py
            if draw_bbox:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, "Head", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame, heads
    
    def toggle_detection(self, enable: bool):
        """
        Enable/disable head detection
        
        Args:
            enable: True untuk enable, False untuk disable
        """
        self.enabled = enable
        self.logger.info(f"Head detection {'enabled' if enable else 'disabled'}")
    
    def get_info(self) -> dict:
        """
        Dapatkan informasi head detector
        
        Returns:
            Dictionary berisi informasi detector
        """
        return {
            "enabled": self.enabled,
            "cascade_type": self.current_cascade_type,
            "available_cascades": list(self.cascades.keys()),
            "current_hat": self.current_hat["name"] if self.current_hat else None,
            "current_hat_index": self.current_hat_idx,
            "total_hats": len(self.hat_images),
            "available_hats": [hat["name"] for hat in self.hat_images]
        }
