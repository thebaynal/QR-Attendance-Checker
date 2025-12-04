# views/event_view.py
"""View for displaying event details and attendance records."""

import flet as ft
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR


class EventView(BaseView):
    """Event detail with attendance log."""
    
    def build(self, event_id: str):
        """Build and return the event detail view.
        
        Args:
            event_id: ID of the event to display
        """
        event = self.db.get_event_by_id(event_id)
        if not event:
            # FIX: Must return a valid view, not None
            self.page.go("/home")
            # Return a dummy view while redirecting
            return ft.View(
                "/",
                [ft.Container()]
            )
        
        attendance = self.db.get_attendance_by_event(event_id)
        
        attendance_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Time", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(record['name'])),
                        ft.DataCell(ft.Text(user_id)),
                        ft.DataCell(ft.Text(record['time'])),
                        ft.DataCell(ft.Text(record['status'], color=ft.Colors.GREEN)),
                    ]
                ) for user_id, record in attendance.items()
            ] if attendance else [
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("No attendance records yet", italic=True)),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                ])
            ]
        )
        
        def export_data(e):
            """Export attendance data to CSV."""
            self.show_snackbar(f"Exporting {len(attendance)} records...", ft.Colors.BLUE)
            # TODO: Implement actual CSV export
        
        return ft.View(
            f"/event/{event_id}",
            [
                self.create_app_bar(event['name'], show_back=True),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                event['name'],
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=PRIMARY_COLOR
                            ),
                            ft.Text(event['date'], size=16, color=ft.Colors.GREY_700),
                            ft.Divider(),
                            ft.Text(
                                f"Total Attendees: {len(attendance)}",
                                size=18,
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [attendance_table],
                                    scroll=ft.ScrollMode.AUTO
                                ),
                                border=ft.border.all(1, ft.Colors.GREY_300),
                                border_radius=10,
                                padding=10,
                                expand=True
                            ),
                            ft.ElevatedButton(
                                "Export to CSV",
                                icon=ft.Icons.DOWNLOAD,
                                on_click=export_data,
                                style=ft.ButtonStyle(
                                    bgcolor=PRIMARY_COLOR,
                                    color=ft.Colors.WHITE
                                )
                            )
                        ],
                        spacing=15
                    ),
                    padding=20,
                    expand=True
                )
            ]
        )