import customtkinter as ctk
from functools import partial
from tkinter import messagebox
import tkinter as tk
import json
from pathlib import Path
from ui.history_screen import HistoryScreen
from sync.manager import SyncManager
from ui.products_ui import ProductsMixin
from categories import CATEGORIES


import threading

CATEGORIES = CATEGORIES

class ProductsUI(ProductsMixin):
    def __init__(self, root, data_manager, sync_manager, history):
        self.root = root
        self.data_manager = data_manager
        self.sync_manager = sync_manager
        self.history = history

        self.products_frame = ctk.CTkFrame(self.root)
        self.products_frame.pack(fill="both", expand=True)

        # استدعاء واجهة المنتجات
        self.create_products_ui()
