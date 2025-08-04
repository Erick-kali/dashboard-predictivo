import tkinter as tk
from utils.loading_overlay import LoadingOverlay

class LoadingView:
    @staticmethod
    def show(parent, gif_path, duration=1000):
        overlay = LoadingOverlay(parent, gif_path)
        parent.after(duration, overlay.close)