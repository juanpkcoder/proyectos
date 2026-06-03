import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pandastable import Table
import statsmodels.api as sm
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
 
class ViviendaRegressionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SISTEMA DE PREDICCIÓN INMOBILIARIA - REGRESIÓN MULTIVARIADA")
        self.root.geometry("1200x800")
        
        self.x_cols = ['Area_m2', 'Habitaciones', 'Banos', 'Estrato', 'Antiguedad_Anos', 'Distancia_Centro_km', 'Seguridad_Sector']
        self.y_col = 'Precio_Millones'
        
        self.df = pd.DataFrame()
        self.model = None
        self.setup_styles()
        self.create_widgets()
 
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Header.TFrame', background='#1e3d59')
        style.configure('Action.TButton', font=('Segoe UI', 10, 'bold'), foreground='white', background='#17a2b8')
        style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'), background='#1e3d59', foreground='white')
        style.configure('Predict.TButton', font=('Segoe UI', 11, 'bold'), foreground='white', background='#28a745')
        style.configure('Result.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#1e3d59')
 
    def create_widgets(self):
        # Panel Superior (Header)
        header = ttk.Frame(self.root, style='Header.TFrame', padding=10)
        header.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Label(header, text="🏠 MODELO DE ESTIMACIÓN DE VALORES COMERCIALES", style='Title.TLabel').pack(side=tk.LEFT, padx=20)
        
        # Botonera
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="📂 CARGAR DATOS (CSV)", command=self.load_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="⚙️ EJECUTAR REGRESIÓN", command=self.run_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔗 MATRIZ DE CORRELACIÓN", command=self.show_correlation_matrix).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ LIMPIAR", command=self.reset).pack(side=tk.RIGHT, padx=5)
 
        # Contenedor Principal (PanedWindow)
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
 
        # Lado Izquierdo: Visualización de Tabla
        self.left_frame = ttk.LabelFrame(self.paned, text=" Datos de Viviendas ")
        self.paned.add(self.left_frame, weight=1)
 
        # Lado Derecho: Pestañas de Resultados y Gráficos
        self.right_frame = ttk.Frame(self.paned)
        self.paned.add(self.right_frame, weight=2)
 
        # Consola de Resultados
        self.res_text = tk.Text(self.right_frame, height=12, font=('Consolas', 10), bg='#f8f9fa')
        self.res_text.pack(fill=tk.X, padx=5, pady=5)
 
        # Notebook (pestañas) para los gráficos
        self.notebook = ttk.Notebook(self.right_frame)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
 
        # Pestaña 1: Gráfico de dispersión (regresión)
        self.graph_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.graph_frame, text=" 📈 Precisión del Modelo ")
 
        # Pestaña 2: Matriz de correlación
        self.corr_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.corr_frame, text=" 🔗 Matriz de Correlación ")
 
        # Pestaña 3: Predictor Individual
        self.pred_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pred_frame, text=" 🔮 Predictor Individual ")
        self._build_predictor_tab()
 
    # ─────────────────────────────────────────────
    #  PESTAÑA PREDICTOR INDIVIDUAL
    # ─────────────────────────────────────────────
    def _build_predictor_tab(self):
        """Construye el formulario de predicción individual."""
 
        # Etiquetas legibles para cada variable
        labels = {
            'Area_m2':              ('Área (m²)',                   0,    500,  80),
            'Habitaciones':         ('Habitaciones',                1,     10,   3),
            'Banos':                ('Baños',                       1,     10,   2),
            'Estrato':              ('Estrato (1–6)',                1,      6,   3),
            'Antiguedad_Anos':      ('Antigüedad (años)',            0,     50,  10),
            'Distancia_Centro_km':  ('Distancia al centro (km)',     0,     30,   5),
            'Seguridad_Sector':     ('Seguridad del sector (1–10)',  1,     10,   7),
        }
 
        # Frame con scroll por si la ventana es pequeña
        canvas_scroll = tk.Canvas(self.pred_frame, bg='#f0f4f8', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.pred_frame, orient='vertical', command=canvas_scroll.yview)
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
 
        inner = tk.Frame(canvas_scroll, bg='#f0f4f8')
        canvas_scroll.create_window((0, 0), window=inner, anchor='nw')
        inner.bind('<Configure>', lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox('all')))
 
        # Título
        tk.Label(inner, text="🔮 Predictor de Precio Individual",
                 font=('Segoe UI', 13, 'bold'), bg='#f0f4f8', fg='#1e3d59').grid(
                 row=0, column=0, columnspan=3, pady=(15, 5), padx=20, sticky='w')
        tk.Label(inner, text="Ingresa los datos de la propiedad para estimar su valor comercial.",
                 font=('Segoe UI', 9), bg='#f0f4f8', fg='#555').grid(
                 row=1, column=0, columnspan=3, pady=(0, 15), padx=20, sticky='w')
 
        # Campos del formulario
        self.pred_vars = {}   # {col: (StringVar, Entry)}
        self.pred_sliders = {}
 
        for i, (col, (label, mn, mx, default)) in enumerate(labels.items()):
            row = i + 2
 
            tk.Label(inner, text=label, font=('Segoe UI', 10), bg='#f0f4f8', width=28, anchor='w').grid(
                row=row, column=0, padx=(20, 5), pady=6, sticky='w')
 
            var = tk.DoubleVar(value=default)
            self.pred_vars[col] = var
 
            slider = ttk.Scale(inner, from_=mn, to=mx, variable=var, orient='horizontal', length=200,
                               command=lambda val, c=col: self._sync_entry(c))
            slider.grid(row=row, column=1, padx=5, pady=6)
            self.pred_sliders[col] = slider
 
            entry = ttk.Entry(inner, textvariable=var, width=8, font=('Segoe UI', 10))
            entry.grid(row=row, column=2, padx=(5, 20), pady=6)
            entry.bind('<Return>', lambda e, c=col: self._sync_slider(c))
            entry.bind('<FocusOut>', lambda e, c=col: self._sync_slider(c))
 
        # Botón predecir
        btn_row = len(labels) + 2
        ttk.Button(inner, text="  💰  ESTIMAR PRECIO  ", command=self.predict_individual,
                   style='Predict.TButton').grid(row=btn_row, column=0, columnspan=3, pady=15)
 
        # Frame resultado
        self.result_frame = tk.Frame(inner, bg='#ffffff', relief='groove', bd=2)
        self.result_frame.grid(row=btn_row + 1, column=0, columnspan=3, padx=20, pady=5, sticky='ew')
 
        self.lbl_resultado = tk.Label(self.result_frame, text="",
                                      font=('Segoe UI', 15, 'bold'), bg='#ffffff', fg='#155724', pady=10)
        self.lbl_resultado.pack()
 
        self.lbl_intervalo = tk.Label(self.result_frame, text="",
                                      font=('Segoe UI', 10), bg='#ffffff', fg='#555', pady=4)
        self.lbl_intervalo.pack()
 
        self.lbl_advertencia = tk.Label(self.result_frame, text="",
                                        font=('Segoe UI', 9, 'italic'), bg='#ffffff', fg='#856404', pady=4)
        self.lbl_advertencia.pack()
 
    def _sync_entry(self, col):
        """Redondea el valor del slider al mover."""
        val = self.pred_vars[col].get()
        self.pred_vars[col].set(round(val, 1))
 
    def _sync_slider(self, col):
        """Ajusta el slider cuando el usuario escribe en el Entry."""
        try:
            val = float(self.pred_vars[col].get())
            self.pred_vars[col].set(val)
        except (ValueError, tk.TclError):
            pass
 
    def predict_individual(self):
        """Ejecuta la predicción para los valores ingresados en el formulario."""
        if self.model is None:
            messagebox.showwarning("Modelo no entrenado",
                                   "Primero debes cargar los datos y ejecutar la regresión.")
            return
 
        try:
            # Recolectar valores del formulario
            valores = {col: float(self.pred_vars[col].get()) for col in self.x_cols}
            X_nuevo = pd.DataFrame([valores])
            X_nuevo = sm.add_constant(X_nuevo, has_constant='add')
 
            # Predicción puntual e intervalo de confianza al 95%
            prediccion = self.model.get_prediction(X_nuevo)
            resumen = prediccion.summary_frame(alpha=0.05)
 
            precio_estimado = resumen['mean'].values[0]
            ic_inf = resumen['obs_ci_lower'].values[0]
            ic_sup = resumen['obs_ci_upper'].values[0]
 
            # Mostrar resultado en la pestaña
            self.lbl_resultado.config(
                text=f"💰  Precio estimado:  ${precio_estimado:,.1f} Millones COP"
            )
            self.lbl_intervalo.config(
                text=f"Intervalo de confianza 95%:  [ ${ic_inf:,.1f}M  —  ${ic_sup:,.1f}M ]"
            )
 
            # Advertencia si algún valor está fuera del rango observado
            advertencias = []
            for col in self.x_cols:
                val = valores[col]
                col_min = self.df[col].min()
                col_max = self.df[col].max()
                if val < col_min or val > col_max:
                    advertencias.append(col)
 
            if advertencias:
                self.lbl_advertencia.config(
                    text=f"⚠️  Valores fuera del rango de entrenamiento: {', '.join(advertencias)}"
                )
            else:
                self.lbl_advertencia.config(text="✅  Todos los valores están dentro del rango de entrenamiento.")
 
            # También mostrar en la consola
            self.res_text.delete('1.0', tk.END)
            self.res_text.insert(tk.END, ">>> PREDICCIÓN INDIVIDUAL <<<\n")
            self.res_text.insert(tk.END, "-"*50 + "\n")
            for col, val in valores.items():
                self.res_text.insert(tk.END, f"  {col:<30} {val}\n")
            self.res_text.insert(tk.END, "-"*50 + "\n")
            self.res_text.insert(tk.END, f"  Precio estimado:       ${precio_estimado:,.2f} Millones\n")
            self.res_text.insert(tk.END, f"  IC 95% inferior:       ${ic_inf:,.2f} Millones\n")
            self.res_text.insert(tk.END, f"  IC 95% superior:       ${ic_sup:,.2f} Millones\n")
 
            # Ir a la pestaña del predictor
            self.notebook.select(self.pred_frame)
 
        except Exception as e:
            messagebox.showerror("Error en predicción", str(e))
 
    # ─────────────────────────────────────────────
    #  RESTO DE MÉTODOS (sin cambios)
    # ─────────────────────────────────────────────
    def load_data(self):
        path = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
        if path:
            try:
                self.df = pd.read_csv(path)
                for widget in self.left_frame.winfo_children():
                    widget.destroy()
                self.table = Table(self.left_frame, dataframe=self.df, showtoolbar=False, showstatusbar=False)
                self.table.show()
                messagebox.showinfo("Carga Exitosa", f"Se han cargado {len(self.df)} registros.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")
 
    def run_analysis(self):
        if self.df.empty:
            messagebox.showwarning("Aviso", "Primero debe cargar el archivo CSV.")
            return
 
        try:
            X = self.df[self.x_cols]
            y = self.df[self.y_col]
            X = sm.add_constant(X)
            
            self.model = sm.OLS(y, X).fit()
            y_pred = self.model.predict(X)
 
            r2 = r2_score(y, y_pred)
            mae = mean_absolute_error(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
 
            self.res_text.delete('1.0', tk.END)
            self.res_text.insert(tk.END, ">>> ANÁLISIS MULTIVARIADO COMPLETADO <<<\n")
            self.res_text.insert(tk.END, f"Coeficiente de Determinación (R²): {r2:.4f}\n")
            self.res_text.insert(tk.END, f"Error Medio Absoluto (MAE): {mae:.2f} Millones\n")
            self.res_text.insert(tk.END, f"Raíz del Error Cuadrático (RMSE): {rmse:.2f} Millones\n")
            self.res_text.insert(tk.END, "-"*50 + "\n")
            self.res_text.insert(tk.END, "COEFICIENTES DEL MODELO:\n")
            self.res_text.insert(tk.END, str(self.model.params))
            
            self.update_plot(y, y_pred)
 
        except KeyError as e:
            messagebox.showerror("Error de Columnas", f"El CSV no contiene la columna: {e}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
 
    def update_plot(self, real, pred):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
 
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.regplot(x=real, y=pred, ax=ax, scatter_kws={'alpha':0.4}, line_kws={'color':'red'})
        ax.set_title("Comparación: Precio Real vs. Predicción", fontsize=10)
        ax.set_xlabel("Precio Real ($ Millones)")
        ax.set_ylabel("Estimación del Modelo ($ Millones)")
        
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.notebook.select(self.graph_frame)
 
    def show_correlation_matrix(self):
        if self.df.empty:
            messagebox.showwarning("Aviso", "Primero debe cargar el archivo CSV.")
            return
 
        cols_analisis = self.x_cols + [self.y_col]
        cols_disponibles = [c for c in cols_analisis if c in self.df.columns]
 
        if len(cols_disponibles) < 2:
            messagebox.showerror("Error", "No hay suficientes columnas numéricas para calcular la correlación.")
            return
 
        for widget in self.corr_frame.winfo_children():
            widget.destroy()
 
        corr_matrix = self.df[cols_disponibles].corr()
 
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor('#f8f9fa')
        ax.set_facecolor('#f8f9fa')
 
        sns.heatmap(
            corr_matrix, ax=ax, annot=True, fmt=".2f", cmap='RdYlGn',
            center=0, vmin=-1, vmax=1, linewidths=0.5, linecolor='white',
            square=True, cbar_kws={"shrink": 0.8, "label": "Coeficiente de Pearson"},
            annot_kws={"size": 9, "weight": "bold"}
        )
 
        ax.set_title("Matriz de Correlación de Pearson\nVariables del Modelo Inmobiliario",
                     fontsize=11, fontweight='bold', pad=15)
        ax.tick_params(axis='x', rotation=45, labelsize=9)
        ax.tick_params(axis='y', rotation=0, labelsize=9)
        plt.tight_layout()
 
        canvas = FigureCanvasTkAgg(fig, master=self.corr_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
 
        self.res_text.delete('1.0', tk.END)
        self.res_text.insert(tk.END, ">>> MATRIZ DE CORRELACIÓN DE PEARSON <<<\n")
        self.res_text.insert(tk.END, "-"*50 + "\n")
 
        if self.y_col in corr_matrix.columns:
            corr_con_precio = corr_matrix[self.y_col].drop(self.y_col).sort_values(ascending=False)
            self.res_text.insert(tk.END, f"Correlación de variables con '{self.y_col}':\n")
            for var, val in corr_con_precio.items():
                nivel = self._nivel_correlacion(abs(val))
                signo = "↑ positiva" if val > 0 else "↓ negativa"
                self.res_text.insert(tk.END, f"  {var:<30} r = {val:+.4f}  [{nivel} / {signo}]\n")
 
        self.notebook.select(self.corr_frame)
 
    def _nivel_correlacion(self, r_abs):
        if r_abs >= 0.8:
            return "Muy alta"
        elif r_abs >= 0.6:
            return "Alta"
        elif r_abs >= 0.4:
            return "Moderada"
        elif r_abs >= 0.2:
            return "Baja"
        else:
            return "Muy baja / nula"
 
    def reset(self):
        self.df = pd.DataFrame()
        self.model = None
        self.res_text.delete('1.0', tk.END)
        for widget in self.left_frame.winfo_children(): widget.destroy()
        for widget in self.graph_frame.winfo_children(): widget.destroy()
        for widget in self.corr_frame.winfo_children(): widget.destroy()
        self.lbl_resultado.config(text="")
        self.lbl_intervalo.config(text="")
        self.lbl_advertencia.config(text="")
 
 
if __name__ == "__main__":
    root = tk.Tk()
    app = ViviendaRegressionApp(root)
    root.mainloop()