# main.py
import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact

def main(page: ft.Page):
    page.title = "Contact Book"
    page.window_width = 400
    page.window_height = 600
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    page.theme_mode = ft.ThemeMode.LIGHT
    theme_button = ft.IconButton(icon=ft.Icons.DARK_MODE)
    
    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_button.icon = ft.Icons.DARK_MODE
        page.update()
    theme_button.on_click = toggle_theme
    
    db_conn = init_db()
    
    name_input = ft.TextField(label="Name", width=350)
    phone_input = ft.TextField(label="Phone", width=350)
    email_input = ft.TextField(label="Email", width=350)
    search_input = ft.TextField(
        label="Search",
        width=350,
        on_change=lambda e: display_contacts(
            page, contacts_list_view, db_conn, search_input.value.strip()
        ),
    )
    
    inputs = (name_input, phone_input, email_input)
    
    contacts_list_view = ft.ListView(expand=1, spacing=10, auto_scroll=True)
    
    add_button = ft.ElevatedButton(
        text="Add Contact",
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn)
    )
    
    # main content
    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Contact Book", size=20, weight=ft.FontWeight.BOLD),
                        theme_button,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text("Enter Contact Details:", size=16, weight=ft.FontWeight.BOLD),
                name_input,
                phone_input,
                email_input,
                add_button,
                ft.Divider(),
                ft.Text("Contacts:", size=16, weight=ft.FontWeight.BOLD),
                search_input,
                contacts_list_view,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            spacing=10,
        )
    )
    
    display_contacts(
        page,
        contacts_list_view,
        db_conn,
        search_term=search_input.value.strip() if search_input.value else ""
    )

if __name__ == "__main__":
    ft.app(target=main)
