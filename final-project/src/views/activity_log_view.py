# views/activity_log_view.py
"""View for admin to see recent login and scan activity."""

import flet as ft
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR, BLUE_50
from datetime import datetime


class ActivityLogView(BaseView):
    """Admin view to monitor login and scan activity."""
    
    def __init__(self, app):
        """Initialize the activity log view.
        
        Args:
            app: Reference to the main MaScanApp instance
        """
        super().__init__(app)
    
    def build(self):
        """Build and return the activity log view."""
        try:
            # Create tab view for logins and scans
            login_tab = self._build_login_tab()
            scan_tab = self._build_scan_tab()
            
            # Create tabs
            tabs = ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(
                        text="Recent Logins",
                        icon=ft.Icons.LOGIN,
                        content=login_tab
                    ),
                    ft.Tab(
                        text="Recent Scans",
                        icon=ft.Icons.QR_CODE_SCANNER,
                        content=scan_tab
                    ),
                ],
                expand=True
            )
            
            # Create the view
            view = ft.View(
                route="/activity_log",
                controls=[
                    self.create_app_bar("Activity Log", show_back=True),
                    ft.Container(
                        content=tabs,
                        expand=True,
                        padding=0
                    )
                ]
            )
            
            return view
        except Exception as e:
            print(f"Error building activity log view: {e}")
            import traceback
            traceback.print_exc()
            
            return ft.View(
                route="/activity_log",
                controls=[
                    self.create_app_bar("Activity Log", show_back=True),
                    ft.Container(
                        content=ft.Text(f"Error: {str(e)}", color=ft.Colors.RED),
                        expand=True,
                        alignment=ft.alignment.center
                    )
                ]
            )
    
    def _build_login_tab(self) -> ft.Control:
        """Build the login history tab."""
        try:
            # Get recent logins
            logins = self.db.get_recent_logins(limit=50)
            
            # Create login list
            login_list = ft.ListView(spacing=8, padding=10, expand=True)
            
            if not logins:
                login_list.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.INFO, size=60, color=ft.Colors.GREY_400),
                                ft.Text("No login history", color=ft.Colors.GREY_600)
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10
                        ),
                        expand=True,
                        alignment=ft.alignment.center
                    )
                )
            else:
                for login in logins:
                    login_card = self._create_login_card(login)
                    login_list.controls.append(login_card)
            
            return ft.Container(
                content=login_list,
                expand=True
            )
        except Exception as e:
            print(f"Error building login tab: {e}")
            return ft.Container(
                content=ft.Text(f"Error: {str(e)}", color=ft.Colors.RED),
                expand=True,
                alignment=ft.alignment.center
            )
    
    def _build_scan_tab(self) -> ft.Control:
        """Build the scan history tab."""
        try:
            # Get recent scans
            scans = self.db.get_recent_scans(limit=50)
            
            # Create scan list
            scan_list = ft.ListView(spacing=8, padding=10, expand=True)
            
            if not scans:
                scan_list.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.INFO, size=60, color=ft.Colors.GREY_400),
                                ft.Text("No scan history", color=ft.Colors.GREY_600)
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10
                        ),
                        expand=True,
                        alignment=ft.alignment.center
                    )
                )
            else:
                for scan in scans:
                    scan_card = self._create_scan_card(scan)
                    scan_list.controls.append(scan_card)
            
            return ft.Container(
                content=scan_list,
                expand=True
            )
        except Exception as e:
            print(f"Error building scan tab: {e}")
            return ft.Container(
                content=ft.Text(f"Error: {str(e)}", color=ft.Colors.RED),
                expand=True,
                alignment=ft.alignment.center
            )
    
    def _create_login_card(self, login: dict) -> ft.Card:
        """Create a card for a login entry."""
        login_time_str = self._format_datetime(login['login_time'])
        logout_time_str = self._format_datetime(login['logout_time']) if login['logout_time'] else "Still logged in"
        
        return ft.Card(
            elevation=2,
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.PERSON, color=PRIMARY_COLOR, size=24),
                                    ft.Column(
                                        [
                                            ft.Text(
                                                login['username'],
                                                weight=ft.FontWeight.BOLD,
                                                size=14,
                                                color=ft.Colors.BLACK87
                                            ),
                                            ft.Text(
                                                "Login Activity",
                                                size=11,
                                                color=ft.Colors.GREY_600
                                            ),
                                        ],
                                        spacing=2,
                                        expand=True
                                    ),
                                ],
                                spacing=12,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            padding=12
                        ),
                        ft.Divider(height=1),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text("Login Time:", size=11, color=ft.Colors.GREY_700, weight=ft.FontWeight.BOLD),
                                            ft.Text(login_time_str, size=11, color=ft.Colors.GREY_700),
                                        ],
                                        spacing=10
                                    ),
                                    ft.Row(
                                        [
                                            ft.Text("Logout Time:", size=11, color=ft.Colors.GREY_700, weight=ft.FontWeight.BOLD),
                                            ft.Text(
                                                logout_time_str,
                                                size=11,
                                                color=ft.Colors.ORANGE if logout_time_str == "Still logged in" else ft.Colors.GREY_700
                                            ),
                                        ],
                                        spacing=10
                                    ),
                                ],
                                spacing=6
                            ),
                            padding=ft.padding.symmetric(horizontal=12, vertical=8)
                        )
                    ],
                    spacing=0
                ),
                padding=0
            )
        )
    
    def _create_scan_card(self, scan: dict) -> ft.Card:
        """Create a card for a scan entry."""
        scan_time_str = self._format_datetime(scan['scan_time'])
        
        # Get event name if available
        event = self.db.get_event_by_id(scan['event_id'])
        event_name = event['name'] if event else f"Event {scan['event_id']}"
        
        return ft.Card(
            elevation=2,
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.QR_CODE_SCANNER, color=PRIMARY_COLOR, size=24),
                                    ft.Column(
                                        [
                                            ft.Text(
                                                f"{scan['scanner_username']} scanned",
                                                weight=ft.FontWeight.BOLD,
                                                size=14,
                                                color=ft.Colors.BLACK87
                                            ),
                                            ft.Text(
                                                "Scan Activity",
                                                size=11,
                                                color=ft.Colors.GREY_600
                                            ),
                                        ],
                                        spacing=2,
                                        expand=True
                                    ),
                                ],
                                spacing=12,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            padding=12
                        ),
                        ft.Divider(height=1),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text("Scanned User:", size=11, color=ft.Colors.GREY_700, weight=ft.FontWeight.BOLD),
                                            ft.Text(scan['scanned_user_name'], size=11, color=ft.Colors.GREY_700),
                                        ],
                                        spacing=10
                                    ),
                                    ft.Row(
                                        [
                                            ft.Text("User ID:", size=11, color=ft.Colors.GREY_700, weight=ft.FontWeight.BOLD),
                                            ft.Text(scan['scanned_user_id'], size=11, color=ft.Colors.GREY_700),
                                        ],
                                        spacing=10
                                    ),
                                    ft.Row(
                                        [
                                            ft.Text("Event:", size=11, color=ft.Colors.GREY_700, weight=ft.FontWeight.BOLD),
                                            ft.Text(event_name, size=11, color=ft.Colors.GREY_700, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                        ],
                                        spacing=10
                                    ),
                                    ft.Row(
                                        [
                                            ft.Text("Scan Time:", size=11, color=ft.Colors.GREY_700, weight=ft.FontWeight.BOLD),
                                            ft.Text(scan_time_str, size=11, color=ft.Colors.GREY_700),
                                        ],
                                        spacing=10
                                    ),
                                ],
                                spacing=6
                            ),
                            padding=ft.padding.symmetric(horizontal=12, vertical=8)
                        )
                    ],
                    spacing=0
                ),
                padding=0
            )
        )
    
    def _format_datetime(self, iso_string: str) -> str:
        """Format ISO datetime string to readable format."""
        if not iso_string:
            return "N/A"
        try:
            dt = datetime.fromisoformat(iso_string)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return iso_string
