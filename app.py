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

L = st.sidebar.number_input("Largo (m)", value=6.47)
W = st.sidebar.number_input("Ancho (m)", value=4.54)
H = st.sidebar.number_input("Altura (m)", value=3.16)

V = L * W * H
S = 2 * (L*W + L*H + W*H)

st.sidebar.write("Volumen:", round(V, 2), "m³")
st.sidebar.write("Superficie total:", round(S, 2), "m²")

# =========================
# Datos de fuente
# =========================

st.sidebar.header("Fuente sonora")

W_fuente = st.sidebar.number_input("Potencia W (W)", value=0.001)
r = st.sidebar.number_input("Distancia r (m)", value=5.0)
Q = st.sidebar.number_input("Directividad Q", value=2.0)
Lw = st.sidebar.number_input("Nivel potencia Lw (dB)", value=90.0)

c = 343
I0 = 1e-12

# =========================
# Materiales
# =========================

st.header("Materiales del recinto")

frecuencias = [125, 250, 500, 1000, 2000, 4000]

data = {
    "Material": [
        "Piso", "Techo", "Cielo raso", "Pared ladrillo",
        "Pared drywall", "Ventanas", "Sillas", "Puerta"
    ],
    "Tipo": [
        "Concreto / baldosa", "Concreto / baldosa", "Drywall",
        "Ladrillo", "Drywall", "Vidrio", "Madera", "Madera"
    ],
    "Area (m2)": [26.9518, 20.5748, 8.799, 51.246, 11.166, 4, 2.422, 3.18],
    "125":  [0.01, 0.01, 0.05, 0.01, 0.05, 0.28, 0.04, 0.15],
    "250":  [0.01, 0.01, 0.05, 0.01, 0.05, 0.22, 0.04, 0.11],
    "500":  [0.02, 0.02, 0.05, 0.02, 0.05, 0.15, 0.06, 0.10],
    "1000": [0.02, 0.02, 0.04, 0.02, 0.04, 0.12, 0.07, 0.07],
    "2000": [0.02, 0.02, 0.04, 0.02, 0.04, 0.08, 0.076, 0.05],
    "4000": [0.02, 0.02, 0.04, 0.02, 0.04, 0.06, 0.076, 0.05]
}

df = pd.DataFrame(data)

st.dataframe(df)

df_edit = st.data_editor(df)

# =========================
# Absorción equivalente
# =========================

A_freq = {}

for f in frecuencias:

    A = 0

    for i, row in df_edit.iterrows():

        area = float(row["Area (m2)"])
        alpha = float(row[str(f)])

        A += area * alpha

    A_freq[f] = A

st.subheader("Área de absorción equivalente")

for f in frecuencias:
    st.write(f"A({f} Hz) =", round(A_freq[f], 3), "sabines")

# =========================
# RT por banda
# =========================

RT_s = []
RT_e = []
RT_m = []

for f in frecuencias:

    A = A_freq[f]

    alpha = A / S
    alpha = min(alpha, 0.999)

    # Sabine
    RTs = 0.161 * V / A
    RT_s.append(round(RTs, 4))

    # Eyring
    RTe = 0.161 * V / (-S * math.log(1 - alpha))
    RT_e.append(round(RTe, 4))

    # Millington
    suma = 0

    for i, row in df_edit.iterrows():

        area = float(row["Area (m2)"])
        a = float(row[str(f)])

        a = min(a, 0.999)

        suma += area * math.log(1 - a)

    if suma == 0:
        RTm = RTs
    else:
        RTm = -0.161 * V / suma

    RT_m.append(round(RTm, 4))

# =========================
# Tabla RT
# =========================

st.header("Tiempo de reverberación")

tabla = pd.DataFrame({
    "Frecuencia (Hz)": frecuencias,
    "RT Sabine (s)": RT_s,
    "RT Eyring (s)": RT_e,
    "RT Millington (s)": RT_m
})

st.dataframe(tabla)

# =========================
# Gráfica
# =========================

st.header("Gráfica RT vs Frecuencia")

plt.style.use("dark_background")

fig, ax = plt.subplots(figsize=(8,4))

ax.plot(frecuencias, RT_s, "o-", label="Sabine", linewidth=2, color="cyan")
ax.plot(frecuencias, RT_e, "o-", label="Eyring", linewidth=2, color="lime")
ax.plot(frecuencias, RT_m, "o-", label="Millington", linewidth=2, color="orange")

ax.set_xscale("log")
ax.set_xticks(frecuencias)
ax.set_xticklabels([str(f) for f in frecuencias])

ax.set_xlabel("Frecuencia (Hz)")
ax.set_ylabel("RT (s)")
ax.set_title("Tiempo de reverberación por banda de frecuencia")

ax.grid(True, alpha=0.3, which="both")
ax.legend()

st.pyplot(fig)

# =========================
# Parámetros del campo acústico
# =========================

st.header("Parámetros del campo acústico")

RT_ref = RT_s[2]

l = 4 * V / S
n = (c * RT_ref) / l
tau = l / c

st.write("Recorrido libre medio l =", round(l, 3), "m")
st.write("Número de reflexiones n =", round(n, 2))
st.write("Tiempo entre reflexiones τ =", round(tau, 5), "s")

# =========================
# Campo directo
# =========================

If = W_fuente / (4 * math.pi * r**2)
LI = 10 * math.log10(If / I0)

st.subheader("Campo directo")

st.write("Intensidad de la fuente If =", round(If, 6), "W/m²")
st.write("Nivel de intensidad LI =", round(LI, 2), "dB")

# =========================
# Campo reverberado
# =========================

A_mid = A_freq[1000]
alpha_mid = A_mid / S
alpha_mid = min(alpha_mid, 0.999)

R = A_mid / (1 - alpha_mid)

Ir = (4 * W_fuente) / R
LIr = 10 * math.log10(Ir / I0)

st.subheader("Campo reverberado")

st.write("Constante de sala R =", round(R, 2))
st.write("Intensidad reverberada Ir =", round(Ir, 8), "W/m²")
st.write("Nivel reverberado LIr =", round(LIr, 2), "dB")

# =========================
# Nivel total
# =========================

Lp = Lw + 10 * math.log10(Q / (4 * math.pi * r**2) + 4 / R)

st.subheader("Nivel de presión sonora")

st.write("Nivel de presión sonora Lp =", round(Lp, 2), "dB")

# =========================
# Distancia crítica
# =========================

Dc = 0.057 * math.sqrt(Q * R)

st.subheader("Distancia crítica")

st.write("Dc =", round(Dc, 2), "m")

# =========================
# Absorción del aire
# =========================

st.subheader("Absorción del aire")

m = st.sidebar.number_input("Coeficiente absorción aire m (dB/m)", value=0.003)

if r > 0:
    Lp_r = Lp - 20 * math.log10(r) - m * r
    st.write("Nivel con absorción del aire Lp(r) =", round(Lp_r, 2), "dB")
