# views/event_view.py
"""Event view with enhanced PDF export and premium styling."""

import flet as ft
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR
from utils.pdf_export import AttendancePDFExporter
from datetime import datetime
import os
import threading
from tkinter import filedialog
import tkinter as tk


class EventView(BaseView):
    """Event detail with grouped attendance export and premium design."""
    
    def build(self, event_id: str):
        """Build event detail view with premium styling."""
        try:
            print(f"DEBUG: Building event view for event_id: {event_id}")
            
            event = self.db.get_event_by_id(event_id)
            if not event:
                print(f"DEBUG: Event not found: {event_id}")
                self.page.go("/home")
                return ft.View("/", [ft.Container()])
            
            print(f"DEBUG: Event found: {event}")
            
            # Get current user role
            current_username = self.app.current_user
            current_user_role = self.db.get_user_role(current_username) if current_username else 'scanner'
            is_admin = current_user_role and current_user_role.lower() == 'admin'
            
            # Get attendance by section (THEIR new database structure)
            attendance_by_section = self.db.get_attendance_by_section(event_id)
            print(f"DEBUG: attendance_by_section: {attendance_by_section}")
            
            if not attendance_by_section:
                print("DEBUG: No attendance data found")
                attendance_by_section = {}
            
            # Create section tabs with YOUR premium styling
            section_tabs = []
            for section_name, students in sorted(attendance_by_section.items()):
                # Calculate stats
                total = len(students)
                morning_present = sum(1 for s in students if s.get('morning_status') == 'Present')
                afternoon_present = sum(1 for s in students if s.get('afternoon_status') == 'Present')
                
                # Create premium table for this section - YOUR styling
                table_data = ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("#", weight=ft.FontWeight.BOLD, size=13, color=PRIMARY_COLOR)),
                        ft.DataColumn(ft.Text("Student ID", weight=ft.FontWeight.BOLD, size=13, color=PRIMARY_COLOR)),
                        ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD, size=13, color=PRIMARY_COLOR)),
                        ft.DataColumn(ft.Text("Morning Time", weight=ft.FontWeight.BOLD, size=13, color=PRIMARY_COLOR)),
                        ft.DataColumn(ft.Text("Morning", weight=ft.FontWeight.BOLD, size=13, color=PRIMARY_COLOR)),
                        ft.DataColumn(ft.Text("Afternoon Time", weight=ft.FontWeight.BOLD, size=13, color=PRIMARY_COLOR)),
                        ft.DataColumn(ft.Text("Afternoon", weight=ft.FontWeight.BOLD, size=13, color=PRIMARY_COLOR)),
                    ],
                    rows=[
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(idx), size=12)),
                                ft.DataCell(ft.Text(s.get('school_id', ''), size=12)),
                                ft.DataCell(ft.Text(s.get('name', ''), size=12, weight=ft.FontWeight.W_500)),
                                ft.DataCell(ft.Text(s.get('morning_time') or '-', size=11, color=ft.Colors.GREY_600)),
                                ft.DataCell(
                                    ft.Container(
                                        content=ft.Text(
                                            s.get('morning_status', 'Absent'),
                                            size=11,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.WHITE
                                        ),
                                        bgcolor=ft.Colors.GREEN_600 if s.get('morning_status') == 'Present' else ft.Colors.RED_400,
                                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                        border_radius=8,
                                    )
                                ),
                                ft.DataCell(ft.Text(s.get('afternoon_time') or '-', size=11, color=ft.Colors.GREY_600)),
                                ft.DataCell(
                                    ft.Container(
                                        content=ft.Text(
                                            s.get('afternoon_status', 'Absent'),
                                            size=11,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.WHITE
                                        ),
                                        bgcolor=ft.Colors.GREEN_600 if s.get('afternoon_status') == 'Present' else ft.Colors.RED_400,
                                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                        border_radius=8,
                                    )
                                ),
                            ]
                        ) for idx, s in enumerate(students, 1)
                    ],
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    border_radius=12,
                    heading_row_color=ft.Colors.BLUE_50,
                    heading_row_height=52,
                    data_row_min_height=56,
                    column_spacing=16,
                    horizontal_margin=16,
                )
                
                # Section content with YOUR premium styling
                section_content = ft.Column(
                    [
                        # Premium stats card
                        self.create_modern_card(
                            content=ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text("Total", size=11, color=ft.Colors.GREY_500, weight=ft.FontWeight.W_500),
                                            ft.Text(str(total), size=24, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=4,
                                        expand=True,
                                    ),
                                    ft.Container(width=1, height=40, bgcolor=ft.Colors.GREY_200),
                                    ft.Column(
                                        [
                                            ft.Row(
                                                [
                                                    ft.Icon(ft.Icons.WB_SUNNY, size=14, color=ft.Colors.ORANGE_600),
                                                    ft.Text("Morning", size=11, color=ft.Colors.GREY_500, weight=ft.FontWeight.W_500),
                                                ],
                                                spacing=4,
                                                alignment=ft.MainAxisAlignment.CENTER,
                                            ),
                                            ft.Text(f"{morning_present}/{total}", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=4,
                                        expand=True,
                                    ),
                                    ft.Container(width=1, height=40, bgcolor=ft.Colors.GREY_200),
                                    ft.Column(
                                        [
                                            ft.Row(
                                                [
                                                    ft.Icon(ft.Icons.NIGHTS_STAY, size=14, color=ft.Colors.BLUE_600),
                                                    ft.Text("Afternoon", size=11, color=ft.Colors.GREY_500, weight=ft.FontWeight.W_500),
                                                ],
                                                spacing=4,
                                                alignment=ft.MainAxisAlignment.CENTER,
                                            ),
                                            ft.Text(f"{afternoon_present}/{total}", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=4,
                                        expand=True,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            padding=20,
                        ),
                        ft.Container(height=16),
                        # Table in premium card
                        self.create_modern_card(
                            content=ft.Column(
                                [table_data],
                                scroll=ft.ScrollMode.AUTO,
                            ),
                            padding=0,
                        ),
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                )
                
                section_tabs.append(
                    ft.Tab(
                        text=section_name,
                        content=section_content
                    )
                )
            
            # Create tabs view
            tabs = ft.Tabs(
                tabs=section_tabs if section_tabs else [
                    ft.Tab(
                        text="No Data",
                        content=ft.Container(
                            content=self.create_empty_state(
                                icon=ft.Icons.INBOX_ROUNDED,
                                title="No attendance records yet",
                                subtitle="Scan QR codes to record attendance",
                            ),
                            expand=True,
                        )
                    )
                ],
                expand=True,
            )
            
            def export_to_pdf(e):
                """Export attendance to PDF with file picker - THEIR new PDF exporter."""
                # Check if user is admin
                if not is_admin:
                    self.show_snackbar("Only admins can export attendance reports", ft.Colors.RED)
                    return
                
                try:
                    print("DEBUG: Export to PDF button clicked")
                    
                    # Sanitize event name for filename
                    safe_event_name = "".join(c for c in event['name'] if c.isalnum() or c in (' ', '-', '_')).strip()
                    
                    # Generate default filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    default_filename = f"Attendance_{safe_event_name}_{timestamp}.pdf"
                    
                    # Show file picker dialog in a separate thread to avoid blocking UI
                    def pick_save_location():
                        try:
                            # Create hidden root window for tkinter
                            root = tk.Tk()
                            root.withdraw()
                            root.attributes('-topmost', True)
                            
                            # Show file save dialog
                            filepath = filedialog.asksaveasfilename(
                                defaultextension=".pdf",
                                initialfile=default_filename,
                                initialdir=os.path.expanduser("~/Documents"),
                                filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
                                title="Save Attendance Report"
                            )
                            
                            root.destroy()
                            
                            # If user cancelled, return None
                            if not filepath:
                                print("DEBUG: File picker cancelled by user")
                                return None
                            
                            print(f"DEBUG: User selected location: {filepath}")
                            return filepath
                        
                        except Exception as picker_error:
                            print(f"Error in file picker: {picker_error}")
                            return None
                    
                    # Run file picker in background thread
                    filepath = pick_save_location()
                    
                    if not filepath:
                        print("DEBUG: No file location selected")
                        return
                    
                    print(f"DEBUG: Exporting to {filepath}")
                    
                    # Create parent directory if it doesn't exist
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    
                    # Export using THEIR new PDF exporter
                    exporter = AttendancePDFExporter(self.db)
                    result = exporter.export_attendance(event_id, filepath)
                    
                    # Verify file was created
                    if os.path.exists(filepath):
                        file_size = os.path.getsize(filepath)
                        print(f"DEBUG: PDF created successfully, size: {file_size} bytes")
                        print(f"DEBUG: Export result: {result}")
                        
                        # Show success message with file location
                        filename_only = os.path.basename(filepath)
                        self.show_snackbar(f"✅ PDF saved: {filename_only}", ft.Colors.GREEN)
                    else:
                        print(f"DEBUG: PDF file was not created at {filepath}")
                        raise FileNotFoundError(f"PDF file was not created: {filepath}")
                    
                except Exception as ex:
                    print(f"Export error: {ex}")
                    import traceback
                    traceback.print_exc()
                    self.show_snackbar(f"❌ Export failed: {str(ex)}", ft.Colors.RED)
            
            # Build premium layout - YOUR design
            content = ft.Column(
                [
                    # Event header card - YOUR premium styling
                    self.create_modern_card(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=ft.Icon(ft.Icons.EVENT, color=ft.Colors.WHITE, size=32),
                                    width=64,
                                    height=64,
                                    bgcolor=PRIMARY_COLOR,
                                    border_radius=16,
                                    alignment=ft.alignment.center,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            event['name'],
                                            size=22,
                                            weight=ft.FontWeight.BOLD,
                                            color=PRIMARY_COLOR,
                                        ),
                                        ft.Row(
                                            [
                                                ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color=ft.Colors.GREY_600),
                                                ft.Text(event['date'], size=14, color=ft.Colors.GREY_700),
                                            ],
                                            spacing=8,
                                        ),
                                    ],
                                    spacing=6,
                                    expand=True,
                                ),
                            ],
                            spacing=16,
                        ),
                        padding=24,
                    ),
                    
                    ft.Container(height=16),
                    
                    # Export button - only for admins - YOUR premium button
                    self.create_modern_button(
                        text="Export to PDF",
                        icon=ft.Icons.PICTURE_AS_PDF,
                        on_click=export_to_pdf,
                        width=360,
                    ) if is_admin else ft.Container(),
                    
                    ft.Container(height=16) if is_admin else ft.Container(),
                    
                    # Tabs with attendance data
                    ft.Container(
                        content=tabs,
                        expand=True,
                    ),
                ],
                spacing=0,
                expand=True,
            )
            
            return ft.View(
                f"/event/{event_id}",
                [
                    self.create_app_bar(event['name'], show_back=True),
                    ft.Container(
                        content=content,
                        padding=20,
                        expand=True,
                        bgcolor=ft.Colors.GREY_50,
                    )
                ],
                bgcolor=ft.Colors.GREY_50,
            )
        
        except Exception as e:
            print(f"ERROR building event view: {e}")
            import traceback
            traceback.print_exc()
            
            # Return error view with YOUR styling
            return ft.View(
                f"/event/{event_id}",
                [
                    self.create_app_bar("Event Error", show_back=True),
                    ft.Container(
                        content=self.create_empty_state(
                            icon=ft.Icons.ERROR_OUTLINE,
                            title="Error loading event",
                            subtitle=str(e),
                        ),
                        expand=True,
                        alignment=ft.alignment.center,
                    )
                ],
                bgcolor=ft.Colors.GREY_50,
            )