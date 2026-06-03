import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Configuración de página
st.set_page_config(
    page_title="Sistema de Predicción Inmobiliaria",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado para un diseño más premium
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        color: #1e3d59;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #555;
        text-align: center;
        margin-bottom: 25px;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #e9ecef;
        text-align: center;
    }
    .prediction-box {
        background-color: #e8f5e9;
        border-left: 5px solid #2e7d32;
        padding: 20px;
        border-radius: 4px;
        margin-top: 15px;
    }
    .warning-box {
        background-color: #fff8e1;
        border-left: 5px solid #ff8f00;
        padding: 15px;
        border-radius: 4px;
        margin-top: 10px;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_style=True)

# Títulos de la aplicación
st.markdown("<div class='main-title'>🏠 MODELO DE ESTIMACIÓN DE VALORES COMERCIALES</div>", unsafe_style=True)
st.markdown("<div class='subtitle'>Sistema de predicción inmobiliaria basado en Regresión Lineal Multivariada</div>", unsafe_style=True)

# Inicializar estado de sesión
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
if 'model' not in st.session_state:
    st.session_state.model = None

# Variables del modelo
x_cols = ['Area_m2', 'Habitaciones', 'Banos', 'Estrato', 'Antiguedad_Anos', 'Distancia_Centro_km', 'Seguridad_Sector']
y_col = 'Precio_Millones'

# Panel lateral / Sidebar
st.sidebar.header("📂 Carga de Datos")
uploaded_file = st.sidebar.file_uploader("Subir archivo de viviendas (CSV)", type=["csv"])

# Botón para generar datos de demostración
if st.sidebar.button("✨ Usar Datos de Demostración"):
    np.random.seed(42)
    n_samples = 150
    area = np.random.normal(110, 35, n_samples).clip(45, 350).astype(int)
    habs = np.random.randint(1, 6, n_samples)
    banos = (habs - np.random.randint(0, 2, n_samples)).clip(1, 4)
    estrato = np.random.randint(1, 7, n_samples)
    antiguedad = np.random.randint(0, 25, n_samples)
    distancia = np.random.uniform(0.5, 20, n_samples).round(1)
    seguridad = np.random.randint(3, 11, n_samples)

    # Fórmula sintética lógica para simular precios en millones de COP
    precio = (40 + 2.8 * area + 18 * habs + 22 * banos + 55 * estrato - 3.5 * antiguedad - 6.2 * distancia + 9.5 * seguridad + np.random.normal(0, 30, n_samples))
    precio = precio.clip(60, 1800).round(1)

    st.session_state.df = pd.DataFrame({
        'Area_m2': area,
        'Habitaciones': habs,
        'Banos': banos,
        'Estrato': estrato,
        'Antiguedad_Anos': antiguedad,
        'Distancia_Centro_km': distancia,
        'Seguridad_Sector': seguridad,
        'Precio_Millones': precio
    })
    st.session_state.model = None # Resetear modelo con nuevos datos
    st.sidebar.success("✅ ¡Datos de demostración generados!")

if uploaded_file is not None:
    try:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.session_state.model = None # Resetear modelo
        st.sidebar.success(f"✅ ¡Se cargaron {len(st.session_state.df)} registros!")
    except Exception as e:
        st.sidebar.error(f"Error al leer el archivo: {e}")

# Comprobar si hay datos cargados
if not st.session_state.df.empty:
    df = st.session_state.df
    
    # Validar que las columnas necesarias existan
    missing_cols = [c for c in x_cols + [y_col] if c not in df.columns]
    
    if missing_cols:
        st.error(f"⚠️ El archivo cargado no contiene las columnas necesarias: {', '.join(missing_cols)}")
    else:
        # Pestañas principales
        tab_datos, tab_regresion, tab_predictor = st.tabs([
            "📂 Datos de Viviendas", 
            "📈 Análisis & Regresión", 
            "🔮 Predictor Individual"
        ])
        
        # 1. Pestaña de Datos
        with tab_datos:
            st.subheader("Datos Cargados")
            st.dataframe(df, use_container_width=True)
            
            # Estadísticas descriptivas básicas
            with st.expander("📊 Ver estadísticas descriptivas"):
                st.write(df.describe())
        
        # Ajustar el modelo si no se ha ajustado todavía
        X = df[x_cols]
        y = df[y_col]
        X_with_const = sm.add_constant(X)
        
        if st.session_state.model is None:
            st.session_state.model = sm.OLS(y, X_with_const).fit()
        
        model = st.session_state.model
        y_pred = model.predict(X_with_const)
        
        # Calcular métricas
        r2 = r2_score(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        
        # 2. Pestaña de Análisis y Regresión
        with tab_regresion:
            st.subheader("Resultados del Modelo Regresión Multivariada (OLS)")
            
            # Tarjetas de métricas
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Coeficiente de Determinación (R²)", f"{r2:.4f}", help="Indica qué proporción de la varianza del precio es explicada por las variables del modelo.")
            with col_m2:
                st.metric("Error Medio Absoluto (MAE)", f"${mae:.2f} M", help="Error promedio absoluto entre la estimación y el precio real (en millones COP).")
            with col_m3:
                st.metric("Raíz del Error Cuadrático Medio (RMSE)", f"${rmse:.2f} M", help="Medida del desvío estándar de los residuos del modelo (en millones COP).")
            
            st.markdown("---")
            
            col_graph, col_summary = st.columns([1, 1])
            
            with col_graph:
                st.subheader("Gráficos de Diagnóstico")
                
                # Gráfico 1: Real vs Predicho
                fig1, ax1 = plt.subplots(figsize=(6, 4.5))
                sns.regplot(x=y, y=y_pred, ax=ax1, scatter_kws={'alpha':0.5, 'color':'#1f77b4'}, line_kws={'color':'red', 'linewidth': 2})
                ax1.set_title("Comparación: Precio Real vs. Predicción", fontsize=11, fontweight='bold')
                ax1.set_xlabel("Precio Real ($ Millones COP)")
                ax1.set_ylabel("Estimación del Modelo ($ Millones COP)")
                st.pyplot(fig1)
                
                # Gráfico 2: Matriz de Correlación
                fig2, ax2 = plt.subplots(figsize=(7, 5))
                corr_matrix = df[x_cols + [y_col]].corr()
                sns.heatmap(
                    corr_matrix, ax=ax2, annot=True, fmt=".2f", cmap='RdYlGn',
                    center=0, vmin=-1, vmax=1, linewidths=0.5, linecolor='white',
                    square=True, cbar_kws={"shrink": 0.8},
                    annot_kws={"size": 8, "weight": "bold"}
                )
                ax2.set_title("Matriz de Correlación de Pearson", fontsize=11, fontweight='bold', pad=10)
                st.pyplot(fig2)
                
            with col_summary:
                st.subheader("Coeficientes e Impacto de Variables")
                
                # Tabla limpia de coeficientes
                coef_df = pd.DataFrame({
                    'Coeficiente': model.params,
                    'Error Estándar': model.bse,
                    'Valor t': model.tvalues,
                    'P-Valor (P>|t|)': model.pvalues
                })
                st.dataframe(coef_df.style.format("{:.4f}").highlight_between(left=0, right=0.05, subset=['P-Valor (P>|t|)'], color='#e8f5e9'), use_container_width=True)
                
                st.markdown("""
                **Interpretación rápida:**
                - Un **P-Valor < 0.05** (resaltado en verde) indica que la variable tiene un impacto estadísticamente significativo sobre el precio.
                - El **Coeficiente** representa el cambio promedio en el precio (en millones de COP) por cada unidad de incremento en esa variable, asumiendo las demás constantes.
                """)
                
                with st.expander("📄 Ver Resumen Estadístico Detallado (OLS)"):
                    st.text(str(model.summary()))
                    
        # 3. Pestaña del Predictor Individual
        with tab_predictor:
            st.subheader("🔮 Estimador de Precios Individual")
            st.write("Ajusta las características de la vivienda utilizando los controles deslizantes para estimar su valor comercial.")
            
            # Formulario
            col_in1, col_in2 = st.columns(2)
            
            with col_in1:
                # Sliders con valores mínimos y máximos observados o lógicos
                area_val = st.slider("Área (m²)", min_value=int(df['Area_m2'].min()), max_value=int(df['Area_m2'].max()), value=80, step=5)
                habs_val = st.slider("Habitaciones", min_value=int(df['Habitaciones'].min()), max_value=int(df['Habitaciones'].max()), value=3, step=1)
                banos_val = st.slider("Baños", min_value=int(df['Banos'].min()), max_value=int(df['Banos'].max()), value=2, step=1)
                estrato_val = st.slider("Estrato socioeconómico (1-6)", min_value=int(df['Estrato'].min()), max_value=int(df['Estrato'].max()), value=3, step=1)
                
            with col_in2:
                antiguedad_val = st.slider("Antigüedad (años)", min_value=int(df['Antiguedad_Anos'].min()), max_value=int(df['Antiguedad_Anos'].max()), value=10, step=1)
                distancia_val = st.slider("Distancia al centro de la ciudad (km)", min_value=float(df['Distancia_Centro_km'].min()), max_value=float(df['Distancia_Centro_km'].max()), value=5.0, step=0.5)
                seguridad_val = st.slider("Seguridad del sector (1-10)", min_value=int(df['Seguridad_Sector'].min()), max_value=int(df['Seguridad_Sector'].max()), value=7, step=1)
            
            # Recolectar datos ingresados
            valores = {
                'Area_m2': float(area_val),
                'Habitaciones': float(habs_val),
                'Banos': float(banos_val),
                'Estrato': float(estrato_val),
                'Antiguedad_Anos': float(antiguedad_val),
                'Distancia_Centro_km': float(distancia_val),
                'Seguridad_Sector': float(seguridad_val)
            }
            
            X_nuevo = pd.DataFrame([valores])
            X_nuevo_const = sm.add_constant(X_nuevo, has_constant='add')
            
            # Predicción e intervalo de confianza
            prediccion = model.get_prediction(X_nuevo_const)
            resumen_pred = prediccion.summary_frame(alpha=0.05)
            
            precio_estimado = resumen_pred['mean'].values[0]
            ic_inf = resumen_pred['obs_ci_lower'].values[0]
            ic_sup = resumen_pred['obs_ci_upper'].values[0]
            
            # Mostrar resultado destacado
            st.markdown(f"""
                <div class="prediction-box">
                    <h3 style="margin: 0; color: #2e7d32;">💰 Precio Estimado Comercial</h3>
                    <p style="font-size: 1.8rem; font-weight: bold; margin: 5px 0 0 0; color: #1b5e20;">
                        ${precio_estimado:,.2f} Millones COP
                    </p>
                    <p style="font-size: 1rem; margin: 5px 0 0 0; color: #388e3c;">
                        Intervalo de confianza del 95%: <b>[ ${ic_inf:,.2f}M — ${ic_sup:,.2f}M ]</b>
                    </p>
                </div>
            """, unsafe_style=True)
            
            # Advertencia de extrapolación
            fuera_de_rango = []
            for col, val in valores.items():
                col_min = df[col].min()
                col_max = df[col].max()
                if val < col_min or val > col_max:
                    fuera_de_rango.append(col)
                    
            if fuera_de_rango:
                st.markdown(f"""
                    <div class="warning-box">
                        ⚠️ <b>Atención:</b> Los valores ingresados para las variables <b>{', '.join(fuera_de_rango)}</b> están fuera del rango de datos con el que se entrenó el modelo. 
                        La predicción podría ser menos precisa o no lineal en estas regiones.
                    </div>
                """, unsafe_style=True)
            else:
                st.info("✅ Todos los valores seleccionados se encuentran dentro del rango observado de datos de entrenamiento.")

else:
    # Estado inicial: Sin datos
    st.info("💡 Por favor, sube un archivo de datos en formato **CSV** desde la barra lateral izquierda o haz clic en el botón **'Usar Datos de Demostración'** para probar el funcionamiento de la aplicación.")
    
    # Mostrar una previsualización de la estructura esperada
    st.markdown("### Estructura de Columnas Esperada en el CSV:")
    ejemplo_df = pd.DataFrame([{
        'Area_m2': 85.0,
        'Habitaciones': 3,
        'Banos': 2,
        'Estrato': 3,
        'Antiguedad_Anos': 5,
        'Distancia_Centro_km': 4.2,
        'Seguridad_Sector': 8,
        'Precio_Millones': 280.0
    }])
    st.dataframe(ejemplo_df)
    st.write("Asegúrate de que los encabezados coincidan exactamente (incluyendo mayúsculas/minúsculas y guiones bajos).")
