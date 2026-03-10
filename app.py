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

L = st.sidebar.number_input("Largo (m)", 6.0)
W = st.sidebar.number_input("Ancho (m)", 4.0)
H = st.sidebar.number_input("Altura (m)", 2.5)

V = L * W * H
S = 2 * (L * W + L * H + W * H)

st.sidebar.write("Volumen:", round(V,2), "m³")
st.sidebar.write("Superficie total:", round(S,2), "m²")

# =========================
# Fuente sonora
# =========================

st.sidebar.header("Fuente sonora")

W_fuente = st.sidebar.number_input("Potencia W (W)", 0.001)
r = st.sidebar.number_input("Distancia r (m)", 5.0)
Q = st.sidebar.number_input("Directividad Q", 2.0)
Lw = st.sidebar.number_input("Nivel potencia Lw (dB)", 90.0)

c = 343
I0 = 1e-12

# =========================
# Frecuencias
# =========================

frecuencias = [125,250,500,1000,2000,4000]

# =========================
# Base de datos de materiales
# =========================

material_db = {
"Concreto / baldosa":[0.01,0.01,0.02,0.02,0.02,0.02],
"Drywall":[0.05,0.05,0.05,0.04,0.04,0.04],
"Ladrillo":[0.01,0.01,0.02,0.02,0.02,0.02],
"Vidrio":[0.28,0.22,0.15,0.12,0.08,0.06],
"Madera":[0.15,0.11,0.10,0.07,0.05,0.05]
}

# =========================
# Superficies del recinto
# =========================

superficies = {
"Piso":("Concreto / baldosa",26.9518),
"Techo":("Concreto / baldosa",20.5748),
"Cielo raso":("Drywall",8.799),
"Pared ladrillo":("Ladrillo",51.246),
"Pared drywall":("Drywall",11.166),
"Ventanas":("Vidrio",4),
"Sillas":("Madera",2.422),
"Puerta":("Madera",3.18)
}

st.header("Superficies del recinto")

tabla_superficies = pd.DataFrame([
    [k, v[0], v[1]] for k,v in superficies.items()
], columns=["Superficie","Material","Área (m2)"])

st.dataframe(tabla_superficies)

# =========================
# Absorción equivalente
# =========================

A_freq = []

for i,f in enumerate(frecuencias):
    A = 0
    for nombre,(material,area) in superficies.items():
        alpha = material_db[material][i]
        A += area * alpha
    A_freq.append(A)

st.subheader("Área de absorción equivalente")

for f,A in zip(frecuencias,A_freq):
    st.write(f"A({f} Hz) =", round(A,3), "sabines")

# =========================
# RT Sabine
# =========================

RT_s = []

for A in A_freq:
    RT = 0.161 * V / A
    RT_s.append(RT)

# =========================
# RT Eyring
# =========================

RT_e = []

for A in A_freq:
    alpha = A / S
    alpha = min(alpha,0.999)
    RT = 0.161 * V / (-S * np.log(1-alpha))
    RT_e.append(RT)

# =========================
# RT Millington
# =========================

RT_m = []

for i,f in enumerate(frecuencias):
    suma = 0
    for nombre,(material,area) in superficies.items():
        alpha = material_db[material][i]
        alpha = min(alpha,0.999)
        suma += area * np.log(1-alpha)
    RT = -0.161 * V / suma
    RT_m.append(RT)

# =========================
# Tabla RT
# =========================

st.header("Tiempo de reverberación")

tabla = pd.DataFrame({
"Frecuencia (Hz)":frecuencias,
"RT Sabine (s)":RT_s,
"RT Eyring (s)":RT_e,
"RT Millington (s)":RT_m
})

st.dataframe(tabla)

# =========================
# Gráfica
# =========================

st.header("Gráfica RT vs Frecuencia")

plt.style.use("dark_background")

fig,ax = plt.subplots(figsize=(8,4))

ax.plot(frecuencias,RT_s,"o-",label="Sabine",linewidth=2)
ax.plot(frecuencias,RT_e,"o-",label="Eyring",linewidth=2)
ax.plot(frecuencias,RT_m,"o-",label="Millington",linewidth=2)

ax.set_xlabel("Frecuencia (Hz)")
ax.set_ylabel("RT (s)")
ax.grid(True,alpha=0.3)
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

st.write("Recorrido libre medio l =", round(l,3),"m")
st.write("Número de reflexiones n =", round(n,2))
st.write("Tiempo entre reflexiones τ =", round(tau,5),"s")

# =========================
# Campo directo
# =========================

If = W_fuente / (4 * math.pi * r**2)
LI = 10 * math.log10(If / I0)

st.subheader("Campo directo")

st.write("Intensidad de la fuente If =", If)
st.write("Nivel de intensidad LI =", round(LI,2), "dB")

# =========================
# Campo reverberado
# =========================

A_mid = A_freq[3]
alpha_mid = A_mid / S

R = A_mid / (1-alpha_mid)

Ir = (4 * W_fuente) / R
LIr = 10 * math.log10(Ir / I0)

st.subheader("Campo reverberado")

st.write("Constante de sala R =", round(R,2))
st.write("Intensidad reverberada Ir =", Ir)
st.write("Nivel reverberado LIr =", round(LIr,2), "dB")

# =========================
# Nivel total
# =========================

Lp = Lw + 10 * math.log10(Q/(4*math.pi*r**2) + 4/R)

st.subheader("Nivel de presión sonora")

st.write("Nivel de presión sonora Lp =", round(Lp,2), "dB")

# =========================
# Distancia crítica
# =========================

Dc = 0.057 * math.sqrt(Q * R)

st.subheader("Distancia crítica")

st.write("Dc =", round(Dc,2), "m")

# =========================
# Absorción del aire
# =========================

st.subheader("Absorción del aire")

m = st.sidebar.number_input("Coeficiente absorción aire m (dB/m)",0.003)

Lp_r = Lp - 20*math.log10(r) - m*r

st.write("Nivel con absorción del aire Lp(r) =", round(Lp_r,2), "dB")
