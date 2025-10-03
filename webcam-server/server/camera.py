"""
Camera module untuk menangkap dan mengolah video dari webcam
"""

import asyncio
import cv2
import numpy as np
import logging
from typing import Optional, Tuple
from config import (
    CAMERA_INDEX, DEFAULT_WIDTH, DEFAULT_HEIGHT, 
    JPEG_QUALITY, CAMERA_LOOP_DELAY
)

class Camera:
    """
    Class untuk mengelola webcam dan encoding frame
    """
    
    def __init__(self, camera_index: int = CAMERA_INDEX):
        """
        Initialize camera
        
        Args:
            camera_index: Index kamera (default 0)
        """
        self.camera_index = camera_index
        self.cap = None
        self.latest_frame = None
        self.frame_lock = asyncio.Lock()
        self.is_running = False
        self.width = DEFAULT_WIDTH
        self.height = DEFAULT_HEIGHT
        self.jpeg_quality = JPEG_QUALITY
        
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> bool:
        """
        Initialize kamera
        
        Returns:
            True jika berhasil, False jika gagal
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                self.logger.error(f"Cannot open camera {self.camera_index}")
                return False
                
            # Set resolusi
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            # Test capture
            ret, frame = self.cap.read()
            if not ret:
                self.logger.error("Cannot read from camera")
                return False
                
            self.logger.info(f"Camera initialized successfully: {self.width}x{self.height}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize camera: {e}")
            return False
    
    async def start_capture_loop(self):
        """
        Mulai loop untuk menangkap frame dari kamera
        """
        if self.cap is None:
            self.logger.error("Camera not initialized")
            return
            
        self.is_running = True
        self.logger.info("Starting camera capture loop")
        
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                
                if not ret:
                    self.logger.warning("Failed to read frame from camera")
                    await asyncio.sleep(CAMERA_LOOP_DELAY)
                    continue
                
                # Resize frame jika perlu
                if frame.shape[1] != self.width or frame.shape[0] != self.height:
                    frame = cv2.resize(frame, (self.width, self.height))
                
                # Encode ke JPEG
                encode_params = [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality]
                ret, jpeg_frame = cv2.imencode('.jpg', frame, encode_params)
                
                if ret:
                    async with self.frame_lock:
                        self.latest_frame = jpeg_frame.tobytes()
                
                await asyncio.sleep(CAMERA_LOOP_DELAY)
                
            except Exception as e:
                self.logger.error(f"Error in capture loop: {e}")
                await asyncio.sleep(CAMERA_LOOP_DELAY)
    
    async def get_latest_frame(self) -> Optional[bytes]:
        """
        Ambil frame terbaru dalam format JPEG bytes
        
        Returns:
            JPEG frame sebagai bytes, atau None jika tidak ada frame
        """
        async with self.frame_lock:
            return self.latest_frame
    
    def set_resolution(self, width: int, height: int):
        """
        Set resolusi kamera
        
        Args:
            width: Lebar frame
            height: Tinggi frame
        """
        self.width = width
        self.height = height
        
        if self.cap and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
        self.logger.info(f"Resolution set to {width}x{height}")
    
    def set_jpeg_quality(self, quality: int):
        """
        Set kualitas JPEG encoding
        
        Args:
            quality: Kualitas JPEG (1-100)
        """
        self.jpeg_quality = max(1, min(100, quality))
        self.logger.info(f"JPEG quality set to {self.jpeg_quality}")
    
    def get_camera_info(self) -> dict:
        """
        Dapatkan informasi kamera
        
        Returns:
            Dictionary berisi informasi kamera
        """
        return {
            "width": self.width,
            "height": self.height,
            "jpeg_quality": self.jpeg_quality,
            "camera_index": self.camera_index,
            "is_running": self.is_running
        }
    
    async def stop(self):
        """
        Stop kamera dan cleanup resources
        """
        self.is_running = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
            
        self.logger.info("Camera stopped")
    
    def __del__(self):
        """
        Destructor untuk cleanup
        """
        if self.cap:
            self.cap.release()