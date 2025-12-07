# views/create_event_view.py
"""Modern view for creating new events."""

import flet as ft
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR
from datetime import datetime, timedelta


class CreateEventView(BaseView):
    """Create new event screen with modern design."""
    
    def build(self):
        """Build and return the create event view."""
        # Store selected date
        selected_date = [None]
        
        # Form fields using modern styling - YOUR premium design
        name_field = self.create_modern_text_field(
            label="Event Name",
            hint_text="",
            prefix_icon=ft.Icons.EVENT_NOTE,
            width=330,
        )
        
        # Date display field (read-only) - clickable to open picker - YOUR design
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
        
        # Status message - YOUR styling
        status_text = ft.Text(
            "",
            size=13,
            text_align=ft.TextAlign.CENTER,
            visible=False,
        )
        
        # THEIR calendar picker logic (new feature from upstream)
        def open_calendar(e):
            """Open a mini calendar picker dialog."""
            current_month = [datetime.now()]
            selected_date_state = [None]  # Track selected date
            
            month_year_text = ft.Text(
                current_month[0].strftime("%B %Y"),
                size=16,
                weight=ft.FontWeight.BOLD,
                color=PRIMARY_COLOR
            )
            
            calendar_days_container = ft.GridView(
                runs_count=7,
                spacing=5,
                run_spacing=5,
                expand=True,
                child_aspect_ratio=1.2
            )
            
            selected_date_text = ft.Text(
                "No date selected",
                size=12,
                color=ft.Colors.GREY_600,
                text_align=ft.TextAlign.CENTER
            )
            
            confirm_button = ft.ElevatedButton(
                "Confirm",
                width=150,
                height=40,
                style=ft.ButtonStyle(
                    bgcolor=PRIMARY_COLOR,
                    color=ft.Colors.WHITE
                ),
                disabled=True
            )
            
            def update_confirm_button():
                """Enable/disable confirm button based on selection."""
                if selected_date_state[0]:
                    confirm_button.disabled = False
                    selected_date_text.value = f"Selected: {selected_date_state[0].strftime('%b %d, %Y')}"
                else:
                    confirm_button.disabled = True
                    selected_date_text.value = "No date selected"
                
                try:
                    confirm_button.update()
                    selected_date_text.update()
                except:
                    pass
            
            def build_calendar(month_date):
                """Build calendar grid for the given month."""
                # Clear previous controls
                calendar_days_container.controls.clear()
                
                # Update month/year text without calling update
                month_year_text.value = month_date.strftime("%B %Y")
                
                # Day headers
                day_headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                for header in day_headers:
                    calendar_days_container.controls.append(
                        ft.Container(
                            content=ft.Text(
                                header,
                                size=9,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                                color=PRIMARY_COLOR
                            ),
                            alignment=ft.alignment.center
                        )
                    )
                
                # Get first day of month and number of days in month
                first_day = month_date.replace(day=1)
                last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                start_weekday = first_day.weekday()  # 0=Monday, 6=Sunday
                
                # Empty cells for days before month starts
                for _ in range(start_weekday):
                    calendar_days_container.controls.append(
                        ft.Container()
                    )
                
                # Days of the month
                for day in range(1, last_day.day + 1):
                    day_date = month_date.replace(day=day)
                    is_today = day_date.date() == datetime.now().date()
                    is_selected = selected_date_state[0] and day_date.date() == selected_date_state[0].date()
                    
                    # Use default parameter to capture the value
                    def create_day_button(current_day_date):
                        def on_day_click(e):
                            selected_date_state[0] = current_day_date
                            selected_date[0] = current_day_date  # Update outer scope
                            update_confirm_button()
                            build_calendar(current_month[0])
                            try:
                                calendar_days_container.update()
                            except:
                                pass
                        
                        # Determine styling based on state
                        if is_selected:
                            bg_color = ft.Colors.GREEN_700
                            border_width = 3
                        elif is_today:
                            bg_color = PRIMARY_COLOR
                            border_width = 1
                        else:
                            bg_color = ft.Colors.GREY_100
                            border_width = 0
                        
                        text_color = ft.Colors.WHITE if (is_selected or is_today) else ft.Colors.BLACK
                        
                        return ft.Container(
                            content=ft.Text(
                                str(current_day_date.day),
                                size=12,
                                color=text_color,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER
                            ),
                            bgcolor=bg_color,
                            border_radius=8,
                            alignment=ft.alignment.center,
                            on_click=on_day_click,
                            border=ft.border.all(border_width, ft.Colors.GREEN) if is_selected else None
                        )
                    
                    calendar_days_container.controls.append(create_day_button(day_date))
            
            def prev_month(e):
                """Navigate to previous month."""
                current_month[0] = (current_month[0].replace(day=1) - timedelta(days=1)).replace(day=1)
                build_calendar(current_month[0])
                try:
                    calendar_days_container.update()
                    month_year_text.update()
                except:
                    pass
            
            def next_month(e):
                """Navigate to next month."""
                current_month[0] = (current_month[0].replace(day=1) + timedelta(days=32)).replace(day=1)
                build_calendar(current_month[0])
                try:
                    calendar_days_container.update()
                    month_year_text.update()
                except:
                    pass
            
            # Create dialog first (without on_click handlers initially)
            dialog = ft.AlertDialog(
                title=ft.Text("Select Event Date", size=18, weight=ft.FontWeight.BOLD),
                content_padding=20,
            )
            
            def on_confirm(e):
                """Handle confirmation of selected date."""
                if selected_date_state[0]:
                    # Format date as "Month Day, Year" (e.g., "December 15, 2024")
                    formatted_date = selected_date_state[0].strftime("%B %d, %Y")
                    date_display.value = formatted_date
                    try:
                        date_display.update()
                    except:
                        pass
                self.page.close(dialog)
            
            def on_cancel(e):
                """Handle cancel button click."""
                self.page.close(dialog)
            
            # Dialog content
            dialog_content = ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.CHEVRON_LEFT,
                                on_click=prev_month,
                                icon_color=PRIMARY_COLOR,
                                icon_size=24
                            ),
                            ft.Container(
                                content=month_year_text,
                                expand=True,
                                alignment=ft.alignment.center
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CHEVRON_RIGHT,
                                on_click=next_month,
                                icon_color=PRIMARY_COLOR,
                                icon_size=24
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        spacing=0
                    ),
                    ft.Container(
                        content=calendar_days_container,
                        padding=ft.padding.only(top=5, bottom=5, left=5, right=5)
                    ),
                    ft.Container(
                        content=selected_date_text,
                        padding=ft.padding.only(top=5, bottom=5)
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.TextButton(
                                    "Cancel",
                                    on_click=on_cancel
                                ),
                                confirm_button
                            ],
                            spacing=10,
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        padding=ft.padding.only(top=5, bottom=0)
                    )
                ],
                spacing=3
            )
            
            # Set dialog content and button handlers
            dialog.content = dialog_content
            confirm_button.on_click = on_confirm
            
            # Build calendar once before opening
            build_calendar(current_month[0])
            
            self.page.open(dialog)
        
        # Attach click handler to date field
        date_display.on_click = open_calendar
        
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
        
        # Modern form card with fixed width - YOUR premium design
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