# views/login_view.py
"""Login view for user authentication."""

import flet as ft
from views.base_view import BaseView
from config.constants import APP_TITLE, APP_TAGLINE, BLUE_600, DEFAULT_USERNAME, DEFAULT_PASSWORD, PRIMARY_COLOR


class LoginView(BaseView):
    """Login screen view."""
    
    def build(self):
        """Build and return the login view."""
        username = ft.TextField(
            label="Username",
            width=340,
            prefix_icon=ft.Icons.PERSON
        )
        password = ft.TextField(
            label="Password",
            width=340,
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
        
        # Main centered view with a blue gradient background and padded card
        return ft.View(
            "/",
            [
                ft.Container(
                    expand=True,
                    padding=24,
                    # Gradient background
                    gradient=ft.LinearGradient(
                        [ft.Colors.BLUE_900, ft.Colors.BLUE_600, ft.Colors.BLUE_400],
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                    ),
                    content=ft.Column(
                        [
                            ft.Container(
                                width=420,
                                padding=ft.padding.all(24),
                                border_radius=10,
                                border=ft.border.all(1, ft.Colors.BLUE_200),
                                bgcolor=ft.Colors.WHITE,
                                content=ft.Column(
                                    [
                                        ft.Column(
                                            [
                                                ft.Image(
                                                    src="C:\\Users\\Asus\\Documents\\QR-Attendance-Checker\\final-project\\src\\assets\\MS_Logo_Blue.png",
                                                    width=100,
                                                    height=100,
                                                    fit=ft.ImageFit.CONTAIN,
                                                    error_content=ft.Icon(
                                                        ft.Icons.QR_CODE_SCANNER,
                                                        size=64,
                                                        color=PRIMARY_COLOR
                                                    )
                                                ),
                                                ft.Text(
                                                    "MaScan",
                                                    size=32,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=BLUE_600
                                                ),
                                                ft.Text(
                                                    "Attendance Management System",
                                                    size=14,
                                                    color=ft.Colors.GREY_700
                                                ),
                                            ],
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            spacing=4
                                        ),

                                        ft.Container(height=18),

                                        # Form fields
                                        ft.Column(
                                            [
                                                username,
                                                password,
                                                error_text,
                                                ft.Container(height=8),
                                                ft.ElevatedButton(
                                                    "LOGIN",
                                                    width=340,
                                                    height=48,
                                                    on_click=authenticate,
                                                    style=ft.ButtonStyle(
                                                        bgcolor=BLUE_600,
                                                        color=ft.Colors.WHITE,
                                                    )
                                                ),
                                            ],
                                            spacing=8,
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                        ),

                                        ft.Container(height=16),

                                        # Default login info box
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
                                                        size=12,
                                                        color=ft.Colors.GREY_600
                                                    ),
                                                    ft.Text(
                                                        f"Password: {DEFAULT_PASSWORD}",
                                                        size=12,
                                                        color=ft.Colors.GREY_600
                                                    ),
                                                ],
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                spacing=4
                                            ),
                                            padding=12,
                                            border=ft.border.all(1, ft.Colors.GREY_200),
                                            border_radius=8,
                                            bgcolor=ft.Colors.GREY_50,
                                            width=340
                                        ),

                                        ft.Container(height=12),
                                        ft.Text(
                                            APP_TAGLINE,
                                            size=12,
                                            color=ft.Colors.GREY_500,
                                            italic=True,
                                            text_align=ft.TextAlign.CENTER
                                        )
                                    ],
                                    spacing=12,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                )
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    )
                )
            ],
            # keep view background transparent since Container provides gradient
            bgcolor=ft.Colors.TRANSPARENT
        )