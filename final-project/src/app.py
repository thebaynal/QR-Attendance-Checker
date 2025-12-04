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
        self.user_management_view = UserManagementView(self)
        
        # Setup routing
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop
        
        # Initialize
        self.page.go("/")

    def view_pop(self, e):
        """Handle back button."""
        if len(self.page.views) > 1:
            # Remove the top view and restore the previous view in-place
            try:
                self.page.views.pop()
                top_view = self.page.views[-1]
                # Instead of calling page.go (which triggers route_change),
                # restore the previous view object and update the page.
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

        # Build the requested view and replace current views with it.
        # Avoid calling `page.go()` inside this method to prevent recursion.
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
                new_view = self.qr_generator_view.build() if self.current_user else self.login_view.build()
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
            else:
                print(f"WARNING: Unknown route {route}, showing home view")
                new_view = self.home_view.build() if self.current_user else self.login_view.build()

            # Append the constructed view and update page
            if new_view is not None:
                self.page.views.append(new_view)
                # Ensure the page.route matches the view's route
                try:
                    self.page.route = new_view.route
                except Exception:
                    pass
                self.page.update()

        except Exception as e:
            print(f"ERROR in route_change while building view: {e}")
            import traceback
            traceback.print_exc()
            # Render an error view instead of recursively navigating
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
            # Use page.snack_bar pattern and open it, then update the page
            self.page.snack_bar = snackbar
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as ex:
            # Fallback to printing if snackbar cannot be shown
            print(f"ERROR showing snackbar: {ex}")
            import traceback
            traceback.print_exc()

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
        # Build menu items dynamically based on user role
        def on_home_click(e):
            self.navigate_home()
        
        def on_qr_click(e):
            self.navigate_qr_generator()
        
        def on_user_mgmt_click(e):
            self.navigate_user_management()
        
        def on_logout_click(e):
            self.logout_handler()
        
        menu_items = [
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
                on_click=on_home_click
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.QR_CODE),
                title=ft.Text("Generate QR Codes"),
                on_click=on_qr_click
            ),
        ]
        
        # Add user management only for admin users
        user_role = self.db.get_user_role(self.current_user) if self.current_user else None
        print(f"DEBUG: current_user={self.current_user}, user_role={user_role}")
        
        if user_role == 'admin':
            print("DEBUG: Adding Manage Users menu item")
            menu_items.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS),
                    title=ft.Text("Manage Users"),
                    on_click=on_user_mgmt_click
                )
            )
        else:
            print(f"DEBUG: NOT adding Manage Users (user_role={user_role})")
        
        # Add logout at the end
        menu_items.append(
            ft.ListTile(
                leading=ft.Icon(ft.Icons.LOGOUT, color=ft.Colors.RED),
                title=ft.Text("Logout", color=ft.Colors.RED),
                on_click=on_logout_click
            )
        )
        
        return ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    menu_items,
                    tight=False,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
            ),
            open=False,
        )

    def open_end_drawer(self):
        """Open the navigation drawer."""
        try:
            # Remove old drawer if it exists
            if self.drawer and self.drawer in self.page.overlay:
                self.page.overlay.remove(self.drawer)
        except:
            pass
        
        # Create and add new drawer
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
