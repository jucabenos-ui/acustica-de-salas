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
        "Piso/Techo", "Drywall", "Ladrillo",
        "Vidrio", "Butaca tapizada", "Madera"
    ],
    "Area (m2)": [
        47.5266, 19.956, 36.5516,
        4, 2.422, 17.8744
    ],
    "125":  [0.01, 0.05, 0.01, 0.28, 0.15, 0.15],
    "250":  [0.01, 0.05, 0.01, 0.22, 0.40, 0.11],
    "500":  [0.02, 0.05, 0.02, 0.15, 0.70, 0.10],
    "1000": [0.02, 0.04, 0.02, 0.12, 0.85, 0.07],
    "2000": [0.03, 0.07, 0.03, 0.08, 0.90, 0.06],
    "4000": [0.04, 0.09, 0.04, 0.06, 0.90, 0.07]
}

df = pd.DataFrame(data)
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
    alpha = min(A / S, 0.999)

    # Sabine
    RTs = 0.161 * V / A

    # Eyring
    RTe = 0.161 * V / (-S * math.log(1 - alpha))

    # Millington
    suma = 0
    for i, row in df_edit.iterrows():
        area = float(row["Area (m2)"])
        a = min(float(row[str(f)]), 0.999)
        suma += area * math.log(1 - a)

    RTm = -0.161 * V / suma

    RT_s.append(RTs)
    RT_e.append(RTe)
    RT_m.append(RTm)

# =========================
# Tabla RT
# =========================

st.header("Tiempo de reverberación")

tabla = pd.DataFrame({
    "Frecuencia (Hz)": frecuencias,
    "RT Sabine (s)": np.round(RT_s, 3),
    "RT Eyring (s)": np.round(RT_e, 3),
    "RT Millington (s)": np.round(RT_m, 3)
})

st.dataframe(tabla)

# =========================
# Gráfica
# =========================

st.header("Gráfica RT vs Frecuencia")

fig, ax = plt.subplots(figsize=(8,4))

ax.plot(frecuencias, RT_s, "o-", label="Sabine")
ax.plot(frecuencias, RT_e, "o-", label="Eyring")
ax.plot(frecuencias, RT_m, "o-", label="Millington")

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
# Parámetros acústicos
# =========================

st.header("Parámetros del campo acústico")

RT_ref = RT_s[2]

l = 4 * V / S
tau = l / c
n = (c * RT_ref) / l

st.write("Recorrido libre medio l =", round(l, 3), "m")
st.write("Tiempo entre reflexiones τ =", round(tau, 5), "s")
st.write("Número de reflexiones n =", round(n, 2))

# =========================
# Campo directo
# =========================

If = W_fuente / (4 * math.pi * r**2)
LI = 10 * math.log10(If / I0)

st.subheader("Campo directo")
st.write("Intensidad If =", round(If, 6), "W/m²")
st.write("Nivel LI =", round(LI, 2), "dB")

# =========================
# Campo reverberado
# =========================

A_mid = A_freq[1000]
alpha_mid = min(A_mid / S, 0.999)

R = A_mid / (1 - alpha_mid)

Ir = (4 * W_fuente) / R
LIr = 10 * math.log10(Ir / I0)

st.subheader("Campo reverberado")
st.write("Constante de sala R =", round(R, 2))
st.write("Intensidad Ir =", round(Ir, 8), "W/m²")
st.write("Nivel LIr =", round(LIr, 2), "dB")

# =========================
# Nivel total
# =========================

Lp = Lw + 10 * math.log10(Q / (4 * math.pi * r**2) + 4 / R)

st.subheader("Nivel de presión sonora")
st.write("Lp =", round(Lp, 2), "dB")

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

m = st.sidebar.number_input("Coeficiente absorción aire (dB/m)", value=0.003)

Lp_r = Lp - 20 * math.log10(r) - m * r
st.write("Nivel con absorción del aire Lp(r) =", round(Lp_r, 2), "dB")

# =========================
# INTELIGIBILIDAD GLOBAL (%ALCons)
# =========================

st.header("Inteligibilidad de la palabra (%ALCons)")

# Distancia
r = st.number_input("Distancia fuente-receptor (m)", value=2.0)

# RT en 2 kHz
RT_2k = RT_s[4]

# =========================
# CÁLCULO CORREGIDO
# =========================

if r > Dc:
    # campo reverberado dominante
    ALcons = 9 * RT_2k
else:
    # modelo general físico
    ALcons = 200 * (RT_2k**2) / V * (1 + (r**2)/(Dc**2))

# =========================
# CLASIFICACIÓN
# =========================

if ALcons <= 1.4:
    calidad = "Excelente"
elif ALcons <= 4.8:
    calidad = "Buena"
elif ALcons <= 11.4:
    calidad = "Aceptable"
elif ALcons <= 24:
    calidad = "Pobre"
else:
    calidad = "Mala"

# =========================
# RESULTADOS
# =========================

st.subheader("Resultado")

st.write("%ALCons =", round(ALcons,2), "%")
st.write("Calidad de inteligibilidad:", calidad)
