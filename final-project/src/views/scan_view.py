# views/scan_view.py
"""View for QR code scanning and attendance recording."""

import flet as ft
from datetime import datetime
import time
import threading
from views.base_view import BaseView
from config.constants import EMPLOYEES, CAMERA_WIDTH, CAMERA_HEIGHT, QR_SCAN_COOLDOWN, PRIMARY_COLOR, YELLOW_50
from utils.qr_scanner import QRCameraScanner


class ScanView(BaseView):
    """QR scanning screen with OpenCV camera support."""
    
    def build(self, event_id: str):
        """Build and return the scan view.
        
        Args:
            event_id: ID of the event to scan for
        """
        event = self.db.get_event_by_id(event_id)
        if not event:
            # FIX: Must return a valid view, not None
            self.page.go("/home")
            # Return a dummy view while redirecting
            return ft.View(
                "/",
                [ft.Container()]
            )
        
        scan_log = ft.ListView(spacing=5, padding=10)
        
        # Load recent scans
        attendance = self.db.get_attendance_by_event(event_id)
        for user_id, record in list(attendance.items())[:10]:
            scan_log.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN),
                    title=ft.Text(record['name']),
                    subtitle=ft.Text(record['time']),
                    dense=True
                )
            )
        
        # UI Components
        qr_input = ft.TextField(
            label="Enter ID manually",
            hint_text="e.g., E101",
            prefix_icon=ft.Icons.QR_CODE,
            autofocus=True,
            expand=True
        )
        
        camera_status = ft.Text(
            "Camera: Ready",
            size=12,
            color=ft.Colors.GREY_600,
            weight=ft.FontWeight.BOLD
        )
        
        camera_image = ft.Image(
            src_base64="",
            width=CAMERA_WIDTH,
            height=CAMERA_HEIGHT,
            fit=ft.ImageFit.CONTAIN,
            visible=False,
            error_content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.CAMERA_ALT, size=50, color=ft.Colors.GREY_400),
                        ft.Text("Loading camera...", size=12, color=ft.Colors.GREY_600)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                bgcolor=ft.Colors.GREY_200,
                width=CAMERA_WIDTH,
                height=CAMERA_HEIGHT,
                alignment=ft.alignment.center
            )
        )
        
        camera_icon = ft.Container(
            content=ft.Icon(
                ft.Icons.QR_CODE_SCANNER,
                size=100,
                color=PRIMARY_COLOR,
            ),
            alignment=ft.alignment.center,
        )
        
        camera_stack = ft.Stack([camera_icon, camera_image])
        
        camera_container = ft.Container(
            content=camera_stack,
            height=300,
            bgcolor=YELLOW_50,
            border_radius=10,
            border=ft.border.all(2, PRIMARY_COLOR),
            alignment=ft.alignment.center
        )
        
        camera_active = [False]
        
        def update_camera_frame(frame_base64: str):
            """Update the camera preview with new frame."""
            if not camera_active[0]:
                return
            
            try:
                if frame_base64 and len(frame_base64) > 0:
                    camera_image.src_base64 = frame_base64
                    camera_image.visible = True
                    camera_icon.visible = False
                    camera_image.update()
                    camera_icon.update()
            except Exception as e:
                print(f"Error updating frame: {e}")
        
        def process_scan(user_id: str):
            """Process a scanned or entered ID."""
            user_id = user_id.strip()
            
            if not user_id:
                return
            
            # Parse QR data: format is "ID|Name" or just "ID"
            if "|" in user_id:
                parts = user_id.split("|", 1)
                school_id = parts[0].strip()
                user_name = parts[1].strip()
            else:
                school_id = user_id
                user_name = user_id
            
            # Accept any school ID without validation
            existing = self.db.is_user_checked_in(event_id, school_id)
            
            if existing:
                self.show_snackbar(
                    f"{user_name} already checked in at {existing}", 
                    ft.Colors.ORANGE
                )
                return
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.db.record_attendance(event_id, school_id, user_name, timestamp)
            
            # Update UI
            scan_log.controls.insert(0, ft.ListTile(
                leading=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN),
                title=ft.Text(user_name),
                subtitle=ft.Text(timestamp),
                dense=True
            ))
            
            try:
                scan_log.update()
            except:
                pass
            
            self.show_snackbar(f"✓ {user_name} checked in!", ft.Colors.GREEN)
        
        def on_qr_detected(qr_data: str):
            """Callback when QR code is detected by camera."""
            process_scan(qr_data)
        
        def handle_manual_scan(e):
            """Handle manual ID entry."""
            user_id = qr_input.value
            qr_input.value = ""
            qr_input.update()
            process_scan(user_id)
        
        def toggle_camera(e):
            """Toggle camera on/off."""
            camera_active[0] = not camera_active[0]
            
            if camera_active[0]:
                # Start camera
                camera_btn.icon = ft.Icons.STOP_CIRCLE
                camera_btn.bgcolor = ft.Colors.RED_700
                camera_btn.tooltip = "Stop Camera"
                camera_status.value = "Camera: Starting..."
                camera_status.color = ft.Colors.ORANGE_700
                camera_container.bgcolor = ft.Colors.BLACK
                camera_container.border = ft.border.all(2, ft.Colors.GREEN_400)
                
                camera_image.visible = False
                camera_icon.visible = True
                camera_icon.content.color = ft.Colors.ORANGE_700
                
                camera_btn.update()
                camera_status.update()
                camera_container.update()
                camera_icon.update()
                
                # Initialize and start scanner
                self.app.qr_scanner = QRCameraScanner(
                    on_qr_detected, 
                    update_camera_frame,
                    CAMERA_WIDTH,
                    CAMERA_HEIGHT,
                    QR_SCAN_COOLDOWN
                )
                self.app.qr_scanner.start()
                
                # Update status after delay
                def update_status():
                    time.sleep(0.5)
                    if camera_active[0]:
                        try:
                            camera_status.value = "Camera: Scanning..."
                            camera_status.color = ft.Colors.GREEN_700
                            camera_status.update()
                        except:
                            pass
                
                threading.Thread(target=update_status, daemon=True).start()
                
            else:
                # Stop camera
                camera_btn.icon = ft.Icons.VIDEOCAM
                camera_btn.bgcolor = PRIMARY_COLOR
                camera_btn.tooltip = "Start Camera"
                camera_status.value = "Camera: Stopped"
                camera_status.color = ft.Colors.GREY_600
                camera_container.bgcolor = YELLOW_50
                camera_container.border = ft.border.all(2, PRIMARY_COLOR)
                
                camera_image.visible = False
                camera_icon.visible = True
                camera_icon.content.color = PRIMARY_COLOR
                
                if self.app.qr_scanner:
                    self.app.qr_scanner.stop()
            
                camera_btn.update()
                camera_status.update()
                camera_container.update()
                camera_icon.update()
                camera_image.update()
        
        qr_input.on_submit = handle_manual_scan
        
        camera_btn = ft.IconButton(
            icon=ft.Icons.VIDEOCAM,
            icon_color=ft.Colors.WHITE,
            bgcolor=PRIMARY_COLOR,
            tooltip="Start Camera",
            on_click=toggle_camera
        )
        
        return ft.View(
            f"/scan/{event_id}",
            [
                self.create_app_bar(event['name'], show_back=True),
                ft.Column(
                    controls=[
                        camera_container,
                        camera_status,
                        ft.Row(
                            [
                                qr_input,
                                camera_btn,
                                ft.IconButton(
                                    icon=ft.Icons.SEND,
                                    icon_color=ft.Colors.WHITE,
                                    bgcolor=PRIMARY_COLOR,
                                    on_click=handle_manual_scan
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Divider(),
                        ft.Text("Recent Activity", weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=scan_log,
                            height=200,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            border_radius=10
                        )
                    ],
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                )
            ],
            padding=20
        )