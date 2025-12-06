# views/scan_view.py
"""View for QR code scanning and attendance recording with time slots."""

import flet as ft
from datetime import datetime
import time
import threading
from views.base_view import BaseView
from config.constants import EMPLOYEES, CAMERA_WIDTH, CAMERA_HEIGHT, QR_SCAN_COOLDOWN, PRIMARY_COLOR, BLUE_50
from utils.qr_scanner import QRCameraScanner


class ScanView(BaseView):
    """QR scanning screen with OpenCV camera support and time slot selection."""
    
    def build(self, event_id: str):
        """Build and return the scan view.
        
        Args:
            event_id: ID of the event to scan for
        """
        event = self.db.get_event_by_id(event_id)
        if not event:
            self.page.go("/home")
            return ft.View("/", [ft.Container()])
        
        # Selected time slot state
        selected_time_slot = ["morning"]  # Default to morning
        
        scan_log = ft.ListView(spacing=5, padding=10)
        
       # In scan_view.py, update the load_recent_scans function:

        def load_recent_scans(time_slot=None):
            """Load recent scans for the selected time slot."""
            scan_log.controls.clear()
            
            if time_slot:
                # Load scans for specific time slot
                query = """
                SELECT user_id, user_name, timestamp, time_slot 
                FROM attendance 
                WHERE event_id = ? AND time_slot = ?
                ORDER BY timestamp DESC 
                LIMIT 10
                """
                results = self.db._execute(query, (event_id, time_slot), fetch_all=True)
            else:
                # Load all recent scans
                attendance = self.db.get_attendance_by_event(event_id)
                results = [(key.split('_')[0], rec['name'], rec['time'], rec.get('time_slot', 'N/A')) 
                        for key, rec in list(attendance.items())[:10]]
            
            if results:
                for record in results:
                    user_id, user_name, timestamp, time_slot_val = record
                    
                    # Icon and color based on time slot
                    if time_slot_val == 'morning':
                        icon = ft.Icons.WB_SUNNY
                        icon_color = ft.Colors.ORANGE
                        slot_text = "☀️ Morning"
                    elif time_slot_val == 'afternoon':
                        icon = ft.Icons.NIGHTS_STAY
                        icon_color = ft.Colors.BLUE
                        slot_text = "🌙 Afternoon"
                    else:
                        icon = ft.Icons.CHECK_CIRCLE
                        icon_color = ft.Colors.GREEN
                        slot_text = "✓"
                    
                    scan_log.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(icon, color=icon_color),
                            title=ft.Text(user_name, weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(f"{slot_text} • {timestamp}"),
                            trailing=ft.Text(user_id, size=12, color=ft.Colors.GREY_600),
                            dense=True
                        )
                    )
            
            # Only update if scan_log is already added to page
            try:
                if hasattr(scan_log, 'page') and scan_log.page:
                    scan_log.update()
            except:
                pass  # Will update when added to page

        load_recent_scans(selected_time_slot[0])
        
        # Time slot selection buttons
        morning_btn = ft.ElevatedButton(
            "☀️ Morning",
            icon=ft.Icons.WB_SUNNY,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.ORANGE_400,
                color=ft.Colors.WHITE,
            ),
            expand=True,
            height=50
        )
        
        afternoon_btn = ft.ElevatedButton(
            "🌙 Afternoon",
            icon=ft.Icons.NIGHTS_STAY,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREY_400,
                color=ft.Colors.WHITE,
            ),
            expand=True,
            height=50
        )
        
        def select_morning(e):
            """Select morning time slot."""
            selected_time_slot[0] = "morning"
            morning_btn.style.bgcolor = ft.Colors.ORANGE_400
            afternoon_btn.style.bgcolor = ft.Colors.GREY_400
            time_slot_indicator.value = "Currently Scanning: ☀️ MORNING"
            time_slot_indicator.color = ft.Colors.ORANGE_700
            camera_container.border = ft.border.all(3, ft.Colors.ORANGE_400)
            
            morning_btn.update()
            afternoon_btn.update()
            time_slot_indicator.update()
            camera_container.update()
            
            # Reload scans for morning
            load_recent_scans("morning")
            self.show_snackbar("Switched to Morning attendance", ft.Colors.ORANGE)
        
        def select_afternoon(e):
            """Select afternoon time slot."""
            selected_time_slot[0] = "afternoon"
            morning_btn.style.bgcolor = ft.Colors.GREY_400
            afternoon_btn.style.bgcolor = ft.Colors.BLUE_400
            time_slot_indicator.value = "Currently Scanning: 🌙 AFTERNOON"
            time_slot_indicator.color = ft.Colors.BLUE_700
            camera_container.border = ft.border.all(3, ft.Colors.BLUE_400)
            
            morning_btn.update()
            afternoon_btn.update()
            time_slot_indicator.update()
            camera_container.update()
            
            # Reload scans for afternoon
            load_recent_scans("afternoon")
            self.show_snackbar("Switched to Afternoon attendance", ft.Colors.BLUE)
        
        morning_btn.on_click = select_morning
        afternoon_btn.on_click = select_afternoon
        
        # Time slot indicator
        time_slot_indicator = ft.Text(
            "Currently Scanning: ☀️ MORNING",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.ORANGE_700
        )
        
        # Get attendance stats
        stats = self.db.get_attendance_summary(event_id)
        morning_count = ft.Text(
            str(stats.get('morning', 0)),
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.ORANGE_700
        )
        afternoon_count = ft.Text(
            str(stats.get('afternoon', 0)),
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700
        )
        
        # Stats cards
        stats_card = ft.Row(
            [
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.WB_SUNNY, size=30, color=ft.Colors.ORANGE_400),
                                ft.Text("Morning", size=12, color=ft.Colors.GREY_700),
                                morning_count,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=5
                        ),
                        padding=15,
                        width=150
                    ),
                    elevation=2
                ),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.NIGHTS_STAY, size=30, color=ft.Colors.BLUE_400),
                                ft.Text("Afternoon", size=12, color=ft.Colors.GREY_700),
                                afternoon_count,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=5
                        ),
                        padding=15,
                        width=150
                    ),
                    elevation=2
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )
        
        # UI Components
        qr_input = ft.TextField(
            label="Enter ID manually",
            hint_text="e.g., 2021-00001",
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
                color=ft.Colors.ORANGE_400,
            ),
            alignment=ft.alignment.center,
        )
        
        camera_stack = ft.Stack([camera_icon, camera_image])
        
        camera_container = ft.Container(
            content=camera_stack,
            height=300,
            bgcolor=BLUE_50,
            border_radius=10,
            border=ft.border.all(3, ft.Colors.ORANGE_400),
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
        
        def process_scan(qr_data: str):
            """Process QR code scan with new database structure."""
            def _process_in_background():
                try:
                    # Parse QR data (format: school_id|name)
                    parts = qr_data.split('|')
                    if len(parts) < 1:
                        self.show_snackbar("Invalid QR format", ft.Colors.RED)
                        return
                    
                    school_id = parts[0].strip()
                    current_time_slot = selected_time_slot[0]
                    
                    # Check if student exists
                    student = self.db.get_student_by_id(school_id)
                    if not student:
                        self.show_snackbar(f"Student {school_id} not found", ft.Colors.RED)
                        return
                    
                    # Check if already checked in for this time slot
                    already_checked = self.db.check_timeslot_attendance(event_id, school_id, current_time_slot)
                    
                    if already_checked:
                        self.show_snackbar(f"✅ Already checked in for {current_time_slot.upper()}!", ft.Colors.ORANGE)
                        return
                    
                    # Record attendance
                    success = self.db.record_timeslot_attendance(event_id, school_id, current_time_slot)
                    
                    if success:
                        # Update stats display
                        stats = self.db.get_attendance_summary(event_id)
                        morning_count.value = str(stats.get('morning', 0))
                        afternoon_count.value = str(stats.get('afternoon', 0))
                        morning_count.update()
                        afternoon_count.update()
                        
                        # Show success message
                        self.show_snackbar(
                            f"✅ {student.get('name', school_id)} checked in for {current_time_slot.upper()}!", 
                            ft.Colors.GREEN
                        )
                        
                        # Reload recent scans
                        load_recent_scans(current_time_slot)
                    else:
                        self.show_snackbar("Failed to record attendance", ft.Colors.RED)
                except Exception as e:
                    print(f"Error processing scan: {e}")
                    self.show_snackbar(f"Error: {str(e)}", ft.Colors.RED)
            
            # Run in background thread to avoid UI freeze
            threading.Thread(target=_process_in_background, daemon=True).start()
        
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
                camera_container.bgcolor = BLUE_50
                
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
                        # Time slot selector
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Select Time Slot",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.GREY_800
                                    ),
                                    ft.Row(
                                        [morning_btn, afternoon_btn],
                                        spacing=10
                                    ),
                                ],
                                spacing=10
                            ),
                            padding=10,
                            bgcolor=ft.Colors.GREY_100,
                            border_radius=10
                        ),
                        
                        # Current time slot indicator
                        time_slot_indicator,
                        
                        # Stats
                        stats_card,
                        
                        # Camera
                        camera_container,
                        camera_status,
                        
                        # Manual input
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
                        
                        # Recent activity
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