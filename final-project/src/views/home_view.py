# views/home_view.py
"""Home view displaying list of events."""

import flet as ft
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR


class HomeView(BaseView):
    """Home screen with event list."""

    def build(self):
        """Build and return the home view with robust error handling."""
        try:
            events = self.db.get_all_events()

            # Create a scrollable column to hold the event list
            event_list_column = ft.Column(
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )
            event_list_container = ft.Container(
                content=event_list_column,
                expand=True
            )

            def refresh_event_list():
                """Refresh the event list from the database."""
                events = self.db.get_all_events()
                
                def create_event_card(event_id: str, event_data: dict):
                    """Create a card for displaying an event."""
                    return ft.Card(
                        elevation=3,
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Container(
                                        content=ft.Row(
                                            [
                                                ft.Icon(ft.Icons.EVENT, color=PRIMARY_COLOR, size=28),
                                                ft.Column(
                                                    [
                                                        ft.Text(
                                                            event_data['name'],
                                                            weight=ft.FontWeight.BOLD,
                                                            size=16,
                                                            color=ft.Colors.BLACK87
                                                        ),
                                                        ft.Text(
                                                            event_data['date'],
                                                            size=13,
                                                            color=ft.Colors.GREY_600
                                                        ),
                                                    ],
                                                    spacing=3,
                                                    expand=True
                                                ),
                                                ft.PopupMenuButton(
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
                                            ],
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                            spacing=12
                                        ),
                                        padding=15
                                    ),
                                    ft.Divider(height=1),
                                    ft.Container(
                                        content=ft.Text(
                                            event_data['desc'] if event_data['desc'] else "No description",
                                            size=12,
                                            color=ft.Colors.GREY_700,
                                            max_lines=2,
                                            overflow=ft.TextOverflow.ELLIPSIS
                                        ),
                                        padding=ft.padding.symmetric(horizontal=15, vertical=10)
                                    )
                                ],
                                spacing=0
                            ),
                            padding=0
                        )
                    )
                
                # Create event list or empty state
                if events:
                    event_list_column.controls = [
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(
                                                "Events",
                                                size=18,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.BLACK87
                                            ),
                                            ft.Text(
                                                f"{len(events)} event{'s' if len(events) != 1 else ''}",
                                                size=13,
                                                color=ft.Colors.GREY_600
                                            )
                                        ],
                                        spacing=4
                                    ),
                                    ft.Container(expand=True),  # Spacer
                                    ft.ElevatedButton(
                                        "Add Event",
                                        icon=ft.Icons.ADD,
                                        on_click=lambda e: self.page.go("/create_event"),
                                        style=ft.ButtonStyle(
                                            bgcolor=PRIMARY_COLOR,
                                            color=ft.Colors.WHITE,
                                            padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                            shape=ft.RoundedRectangleBorder(radius=5)
                                        )
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=12
                            ),
                            padding=ft.padding.only(left=20, right=20, top=16, bottom=12)
                        ),
                        ft.ListView(
                            controls=[create_event_card(eid, data) for eid, data in events.items()],
                            spacing=12,
                            padding=ft.padding.symmetric(horizontal=20, vertical=0),
                            expand=True
                        )
                    ]
                else:
                    event_list_column.controls = [
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(
                                                "Events",
                                                size=18,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.BLACK87
                                            ),
                                            ft.Text(
                                                "0 events",
                                                size=13,
                                                color=ft.Colors.GREY_600
                                            )
                                        ],
                                        spacing=4
                                    ),
                                    ft.Container(expand=True),  # Spacer
                                    ft.ElevatedButton(
                                        "Add Event",
                                        icon=ft.Icons.ADD,
                                        on_click=lambda e: self.page.go("/create_event"),
                                        style=ft.ButtonStyle(
                                            bgcolor=PRIMARY_COLOR,
                                            color=ft.Colors.WHITE,
                                            padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                            shape=ft.RoundedRectangleBorder(radius=5)
                                        )
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=12
                            ),
                            padding=ft.padding.only(left=20, right=20, top=16, bottom=12)
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Icon(ft.Icons.EVENT_BUSY, size=80, color=ft.Colors.GREY_300),
                                    ft.Text("No events yet", size=22, color=ft.Colors.GREY_600, weight=ft.FontWeight.BOLD),
                                    ft.Text("Create your first event to get started", size=14, color=ft.Colors.GREY_500)
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=16
                            ),
                            alignment=ft.alignment.center,
                            expand=True
                        )
                    ]
                
                try:
                    event_list_column.update()
                except:
                    pass

            def delete_event_handler(event_id: str, event_name: str):
                """Handle event deletion with confirmation."""
                def confirm_delete(e):
                    self.db.delete_event(event_id)
                    self.show_snackbar(f"Event '{event_name}' deleted", ft.Colors.GREEN)
                    self.page.close(dialog)
                    # Refresh the event list immediately
                    refresh_event_list()

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

            # Initial population of event list
            refresh_event_list()

            return ft.View(
                "/home",
                [
                    ft.AppBar(
                        title=ft.Row(
                            [
                                ft.Image(
                                    src="C:\\Users\\Asus\\Documents\\QR-Attendance-Checker\\final-project\\src\\assets\\MS_Logo_White.png",
                                    width=32,
                                    height=32
                                ),
                                ft.Text("MaScan", size=20, weight=ft.FontWeight.BOLD)
                            ],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        actions=[
                            ft.IconButton(
                                icon=ft.Icons.MENU,
                                on_click=lambda e: self.app.open_end_drawer()
                            )
                        ] if self.app.current_user else [],
                        bgcolor=PRIMARY_COLOR,
                        color=ft.Colors.WHITE,
                    ),
                    event_list_container,
                ]
            )

        except Exception as ex:
            print(f"ERROR building HomeView: {ex}")
            import traceback
            traceback.print_exc()
            # Return a safe error view to avoid blank/black screens
            return ft.View(
                "/home",
                [
                    self.create_app_bar("Error", show_back=True),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.ERROR, size=80, color=ft.Colors.RED),
                                ft.Text("An error occurred while loading Home.", size=16, color=ft.Colors.RED),
                                ft.Text(str(ex), size=12, color=ft.Colors.GREY_600)
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10
                        ),
                        expand=True,
                        alignment=ft.alignment.center
                    )
                ]
            )