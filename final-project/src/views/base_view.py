# views/base_view.py
"""Base class for all views with premium styling utilities."""

import flet as ft
from config.constants import PRIMARY_COLOR, BLUE_600


class BaseView:
    """Base class for all views providing common functionality and premium styling."""
    
    def __init__(self, app):
        """Initialize base view with app reference.
        
        Args:
            app: Reference to the main MaScanApp instance
        """
        self.app = app
        self.page = app.page
        self.db = app.db
    
    def build(self, *args, **kwargs):
        """Build and return the view. Must be implemented by subclasses.
        
        Returns:
            ft.View: The constructed Flet view
        """
        raise NotImplementedError("Subclasses must implement build()")
    
    def show_snackbar(self, message: str, color: str = ft.Colors.BLUE):
        """Show a snackbar message.
        
        Args:
            message: Message to display
            color: Background color of snackbar
        """
        self.app.show_snackbar(message, color)
    
    def create_app_bar(self, title: str, show_back: bool = False):
        """Create standardized app bar.
        
        Args:
            title: Title text for the app bar
            show_back: Whether to show back button
            
        Returns:
            ft.AppBar: The constructed app bar
        """
        return self.app.create_app_bar(title, show_back)
    
    # Premium UI Component Builders
    
    def create_modern_card(self, content, padding=20, expand=False):
        """Create a premium card with enhanced shadows and styling.
        
        Args:
            content: Content to display in card
            padding: Padding around content
            expand: Whether card should expand
            
        Returns:
            ft.Container: Styled card container
        """
        return ft.Container(
            content=content,
            padding=padding,
            border_radius=18,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
            expand=expand,
        )
    
    def create_modern_button(self, text, icon=None, on_click=None, width=None, 
                            height=50, is_primary=True, is_danger=False):
        """Create a premium styled button with shadows.
        
        Args:
            text: Button text
            icon: Optional icon
            on_click: Click handler
            width: Button width
            height: Button height
            is_primary: Use primary color scheme
            is_danger: Use danger/red color scheme
            
        Returns:
            ft.ElevatedButton: Styled button
        """
        if is_danger:
            bg_color = ft.Colors.RED_600
            hover_color = ft.Colors.RED_700
            shadow_color = ft.Colors.RED_600
        elif is_primary:
            bg_color = PRIMARY_COLOR
            hover_color = BLUE_600
            shadow_color = PRIMARY_COLOR
        else:
            bg_color = ft.Colors.GREY_200
            hover_color = ft.Colors.GREY_300
            shadow_color = ft.Colors.GREY_400
        
        return ft.ElevatedButton(
            text=text,
            icon=icon,
            width=width,
            height=height,
            on_click=on_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=14),
                bgcolor={
                    ft.ControlState.DEFAULT: bg_color,
                    ft.ControlState.HOVERED: hover_color,
                },
                color=ft.Colors.WHITE if (is_primary or is_danger) else ft.Colors.BLACK,
                text_style=ft.TextStyle(
                    size=15,
                    weight=ft.FontWeight.BOLD,
                    letter_spacing=0.3,
                ),
                elevation=3,
                shadow_color=ft.Colors.with_opacity(0.25, shadow_color),
                overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            )
        )
    
    def create_modern_text_field(self, label, hint_text="", prefix_icon=None, 
                                 password=False, multiline=False, width=400, height=56):
        """Create a premium styled text field.
        
        Args:
            label: Field label
            hint_text: Placeholder text
            prefix_icon: Optional icon
            password: Whether field is password
            multiline: Whether field is multiline
            width: Field width (default 400)
            height: Field height
            
        Returns:
            ft.TextField: Styled text field
        """
        return ft.TextField(
            label=label,
            hint_text=hint_text,
            prefix_icon=prefix_icon,
            password=password,
            can_reveal_password=password,
            multiline=multiline,
            min_lines=3 if multiline else 1,
            max_lines=5 if multiline else 1,
            width=width,
            height=None if multiline else height,
            border_radius=14,
            filled=True,
            bgcolor=ft.Colors.GREY_50,
            border_color=ft.Colors.GREY_200,
            focused_border_color=PRIMARY_COLOR,
            focused_bgcolor=ft.Colors.WHITE,
            content_padding=ft.padding.symmetric(horizontal=18, vertical=16),
            text_size=15,
            label_style=ft.TextStyle(
                size=14,
                weight=ft.FontWeight.W_500,
            ),
        )
    
    def create_section_title(self, text, size=20, icon=None):
        """Create a premium section title with optional icon.
        
        Args:
            text: Title text
            size: Font size
            icon: Optional icon
            
        Returns:
            ft.Row or ft.Text: Styled title
        """
        title = ft.Text(
            text,
            size=size,
            weight=ft.FontWeight.BOLD,
            color=PRIMARY_COLOR,
        )
        
        if icon:
            return ft.Row(
                [
                    ft.Icon(icon, color=PRIMARY_COLOR, size=size + 4),
                    title,
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        return title
    
    def create_info_badge(self, text, color=ft.Colors.BLUE):
        """Create a premium info badge with shadow.
        
        Args:
            text: Badge text
            color: Badge color
            
        Returns:
            ft.Container: Styled badge
        """
        return ft.Container(
            content=ft.Text(
                text,
                color=ft.Colors.WHITE,
                size=11,
                weight=ft.FontWeight.BOLD,
            ),
            bgcolor=color,
            padding=ft.padding.symmetric(horizontal=14, vertical=6),
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.3, color),
                offset=ft.Offset(0, 2),
            ),
        )
    
    def create_gradient_container(self, content, colors=None, padding=20):
        """Create container with premium gradient background.
        
        Args:
            content: Content to display
            colors: List of gradient colors
            padding: Container padding
            
        Returns:
            ft.Container: Container with gradient
        """
        if colors is None:
            colors = [
                ft.Colors.BLUE_50,
                ft.Colors.PURPLE_50,
                ft.Colors.PINK_50,
            ]
        
        return ft.Container(
            content=content,
            padding=padding,
            expand=True,
            gradient=ft.LinearGradient(
                colors=colors,
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                rotation=0.785,
            ),
        )
    
    def create_empty_state(self, icon, title, subtitle, icon_size=80):
        """Create a premium empty state display.
        
        Args:
            icon: Icon to display
            title: Main text
            subtitle: Secondary text
            icon_size: Size of icon
            
        Returns:
            ft.Container: Empty state container
        """
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=icon_size, color=ft.Colors.GREY_300),
                    ft.Text(
                        title,
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_600,
                    ),
                    ft.Text(
                        subtitle,
                        size=15,
                        color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.W_400,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
    
    def create_list_tile_card(self, leading_icon, title, subtitle, trailing=None, 
                              on_click=None, leading_color=None):
        """Create a premium list tile in a card.
        
        Args:
            leading_icon: Leading icon
            title: Title text
            subtitle: Subtitle text
            trailing: Trailing widget
            on_click: Click handler
            leading_color: Color for leading icon
            
        Returns:
            ft.Card: Styled card with list tile
        """
        return ft.Card(
            content=ft.Container(
                content=ft.ListTile(
                    leading=ft.Icon(
                        leading_icon,
                        color=leading_color or PRIMARY_COLOR,
                        size=28,
                    ),
                    title=ft.Text(
                        title,
                        weight=ft.FontWeight.BOLD,
                        size=16,
                    ),
                    subtitle=ft.Text(
                        subtitle, 
                        size=14,
                        color=ft.Colors.GREY_600,
                    ),
                    trailing=trailing,
                    on_click=on_click,
                ),
                padding=10,
            ),
            elevation=2,
            shadow_color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
        )