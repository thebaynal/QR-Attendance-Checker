# views/home_view.py
"""Home view displaying list of events."""

import flet as ft
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR


class HomeView(BaseView):
    """Home screen with event list."""
    
    def build(self):
        """Build and return the home view."""
        events = self.db.get_all_events()
        
        def delete_event_handler(event_id: str, event_name: str):
            """Handle event deletion with confirmation."""
            def confirm_delete(e):
                self.db.delete_event(event_id)
                self.show_snackbar(f"Event '{event_name}' deleted", ft.Colors.GREEN)
                self.page.close(dialog)
                self.page.go("/home")  # Refresh the view
            
            def cancel_delete(e):
                self.page.close(dialog)
            
            dialog = ft.AlertDialog(
                title=ft.Text("Delete Event"),
                content=ft.Text(
                    f"Are you sure you want to delete '{event_name}'? "
                    "This will also delete all attendance records."
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=cancel_delete),
                    ft.TextButton(
                        "Delete",
                        on_click=confirm_delete,
                        style=ft.ButtonStyle(color=ft.Colors.RED)
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.open(dialog)
        
        def create_event_card(event_id: str, event_data: dict):
            """Create a card for displaying an event."""
            return ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.EVENT, color=PRIMARY_COLOR),
                                title=ft.Text(
                                    event_data['name'],
                                    weight=ft.FontWeight.BOLD,
                                    size=16
                                ),
                                subtitle=ft.Text(event_data['date']),
                                trailing=ft.PopupMenuButton(
                                    items=[
                                        ft.PopupMenuItem(
                                            text="View Attendance",
                                            icon=ft.Icons.LIST,
                                            on_click=lambda e, eid=event_id: self.page.go(f"/event/{eid}")
                                        ),
                                        ft.PopupMenuItem(
                                            text="Start Scanning",
                                            icon=ft.Icons.QR_CODE_SCANNER,
                                            on_click=lambda e, eid=event_id: self.page.go(f"/scan/{eid}")
                                        ),
                                        ft.PopupMenuItem(),  # Divider
                                        ft.PopupMenuItem(
                                            text="Delete Event",
                                            icon=ft.Icons.DELETE,
                                            on_click=lambda e, eid=event_id, name=event_data['name']: 
                                                delete_event_handler(eid, name)
                                        ),
                                    ]
                                )
                            ),
                            ft.Container(
                                content=ft.Text(
                                    event_data['desc'],
                                    size=12,
                                    color=ft.Colors.GREY_700
                                ),
                                padding=ft.padding.only(left=16, right=16, bottom=10)
                            )
                        ]
                    ),
                    padding=0
                )
            )
        
        # Create event list or empty state
        event_list = ft.ListView(
            controls=[create_event_card(eid, data) for eid, data in events.items()],
            spacing=10,
            padding=20,
            expand=True
        ) if events else ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.EVENT_BUSY, size=80, color=ft.Colors.GREY_400),
                    ft.Text("No events yet", size=20, color=ft.Colors.GREY_600),
                    ft.Text("Create your first event", size=14, color=ft.Colors.GREY_500)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            alignment=ft.alignment.center,
            expand=True
        )
        
        return ft.View(
            "/home",
            [
                self.create_app_bar("MaScan"),
                event_list,
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    on_click=lambda e: self.page.go("/create_event"),
                    bgcolor=PRIMARY_COLOR,
                )
            ]
        )