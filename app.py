import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

st.set_page_config(page_title="Acústica de Salas", layout="wide")

st.title("Modelación Acústica de un Recinto")

# =========================================================
# CONSTANTES
# =========================================================

c = 343
I0 = 1e-12

frecuencias = np.array([125,250,500,1000,2000,4000])

# =========================================================
# DIMENSIONES DEL RECINTO
# =========================================================

st.sidebar.header("Dimensiones de la sala")

L = st.sidebar.number_input("Largo (m)",6.47)
W = st.sidebar.number_input("Ancho (m)",4.54)
H = st.sidebar.number_input("Altura (m)",3.16)

V = L*W*H
S = 2*(L*W + L*H + W*H)

st.sidebar.write("Volumen:",round(V,2),"m³")
st.sidebar.write("Superficie total:",round(S,2),"m²")

# =========================================================
# DATOS DE FUENTE
# =========================================================

st.sidebar.header("Fuente sonora")

W_fuente = st.sidebar.number_input("Potencia acústica (W)",0.001)
r = st.sidebar.number_input("Distancia fuente-receptor (m)",5.0)
Q = st.sidebar.number_input("Directividad",2.0)
Lw = st.sidebar.number_input("Nivel potencia sonora (dB)",90.0)

# =========================================================
# TABLA DE MATERIALES
# =========================================================

st.header("Materiales del recinto")

data={

"Elemento":[
"Piso",
"Techo",
"Cielo raso",
"Pared ladrillo",
"Pared drywall",
"Ventanas",
"Sillas",
"Puerta"
],

"Area":[26.9518,20.5748,8.799,51.246,11.166,4,2.422,3.18],

"125":[0.01,0.01,0.05,0.01,0.05,0.28,0.10,0.15],
"250":[0.01,0.01,0.05,0.01,0.05,0.22,0.10,0.11],
"500":[0.02,0.02,0.05,0.02,0.05,0.15,0.10,0.10],
"1000":[0.02,0.02,0.04,0.02,0.04,0.12,0.10,0.07],
"2000":[0.02,0.02,0.04,0.02,0.04,0.08,0.10,0.05],
"4000":[0.02,0.02,0.04,0.02,0.04,0.06,0.10,0.05]

}

df = pd.DataFrame(data)

df_edit = st.data_editor(df)

# =========================================================
# ABSORCIÓN EQUIVALENTE
# =========================================================

A = []

for f in frecuencias:

    absorcion = np.sum(df_edit["Area"] * df_edit[str(f)])

    if absorcion <= 0:
        absorcion = 1e-6

    A.append(absorcion)

A = np.array(A)

st.subheader("Área de absorción equivalente")

for i,f in enumerate(frecuencias):
    st.write(f"A({f} Hz) = {round(A[i],3)} sabines")

# =========================================================
# COEFICIENTE PROMEDIO
# =========================================================

alpha_prom = A/S
alpha_prom = np.clip(alpha_prom,1e-6,0.999)

# =========================================================
# TIEMPOS DE REVERBERACIÓN
# =========================================================

RT_sabine = 0.161*V/A

RT_eyring = 0.161*V/(-S*np.log(1-alpha_prom))

RT_millington = []

for f in frecuencias:

    suma = 0

    for i,row in df_edit.iterrows():

        area = row["Area"]
        alpha = row[str(f)]

        alpha = np.clip(alpha,1e-6,0.999)

        suma += -area*np.log(1-alpha)

    RT_millington.append(0.161*V/suma)

RT_millington = np.array(RT_millington)

# =========================================================
# TABLA RESULTADOS
# =========================================================

st.header("Tiempo de reverberación")

tabla = pd.DataFrame({

"Frecuencia":frecuencias,
"Sabine":RT_sabine,
"Eyring":RT_eyring,
"Millington":RT_millington

})

st.dataframe(tabla)

# =========================================================
# GRÁFICA
# =========================================================

st.subheader("RT vs Frecuencia")

plt.style.use("dark_background")

fig,ax = plt.subplots(figsize=(8,4))

ax.plot(frecuencias,RT_sabine,'o-',label="Sabine")
ax.plot(frecuencias,RT_eyring,'s-',label="Eyring")
ax.plot(frecuencias,RT_millington,'^-',label="Millington")

ax.set_xscale("log")
ax.set_xticks(frecuencias)
ax.set_xticklabels(frecuencias)

ax.set_xlabel("Frecuencia (Hz)")
ax.set_ylabel("Tiempo de reverberación (s)")

ax.grid(True,alpha=0.3)
ax.legend()

st.pyplot(fig)

# =========================================================
# PARÁMETROS DEL CAMPO ACÚSTICO
# =========================================================

st.header("Parámetros del campo acústico")

l = 4*V/S
tau = l/c

st.write("Recorrido libre medio:",round(l,3),"m")
st.write("Tiempo entre reflexiones:",round(tau,5),"s")

# =========================================================
# CAMPO DIRECTO
# =========================================================

If = W_fuente/(4*math.pi*r**2)
LI = 10*np.log10(If/I0)

st.subheader("Campo directo")

st.write("Intensidad:",If)
st.write("Nivel intensidad:",round(LI,2),"dB")

# =========================================================
# CAMPO REVERBERADO
# =========================================================

A_mid = A[3]
alpha_mid = A_mid/S

R = A_mid/(1-alpha_mid)

Ir = (4*W_fuente)/R
LIr = 10*np.log10(Ir/I0)

st.subheader("Campo reverberado")

st.write("Constante de sala:",round(R,2))
st.write("Intensidad reverberada:",Ir)
st.write("Nivel reverberado:",round(LIr,2),"dB")

# =========================================================
# NIVEL TOTAL
# =========================================================

Lp = Lw + 10*np.log10(Q/(4*np.pi*r**2) + 4/R)

st.subheader("Nivel de presión sonora")

st.write("Lp =",round(Lp,2),"dB")

# =========================================================
# DISTANCIA CRÍTICA
# =========================================================

Dc = 0.057*np.sqrt(Q*R)

st.subheader("Distancia crítica")

st.write("Dc =",round(Dc,2),"m")
