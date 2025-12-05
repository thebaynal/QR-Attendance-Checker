# views/qr_generator_view.py
"""View for uploading CSV and generating QR codes."""

import flet as ft
import csv
import io
import os
import qrcode
import base64
from datetime import datetime
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR, BLUE_50
from database.db_manager import Database


class QRGeneratorView(BaseView):
    """QR code generator from CSV file."""
    
    def __init__(self, app):
        """Initialize with access to the app and database."""
        super().__init__(app)
        self.db = app.db
        self.qr_codes_data = []
    
    def build(self):
        """Build and return the QR generator view."""
        try:
            print("DEBUG: Building QR generator view")
            
            # UI Components
            file_picker = ft.FilePicker()
            folder_picker = ft.FilePicker()
            selected_file_name = ft.Text(
                "No file selected",
                size=12,
                color=ft.Colors.GREY_600
            )
            
            qr_output = ft.Column(
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )
            
            status_text = ft.Text(
                "",
                size=14,
                color=ft.Colors.GREY_700,
                weight=ft.FontWeight.BOLD
            )
            
            # Store student data for database insertion
            students_data = []
            
            def handle_file_pick(e):
                """Handle file selection."""
                if e.files:
                    file_path = e.files[0].path
                    selected_file_name.value = f"Selected: {e.files[0].name}"
                    selected_file_name.update()
                    
                    try:
                        # Read and parse CSV
                        with open(file_path, 'r', encoding='utf-8') as f:
                            csv_reader = csv.DictReader(f)
                            rows = list(csv_reader)
                        
                        if not rows:
                            status_text.value = "CSV file is empty"
                            status_text.color = ft.Colors.RED
                            status_text.update()
                            return
                        
                        # Clear previous QR codes
                        qr_output.controls.clear()
                        self.qr_codes_data.clear()
                        students_data.clear()
                        
                        valid_count = 0
                        
                        # Generate QR code for each row
                        for idx, row in enumerate(rows, 1):
                            # Use first column value as school ID
                            school_id = list(row.values())[0].strip() if row else None
                            
                            if not school_id:
                                continue
                            
                            # Get student name from second column if available
                            row_values = list(row.values())
                            student_name = row_values[1].strip() if len(row_values) > 1 else "N/A"
                            
                            # Generate QR code with both ID and name (separated by pipe)
                            qr_data = f"{school_id}|{student_name}"
                            qr = qrcode.QRCode(
                                version=1,
                                error_correction=qrcode.constants.ERROR_CORRECT_L,
                                box_size=10,
                                border=2,
                            )
                            qr.add_data(qr_data)
                            qr.make(fit=True)
                            
                            # Convert to image and then to base64
                            img = qr.make_image(fill_color="black", back_color="white")
                            
                            # Convert PIL image to base64
                            buffer = io.BytesIO()
                            img.save(buffer, format='PNG')
                            img_base64 = base64.b64encode(buffer.getvalue()).decode()
                            
                            # Store QR code data and student info
                            self.qr_codes_data.append((qr_data, img_base64))
                            students_data.append({
                                "school_id": school_id,
                                "name": student_name,
                                "qr_data": qr_data,
                                "row_data": row
                            })
                            
                            # Create card for each QR code
                            qr_card = ft.Card(
                                content=ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Text(
                                                f"{school_id}: {student_name}",
                                                size=12,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.GREY_800
                                            ),
                                            ft.Image(
                                                src_base64=img_base64,
                                                width=200,
                                                height=200,
                                                fit=ft.ImageFit.CONTAIN
                                            ),
                                            ft.Text(
                                                f"Payload: {qr_data}",
                                                size=10,
                                                color=ft.Colors.GREY_500
                                            ),
                                            ft.ElevatedButton(
                                                "Download",
                                                icon=ft.Icons.DOWNLOAD,
                                                width=180,
                                                on_click=lambda e, data=qr_data, b64=img_base64: 
                                                    download_single_qr(data, b64),
                                                style=ft.ButtonStyle(
                                                    bgcolor=PRIMARY_COLOR,
                                                    color=ft.Colors.BLACK
                                                )
                                            )
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=10
                                    ),
                                    padding=15,
                                    bgcolor=YELLOW_50,
                                    border_radius=10
                                )
                            )
                            qr_output.controls.append(qr_card)
                            valid_count += 1
                        
                        # Show results summary
                        if valid_count > 0:
                            status_text.value = f"Generated {valid_count} QR code(s)"
                            status_text.color = ft.Colors.GREEN
                        else:
                            status_text.value = "No data found in CSV"
                            status_text.color = ft.Colors.RED
                        
                        qr_output.update()
                        
                    except Exception as ex:
                        status_text.value = f"Error: {str(ex)}"
                        status_text.color = ft.Colors.RED
                    
                    status_text.update()
            
            def download_single_qr(qr_data: str, img_base64: str):
                """Handle single QR code download with folder selection."""
                # Create a callback for folder selection
                def on_folder_selected(e):
                    if e.path:
                        try:
                            qr_dir = e.path
                            os.makedirs(qr_dir, exist_ok=True)
                            
                            # Generate filename from QR data and timestamp
                            safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in qr_data)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"QR_{safe_name}_{timestamp}.png"
                            file_path = os.path.join(qr_dir, filename)
                            
                            # Decode base64 and save image
                            img_data = base64.b64decode(img_base64)
                            with open(file_path, 'wb') as f:
                                f.write(img_data)
                            
                            self.show_snackbar(f"QR code saved: {filename}", ft.Colors.GREEN)
                        except Exception as ex:
                            self.show_snackbar(f"Download error: {str(ex)}", ft.Colors.RED)
                
                # Set the callback and open folder picker
                folder_picker.on_result = on_folder_selected
                folder_picker.get_directory_path("Select folder to save QR code")
            
            def download_all_qrs(e):
                """Download all generated QR codes after user selects a folder."""
                if not self.qr_codes_data:
                    self.show_snackbar("No QR codes to download", ft.Colors.ORANGE)
                    return
                
                def on_folder_selected(e):
                    if e.path:
                        try:
                            qr_dir = e.path
                            os.makedirs(qr_dir, exist_ok=True)
                            
                            count = 0
                            base_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            for idx, (qr_data, img_base64) in enumerate(self.qr_codes_data, 1):
                                safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in qr_data)
                                filename = f"QR_{safe_name}_{base_timestamp}_{idx:03d}.png"
                                file_path = os.path.join(qr_dir, filename)
                                
                                img_data = base64.b64decode(img_base64)
                                with open(file_path, 'wb') as f:
                                    f.write(img_data)
                                count += 1
                            
                            self.show_snackbar(f"Downloaded {count} QR code(s) successfully!", ft.Colors.GREEN)
                        except Exception as ex:
                            self.show_snackbar(f"Download error: {str(ex)}", ft.Colors.RED)
                
                # Set the callback and open folder picker
                folder_picker.on_result = on_folder_selected
                folder_picker.get_directory_path(f"Select folder to save {len(self.qr_codes_data)} QR code(s)")
            
            def save_students_to_db(e):
                """Save all students to database with their QR codes after confirmation."""
                if not students_data:
                    self.show_snackbar("No students to save", ft.Colors.ORANGE)
                    return
                
                print(f"DEBUG: Save button clicked, students_data has {len(students_data)} students")
                
                def confirm_save(e):
                    print("DEBUG: Confirm save clicked")
                    try:
                        # Close dialog first
                        self.page.close(dlg)
                        
                        # Add students_qrcodes table if it doesn't exist
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
                        failed_count = 0
                        
                        for student in students_data:
                            try:
                                # Check if student already exists
                                check_query = "SELECT id FROM students_qrcodes WHERE school_id = ?"
                                existing = self.db._execute(check_query, (student['school_id'],), fetch_one=True)
                                
                                if existing:
                                    # Update existing student
                                    update_query = """
                                    UPDATE students_qrcodes 
                                    SET name = ?, qr_data = ?, qr_data_encoded = ?, csv_data = ?
                                    WHERE school_id = ?
                                    """
                                    self.db._execute(update_query, (
                                        student['name'],
                                        student['qr_data'],
                                        # Find the base64 encoded version
                                        next(b64 for data, b64 in self.qr_codes_data if data == student['qr_data']),
                                        str(student['row_data']),
                                        student['school_id']
                                    ))
                                else:
                                    # Insert new student
                                    insert_query = """
                                    INSERT INTO students_qrcodes 
                                    (school_id, name, qr_data, qr_data_encoded, csv_data, created_at)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                    """
                                    self.db._execute(insert_query, (
                                        student['school_id'],
                                        student['name'],
                                        student['qr_data'],
                                        # Find the base64 encoded version
                                        next(b64 for data, b64 in self.qr_codes_data if data == student['qr_data']),
                                        str(student['row_data']),
                                        datetime.now().isoformat()
                                    ))
                                saved_count += 1
                            except Exception as ex:
                                print(f"Error saving student {student.get('school_id')}: {ex}")
                                failed_count += 1
                        
                        message = f"Saved {saved_count} student(s) to database"
                        if failed_count > 0:
                            message += f" ({failed_count} failed)"
                        self.show_snackbar(message, ft.Colors.GREEN)
                        print(f"DEBUG: {message}")
                        
                    except Exception as ex:
                        print(f"DEBUG: Database error: {str(ex)}")
                        import traceback
                        traceback.print_exc()
                        self.show_snackbar(f"Database error: {str(ex)}", ft.Colors.RED)
                
                def cancel_save(e):
                    print("DEBUG: Cancel save clicked")
                    self.page.close(dlg)
                
                # Create dialog
                dlg = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Save Students to Database?", weight=ft.FontWeight.BOLD),
                    content=ft.Text(
                        f"This will save {len(students_data)} student(s) with their QR codes to the database.\n\n"
                        f"Existing students will be updated.",
                        size=14
                    ),
                    actions=[
                        ft.TextButton("Cancel", on_click=cancel_save),
                        ft.ElevatedButton(
                            "Save to Database", 
                            on_click=confirm_save, 
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.BLUE,
                                color=ft.Colors.WHITE
                            )
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                
                # Open dialog using page.open() instead of setting page.dialog
                self.page.open(dlg)
                print("DEBUG: Dialog opened using page.open()")
                            
            def pick_csv_file(e):
                """Trigger file picker."""
                file_picker.pick_files(
                    allowed_extensions=["csv"],
                    dialog_title="Select CSV file"
                )
            
            # Add file picker to page overlay
            self.page.overlay.append(file_picker)
            self.page.overlay.append(folder_picker)
            file_picker.on_result = handle_file_pick
            
            print("DEBUG: QR generator view built successfully")
            return ft.View(
                "/qr_generator",
                [
                    self.create_app_bar("QR Code Generator", show_back=True),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Upload CSV File",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color=PRIMARY_COLOR
                                ),
                                ft.Text(
                                    "The first column will be used as QR code data",
                                    size=12,
                                    color=ft.Colors.GREY_600,
                                    italic=True
                                ),
                                ft.Container(height=10),
                                ft.ElevatedButton(
                                    "Choose CSV File",
                                    icon=ft.Icons.UPLOAD_FILE,
                                    width=250,
                                    height=50,
                                    on_click=pick_csv_file,
                                    style=ft.ButtonStyle(
                                        bgcolor=PRIMARY_COLOR,
                                        color=ft.Colors.BLACK
                                    )
                                ),
                                selected_file_name,
                                ft.Divider(),
                                status_text,
                                ft.Container(height=10),
                                ft.Row(
                                    [
                                        ft.ElevatedButton(
                                            "Download All QR Codes",
                                            icon=ft.Icons.DOWNLOAD,
                                            on_click=download_all_qrs,
                                            style=ft.ButtonStyle(
                                                bgcolor=PRIMARY_COLOR,
                                                color=ft.Colors.BLACK
                                            )
                                        ),
                                        ft.ElevatedButton(
                                            "Save to Database",
                                            icon=ft.Icons.SAVE,
                                            on_click=save_students_to_db,
                                            style=ft.ButtonStyle(
                                                bgcolor=ft.Colors.BLUE,
                                                color=ft.Colors.WHITE
                                            )
                                        ),
                                    ],
                                    spacing=10,
                                    wrap=True
                                ),
                                ft.Text(
                                    "Generated QR Codes",
                                    size=16,
                                    weight=ft.FontWeight.BOLD
                                ),
                                ft.Container(
                                    content=qr_output,
                                    expand=True,
                                    border=ft.border.all(1, ft.Colors.GREY_300),
                                    border_radius=10,
                                    padding=10
                                )
                            ],
                            spacing=15,
                            expand=True
                        ),
                        padding=20,
                        expand=True
                    )
                ]
            )
        
        except Exception as e:
            print(f"ERROR building QR generator view: {e}")
            import traceback
            traceback.print_exc()
            
            # Return error view
            return ft.View(
                "/qr_generator",
                [
                    self.create_app_bar("QR Code Generator", show_back=True),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.ERROR, size=80, color=ft.Colors.RED),
                                ft.Text("Error loading QR generator", size=20, color=ft.Colors.RED),
                                ft.Text(str(e), size=14, color=ft.Colors.GREY_600),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20
                        ),
                        alignment=ft.alignment.center,
                        expand=True
                    )
                ]
            )
