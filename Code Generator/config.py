import os

class AppConfig:
    BASE_DIR = os.path.dirname(__file__)
    LOGO_IMAGE = os.path.join(BASE_DIR, "assets", "logo.png")
    APP_NAME = "Euro Tools Code Manager"
    VERSION = "4.2.0"
    SPLASH_SIZE = (300, 650)
    WINDOW_SIZE = (1000, 600) #main screen 
    MIN_WINDOW_SIZE = (600, 600) #Login screen
    APPEARANCE_MODE = "Dark"
    COLOR_THEME = "dark-blue"
    LOADING_DELAY = 1
    ANIMATION_SPEED = 1
    VERSION_URL = "https://raw.githubusercontent.com/Eslam30503o/eurotools-updater/main/version.txt"
    DOWNLOAD_URL = "https://github.com/Eslam30503o/eurotools-updater/releases/download/v2.2.3/Euro.Tools.Code.Generators.exe"
    UPDATE_CHECK_INTERVAL_HOURS = .2

