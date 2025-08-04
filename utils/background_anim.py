import tkinter as tk
from PIL import Image, ImageTk, ImageFilter

class BackgroundAnimator:
    def __init__(self, canvas, image_path, blur_radius=5, alpha_factor=0.5, speed=0.5, amplitude=20, interval=50):
        """
        canvas: tk.Canvas donde dibujar
        image_path: ruta de la imagen de fondo
        blur_radius: radio de desenfoque
        alpha_factor: transparencia (0.0 a 1.0)
        speed: píxeles de movimiento por frame (más alto = más rápido)
        amplitude: desplazamiento máximo vertical en píxeles
        interval: tiempo en ms entre frames
        """
        self.canvas = canvas
        # Carga y procesa la imagen original
        img = Image.open(image_path).convert("RGBA")
        img = img.filter(ImageFilter.GaussianBlur(blur_radius))
        r, g, b, a = img.split()
        a = a.point(lambda p: int(p * alpha_factor))
        img.putalpha(a)

        # Obtén tamaño del canvas y agranda altura para cubrir movimiento
        width = int(canvas['width'])
        height = int(canvas['height'])
        total_height = height + amplitude * 2
        img = img.resize((width, total_height), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(img)

        # Parámetros de animación
        # Inicia centrado verticalmente con margen de amplitude
        self.x = 0
        self.y = -amplitude
        self.speed = speed
        self.amplitude = amplitude
        self.interval = interval
        self.direction = 1  # 1: hacia abajo, -1: hacia arriba

        # Dibuja imagen en canvas
        self.image_id = canvas.create_image(self.x, self.y, image=self.tk_image, anchor="nw")

    def animate(self):
        # Movimiento entre -amplitude y +0 (cubriendo full)
        self.y += self.speed * self.direction
        if self.y >= 0:
            self.y = 0
            self.direction = -1
        elif self.y <= -self.amplitude:
            self.y = -self.amplitude
            self.direction = 1
        # Actualiza posición
        self.canvas.coords(self.image_id, self.x, self.y)
        # Próximo frame
        self.canvas.after(self.interval, self.animate)

    def start(self):
        # Inicia animación
        self.canvas.after(self.interval, self.animate)