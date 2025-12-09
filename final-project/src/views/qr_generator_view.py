# views/qr_generator_view.py
"""Modern view for uploading CSV and generating QR codes."""

import flet as ft
import csv
import io
import os
import qrcode
import base64
from datetime import datetime
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR


class QRGeneratorView(BaseView):
    """Modern QR code generator from CSV file."""
    
    def __init__(self, app):
        super().__init__(app)
        self.db = app.db
        self.qr_codes_data = []
    
    def build(self):
        """Build and return the QR generator view."""
        try:
            # UI Components
            file_picker = ft.FilePicker()
            folder_picker = ft.FilePicker()
            
            selected_file_info = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.INSERT_DRIVE_FILE, size=20, color=ft.Colors.GREY_500),
                        ft.Text("No file selected", size=13, color=ft.Colors.GREY_600),
                    ],
                    spacing=8,
                ),
                padding=12,
                border_radius=8,
                border=ft.border.all(1, ft.Colors.GREY_200),
                bgcolor=ft.Colors.GREY_50,
            )
            
            qr_output = ft.Column(
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )
            
            status_container = ft.Container(
                content=ft.Text("", size=14),
                visible=False,
                padding=12,
                border_radius=8,
                animate_opacity=300,
            )
            
            students_data = []
            
            def handle_file_pick(e):
                """Handle file selection."""
                if not e.files:
                    return
                    
                file_path = e.files[0].path
                file_name = e.files[0].name
                
                selected_file_info.content.controls[1].value = file_name
                selected_file_info.border = ft.border.all(1, PRIMARY_COLOR)
                selected_file_info.bgcolor = ft.Colors.BLUE_50
                selected_file_info.update()
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        csv_reader = csv.DictReader(f)
                        rows = list(csv_reader)
                    
                    if not rows:
                        status_container.content.value = "❌ CSV file is empty"
                        status_container.content.color = ft.Colors.RED_700
                        status_container.bgcolor = ft.Colors.RED_50
                        status_container.border = ft.border.all(1, ft.Colors.RED_200)
                        status_container.visible = True
                        status_container.update()
                        return
                    
                    # Clear previous data
                    qr_output.controls.clear()
                    self.qr_codes_data.clear()
                    students_data.clear()
                    
                    valid_count = 0
                    
                    # Generate QR codes
                    for idx, row in enumerate(rows, 1):
                        school_id = list(row.values())[0].strip() if row else None
                        if not school_id:
                            continue
                        
                        row_values = list(row.values())
                        student_name = row_values[1].strip() if len(row_values) > 1 else "N/A"
                        
                        qr_data = f"{school_id}|{student_name}"
                        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, 
                                          box_size=10, border=2)
                        qr.add_data(qr_data)
                        qr.make(fit=True)
                        
                        img = qr.make_image(fill_color="black", back_color="white")
                        buffer = io.BytesIO()
                        img.save(buffer, format='PNG')
                        img_base64 = base64.b64encode(buffer.getvalue()).decode()
                        
                        self.qr_codes_data.append((qr_data, img_base64))
                        students_data.append({
                            "school_id": school_id,
                            "name": student_name,
                            "qr_data": qr_data,
                            "row_data": row
                        })
                        
                        # Create modern QR card
                        qr_card = self.create_modern_card(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.PERSON, color=PRIMARY_COLOR, size=20),
                                            ft.Column(
                                                [
                                                    ft.Text(student_name, size=14, weight=ft.FontWeight.W_600),
                                                    ft.Text(f"ID: {school_id}", size=12, color=ft.Colors.GREY_600),
                                                ],
                                                spacing=2,
                                                expand=True,
                                            ),
                                        ],
                                        spacing=12,
                                    ),
                                    ft.Container(
                                        content=ft.Image(
                                            src_base64=img_base64,
                                            width=180,
                                            height=180,
                                            fit=ft.ImageFit.CONTAIN,
                                        ),
                                        bgcolor=ft.Colors.WHITE,
                                        border_radius=12,
                                        padding=12,
                                        alignment=ft.alignment.center,
                                    ),
                                    ft.OutlinedButton(
                                        content=ft.Row(
                                            [
                                                ft.Icon(ft.Icons.DOWNLOAD, size=18),
                                                ft.Text("Download", size=13),
                                            ],
                                            spacing=8,
                                            alignment=ft.MainAxisAlignment.CENTER,
                                        ),
                                        width=180,
                                        height=40,
                                        on_click=lambda e, data=qr_data, b64=img_base64: 
                                            download_single_qr(data, b64),
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=10),
                                        ),
                                    )
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=12,
                            ),
                            padding=16,
                        )
                        qr_output.controls.append(qr_card)
                        valid_count += 1
                    
                    if valid_count > 0:
                        status_container.content.value = f"✅ Generated {valid_count} QR code(s)"
                        status_container.content.color = ft.Colors.GREEN_700
                        status_container.bgcolor = ft.Colors.GREEN_50
                        status_container.border = ft.border.all(1, ft.Colors.GREEN_200)
                    else:
                        status_container.content.value = "⚠️ No valid data found in CSV"
                        status_container.content.color = ft.Colors.ORANGE_700
                        status_container.bgcolor = ft.Colors.ORANGE_50
                        status_container.border = ft.border.all(1, ft.Colors.ORANGE_200)
                    
                    status_container.visible = True
                    qr_output.update()
                    
                except Exception as ex:
                    status_container.content.value = f"❌ Error: {str(ex)}"
                    status_container.content.color = ft.Colors.RED_700
                    status_container.bgcolor = ft.Colors.RED_50
                    status_container.border = ft.border.all(1, ft.Colors.RED_200)
                    status_container.visible = True
                
                status_container.update()
            
            def download_single_qr(qr_data: str, img_base64: str):
                def on_folder_selected(e):
                    if e.path:
                        try:
                            safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in qr_data)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"QR_{safe_name}_{timestamp}.png"
                            file_path = os.path.join(e.path, filename)
                            
                            img_data = base64.b64decode(img_base64)
                            with open(file_path, 'wb') as f:
                                f.write(img_data)
                            
                            self.show_snackbar(f"✅ QR code saved: {filename}", ft.Colors.GREEN)
                        except Exception as ex:
                            self.show_snackbar(f"❌ Download error: {str(ex)}", ft.Colors.RED)
                
                folder_picker.on_result = on_folder_selected
                folder_picker.get_directory_path("Select folder to save QR code")
            
            def download_all_qrs(e):
                if not self.qr_codes_data:
                    self.show_snackbar("⚠️ No QR codes to download", ft.Colors.ORANGE)
                    return
                
                def on_folder_selected(e):
                    if e.path:
                        try:
                            count = 0
                            base_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            for idx, (qr_data, img_base64) in enumerate(self.qr_codes_data, 1):
                                safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in qr_data)
                                filename = f"QR_{safe_name}_{base_timestamp}_{idx:03d}.png"
                                file_path = os.path.join(e.path, filename)
                                
                                img_data = base64.b64decode(img_base64)
                                with open(file_path, 'wb') as f:
                                    f.write(img_data)
                                count += 1
                            
                            self.show_snackbar(f"✅ Downloaded {count} QR code(s)!", ft.Colors.GREEN)
                        except Exception as ex:
                            self.show_snackbar(f"❌ Download error: {str(ex)}", ft.Colors.RED)
                
                folder_picker.on_result = on_folder_selected
                folder_picker.get_directory_path(f"Select folder to save {len(self.qr_codes_data)} QR code(s)")
            
            def save_students_to_db(e):
                if not students_data:
                    self.show_snackbar("⚠️ No students to save", ft.Colors.ORANGE)
                    return
                
                def confirm_save(e):
                    try:
                        self.page.close(dlg)
                        
                        self.db._execute("""
                        CREATE TABLE IF NOT EXISTS students_qrcodes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            school_id TEXT NOT NULL UNIQUE,
                            name TEXT NOT NULL,
                            qr_data TEXT NOT NULL UNIQUE,
                            qr_data_encoded TEXT NOT NULL,
                            csv_data TEXT,
                            created_at TEXT NOT NULL,
                            FOREIGN KEY (school_id) REFERENCES attendance(user_id)
                        )
                        """)
                        
                        saved_count = 0
                        for student in students_data:
                            try:
                                check_query = "SELECT id FROM students_qrcodes WHERE school_id = ?"
                                existing = self.db._execute(check_query, (student['school_id'],), fetch_one=True)
                                
                                if existing:
                                    update_query = """
                                    UPDATE students_qrcodes 
                                    SET name = ?, qr_data = ?, qr_data_encoded = ?, csv_data = ?
                                    WHERE school_id = ?
                                    """
                                    self.db._execute(update_query, (
                                        student['name'], student['qr_data'],
                                        next(b64 for data, b64 in self.qr_codes_data if data == student['qr_data']),
                                        str(student['row_data']), student['school_id']
                                    ))
                                else:
                                    insert_query = """
                                    INSERT INTO students_qrcodes 
                                    (school_id, name, qr_data, qr_data_encoded, csv_data, created_at)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                    """
                                    self.db._execute(insert_query, (
                                        student['school_id'], student['name'], student['qr_data'],
                                        next(b64 for data, b64 in self.qr_codes_data if data == student['qr_data']),
                                        str(student['row_data']), datetime.now().isoformat()
                                    ))
                                saved_count += 1
                            except Exception as ex:
                                print(f"Error saving student {student.get('school_id')}: {ex}")
                        
                        self.show_snackbar(f"✅ Saved {saved_count} student(s) to database", ft.Colors.GREEN)
                        
                    except Exception as ex:
                        print(f"Database error: {str(ex)}")
                        import traceback
                        traceback.print_exc()
                        self.show_snackbar(f"❌ Database error: {str(ex)}", ft.Colors.RED)
                
                dlg = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Save to Database?", weight=ft.FontWeight.BOLD),
                    content=ft.Text(
                        f"This will save {len(students_data)} student(s) with their QR codes.\n\n"
                        "Existing students will be updated.",
                        size=14,
                    ),
                    actions=[
                        ft.TextButton("Cancel", on_click=lambda e: self.page.close(dlg)),
                        self.create_modern_button(
                            text="Save",
                            icon=ft.Icons.SAVE,
                            on_click=confirm_save,
                            width=140,
                            height=45,
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                self.page.open(dlg)
            
            # File picker setup
            self.page.overlay.append(file_picker)
            self.page.overlay.append(folder_picker)
            file_picker.on_result = handle_file_pick
            
            # Main content
            content_card = self.create_modern_card(
                content=ft.Column(
                    [
                        # Header
                        self.create_section_title("QR Code Generator", size=24, icon=ft.Icons.QR_CODE_2),
                        ft.Text(
                            "Upload a CSV file to generate QR codes for students",
                            size=14,
                            color=ft.Colors.GREY_600,
                        ),
                        
                        ft.Container(height=24),
                        
                        # File selection
                        self.create_modern_button(
                            text="Choose CSV File",
                            icon=ft.Icons.UPLOAD_FILE,
                            on_click=lambda e: file_picker.pick_files(
                                allowed_extensions=["csv"],
                                dialog_title="Select CSV file"
                            ),
                            width=240,
                        ),
                        ft.Container(height=12),
                        selected_file_info,
                        
                        ft.Container(height=20),
                        status_container,
                        
                        # Action buttons
                        ft.Row(
                            [
                                self.create_modern_button(
                                    text="Download All",
                                    icon=ft.Icons.DOWNLOAD,
                                    on_click=download_all_qrs,
                                    width=180,
                                ),
                                ft.ElevatedButton(
                                    content=ft.Row(
                                        [
                                            ft.Icon(ft.Icons.SAVE, size=18),
                                            ft.Text("Save to DB", size=15),
                                        ],
                                        spacing=8,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                    width=180,
                                    height=50,
                                    on_click=save_students_to_db,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                        bgcolor=ft.Colors.BLUE,
                                        color=ft.Colors.WHITE,
                                        text_style=ft.TextStyle(
                                            size=15,
                                            weight=ft.FontWeight.W_600,
                                        ),
                                        elevation=0,
                                    )
                                ),
                            ],
                            spacing=12,
                            wrap=True,
                        ),
                        
                        ft.Container(height=16),
                        ft.Divider(color=ft.Colors.GREY_200),
                        ft.Container(height=16),
                        
                        # QR codes output
                        self.create_section_title("Generated QR Codes", size=18),
                        ft.Container(height=12),
                        ft.Container(
                            content=qr_output,
                            expand=True,
                        ),
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                padding=24,
                expand=True,
            )
            
            return ft.View(
                "/qr_generator",
                [
                    self.create_app_bar("QR Generator", show_back=True),
                    ft.Container(
                        content=content_card,
                        padding=20,
                        expand=True,
                        bgcolor=ft.Colors.GREY_50,
                    )
                ],
                bgcolor=ft.Colors.GREY_50,
            )
        
        except Exception as e:
            print(f"ERROR building QR generator view: {e}")
            import traceback
            traceback.print_exc()
            
            return ft.View(
                "/qr_generator",
                [
                    self.create_app_bar("QR Generator", show_back=True),
                    self.create_empty_state(
                        icon=ft.Icons.ERROR_OUTLINE,
                        title="Error loading QR generator",
                        subtitle=str(e),
                    )
                ],
                bgcolor=ft.Colors.GREY_50,
            )