# views/base_view.py
"""Base class for all views."""

import flet as ft


class BaseView:
    """Base class for all views providing common functionality."""
    
    def __init__(self, app):
        """Initialize base view with app reference.
        
        Args:
            app: Reference to the main MaScanApp instance
        """
        self.app = app
        self.page = app.page
        self.db = app.db
    
    def build(self, *args, **kwargs):
        """Build and return the view. Must be implemented by subclasses.
        
        Returns:
            ft.View: The constructed Flet view
        """
        raise NotImplementedError("Subclasses must implement build()")
    
    def show_snackbar(self, message: str, color: str = ft.Colors.BLUE):
        """Show a snackbar message.
        
        Args:
            message: Message to display
            color: Background color of snackbar
        """
        self.app.show_snackbar(message, color)
    
    def create_app_bar(self, title: str, show_back: bool = False):
        """Create standardized app bar.
        
        Args:
            title: Title text for the app bar
            show_back: Whether to show back button
            
        Returns:
            ft.AppBar: The constructed app bar
        """
        return self.app.create_app_bar(title, show_back)