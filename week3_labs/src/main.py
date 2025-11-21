import flet as ft
import mysql.connector
from db_connection import connect_db


def main(page: ft.Page):
    # Page configuration
    page.title = "User Login"
    page.window_width = 400
    page.window_height = 350
    page.window_frameless = True
    page.bgcolor = ft.Colors.AMBER_ACCENT
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    # Title
    title = ft.Text(
        value="User Login",
        size=20,
        weight=ft.FontWeight.BOLD,
        font_family="Arial",
        text_align="center"
    )

    # Username field
    username_field = ft.TextField(
        label="User name",
        hint_text="Enter your user name",
        helper_text="This is your unique identifier",
        width=300,
        autofocus=True,
        icon=ft.Icon(name="person"),
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT,
    )

    # Password field
    password_field = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        helper_text="This is your secret key",
        width=300,
        password=True,
        can_reveal_password=True,
        icon=ft.Icon(name="lock"),
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT,
    )


    # Login
    def login_click(e):
        print("Login button clicked")

        username = username_field.value
        password = password_field.value
        print(f"Username: {username}, Password: {password}")
        
        success_dialog = ft.AlertDialog(
        title=ft.Text("Login Successful"),
        content=ft.Text("Welcome!"),
        actions=[ft.TextButton("OK", on_click=lambda e: page.dialog.close())],
        icon=ft.Icon(name="check_circle", color="green"),
        )
        failure_dialog = ft.AlertDialog(
            title=ft.Text("Login Failed"),
            content=ft.Text("Invalid username or password"),
            actions=[ft.TextButton("OK", on_click=lambda e: page.dialog.close())],
            icon=ft.Icon(name="error", color="red"),
        )
        invalid_input_dialog = ft.AlertDialog(
            title=ft.Text("Input Error"),
            content=ft.Text("Please enter username and password"),
            actions=[ft.TextButton("OK", on_click=lambda e: page.dialog.close())],
            icon=ft.Icon(name="info", color="blue"),
        )
        database_error_dialog = ft.AlertDialog(
            title=ft.Text("Database Error"),
            content=ft.Text("An error occurred while connecting to the database"),
            actions=[ft.TextButton("OK", on_click=lambda e: page.dialog.close())],
            icon=ft.Icon(name="warning", color="orange"),
        )

        page.overlay.append(success_dialog)
        page.overlay.append(failure_dialog)
        page.overlay.append(invalid_input_dialog)
        page.overlay.append(database_error_dialog)

        if not username or not password:
            page.dialog = invalid_input_dialog
            invalid_input_dialog.open = True
            page.update()
            return

        try:
            conn = connect_db()
            print("Database connected") # I want to make sure that connect_db is connected so I printed it
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username, password)
            )
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            print(f"Query result: {result}") 

            if result:
                success_dialog.content = ft.Text(f"Welcome, {username}!")
                page.dialog = success_dialog
                success_dialog.open = True
            else:
                page.dialog = failure_dialog
                failure_dialog.open = True

            page.update()

        except mysql.connector.Error as err:
            print(f"Database error: {err}")  # If there are errors, I want to know where to debug so I printed the errors in the terminal.
            page.dialog = database_error_dialog
            database_error_dialog.open = True
            page.update()
        
        

    # Login button
    login_button = ft.ElevatedButton(
        text="Login",
        width=100,
        icon=ft.Icon(name="login"),
        on_click=login_click,
    )

    # Layout
    page.add(
        title,
        ft.Container(
            content=ft.Column(
                [username_field, password_field],
                spacing=20,
            ),
        ),
        ft.Container(
            content=login_button,
            alignment=ft.alignment.top_right,
            margin=ft.margin.only(top=20, right=40),
        ),
    )


# Run the app
ft.app(target=main)
