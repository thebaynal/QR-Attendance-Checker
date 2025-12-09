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
        
        # Check if event is in the past
        try:
            event_date = datetime.strptime(event['date'], '%Y-%m-%d').date()
            today = datetime.now().date()
            if event_date < today:
                # Event is in the past, prevent scanning
                self.show_snackbar(f"Cannot scan for past event ({event['date']})", ft.Colors.RED)
                self.page.go("/home")
                return ft.View("/", [ft.Container()])
        except (ValueError, KeyError):
            # If date parsing fails, allow scanning (legacy data handling)
            pass
        
        # Selected time slot state
        selected_time_slot = ["morning"]  # Default to morning
        
        scan_log = ft.ListView(spacing=5, padding=10)

        def load_recent_scans(time_slot=None):
            """Load recent scans for the selected time slot."""
            scan_log.controls.clear()
            
            try:
                # Get attendance data by section which has the timeslot info
                attendance_by_section = self.db.get_attendance_by_section(event_id)
                
                # Flatten and collect all scans
                all_scans = []
                for section_name, students in attendance_by_section.items():
                    for student in students:
                        # Add morning scan if present
                        if student.get('morning_status') == 'Present' and student.get('morning_time'):
                            all_scans.append({
                                'school_id': student['school_id'],
                                'name': student['name'],
                                'time': student['morning_time'],
                                'time_slot': 'morning',
                                'status': 'Present'
                            })
                        # Add afternoon scan if present
                        if student.get('afternoon_status') == 'Present' and student.get('afternoon_time'):
                            all_scans.append({
                                'school_id': student['school_id'],
                                'name': student['name'],
                                'time': student['afternoon_time'],
                                'time_slot': 'afternoon',
                                'status': 'Present'
                            })
                
                # Sort by time (most recent first)
                all_scans.sort(key=lambda x: x['time'], reverse=True)
                
                # Filter by selected time slot if specified
                if time_slot:
                    filtered_scans = [s for s in all_scans if s['time_slot'] == time_slot]
                else:
                    filtered_scans = all_scans
                
                # Limit to 15 most recent
                filtered_scans = filtered_scans[:15]
                
                if filtered_scans:
                    for record in filtered_scans:
                        time_slot_val = record['time_slot']
                        user_id = record['school_id']
                        user_name = record['name']
                        timestamp = record['time']
                        
                        # Icon and color based on time slot
                        if time_slot_val == 'morning':
                            icon = ft.Icons.WB_SUNNY
                            icon_color = ft.Colors.ORANGE
                            slot_text = "☀️ Morning"
                            bg_color = ft.Colors.ORANGE_50
                        elif time_slot_val == 'afternoon':
                            icon = ft.Icons.NIGHTS_STAY
                            icon_color = ft.Colors.BLUE
                            slot_text = "🌙 Afternoon"
                            bg_color = ft.Colors.BLUE_50
                        else:
                            icon = ft.Icons.CHECK_CIRCLE
                            icon_color = ft.Colors.GREEN
                            slot_text = "✓"
                            bg_color = ft.Colors.GREEN_50
                        
                        scan_tile = ft.Container(
                            content=ft.ListTile(
                                leading=ft.Icon(icon, color=icon_color),
                                title=ft.Text(user_name, weight=ft.FontWeight.BOLD, size=14),
                                subtitle=ft.Text(f"{slot_text} • {timestamp}", size=11),
                                trailing=ft.Text(user_id, size=11, color=ft.Colors.GREY_600),
                                dense=True,
                                content_padding=ft.padding.symmetric(horizontal=10, vertical=5)
                            ),
                            bgcolor=bg_color,
                            padding=ft.padding.symmetric(horizontal=5, vertical=3),
                            border_radius=8,
                            margin=ft.margin.only(bottom=5)
                        )
                        scan_log.controls.append(scan_tile)
                else:
                    # Show empty state
                    scan_log.controls.append(
                        ft.Container(
                            content=ft.Text(
                                "No scans yet for this time slot",
                                size=12,
                                color=ft.Colors.GREY_500,
                                italic=True
                            ),
                            alignment=ft.alignment.center,
                            padding=20
                        )
                    )
            
            except Exception as e:
                print(f"Error loading recent scans: {e}")
                scan_log.controls.append(
                    ft.Text(f"Error loading scans: {str(e)}", color=ft.Colors.RED)
                )
            
            # Update the list view
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
        
        # Scan result feedback display
        scan_result_container = ft.Container(
            content=ft.Text("", size=14, weight=ft.FontWeight.BOLD),
            bgcolor=ft.Colors.TRANSPARENT,
            padding=15,
            border_radius=10,
            visible=False,
            alignment=ft.alignment.center
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
                    # Double-check if event is still valid (not in past)
                    current_event = self.db.get_event_by_id(event_id)
                    if current_event:
                        try:
                            event_date = datetime.strptime(current_event['date'], '%Y-%m-%d').date()
                            today = datetime.now().date()
                            if event_date < today:
                                scan_result_container.bgcolor = ft.Colors.RED_100
                                scan_result_container.content.value = "❌ This event is in the past"
                                scan_result_container.content.color = ft.Colors.RED_700
                                scan_result_container.visible = True
                                scan_result_container.update()
                                
                                self.show_snackbar("Cannot scan for past events", ft.Colors.RED)
                                
                                time.sleep(2)
                                scan_result_container.visible = False
                                scan_result_container.update()
                                return
                        except (ValueError, KeyError):
                            pass
                    
                    # Parse QR data (format: school_id|name)
                    parts = qr_data.split('|')
                    if len(parts) < 1:
                        # Show error feedback
                        scan_result_container.bgcolor = ft.Colors.RED_100
                        scan_result_container.content.value = "❌ Invalid QR format"
                        scan_result_container.content.color = ft.Colors.RED_700
                        scan_result_container.visible = True
                        scan_result_container.update()
                        
                        # Hide after 2 seconds
                        time.sleep(2)
                        scan_result_container.visible = False
                        scan_result_container.update()
                        return
                    
                    school_id = parts[0].strip()
                    current_time_slot = selected_time_slot[0]
                    
                    # Check if student exists
                    student = self.db.get_student_by_id(school_id)
                    if not student:
                        # Show not found feedback
                        scan_result_container.bgcolor = ft.Colors.RED_100
                        scan_result_container.content.value = f"❌ Student {school_id} not found"
                        scan_result_container.content.color = ft.Colors.RED_700
                        scan_result_container.visible = True
                        scan_result_container.update()
                        
                        time.sleep(2)
                        scan_result_container.visible = False
                        scan_result_container.update()
                        return
                    
                    # Check if already checked in for this time slot
                    already_checked = self.db.check_timeslot_attendance(event_id, school_id, current_time_slot)
                    
                    if already_checked:
                        # Show already scanned feedback
                        scan_result_container.bgcolor = ft.Colors.AMBER_100
                        scan_result_container.content.value = f"⚠️ Already checked in for {current_time_slot.upper()}"
                        scan_result_container.content.color = ft.Colors.AMBER_900
                        scan_result_container.visible = True
                        scan_result_container.update()
                        
                        # Keep visible longer for duplicate
                        time.sleep(3)
                        scan_result_container.visible = False
                        scan_result_container.update()
                        return
                    
                    # Record attendance
                    success = self.db.record_timeslot_attendance(event_id, school_id, current_time_slot)
                    
                    # Record scan in activity log
                    if success and self.app.current_user:
                        student_name = student.get('name', school_id)
                        self.db.record_scan(
                            scanner_username=self.app.current_user,
                            scanned_user_id=school_id,
                            scanned_user_name=student_name,
                            event_id=event_id
                        )
                    
                    if success:
                        # Show success feedback with animation
                        student_name = student.get('name', school_id)
                        scan_result_container.bgcolor = ft.Colors.GREEN_100
                        scan_result_container.content.value = f"✅ {student_name}\n{current_time_slot.upper()} checked in"
                        scan_result_container.content.color = ft.Colors.GREEN_700
                        scan_result_container.visible = True
                        scan_result_container.update()
                        
                        # Update stats display with a small delay for visual effect
                        time.sleep(0.3)
                        stats = self.db.get_attendance_summary(event_id)
                        morning_count.value = str(stats.get('morning', 0))
                        afternoon_count.value = str(stats.get('afternoon', 0))
                        morning_count.update()
                        afternoon_count.update()
                        
                        # Reload recent scans to show the new entry
                        load_recent_scans(current_time_slot)
                        
                        # Show snackbar with updated info
                        self.show_snackbar(
                            f"✅ {student_name} checked in for {current_time_slot.upper()}!", 
                            ft.Colors.GREEN
                        )
                        
                        # Keep success message visible for 2.5 seconds
                        time.sleep(2.5)
                        scan_result_container.visible = False
                        scan_result_container.update()
                    else:
                        # Show failure feedback
                        scan_result_container.bgcolor = ft.Colors.RED_100
                        scan_result_container.content.value = "❌ Failed to record attendance"
                        scan_result_container.content.color = ft.Colors.RED_700
                        scan_result_container.visible = True
                        scan_result_container.update()
                        
                        self.show_snackbar("Failed to record attendance", ft.Colors.RED)
                        
                        time.sleep(2)
                        scan_result_container.visible = False
                        scan_result_container.update()
                except Exception as e:
                    print(f"Error processing scan: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    # Show error feedback
                    scan_result_container.bgcolor = ft.Colors.RED_100
                    scan_result_container.content.value = f"❌ Error: {str(e)[:30]}"
                    scan_result_container.content.color = ft.Colors.RED_700
                    scan_result_container.visible = True
                    scan_result_container.update()
                    
                    self.show_snackbar(f"Error: {str(e)}", ft.Colors.RED)
                    
                    time.sleep(2)
                    scan_result_container.visible = False
                    scan_result_container.update()
            
            # Run in background thread to avoid UI freeze
            threading.Thread(target=_process_in_background, daemon=True).start()
        
        def on_qr_detected(qr_data: str):
            """Callback when QR code is detected by camera."""
            print(f"DEBUG: on_qr_detected called with: {qr_data}")
            try:
                process_scan(qr_data)
            except Exception as e:
                print(f"ERROR in on_qr_detected: {e}")
                import traceback
                traceback.print_exc()
        
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
                        
                        # Scan result feedback
                        scan_result_container,
                        
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
                        
                        # Recent activity header
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.HISTORY, color=PRIMARY_COLOR, size=20),
                                ft.Text("Recent Activity", weight=ft.FontWeight.BOLD, size=16)
                            ],
                            spacing=10,
                            alignment=ft.MainAxisAlignment.START
                        ),
                        
                        ft.Container(
                            content=scan_log,
                            height=220,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            border_radius=10,
                            bgcolor=ft.Colors.GREY_50,
                            padding=10
                        )
                    ],
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                )
            ],
            padding=20
        )
    
    def _refresh_attendance(self):
        """Refresh attendance display (called by sync service when data changes)."""
        try:
            # This is called from a background thread, so we need to be careful
            # Try to update the scan log if we're still on the scan view
            if hasattr(self, '_current_event_id'):
                # Reload recent scans in background
                pass
        except Exception as e:
            print(f"Error refreshing attendance: {e}")