# views/user_management_view.py
"""Modern view for admin to manage users."""

import flet as ft
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR


class UserManagementView(BaseView):
    """Modern admin panel to create and manage scanner users."""
    
    def __init__(self, app):
        super().__init__(app)
    
    def build(self):
        """Build and return the user management view."""
        try:
            # User list
            users_list = ft.ListView(spacing=12, padding=12, expand=True)
            
            # Form fields - YOUR premium design
            username_field = self.create_modern_text_field(
                label="Username",
                hint_text="Enter Username",
                prefix_icon=ft.Icons.PERSON_OUTLINE,
                width=360,
            )
            
            password_field = self.create_modern_text_field(
                label="Password",
                hint_text="Minimum 4 characters",
                password=True,
                width=360,
            )
            
            full_name_field = self.create_modern_text_field(
                label="Full Name",
                hint_text="e.g., John Doe",
                prefix_icon=ft.Icons.BADGE_OUTLINED,
                width=360,
            )
            
            role_dropdown = ft.Dropdown(
                label="Role",
                hint_text="Select role",
                options=[
                    ft.dropdown.Option("admin", "Admin"),
                    ft.dropdown.Option("scanner", "Scanner"),
                ],
                value="scanner",
                width=360,
                border_radius=12,
                filled=True,
                bgcolor=ft.Colors.GREY_50,
                border_color=ft.Colors.TRANSPARENT,
                focused_border_color=PRIMARY_COLOR,
                focused_bgcolor=ft.Colors.WHITE,
                text_size=15,
            )
            
            status_container = ft.Container(
                content=ft.Text("", size=13),
                visible=False,
                padding=12,
                border_radius=8,
                animate_opacity=300,
            )
            
            def load_users():
                """Load and display all users with modern cards."""
                try:
                    users_list.controls.clear()
                    query = "SELECT username, full_name, role FROM users ORDER BY username"
                    results = self.db._execute(query, fetch_all=True)
                    
                    if results:
                        for username, full_name, role in results:
                            is_admin = role == 'admin'
                            badge_color = ft.Colors.GREEN_600 if is_admin else ft.Colors.BLUE_600
                            role_label = "Admin" if is_admin else "Scanner"
                            
                            # THEIR delete handler logic with proper closure
                            def make_delete_handler(user_username, user_fullname):
                                def delete_user_click(e):
                                    print(f"DEBUG: Delete clicked for {user_username}")
                                    
                                    def handle_confirm(dlg_event):
                                        try:
                                            print(f"DEBUG: Confirming deletion of {user_username}")
                                            
                                            # Close dialog first
                                            self.page.close(delete_dlg)
                                            
                                            # Delete from database
                                            self.db._execute("DELETE FROM users WHERE username = ?", (user_username,))
                                            print(f"DEBUG: User deleted from database")
                                            
                                            # Show success message
                                            self.show_snackbar(f"✅ User '{user_fullname}' deleted!", ft.Colors.GREEN)
                                            
                                            # Reload users list
                                            load_users()
                                            
                                        except Exception as ex:
                                            print(f"ERROR: {ex}")
                                            import traceback
                                            traceback.print_exc()
                                            self.show_snackbar(f"❌ Error deleting user: {str(ex)}", ft.Colors.RED)
                                    
                                    def handle_cancel(dlg_event):
                                        print(f"DEBUG: Deletion cancelled")
                                        self.page.close(delete_dlg)
                                    
                                    # Create dialog with proper styling
                                    delete_dlg = ft.AlertDialog(
                                        modal=True,
                                        title=ft.Row(
                                            [
                                                ft.Icon(ft.Icons.WARNING, color=ft.Colors.RED, size=30),
                                                ft.Text("Confirm Deletion", weight=ft.FontWeight.BOLD, size=18),
                                            ],
                                            spacing=10
                                        ),
                                        content=ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Text(
                                                        f"Are you sure you want to delete user:",
                                                        size=14
                                                    ),
                                                    ft.Text(
                                                        f"'{user_fullname}' (@{user_username})",
                                                        size=14,
                                                        weight=ft.FontWeight.BOLD,
                                                        color=ft.Colors.RED
                                                    ),
                                                    ft.Container(height=10),
                                                    ft.Row(
                                                        [
                                                            ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.ORANGE, size=20),
                                                            ft.Text(
                                                                "This action cannot be undone!",
                                                                size=12,
                                                                color=ft.Colors.GREY_700,
                                                                italic=True
                                                            ),
                                                        ],
                                                        spacing=5
                                                    )
                                                ],
                                                tight=True
                                            ),
                                            width=400
                                        ),
                                        actions=[
                                            ft.TextButton(
                                                "Cancel", 
                                                on_click=handle_cancel,
                                                style=ft.ButtonStyle(color=ft.Colors.GREY_700)
                                            ),
                                            ft.ElevatedButton(
                                                "Yes, Delete",
                                                icon=ft.Icons.DELETE_FOREVER,
                                                on_click=handle_confirm,
                                                style=ft.ButtonStyle(
                                                    bgcolor=ft.Colors.RED_700,
                                                    color=ft.Colors.WHITE
                                                )
                                            ),
                                        ],
                                        actions_alignment=ft.MainAxisAlignment.END,
                                    )
                                    
                                    # Open dialog using page.open() method
                                    self.page.open(delete_dlg)
                                    print("DEBUG: Dialog opened")
                                
                                return delete_user_click
                            
                            # YOUR premium user card design
                            user_card = self.create_modern_card(
                                content=ft.Row(
                                    [
                                        ft.Container(
                                            content=ft.Icon(
                                                ft.Icons.ADMIN_PANEL_SETTINGS if is_admin else ft.Icons.QR_CODE_SCANNER,
                                                color=ft.Colors.WHITE,
                                                size=24,
                                            ),
                                            width=48,
                                            height=48,
                                            bgcolor=badge_color,
                                            border_radius=12,
                                            alignment=ft.alignment.center,
                                        ),
                                        ft.Column(
                                            [
                                                ft.Text(
                                                    full_name,
                                                    weight=ft.FontWeight.W_600,
                                                    size=15,
                                                ),
                                                ft.Text(
                                                    f"@{username}",
                                                    size=13,
                                                    color=ft.Colors.GREY_600,
                                                ),
                                            ],
                                            spacing=2,
                                            expand=True,
                                        ),
                                        self.create_info_badge(role_label, badge_color),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINE,
                                            icon_color=ft.Colors.RED_400,
                                            icon_size=20,
                                            tooltip="Delete User",
                                            on_click=make_delete_handler(username, full_name),
                                            style=ft.ButtonStyle(
                                                bgcolor=ft.Colors.RED_50,
                                                shape=ft.RoundedRectangleBorder(radius=8),
                                            ),
                                        ),
                                    ],
                                    spacing=16,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                padding=16,
                            )
                            users_list.controls.append(user_card)
                    else:
                        users_list.controls.append(
                            self.create_empty_state(
                                icon=ft.Icons.PEOPLE_OUTLINE,
                                title="No Users Yet",
                                subtitle="Create your first user to get started",
                                icon_size=60,
                            )
                        )
                    
                    # Only update if ListView is on the page
                    if users_list.page:
                        users_list.update()
                except Exception as e:
                    print(f"ERROR in load_users: {e}")
                    import traceback
                    traceback.print_exc()
            
            def create_user_handler(e):
                """Handle user creation with validation."""
                try:
                    # Clear previous status
                    status_container.visible = False
                    status_container.update()
                    
                    username = username_field.value.strip() if username_field.value else ""
                    password = password_field.value.strip() if password_field.value else ""
                    full_name = full_name_field.value.strip() if full_name_field.value else ""
                    role = role_dropdown.value or 'scanner'
                    
                    # Validation
                    if not all([username, password, full_name]):
                        status_container.content.value = "❌ All fields are required"
                        status_container.content.color = ft.Colors.RED_700
                        status_container.bgcolor = ft.Colors.RED_50
                        status_container.border = ft.border.all(1, ft.Colors.RED_200)
                        status_container.visible = True
                        status_container.update()
                        return
                    
                    if len(password) < 4:
                        status_container.content.value = "❌ Password must be at least 4 characters"
                        status_container.content.color = ft.Colors.RED_700
                        status_container.bgcolor = ft.Colors.RED_50
                        status_container.border = ft.border.all(1, ft.Colors.RED_200)
                        status_container.visible = True
                        status_container.update()
                        return
                    
                    # Create user
                    result = self.db.create_user(username, password, full_name, role)
                    
                    if result:
                        status_container.content.value = f"✅ User '{full_name}' created successfully!"
                        status_container.content.color = ft.Colors.GREEN_700
                        status_container.bgcolor = ft.Colors.GREEN_50
                        status_container.border = ft.border.all(1, ft.Colors.GREEN_200)
                        
                        # Clear fields
                        username_field.value = ""
                        password_field.value = ""
                        full_name_field.value = ""
                        role_dropdown.value = "scanner"
                        
                        # Update fields
                        username_field.update()
                        password_field.update()
                        full_name_field.update()
                        role_dropdown.update()
                        
                        # Reload list - safely handle ListView update
                        try:
                            load_users()
                        except Exception as load_ex:
                            print(f"DEBUG: Could not update users_list on page, will update next load: {load_ex}")
                    else:
                        status_container.content.value = f"❌ User '{username}' already exists"
                        status_container.content.color = ft.Colors.RED_700
                        status_container.bgcolor = ft.Colors.RED_50
                        status_container.border = ft.border.all(1, ft.Colors.RED_200)
                    
                    status_container.visible = True
                    status_container.update()
                    
                except Exception as e:
                    print(f"ERROR in create_user_handler: {e}")
                    import traceback
                    traceback.print_exc()
                    status_container.content.value = f"❌ Error: {str(e)}"
                    status_container.content.color = ft.Colors.RED_700
                    status_container.bgcolor = ft.Colors.RED_50
                    status_container.border = ft.border.all(1, ft.Colors.RED_200)
                    status_container.visible = True
                    status_container.update()
            
            # Load users initially
            load_users()
            
            # Build form card - YOUR premium design
            form_card = self.create_modern_card(
                content=ft.Column(
                    [
                        self.create_section_title("Create New User", size=20, icon=ft.Icons.PERSON_ADD),
                        ft.Text(
                            "Add users who can scan attendance for events",
                            size=13,
                            color=ft.Colors.GREY_600,
                        ),
                        
                        ft.Container(height=20),
                        
                        # Form fields
                        username_field,
                        password_field,
                        full_name_field,
                        role_dropdown,
                        
                        ft.Container(height=12),
                        status_container,
                        ft.Container(height=16),
                        
                        # Create button
                        self.create_modern_button(
                            text="Create User",
                            icon=ft.Icons.PERSON_ADD,
                            on_click=create_user_handler,
                            width=360,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                ),
                padding=28,
            )
            
            # Build users list card - YOUR premium design
            users_card = self.create_modern_card(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                self.create_section_title("Existing Users", size=18, icon=ft.Icons.PEOPLE),
                                ft.Container(expand=True),
                                ft.IconButton(
                                    icon=ft.Icons.REFRESH,
                                    icon_size=20,
                                    tooltip="Refresh list",
                                    on_click=lambda e: load_users(),
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.Colors.GREY_100,
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    ),
                                ),
                            ],
                        ),
                        ft.Container(height=12),
                        users_list,
                    ],
                    spacing=0,
                    expand=True,
                ),
                padding=20,
                expand=True,
            )
            
            return ft.View(
                "/user_management",
                [
                    self.create_app_bar("User Management", show_back=True),
                    ft.Container(
                        content=ft.Column(
                            [
                                form_card,
                                ft.Container(height=20),
                                users_card,
                            ],
                            spacing=0,
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        padding=20,
                        expand=True,
                        bgcolor=ft.Colors.GREY_50,
                    )
                ],
                bgcolor=ft.Colors.GREY_50,
            )
            
        except Exception as e:
            print(f"ERROR building user management view: {e}")
            import traceback
            traceback.print_exc()
            
            return ft.View(
                "/user_management",
                [
                    self.create_app_bar("User Management", show_back=True),
                    self.create_empty_state(
                        icon=ft.Icons.ERROR_OUTLINE,
                        title="Error loading user management",
                        subtitle=str(e),
                    )
                ],
                bgcolor=ft.Colors.GREY_50,
            )