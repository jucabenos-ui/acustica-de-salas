import streamlit as st
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt

st.set_page_config(page_title="Acústica de Salas", layout="wide")

st.title("Modelación del Campo Sonoro en Recintos")

# =========================
# Dimensiones de la sala
# =========================
st.sidebar.header("Dimensiones de la sala")

largo = st.sidebar.number_input("Largo (m)", 6.0)
ancho = st.sidebar.number_input("Ancho (m)", 4.0)
alto = st.sidebar.number_input("Altura (m)", 2.5)

V = largo * ancho * alto
S_total = 2*(largo*ancho + largo*alto + ancho*alto)

st.sidebar.write("Volumen:", round(V,2), "m³")
st.sidebar.write("Superficie total:", round(S_total,2), "m²")

# =========================
# Materiales
# =========================

st.header("Materiales del recinto")

frecuencias = [125,250,500,1000,2000,4000]

data = {
    "Material":["Piso","Techo","Paredes","Ventanas","Sillas","Puerta"],
    "Tipo":["Concreto / baldosa","Drywall","Ladrillo","Vidrio","Butaca tapizada","Madera"],
    "Area (m2)":[20.45,0,0,0,0,0],
    "125":[0.01,0.05,0.01,0.28,0.15,0.15],
    "250":[0.01,0.05,0.01,0.22,0.4,0.11],
    "500":[0.02,0.05,0.02,0.15,0.7,0.1],
    "1000":[0.02,0.04,0.02,0.12,0.85,0.07],
    "2000":[0.02,0.04,0.02,0.08,0.9,0.05],
    "4000":[0.02,0.04,0.02,0.06,0.9,0.05]
}

df = pd.DataFrame(data)

df_edit = st.data_editor(df, num_rows="dynamic")

# =========================
# Absorción total A(f)
# =========================

A_freq = {}

for f in frecuencias:
    A = np.sum(df_edit["Area (m2)"] * df_edit[str(f)])
    A_freq[f] = A

st.write("### Área de absorción equivalente")

for f in frecuencias:
    st.write(f"A({f} Hz) = {round(A_freq[f],3)} sabines")

# =========================
# RT por banda
# =========================

c = 343

RT_sabine = []
RT_eyring = []
RT_millington = []

for f in frecuencias:

    A = A_freq[f]
    alpha_m = A / S_total if S_total>0 else 0

    # Sabine
    RTs = 0.161 * V / A if A>0 else 0
    RT_sabine.append(RTs)

    # Eyring
    RTe = 0.161 * V / (-S_total * math.log(1-alpha_m)) if alpha_m<1 and alpha_m>0 else RTs
    RT_eyring.append(RTe)

    # Millington
    suma = 0
    for i,row in df_edit.iterrows():
        area = row["Area (m2)"]
        alpha = row[str(f)]
        if alpha < 1:
            suma += area * math.log(1-alpha)

    RTm = -0.161 * V / suma if suma!=0 else RTs
    RT_millington.append(RTm)

# =========================
# Tabla de resultados
# =========================

st.header("Tiempo de reverberación")

resultados = pd.DataFrame({
    "Frecuencia (Hz)":frecuencias,
    "RT Sabine (s)":RT_sabine,
    "RT Eyring (s)":RT_eyring,
    "RT Millington (s)":RT_millington
})

st.write("### Resultados de RT")
st.dataframe(resultados)

# =========================
# Gráfica
# =========================

st.header("Gráfica RT vs Frecuencia")

plt.style.use("dark_background")

fig, ax = plt.subplots(figsize=(8,4))

# Colores más sobrios
color_sabine = "#4C78A8"
color_eyring = "#F58518"
color_millington = "#54A24B"

ax.plot(
    frecuencias,
    RT_sabine,
    marker="o",
    linewidth=2,
    markersize=6,
    color=color_sabine,
    label="Sabine"
)

ax.plot(
    frecuencias,
    RT_eyring,
    marker="o",
    linewidth=2,
    markersize=6,
    color=color_eyring,
    label="Eyring"
)

ax.plot(
    frecuencias,
    RT_millington,
    marker="o",
    linewidth=2,
    markersize=6,
    color=color_millington,
    label="Millington"
)

ax.set_xlabel("Frecuencia (Hz)", fontsize=11)
ax.set_ylabel("RT (s)", fontsize=11)

ax.set_title("Tiempo de Reverberación vs Frecuencia", fontsize=13)

# grid tenue
ax.grid(True, linestyle="--", alpha=0.25)

# fondo
ax.set_facecolor("#0E1117")
fig.patch.set_facecolor("#0E1117")

# leyenda limpia
ax.legend(frameon=False)

st.pyplot(fig)

ax.set_xlabel("Frecuencia (Hz)")
ax.set_ylabel("Tiempo de reverberación (s)")
ax.set_title("RT vs Frecuencia")

ax.legend()

st.pyplot(fig)
