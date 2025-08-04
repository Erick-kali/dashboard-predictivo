import tkinter as tk
class Header(tk.Frame):
    def __init__(self, parent, text):
        super().__init__(parent, bg="#5C9DBF", height=50)
        self.pack(fill="x")
        label = tk.Label(self, text=text, bg="#5C9DBF", fg="white", font=(None, 16, "bold"))
        label.pack(pady=10)