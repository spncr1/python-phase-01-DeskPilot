# Logic for organising files
import webbrowser
from pathlib import Path
import os

class DesktopOrganiserUI:
    def __init__(self, parent=None, main_menu=None):
        self.parent = parent
        self.main_menu = main_menu
        self.show_ui()
    
    def show_ui(self):
        # Get the absolute path to the HTML file
        html_path = Path(__file__).parent.parent / "gui" / "desktop_organiser_ui.html"
        
        # Convert to file URL and open in default web browser
        file_url = f"file://{html_path.absolute()}"
        webbrowser.open(file_url)

if __name__ == "__main__":
    DesktopOrganiserUI()
