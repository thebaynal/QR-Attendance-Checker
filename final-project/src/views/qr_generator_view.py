# views/qr_generator_view.py
"""View for uploading CSV and generating QR codes."""

import flet as ft
import csv
import io
import qrcode
import base64
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR, YELLOW_50


class QRGeneratorView(BaseView):
    """QR code generator from CSV file."""
    
    def build(self):
        """Build and return the QR generator view."""
        
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
                    
                    # Generate QR code for each row
                    for idx, row in enumerate(rows, 1):
                        # Use first column value as QR data
                        qr_data = list(row.values())[0] if row else f"Row {idx}"
                        
                        # Generate QR code
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
                                            f"Row {idx}: {qr_data}",
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
                    
                    status_text.value = f"Generated {len(rows)} QR code(s)"
                    status_text.color = ft.Colors.GREEN
                    qr_output.update()
                    
                except Exception as ex:
                    status_text.value = f"Error: {str(ex)}"
                    status_text.color = ft.Colors.RED
                
                status_text.update()
        
        def download_qr(qr_data: str, img_base64: str):
            """Handle QR code download."""
            self.show_snackbar(f"QR code for '{qr_data}' ready", ft.Colors.GREEN)
            # Note: Download functionality would require backend implementation
        
        def pick_csv_file(e):
            """Trigger file picker."""
            file_picker.pick_files(
                allowed_extensions=["csv"],
                dialog_title="Select CSV file"
            )
        
        # Add file picker to page overlay
        self.page.overlay.append(file_picker)
        file_picker.on_result = handle_file_pick
        
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
