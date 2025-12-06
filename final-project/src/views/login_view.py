# views/login_view.py
"""Modern login view with enhanced UI/UX."""

import flet as ft
from views.base_view import BaseView
from config.constants import APP_TITLE, APP_TAGLINE, BLUE_600, DEFAULT_USERNAME, DEFAULT_PASSWORD, PRIMARY_COLOR
import os


class LoginView(BaseView):
    """Modern login screen view with smooth animations and contemporary design."""
    
    def build(self):
        """Build and return the modern login view."""
        
        # Input fields with modern styling
        username = ft.TextField(
            label="Username",
            width=360,
            height=56,
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            border_radius=12,
            filled=True,
            bgcolor=ft.Colors.GREY_50,
            border_color=ft.Colors.TRANSPARENT,
            focused_border_color=PRIMARY_COLOR,
            focused_bgcolor=ft.Colors.WHITE,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=16),
            text_size=15,
        )
        
        password = ft.TextField(
            label="Password",
            width=360,
            height=56,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            border_radius=12,
            filled=True,
            bgcolor=ft.Colors.GREY_50,
            border_color=ft.Colors.TRANSPARENT,
            focused_border_color=PRIMARY_COLOR,
            focused_bgcolor=ft.Colors.WHITE,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=16),
            text_size=15,
        )
        
        # Animated error container
        error_container = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=16, color=ft.Colors.RED_400),
                    ft.Text(
                        "",
                        size=13,
                        color=ft.Colors.RED_600,
                        weight=ft.FontWeight.W_500,
                    ),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            visible=False,
            padding=12,
            border_radius=8,
            bgcolor=ft.Colors.RED_50,
            border=ft.border.all(1, ft.Colors.RED_200),
            animate_opacity=300,
            width=360,
        )
        
        # Collapsible default credentials info
        show_credentials = ft.Ref[ft.Container]()
        credentials_visible = [True]  # Using list to maintain state in closure
        
        def toggle_credentials(e):
            credentials_visible[0] = not credentials_visible[0]
            show_credentials.current.visible = credentials_visible[0]
            show_credentials.current.update()
            e.control.icon = ft.Icons.KEYBOARD_ARROW_UP if credentials_visible[0] else ft.Icons.KEYBOARD_ARROW_DOWN
            e.control.update()
        
        credentials_box = ft.Container(
            ref=show_credentials,
            content=ft.Column(
                [
                    ft.Text(
                        f"Username: {DEFAULT_USERNAME}",
                        size=12,
                        color=ft.Colors.GREY_600,
                    ),
                    ft.Text(
                        f"Password: {DEFAULT_PASSWORD}",
                        size=12,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(top=8, bottom=4),
            visible=True,
            animate_opacity=200,
        )
        
        def authenticate(e):
            """Handle login authentication with smooth feedback."""
            # Clear previous error with animation
            error_container.visible = False
            error_container.update()
            
            # Validate inputs
            if not username.value or not password.value:
                error_container.content.controls[1].value = "Please enter both username and password"
                error_container.visible = True
                error_container.update()
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
                self.show_snackbar(f"Welcome back, {display_name}! 🎉", ft.Colors.GREEN)
                self.page.go("/home")
            else:
                error_container.content.controls[1].value = "Invalid username or password"
                error_container.visible = True
                error_container.update()
                password.value = ""
                password.update()
        
        # Allow Enter key to submit
        username.on_submit = authenticate
        password.on_submit = authenticate
        
        # Get relative path for logo (fallback to assets folder)
        # Assumes the logo is in src/assets/MS_Logo_Blue.png relative to the script
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "MS_Logo_Blue.png")
        
        # Modern login card with shadow
        login_card = ft.Container(
            width=440,
            padding=ft.padding.all(40),
            border_radius=20,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=20,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
            content=ft.Column(
                [
                    # Logo and branding section
                    ft.Column(
                        [
                            ft.Container(
                                content=ft.Image(
                                    src=logo_path,
                                    width=80,
                                    height=80,
                                    fit=ft.ImageFit.CONTAIN,
                                    error_content=ft.Icon(
                                        ft.Icons.QR_CODE_SCANNER_ROUNDED,
                                        size=64,
                                        color=PRIMARY_COLOR
                                    )
                                ),
                                padding=12,
                                border_radius=16,
                                gradient=ft.LinearGradient(
                                    colors=[
                                        ft.Colors.with_opacity(0.1, PRIMARY_COLOR),
                                        ft.Colors.with_opacity(0.05, PRIMARY_COLOR),
                                    ],
                                    begin=ft.alignment.top_left,
                                    end=ft.alignment.bottom_right,
                                ),
                            ),
                            ft.Text(
                                "MaScan",
                                size=36,
                                weight=ft.FontWeight.BOLD,
                                color=BLUE_600,
                            ),
                            ft.Text(
                                "Attendance Management System",
                                size=14,
                                color=ft.Colors.GREY_600,
                                weight=ft.FontWeight.W_400,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),

                    ft.Container(height=32),

                    # Form fields
                    ft.Column(
                        [
                            username,
                            password,
                            error_container,
                            
                            ft.Container(height=8),
                            
                            # Modern gradient button
                            ft.Container(
                                content=ft.ElevatedButton(
                                    "LOGIN",
                                    width=360,
                                    height=56,
                                    on_click=authenticate,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                        bgcolor={
                                            ft.ControlState.DEFAULT: PRIMARY_COLOR,
                                            ft.ControlState.HOVERED: BLUE_600,
                                        },
                                        color=ft.Colors.WHITE,
                                        text_style=ft.TextStyle(
                                            size=16,
                                            weight=ft.FontWeight.W_600,
                                            letter_spacing=0.5,
                                        ),
                                        elevation=0,
                                        overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                    )
                                ),
                            ),
                        ],
                        spacing=16,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),

                    ft.Container(height=20),

                    # Collapsible default login info
                    ft.Column(
                        [
                            ft.TextButton(
                                content=ft.Row(
                                    [
                                        ft.Text(
                                            "Default Login Credentials",
                                            size=12,
                                            color=ft.Colors.GREY_500,
                                            weight=ft.FontWeight.W_500,
                                        ),
                                        ft.Icon(
                                            ft.Icons.KEYBOARD_ARROW_UP,
                                            size=16,
                                            color=ft.Colors.GREY_500,
                                        ),
                                    ],
                                    spacing=4,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                                on_click=toggle_credentials,
                                style=ft.ButtonStyle(
                                    overlay_color=ft.Colors.TRANSPARENT,
                                ),
                            ),
                            credentials_box,
                        ],
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),

                    ft.Container(height=12),
                    
                    # Tagline
                    ft.Text(
                        APP_TAGLINE,
                        size=12,
                        color=ft.Colors.GREY_400,
                        italic=True,
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.W_300,
                    ),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
        
        # Main view with modern gradient background
        return ft.View(
            "/",
            [
                ft.Container(
                    expand=True,
                    padding=24,
                    gradient=ft.LinearGradient(
                        colors=[
                            ft.Colors.BLUE_50,
                            ft.Colors.PURPLE_50,
                            ft.Colors.PINK_50,
                        ],
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                        rotation=0.785,  # 45 degrees in radians
                    ),
                    content=ft.Column(
                        [login_card],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
            ],
            bgcolor=ft.Colors.TRANSPARENT,
        )