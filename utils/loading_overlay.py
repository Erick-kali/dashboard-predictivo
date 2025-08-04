import tkinter as tk
from PIL import Image, ImageTk, ImageSequence

class LoadingOverlay(tk.Toplevel):
    def __init__(self, parent, gif_path, text="Cargando..."):
        super().__init__(parent)
        self.overrideredirect(True)
        self.geometry(f"300x200+{parent.winfo_x()+250}+{parent.winfo_y()+200}")
        self.config(bg="#000000")
        self.attributes('-alpha', 0.75)

        self.label = tk.Label(self, text=text, bg="#000000", fg="white", font=(None, 14))
        self.label.pack(pady=10)

        self.frames = [ImageTk.PhotoImage(frame.copy().convert('RGBA'))
                       for frame in ImageSequence.Iterator(Image.open(gif_path))]
        self.gif_label = tk.Label(self, bg="#000000")
        self.gif_label.pack()
        self.anim_index = 0
        self.animate()

    def animate(self):
        frame = self.frames[self.anim_index]
        self.gif_label.configure(image=frame)
        self.anim_index = (self.anim_index + 1) % len(self.frames)
        self.after(100, self.animate)

    def close(self):
        self.destroy()