"""Weather Application using Flet v0.28.3"""

import flet as ft
# FIX: All custom exception classes (CityNotFoundError, NetworkError, WeatherServiceError) 
# must be explicitly imported from the service file so Python recognizes them when they are raised.
from mod6_labs.weather_service import WeatherService, WeatherServiceError, CityNotFoundError, NetworkError
from mod6_labs.config import Config


class WeatherApp:
    """Main Weather Application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.setup_page()
        self.build_ui()
    
    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        
        # Add theme switcher
        self.page.theme_mode = ft.ThemeMode.SYSTEM  # Use system theme preference
    
        # Custom Light Theme
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.colors.BLUE,
        )
        # Custom Dark Theme for proper contrast in dark mode
        self.page.dark_theme = ft.Theme(
            color_scheme_seed=ft.colors.BLUE,
            # Ensure background is darker in dark mode
            color_scheme=ft.ColorScheme(background=ft.colors.BLACK87), 
        )
    
        self.page.padding = 20
    
        # FIX: Corrected window property access to solve AttributeError.
        # Properties are set directly on the page object, not via page.window.
        self.page.window_width = Config.APP_WIDTH
        self.page.window_height = Config.APP_HEIGHT
        self.page.window_resizable = False
        self.page.window_center()
    
    def build_ui(self):
        """Build the user interface."""
        # Title
        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLUE_700,
        )
        
        # Theme toggle button
        self.theme_button = ft.IconButton(
            icon=ft.icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )

        # Title and Theme Toggle in a Row
        title_row = ft.Row(
            [
                self.title,
                self.theme_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # City input field
        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.colors.BLUE_400,
            prefix_icon=ft.icons.LOCATION_CITY,
            autofocus=True,
            on_submit=self.on_search,
        )
        
        # Search button
        self.search_button = ft.ElevatedButton(
            "Get Weather",
            icon=ft.icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE_700,
            ),
        )
        
        # Weather display container (initially hidden)
        self.weather_container = ft.Container(
            visible=False,
            # IMPROVEMENT: Use theme-aware color for a contrasting background
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.SURFACE), 
            border_radius=10,
            padding=20,
        )
        
        # Error message
        self.error_message = ft.Text(
            "",
            color=ft.colors.RED_700,
            visible=False,
        )
        
        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        # Add all components to page
        self.page.add(
            ft.Column(
                [
                    title_row, # Using the new row container
                    ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                    self.city_input,
                    self.search_button,
                    ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                    self.loading,
                    self.error_message,
                    self.weather_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                width=Config.APP_WIDTH, # Ensures the row stretches properly
            )
        )
    
    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.icons.DARK_MODE
        self.page.update()
    
    def on_search(self, e):
        """Handle search button click or enter key press."""
        self.page.run_task(self.get_weather)
    
    async def get_weather(self):
        """Fetch and display weather data."""
        city = self.city_input.value.strip()
        
        # User Input Validation
        if not city:
            self.show_error("Please enter a city name.")
            return
        
        # Show loading, hide previous results
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()
        
        # --- Simplified Error Handling ---
        try:
            weather_data = await self.weather_service.get_weather(city)
            self.display_weather(weather_data)
        
        # Catches CityNotFoundError, NetworkError, and the base WeatherServiceError
        except WeatherServiceError as e:
            # Show user-friendly error message generated by weather_service.py
            self.show_error(str(e))
        
        # Catch any unexpected system or programming errors
        except Exception as e:
            self.show_error("An unexpected error occurred. Please try again.")
        
        finally:
            self.loading.visible = False
            self.page.update()
            
    
    def display_weather(self, data: dict):
        """Display weather information and animate the reveal."""
        # Extract data (unchanged)
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = data.get("main", {}).get("temp", 0)
        feels_like = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        
        # Build weather display
        self.weather_container.content = ft.Column(
            [
                # Location
                ft.Text(
                    f"{city_name}, {country}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                
                # Weather icon and description
                ft.Row(
                    [
                        ft.Image(
                            src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
                            width=100,
                            height=100,
                        ),
                        ft.Text(
                            description,
                            size=20,
                            italic=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                
                # Temperature
                ft.Text(
                    f"{temp:.1f}°C",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE_900,
                ),
                
                ft.Text(
                    f"Feels like {feels_like:.1f}°C",
                    size=16,
                    # IMPROVEMENT: Use theme-aware text color
                    color=ft.colors.with_opacity(0.8, ft.colors.ON_BACKGROUND), 
                ),
                
                ft.Divider(),
                
                # Additional info
                ft.Row(
                    [
                        self.create_info_card(
                            ft.icons.WATER_DROP,
                            "Humidity",
                            f"{humidity}%"
                        ),
                        self.create_info_card(
                            ft.icons.AIR,
                            "Wind Speed",
                            f"{wind_speed} m/s"
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        # --- FIX: Correct Animation Implementation (No asyncio.sleep needed) ---
        
        # 1. Set the animation property (Duration in milliseconds)
        self.weather_container.animate_opacity = 300
        
        # 2. Set the starting state (Invisible) and visible=True
        # Flet registers the starting point (opacity 0)
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.page.update() 
        
        # 3. Set the final state (Fully visible)
        # Flet detects the change from opacity=0 to opacity=1 and animates the difference.
        self.weather_container.opacity = 1
        self.error_message.visible = False
        self.page.update() # Triggers the animation
    
    def create_info_card(self, icon, label, value):
        """Create an info card for weather details."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=ft.colors.BLUE_700),
                    # IMPROVEMENT: Use theme-aware label color
                    ft.Text(label, size=12, color=ft.colors.with_opacity(0.8, ft.colors.ON_SURFACE)), 
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE_900,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            # IMPROVEMENT: Use theme-aware color for card background
            bgcolor=ft.colors.SURFACE_VARIANT, 
            border_radius=10,
            padding=15,
            width=150,
        )
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.page.update()


def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)