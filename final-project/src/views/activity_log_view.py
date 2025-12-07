# views/activity_log_view.py
"""Activity log view for tracking user actions."""

import flet as ft
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR


class ActivityLogView(BaseView):
    """View for displaying system activity logs."""
    
    def build(self):
        """Build and return the activity log view."""
        
        # Filter state
        filter_type = ["all"]  # all, login, scan
        
        # Activity list
        activity_list = ft.ListView(spacing=10, padding=14, expand=True)
        
        # Filter buttons
        all_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.LIST_ALT, size=20, color=ft.Colors.WHITE),
                    ft.Text("All", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            bgcolor=PRIMARY_COLOR,
            border_radius=10,
            padding=12,
            expand=True,
        )
        
        login_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.LOGIN, size=20, color=ft.Colors.GREY_600),
                    ft.Text("Logins", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            bgcolor=ft.Colors.GREY_200,
            border_radius=10,
            padding=12,
            expand=True,
        )
        
        scan_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.QR_CODE_SCANNER, size=20, color=ft.Colors.GREY_600),
                    ft.Text("Scans", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            bgcolor=ft.Colors.GREY_200,
            border_radius=10,
            padding=12,
            expand=True,
        )
        
        def load_activities(activity_filter="all"):
            """Load activities based on filter."""
            activity_list.controls.clear()
            
            try:
                # Get activities from database
                if activity_filter == "all":
                    query = "SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT 100"
                    activities = self.db._execute(query, fetch_all=True)
                elif activity_filter == "login":
                    query = "SELECT * FROM activity_log WHERE action_type = 'login' ORDER BY timestamp DESC LIMIT 100"
                    activities = self.db._execute(query, fetch_all=True)
                elif activity_filter == "scan":
                    query = "SELECT * FROM activity_log WHERE action_type = 'scan' ORDER BY timestamp DESC LIMIT 100"
                    activities = self.db._execute(query, fetch_all=True)
                else:
                    activities = []
                
                if not activities:
                    # Show empty state
                    activity_list.controls.append(
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Icon(
                                        ft.Icons.INBOX_OUTLINED,
                                        size=64,
                                        color=ft.Colors.GREY_400
                                    ),
                                    ft.Text(
                                        "No activity records found",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.GREY_600
                                    ),
                                    ft.Text(
                                        "Activity will appear here as users login and scan",
                                        size=13,
                                        color=ft.Colors.GREY_500,
                                        text_align=ft.TextAlign.CENTER
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=12
                            ),
                            padding=60,
                            alignment=ft.alignment.center,
                        )
                    )
                else:
                    # Display activities
                    for activity in activities:
                        # activity is a tuple: (id, action_type, username, details, timestamp)
                        activity_id = activity[0]
                        action_type = activity[1]
                        username = activity[2]
                        details = activity[3] if len(activity) > 3 else ""
                        timestamp = activity[4] if len(activity) > 4 else ""
                        
                        # Determine icon and color based on action type
                        if action_type == "login":
                            icon = ft.Icons.LOGIN
                            icon_color = ft.Colors.GREEN_600
                            title = f"{username} logged in"
                        elif action_type == "scan":
                            icon = ft.Icons.QR_CODE_SCANNER
                            icon_color = ft.Colors.BLUE_600
                            title = f"{username} scanned a student"
                        else:
                            icon = ft.Icons.CIRCLE
                            icon_color = ft.Colors.GREY_600
                            title = f"{username} - {action_type}"
                        
                        # Create activity card
                        activity_card = self.create_list_tile_card(
                            leading_icon=icon,
                            leading_color=icon_color,
                            title=title,
                            subtitle=f"{details}\n{timestamp}" if details else timestamp,
                        )
                        
                        activity_list.controls.append(activity_card)
                
                # Update the list
                activity_list.update()
                
            except Exception as e:
                print(f"Error loading activities: {e}")
                import traceback
                traceback.print_exc()
                
                # Show error state
                activity_list.controls.clear()
                activity_list.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(
                                    ft.Icons.ERROR_OUTLINE,
                                    size=64,
                                    color=ft.Colors.RED_400
                                ),
                                ft.Text(
                                    "Error loading activities",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.RED_600
                                ),
                                ft.Text(
                                    str(e),
                                    size=12,
                                    color=ft.Colors.GREY_600,
                                    text_align=ft.TextAlign.CENTER
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=12
                        ),
                        padding=60,
                        alignment=ft.alignment.center,
                    )
                )
                activity_list.update()
        
        def select_all(e):
            """Show all activities."""
            filter_type[0] = "all"
            all_btn.bgcolor = PRIMARY_COLOR
            all_btn.content.controls[0].color = ft.Colors.WHITE
            all_btn.content.controls[1].color = ft.Colors.WHITE
            login_btn.bgcolor = ft.Colors.GREY_200
            login_btn.content.controls[0].color = ft.Colors.GREY_600
            login_btn.content.controls[1].color = ft.Colors.GREY_600
            scan_btn.bgcolor = ft.Colors.GREY_200
            scan_btn.content.controls[0].color = ft.Colors.GREY_600
            scan_btn.content.controls[1].color = ft.Colors.GREY_600
            
            all_btn.update()
            login_btn.update()
            scan_btn.update()
            
            load_activities("all")
        
        def select_login(e):
            """Show only login activities."""
            filter_type[0] = "login"
            all_btn.bgcolor = ft.Colors.GREY_200
            all_btn.content.controls[0].color = ft.Colors.GREY_600
            all_btn.content.controls[1].color = ft.Colors.GREY_600
            login_btn.bgcolor = ft.Colors.GREEN_400
            login_btn.content.controls[0].color = ft.Colors.WHITE
            login_btn.content.controls[1].color = ft.Colors.WHITE
            scan_btn.bgcolor = ft.Colors.GREY_200
            scan_btn.content.controls[0].color = ft.Colors.GREY_600
            scan_btn.content.controls[1].color = ft.Colors.GREY_600
            
            all_btn.update()
            login_btn.update()
            scan_btn.update()
            
            load_activities("login")
        
        def select_scan(e):
            """Show only scan activities."""
            filter_type[0] = "scan"
            all_btn.bgcolor = ft.Colors.GREY_200
            all_btn.content.controls[0].color = ft.Colors.GREY_600
            all_btn.content.controls[1].color = ft.Colors.GREY_600
            login_btn.bgcolor = ft.Colors.GREY_200
            login_btn.content.controls[0].color = ft.Colors.GREY_600
            login_btn.content.controls[1].color = ft.Colors.GREY_600
            scan_btn.bgcolor = ft.Colors.BLUE_400
            scan_btn.content.controls[0].color = ft.Colors.WHITE
            scan_btn.content.controls[1].color = ft.Colors.WHITE
            
            all_btn.update()
            login_btn.update()
            scan_btn.update()
            
            load_activities("scan")
        
        all_btn.on_click = select_all
        login_btn.on_click = select_login
        scan_btn.on_click = select_scan
        
        # Load initial activities
        load_activities("all")
        
        # Build layout
        content = ft.Column(
            [
                # Header
                ft.Row(
                    [
                        ft.Icon(ft.Icons.HISTORY, size=28, color=PRIMARY_COLOR),
                        ft.Text(
                            "Activity Log",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=PRIMARY_COLOR,
                        ),
                    ],
                    spacing=12,
                ),
                
                ft.Container(height=16),
                
                # Filter buttons
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Filter by Type",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_700
                            ),
                            ft.Row(
                                [all_btn, login_btn, scan_btn],
                                spacing=10
                            ),
                        ],
                        spacing=10
                    ),
                    padding=16,
                    border_radius=16,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                ),
                
                ft.Container(height=20),
                
                # Activity list
                ft.Container(
                    content=activity_list,
                    padding=0,
                    border_radius=18,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=20,
                        color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                        offset=ft.Offset(0, 4),
                    ),
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        )
        
        return ft.View(
            "/activity_log",
            [
                self.create_app_bar("Activity Log", show_back=True),
                ft.Container(
                    content=content,
                    padding=24,
                    expand=True,
                    bgcolor=ft.Colors.GREY_50,
                )
            ],
            bgcolor=ft.Colors.GREY_50,
        )