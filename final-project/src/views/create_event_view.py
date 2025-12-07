# views/create_event_view.py
"""Modern view for creating new events."""

import flet as ft
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR
from datetime import datetime


class CreateEventView(BaseView):
    """Create new event screen with modern design."""
    
    def build(self):
        """Build and return the create event view."""
        # Store selected date
        selected_date = [None]
        
        # Form fields using modern styling - adjusted for 414px window
        name_field = self.create_modern_text_field(
            label="Event Name",
            hint_text="",
            prefix_icon=ft.Icons.EVENT_NOTE,
            width=330,
        )
        
        # Date display field (read-only) - clickable to open picker
        date_display = ft.TextField(
            label="Event Date",
            hint_text="Select Date",
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            suffix_icon=ft.Icons.ARROW_DROP_DOWN,
            width=330,
            height=56,
            border_radius=12,
            filled=True,
            read_only=True,
            bgcolor=ft.Colors.GREY_50,
            border_color=ft.Colors.TRANSPARENT,
            focused_border_color=PRIMARY_COLOR,
            focused_bgcolor=ft.Colors.WHITE,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=16),
            text_size=15,
        )
        
        desc_field = self.create_modern_text_field(
            label="Describe Event",
            hint_text="Add event details or notes...",
            multiline=True,
            width=330,
            
        )
        
        # Status message
        status_text = ft.Text(
            "",
            size=13,
            text_align=ft.TextAlign.CENTER,
            visible=False,
        )
        
        def handle_date_change(e):
            """Handle date selection from date picker."""
            if e.control.value:
                selected_date[0] = e.control.value
                # Format date as "Month Day, Year" (e.g., "December 15, 2024")
                formatted_date = e.control.value.strftime("%B %d, %Y")
                date_display.value = formatted_date
                date_display.update()
        
        def handle_date_dismiss(e):
            """Handle date picker dismissal."""
            pass
        
        # Date picker
        date_picker = ft.DatePicker(
            on_change=handle_date_change,
            on_dismiss=handle_date_dismiss,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
        )
        
        def open_date_picker(e):
            """Open the date picker dialog."""
            # Add date picker to page overlay if not already there
            if date_picker not in self.page.overlay:
                self.page.overlay.append(date_picker)
                self.page.update()
            date_picker.open = True
            date_picker.update()
        
        # Make date field clickable
        date_display.on_click = open_date_picker
        
        def save_event(e):
            """Save the new event to database."""
            # Clear previous status
            status_text.visible = False
            status_text.update()
            
            if not name_field.value or not name_field.value.strip():
                status_text.value = "Event name is required"
                status_text.color = ft.Colors.RED_600
                status_text.visible = True
                status_text.update()
                return
            
            if not date_display.value or not date_display.value.strip():
                status_text.value = "Please select an event date"
                status_text.color = ft.Colors.RED_600
                status_text.visible = True
                status_text.update()
                return
            
            try:
                self.db.create_event(
                    name_field.value.strip(),
                    date_display.value.strip(),
                    desc_field.value.strip() if desc_field.value else "No description"
                )
                self.show_snackbar(
                    f"✓ Event '{name_field.value.strip()}' created successfully!",
                    ft.Colors.GREEN
                )
                self.page.go("/home")
            except Exception as ex:
                status_text.value = f"Error creating event: {str(ex)}"
                status_text.color = ft.Colors.RED_600
                status_text.visible = True
                status_text.update()
        
        # Modern form card with fixed width
        form_card = ft.Container(
            content=self.create_modern_card(
                content=ft.Column(
                    [
                        # Header with icon
                        ft.Column(
                            [
                                ft.Icon(
                                    ft.Icons.ADD_CIRCLE_OUTLINE,
                                    size=56,
                                    color=PRIMARY_COLOR,
                                ),
                                self.create_section_title("Create New Event", size=24),
                                ft.Text(
                                    "Set up a new event for attendance tracking",
                                    size=14,
                                    color=ft.Colors.GREY_600,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        
                        ft.Container(height=24),
                        
                        # Form fields - all centered
                        ft.Column(
                            [
                                name_field,
                                date_display,
                                desc_field,
                            ],
                            spacing=16,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        
                        ft.Container(height=8),
                        status_text,
                        ft.Container(height=16),
                        
                        # Action buttons - full width to match fields
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.OutlinedButton(
                                        "Cancel",
                                        expand=1,
                                        height=50,
                                        on_click=lambda e: self.page.go("/home"),
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=12),
                                            side=ft.BorderSide(1, ft.Colors.GREY_400),
                                            text_style=ft.TextStyle(
                                                size=14,
                                                weight=ft.FontWeight.W_600,
                                            ),
                                        ),
                                    ),
                                    ft.Container(width=10),
                                    ft.Container(
                                        content=self.create_modern_button(
                                            text="Create Event",
                                            icon=ft.Icons.CHECK_CIRCLE,
                                            on_click=save_event,
                                            width=None,
                                        ),
                                        expand=1,
                                    ),
                                ],
                            ),
                            width=330,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                ),
                padding=40,
            ),
            width=520,
            alignment=ft.alignment.center,
        )
        
        return ft.View(
            "/create_event",
            [
                self.create_app_bar("Create Event", show_back=True),
                self.create_gradient_container(
                    content=ft.Column(
                        [form_card],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ),
            ],
            bgcolor=ft.Colors.TRANSPARENT,
        )