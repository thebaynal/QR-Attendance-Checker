# views/user_management_view.py
"""View for admin to manage users who can scan attendance."""

import flet as ft
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR, BLUE_50


class UserManagementView(BaseView):
    """Admin panel to create scanner users."""
    
    def __init__(self, app):
        """Initialize the user management view.
        
        Args:
            app: Reference to the main MaScanApp instance
        """
        super().__init__(app)
    
    def build(self):
        """Build and return the user management view."""
        try:
            print("DEBUG: Building user management view")
            
            # User list
            users_list = ft.ListView(spacing=5, padding=10, expand=True)
            
            # Form fields
            username_field = ft.TextField(
                label="Username",
                hint_text="Enter username",
                prefix_icon=ft.Icons.PERSON,
                width=300
            )
            password_field = ft.TextField(
                label="Password",
                hint_text="Enter password",
                password=True,
                can_reveal_password=True,
                prefix_icon=ft.Icons.LOCK,
                width=300
            )
            full_name_field = ft.TextField(
                label="Full Name",
                hint_text="Enter full name",
                prefix_icon=ft.Icons.PERSON_OUTLINE,
                width=300
            )
            
            role_dropdown = ft.Dropdown(
                label="Role",
                hint_text="Select role",
                options=[
                    ft.dropdown.Option("admin", "Admin"),
                    ft.dropdown.Option("scanner", "Scanner"),
                ],
                value="scanner",
                width=300
            )
            
            status_text = ft.Text(
                "",
                size=14,
                color=ft.Colors.GREY_700,
                weight=ft.FontWeight.BOLD
            )
            
            def load_users():
                """Load and display all users."""
                try:
                    print("DEBUG: Loading users")
                    users_list.controls.clear()
                    query = "SELECT username, full_name, role FROM users ORDER BY username"
                    results = self.db._execute(query, fetch_all=True)
                    print(f"DEBUG: Found {len(results) if results else 0} users")
                    
                    if results:
                        for username, full_name, role in results:
                            role_badge_color = ft.Colors.GREEN if role == 'admin' else ft.Colors.BLUE
                            role_label = "Admin" if role == 'admin' else "Scanner"
                            
                            user_tile = ft.Card(
                                content=ft.Container(
                                    content=ft.Row(
                                        [
                                            ft.Column(
                                                [
                                                    ft.Text(
                                                        f"{full_name} (@{username})",
                                                        weight=ft.FontWeight.BOLD,
                                                        size=14
                                                    ),
                                                    ft.Text(
                                                        f"Role: {role_label}",
                                                        size=12,
                                                        color=ft.Colors.GREY_600
                                                    ),
                                                ],
                                                expand=True
                                            ),
                                            ft.Container(
                                                content=ft.Text(
                                                    role_label,
                                                    color=ft.Colors.WHITE,
                                                    size=10,
                                                    weight=ft.FontWeight.BOLD
                                                ),
                                                bgcolor=role_badge_color,
                                                padding=8,
                                                border_radius=5
                                            )
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                                    ),
                                    padding=10
                                )
                            )
                            users_list.controls.append(user_tile)
                    else:
                        users_list.controls.append(
                            ft.Text("No users yet", color=ft.Colors.GREY_500)
                        )
                    
                    users_list.update()
                except Exception as e:
                    print(f"ERROR in load_users: {e}")
                    import traceback
                    traceback.print_exc()
            
            def create_user_handler(e):
                """Handle user creation."""
                try:
                    print("DEBUG: Create user handler called")
                    username = username_field.value.strip() if username_field.value else ""
                    password = password_field.value.strip() if password_field.value else ""
                    full_name = full_name_field.value.strip() if full_name_field.value else ""
                    role = role_dropdown.value or 'scanner'
                    
                    print(f"DEBUG: Attempting to create user - username: {username}, password: {password}, full_name: {full_name}, role: {role}")
                    
                    if not all([username, password, full_name]):
                        status_text.value = "All fields are required"
                        status_text.color = ft.Colors.RED
                        status_text.update()
                        print(f"DEBUG: Missing fields - username: {bool(username)}, password: {bool(password)}, full_name: {bool(full_name)}")
                        return
                    
                    if len(password) < 4:
                        status_text.value = "Password must be at least 4 characters"
                        status_text.color = ft.Colors.RED
                        status_text.update()
                        print(f"DEBUG: Password too short: {len(password)} chars")
                        return
                    
                    # Create user
                    result = self.db.create_user(username, password, full_name, role)
                    print(f"DEBUG: Database create_user result: {result}")
                    
                    if result:
                        status_text.value = f"User '{full_name}' created successfully!"
                        status_text.color = ft.Colors.GREEN
                        
                        # Clear fields
                        username_field.value = ""
                        password_field.value = ""
                        full_name_field.value = ""
                        role_dropdown.value = "scanner"
                        
                        # Reload list
                        load_users()
                    else:
                        status_text.value = f"User '{username}' already exists"
                        status_text.color = ft.Colors.RED
                        print(f"DEBUG: User creation failed - user '{username}' may already exist")
                    
                    status_text.update()
                    username_field.update()
                    password_field.update()
                    full_name_field.update()
                    role_dropdown.update()
                except Exception as e:
                    print(f"ERROR in create_user_handler: {e}")
                    import traceback
                    traceback.print_exc()
                    status_text.value = f"Error: {str(e)}"
                    status_text.color = ft.Colors.RED
                    status_text.update()
            
            # Load users on view creation
            print("DEBUG: Calling load_users before returning view")
            load_users()
            
            print("DEBUG: Building UI components")
            view = ft.View(
                "/user_management",
                [
                    self.create_app_bar("User Management", show_back=True),
                    ft.Column(
                        [
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            "Create New Scanner User",
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                            color=PRIMARY_COLOR
                                        ),
                                        ft.Text(
                                            "Create users who can scan attendance for events",
                                            size=12,
                                            color=ft.Colors.GREY_600,
                                            italic=True
                                        ),
                                        ft.Container(height=10),
                                        
                                        # Form
                                        ft.Container(
                                            content=ft.Column(
                                                [
                                                    username_field,
                                                    password_field,
                                                    full_name_field,
                                                    role_dropdown,
                                                    ft.Container(height=10),
                                                    ft.ElevatedButton(
                                                        "Create User",
                                                        width=300,
                                                        height=50,
                                                        on_click=create_user_handler,
                                                        style=ft.ButtonStyle(
                                                            bgcolor=PRIMARY_COLOR,
                                                            color=ft.Colors.BLACK
                                                        )
                                                    ),
                                                    status_text,
                                                ],
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                spacing=15
                                            ),
                                            padding=20,
                                            bgcolor=YELLOW_50,
                                            border_radius=10
                                        ),
                                    ],
                                    spacing=15
                                ),
                                padding=20
                            ),
                            
                            ft.Divider(),
                            ft.Text(
                                "Existing Users",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Container(
                                content=users_list,
                                expand=True,
                                border=ft.border.all(1, ft.Colors.GREY_300),
                                border_radius=10,
                                padding=10
                            )
                        ],
                        spacing=10,
                        expand=True,
                        scroll=ft.ScrollMode.AUTO
                    )
                ]
            )
            print("DEBUG: User management view built successfully")
            return view
            
        except Exception as e:
            print(f"ERROR building user management view: {e}")
            import traceback
            traceback.print_exc()
            
            # Return error view
            return ft.View(
                "/user_management",
                [
                    self.create_app_bar("User Management", show_back=True),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.ERROR, size=80, color=ft.Colors.RED),
                                ft.Text("Error loading user management", size=20, color=ft.Colors.RED),
                                ft.Text(str(e), size=14, color=ft.Colors.GREY_600),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20
                        ),
                        alignment=ft.alignment.center,
                        expand=True
                    )
                ]
            )
