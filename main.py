import tkinter as tk
from tkinter import messagebox
import pygame
import os
from utils.background_anim import BackgroundAnimator
from views.loading_view import LoadingView
from db import get_connection
from utils.asistente import AsistenteGUI

class App(tk.Tk):
    def __init__(self, bg_image, music_folder, loading_gif):
        super().__init__()

        self.title("App Modular")
        self.geometry("800x500")
        self.resizable(False, False)

        try:
            self.iconphoto(False, tk.PhotoImage(file="uploads/logo.png"))
        except Exception as e:
            print("No se pudo cargar el ícono:", e)

        self.loading_gif = loading_gif
        self.loading_duration = 800

        pygame.init()
        pygame.display.set_mode((1, 1))
        pygame.mixer.init()
        self.music_files = [os.path.join(music_folder, f)
                            for f in os.listdir(music_folder)
                            if f.lower().endswith(('.mp3', '.wav'))]
        self.current_track = 0
        self.play_music()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        self.bind("<Any-KeyPress>", self.check_music_event)
        self.check_music_event()

        self.canvas = tk.Canvas(self, width=800, height=500, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.bg_anim = BackgroundAnimator(self.canvas, bg_image)
        self.bg_anim.start()

        # Crear asistente
        self.asistente = AsistenteGUI(self)

        # Crear burbuja asistente movible y siempre visible
        self._crear_burbuja_movable()

        self.after(100, lambda: LoadingView.show(self, self.loading_gif, duration=1500))
        self.after(1600, self.show_login)

    def _crear_burbuja_movable(self):
        # Botón burbuja asistente
        self.burbuja_btn = tk.Button(
            self,
            text="🤖",
            font=("Arial", 16, "bold"),
            bg="#5C9DBF",
            fg="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.asistente.toggle_asistente  # Abrir/cerrar asistente
        )
        # Posición inicial (abajo a la derecha)
        self.burbuja_btn.place(x=750, y=450, width=44, height=44)

        # Variables para arrastrar la burbuja
        self._drag_data = {"x": 0, "y": 0}

        # Eventos para mover burbuja con mouse
        self.burbuja_btn.bind("<ButtonPress-1>", self._inicio_arrastre)
        self.burbuja_btn.bind("<B1-Motion>", self._arrastrar_burbuja)
        self.burbuja_btn.bind("<ButtonRelease-1>", self._fin_arrastre)

    def _inicio_arrastre(self, event):
        # Guardar posición inicial del cursor cuando empieza a arrastrar
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _arrastrar_burbuja(self, event):
        # Calcular nueva posición de la burbuja
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]

        x = self.burbuja_btn.winfo_x() + dx
        y = self.burbuja_btn.winfo_y() + dy

        # Limitar que no salga de la ventana
        x = max(0, min(x, self.winfo_width() - self.burbuja_btn.winfo_width()))
        y = max(0, min(y, self.winfo_height() - self.burbuja_btn.winfo_height()))

        self.burbuja_btn.place(x=x, y=y)

    def _fin_arrastre(self, event):
        # Cuando se suelta el mouse ya no hace nada, pero podría guardar posición si quieres
        pass

    # --- El resto de tus métodos existentes siguen igual ---
    def play_music(self):
        if not self.music_files:
            return
        pygame.mixer.music.load(self.music_files[self.current_track])
        pygame.mixer.music.play()

    def check_music_event(self, event=None):
        for e in pygame.event.get():
            if e.type == pygame.USEREVENT:
                self.current_track = (self.current_track + 1) % len(self.music_files)
                self.play_music()
        self.after(1000, self.check_music_event)

    def clear_ui(self):
        self.canvas.delete("ui")

    def show_login(self):
        self.clear_ui()
        self.title("Inicio de sesión")
        self.geometry("800x500")

        frame_logo = tk.Frame(self.canvas.master, bd=0, width=300,
                              relief=tk.SOLID, padx=10, pady=10, bg='#3a7ff6')
        self.canvas.create_window(0, 0, anchor='nw', window=frame_logo, width=300, height=500)
        try:
            from utils.generic import leer_imagen
            logo_img = leer_imagen("uploads/logo.png", (200, 200))
            lbl_logo = tk.Label(frame_logo, image=logo_img, bg='#3a7ff6')
            lbl_logo.image = logo_img
            lbl_logo.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error cargando logo: {e}")

        frame_form = tk.Frame(self.canvas.master, bd=0, relief=tk.SOLID, bg='#fcfcfc')
        self.canvas.create_window(300, 0, anchor='nw', window=frame_form, width=500, height=500)

        frame_form_top = tk.Frame(frame_form, height=100, bd=0, bg='#fcfcfc')
        frame_form_top.pack(side="top", fill="x")
        lbl_title = tk.Label(frame_form_top, text="Inicio de sesión",
                             font=('Times', 30), fg="#666a88", bg='#fcfcfc', pady=20)
        lbl_title.pack(expand=True, fill="both")

        frame_form_fill = tk.Frame(frame_form, bd=0, bg='#fcfcfc')
        frame_form_fill.pack(side="top", fill="both", expand=True)

        tk.Label(frame_form_fill, text="Usuario", font=('Times', 14),
                 fg="#666a88", bg='#fcfcfc', anchor="w").pack(fill=tk.X, padx=20, pady=5)
        ent_u = tk.Entry(frame_form_fill, font=('Times', 14))
        ent_u.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(frame_form_fill, text="Contraseña", font=('Times', 14),
                 fg="#666a88", bg='#fcfcfc', anchor="w").pack(fill=tk.X, padx=20, pady=5)
        ent_p = tk.Entry(frame_form_fill, font=('Times', 14), show="*")
        ent_p.pack(fill=tk.X, padx=20, pady=10)

        btn_login = tk.Button(frame_form_fill, text="Iniciar sesión",
                              font=('Times', 15), bg='#3a7ff6', fg="#fff", bd=0,
                              command=lambda: self._with_loading(lambda:
                                  self._attempt_login(ent_u.get().strip(), ent_p.get().strip())))
        btn_login.pack(fill=tk.X, padx=20, pady=(20,10))
        btn_login.bind("<Return>", lambda e: self._attempt_login(ent_u.get().strip(), ent_p.get().strip()))
        ent_p.bind("<Return>", lambda e: self._attempt_login(ent_u.get().strip(), ent_p.get().strip()))
        ent_u.bind("<Return>", lambda e: self._attempt_login(ent_u.get().strip(), ent_p.get().strip()))

        btn_reg = tk.Button(frame_form_fill, text="Registrar usuario",
                            font=('Times', 15), bg='#fcfcfc', fg="#3a7ff6", bd=0,
                            command=lambda: self._with_loading(self.show_register))
        btn_reg.pack(fill=tk.X, padx=20, pady=(0,20))
        btn_reg.bind("<Return>", lambda e: self.show_register())
        self._crear_burbuja_movable()


    def show_register(self):
        self.clear_ui()
        self.title("Registro de usuario")
        self.geometry("800x500")

        frame_logo = tk.Frame(self.canvas.master, bd=0, width=300,
                              relief=tk.SOLID, padx=10, pady=10, bg='#3a7ff6')
        self.canvas.create_window(0, 0, anchor='nw', window=frame_logo, width=300, height=500)
        try:
            from utils.generic import leer_imagen
            logo_img = leer_imagen("uploads/logo.png", (200, 200))
            lbl_logo = tk.Label(frame_logo, image=logo_img, bg='#3a7ff6')
            lbl_logo.image = logo_img
            lbl_logo.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error cargando logo: {e}")

        frame_form = tk.Frame(self.canvas.master, bd=0, relief=tk.SOLID, bg='#fcfcfc')
        self.canvas.create_window(300, 0, anchor='nw', window=frame_form, width=500, height=500)

        frame_form_top = tk.Frame(frame_form, height=100, bd=0, bg='#fcfcfc')
        frame_form_top.pack(side="top", fill="x")
        lbl_title = tk.Label(frame_form_top, text="Registro de usuario",
                             font=('Times', 30), fg="#666a88", bg='#fcfcfc', pady=20)
        lbl_title.pack(expand=True, fill="both")

        frame_form_fill = tk.Frame(frame_form, bd=0, bg='#fcfcfc')
        frame_form_fill.pack(side="top", fill="both", expand=True)

        tk.Label(frame_form_fill, text="Nuevo Usuario", font=('Times', 14),
                 fg="#666a88", bg='#fcfcfc', anchor="w").pack(fill=tk.X, padx=20, pady=5)
        ent_u = tk.Entry(frame_form_fill, font=('Times', 14))
        ent_u.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(frame_form_fill, text="Nueva Contraseña", font=('Times', 14),
                 fg="#666a88", bg='#fcfcfc', anchor="w").pack(fill=tk.X, padx=20, pady=5)
        ent_p = tk.Entry(frame_form_fill, font=('Times', 14), show="*")
        ent_p.pack(fill=tk.X, padx=20, pady=10)

        btn_reg = tk.Button(frame_form_fill, text="Registrar",
                            font=('Times', 15), bg='#3a7ff6', fg="#fff", bd=0,
                            command=lambda: self._with_loading(lambda:
                                self._register_user(ent_u.get().strip(), ent_p.get().strip())))
        btn_reg.pack(fill=tk.X, padx=20, pady=(20,10))

        btn_back = tk.Button(frame_form_fill, text="Volver a Login",
                             font=('Times', 15), bg='#fcfcfc', fg="#3a7ff6", bd=0,
                             command=lambda: self._with_loading(self.show_login))
        btn_back.pack(fill=tk.X, padx=20, pady=(0,20))
        self._crear_burbuja_movable()
        

    def _with_loading(self, action):
        LoadingView.show(self, self.loading_gif, duration=self.loading_duration)
        self.after(self.loading_duration, action)

    def _attempt_login(self, user, pwd):
        if not user:
            messagebox.showerror("Error", "El campo Usuario no puede estar vacío")
            return
        if not pwd:
            messagebox.showerror("Error", "El campo Contraseña no puede estar vacío")
            return

        conn = get_connection()
        if conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM usuarios WHERE usuario=%s AND contraseña=%s",
                (user, pwd)
            )
            if cur.fetchone()[0] == 1:
                self.show_dashboard()
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            conn.close()
        else:
            messagebox.showerror("Error", "No hay conexión con la base de datos")

    def _register_user(self, user, pwd):
        if not user:
            messagebox.showerror("Error", "El campo Usuario no puede estar vacío")
            return
        if not pwd:
            messagebox.showerror("Error", "El campo Contraseña no puede estar vacío")
            return

        conn = get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO usuarios (usuario, contraseña) VALUES (%s, %s)",
                    (user, pwd)
                )
                conn.commit()
                messagebox.showinfo("Éxito", "Usuario registrado correctamente")
                self.show_login()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo registrar: {e}")
            finally:
                conn.close()
        else:
            messagebox.showerror("Error", "No hay conexión con la base de datos")

    def show_dashboard(self):
        self.destroy()
        import views.dashboard_view
        views.dashboard_view.launch_dashboard()

if __name__ == "__main__":
    bg_path = "uploads/fondo.png"
    music_folder = "uploads/music"
    loading_gif = "uploads/loading.gif"
    app = App(bg_path, music_folder, loading_gif)
    app.mainloop()
