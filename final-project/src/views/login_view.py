# views/login_view.py
"""Login view for user authentication."""

import flet as ft
from views.base_view import BaseView
from config.constants import APP_TITLE, APP_TAGLINE, DEFAULT_USERNAME, DEFAULT_PASSWORD, PRIMARY_COLOR


class LoginView(BaseView):
    """Login screen view."""
    
    def build(self):
        """Build and return the login view."""
        username = ft.TextField(
            label="Username",
            width=300,
            prefix_icon=ft.Icons.PERSON
        )
        password = ft.TextField(
            label="Password",
            width=300,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK
        )
        
        error_text = ft.Text(
            "",
            color=ft.Colors.RED,
            size=12,
            visible=False
        )
        
        def authenticate(e):
            """Handle login authentication."""
            # Clear previous error
            error_text.visible = False
            error_text.update()
            
            # Validate inputs
            if not username.value or not password.value:
                error_text.value = "Please enter both username and password"
                error_text.visible = True
                error_text.update()
                return
            
            # Authenticate against database
            username_value = username.value.strip()
            user_authenticated = self.db.authenticate_user(username_value, password.value)
            
            if user_authenticated:
                # Get full name for display
                full_name = self.db._execute(
                    "SELECT full_name FROM users WHERE username = ?",
                    (username_value,),
                    fetch_one=True
                )
                display_name = full_name[0] if full_name else username_value
                
                self.app.current_user = username_value
                self.show_snackbar(f"Welcome, {display_name}!", ft.Colors.GREEN)
                self.page.go("/home")
            else:
                error_text.value = "Invalid username or password"
                error_text.visible = True
                error_text.update()
                password.value = ""
                password.update()
        
        # Allow Enter key to submit
        username.on_submit = authenticate
        password.on_submit = authenticate
        
        return ft.View(
            "/",
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Image(
                                src="C:\\Users\\Macmac\\Documents\\App Dev Final Project\\QR-Attendance-Checker\\final-project\\src\\assets\\mascan.png",
                                width=120,
                                height=120,
                                fit=ft.ImageFit.CONTAIN,
                                error_content=ft.Icon(
                                    ft.Icons.QR_CODE_SCANNER,
                                    size=80,
                                    color=PRIMARY_COLOR
                                )
                            ),
                            ft.Text(
                                "MaScan",
                                size=40,
                                weight=ft.FontWeight.BOLD,
                                color=PRIMARY_COLOR
                            ),
                            ft.Text(
                                "Attendance Management System",
                                size=16,
                                color=ft.Colors.GREY_700
                            ),
                            ft.Container(height=40),
                            username,
                            password,
                            error_text,
                            ft.Container(height=10),
                            ft.ElevatedButton(
                                "LOGIN",
                                width=300,
                                height=50,
                                on_click=authenticate,
                                style=ft.ButtonStyle(
                                    bgcolor=PRIMARY_COLOR,
                                    color=ft.Colors.WHITE,
                                )
                            ),
                            ft.Container(height=20),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            "Default Login:",
                                            size=12,
                                            color=ft.Colors.GREY_600,
                                            weight=ft.FontWeight.BOLD
                                        ),
                                        ft.Text(
                                            f"Username: {DEFAULT_USERNAME}",
                                            size=11,
                                            color=ft.Colors.GREY_500
                                        ),
                                        ft.Text(
                                            f"Password: {DEFAULT_PASSWORD}",
                                            size=11,
                                            color=ft.Colors.GREY_500
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2
                                ),
                                padding=10,
                                border=ft.border.all(1, ft.Colors.GREY_300),
                                border_radius=5,
                                bgcolor=ft.Colors.GREY_50
                            ),
                            ft.Container(height=10),
                            ft.Text(
                                APP_TAGLINE,
                                size=12,
                                color=ft.Colors.GREY_500,
                                italic=True
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10
                    ),
                    alignment=ft.alignment.center,
                    expand=True
                )
            ],
            bgcolor=ft.Colors.WHITE
        )