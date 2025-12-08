# views/ui_utils.py
"""UI utilities for animations and styling."""

import flet as ft
from typing import Callable
import threading
import time


class AnimationUtils:
    """Helper class for creating smooth animations."""
    
    @staticmethod
    def fade_in_container(content, duration_ms=500):
        """Create a container that fades in."""
        container = ft.Container(
            content=content,
            opacity=0,
            animate_opacity=ft.animation.Animation(
                duration_ms=duration_ms,
                curve=ft.AnimationCurve.EASE_IN_OUT
            )
        )
        
        def do_fade():
            container.opacity = 1
            container.update()
        
        # Schedule fade in
        threading.Timer(0.1, do_fade).start()
        return container
    
    @staticmethod
    def slide_in_container(content, direction="up", duration_ms=400):
        """Create a container that slides in."""
        if direction == "up":
            offset = ft.transform.Offset(0, 1)
        elif direction == "down":
            offset = ft.transform.Offset(0, -1)
        elif direction == "left":
            offset = ft.transform.Offset(1, 0)
        else:  # right
            offset = ft.transform.Offset(-1, 0)
        
        container = ft.Container(
            content=content,
            offset=offset,
            animate_offset=ft.animation.Animation(
                duration_ms=duration_ms,
                curve=ft.AnimationCurve.EASE_OUT
            )
        )
        
        def do_slide():
            container.offset = ft.transform.Offset(0, 0)
            container.update()
        
        threading.Timer(0.1, do_slide).start()
        return container
    
    @staticmethod
    def scale_in_button(button, scale_start=0.8, duration_ms=300):
        """Create a button that scales in."""
        button.scale = scale_start
        button.animate_scale = ft.animation.Animation(
            duration_ms=duration_ms,
            curve=ft.AnimationCurve.EASE_OUT
        )
        
        def do_scale():
            button.scale = 1.0
            button.update()
        
        threading.Timer(0.1, do_scale).start()
        return button


class StyleUtils:
    """Utility class for consistent styling."""
    
    # Color palette
    COLORS = {
        "primary": "#2A73FF",
        "primary_dark": "#1A5FDD",
        "primary_light": "#E3F2FD",
        "success": "#4CAF50",
        "success_light": "#E8F5E9",
        "warning": "#FF9800",
        "warning_light": "#FFF3E0",
        "error": "#F44336",
        "error_light": "#FFEBEE",
        "info": "#2196F3",
        "info_light": "#E3F2FD",
        "dark": "#1F1F1F",
        "light": "#F5F5F5",
        "border": "#E0E0E0",
        "text_primary": "#212121",
        "text_secondary": "#757575",
    }
    
    @staticmethod
    def card(content, elevation=4, padding=20, border_radius=12):
        """Create a styled card."""
        return ft.Card(
            content=ft.Container(
                content=content,
                padding=padding,
                border_radius=border_radius
            ),
            elevation=elevation
        )
    
    @staticmethod
    def primary_button(text, on_click=None, icon=None, width=None, loading=False):
        """Create a primary button."""
        return ft.ElevatedButton(
            text=text,
            icon=icon,
            on_click=on_click,
            width=width or 280,
            height=48,
            style=ft.ButtonStyle(
                bgcolor=StyleUtils.COLORS["primary"],
                color=ft.Colors.WHITE,
                padding=ft.padding.symmetric(horizontal=24),
                shape=ft.RoundedRectangleBorder(radius=8),
            )
        )
    
    @staticmethod
    def secondary_button(text, on_click=None, icon=None, width=None):
        """Create a secondary button."""
        return ft.OutlinedButton(
            text=text,
            icon=icon,
            on_click=on_click,
            width=width or 280,
            height=48,
            style=ft.ButtonStyle(
                color=StyleUtils.COLORS["primary"],
                side=ft.BorderSide(color=StyleUtils.COLORS["primary"], width=2),
                padding=ft.padding.symmetric(horizontal=24),
                shape=ft.RoundedRectangleBorder(radius=8),
            )
        )
    
    @staticmethod
    def stat_card(value, label, icon=None, color=None):
        """Create a stat display card."""
        color = color or StyleUtils.COLORS["primary"]
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(icon, size=32, color=color) if icon else ft.Container(),
                            ft.Container(expand=True),
                        ]
                    ),
                    ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(label, size=14, color=StyleUtils.COLORS["text_secondary"]),
                ],
                spacing=8
            ),
            padding=20,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, StyleUtils.COLORS["border"]),
        )


class LoadingIndicator:
    """Custom loading indicator."""
    
    @staticmethod
    def pulse_dots():
        """Create animated pulse dots."""
        dots = []
        for i in range(3):
            dot = ft.Container(
                width=12,
                height=12,
                border_radius=6,
                bgcolor=StyleUtils.COLORS["primary"],
                opacity=0.3,
                animate_opacity=ft.animation.Animation(duration_ms=600)
            )
            dots.append(dot)
        
        def animate_dots():
            idx = [0]
            while True:
                for i, dot in enumerate(dots):
                    dot.opacity = 0.3 if i != idx[0] else 1.0
                    try:
                        dot.update()
                    except:
                        pass
                idx[0] = (idx[0] + 1) % len(dots)
                time.sleep(0.2)
        
        threading.Thread(target=animate_dots, daemon=True).start()
        
        return ft.Row(dots, spacing=8)