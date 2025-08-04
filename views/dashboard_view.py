import tkinter as tk
from tkinter import filedialog, messagebox, font
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from utils.background_anim import BackgroundAnimator
from views.loading_view import LoadingView
from db import get_connection
import utils.util_ventana as util_ventana
from config import COLOR_BARRA_SUPERIOR, COLOR_MENU_LATERAL, COLOR_CUERPO_PRINCIPAL, COLOR_MENU_CURSOR_ENCIMA
from utils.asistente import AsistenteGUI

MODELS = {
    'Regresión Lineal': LinearRegression,
    'Regresión Logística': LogisticRegression,
    'K-Means': KMeans,
    'Árbol de Decisión Clasificación': DecisionTreeClassifier,
    'Árbol de Decisión Regresión': DecisionTreeRegressor,
    'SVM': SVC,
    'Red Neuronal (MLP)': lambda: MLPClassifier(max_iter=1000),
}

class DashboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        try:
            logo = tk.PhotoImage(file='uploads/fondo.png')
            self.iconphoto(False, logo)
        except:
            pass
        self.title('Gestión Predictiva')
        self.fullscreen = False
        self._config_window()
        self._create_panels()
        self._create_topbar()
        self._create_sidebar()
        self.asistente = AsistenteGUI(self)
        self.burbuja_btn = tk.Button(
            self,
            text="🤖",
            font=("Arial", 16, "bold"),
            bg="#5C9DBF",
            fg="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.asistente.toggle_asistente
        )
        self.burbuja_btn.place(x=750, y=450, width=44, height=44)
        self._drag_data = {"x": 0, "y": 0}
        self.burbuja_btn.bind("<ButtonPress-1>", self._inicio_arrastre)
        self.burbuja_btn.bind("<B1-Motion>", self._arrastrar_burbuja)
        self._create_main_area()
        self.selected_model = None
        self.model_buttons = {}
        self.data = {'df': None, 'model': None, 'X': None, 'y': None, 'from_mysql': False}
        self._add_model_buttons()
        self.protocol('WM_DELETE_WINDOW', self.on_close)

    def _config_window(self):
        util_ventana.centrar_ventana(self, 1024, 768)
        self.resizable(False, False)

    def _create_panels(self):
        self.topbar = tk.Frame(self, bg=COLOR_BARRA_SUPERIOR, height=60)
        self.topbar.pack(side='top', fill='x')
        self.sidebar = tk.Frame(self, bg=COLOR_MENU_LATERAL, width=280)
        self.sidebar.pack(side='left', fill='y')
        self.main_area = tk.Frame(self, bg=COLOR_CUERPO_PRINCIPAL)
        self.main_area.pack(side='right', fill='both', expand=True)
        
    def _inicio_arrastre(self, event):
        self._drag_data['x'] = event.x
        self._drag_data['y'] = event.y

    def _arrastrar_burbuja(self, event):
        dx = event.x - self._drag_data['x']
        dy = event.y - self._drag_data['y']
        x = self.burbuja_btn.winfo_x() + dx
        y = self.burbuja_btn.winfo_y() + dy
        x = max(0, min(x, self.winfo_width() - self.burbuja_btn.winfo_width()))
        y = max(0, min(y, self.winfo_height() - self.burbuja_btn.winfo_height()))
        self.burbuja_btn.place(x=x, y=y)

    def _create_topbar(self):
        fa = font.Font(family='FontAwesome', size=18)
        tk.Label(self.topbar, text='4C Predictivo', fg='white', bg=COLOR_BARRA_SUPERIOR, font=('Roboto', 20)).pack(side='left', padx=20)
        tk.Button(self.topbar, text='', font=fa, bd=0, bg=COLOR_BARRA_SUPERIOR, fg='white', command=self._toggle_sidebar).pack(side='left', padx=5)
        tk.Button(self.topbar, text='', font=fa, bd=0, bg=COLOR_BARRA_SUPERIOR, fg='white', command=self._toggle_fullscreen).pack(side='left', padx=5)
        tk.Button(self.topbar, text='', font=fa, bd=0, bg=COLOR_BARRA_SUPERIOR, fg='white', command=self.destroy).pack(side='right', padx=20)
        tk.Label(self.topbar, text='erick.arce@codeec.net', fg='white', bg=COLOR_BARRA_SUPERIOR, font=('Roboto', 14)).pack(side='right', padx=20)

    def _create_sidebar(self):
        opts = {'bd': 0, 'bg': COLOR_MENU_LATERAL, 'fg': 'white', 'anchor': 'w', 'font': ('Roboto', 12), 'height': 1}
        tk.Button(self.sidebar, text='📁  Cargar Datos', command=lambda: self._with_loading(self.load_file), **opts).pack(fill='x', padx=20, pady=8)
        tk.Button(self.sidebar, text='🛢️  Cargar MySQL', command=lambda: self._with_loading(self.load_mysql), **opts).pack(fill='x', padx=20, pady=8)
        self.run_btn = tk.Button(self.sidebar, text='▶️  Ejecutar Modelo', command=lambda: self._with_loading(self.run_model), **opts)
        self.run_btn.pack(fill='x', padx=20, pady=(8, 12))

        self.model_frame = tk.Frame(self.sidebar, bg=COLOR_MENU_LATERAL)
        self.model_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def _add_model_buttons(self):
        for name in MODELS:
            btn = tk.Button(self.model_frame, text=f'   {name}', bd=0, bg=COLOR_MENU_LATERAL, fg='white', anchor='w', font=('Roboto', 11), height=1,
                            command=lambda n=name: self._with_loading(lambda: self._select_model(n)))
            btn.pack(fill='x', padx=10, pady=2)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=COLOR_MENU_CURSOR_ENCIMA))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=COLOR_MENU_CURSOR_ENCIMA if b['text'].strip() == self.selected_model else COLOR_MENU_LATERAL))
            self.model_buttons[name] = btn

    def _create_main_area(self):
        canvas = tk.Canvas(self.main_area, bg=COLOR_CUERPO_PRINCIPAL)
        canvas.pack(fill='both', expand=True)
        self.bg_anim = BackgroundAnimator(canvas, 'uploads/fondo.png'); self.bg_anim.start()
        self.fig, self.ax = plt.subplots(figsize=(7, 4.4))  # Ajuste aquí (altura de 5 a 4.4)
        self.chart = FigureCanvasTkAgg(self.fig, master=canvas)
        self.chart.get_tk_widget().place(relx=0.05, rely=0.1, relwidth=0.9, relheight=0.6)
        self.log_box = tk.Text(canvas, font=('Roboto', 12), height=8)
        self.log_box.place(relx=0.05, rely=0.72, relwidth=0.9)

    def _with_loading(self, func):
        LoadingView.show(self, 'uploads/loading.gif', duration=500)
        self.after(500, func)

    def _select_model(self, name):
        self.selected_model = name
        for n, btn in self.model_buttons.items():
            btn.config(bg=COLOR_MENU_CURSOR_ENCIMA if n == name else COLOR_MENU_LATERAL)
        self._log(f'Modelo seleccionado: {name}')

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[('Excel', '*.xlsx'), ('CSV', '*.csv')])
        if not path: return
        df = pd.read_excel(path) if path.endswith('.xlsx') else pd.read_csv(path)
        for col in df.select_dtypes(['object', 'category']):
            df[col] = df[col].astype('category').cat.codes
        self.data['df'] = df
        self.data['from_mysql'] = False
        self._log(f'Datos cargados: {df.shape[0]} filas x {df.shape[1]} cols')
        self.ax.clear(); self.chart.draw()

    def load_mysql(self):
        conn = get_connection()
        query = """
            SELECT edad,
                   CASE genero WHEN 'M' THEN 0 WHEN 'F' THEN 1 ELSE NULL END AS genero,
                   ingreso
            FROM personas
        """
        df = pd.read_sql(query, conn)
        conn.close()
        self.data['df'] = df
        self.data['from_mysql'] = True
        self._log(f'Datos MySQL: {df.shape[0]} filas x {df.shape[1]} cols')
        self.ax.clear(); self.chart.draw()

    def run_model(self):
        df = self.data.get('df')
        if df is None:
            return messagebox.showwarning('Sin datos', 'Carga datos primero')
        if not self.selected_model:
            return messagebox.showwarning('Sin modelo', 'Selecciona un modelo')

        num_df = df.select_dtypes(include=[np.number])
        if num_df.shape[1] < 1:
            return messagebox.showerror('Error', 'No hay columnas numéricas')
        if num_df.shape[1] == 1:
            y = num_df.iloc[:, 0].values
            X = np.arange(len(y)).reshape(-1, 1)
        else:
            X = num_df.iloc[:, :-1].values
            y = num_df.iloc[:, -1].values

        ModelClass = MODELS[self.selected_model]
        model = ModelClass()
        if self.selected_model == 'K-Means':
            model = ModelClass(n_clusters=min(4, len(X)))
            model.fit(X)
        else:
            model.fit(X, y)

        self.data.update({'model': model, 'X': X, 'y': y})
        self._log('Modelo entrenado')
        if hasattr(model, 'score') and self.selected_model != 'K-Means':
            self._log(f"Score: {model.score(X, y):.3f}")
        self._draw_plot(model, X, y)

    def _draw_plot(self, model, X, y):
        self.ax.clear()
        name = self.selected_model
        if name == 'Regresión Lineal':
            y_pred = model.predict(X)
            self.ax.scatter(y, y_pred)
            self.ax.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
            self.ax.set_xlabel('Valor Real')
            self.ax.set_ylabel('Valor Predicho')
        else:
            pred = model.predict(X)
            vals, counts = np.unique(pred, return_counts=True)
            self.ax.bar(vals.astype(str), counts)
            self.ax.set_xlabel('Clases o Categorías')
            self.ax.set_ylabel('Frecuencia')
            rotation_angle = 45 if self.data.get('from_mysql') else 0
            font_size = 8 if self.data.get('from_mysql') else 10  # ← Nuevo ajuste
            self.ax.tick_params(axis='x', rotation=rotation_angle, labelsize=font_size)  # ← Aplicado aquí
        self.ax.set_title(f'Resultado del modelo: {name}')
        self.chart.draw()

    def _toggle_sidebar(self):
        if self.sidebar.winfo_ismapped():
            self.sidebar.pack_forget()
        else:
            self.sidebar.pack(side='left', fill='y')

    def _toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.attributes('-fullscreen', self.fullscreen)

    def _log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    def on_close(self):
        try:
            self.bg_anim.stop()
        except:
            pass
        self.destroy()

def launch_dashboard():
    
    app = DashboardApp()
    app.mainloop()
