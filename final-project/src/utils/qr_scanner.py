# utils/qr_scanner.py
"""QR code scanner using OpenCV and pyzbar."""

import cv2
from pyzbar import pyzbar
import threading
import time
import base64
import numpy as np


class QRCameraScanner:
    """Handle camera operations and QR code detection using OpenCV."""
    
    def __init__(self, on_qr_detected, on_frame_update, 
                 width=640, height=480, cooldown=2):
        self.on_qr_detected = on_qr_detected
        self.on_frame_update = on_frame_update
        self.camera = None
        self.is_running = False
        self.thread = None
        self.last_scanned = None
        self.scan_cooldown = cooldown
        self.current_frame_base64 = None
        self.width = width
        self.height = height
        
    def start(self):
        """Start the camera and QR detection."""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._scan_loop, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop the camera and QR detection."""
        self.is_running = False
        if self.camera:
            self.camera.release()
            self.camera = None
        if self.thread:
            self.thread.join(timeout=1)
    
    def _scan_loop(self):
        """Main scanning loop running in separate thread."""
        try:
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                print("Error: Could not open camera")
                self.is_running = False
                return
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            print(f"DEBUG: Camera initialized - {self.width}x{self.height}")
            
            frame_count = 0
            qr_count = 0
            
            while self.is_running:
                ret, frame = self.camera.read()
                
                if not ret:
                    print("Error: Could not read frame")
                    break
                
                frame_count += 1
                
                # Decode QR codes in the frame
                try:
                    decoded_objects = pyzbar.decode(frame)
                except Exception as e:
                    print(f"Error decoding QR: {e}")
                    decoded_objects = []
                
                # Draw rectangles around detected QR codes
                for obj in decoded_objects:
                    try:
                        points = obj.polygon
                        if len(points) == 4:
                            pts = [(point.x, point.y) for point in points]
                            pts = [pts[i] for i in range(4)]
                            cv2.polylines(frame, [np.array(pts, dtype=np.int32)], True, (0, 255, 0), 3)
                        
                        qr_data = obj.data.decode('utf-8')
                        current_time = time.time()
                        qr_count += 1
                        
                        print(f"DEBUG: QR detected #{qr_count}: {qr_data}")
                        
                        # Check cooldown to avoid duplicate scans
                        if (self.last_scanned is None or 
                            self.last_scanned[0] != qr_data or 
                            current_time - self.last_scanned[1] > self.scan_cooldown):
                            
                            self.last_scanned = (qr_data, current_time)
                            print(f"DEBUG: QR passed cooldown, triggering callback")
                            
                            # Callback to main app
                            if self.on_qr_detected:
                                try:
                                    self.on_qr_detected(qr_data)
                                except Exception as cb_error:
                                    print(f"Error in QR callback: {cb_error}")
                        else:
                            print(f"DEBUG: QR still in cooldown or duplicate")
                    except Exception as decode_error:
                        print(f"Error processing QR object: {decode_error}")
                        continue
                
                # Convert frame to base64 for display
                try:
                    _, buffer = cv2.imencode('.jpg', frame)
                    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                    self.current_frame_base64 = jpg_as_text
                    
                    # Update UI with new frame
                    if self.on_frame_update:
                        try:
                            self.on_frame_update(jpg_as_text)
                        except Exception as frame_error:
                            print(f"Error updating frame: {frame_error}")
                except Exception as encode_error:
                    print(f"Error encoding frame: {encode_error}")
                
                # Print debug every 150 frames (~5 seconds at 30 FPS)
                if frame_count % 150 == 0:
                    print(f"DEBUG: Scanner running - {frame_count} frames, {qr_count} QRs detected")
                
                # Small delay to reduce CPU usage (~20 FPS)
                time.sleep(0.05)
            
            print("DEBUG: Scan loop ended")
            
        except Exception as e:
            print(f"Critical error in scan loop: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.camera:
                self.camera.release()
            print("DEBUG: Camera released")