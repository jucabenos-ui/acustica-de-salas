import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math

st.set_page_config(page_title="Acústica de Salas", layout="wide")

st.title("Modelación del Campo Sonoro en Recintos")

# ====================================================
# CONSTANTES
# ====================================================

c = 343
I0 = 1e-12

# ====================================================
# DIMENSIONES DEL RECINTO
# ====================================================

st.sidebar.header("Dimensiones del recinto")

L = st.sidebar.number_input("Largo (m)",6.47)
W = st.sidebar.number_input("Ancho (m)",4.54)
H = st.sidebar.number_input("Altura (m)",3.16)

V = L*W*H

S_piso = L*W
S_techo = S_piso
S_pared = 2*(L*H)+2*(W*H)
S_total = 2*S_piso + S_pared

st.sidebar.write("Volumen:",round(V,2),"m³")
st.sidebar.write("Superficie total:",round(S_total,2),"m²")

# ====================================================
# DATOS DE FUENTE
# ====================================================

st.sidebar.header("Fuente sonora")

W_fuente = st.sidebar.number_input("Potencia W (W)",0.001)
r = st.sidebar.number_input("Distancia r (m)",5.0)
Q = st.sidebar.number_input("Directividad Q",2.0)
Lw = st.sidebar.number_input("Nivel potencia Lw (dB)",90.0)

# ====================================================
# FRECUENCIAS
# ====================================================

frecuencias = np.array([125,250,500,1000,2000,4000])

# ====================================================
# BASE DE DATOS DE MATERIALES
# ====================================================

materiales = {

"concreto":[0.01,0.01,0.02,0.02,0.03,0.04],
"drywall":[0.05,0.05,0.05,0.04,0.07,0.09],
"ladrillo":[0.03,0.03,0.04,0.05,0.07,0.07],
"vidrio":[0.28,0.22,0.15,0.12,0.08,0.06],
"madera":[0.15,0.11,0.10,0.07,0.06,0.07]

}

# ====================================================
# SELECCIÓN DE MATERIALES
# ====================================================

st.header("Materiales del recinto")

piso = st.selectbox("Material del piso",materiales.keys())
techo = st.selectbox("Material del techo",materiales.keys())

alpha_piso = np.array(materiales[piso])
alpha_techo = np.array(materiales[techo])

# ====================================================
# PAREDES
# ====================================================

st.subheader("Materiales de pared")

n = st.number_input("Número de materiales en paredes",1,5)

A_pared = np.zeros(len(frecuencias))
secciones = []

for i in range(int(n)):

    mat = st.selectbox(f"Material pared {i+1}",materiales.keys(),key=i)
    area = st.number_input(f"Área pared {i+1} (m²)",1.0,key=f"a{i}")

    alpha = np.array(materiales[mat])

    secciones.append((area,alpha))
    A_pared += area*alpha

# ====================================================
# ABSORCIÓN TOTAL
# ====================================================

A = S_piso*alpha_piso + S_techo*alpha_techo + A_pared

alpha_prom = A/S_total
alpha_prom = np.clip(alpha_prom,1e-6,0.999)

st.subheader("Absorción equivalente")

for i,f in enumerate(frecuencias):
    st.write(f"A({f} Hz) =",round(A[i],3),"sabines")

# ====================================================
# TIEMPOS DE REVERBERACIÓN
# ====================================================

RT_sabine = 0.161*V/A

RT_eyring = 0.161*V/(-S_total*np.log(1-alpha_prom))

term_piso = -S_piso*np.log(1-alpha_piso)
term_techo = -S_techo*np.log(1-alpha_techo)

term_pared = np.zeros(len(frecuencias))

for area,alpha in secciones:
    alpha = np.clip(alpha,1e-6,0.999)
    term_pared += -area*np.log(1-alpha)

den = term_piso + term_techo + term_pared

RT_millington = 0.161*V/den

# ====================================================
# TABLA
# ====================================================

tabla = pd.DataFrame({

"Frecuencia":frecuencias,
"Sabine":RT_sabine,
"Eyring":RT_eyring,
"Millington":RT_millington

})

st.header("Tiempo de reverberación")

st.dataframe(tabla)

# ====================================================
# GRÁFICA
# ====================================================

fig,ax = plt.subplots()

ax.plot(frecuencias,RT_sabine,'o-',label="Sabine")
ax.plot(frecuencias,RT_eyring,'s-',label="Eyring")
ax.plot(frecuencias,RT_millington,'^-',label="Millington")

ax.set_xscale("log")
ax.set_xticks(frecuencias)
ax.set_xticklabels(frecuencias)

ax.set_xlabel("Frecuencia (Hz)")
ax.set_ylabel("RT (s)")
ax.set_title("Tiempo de Reverberación")

ax.grid(True,which="both",ls="--")
ax.legend()

st.pyplot(fig)

# ====================================================
# PARÁMETROS DEL CAMPO ACÚSTICO
# ====================================================

st.header("Parámetros del campo acústico")

l = 4*V/S_total
tau = l/c
n_reflexiones = c*RT_sabine/l

st.write("Recorrido libre medio:",round(l,3),"m")
st.write("Tiempo entre reflexiones:",round(tau,5),"s")

# ====================================================
# CAMPO DIRECTO
# ====================================================

If = W_fuente/(4*math.pi*r**2)
LI = 10*math.log10(If/I0)

st.subheader("Campo directo")

st.write("Intensidad:",If)
st.write("Nivel de intensidad:",round(LI,2),"dB")

# ====================================================
# CAMPO REVERBERADO
# ====================================================

R = A/(1-alpha_prom)

Ir = (4*W_fuente)/R

st.subheader("Campo reverberado")

st.write("Constante de sala R:",np.round(R,2))
st.write("Campo reverberado Ir:",np.round(Ir,8))

# ====================================================
# NIVEL TOTAL
# ====================================================

Lp = Lw + 10*np.log10((Q/(4*np.pi*r**2)) + (4/R))

st.subheader("Nivel de presión sonora")

st.write("Lp:",np.round(Lp,2),"dB")

# ====================================================
# DISTANCIA CRÍTICA
# ====================================================

Dc = 0.057*np.sqrt(Q*R)

st.subheader("Distancia crítica")

st.write("Dc:",np.round(Dc,2),"m")
