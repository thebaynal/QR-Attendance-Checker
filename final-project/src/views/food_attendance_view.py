# views/food_attendance_view.py
"""View for QR code scanning and food attendance recording."""

import flet as ft
from datetime import datetime
import time
import threading
import base64
from views.base_view import BaseView
from config.constants import CAMERA_WIDTH, CAMERA_HEIGHT, QR_SCAN_COOLDOWN, PRIMARY_COLOR, BLUE_50
from utils.qr_scanner import QRCameraScanner


class FoodAttendanceView(BaseView):
    """Food attendance scanning screen with QR code support."""
    
    def build(self, event_id: str):
        """Build and return the food attendance view.
        
        Args:
            event_id: ID of the event to scan for
        """
        event = self.db.get_event_by_id(event_id)
        if not event:
            self.page.go("/home")
            return ft.View("/", [ft.Container()])
        
        # Selected food type state
        selected_food_type = ["Breakfast"]  # Default to Breakfast
        camera_active = [False]  # Camera state
        
        scan_log = ft.ListView(spacing=5, padding=10)
        camera_image = ft.Image(width=CAMERA_WIDTH, height=CAMERA_HEIGHT)
        camera_icon = ft.Container(
            content=ft.Icon(ft.Icons.VIDEOCAM, color=PRIMARY_COLOR, size=64),
            width=CAMERA_WIDTH,
            height=CAMERA_HEIGHT,
            bgcolor=BLUE_50,
            alignment=ft.alignment.center,
        )
        
        def load_recent_food_scans(food_type=None):
            """Load recent food attendance scans."""
            scan_log.controls.clear()
            
            try:
                # Get recent food scans
                recent_scans = self.db.get_recent_food_scans(event_id, limit=15)
                
                # Filter by food type if specified
                if food_type:
                    recent_scans = [s for s in recent_scans if s['food_type'] == food_type]
                
                if recent_scans:
                    for record in recent_scans:
                        user_name = record['user_name']
                        timestamp = record['food_time']
                        food_type_val = record['food_type']
                        
                        # Color based on food type
                        if food_type_val == 'Breakfast':
                            icon_color = ft.Colors.ORANGE
                            bg_color = ft.Colors.ORANGE_50
                        elif food_type_val == 'Lunch':
                            icon_color = ft.Colors.AMBER
                            bg_color = ft.Colors.AMBER_50
                        elif food_type_val == 'Dinner':
                            icon_color = ft.Colors.BLUE
                            bg_color = ft.Colors.BLUE_50
                        else:
                            icon_color = ft.Colors.GREEN
                            bg_color = ft.Colors.GREEN_50
                        
                        scan_item = ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.LOCAL_DINING, color=icon_color, size=24),
                                    ft.Column(
                                        [
                                            ft.Text(user_name, size=14, weight="bold"),
                                            ft.Text(f"{food_type_val} • {timestamp}", size=12, color=ft.Colors.GREY_700),
                                        ],
                                        spacing=2,
                                        expand=True
                                    ),
                                ],
                                spacing=10
                            ),
                            bgcolor=bg_color,
                            padding=10,
                            border_radius=5
                        )
                        scan_log.controls.append(scan_item)
                else:
                    scan_log.controls.append(
                        ft.Text("No food attendance records yet", color=ft.Colors.GREY_600, size=12)
                    )
                    
                self.page.update()
            except Exception as e:
                print(f"Error loading recent scans: {e}")
        
        def update_camera_frame(frame_base64: str):
            """Update camera display with new frame."""
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
                print(f"Error updating camera frame: {e}")
        
        def on_qr_detected(qr_data: str):
            """Handle QR code detection."""
            try:
                process_food_scan(qr_data)
            except Exception as e:
                print(f"Error in on_qr_detected: {e}")
        
        def process_food_scan(school_id: str):
            """Process food attendance scan."""
            try:
                # Get student info from database
                student = self.db.get_student_by_id(school_id)
                if not student:
                    self.show_snackbar(f"Student {school_id} not found", ft.Colors.RED)
                    return
                
                food_type = selected_food_type[0]
                student_name = student.get('name', f"Student {school_id}")
                
                # Record food attendance
                success = self.db.record_food_attendance(
                    event_id=event_id,
                    school_id=school_id,
                    user_name=student_name,
                    food_type=food_type,
                    scanner_username=self.current_user
                )
                
                if success:
                    self.show_snackbar(f"✓ {student_name} ({food_type})", ft.Colors.GREEN)
                    load_recent_food_scans(food_type)
                else:
                    self.show_snackbar(f"✗ Failed to record {student_name}", ft.Colors.RED)
            except Exception as e:
                print(f"Error processing scan: {e}")
                self.show_snackbar(f"Error: {str(e)}", ft.Colors.RED)
        
        def toggle_camera(e):
            """Toggle camera on/off."""
            camera_active[0] = not camera_active[0]
            
            if camera_active[0]:
                # Initialize and start scanner
                try:
                    self.app.qr_scanner = QRCameraScanner(
                        on_qr_detected,
                        update_camera_frame,
                        CAMERA_WIDTH,
                        CAMERA_HEIGHT,
                        QR_SCAN_COOLDOWN
                    )
                    self.app.qr_scanner.start()
                    camera_btn.icon = ft.Icons.STOP_CIRCLE
                    camera_btn.bgcolor = ft.Colors.RED_700
                except Exception as e:
                    print(f"Camera error: {e}")
                    camera_active[0] = False
                    self.show_snackbar(f"Camera error: {e}", ft.Colors.RED)
            else:
                # Stop camera
                if self.app.qr_scanner:
                    self.app.qr_scanner.stop()
                camera_btn.icon = ft.Icons.VIDEOCAM
                camera_btn.bgcolor = PRIMARY_COLOR
            
            camera_btn.update()

        # Food type selector
        def on_food_type_changed(e):
            """Handle food type change."""
            selected_food_type[0] = e.control.value
            load_recent_food_scans(e.control.value)
            food_count_text.value = get_food_count()
            food_count_text.update()

        food_type_dropdown = ft.Dropdown(
            label="Food Type",
            value="Breakfast",
            options=[
                ft.dropdown.Option("Breakfast"),
                ft.dropdown.Option("Lunch"),
                ft.dropdown.Option("Dinner"),
                ft.dropdown.Option("Snack"),
            ],
            on_change=on_food_type_changed,
            width=200
        )

        # Get food count for selected type
        def get_food_count():
            try:
                count = self.db.get_food_attendance_count(event_id, selected_food_type[0])
                return f"{count} attended"
            except:
                return "0 attended"

        food_count_text = ft.Text(get_food_count(), size=14, weight="bold", color=PRIMARY_COLOR)

        # Load initial scans
        load_recent_food_scans()

        # Refresh button
        def on_refresh_click(e):
            food_count_text.value = get_food_count()
            load_recent_food_scans(selected_food_type[0])
            food_count_text.update()

        camera_btn = ft.IconButton(
            ft.Icons.VIDEOCAM,
            icon_size=28,
            bgcolor=PRIMARY_COLOR,
            icon_color=ft.Colors.WHITE,
            on_click=toggle_camera,
            tooltip="Start Camera"
        )

        # Build view
        view_content = [
            # Header
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.LOCAL_DINING, size=28, color=ft.Colors.ORANGE),
                        ft.Column(
                            [
                                ft.Text("Food Attendance", size=24, weight="bold"),
                                ft.Text(event['name'], size=12, color=ft.Colors.GREY_700),
                            ],
                            spacing=2,
                            expand=True
                        ),
                    ],
                    spacing=10
                ),
                padding=15,
                bgcolor=BLUE_50,
                border_radius=10,
                margin=10
            ),
            
            # Controls
            ft.Container(
                content=ft.Row(
                    [
                        food_type_dropdown,
                        camera_btn,
                        ft.IconButton(
                            ft.Icons.REFRESH,
                            on_click=on_refresh_click,
                            tooltip="Refresh"
                        ),
                    ],
                    spacing=10
                ),
                padding=10,
                margin=ft.margin.symmetric(horizontal=10)
            ),
            
            # Food count
            ft.Container(
                content=food_count_text,
                padding=10,
                margin=ft.margin.symmetric(horizontal=10)
            ),
            
            # Camera display
            ft.Container(
                content=ft.Stack(
                    [
                        camera_image,
                        camera_icon,
                    ]
                ),
                height=CAMERA_HEIGHT,
                margin=10,
                border_radius=10,
                clip_behavior=ft.ClipBehavior.HARD_EDGE
            ),
            
            # Recent scans
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Recent Scans", size=16, weight="bold"),
                        scan_log,
                    ],
                    spacing=10,
                    expand=True
                ),
                padding=10,
                margin=10,
                expand=True
            ),
        ]

        return ft.View(
            f"/food-attendance/{event_id}",
            view_content,
            scroll=ft.ScrollMode.AUTO,
            appbar=ft.AppBar(
                title=ft.Text("Food Attendance"),
                bgcolor=PRIMARY_COLOR,
                actions=[
                    ft.IconButton(
                        ft.Icons.HOME,
                        on_click=lambda e: self.page.go("/home"),
                        tooltip="Back to Home"
                    ),
                ],
            ),
        )
