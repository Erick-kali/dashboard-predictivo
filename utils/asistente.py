import tkinter as tk
import difflib
import requests
import unicodedata
import os
import json
from PIL import Image, ImageTk
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from tkinter import messagebox

MODELS = {
    'Regresión Lineal': LinearRegression,
    'Regresión Logística': LogisticRegression,
    'K-Means': KMeans,
    'Árbol de Decisión Clasificación': DecisionTreeClassifier,
    'Árbol de Decisión Regresión': DecisionTreeRegressor,
    'SVM': SVC,
    'Red Neuronal (MLP)': lambda: MLPClassifier(max_iter=1000),
}

MODELO_EXPLICACIONES = {
    'Regresión Lineal': 'La Regresión Lineal se usa para predecir valores numéricos continuos a partir de variables independientes. Ajusta una línea que minimiza la suma de errores cuadrados.',
    'Regresión Logística': 'La Regresión Logística se utiliza para problemas de clasificación binaria. Estima la probabilidad de pertenecer a una clase mediante una función logística.',
    'K-Means': 'K-Means es un algoritmo de agrupamiento no supervisado que divide los datos en K grupos según similitudes, iterando para minimizar la distancia intra-grupo.',
    'Árbol de Decisión Clasificación': 'Este modelo crea reglas de decisión para clasificar datos en categorías, dividiendo recursivamente según características que mejor separan las clases.',
    'Árbol de Decisión Regresión': 'Similar al árbol de clasificación, pero para predecir valores continuos en lugar de categorías.',
    'SVM': 'Las Máquinas de Vectores de Soporte (SVM) buscan un hiperplano que separa las clases con el mayor margen posible, útil para clasificación y regresión.',
    'Red Neuronal (MLP)': 'La Red Neuronal Perceptrón Multicapa (MLP) es un modelo inspirado en redes neuronales biológicas capaz de aprender patrones complejos para clasificación y regresión.',
}

KEYWORDS = {
    'registro': ['registrar', 'registro', 'registro usuario', 'crear cuenta', 'sign up'],
    'modelos': ['modelo', 'modelos', 'machine learning', 'ml', 'regresión', 'clasificación', 'k-means', 'árbol', 'svm', 'red neuronal', 'mlp'],
    'explicacion_modelos': ['qué hace', 'funciona', 'para qué', 'explicar modelo', 'descripción modelo', 'qué es', 'para que sirve', 'detalles'],
    'subir_datos': ['subir datos', 'cargar datos', 'importar datos', 'subir archivo', 'importar archivo', 'csv'],
    'cancion': ['canción', 'musica', 'música', 'song', 'playlist', 'audio'],
    'ingreso': ['ingresar', 'login', 'entrar', 'inicio sesión', 'iniciar sesión', 'acceder'],
    'contraseña': ['contraseña', 'clave', 'recuperar contraseña', 'olvidé contraseña', 'forgot password'],
    'graficas': ['gráfica', 'grafica', 'gráfico', 'grafico', 'eje', 'ejes', 'punto', 'puntos', 'chart', 'plot'],
    'bd': ['mysql', 'base de datos', 'bd', 'database'],
    'agradecimiento': ['gracias', 'thank you', 'thx'],
    'erick': ['quien es el mejor programador', 'rey de la programación', 'the king', 'mejor', 'rey'],
}

def normaliza(texto):
    texto = texto or ""
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ASCII', 'ignore').decode('utf-8')
    return texto.lower().strip()

def distancia_levenshtein(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).ratio()

class ElegantToggle(tk.Frame):
    def __init__(self, master, text, icon_on, icon_off, callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.callback = callback
        self.state = False
        self.icon_on = icon_on
        self.icon_off = icon_off
        self.btn = tk.Button(self, text=f"{icon_off} {text} OFF", bg='#b0b0b0', fg='black',
                             font=("Helvetica", 10, "bold"),
                             relief="flat", padx=10, pady=6, command=self.toggle)
        self.btn.pack()
    def toggle(self):
        self.state = not self.state
        if self.state:
            self.btn.config(bg='#4caf50', fg='white',
                           text=f"{self.icon_on} {self.btn.cget('text').split(' ')[1]} ON")
        else:
            self.btn.config(bg='#b0b0b0', fg='black',
                           text=f"{self.icon_off} {self.btn.cget('text').split(' ')[1]} OFF")
        self.callback(self.state)
    def set_state(self, value):
        if value != self.state:
            self.toggle()
    def get_state(self):
        return self.state

class AsistenteGUI:
    def __init__(self, master):
        self.master = master
        self.ventana = None
        self.avatar_asistente_img = None
        self.avatar_usuario_img = None
        self.avatar_asistente = '🤖'
        self.avatar_usuario = '🧑'
        self.modo = "conocimiento"
        self.aprendizaje_estado = "normal"
        self.aprendizaje_temp_pregunta = ""
        self.base_aprendizaje = {}
        self._cargar_aprendizaje_local()
        self.comandos_abrir = ['abrir', 'abre', 'abrirme', 'ingresar', 'acceder']
        self.comandos_tipo = {}
        if hasattr(master, 'show_login'):
            self.comandos_tipo['login'] = master.show_login
        if hasattr(master, 'show_register'):
            self.comandos_tipo['registro'] = master.show_register
            self.comandos_tipo['register'] = master.show_register
        self.comandos_tipo['dashboard'] = self._solicitar_login

    def set_avatar_asistente(self, path):
        img = Image.open(path).resize((50, 50))
        self.avatar_asistente_img = ImageTk.PhotoImage(img)

    def set_avatar_usuario(self, path):
        img = Image.open(path).resize((50, 50))
        self.avatar_usuario_img = ImageTk.PhotoImage(img)

    def toggle_asistente(self):
        if self.ventana and self.ventana.winfo_exists():
            self.ventana.destroy()
            self.ventana = None
        else:
            self._mostrar_chat()

    def _mostrar_chat(self):
        self.ventana = tk.Toplevel(self.master)
        self.ventana.title('Asistente IA')
        self.ventana.geometry('900x650')
        self.ventana.configure(bg='#eceff1')
        self.ventana.transient(self.master)
        container = tk.Frame(self.ventana, bg='#eceff1')
        container.pack(fill='both', expand=True, padx=10, pady=10)
        canvas = tk.Canvas(container, bg='#eceff1', highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient='vertical', command=canvas.yview)
        self.messages_frame = tk.Frame(canvas, bg='#eceff1')
        self.messages_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=self.messages_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), 'units'))
        toggle_row = tk.Frame(self.ventana, bg='#eceff1')
        toggle_row.pack(fill='x', pady=(0, 10))
        self.google_toggle = ElegantToggle(toggle_row, "Busqueda Google", "🌐", "🌐", self._on_toggle_google)
        self.google_toggle.pack(side='left', padx=10)
        self.conocimiento_toggle = ElegantToggle(toggle_row, "Conocimiento", "📚", "📚", self._on_toggle_conocimiento)
        self.conocimiento_toggle.pack(side='left', padx=10)
        self.aprendizaje_toggle = ElegantToggle(toggle_row, "Aprendizaje", "🧠", "🧠", self._on_toggle_aprendizaje)
        self.aprendizaje_toggle.pack(side='left', padx=10)
        self.conocimiento_toggle.set_state(True)
        entry_frame = tk.Frame(self.ventana, bg='#cfd8dc', pady=10)
        entry_frame.pack(fill='x')
        self.entry = tk.Entry(entry_frame, font=('Helvetica', 14), bd=0, relief='flat')
        self.entry.pack(side='left', fill='x', expand=True, padx=(10, 0))
        send_btn = tk.Button(entry_frame, text='Enviar', font=('Helvetica', 12), bg='#37474f', fg='white', bd=0, command=self._procesar_input)
        send_btn.pack(side='right', padx=10)
        self.entry.focus()
        self.entry.bind('<Return>', self._procesar_input)
        self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, 'Asistente IA', 'Hola, ¿en qué te puedo ayudar?', 'izquierda')

    def _on_toggle_google(self, state):
        if state:
            self.modo = "google"
            self.conocimiento_toggle.set_state(False)
            self.aprendizaje_toggle.set_state(False)
            self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, "Asistente", "🌐 Modo Google activado. Solo responderé usando Google.", "izquierda")
        else:
            if not self.conocimiento_toggle.get_state() and not self.aprendizaje_toggle.get_state():
                self.conocimiento_toggle.set_state(True)

    def _on_toggle_conocimiento(self, state):
        if state:
            self.modo = "conocimiento"
            self.google_toggle.set_state(False)
            self.aprendizaje_toggle.set_state(False)
            self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, "Asistente", "📚 Modo conocimiento activado. Solo responderé con mi base local.", "izquierda")
        else:
            if not self.google_toggle.get_state() and not self.aprendizaje_toggle.get_state():
                self.google_toggle.set_state(True)

    def _on_toggle_aprendizaje(self, state):
        if state:
            self.modo = "aprendizaje"
            self.google_toggle.set_state(False)
            self.conocimiento_toggle.set_state(False)
            self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, "Asistente", "🧠 Modo aprendizaje activado.", "izquierda")
        else:
            if not self.google_toggle.get_state() and not self.conocimiento_toggle.get_state():
                self.conocimiento_toggle.set_state(True)
        self.aprendizaje_estado = "normal"

    def _agregar_mensaje(self, avatar, nombre, texto, lado):
        cont = tk.Frame(self.messages_frame, bg='#eceff1')
        cont.pack(anchor='w' if lado == 'izquierda' else 'e', pady=5,
                  padx=(20, 200) if lado == 'izquierda' else (200, 20))
        avatar_lbl = tk.Label(cont, bg='#eceff1')
        if isinstance(avatar, ImageTk.PhotoImage):
            avatar_lbl.configure(image=avatar)
        else:
            avatar_lbl.configure(text=avatar, font=('Helvetica', 20))
        avatar_lbl.pack(side='left' if lado == 'izquierda' else 'right')
        bubble_bg = '#bbdefb' if lado == 'izquierda' else '#c8e6c9'
        txt = f"{nombre}\n{texto}"
        lbl = tk.Label(cont, text=txt, font=('Helvetica', 12), justify='left', wraplength=400,
                       bg=bubble_bg, padx=12, pady=8, bd=0)
        lbl.pack(side='left' if lado == 'izquierda' else 'right')

    def _buscar_mejor_coincidencia(self, msg):
        msgl = normaliza(msg)
        palabras_usuario = msgl.split()

        # 1. Aprendizaje personalizado exacto o casi exacto
        for pregunta, respuesta in self.base_aprendizaje.items():
            if msgl == pregunta or distancia_levenshtein(msgl, pregunta) > 0.93:
                return ("aprendizaje", pregunta, respuesta, 1.0)
        # 2. Coincidencia exacta en modelos
        for modelo in MODELO_EXPLICACIONES:
            if msgl == normaliza(modelo):
                return ("modelo", modelo, MODELO_EXPLICACIONES[modelo], 1.0)
        # 3. Coincidencia por inclusión directa de keyword en el mensaje
        for cat, palabras in KEYWORDS.items():
            for palabra in palabras:
                palabra_norm = normaliza(palabra)
                if palabra_norm in msgl:
                    return ("keyword_contains", cat, palabra, 1.0)
        # 4. Fuzzy por palabra: si alguna palabra del usuario es muy parecida a una keyword
        for cat, palabras in KEYWORDS.items():
            for palabra in palabras:
                palabra_norm = normaliza(palabra)
                for pu in palabras_usuario:
                    if distancia_levenshtein(pu, palabra_norm) > 0.8:
                        return ("keyword_fuzzy", cat, palabra, 0.9)
        # 5. Fuzzy en modelos si todo el mensaje es muy parecido al nombre
        mejor_modelo, mejor_score = None, 0
        for modelo in MODELO_EXPLICACIONES:
            modelo_norm = normaliza(modelo)
            score = distancia_levenshtein(msgl, modelo_norm)
            if score > mejor_score:
                mejor_modelo, mejor_score = modelo, score
        if mejor_score > 0.8:
            return ("modelo", mejor_modelo, MODELO_EXPLICACIONES[mejor_modelo], mejor_score)
        return (None, None, None, 0)

    def _procesar_input(self, event=None):
        msg = self.entry.get().strip()
        if not msg: return
        cmd = normaliza(msg)
        for key, action in self.comandos_tipo.items():
            if key in cmd and any(op in cmd for op in self.comandos_abrir):
                self._agregar_mensaje(self.avatar_asistente, 'Asistente IA', f"Abriendo {key}...", 'izquierda')
                if self.ventana:
                    self.ventana.destroy()
                action()
                return
        self._agregar_mensaje(self.avatar_usuario_img or self.avatar_usuario, 'Tú', msg, 'derecha')
        self.entry.delete(0, 'end')

        # Modo Google
        if self.modo == "google":
            respuesta = self._realizar_busqueda_google(msg)
            if respuesta:
                self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, 'Asistente', respuesta, "izquierda")
            else:
                self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, 'Asistente', "No encontré información en Google.", "izquierda")
            return

        # Modo aprendizaje
        if self.modo == "aprendizaje":
            if self.aprendizaje_estado == "esperando_pregunta":
                self.aprendizaje_temp_pregunta = normaliza(msg)
                self.aprendizaje_estado = "esperando_respuesta"
                self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, 'Asistente',
                                      "¿Cuál es la respuesta que debo aprender para esta pregunta?", "izquierda")
                return
            elif self.aprendizaje_estado == "esperando_respuesta":
                pregunta = self.aprendizaje_temp_pregunta
                respuesta = msg.strip()
                if pregunta and respuesta:
                    self.base_aprendizaje[pregunta] = respuesta
                    self._guardar_aprendizaje_local()
                    self.aprendizaje_estado = "normal"
                    self.aprendizaje_temp_pregunta = ""
                    self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, 'Asistente',
                                          "He aprendido con éxito. Si me haces esa pregunta, te responderé lo aprendido.", "izquierda")
                else:
                    self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, 'Asistente',
                                          "No entendí la pregunta o la respuesta, inténtalo de nuevo.", "izquierda")
                return
            elif cmd == "/aprender":
                self.aprendizaje_estado = "esperando_pregunta"
                self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, 'Asistente',
                                      "¿Qué pregunta quieres que aprenda? Escríbela exactamente como la harías.", "izquierda")
                return
            # Si ya aprendió
            msgl = normaliza(msg)
            for pregunta, respuesta in self.base_aprendizaje.items():
                if msgl == pregunta or distancia_levenshtein(msgl, pregunta) > 0.93:
                    self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, 'Asistente', respuesta, "izquierda")
                    return
            self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, 'Asistente', "No conozco esa información. Puedes usar /aprender para enseñarme.", "izquierda")
            return

        # Modo conocimiento (analiza SIEMPRE el mensaje actual, responde directo)
        tipo, clave, valor, score = self._buscar_mejor_coincidencia(msg)
        if tipo in ["keyword_contains", "keyword_fuzzy"]:
            self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, 'Asistente', self._respuesta_keyword(clave), "izquierda")
            return
        if score == 1.0 and tipo:
            if tipo == "modelo":
                self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, 'Asistente', valor, "izquierda")
            elif tipo == "keyword":
                self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, 'Asistente', self._respuesta_keyword(clave), "izquierda")
            elif tipo == "aprendizaje":
                self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, 'Asistente', valor, "izquierda")
            return
        if tipo and score > 0.93:
            if tipo == "modelo":
                self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, 'Asistente', valor, "izquierda")
            elif tipo == "keyword":
                self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, 'Asistente', self._respuesta_keyword(clave), "izquierda")
            elif tipo == "aprendizaje":
                self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, 'Asistente', valor, "izquierda")
            return
        self._agregar_mensaje(self.avatar_asistente_img or self.avatar_asistente, 'Asistente', "No conozco esa información.", "izquierda")

    def _respuesta_keyword(self, categoria):
        if categoria == "agradecimiento":
            return "¡De nada! ¿En qué más te puedo ayudar?"
        if categoria == "registro":
            return "anda a registrarse, o pideme abre registro y llenas los campos, es muy facil"
        if categoria == "modelos":
            modelos_disponibles = ", ".join(MODELS.keys())
            return f"¿Te gustaría saber sobre los modelos de machine learning disponibles? Los modelos disponibles son: {modelos_disponibles}."
        if categoria == "explicacion_modelos":
            return "¿Quieres una explicación de algún modelo específico? Dímelo, por ejemplo: 'qué es regresión lineal'."
        if categoria == "subir_datos":
            return "Para subir o importar datos, busca el botón correspondiente o selecciona un archivo CSV."
        if categoria == "cancion":
            return "la cancion se llama, The Perfect Girl x After Dark x Babydoll x Sweater Weather - 1 Hour Loop, es un mix de 1 hora"
        if categoria == "ingreso":
            return "debes registrarte o iniciar sesion, es muy facil"
        if categoria == "contraseña":
            return "¿Olvidaste tu contraseña o necesitas recuperarla? contacta al administrador"
        if categoria == "graficas":
            return "¿Te interesa visualizar datos en gráficas o charts? Puedo orientarte sobre cómo hacerlo."
        if categoria == "bd":
            return "¿Tienes dudas sobre la base de datos (MySQL, BD)? Sirve para cargar los empleados de forma local, y saca grafica sin necesidad de un archivo."
        if categoria == "erick":
            return "¡Erick es considerado el mejor programador y el rey de la programación! 👑"
        return f"Tu mensaje está relacionado con '{categoria}'."

    def _realizar_busqueda_google(self, query):
        try:
            url = f""#poner su propia apikey
            response = requests.get(url)
            results = response.json()
            if 'items' in results:
                snippets = [item.get('snippet', '') for item in results['items'][:3]]
                textos = "\n\n".join(snippets).strip()
                if textos:
                    return textos
            return None
        except Exception:
            return None

    def _solicitar_login(self):
        messagebox.showinfo('Info', 'Debes registrarte o iniciar sesión para acceder al dashboard.')
        self.master.show_login()

    def _guardar_aprendizaje_local(self):
        try:
            with open("asistente_aprendizaje.json", "w", encoding="utf-8") as f:
                json.dump(self.base_aprendizaje, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("No se pudo guardar el aprendizaje local:", e)

    def _cargar_aprendizaje_local(self):
        if os.path.exists("asistente_aprendizaje.json"):
            try:
                with open("asistente_aprendizaje.json", "r", encoding="utf-8") as f:
                    self.base_aprendizaje = json.load(f)
            except Exception as e:
                print("No se pudo cargar el aprendizaje local:", e)
                self.base_aprendizaje = {}

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('900x650')
    root.title('Demo Aplicación con Asistente')
    app = AsistenteGUI(root)
    app.set_avatar_asistente('./avatar.png')
    app.set_avatar_usuario('./user.png')
    root.mainloop()