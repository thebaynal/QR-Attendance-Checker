# src/main.py
import flet as ft
from app import MoScanApp


def main(page: ft.Page):
    MoScanApp(page)


if __name__ == "__main__":
    ft.app(target=main, port=8000, host="0.0.0.0")