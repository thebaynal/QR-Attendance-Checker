# views/home_view.py
"""Modern home view with sorting and enhanced visual design."""

import flet as ft
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR
from datetime import datetime


class HomeView(BaseView):
    """Home screen with sorting, filters, and polished design."""

    def build(self, sort_option="date_desc", filter_option="all"):
        """Build and return the enhanced home view."""
        try:
            events = self.db.get_all_events()

            def parse_event_date(event_date_str: str):
                """Parse event date string handling multiple formats."""
                try:
                    # Try full month format first: "November 24, 2025"
                    return datetime.strptime(event_date_str, "%B %d, %Y").date()
                except:
                    try:
                        # Try abbreviated month with period: "Nov. 24, 2025"
                        return datetime.strptime(event_date_str, "%b. %d, %Y").date()
                    except:
                        try:
                            # Try abbreviated month without period: "Nov 24, 2025"
                            return datetime.strptime(event_date_str, "%b %d, %Y").date()
                        except:
                            return None

            def is_event_upcoming(event_date_str: str) -> bool:
                """Check if event date is in the future."""
                event_date = parse_event_date(event_date_str)
                if event_date is None:
                    return False
                today = datetime.now().date()
                return event_date > today

            def is_event_today(event_date_str: str) -> bool:
                """Check if event is today."""
                event_date = parse_event_date(event_date_str)
                if event_date is None:
                    return False
                today = datetime.now().date()
                return event_date == today

            def sort_events(events_dict: dict) -> list:
                """Sort events based on current sort option."""
                events_list = [(eid, data) for eid, data in events_dict.items()]
                
                if sort_option == "date_desc":
                    # Newest first
                    events_list.sort(
                        key=lambda x: parse_event_date(x[1]['date']) or datetime.min.date(),
                        reverse=True
                    )
                elif sort_option == "date_asc":
                    # Oldest first
                    events_list.sort(
                        key=lambda x: parse_event_date(x[1]['date']) or datetime.min.date()
                    )
                elif sort_option == "name_asc":
                    # A-Z
                    events_list.sort(key=lambda x: x[1]['name'].lower())
                elif sort_option == "name_desc":
                    # Z-A
                    events_list.sort(key=lambda x: x[1]['name'].lower(), reverse=True)
                
                return events_list

            def filter_events(events_list: list) -> list:
                """Filter events based on current filter option."""
                if filter_option == "upcoming":
                    return [(eid, data) for eid, data in events_list if is_event_upcoming(data['date'])]
                elif filter_option == "past":
                    return [(eid, data) for eid, data in events_list if not is_event_upcoming(data['date']) and not is_event_today(data['date'])]
                elif filter_option == "today":
                    return [(eid, data) for eid, data in events_list if is_event_today(data['date'])]
                return events_list

            def handle_sort_change(e):
                """Handle sort option change."""
                refresh_view(e.control.value, filter_option)

            def handle_filter_change(e):
                """Handle filter option change."""
                refresh_view(sort_option, e.control.value)

            def refresh_view(new_sort=None, new_filter=None):
                """Refresh the view with new sort/filter settings."""
                self.page.views.clear()
                self.page.views.append(self.build(
                    sort_option=new_sort or sort_option,
                    filter_option=new_filter or filter_option
                ))
                self.page.update()

            def handle_scan_click(event_id: str, event_date: str, event_name: str):
                """Handle scan button click with upcoming event check."""
                if is_event_upcoming(event_date):
                    dialog = ft.AlertDialog(
                        modal=True,
                        title=ft.Row(
                            [
                                ft.Icon(ft.Icons.SCHEDULE, color=ft.Colors.ORANGE_700, size=28),
                                ft.Text("Event Not Started", weight=ft.FontWeight.BOLD, size=18),
                            ],
                            spacing=10,
                        ),
                        content=ft.Container(
                            content=ft.Text(
                                f"The event '{event_name}' is scheduled for {event_date}.\n\n"
                                "Attendance scanning is only available on or after the event date.",
                                size=15,
                                color=ft.Colors.GREY_700,
                            ),
                            padding=ft.padding.only(top=10),
                        ),
                        actions=[
                            ft.TextButton(
                                "Got it",
                                on_click=lambda e: self.page.close(dialog),
                                style=ft.ButtonStyle(
                                    color=PRIMARY_COLOR,
                                ),
                            ),
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    self.page.open(dialog)
                else:
                    self.page.go(f"/scan/{event_id}")

            def delete_event_handler(event_id: str, event_name: str):
                """Handle event deletion with confirmation dialog."""
                def confirm_delete(e):
                    try:
                        self.db.delete_event(event_id)
                        self.show_snackbar(f"✓ Event '{event_name}' deleted successfully", ft.Colors.GREEN_600)
                        self.page.close(dialog)
                        refresh_view()
                    except Exception as ex:
                        self.show_snackbar(f"✗ Error deleting event: {str(ex)}", ft.Colors.RED_600)
                        self.page.close(dialog)

                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Row(
                        [
                            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.RED_600, size=28),
                            ft.Text("Delete Event?", weight=ft.FontWeight.BOLD, size=18),
                        ],
                        spacing=10,
                    ),
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    f"Are you sure you want to delete:",
                                    size=15,
                                    color=ft.Colors.GREY_700,
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        event_name,
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.GREY_900,
                                    ),
                                    padding=ft.padding.symmetric(vertical=8, horizontal=12),
                                    bgcolor=ft.Colors.GREY_100,
                                    border_radius=8,
                                ),
                                ft.Text(
                                    "⚠️ This will permanently delete all attendance records for this event.",
                                    size=13,
                                    color=ft.Colors.RED_700,
                                    italic=True,
                                ),
                            ],
                            spacing=12,
                            tight=True,
                        ),
                        padding=ft.padding.only(top=10),
                    ),
                    actions=[
                        ft.TextButton(
                            "Cancel",
                            on_click=lambda e: self.page.close(dialog),
                        ),
                        ft.ElevatedButton(
                            "Delete",
                            on_click=confirm_delete,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.RED_600,
                                color=ft.Colors.WHITE,
                            ),
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                self.page.open(dialog)

            def create_event_card(event_id: str, event_data: dict):
                """Create an enhanced card for displaying an event."""
                description = event_data.get('desc', '').strip()
                if not description or description == "No description":
                    description = "No additional details provided"
                
                is_upcoming = is_event_upcoming(event_data['date'])
                is_today = is_event_today(event_data['date'])
                
                # Determine card styling based on event status
                if is_today:
                    card_color = ft.Colors.BLUE_50
                    icon_color = ft.Colors.BLUE_600
                    icon_bg = ft.Colors.BLUE_600
                    badge_text = "TODAY"
                    badge_color = ft.Colors.BLUE_600
                    scan_button_color = ft.Colors.BLUE_600
                    scan_button_text = "Scan Now"
                elif is_upcoming:
                    card_color = ft.Colors.ORANGE_50
                    icon_color = ft.Colors.ORANGE_600
                    icon_bg = ft.Colors.ORANGE_400
                    badge_text = "UPCOMING"
                    badge_color = ft.Colors.ORANGE_500
                    scan_button_color = ft.Colors.GREY_300
                    scan_button_text = "Scan QR"
                else:
                    card_color = ft.Colors.WHITE
                    icon_color = ft.Colors.GREEN_600
                    icon_bg = PRIMARY_COLOR
                    badge_text = None
                    badge_color = None
                    scan_button_color = ft.Colors.RED_400
                    scan_button_text = "Past Event"
                
                return ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    # Event header
                                    ft.Container(
                                        content=ft.Row(
                                            [
                                                # Event icon
                                                ft.Container(
                                                    content=ft.Icon(
                                                        ft.Icons.EVENT_ROUNDED,
                                                        color=ft.Colors.WHITE,
                                                        size=30,
                                                    ),
                                                    width=60,
                                                    height=60,
                                                    bgcolor=icon_bg,
                                                    border_radius=16,
                                                    alignment=ft.alignment.center,
                                                    shadow=ft.BoxShadow(
                                                        spread_radius=0,
                                                        blur_radius=12,
                                                        color=ft.Colors.with_opacity(0.25, icon_bg),
                                                        offset=ft.Offset(0, 4),
                                                    ),
                                                ),
                                                # Event details - with proper wrapping
                                                ft.Container(
                                                    content=ft.Column(
                                                        [
                                                            # Event name with badge
                                                            ft.Row(
                                                                [
                                                                    ft.Container(
                                                                        content=ft.Text(
                                                                            event_data['name'],
                                                                            weight=ft.FontWeight.BOLD,
                                                                            size=17,
                                                                            color=ft.Colors.GREY_900,
                                                                            max_lines=2,
                                                                            overflow=ft.TextOverflow.ELLIPSIS,
                                                                        ),
                                                                        expand=True,
                                                                    ),
                                                                    ft.Container(
                                                                        content=ft.Text(
                                                                            badge_text,
                                                                            size=9,
                                                                            weight=ft.FontWeight.BOLD,
                                                                            color=ft.Colors.WHITE,
                                                                        ),
                                                                        bgcolor=badge_color,
                                                                        padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                                                        border_radius=10,
                                                                        visible=badge_text is not None,
                                                                    ),
                                                                ],
                                                                spacing=8,
                                                                alignment=ft.MainAxisAlignment.START,
                                                                vertical_alignment=ft.CrossAxisAlignment.START,
                                                            ),
                                                            # Date
                                                            ft.Row(
                                                                [
                                                                    ft.Icon(
                                                                        ft.Icons.CALENDAR_TODAY_ROUNDED,
                                                                        size=15,
                                                                        color=ft.Colors.GREY_600,
                                                                    ),
                                                                    ft.Text(
                                                                        event_data['date'],
                                                                        size=13,
                                                                        color=ft.Colors.GREY_600,
                                                                        weight=ft.FontWeight.W_500,
                                                                    ),
                                                                ],
                                                                spacing=6,
                                                            ),
                                                        ],
                                                        spacing=6,
                                                        tight=True,
                                                    ),
                                                    expand=True,
                                                ),
                                                # Menu button - fixed position
                                                ft.Container(
                                                    content=ft.PopupMenuButton(
                                                        icon=ft.Icons.MORE_VERT_ROUNDED,
                                                        icon_color=ft.Colors.GREY_700,
                                                        icon_size=22,
                                                        items=[
                                                            ft.PopupMenuItem(
                                                                text="View Attendance",
                                                                icon=ft.Icons.PEOPLE_OUTLINE_ROUNDED,
                                                                on_click=lambda e, eid=event_id: self.page.go(f"/event/{eid}")
                                                            ),
                                                            ft.PopupMenuItem(
                                                                text="Start Scanning",
                                                                icon=ft.Icons.QR_CODE_SCANNER_ROUNDED,
                                                                on_click=lambda e, eid=event_id, edate=event_data['date'], ename=event_data['name']: 
                                                                    handle_scan_click(eid, edate, ename)
                                                            ),
                                                            ft.PopupMenuItem(),
                                                            ft.PopupMenuItem(
                                                                text="Delete Event",
                                                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                                                on_click=lambda e, eid=event_id, name=event_data['name']: 
                                                                    delete_event_handler(eid, name)
                                                            ),
                                                        ]
                                                    ),
                                                    width=40,
                                                    alignment=ft.alignment.top_right,
                                                ),
                                            ],
                                            spacing=12,
                                            alignment=ft.MainAxisAlignment.START,
                                        ),
                                        padding=ft.padding.all(20),
                                    ),
                                    # Description with divider
                                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                                    ft.Container(
                                        content=ft.Row(
                                            [
                                                ft.Icon(
                                                    ft.Icons.DESCRIPTION_OUTLINED,
                                                    size=18,
                                                    color=ft.Colors.GREY_500,
                                                ),
                                                ft.Text(
                                                    description,
                                                    size=14,
                                                    color=ft.Colors.GREY_700,
                                                    max_lines=2,
                                                    overflow=ft.TextOverflow.ELLIPSIS,
                                                    italic=not event_data.get('desc') or event_data['desc'] == "No description",
                                                    expand=True,
                                                ),
                                            ],
                                            spacing=10,
                                        ),
                                        padding=ft.padding.symmetric(horizontal=20, vertical=14),
                                    ),
                                    # Action buttons
                                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                                    ft.Container(
                                        content=ft.Row(
                                            [
                                                ft.Container(
                                                    content=ft.TextButton(
                                                        content=ft.Row(
                                                            [
                                                                ft.Icon(ft.Icons.PEOPLE_OUTLINE_ROUNDED, size=20),
                                                                ft.Text("View Details", size=14, weight=ft.FontWeight.W_600),
                                                            ],
                                                            spacing=6,
                                                            tight=True,
                                                        ),
                                                        on_click=lambda e, eid=event_id: self.page.go(f"/event/{eid}"),
                                                        style=ft.ButtonStyle(
                                                            color=PRIMARY_COLOR,
                                                            overlay_color=ft.Colors.with_opacity(0.08, PRIMARY_COLOR),
                                                            padding=ft.padding.symmetric(horizontal=16, vertical=12),
                                                        ),
                                                    ),
                                                    expand=True,
                                                ),
                                                ft.Container(
                                                    width=1,
                                                    height=30,
                                                    bgcolor=ft.Colors.GREY_200,
                                                ),
                                                ft.Container(
                                                    content=ft.ElevatedButton(
                                                        content=ft.Row(
                                                            [
                                                                ft.Icon(ft.Icons.QR_CODE_SCANNER_ROUNDED, size=20),
                                                                ft.Text(scan_button_text, size=14, weight=ft.FontWeight.W_600),
                                                            ],
                                                            spacing=6,
                                                            tight=True,
                                                        ),
                                                        on_click=lambda e, eid=event_id, edate=event_data['date'], ename=event_data['name']: 
                                                            handle_scan_click(eid, edate, ename),
                                                        disabled=is_upcoming,
                                                        style=ft.ButtonStyle(
                                                            bgcolor=scan_button_color,
                                                            color=ft.Colors.WHITE,
                                                            elevation=0,
                                                            padding=ft.padding.symmetric(horizontal=16, vertical=12),
                                                            shape=ft.RoundedRectangleBorder(radius=8),
                                                        ),
                                                    ),
                                                    expand=True,
                                                ),
                                            ],
                                            spacing=0,
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        ),
                                        padding=ft.padding.symmetric(horizontal=12, vertical=10),
                                    ),
                                ],
                                spacing=0,
                            ),
                            bgcolor=card_color,
                            border_radius=16,
                        ),
                        elevation=3,
                        surface_tint_color=ft.Colors.TRANSPARENT,
                    ),
                    margin=ft.margin.only(bottom=16),
                )

            # Sort and filter events
            sorted_events = sort_events(events)
            filtered_events = filter_events(sorted_events)

            # Header with title and stats
            header = ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            "My Events",
                                            size=32,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.GREY_900,
                                        ),
                                        ft.Text(
                                            f"{len(filtered_events)} of {len(events)} event{'s' if len(events) != 1 else ''}",
                                            size=15,
                                            color=ft.Colors.GREY_600,
                                            weight=ft.FontWeight.W_500,
                                        ),
                                    ],
                                    spacing=4,
                                    expand=True,
                                ),
                                ft.ElevatedButton(
                                    content=ft.Row(
                                        [
                                            ft.Icon(ft.Icons.ADD_ROUNDED, size=22),
                                            ft.Text("New Event", size=15, weight=ft.FontWeight.BOLD),
                                        ],
                                        spacing=8,
                                        tight=True,
                                    ),
                                    on_click=lambda e: self.page.go("/create_event"),
                                    style=ft.ButtonStyle(
                                        bgcolor=PRIMARY_COLOR,
                                        color=ft.Colors.WHITE,
                                        padding=ft.padding.symmetric(horizontal=24, vertical=16),
                                        shape=ft.RoundedRectangleBorder(radius=14),
                                        elevation=3,
                                        shadow_color=ft.Colors.with_opacity(0.3, PRIMARY_COLOR),
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        # Sort and Filter controls
                        ft.Container(
                            content=ft.Row(
                                [
                                    # Sort dropdown
                                    ft.Container(
                                        content=ft.Row(
                                            [
                                                ft.Container(
                                                    content=ft.Icon(
                                                        ft.Icons.SWAP_VERT_ROUNDED, 
                                                        size=20, 
                                                        color=PRIMARY_COLOR
                                                    ),
                                                    padding=ft.padding.only(right=4),
                                                ),
                                                ft.Dropdown(
                                                    value=sort_option,
                                                    on_change=handle_sort_change,
                                                    options=[
                                                        ft.dropdown.Option("date_desc", "Newest First"),
                                                        ft.dropdown.Option("date_asc", "Oldest First"),
                                                        ft.dropdown.Option("name_asc", "A → Z"),
                                                        ft.dropdown.Option("name_desc", "Z → A"),
                                                    ],
                                                    text_size=14,
                                                    width=145,
                                                    border_color=ft.Colors.GREY_300,
                                                    focused_border_color=PRIMARY_COLOR,
                                                    content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
                                                ),
                                            ],
                                            spacing=0,
                                            alignment=ft.MainAxisAlignment.START,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                        expand=True,
                                    ),
                                    # Filter dropdown
                                    ft.Container(
                                        content=ft.Row(
                                            [
                                                ft.Container(
                                                    content=ft.Icon(
                                                        ft.Icons.FILTER_LIST_ROUNDED, 
                                                        size=20, 
                                                        color=PRIMARY_COLOR
                                                    ),
                                                    padding=ft.padding.only(right=4),
                                                ),
                                                ft.Dropdown(
                                                    value=filter_option,
                                                    on_change=handle_filter_change,
                                                    options=[
                                                        ft.dropdown.Option("all", "All Events"),
                                                        ft.dropdown.Option("today", "Today"),
                                                        ft.dropdown.Option("upcoming", "Upcoming"),
                                                        ft.dropdown.Option("past", "Past Events"),
                                                    ],
                                                    text_size=14,
                                                    width=145,
                                                    border_color=ft.Colors.GREY_300,
                                                    focused_border_color=PRIMARY_COLOR,
                                                    content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
                                                ),
                                            ],
                                            spacing=0,
                                            alignment=ft.MainAxisAlignment.START,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                        expand=True,
                                    ),
                                ],
                                spacing=16,
                            ),
                            padding=ft.padding.only(top=20),
                        ),
                    ],
                    spacing=0,
                ),
                padding=ft.padding.all(24),
                bgcolor=ft.Colors.WHITE,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=8,
                    color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2),
                ),
            )

            # Create event list or empty state
            if filtered_events:
                event_list = ft.Container(
                    content=ft.ListView(
                        controls=[create_event_card(eid, data) for eid, data in filtered_events],
                        spacing=0,
                        padding=ft.padding.all(24),
                    ),
                    expand=True,
                )
            else:
                empty_message = "No events match your filter" if events else "No events yet"
                empty_subtitle = "Try changing the filter" if events else "Create your first event to start tracking attendance"
                
                event_list = ft.Container(
                    content=self.create_empty_state(
                        icon=ft.Icons.EVENT_BUSY_OUTLINED,
                        title=empty_message,
                        subtitle=empty_subtitle,
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