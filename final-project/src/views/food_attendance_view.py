# views/food_attendance_view.py
"""View for QR code scanning and food attendance recording."""

import flet as ft
from datetime import datetime
import time
import threading
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
        
        scan_log = ft.ListView(spacing=5, padding=10)

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
                    
                page.update()
            except Exception as e:
                print(f"Error loading recent scans: {e}")

        def on_qr_scanned(school_id: str, student_name: str):
            """Handle QR code scan."""
            try:
                food_type = selected_food_type[0]
                
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

        # Initialize camera scanner
        try:
            camera = QRCameraScanner(
                on_qr_detected=on_qr_scanned,
                width=CAMERA_WIDTH,
                height=CAMERA_HEIGHT,
                cooldown=QR_SCAN_COOLDOWN
            )
        except Exception as e:
            print(f"Camera initialization error: {e}")
            camera = None

        # Food type selector
        def on_food_type_changed(e):
            """Handle food type change."""
            selected_food_type[0] = e.control.value
            load_recent_food_scans(e.control.value)

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
            page.update()

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
            
            # Camera (if available)
            ft.Container(
                content=camera if camera else ft.Text(
                    "Camera not available",
                    color=ft.Colors.RED,
                    text_align=ft.TextAlign.CENTER
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
            "/food-attendance",
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
