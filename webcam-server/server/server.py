"""
WebSocket Server untuk streaming webcam
"""

import asyncio
import websockets
import logging
import json
from typing import Set, Any

from camera import Camera
from config import (
    SERVER_HOST, SERVER_PORT, TARGET_FPS, BROADCAST_DELAY,
    MAX_CLIENTS, LOG_LEVEL, LOG_FORMAT
)
from utils import (
    setup_logging, create_metadata_message, 
    parse_client_message, validate_resolution, validate_fps
)

class WebcamWebSocketServer:
    """
    WebSocket server untuk streaming video webcam
    """
    
    def __init__(self):
        """
        Initialize server
        """
        self.logger = setup_logging(LOG_LEVEL, LOG_FORMAT)
        self.camera = Camera()
        self.clients: Set[Any] = set()
        self.is_running = False
        
    async def register_client(self, websocket: Any):
        """
        Register client baru
        
        Args:
            websocket: WebSocket connection
        """
        if len(self.clients) >= MAX_CLIENTS:
            await websocket.close(code=1008, reason="Server full")
            self.logger.warning("Client rejected: server full")
            return
            
        self.clients.add(websocket)
        client_addr = websocket.remote_address
        self.logger.info(f"Client connected: {client_addr}, Total clients: {len(self.clients)}")
        
        # Kirim metadata ke client baru
        camera_info = self.camera.get_camera_info()
        metadata = create_metadata_message(
            camera_info["width"], 
            camera_info["height"], 
            TARGET_FPS
        )
        
        try:
            await websocket.send(metadata)
            self.logger.debug(f"Metadata sent to {client_addr}")
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning(f"Client {client_addr} disconnected during metadata send")
    
    async def unregister_client(self, websocket: Any):
        """
        Unregister client
        
        Args:
            websocket: WebSocket connection
        """
        if websocket in self.clients:
            self.clients.remove(websocket)
            client_addr = websocket.remote_address
            self.logger.info(f"Client disconnected: {client_addr}, Total clients: {len(self.clients)}")
    
    async def handle_client_message(self, websocket: Any, message: str):
        """
        Handle pesan dari client
        
        Args:
            websocket: WebSocket connection
            message: Pesan dari client
        """
        client_addr = websocket.remote_address
        self.logger.debug(f"Message from {client_addr}: {message}")
        
        parsed_message = parse_client_message(message)
        if not parsed_message:
            return
        
        message_type = parsed_message.get("type")
        
        if message_type == "config":
            await self.handle_config_message(websocket, parsed_message)
        else:
            self.logger.warning(f"Unknown message type from {client_addr}: {message_type}")
    
    async def handle_config_message(self, websocket: Any, config: dict):
        """
        Handle pesan konfigurasi dari client
        
        Args:
            websocket: WebSocket connection
            config: Dictionary konfigurasi
        """
        client_addr = websocket.remote_address
        
        # Handle resolution change
        if "resolution" in config:
            resolution = config["resolution"]
            if isinstance(resolution, list) and len(resolution) == 2:
                width, height = validate_resolution(resolution[0], resolution[1])
                self.camera.set_resolution(width, height)
                self.logger.info(f"Resolution changed by {client_addr}: {width}x{height}")
        
        # Handle FPS change
        if "fps" in config:
            fps = validate_fps(config["fps"])
            # Note: FPS change memerlukan restart broadcast loop
            self.logger.info(f"FPS change requested by {client_addr}: {fps}")
        
        # Handle JPEG quality change
        if "jpeg_quality" in config:
            quality = config["jpeg_quality"]
            if isinstance(quality, int):
                self.camera.set_jpeg_quality(quality)
                self.logger.info(f"JPEG quality changed by {client_addr}: {quality}")
    
    async def client_handler(self, websocket: Any):
        """
        Handler untuk setiap client connection
        
        Args:
            websocket: WebSocket connection
        """
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                if isinstance(message, str):
                    await self.handle_client_message(websocket, message)
                else:
                    # Binary message dari client (tidak diharapkan untuk sekarang)
                    self.logger.warning(f"Unexpected binary message from {websocket.remote_address}")
        
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            self.logger.error(f"Error handling client {websocket.remote_address}: {e}")
        finally:
            await self.unregister_client(websocket)
    
    async def broadcast_frames(self):
        """
        Loop untuk broadcast frame ke semua client
        """
        self.logger.info("Starting frame broadcast loop")
        
        while self.is_running:
            try:
                # Ambil frame terbaru
                frame_data = await self.camera.get_latest_frame()
                
                if frame_data and self.clients:
                    # Broadcast ke semua client
                    disconnected_clients = set()
                    
                    for client in self.clients.copy():
                        try:
                            await client.send(frame_data)
                        except websockets.exceptions.ConnectionClosed:
                            disconnected_clients.add(client)
                        except Exception as e:
                            self.logger.error(f"Error sending frame to {client.remote_address}: {e}")
                            disconnected_clients.add(client)
                    
                    # Remove disconnected clients
                    for client in disconnected_clients:
                        await self.unregister_client(client)
                
                await asyncio.sleep(BROADCAST_DELAY)
                
            except Exception as e:
                self.logger.error(f"Error in broadcast loop: {e}")
                await asyncio.sleep(BROADCAST_DELAY)
    
    async def start_server(self):
        """
        Start WebSocket server
        """
        # Initialize camera
        if not await self.camera.initialize():
            self.logger.error("Failed to initialize camera")
            return
        
        self.is_running = True
        
        # Start camera capture loop
        camera_task = asyncio.create_task(self.camera.start_capture_loop())
        
        # Start broadcast loop
        broadcast_task = asyncio.create_task(self.broadcast_frames())
        
        # Start WebSocket server
        self.logger.info(f"Starting WebSocket server on {SERVER_HOST}:{SERVER_PORT}")
        
        try:
            async with websockets.serve(
                self.client_handler,
                SERVER_HOST,
                SERVER_PORT,
                max_size=None,  # No message size limit
                ping_interval=20,
                ping_timeout=10
            ):
                self.logger.info("WebSocket server started successfully")
                await asyncio.gather(camera_task, broadcast_task)
                
        except Exception as e:
            self.logger.error(f"Server error: {e}")
        finally:
            await self.stop_server()
    
    async def stop_server(self):
        """
        Stop server dan cleanup
        """
        self.logger.info("Stopping server...")
        self.is_running = False
        
        # Close all client connections
        if self.clients:
            await asyncio.gather(
                *[client.close() for client in self.clients],
                return_exceptions=True
            )
        
        # Stop camera
        await self.camera.stop()
        
        self.logger.info("Server stopped")

async def main():
    """
    Main function untuk menjalankan server
    """
    server = WebcamWebSocketServer()
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        await server.stop_server()

if __name__ == "__main__":
    asyncio.run(main())