import streamlit as st
import math

st.title("Modelación del Campo Sonoro en Recintos")

st.sidebar.header("Datos del recinto")

V = st.sidebar.number_input("Volumen V (m³)",100.0)
S = st.sidebar.number_input("Superficie total S (m²)",160.0)
A = st.sidebar.number_input("Área de absorción A (sabines)",20.0)

alpha = A/S if S>0 else 0

st.sidebar.header("Datos de la fuente")

W = st.sidebar.number_input("Potencia acústica W (W)",0.001)
r = st.sidebar.number_input("Distancia r (m)",5.0)
Q = st.sidebar.number_input("Factor de directividad Q",2.0)
Lw = st.sidebar.number_input("Nivel potencia Lw (dB)",90.0)

c = 343
I0 = 1e-12

RT_sabine = 0.161*V/A if A>0 else 0
RT_eyring = 0.161*V/(-S*math.log(1-alpha)) if alpha<1 else 0

l = 4*V/S if S>0 else 0

n = (c*RT_sabine)/l if l>0 else 0

tau = l/c if c>0 else 0

If = W/(4*math.pi*r**2)

LI = 10*math.log10(If/I0)

R = A/(1-alpha) if alpha<1 else 0

Ir = (4*W)/R if R>0 else 0

LIr = 10*math.log10(Ir/I0) if Ir>0 else 0

Lp = Lw + 10*math.log10(Q/(4*math.pi*r**2)+4/R)

Dc = 0.057*math.sqrt(Q*R)

st.header("Resultados")

st.write("RT Sabine:",RT_sabine,"s")
st.write("RT Eyring:",RT_eyring,"s")
st.write("Recorrido libre medio:",l,"m")
st.write("Número de reflexiones:",n)
st.write("Tiempo entre reflexiones:",tau,"s")
st.write("Intensidad fuente:",If)
st.write("Nivel intensidad:",LI,"dB")
st.write("Constante sala R:",R)
st.write("Intensidad reverberada:",Ir)
st.write("Nivel campo reverberado:",LIr,"dB")
st.write("Nivel presión sonora total:",Lp,"dB")
st.write("Distancia crítica:",Dc,"m")
