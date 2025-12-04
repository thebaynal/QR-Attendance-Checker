# app.py
"""Main application class for MaScan Attendance."""

import flet as ft
import time
from config.constants import *
from database.db_manager import Database
from views.login_view import LoginView
from views.home_view import HomeView
from views.event_view import EventView
from views.scan_view import ScanView
from views.create_event_view import CreateEventView
from views.qr_generator_view import QRGeneratorView


class MaScanApp:
    """Main application class for MaScan Attendance."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = Database(DATABASE_NAME)
        self.current_user = None
        self.drawer = None
        self.qr_scanner = None
        
        # Configure page
        self.page.title = APP_TITLE
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.window.width = WINDOW_WIDTH
        self.page.window.height = WINDOW_HEIGHT
        
        # Initialize views
        self.login_view = LoginView(self)
        self.home_view = HomeView(self)
        self.event_view = EventView(self)
        self.scan_view = ScanView(self)
        self.create_event_view = CreateEventView(self)
        self.qr_generator_view = QRGeneratorView(self)
        
        # Setup routing
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop
        
        # Initialize
        self.page.go("/")
    
    def route_change(self, e):
        """Handle route changes."""
        # Stop camera when leaving scan view
        if self.qr_scanner and self.qr_scanner.is_running:
            self.qr_scanner.stop()
        
        self.page.views.clear()
        route = self.page.route
        
        if route == "/":
            self.page.views.append(self.login_view.build())
        elif route == "/home":
            if not self.current_user:
                self.page.go("/")
                return
            self.page.views.append(self.home_view.build())
        elif route == "/create_event":
            if not self.current_user:
                self.page.go("/")
                return
            self.page.views.append(self.create_event_view.build())
        elif route.startswith("/event/"):
            if not self.current_user:
                self.page.go("/")
                return
            event_id = route.split("/")[-1]
            self.page.views.append(self.event_view.build(event_id))
        elif route.startswith("/scan/"):
            if not self.current_user:
                self.page.go("/")
                return
            event_id = route.split("/")[-1]
            self.page.views.append(self.scan_view.build(event_id))
        elif route == "/qr_generator":
            if not self.current_user:
                self.page.go("/")
                return
            self.page.views.append(self.qr_generator_view.build())
            
        self.page.update()
    
    def view_pop(self, e):
        """Handle back button."""
        if len(self.page.views) > 1:
            self.page.views.pop()
            top_view = self.page.views[-1]
            self.page.go(top_view.route)
    
    def show_snackbar(self, message: str, color: str = ft.Colors.BLUE):
        """Show snackbar message."""
        snackbar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        self.page.open(snackbar)
    
    def create_app_bar(self, title: str, show_back: bool = False):
        """Create standardized app bar."""
        def open_drawer(e):
            self.open_end_drawer()
        
        return ft.AppBar(
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda e: self.page.go("/home")
            ) if show_back else None,
            title=ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
            actions=[
                ft.IconButton(
                    icon=ft.Icons.MENU,
                    on_click=open_drawer
                )
            ] if self.current_user else [],
            bgcolor=PRIMARY_COLOR,
            color=ft.Colors.WHITE,
        )
    
    def create_drawer(self):
        """Create navigation drawer using BottomSheet."""
        return ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.PERSON, color=PRIMARY_COLOR),
                            title=ft.Text(
                                f"Welcome, {self.current_user or 'User'}!",
                                weight=ft.FontWeight.BOLD,
                                size=16
                            ),
                        ),
                        ft.Divider(height=1),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.HOME),
                            title=ft.Text("Home"),
                            on_click=lambda e: self.navigate_home()
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.QR_CODE),
                            title=ft.Text("Generate QR Codes"),
                            on_click=lambda e: self.navigate_qr_generator()
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.LOGOUT, color=ft.Colors.RED),
                            title=ft.Text("Logout", color=ft.Colors.RED),
                            on_click=lambda e: self.logout_handler()
                        ),
                    ],
                    tight=True,
                ),
                padding=20,
            ),
            open=False,
        )
    
    def open_end_drawer(self):
        """Open the navigation drawer."""
        if self.drawer is None:
            self.drawer = self.create_drawer()
            self.page.overlay.append(self.drawer)
            self.page.update()
        self.drawer.open = True
        self.drawer.update()
    
    def navigate_home(self):
        """Navigate to home and close drawer."""
        if self.drawer:
            try:
                self.drawer.open = False
                self.drawer.update()
            except:
                pass
        self.page.go("/home")
    
    def navigate_qr_generator(self):
        """Navigate to QR generator and close drawer."""
        if self.drawer:
            try:
                self.drawer.open = False
                self.drawer.update()
            except:
                pass
        self.page.go("/qr_generator")
    
    def logout_handler(self):
        """Handle logout and close drawer."""
        if self.drawer:
            try:
                self.drawer.open = False
                self.page.update()
            except:
                pass
        
        time.sleep(0.1)
        self.logout()
    
    def logout(self):
        """Handle logout."""
        # Stop camera if running
        if self.qr_scanner and self.qr_scanner.is_running:
            self.qr_scanner.stop()
        
        # Clear user and drawer
        self.current_user = None
        if self.drawer:
            try:
                if self.drawer in self.page.overlay:
                    self.page.overlay.remove(self.drawer)
            except:
                pass
        self.drawer = None
        
        # Navigate to login
        self.page.go("/")