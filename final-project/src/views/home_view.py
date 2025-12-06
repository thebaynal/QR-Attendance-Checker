# views/home_view.py
"""Modern home view displaying list of events."""

import flet as ft
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR


class HomeView(BaseView):
    """Home screen with modern event list."""

    def build(self):
        """Build and return the home view with modern design."""
        try:
            events = self.db.get_all_events()

            def delete_event_handler(event_id: str, event_name: str):
                """Handle event deletion with modern confirmation dialog."""
                def confirm_delete(e):
                    try:
                        self.db.delete_event(event_id)
                        self.show_snackbar(f"✓ Event '{event_name}' deleted", ft.Colors.GREEN)
                        self.page.close(dialog)
                        # Force a full refresh by rebuilding the view
                        self.page.views.clear()
                        self.page.views.append(self.build())
                        self.page.update()
                    except Exception as ex:
                        self.show_snackbar(f"Error deleting event: {str(ex)}", ft.Colors.RED)
                        self.page.close(dialog)

                def cancel_delete(e):
                    self.page.close(dialog)

                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Row(
                        [
                            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.RED_700, size=28),
                            ft.Text("Delete Event?", weight=ft.FontWeight.BOLD),
                        ],
                        spacing=8,
                    ),
                    content=ft.Text(
                        f"Are you sure you want to delete '{event_name}'?\n\n"
                        "This will permanently delete all attendance records for this event.",
                        size=14,
                    ),
                    actions=[
                        ft.TextButton(
                            "Cancel",
                            on_click=cancel_delete,
                        ),
                        ft.ElevatedButton(
                            "Delete",
                            on_click=confirm_delete,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.RED_700,
                                color=ft.Colors.WHITE,
                            ),
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                self.page.open(dialog)

            def create_event_card(event_id: str, event_data: dict):
                """Create a modern card for displaying an event."""
                # Default description if none exists
                description = event_data.get('desc', '').strip()
                if not description or description == "No description":
                    description = "📋 No additional details provided for this event"
                
                return ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.ListTile(
                                        leading=ft.Container(
                                            content=ft.Icon(
                                                ft.Icons.EVENT,
                                                color=ft.Colors.WHITE,
                                                size=28,
                                            ),
                                            width=56,
                                            height=56,
                                            bgcolor=PRIMARY_COLOR,
                                            border_radius=16,
                                            alignment=ft.alignment.center,
                                            shadow=ft.BoxShadow(
                                                spread_radius=0,
                                                blur_radius=8,
                                                color=ft.Colors.with_opacity(0.2, PRIMARY_COLOR),
                                                offset=ft.Offset(0, 2),
                                            ),
                                        ),
                                        title=ft.Text(
                                            event_data['name'],
                                            weight=ft.FontWeight.W_700,
                                            size=18,
                                            color=ft.Colors.GREY_900,
                                        ),
                                        subtitle=ft.Container(
                                            content=ft.Row(
                                                [
                                                    ft.Icon(
                                                        ft.Icons.CALENDAR_TODAY,
                                                        size=16,
                                                        color=ft.Colors.GREY_600,
                                                    ),
                                                    ft.Text(
                                                        event_data['date'],
                                                        size=14,
                                                        color=ft.Colors.GREY_600,
                                                        weight=ft.FontWeight.W_500,
                                                    ),
                                                ],
                                                spacing=6,
                                            ),
                                            padding=ft.padding.only(top=4),
                                        ),
                                        trailing=ft.PopupMenuButton(
                                            icon=ft.Icons.MORE_VERT,
                                            icon_color=ft.Colors.GREY_700,
                                            items=[
                                                ft.PopupMenuItem(
                                                    text="View Attendance",
                                                    icon=ft.Icons.PEOPLE_OUTLINE,
                                                    on_click=lambda e, eid=event_id: self.page.go(f"/event/{eid}")
                                                ),
                                                ft.PopupMenuItem(
                                                    text="Start Scanning",
                                                    icon=ft.Icons.QR_CODE_SCANNER,
                                                    on_click=lambda e, eid=event_id: self.page.go(f"/scan/{eid}")
                                                ),
                                                ft.PopupMenuItem(),
                                                ft.PopupMenuItem(
                                                    text="Delete Event",
                                                    icon=ft.Icons.DELETE_OUTLINE,
                                                    on_click=lambda e, eid=event_id, name=event_data['name']: 
                                                        delete_event_handler(eid, name)
                                                ),
                                            ]
                                        )
                                    ),
                                    # Event description with improved styling
                                    ft.Container(
                                        content=ft.Text(
                                            description,
                                            size=14,
                                            color=ft.Colors.GREY_600,
                                            max_lines=2,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                            italic=not event_data.get('desc') or event_data['desc'] == "No description",
                                        ),
                                        padding=ft.padding.only(left=72, right=16, bottom=16, top=0),
                                    ),
                                    # Action buttons row
                                    ft.Container(
                                        content=ft.Row(
                                            [
                                                ft.Container(
                                                    content=ft.TextButton(
                                                        content=ft.Row(
                                                            [
                                                                ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=18),
                                                                ft.Text("View", size=13, weight=ft.FontWeight.W_600),
                                                            ],
                                                            spacing=4,
                                                            tight=True,
                                                        ),
                                                        on_click=lambda e, eid=event_id: self.page.go(f"/event/{eid}"),
                                                        style=ft.ButtonStyle(
                                                            color=PRIMARY_COLOR,
                                                            overlay_color=ft.Colors.with_opacity(0.1, PRIMARY_COLOR),
                                                        ),
                                                    ),
                                                    expand=True,
                                                ),
                                                ft.Container(
                                                    content=ft.ElevatedButton(
                                                        content=ft.Row(
                                                            [
                                                                ft.Icon(ft.Icons.QR_CODE_SCANNER, size=18),
                                                                ft.Text("Scan", size=13, weight=ft.FontWeight.W_600),
                                                            ],
                                                            spacing=4,
                                                            tight=True,
                                                        ),
                                                        on_click=lambda e, eid=event_id: self.page.go(f"/scan/{eid}"),
                                                        style=ft.ButtonStyle(
                                                            bgcolor=PRIMARY_COLOR,
                                                            color=ft.Colors.WHITE,
                                                        ),
                                                    ),
                                                    expand=True,
                                                ),
                                            ],
                                            spacing=8,
                                        ),
                                        padding=ft.padding.only(left=16, right=16, bottom=12, top=0),
                                    ),
                                ],
                                spacing=8,
                            ),
                            padding=ft.padding.symmetric(vertical=8),
                        ),
                        elevation=2,
                        surface_tint_color=ft.Colors.WHITE,
                    ),
                )

            # Header with event count and add button
            header = ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    "My Events",
                                    size=28,
                                    weight=ft.FontWeight.W_800,
                                    color=ft.Colors.GREY_900,
                                ),
                                ft.Text(
                                    f"{len(events)} event{'s' if len(events) != 1 else ''} total",
                                    size=14,
                                    color=ft.Colors.GREY_600,
                                    weight=ft.FontWeight.W_500,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.ADD_ROUNDED, size=22),
                                    ft.Text("Add Event", size=15, weight=ft.FontWeight.W_600),
                                ],
                                spacing=6,
                                tight=True,
                            ),
                            on_click=lambda e: self.page.go("/create_event"),
                            style=ft.ButtonStyle(
                                bgcolor=PRIMARY_COLOR,
                                color=ft.Colors.WHITE,
                                padding=ft.padding.symmetric(horizontal=20, vertical=14),
                                shape=ft.RoundedRectangleBorder(radius=12),
                                elevation=2,
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=ft.padding.all(20),
                bgcolor=ft.Colors.WHITE,
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
            )

            # Create event list or empty state
            if events:
                event_list = ft.Container(
                    content=ft.ListView(
                        controls=[create_event_card(eid, data) for eid, data in events.items()],
                        spacing=16,
                        padding=20,
                    ),
                    expand=True,
                )
            else:
                event_list = ft.Container(
                    content=self.create_empty_state(
                        icon=ft.Icons.EVENT_BUSY_OUTLINED,
                        title="No Events Yet",
                        subtitle="Create your first event to get started with attendance tracking",
                    ),
                    expand=True,
                )

            return ft.View(
                "/home",
                [
                    self.create_app_bar("MaScan"),
                    header,
                    event_list,
                ],
                bgcolor=ft.Colors.GREY_50,
            )

        except Exception as ex:
            print(f"ERROR building HomeView: {ex}")
            import traceback
            traceback.print_exc()
            
            return ft.View(
                "/home",
                [
                    self.create_app_bar("Error", show_back=True),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.ERROR_OUTLINE, size=80, color=ft.Colors.RED_400),
                                ft.Text(
                                    "An error occurred",
                                    size=20,
                                    weight=ft.FontWeight.W_600,
                                    color=ft.Colors.RED_600,
                                ),
                                ft.Text(
                                    str(ex),
                                    size=13,
                                    color=ft.Colors.GREY_600,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=12,
                        ),
                        expand=True,
                        alignment=ft.alignment.center,
                    )
                ],
                bgcolor=ft.Colors.GREY_50,
            )