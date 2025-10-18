import os

class AppConfig:
    BASE_DIR = os.path.dirname(__file__)
    LOGO_IMAGE = os.path.join(BASE_DIR, "assets", "logo.png")
    APP_NAME = "Euro Tools Code Manager"
    VERSION = "2.2.3"
    SPLASH_SIZE = (450, 500)
    WINDOW_SIZE = (1200, 700)
    MIN_WINDOW_SIZE = (900, 600)
    APPEARANCE_MODE = "system"
    COLOR_THEME = "dark-blue"
    LOADING_DELAY = 50
    ANIMATION_SPEED = 8
    VERSION_URL = "https://raw.githubusercontent.com/USERNAME/REPO/main/version.txt"
    DOWNLOAD_URL = "https://github.com/USERNAME/REPO/releases/latest/download/EuroTools.exe"
    UPDATE_CHECK_INTERVAL_HOURS = 24

