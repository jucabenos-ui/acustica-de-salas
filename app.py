import streamlit as st
import math

st.title("Modelación del Campo Sonoro en Recintos")

st.sidebar.header("Dimensiones de la sala")

largo = st.sidebar.number_input("Largo (m)",6.0)
ancho = st.sidebar.number_input("Ancho (m)",4.0)
alto = st.sidebar.number_input("Altura (m)",2.5)

V = largo * ancho * alto

st.sidebar.header("Propiedades acústicas")

S = st.sidebar.number_input("Superficie total S (m²)",160.0)
A = st.sidebar.number_input("Área de absorción A (sabines)",20.0)

alpha = A/S if S>0 else 0

st.sidebar.header("Datos de la fuente")

W = st.sidebar.number_input("Potencia acústica W (W)",0.001)
r = st.sidebar.number_input("Distancia a la fuente r (m)",5.0)
Q = st.sidebar.number_input("Factor de directividad Q",2.0)
Lw = st.sidebar.number_input("Nivel de potencia Lw (dB)",90.0)

c = 343
I0 = 1e-12

# ===============================
# CALCULOS ACUSTICOS
# ===============================

RT_sabine = 0.161 * V / A if A>0 else 0

RT_eyring = 0.161 * V / (-S * math.log(1-alpha)) if alpha<1 else 0

l = 4 * V / S if S>0 else 0

n = (c * RT_sabine) / l if l>0 else 0

tau = l / c if c>0 else 0

If = W / (4 * math.pi * r**2)

LI = 10 * math.log10(If / I0)

R = A / (1-alpha) if alpha<1 else 0

Ir = (4 * W) / R if R>0 else 0

LIr = 10 * math.log10(Ir / I0) if Ir>0 else 0

Lp = Lw + 10 * math.log10(Q/(4*math.pi*r**2) + 4/R) if R>0 else 0

Dc = 0.057 * math.sqrt(Q * R) if R>0 else 0

# ===============================
# RESULTADOS
# ===============================

st.header("Resultados")

st.subheader("Parámetros de la sala")

st.write("Volumen de la sala:", round(V,2),"m³")
st.write("Superficie total:", S,"m²")
st.write("Área de absorción:", A,"sabines")

st.subheader("Tiempo de reverberación")

st.write("RT Sabine:", round(RT_sabine,3),"s")
st.write("RT Eyring:", round(RT_eyring,3),"s")

st.subheader("Propagación del sonido")

st.write("Recorrido libre medio:", round(l,3),"m")
st.write("Número de reflexiones:", round(n,2))
st.write("Tiempo entre reflexiones:", round(tau,5),"s")

st.subheader("Campo directo")

st.write("Intensidad de la fuente If:", If)
st.write("Nivel de intensidad LI:", round(LI,2),"dB")

st.subheader("Campo reverberado")

st.write("Constante de sala R:", round(R,2))
st.write("Intensidad reverberada Ir:", Ir)
st.write("Nivel reverberado LIr:", round(LIr,2),"dB")

st.subheader("Nivel total de presión sonora")

st.write("Nivel de presión sonora Lp:", round(Lp,2),"dB")

st.subheader("Distancia crítica")

st.write("Distancia crítica Dc:", round(Dc,2),"m")
