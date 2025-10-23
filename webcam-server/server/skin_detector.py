"""
Skin Detection module untuk mendeteksi dan segmentasi area kulit (tangan)
"""

import cv2
import numpy as np
import logging
from typing import Optional, Tuple, List

from config import (
    SKIN_LOWER_HSV, SKIN_UPPER_HSV,
    MORPH_KERNEL_SIZE, MORPH_OPEN_ITERATIONS, MORPH_DILATE_ITERATIONS,
    MIN_CONTOUR_AREA, DRAW_CONTOURS, CONTOUR_COLOR, CONTOUR_THICKNESS,
    SHOW_BOUNDING_BOX
)


class SkinDetector:
    """
    Class untuk mendeteksi dan segmentasi area kulit pada gambar
    """
    
    def __init__(self):
        """
        Initialize skin detector dengan parameter default dari config
        """
        self.logger = logging.getLogger(__name__)
        
        # HSV color range untuk skin detection
        self.lower_skin = np.array(SKIN_LOWER_HSV, dtype=np.uint8)
        self.upper_skin = np.array(SKIN_UPPER_HSV, dtype=np.uint8)
        
        # Morphological operation kernel
        self.kernel = np.ones((MORPH_KERNEL_SIZE, MORPH_KERNEL_SIZE), np.uint8)
        
        # Configuration
        self.morph_open_iterations = MORPH_OPEN_ITERATIONS
        self.morph_dilate_iterations = MORPH_DILATE_ITERATIONS
        self.min_contour_area = MIN_CONTOUR_AREA
        self.draw_contours = DRAW_CONTOURS
        self.contour_color = tuple(CONTOUR_COLOR)
        self.contour_thickness = CONTOUR_THICKNESS
        self.show_bounding_box = SHOW_BOUNDING_BOX
        
        self.logger.info("SkinDetector initialized")
    
    def detect_skin(self, frame: np.ndarray) -> np.ndarray:
        """
        Deteksi area kulit pada frame dan return binary mask
        
        Args:
            frame: Input frame dalam format BGR
            
        Returns:
            Binary mask dengan area kulit bernilai 255
        """
        # Konversi ke HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Threshold untuk mendapatkan area kulit
        mask = cv2.inRange(hsv, self.lower_skin, self.upper_skin)
        
        # Bersihkan noise dengan morphological operations
        mask = self.clean_mask(mask)
        
        return mask
    
    def clean_mask(self, mask: np.ndarray) -> np.ndarray:
        """
        Bersihkan binary mask dengan morphological operations
        
        Args:
            mask: Binary mask input
            
        Returns:
            Cleaned binary mask
        """
        # Morphological opening (erosion diikuti dilation) untuk menghilangkan noise
        mask = cv2.morphologyEx(
            mask, 
            cv2.MORPH_OPEN, 
            self.kernel, 
            iterations=self.morph_open_iterations
        )
        
        # Dilasi untuk memperbesar area yang terdeteksi
        mask = cv2.dilate(
            mask, 
            self.kernel, 
            iterations=self.morph_dilate_iterations
        )
        
        return mask
    
    def find_largest_contour(self, mask: np.ndarray) -> Optional[np.ndarray]:
        """
        Temukan kontur terbesar dari binary mask (diasumsikan sebagai tangan)
        
        Args:
            mask: Binary mask
            
        Returns:
            Kontur terbesar atau None jika tidak ada kontur yang valid
        """
        # Temukan semua kontur
        contours, _ = cv2.findContours(
            mask, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        if not contours:
            return None
        
        # Filter kontur berdasarkan area minimum
        valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= self.min_contour_area]
        
        if not valid_contours:
            return None
        
        # Pilih kontur dengan area terbesar
        largest_contour = max(valid_contours, key=cv2.contourArea)
        
        return largest_contour
    
    def draw_contour_on_frame(self, frame: np.ndarray, contour: np.ndarray) -> np.ndarray:
        """
        Gambar kontur pada frame
        
        Args:
            frame: Input frame
            contour: Kontur yang akan digambar
            
        Returns:
            Frame dengan kontur yang telah digambar
        """
        result_frame = frame.copy()
        
        # Gambar kontur
        cv2.drawContours(
            result_frame, 
            [contour], 
            -1, 
            self.contour_color, 
            self.contour_thickness
        )
        
        # Gambar bounding box jika diaktifkan
        if self.show_bounding_box:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(
                result_frame, 
                (x, y), 
                (x + w, y + h), 
                self.contour_color, 
                2
            )
            
            # Tambahkan label area
            area = cv2.contourArea(contour)
            label = f"Area: {int(area)}"
            cv2.putText(
                result_frame,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.contour_color,
                2
            )
        
        return result_frame
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Process frame lengkap: deteksi kulit, temukan kontur, dan gambar overlay
        
        Args:
            frame: Input frame dalam format BGR
            
        Returns:
            Tuple of (processed_frame, binary_mask, largest_contour)
            - processed_frame: Frame dengan kontur overlay (jika ada)
            - binary_mask: Binary mask dari skin detection
            - largest_contour: Kontur terbesar yang terdeteksi (atau None)
        """
        # Deteksi area kulit
        mask = self.detect_skin(frame)
        
        # Temukan kontur terbesar (tangan)
        largest_contour = self.find_largest_contour(mask)
        
        # Gambar kontur pada frame jika ada dan fitur aktif
        result_frame = frame.copy()
        if largest_contour is not None and self.draw_contours:
            result_frame = self.draw_contour_on_frame(result_frame, largest_contour)
        
        return result_frame, mask, largest_contour
    
    def update_skin_range(self, lower_hsv: List[int], upper_hsv: List[int]):
        """
        Update rentang warna kulit untuk kalibrasi
        
        Args:
            lower_hsv: Lower bound HSV [H, S, V]
            upper_hsv: Upper bound HSV [H, S, V]
        """
        self.lower_skin = np.array(lower_hsv, dtype=np.uint8)
        self.upper_skin = np.array(upper_hsv, dtype=np.uint8)
        self.logger.info(f"Skin range updated: {lower_hsv} - {upper_hsv}")
    
    def set_min_contour_area(self, area: int):
        """
        Set minimum area untuk kontur yang valid
        
        Args:
            area: Minimum area dalam pixels
        """
        self.min_contour_area = area
        self.logger.info(f"Minimum contour area set to {area}")
    
    def toggle_contour_drawing(self, enable: bool):
        """
        Enable/disable penggambaran kontur
        
        Args:
            enable: True untuk enable, False untuk disable
        """
        self.draw_contours = enable
        self.logger.info(f"Contour drawing {'enabled' if enable else 'disabled'}")
    
    def toggle_bounding_box(self, enable: bool):
        """
        Enable/disable bounding box
        
        Args:
            enable: True untuk enable, False untuk disable
        """
        self.show_bounding_box = enable
        self.logger.info(f"Bounding box {'enabled' if enable else 'disabled'}")
    
    def get_contour_info(self, contour: np.ndarray) -> dict:
        """
        Dapatkan informasi detail dari kontur
        
        Args:
            contour: Kontur yang akan dianalisis
            
        Returns:
            Dictionary berisi informasi kontur
        """
        if contour is None:
            return {}
        
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        x, y, w, h = cv2.boundingRect(contour)
        
        # Hitung centroid
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            cx, cy = 0, 0
        
        return {
            "area": float(area),
            "perimeter": float(perimeter),
            "bounding_box": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
            "centroid": {"x": cx, "y": cy}
        }
