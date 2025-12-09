# views/login_view.py
"""Premium login view with enhanced typography and shadows."""

import flet as ft
from views.base_view import BaseView
from config.constants import APP_TITLE, APP_TAGLINE, BLUE_600, DEFAULT_USERNAME, DEFAULT_PASSWORD, PRIMARY_COLOR
import os


class LoginView(BaseView):
    """Premium login screen with sophisticated styling."""
    
    def build(self):
        """Build and return the premium login view."""
        
        # Premium input fields
        username = ft.TextField(
            label="Username",
            width=360,
            height=56,
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            border_radius=14,
            filled=True,
            bgcolor=ft.Colors.GREY_50,
            border_color=ft.Colors.GREY_200,
            focused_border_color=PRIMARY_COLOR,
            focused_bgcolor=ft.Colors.WHITE,
            content_padding=ft.padding.symmetric(horizontal=18, vertical=16),
            text_size=15,
            label_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_500),
        )
        
        password = ft.TextField(
            label="Password",
            width=360,
            height=56,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            border_radius=14,
            filled=True,
            bgcolor=ft.Colors.GREY_50,
            border_color=ft.Colors.GREY_200,
            focused_border_color=PRIMARY_COLOR,
            focused_bgcolor=ft.Colors.WHITE,
            content_padding=ft.padding.symmetric(horizontal=18, vertical=16),
            text_size=15,
            label_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_500),
        )
        
        # Premium error container
        error_text = ft.Text(
            "",
            size=13,
            color=ft.Colors.RED_700,
            weight=ft.FontWeight.W_500,
            text_align=ft.TextAlign.CENTER,
            max_lines=2,
        )
        
        error_container = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=18, color=ft.Colors.RED_500),
                    ft.Container(
                        content=error_text,
                        expand=True,
                    ),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            visible=False,
            padding=14,
            border_radius=12,
            bgcolor=ft.Colors.RED_50,
            border=ft.border.all(1, ft.Colors.RED_200),
            animate_opacity=300,
            width=360,
        )
        
        # Collapsible credentials
        show_credentials = ft.Ref[ft.Container]()
        credentials_visible = [False]
        
        def toggle_credentials(e):
            credentials_visible[0] = not credentials_visible[0]
            show_credentials.current.visible = credentials_visible[0]
            show_credentials.current.update()
            e.control.content.controls[1].icon = ft.Icons.KEYBOARD_ARROW_UP if credentials_visible[0] else ft.Icons.KEYBOARD_ARROW_DOWN
            e.control.update()
        
        credentials_box = ft.Container(
            ref=show_credentials,
            content=ft.Column(
                [
                    ft.Text(
                        f"Username: {DEFAULT_USERNAME}",
                        size=12,
                        color=ft.Colors.GREY_600,
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Text(
                        f"Password: {DEFAULT_PASSWORD}",
                        size=12,
                        color=ft.Colors.GREY_600,
                        weight=ft.FontWeight.W_500,
                    ),
                ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(top=10, bottom=6),
            visible=False,
            animate_opacity=200,
        )
        
        def authenticate(e):
            """Handle login with premium feedback."""
            error_container.visible = False
            error_container.update()
            
            if not username.value or not password.value:
                error_text.value = "Please enter both username and password"
                error_container.visible = True
                error_container.update()
                return
            
            username_value = username.value.strip()
            user_authenticated = self.db.authenticate_user(username_value, password.value)
            
            if user_authenticated:
                full_name = self.db._execute(
                    "SELECT full_name FROM users WHERE username = ?",
                    (username_value,),
                    fetch_one=True
                )
                display_name = full_name[0] if full_name else username_value
                
                self.app.current_user = username_value
                self.show_snackbar(f"Welcome back, {display_name}! 🎉", ft.Colors.GREEN_600)
                self.page.go("/home")
            else:
                error_text.value = "Invalid username or password"
                error_container.visible = True
                error_container.update()
                password.value = ""
                password.update()
        
        username.on_submit = authenticate
        password.on_submit = authenticate
        
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "MS_Logo_Blue.png")
        
        # Premium login card with enhanced shadows
        login_card = ft.Container(
            width=440,
            padding=ft.padding.all(42),
            border_radius=22,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=28,
                color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
                offset=ft.Offset(0, 8),
            ),
            content=ft.Column(
                [
                    # Premium logo section
                    ft.Column(
                        [
                            ft.Container(
                                content=ft.Image(
                                    src=logo_path,
                                    width=85,
                                    height=85,
                                    fit=ft.ImageFit.CONTAIN,
                                    error_content=ft.Icon(
                                        ft.Icons.QR_CODE_SCANNER_ROUNDED,
                                        size=68,
                                        color=PRIMARY_COLOR
                                    )
                                ),
                                padding=14,
                                border_radius=18,
                                gradient=ft.LinearGradient(
                                    colors=[
                                        ft.Colors.with_opacity(0.12, PRIMARY_COLOR),
                                        ft.Colors.with_opacity(0.05, PRIMARY_COLOR),
                                    ],
                                    begin=ft.alignment.top_left,
                                    end=ft.alignment.bottom_right,
                                ),
                                shadow=ft.BoxShadow(
                                    spread_radius=0,
                                    blur_radius=16,
                                    color=ft.Colors.with_opacity(0.08, PRIMARY_COLOR),
                                    offset=ft.Offset(0, 4),
                                ),
                            ),
                            ft.Text(
                                "MaScan",
                                size=38,
                                weight=ft.FontWeight.BOLD,
                                color=BLUE_600,
                            ),
                            ft.Text(
                                "Attendance Management System",
                                size=15,
                                color=ft.Colors.GREY_600,
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),

                    ft.Container(height=36),

                    # Form fields
                    ft.Column(
                        [
                            username,
                            password,
                            error_container,
                            
                            ft.Container(height=10),
                            
                            # Premium gradient button
                            ft.Container(
                                content=ft.ElevatedButton(
                                    "LOGIN",
                                    width=360,
                                    height=56,
                                    on_click=authenticate,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=14),
                                        bgcolor={
                                            ft.ControlState.DEFAULT: PRIMARY_COLOR,
                                            ft.ControlState.HOVERED: BLUE_600,
                                        },
                                        color=ft.Colors.WHITE,
                                        text_style=ft.TextStyle(
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                            letter_spacing=0.8,
                                        ),
                                        elevation=3,
                                        shadow_color=ft.Colors.with_opacity(0.3, PRIMARY_COLOR),
                                        overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                    )
                                ),
                            ),
                        ],
                        spacing=18,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),

                    ft.Container(height=22),

                    # Collapsible credentials
                    ft.Column(
                        [
                            ft.TextButton(
                                content=ft.Row(
                                    [
                                        ft.Text(
                                            "Default Login Credentials",
                                            size=12,
                                            color=ft.Colors.GREY_500,
                                            weight=ft.FontWeight.W_600,
                                        ),
                                        ft.Icon(
                                            ft.Icons.KEYBOARD_ARROW_DOWN,
                                            size=18,
                                            color=ft.Colors.GREY_500,
                                        ),
                                    ],
                                    spacing=6,
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

                    ft.Container(height=14),
                    
                    # Premium tagline
                    ft.Text(
                        APP_TAGLINE,
                        size=12,
                        color=ft.Colors.GREY_400,
                        italic=True,
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.W_400,
                    ),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
        
        # Premium gradient background
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
                        rotation=0.785,
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