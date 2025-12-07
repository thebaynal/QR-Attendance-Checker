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
from views.user_management_view import UserManagementView
from views.activity_log_view import ActivityLogView


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
        self.page.window.icon = "final-project\\src\\assets\\MS_Logo_Blue.png"
        
        # Initialize views
        self.login_view = LoginView(self)
        self.home_view = HomeView(self)
        self.event_view = EventView(self)
        self.scan_view = ScanView(self)
        self.create_event_view = CreateEventView(self)
        self.qr_generator_view = QRGeneratorView(self)
        self.user_management_view = UserManagementView(self)
        self.activity_log_view = ActivityLogView(self)
        
        # Setup routing
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop
        
        # Initialize
        self.page.go("/")

    def view_pop(self, e):
        """Handle back button."""
        if len(self.page.views) > 1:
            try:
                self.page.views.pop()
                top_view = self.page.views[-1]
                self.page.route = top_view.route
                self.page.update()
            except Exception as ex:
                print(f"ERROR in view_pop: {ex}")
                import traceback
                traceback.print_exc()

    def route_change(self, e):
        """Handle route changes safely and render fallback on errors."""
        print(f"DEBUG: Route change to {self.page.route}")

        # Stop camera when leaving scan view
        try:
            if self.qr_scanner and self.qr_scanner.is_running:
                self.qr_scanner.stop()
        except Exception:
            pass

        self.page.views.clear()
        route = self.page.route

        try:
            if route == "/":
                new_view = self.login_view.build()
            elif route == "/home":
                new_view = self.home_view.build() if self.current_user else self.login_view.build()
            elif route == "/create_event":
                new_view = self.create_event_view.build() if self.current_user else self.login_view.build()
            elif route.startswith("/event/"):
                event_id = route.split("/")[-1]
                new_view = self.event_view.build(event_id) if self.current_user else self.login_view.build()
            elif route.startswith("/scan/"):
                event_id = route.split("/")[-1]
                new_view = self.scan_view.build(event_id) if self.current_user else self.login_view.build()
            elif route == "/qr_generator":
                if not self.current_user:
                    new_view = self.login_view.build()
                else:
                    user_role = self.db.get_user_role(self.current_user)
                    if user_role != 'admin':
                        self.show_snackbar("Only admins can generate QR codes", ft.Colors.RED)
                        new_view = self.home_view.build() if self.current_user else self.login_view.build()
                    else:
                        new_view = self.qr_generator_view.build()
            elif route == "/user_management":
                if not self.current_user:
                    new_view = self.login_view.build()
                else:
                    user_role = self.db.get_user_role(self.current_user)
                    if user_role != 'admin':
                        self.show_snackbar("Only admins can access user management", ft.Colors.RED)
                        new_view = self.home_view.build() if self.current_user else self.login_view.build()
                    else:
                        new_view = self.user_management_view.build()
            elif route == "/activity_log":
                if not self.current_user:
                    new_view = self.login_view.build()
                else:
                    user_role = self.db.get_user_role(self.current_user)
                    if user_role != 'admin':
                        self.show_snackbar("Only admins can access activity log", ft.Colors.RED)
                        new_view = self.home_view.build() if self.current_user else self.login_view.build()
                    else:
                        new_view = self.activity_log_view.build()
            else:
                print(f"WARNING: Unknown route {route}, showing home view")
                new_view = self.home_view.build() if self.current_user else self.login_view.build()

            if new_view is not None:
                self.page.views.append(new_view)
                try:
                    self.page.route = new_view.route
                except Exception:
                    pass
                self.page.update()

        except Exception as e:
            print(f"ERROR in route_change while building view: {e}")
            import traceback
            traceback.print_exc()
            error_view = ft.View(
                route,
                [
                    self.create_app_bar("Error", show_back=True),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.ERROR, size=80, color=ft.Colors.RED),
                                ft.Text("An error occurred while loading the view.", size=16, color=ft.Colors.RED),
                                ft.Text(str(e), size=12, color=ft.Colors.GREY_600)
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10
                        ),
                        expand=True,
                        alignment=ft.alignment.center
                    )
                ]
            )
            self.page.views.append(error_view)
            try:
                self.page.update()
            except Exception:
                pass

    def show_snackbar(self, message: str, color: str = ft.Colors.BLUE):
        """Show snackbar message."""
        try:
            snackbar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
            self.page.snack_bar = snackbar
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as ex:
            print(f"ERROR showing snackbar: {ex}")
            import traceback
            traceback.print_exc()

    def create_app_bar(self, title: str, show_back: bool = False):
        """Create standardized app bar with modern design."""
        def open_drawer(e):
            self.open_end_drawer()
        
        return ft.AppBar(
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=ft.Colors.WHITE,
                on_click=lambda e: self.page.go("/home"),
                tooltip="Back to Home"
            ) if show_back else None,
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.QR_CODE_SCANNER, color=ft.Colors.WHITE, size=24),
                    ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ],
                spacing=8,
            ),
            actions=[
                ft.IconButton(
                    icon=ft.Icons.MENU,
                    icon_color=ft.Colors.WHITE,
                    on_click=open_drawer,
                    tooltip="Menu"
                )
            ] if self.current_user else [],
            bgcolor=PRIMARY_COLOR,
            center_title=False,
            toolbar_height=64,
        )

    def create_drawer(self):
        """Create modern navigation drawer with enhanced styling."""
        def on_home_click(e):
            self.navigate_home()
        
        def on_qr_click(e):
            self.navigate_qr_generator()
        
        def on_user_mgmt_click(e):
            self.navigate_user_management()
        
        def on_activity_log_click(e):
            self.navigate_activity_log()
        
        def on_logout_click(e):
            self.logout_handler()
        
        # User info header
        user_role = self.db.get_user_role(self.current_user) if self.current_user else None
        role_badge_color = ft.Colors.AMBER_600 if user_role == 'admin' else ft.Colors.BLUE_600
        
        menu_items = [
            # User Profile Section
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.ACCOUNT_CIRCLE,
                                size=60,
                                color=PRIMARY_COLOR
                            ),
                            alignment=ft.alignment.center,
                        ),
                        ft.Text(
                            self.current_user or 'User',
                            weight=ft.FontWeight.BOLD,
                            size=18,
                            color=ft.Colors.GREY_900,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(
                            content=ft.Text(
                                user_role.upper() if user_role else 'USER',
                                size=11,
                                weight=ft.FontWeight.W_600,
                                color=ft.Colors.WHITE,
                            ),
                            bgcolor=role_badge_color,
                            padding=ft.padding.symmetric(horizontal=12, vertical=4),
                            border_radius=12,
                            alignment=ft.alignment.center,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                padding=ft.padding.only(top=20, bottom=16, left=16, right=16),
                bgcolor=ft.Colors.BLUE_50,
                border_radius=ft.border_radius.only(top_left=16, top_right=16),
            ),
            
            ft.Container(height=12),
            
            # Navigation Items - Home (always visible)
            self._create_nav_item(
                icon=ft.Icons.HOME_ROUNDED,
                title="Home",
                on_click=on_home_click,
            ),
        ]
        
        # Add admin-only options
        print(f"DEBUG: current_user={self.current_user}, user_role={user_role}")
        
        if user_role == 'admin':
            print("DEBUG: Adding admin menu items")
            menu_items.extend([
                self._create_nav_item(
                    icon=ft.Icons.QR_CODE_2,
                    title="Generate QR Codes",
                    on_click=on_qr_click,
                    is_admin=True,
                ),
                self._create_nav_item(
                    icon=ft.Icons.ADMIN_PANEL_SETTINGS,
                    title="Manage Users",
                    on_click=on_user_mgmt_click,
                    is_admin=True,
                ),
                self._create_nav_item(
                    icon=ft.Icons.HISTORY,
                    title="Activity Log",
                    on_click=on_activity_log_click,
                    is_admin=True,
                ),
            ])
        else:
            print(f"DEBUG: NOT adding admin menu items (user_role={user_role})")
        
        # Divider and logout
        menu_items.extend([
            ft.Container(height=8),
            ft.Divider(height=1, color=ft.Colors.GREY_300),
            ft.Container(height=8),
            self._create_nav_item(
                icon=ft.Icons.LOGOUT,
                title="Logout",
                on_click=on_logout_click,
                is_logout=True,
            ),
        ])
        
        return ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    menu_items,
                    tight=False,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=0,
                ),
                padding=ft.padding.only(bottom=20, left=12, right=12),
                bgcolor=ft.Colors.WHITE,
                border_radius=ft.border_radius.only(top_left=16, top_right=16),
            ),
            open=False,
        )

    def _create_nav_item(self, icon, title, on_click, is_admin=False, is_logout=False):
        """Helper to create consistent navigation items."""
        if is_logout:
            icon_color = ft.Colors.RED_400
            text_color = ft.Colors.RED_600
            hover_color = ft.Colors.RED_50
        elif is_admin:
            icon_color = ft.Colors.AMBER_600
            text_color = ft.Colors.GREY_800
            hover_color = ft.Colors.AMBER_50
        else:
            icon_color = PRIMARY_COLOR
            text_color = ft.Colors.GREY_800
            hover_color = ft.Colors.BLUE_50
        
        return ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(icon, color=icon_color, size=24),
                title=ft.Text(
                    title,
                    size=15,
                    weight=ft.FontWeight.W_500,
                    color=text_color,
                ),
                on_click=on_click,
                hover_color=hover_color,
            ),
            padding=ft.padding.symmetric(horizontal=4),
            border_radius=12,
        )

    def open_end_drawer(self):
        """Open the navigation drawer."""
        try:
            if self.drawer and self.drawer in self.page.overlay:
                self.page.overlay.remove(self.drawer)
        except:
            pass
        
        self.drawer = self.create_drawer()
        self.page.overlay.append(self.drawer)
        self.drawer.open = True
        self.page.update()

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

    def navigate_user_management(self):
        """Navigate to user management and close drawer."""
        if self.drawer:
            try:
                self.drawer.open = False
                self.drawer.update()
            except:
                pass
        self.page.go("/user_management")

    def navigate_activity_log(self):
        """Navigate to activity log and close drawer."""
        if self.drawer:
            try:
                self.drawer.open = False
                self.drawer.update()
            except:
                pass
        self.page.go("/activity_log")

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
        # Record logout in activity log
        if self.current_user:
            self.db.record_logout(self.current_user)
        
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