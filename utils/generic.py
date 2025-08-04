from PIL import Image, ImageTk

# para compatibilidad con versiones nuevas y viejas:
try:
    resample_filter = Image.Resampling.LANCZOS
except AttributeError:
    resample_filter = Image.ANTIALIAS

def leer_imagen(ruta, size=None):
    img = Image.open(ruta)
    if size:
        img = img.resize(size, resample_filter)
    return ImageTk.PhotoImage(img)

def centrar_ventana(ventana, ancho, alto):
    screen_width = ventana.winfo_screenwidth()
    screen_height = ventana.winfo_screenheight()
    x = (screen_width - ancho) // 2
    y = (screen_height - alto) // 2
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
