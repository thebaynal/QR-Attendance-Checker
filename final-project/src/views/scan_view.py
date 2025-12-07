# views/scan_view.py
"""Premium QR code scanning view with time slot selection."""

import flet as ft
from datetime import datetime
import time
import threading
from views.base_view import BaseView
from config.constants import CAMERA_WIDTH, CAMERA_HEIGHT, QR_SCAN_COOLDOWN, PRIMARY_COLOR
from utils.qr_scanner import QRCameraScanner


class ScanView(BaseView):
    """Premium QR scanning screen with camera support and time slots."""
    
    def build(self, event_id: str):
        """Build and return the premium scan view."""
        event = self.db.get_event_by_id(event_id)
        if not event:
            self.page.go("/home")
            return ft.View("/", [ft.Container()])
        
        # Selected time slot state
        selected_time_slot = ["morning"]  # Default to morning
        
        # Scan log list
        scan_log = ft.ListView(spacing=10, padding=14, expand=True)
        
        # Scan result feedback container (for visual feedback)
        scan_result_container = ft.Container(
            content=ft.Text("", size=14, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            padding=16,
            border_radius=12,
            visible=False,
            animate_opacity=300,
        )
        
        # Load recent scans function with time slot support
        def load_recent_scans(time_slot=None):
            """Load recent scans for the selected time slot using new database structure."""
            scan_log.controls.clear()
            
            try:
                # Get attendance data by section which has the timeslot info (THEIR database call)
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
                            icon_color = ft.Colors.ORANGE_600
                        elif time_slot_val == 'afternoon':
                            icon = ft.Icons.NIGHTS_STAY
                            icon_color = ft.Colors.BLUE_600
                        else:
                            icon = ft.Icons.CHECK_CIRCLE
                            icon_color = ft.Colors.GREEN_600
                        
                        # Premium list tile card (YOUR design)
                        scan_log.controls.append(
                            self.create_list_tile_card(
                                leading_icon=icon,
                                leading_color=icon_color,
                                title=user_name,
                                subtitle=timestamp,
                            )
                        )
                else:
                    # Empty state (YOUR design)
                    scan_log.controls.append(
                        self.create_empty_state(
                            icon=ft.Icons.INBOX_ROUNDED,
                            title="No scans yet",
                            subtitle="Scans will appear here",
                            icon_size=48,
                        )
                    )
            
            except Exception as e:
                print(f"Error loading recent scans: {e}")
                scan_log.controls.append(
                    ft.Text(f"Error loading scans: {str(e)}", color=ft.Colors.RED)
                )
            
            # Only update if scan_log is already added to page
            try:
                if hasattr(scan_log, 'page') and scan_log.page:
                    scan_log.update()
            except:
                pass

        load_recent_scans(selected_time_slot[0])
        
        # Get attendance stats (THEIR database call)
        stats = self.db.get_attendance_summary(event_id)
        morning_count = ft.Text(
            str(stats.get('morning', 0)),
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.ORANGE_700
        )
        afternoon_count = ft.Text(
            str(stats.get('afternoon', 0)),
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700
        )
        
        # Premium stats cards (YOUR design)
        stats_card = ft.Row(
            [
                self.create_modern_card(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.WB_SUNNY, size=36, color=ft.Colors.ORANGE_400),
                            ft.Text("Morning", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_700),
                            morning_count,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8
                    ),
                    padding=20,
                ),
                self.create_modern_card(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.NIGHTS_STAY, size=36, color=ft.Colors.BLUE_400),
                            ft.Text("Afternoon", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_700),
                            afternoon_count,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8
                    ),
                    padding=20,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )
        
        # Time slot indicator (YOUR design)
        time_slot_indicator = ft.Container(
            content=ft.Text(
                "☀️ MORNING SESSION",
                size=15,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.ORANGE_700,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            border_radius=24,
            bgcolor=ft.Colors.ORANGE_50,
            border=ft.border.all(2, ft.Colors.ORANGE_200),
        )
        
        # Time slot selection buttons (YOUR premium design)
        morning_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.WB_SUNNY, size=24, color=ft.Colors.WHITE),
                    ft.Text("Morning", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            bgcolor=ft.Colors.ORANGE_400,
            border_radius=12,
            padding=14,
            expand=True,
        )
        
        afternoon_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.NIGHTS_STAY, size=24, color=ft.Colors.GREY_600),
                    ft.Text("Afternoon", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            bgcolor=ft.Colors.GREY_200,
            border_radius=12,
            padding=14,
            expand=True,
        )
        
        # Camera preview (YOUR design)
        camera_image = ft.Image(
            src_base64="",
            width=CAMERA_WIDTH,
            height=CAMERA_HEIGHT,
            fit=ft.ImageFit.CONTAIN,
            visible=False,
            border_radius=16,
        )
        
        camera_placeholder = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.QR_CODE_SCANNER_ROUNDED, 
                        size=90, 
                        color=PRIMARY_COLOR,
                    ),
                    ft.Text(
                        "Tap to start camera",
                        size=17,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_700,
                    ),
                    ft.Text(
                        "Point camera at QR code",
                        size=13,
                        weight=ft.FontWeight.W_400,
                        color=ft.Colors.GREY_500,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=14,
            ),
            width=CAMERA_WIDTH,
            height=CAMERA_HEIGHT,
            bgcolor=ft.Colors.GREY_50,
            border_radius=16,
            border=ft.border.all(2, ft.Colors.GREY_200),
            alignment=ft.alignment.center,
        )
        
        camera_stack = ft.Stack([camera_placeholder, camera_image])
        
        # Camera container with premium styling (YOUR design)
        camera_container = ft.Container(
            content=camera_stack,
            padding=18,
            border_radius=18,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(3, ft.Colors.ORANGE_400),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
        )
        
        # Camera status indicator (YOUR design)
        camera_status = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CIRCLE, size=12, color=ft.Colors.GREY_400),
                    ft.Text(
                        "Camera Ready",
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            border_radius=24,
            bgcolor=ft.Colors.GREY_100,
        )
        
        camera_active = [False]
        
        def select_morning(e):
            """Select morning time slot."""
            selected_time_slot[0] = "morning"
            morning_btn.bgcolor = ft.Colors.ORANGE_400
            morning_btn.content.controls[0].color = ft.Colors.WHITE
            morning_btn.content.controls[1].color = ft.Colors.WHITE
            afternoon_btn.bgcolor = ft.Colors.GREY_200
            afternoon_btn.content.controls[0].color = ft.Colors.GREY_600
            afternoon_btn.content.controls[1].color = ft.Colors.GREY_600
            time_slot_indicator.content.value = "☀️ MORNING SESSION"
            time_slot_indicator.content.color = ft.Colors.ORANGE_700
            time_slot_indicator.bgcolor = ft.Colors.ORANGE_50
            time_slot_indicator.border = ft.border.all(2, ft.Colors.ORANGE_200)
            camera_container.border = ft.border.all(3, ft.Colors.ORANGE_400)
            
            morning_btn.update()
            afternoon_btn.update()
            time_slot_indicator.update()
            camera_container.update()
            
            load_recent_scans("morning")
            self.show_snackbar("☀️ Switched to Morning attendance", ft.Colors.ORANGE)
        
        def select_afternoon(e):
            """Select afternoon time slot."""
            selected_time_slot[0] = "afternoon"
            morning_btn.bgcolor = ft.Colors.GREY_200
            morning_btn.content.controls[0].color = ft.Colors.GREY_600
            morning_btn.content.controls[1].color = ft.Colors.GREY_600
            afternoon_btn.bgcolor = ft.Colors.BLUE_400
            afternoon_btn.content.controls[0].color = ft.Colors.WHITE
            afternoon_btn.content.controls[1].color = ft.Colors.WHITE
            time_slot_indicator.content.value = "🌙 AFTERNOON SESSION"
            time_slot_indicator.content.color = ft.Colors.BLUE_700
            time_slot_indicator.bgcolor = ft.Colors.BLUE_50
            time_slot_indicator.border = ft.border.all(2, ft.Colors.BLUE_200)
            camera_container.border = ft.border.all(3, ft.Colors.BLUE_400)
            
            morning_btn.update()
            afternoon_btn.update()
            time_slot_indicator.update()
            camera_container.update()
            
            load_recent_scans("afternoon")
            self.show_snackbar("🌙 Switched to Afternoon attendance", ft.Colors.BLUE)
        
        morning_btn.on_click = select_morning
        afternoon_btn.on_click = select_afternoon
        
        def update_camera_frame(frame_base64: str):
            """Update the camera preview with new frame."""
            if not camera_active[0]:
                return
            
            try:
                if frame_base64 and len(frame_base64) > 0:
                    camera_image.src_base64 = frame_base64
                    camera_image.visible = True
                    camera_placeholder.visible = False
                    camera_image.update()
                    camera_placeholder.update()
            except Exception as e:
                print(f"Error updating frame: {e}")
        
        def process_scan(qr_data: str):
            """Process QR code scan with new database structure (THEIR logic with YOUR UI feedback)."""
            def _process_in_background():
                try:
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
                    
                    # Check if student exists (THEIR database call)
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
                    
                    # Check if already checked in for this time slot (THEIR database call)
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
                    
                    # Record attendance (THEIR database call)
                    success = self.db.record_timeslot_attendance(event_id, school_id, current_time_slot)
                    
                    # Record scan in activity log (THEIR feature)
                    if success and self.app.current_user:
                        student_name = student.get('name', school_id)
                        self.db.record_scan(
                            scanner_username=self.app.current_user,
                            scanned_user_id=school_id,
                            scanned_user_name=student_name,
                            event_id=event_id
                        )
                    
                    if success:
                        # Show success feedback with animation (YOUR UI)
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
            
            # Run processing in background thread
            threading.Thread(target=_process_in_background, daemon=True).start()
        
        def on_qr_detected(qr_data: str):
            """Callback when QR code is detected."""
            process_scan(qr_data)
        
        # Premium input field (YOUR design)
        qr_input = ft.TextField(
            label="Enter ID manually",
            hint_text="e.g., 2021-00001",
            prefix_icon=ft.Icons.QR_CODE_2,
            height=56,
            border_radius=14,
            filled=True,
            bgcolor=ft.Colors.GREY_50,
            border_color=ft.Colors.GREY_200,
            focused_border_color=PRIMARY_COLOR,
            focused_bgcolor=ft.Colors.WHITE,
            content_padding=ft.padding.symmetric(horizontal=18, vertical=16),
            text_size=15,
            label_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_500),
            expand=True,
        )
        
        def handle_manual_scan(e):
            """Handle manual ID entry."""
            user_id = qr_input.value
            if user_id and user_id.strip():
                qr_input.value = ""
                qr_input.update()
                process_scan(user_id)
        
        def toggle_camera(e):
            """Toggle camera on/off."""
            camera_active[0] = not camera_active[0]
            
            if camera_active[0]:
                # Start camera
                camera_btn.icon = ft.Icons.STOP_CIRCLE_ROUNDED
                camera_btn.style.bgcolor = ft.Colors.RED_600
                camera_btn.tooltip = "Stop Camera"
                
                camera_status.content.controls[0].color = ft.Colors.ORANGE_600
                camera_status.content.controls[1].value = "Starting..."
                camera_status.content.controls[1].color = ft.Colors.ORANGE_700
                camera_status.bgcolor = ft.Colors.ORANGE_50
                
                # Update border based on selected time slot
                if selected_time_slot[0] == "morning":
                    camera_container.border = ft.border.all(3, ft.Colors.ORANGE_400)
                else:
                    camera_container.border = ft.border.all(3, ft.Colors.BLUE_400)
                    
                camera_container.shadow = ft.BoxShadow(
                    blur_radius=24,
                    color=ft.Colors.with_opacity(0.15, ft.Colors.GREEN_400),
                    offset=ft.Offset(0, 4),
                )
                
                camera_btn.update()
                camera_status.update()
                camera_container.update()
                
                # Initialize scanner
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
                            camera_status.content.controls[0].color = ft.Colors.GREEN_600
                            camera_status.content.controls[1].value = "Scanning..."
                            camera_status.content.controls[1].color = ft.Colors.GREEN_700
                            camera_status.bgcolor = ft.Colors.GREEN_50
                            camera_status.update()
                        except:
                            pass
                
                threading.Thread(target=update_status, daemon=True).start()
                
            else:
                # Stop camera
                camera_btn.icon = ft.Icons.VIDEOCAM_ROUNDED
                camera_btn.style.bgcolor = PRIMARY_COLOR
                camera_btn.tooltip = "Start Camera"
                
                camera_status.content.controls[0].color = ft.Colors.GREY_400
                camera_status.content.controls[1].value = "Camera Stopped"
                camera_status.content.controls[1].color = ft.Colors.GREY_600
                camera_status.bgcolor = ft.Colors.GREY_100
                
                camera_container.border = ft.border.all(2, ft.Colors.GREY_200)
                camera_container.shadow = ft.BoxShadow(
                    blur_radius=20,
                    color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                    offset=ft.Offset(0, 4),
                )
                
                camera_image.visible = False
                camera_placeholder.visible = True
                
                if self.app.qr_scanner:
                    self.app.qr_scanner.stop()
                
                camera_btn.update()
                camera_status.update()
                camera_container.update()
                camera_image.update()
                camera_placeholder.update()
        
        qr_input.on_submit = handle_manual_scan
        
        # Premium action buttons (YOUR design)
        camera_btn = ft.IconButton(
            icon=ft.Icons.VIDEOCAM_ROUNDED,
            icon_color=ft.Colors.WHITE,
            icon_size=28,
            style=ft.ButtonStyle(
                bgcolor=PRIMARY_COLOR,
                shape=ft.RoundedRectangleBorder(radius=14),
                padding=14,
                shadow_color=ft.Colors.with_opacity(0.3, PRIMARY_COLOR),
                elevation=3,
            ),
            tooltip="Start Camera",
            on_click=toggle_camera,
        )
        
        submit_btn = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED,
            icon_color=ft.Colors.WHITE,
            icon_size=24,
            style=ft.ButtonStyle(
                bgcolor=PRIMARY_COLOR,
                shape=ft.RoundedRectangleBorder(radius=14),
                padding=14,
                shadow_color=ft.Colors.with_opacity(0.3, PRIMARY_COLOR),
                elevation=3,
            ),
            on_click=handle_manual_scan,
            tooltip="Submit ID",
        )
        
        # Build premium layout with proper alignment (YOUR design)
        content = ft.Column(
            [
                # Time slot selector section
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
                                spacing=12
                            ),
                        ],
                        spacing=12
                    ),
                    padding=16,
                    border_radius=16,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                ),
                
                ft.Container(height=12),
                
                # Current session indicator
                ft.Container(
                    content=time_slot_indicator,
                    alignment=ft.alignment.center,
                ),
                
                ft.Container(height=16),
                
                # Stats cards
                stats_card,
                
                ft.Container(height=20),
                
                # Scan result feedback
                scan_result_container,
                
                # Camera section - centered
                ft.Container(
                    content=camera_container,
                    alignment=ft.alignment.center,
                ),
                ft.Container(height=16),
                
                # Status - centered
                ft.Container(
                    content=camera_status,
                    alignment=ft.alignment.center,
                ),
                
                ft.Container(height=20),
                
                # Input section - full width
                ft.Container(
                    content=ft.Row(
                        [qr_input, camera_btn, submit_btn],
                        spacing=12,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.symmetric(horizontal=0),
                ),
                
                ft.Container(height=24),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=20),
                
                # Recent activity section
                ft.Row(
                    [
                        ft.Icon(ft.Icons.HISTORY_ROUNDED, size=24, color=PRIMARY_COLOR),
                        ft.Text(
                            "Recent Activity",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=PRIMARY_COLOR,
                        ),
                    ],
                    spacing=10,
                ),
                ft.Container(height=14),
                
                # Scan log with premium card
                ft.Container(
                    content=scan_log,
                    padding=0,
                    border_radius=18,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=20,
                        color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                        offset=ft.Offset(0, 4),
                    ),
                    expand=True,
                ),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        return ft.View(
            f"/scan/{event_id}",
            [
                self.create_app_bar(f"Scan: {event['name']}", show_back=True),
                ft.Container(
                    content=content,
                    padding=24,
                    expand=True,
                    bgcolor=ft.Colors.GREY_50,
                )
            ],
            bgcolor=ft.Colors.GREY_50,
        )