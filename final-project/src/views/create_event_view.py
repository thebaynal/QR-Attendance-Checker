# views/create_event_view.py
"""View for creating new events."""

import flet as ft
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR


class CreateEventView(BaseView):
    """Create new event screen."""
    
    def build(self):
        """Build and return the create event view."""
        name_field = ft.TextField(
            label="Event Name",
            hint_text="Enter event name",
            prefix_icon=ft.Icons.EVENT
        )
        date_field = ft.TextField(
            label="Date",
            hint_text="e.g., Dec 15, 2024",
            prefix_icon=ft.Icons.CALENDAR_TODAY
        )
        desc_field = ft.TextField(
            label="Description",
            hint_text="Optional description",
            multiline=True,
            min_lines=3,
            max_lines=5
        )
        
        def save_event(e):
            """Save the new event to database."""
            if name_field.value and date_field.value:
                self.db.create_event(
                    name_field.value,
                    date_field.value,
                    desc_field.value or "No description"
                )
                self.show_snackbar("Event created successfully!", ft.Colors.GREEN)
                self.page.go("/home")
            else:
                self.show_snackbar("Name and date are required", ft.Colors.RED)
        
        return ft.View(
            "/create_event",
            [
                self.create_app_bar("Create Event", show_back=True),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "New Event",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=PRIMARY_COLOR
                            ),
                            ft.Container(height=20),
                            name_field,
                            date_field,
                            desc_field,
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                "CREATE EVENT",
                                width=300,
                                height=50,
                                on_click=save_event,
                                style=ft.ButtonStyle(
                                    bgcolor=PRIMARY_COLOR,
                                    color=ft.Colors.WHITE
                                )
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=15
                    ),
                    padding=20,
                    expand=True
                )
            ]
        )