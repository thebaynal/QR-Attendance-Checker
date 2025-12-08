# src/main.py
import flet as ft
import time
import threading
from app import MaScanApp


def main(page: ft.Page):
    MaScanApp(page)


if __name__ == "__main__":
    ft.app(target=main, port=0)



# views/login_view.py
"""Login view with modern animations and styling."""

import flet as ft
from views.base_view import BaseView
from views.ui_utils import AnimationUtils, StyleUtils
from config.constants import APP_TITLE, APP_TAGLINE, PRIMARY_COLOR


class LoginView(BaseView):
    """Modern login screen with animations."""
    
    def build(self):
        """Build and return the login view."""
        username = ft.TextField(
            label="Username",
            width=340,
            prefix_icon=ft.Icons.PERSON,
            border_radius=8,
            bgcolor=StyleUtils.COLORS["light"],
            border_color=StyleUtils.COLORS["border"],
        )
        password = ft.TextField(
            label="Password",
            width=340,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            border_radius=8,
            bgcolor=StyleUtils.COLORS["light"],
            border_color=StyleUtils.COLORS["border"],
        )
        
        error_text = ft.Text(
            "",
            color=StyleUtils.COLORS["error"],
            size=12,
            visible=False,
            text_align=ft.TextAlign.CENTER
        )
        
        login_button = StyleUtils.primary_button("LOGIN", width=340)
        
        def authenticate(e):
            """Handle login authentication."""
            error_text.visible = False
            login_button.disabled = True
            login_button.update()
            error_text.update()
            
            if not username.value or not password.value:
                error_text.value = "Please enter both username and password"
                error_text.visible = True
                login_button.disabled = False
                error_text.update()
                login_button.update()
                return
            
            username_value = username.value.strip()
            user_authenticated = self.db.authenticate_user(username_value, password.value)
            
            if user_authenticated:
                full_name = self.db._execute(
                    "SELECT full_name FROM users WHERE username = ?",
                    (username_value,),
                    fetch_one=True
                )
                display_name = full_name[0] if full_name else username_value
                
                self.app.current_user = username_value
                self.db.record_login(username_value)
                
                self.show_snackbar(f"Welcome, {display_name}! 👋", ft.Colors.GREEN)
                self.page.go("/home")
            else:
                error_text.value = "❌ Invalid username or password"
                error_text.visible = True
                error_text.update()
                password.value = ""
                password.update()
                login_button.disabled = False
                login_button.update()
        
        login_button.on_click = authenticate
        username.on_submit = authenticate
        password.on_submit = authenticate
        
        # Animated form card
        form_card = ft.Container(
            width=380,
            padding=ft.padding.all(28),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.BLACK12),
            content=ft.Column(
                [
                    # Logo & Title Section
                    ft.Column(
                        [
                            ft.Image(
                                src="final-project\\src\\assets\\MS_Logo_Blue.png",
                                width=90,
                                height=90,
                                fit=ft.ImageFit.CONTAIN,
                                error_content=ft.Icon(
                                    ft.Icons.QR_CODE_SCANNER,
                                    size=60,
                                    color=PRIMARY_COLOR
                                )
                            ),
                            ft.Text(
                                "MaScan",
                                size=32,
                                weight=ft.FontWeight.BOLD,
                                color=StyleUtils.COLORS["primary"]
                            ),
                            ft.Text(
                                "Attendance Management",
                                size=14,
                                color=StyleUtils.COLORS["text_secondary"]
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6
                    ),
                    
                    ft.Container(height=24),
                    
                    # Form fields
                    ft.Column(
                        [
                            username,
                            password,
                            error_text,
                            ft.Container(height=4),
                            login_button,
                        ],
                        spacing=12,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    
                    ft.Container(height=20),
                    
                    ft.Divider(color=StyleUtils.COLORS["border"]),
                    
                    ft.Text(
                        APP_TAGLINE,
                        size=12,
                        color=StyleUtils.COLORS["text_secondary"],
                        italic=True,
                        text_align=ft.TextAlign.CENTER
                    )
                ],
                spacing=14,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        
        # Animated form card with slide-in
        animated_form = AnimationUtils.slide_in_container(form_card, direction="up", duration_ms=600)
        
        return ft.View(
            "/",
            [
                ft.Container(
                    expand=True,
                    padding=24,
                    gradient=ft.LinearGradient(
                        [StyleUtils.COLORS["primary_dark"], StyleUtils.COLORS["primary"], StyleUtils.COLORS["primary_light"]],
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                    ),
                    content=ft.Column(
                        [animated_form],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    )
                )
            ],
            bgcolor=ft.Colors.TRANSPARENT
        )

# views/event_view.py
"""Event view for displaying and managing events."""

import flet as ft
from views.base_view import BaseView
from views.ui_utils import AnimationUtils, StyleUtils
from config.constants import PRIMARY_COLOR


class EventView(BaseView):
    """View for displaying event details and managing attendance."""
    
    def build(self):
        """Build and return the event view."""
        event_id = self.page.route.id
        event_data = self.db.get_event(event_id)
        
        if not event_data:
            return ft.Column(
                [
                    ft.Text("Event not found", size=18, weight=ft.FontWeight.BOLD),
                    ft.TextButton("Go back", on_click=lambda e: self.page.go("/home")),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        
        is_admin = self.db.is_user_admin(self.app.current_user)
        user_attendance = self.db.get_user_attendance(event_id, self.app.current_user)
        
        # Header section
        header = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        event_data['name'],
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=StyleUtils.COLORS["text_primary"]
                    ),
                    ft.Text(
                        event_data['date'],
                        size=14,
                        color=StyleUtils.COLORS["text_secondary"]
                    ),
                ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.START
            ),
            padding=ft.padding.all(16),
            bgcolor=StyleUtils.COLORS["primary_light"],
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
        )
        
        # Description section
        description = ft.Container(
            content=ft.Text(
                event_data['desc'] if event_data['desc'] else "No description available",
                size=14,
                color=StyleUtils.COLORS["text_primary"],
                max_lines=3,
                overflow=ft.TextOverflow.ELLIPSIS
            ),
            padding=ft.padding.all(16),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, StyleUtils.COLORS["border"]),
        )
        
        # Attendance section
        attendance_title = ft.Text(
            "Attendance",
            size=18,
            weight=ft.FontWeight.BOLD,
            color=StyleUtils.COLORS["text_primary"]
        )
        
        attendance_list = ft.Column(
            spacing=12,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.START
        )
        
        def load_attendance():
            """Load and display attendance records."""
            attendance_records = self.db.get_attendance_records(event_id)
            
            for index, record in enumerate(attendance_records):
                user_name = record['username']
                check_in_time = record['check_in']
                check_out_time = record['check_out'] if record['check_out'] else "N/A"
                
                item = ft.Row(
                    [
                        ft.Text(user_name, size=14, color=StyleUtils.COLORS["text_primary"]),
                        ft.Text(check_in_time, size=12, color=StyleUtils.COLORS["text_secondary"]),
                        ft.Text(check_out_time, size=12, color=StyleUtils.COLORS["text_secondary"]),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8
                )
                
                attendance_list.controls.append(item)
            
            attendance_list.update()
        
        load_attendance()
        
        # Action buttons
        action_buttons = ft.Row(
            [
                StyleUtils.primary_button(
                    "Check In",
                    on_click=lambda e: self.check_in_out("check_in"),
                    width=160
                ),
                StyleUtils.primary_button(
                    "Check Out",
                    on_click=lambda e: self.check_in_out("check_out"),
                    width=160
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=16
        )
        
        # Admin controls
        admin_controls = ft.Column(
            [
                StyleUtils.secondary_button(
                    "Delete Event",
                    on_click=lambda e: self.delete_event(event_id, event_data['name']),
                    icon=ft.Icons.DELETE,
                    width=180
                ),
            ],
            spacing=12,
            visible=is_admin
        )
        
        # Main content column
        content = ft.Column(
            [
                header,
                ft.Container(height=16),
                description,
                ft.Container(height=24),
                attendance_title,
                attendance_list,
                ft.Container(height=24),
                action_buttons,
                admin_controls,
            ],
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        return ft.View(
            f"/event/{event_id}",
            [
                ft.Container(
                    expand=True,
                    padding=24,
                    bgcolor=StyleUtils.COLORS["light"],
                    content=content
                )
            ],
            bgcolor=ft.Colors.TRANSPARENT
        )
    
    def check_in_out(self, action):
        """Handle check-in and check-out actions."""
        event_id = self.page.route.id
        username = self.app.current_user
        
        if action == "check_in":
            self.db.check_in(event_id, username)
            self.show_snackbar("Checked in successfully!", ft.Colors.GREEN)
        elif action == "check_out":
            self.db.check_out(event_id, username)
            self.show_snackbar("Checked out successfully!", ft.Colors.GREEN)
        
        # Refresh attendance list
        self.load_attendance()
    
    def delete_event(self, event_id, event_name):
        """Delete an event from the database."""
        def confirm_delete(e):
            """Confirm deletion of the event."""
            self.db.delete_event(event_id)
            self.show_snackbar(f"Event '{event_name}' deleted successfully.", ft.Colors.GREEN)
            self.page.go("/home")
        
        # Show confirmation dialog
        self.dialogs.confirm(
            title="Delete Event",
            content=f"Are you sure you want to delete the event '{event_name}'?",
            on_confirm=confirm_delete
        )

# views/home_view.py
"""Home view displaying upcoming events and user statistics."""

import flet as ft
from views.base_view import BaseView
from views.ui_utils import AnimationUtils, StyleUtils
from config.constants import PRIMARY_COLOR


class HomeView(BaseView):
    """Home screen displaying user-specific information and events."""
    
    def build(self):
        """Build and return the home view."""
        user_name = self.app.current_user
        user_data = self.db.get_user_data(user_name)
        
        # Welcome section
        welcome_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        f"Welcome back, {user_data['full_name']}!",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=StyleUtils.COLORS["text_primary"]
                    ),
                    ft.Text(
                        "Here are your upcoming events:",
                        size=14,
                        color=StyleUtils.COLORS["text_secondary"]
                    ),
                ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.START
            ),
            padding=ft.padding.all(16),
            bgcolor=StyleUtils.COLORS["primary_light"],
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
        )
        
        # Upcoming events list
        events_list = ft.Column(
            spacing=16,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        def load_events():
            """Load and display upcoming events."""
            upcoming_events = self.db.get_upcoming_events(user_name)
            
            for index, event in enumerate(upcoming_events):
                event_card = self.create_event_card(event['id'], event, index)
                events_list.controls.append(event_card)
            
            events_list.update()
        
        load_events()
        
        # Statistics section
        stats_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Your Statistics",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=StyleUtils.COLORS["text_primary"]
                    ),
                    ft.Row(
                        [
                            StyleUtils.stat_card(
                                str(user_data['events_attended']),
                                "Events Attended",
                                icon=ft.Icons.EVENT,
                                color=PRIMARY_COLOR
                            ),
                            StyleUtils.stat_card(
                                str(user_data['check_ins']),
                                "Total Check-Ins",
                                icon=ft.Icons.QR_CODE,
                                color=PRIMARY_COLOR
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        spacing=16
                    ),
                ],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.START
            ),
            padding=ft.padding.all(16),
            border_radius=12,
            bgcolor=StyleUtils.COLORS["light"],
            border=ft.border.all(1, StyleUtils.COLORS["border"]),
        )
        
        # Main content column
        content = ft.Column(
            [
                welcome_card,
                ft.Container(height=16),
                events_list,
                ft.Container(height=16),
                stats_card,
            ],
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        return ft.View(
            "/home",
            [
                ft.Container(
                    expand=True,
                    padding=24,
                    bgcolor=StyleUtils.COLORS["light"],
                    content=content
                )
            ],
            bgcolor=ft.Colors.TRANSPARENT
        )
    
    def create_event_card(self, event_id: str, event_data: dict, index: int = 0):
        """Create an animated card for displaying an event."""
        # Build menu items based on user role
        menu_items = [
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
        ]
        
        if self.db.is_user_admin(self.app.current_user):
            menu_items.extend([
                ft.PopupMenuItem(),
                ft.PopupMenuItem(
                    text="Delete Event",
                    icon=ft.Icons.DELETE,
                    on_click=lambda e, eid=event_id, name=event_data['name']: 
                        self.delete_event_handler(eid, name)
                ),
            ])
        
        card_content = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.EVENT, color=PRIMARY_COLOR, size=32),
                                ft.Column(
                                    [
                                        ft.Text(
                                            event_data['name'],
                                            weight=ft.FontWeight.BOLD,
                                            size=16,
                                            color=StyleUtils.COLORS["text_primary"]
                                        ),
                                        ft.Text(
                                            event_data['date'],
                                            size=13,
                                            color=StyleUtils.COLORS["text_secondary"]
                                        ),
                                    ],
                                    spacing=3,
                                    expand=True
                                ),
                                ft.PopupMenuButton(items=menu_items)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=12
                        ),
                        padding=16
                    ),
                    ft.Divider(height=1, color=StyleUtils.COLORS["border"]),
                    ft.Container(
                        content=ft.Text(
                            event_data['desc'] if event_data['desc'] else "No description",
                            size=12,
                            color=StyleUtils.COLORS["text_secondary"],
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        padding=ft.padding.symmetric(horizontal=16, vertical=12)
                    )
                ],
                spacing=0
            ),
            padding=0,
            border_radius=12,
            shadow=ft.BoxShadow(
                blur_radius=8,
                color=ft.Colors.BLACK10,
                offset=ft.Offset(0, 2)
            )
        )
        
        card = ft.Card(
            content=card_content,
            elevation=0,
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        
        # Stagger animation for cards
        return AnimationUtils.slide_in_container(
            card, 
            direction="up", 
            duration_ms=300 + (index * 50)
        )
    
    def delete_event_handler(self, event_id, event_name):
        """Handle event deletion."""
        def confirm_delete(e):
            """Confirm deletion of the event."""
            self.db.delete_event(event_id)
            self.show_snackbar(f"Event '{event_name}' deleted successfully.", ft.Colors.GREEN)
            self.load_events()
        
        # Show confirmation dialog
        self.dialogs.confirm(
            title="Delete Event",
            content=f"Are you sure you want to delete the event '{event_name}'?",
            on_confirm=confirm_delete
        )

def show_success_animation():
    """Show a success animation when attendance is recorded."""
    success_container = ft.Container(
        content=ft.Column(
            [
                ft.Icon(
                    ft.Icons.CHECK_CIRCLE,
                    size=64,
                    color=ft.Colors.GREEN,
                    opacity=0,
                    animate_opacity=ft.animation.Animation(
                        duration_ms=500,
                        curve=ft.AnimationCurve.EASE_OUT
                    )
                ),
                ft.Text(
                    "✓ Attendance Recorded!",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREEN
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12
        ),
        alignment=ft.alignment.center,
        height=200,
        opacity=0,
        animate_opacity=ft.animation.Animation(
            duration_ms=300,
            curve=ft.AnimationCurve.EASE_IN
        )
    )
    
    def animate():
        success_container.opacity = 1
        success_container.update()
        time.sleep(1.5)
        success_container.opacity = 0
        success_container.update()
    
    threading.Thread(target=animate, daemon=True).start()
    return success_container