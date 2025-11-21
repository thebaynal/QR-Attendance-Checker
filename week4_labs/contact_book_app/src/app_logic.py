# app_logic.py

import flet as ft

from database import update_contact_db, delete_contact_db, add_contact_db, get_all_contacts_db

def display_contacts(page, contacts_list_view, db_conn, search_term=""):
    """Fetches and displays all contacts in the ListView."""
    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(db_conn, search_term)

    for contact in contacts:
        contact_id, name, phone, email = contact

        container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(name, size=16, weight=ft.FontWeight.BOLD),
                            ft.PopupMenuButton(
                                icon=ft.Icons.MORE_VERT,
                                items=[
                                    ft.PopupMenuItem(
                                        text="Edit",
                                        icon=ft.Icons.EDIT,
                                        on_click=lambda _, c=contact: open_edit_dialog(
                                            page, c, db_conn, contacts_list_view
                                        ),
                                    ),
                                    ft.PopupMenuItem(),
                                    ft.PopupMenuItem(
                                        text="Delete",
                                        icon=ft.Icons.DELETE,
                                        on_click=lambda e, cid=contact_id: delete_contact(
                                            page, cid, db_conn, contacts_list_view
                                        ),
                                    ),
                                ],
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        [ft.Icon(ft.Icons.PHONE, size=16, color=ft.Colors.GREEN), ft.Text(phone or "—")],
                        spacing=10,
                    ),
                    ft.Row(
                        [ft.Icon(ft.Icons.EMAIL, size=16, color=ft.Colors.BLUE), ft.Text(email or "—")],
                        spacing=10,
                    ),
                ],
                spacing=5,
            ),
            padding=10,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            width=300,  # 👈 Restrict width so it doesn’t stretch
        )

        # Hover effect
        def on_hover(e):
            container.bgcolor = ft.Colors.GREY_200 if e.data == "true" else ft.Colors.WHITE
            container.update()

        container.on_hover = on_hover

        # Center the card
        contacts_list_view.controls.append(
            ft.Row(
                [
                    ft.Card(content=container, elevation=2, margin=5)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )

    page.update()
    
def add_contact(page, inputs, contacts_list_view, db_conn):
    """Adds a new contact and refreshes the list."""
    name_input, phone_input, email_input = inputs
    
    
    if not name_input.value.strip():
        name_input.error_text = "Name cannot be empty"
        page.update()
        return
    
    name_input.error_text = None
    
    add_contact_db(db_conn, name_input.value, phone_input.value, email_input.value)
   
    for field in inputs:
        field.value = ""
    
    display_contacts(page, contacts_list_view, db_conn)
    page.update()

def delete_contact(page, contact_id, db_conn, contacts_list_view):
    """Deletes a contact and refreshes the list."""

    def on_yes(e):
        delete_contact_db(db_conn, contact_id)
        dialog.open = False
        page.update()
        display_contacts(page, contacts_list_view, db_conn)

    def on_no(e):
        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirm Delete"),
        content=ft.Text("Are you sure you want to delete this contact?"),
        actions=[
            ft.TextButton("Yes", on_click=on_yes),
            ft.TextButton("No", on_click=on_no),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.open(dialog)

def open_edit_dialog(page, contact, db_conn, contacts_list_view):
    """Opens a dialog to edit a contact's details."""
    contact_id, name, phone, email = contact
    
    edit_name = ft.TextField(label="Name", value=name)
    edit_phone = ft.TextField(label="Phone", value=phone)
    edit_email = ft.TextField(label="Email", value=email)
    
    def save_and_close(e):
        update_contact_db(db_conn, contact_id, edit_name.value, edit_phone.value, edit_email.value)
        dialog.open = False
        page.update()
        display_contacts(page, contacts_list_view, db_conn)
        
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Contact"),
        content=ft.Column([edit_name, edit_phone, edit_email]),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
            ft.TextButton("Save", on_click=save_and_close),
        ],
    )
    
    page.open(dialog)