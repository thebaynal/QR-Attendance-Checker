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
from config.constants import PRIMARY_COLOR, YELLOW_50


class QRGeneratorView(BaseView):
    """QR code generator from CSV file."""
    
    def build(self):
        """Build and return the QR generator view."""
        try:
            print("DEBUG: Building QR generator view")
            
            # UI Components
            file_picker = ft.FilePicker()
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
                                                    download_qr(data, b64),
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
            
            def download_qr(qr_data: str, img_base64: str):
                """Handle QR code download by saving to Downloads folder."""
                try:
                    # Create qr_codes directory if it doesn't exist
                    qr_dir = os.path.expanduser("~/Downloads/QR_Codes")
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
                    
                    self.show_snackbar(f"QR code saved to Downloads/QR_Codes/{filename}", ft.Colors.GREEN)
                except Exception as ex:
                    self.show_snackbar(f"Download error: {str(ex)}", ft.Colors.RED)
            
            def pick_csv_file(e):
                """Trigger file picker."""
                file_picker.pick_files(
                    allowed_extensions=["csv"],
                    dialog_title="Select CSV file"
                )
            
            # Add file picker to page overlay
            self.page.overlay.append(file_picker)
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
