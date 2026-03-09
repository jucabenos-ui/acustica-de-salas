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

L = st.sidebar.number_input("Largo (m)",6.0)
W = st.sidebar.number_input("Ancho (m)",4.0)
H = st.sidebar.number_input("Altura (m)",2.5)

V = L*W*H
S = 2*(L*W + L*H + W*H)

st.sidebar.write("Volumen:",round(V,2),"m³")
st.sidebar.write("Superficie total:",round(S,2),"m²")

# =========================
# Datos de fuente
# =========================

st.sidebar.header("Fuente sonora")

W_fuente = st.sidebar.number_input("Potencia W (W)",0.001)
r = st.sidebar.number_input("Distancia r (m)",5.0)
Q = st.sidebar.number_input("Directividad Q",2.0)
Lw = st.sidebar.number_input("Nivel potencia Lw (dB)",90.0)

c = 343
I0 = 1e-12

# =========================
# Materiales
# =========================

st.header("Materiales del recinto")

frecuencias=[125,250,500,1000,2000,4000]

data={
"Material":[
"Piso",
"Techo",
"Cielo raso",
"Pared ladrillo",
"Pared drywall",
"Ventanas",
"Sillas",
"Puerta"
],

"Tipo":[
"Concreto / baldosa",
"Concreto / baldosa",
"Drywall",
"Ladrillo",
"Drywall",
"Vidrio",
"Madera",
"Madera"
],

"Area (m2)":[26.9518,20.5748,8.799,51.246,11.166,4,2.422,3.18],

"125":[0.01,0.01,0.05,0.01,0.05,0.28,0.10,0.15],
"250":[0.01,0.01,0.05,0.01,0.05,0.22,0.10,0.11],
"500":[0.02,0.02,0.05,0.02,0.05,0.15,0.10,0.10],
"1000":[0.02,0.02,0.04,0.02,0.04,0.12,0.10,0.07],
"2000":[0.02,0.02,0.04,0.02,0.04,0.08,0.10,0.05],
"4000":[0.02,0.02,0.04,0.02,0.04,0.06,0.10,0.05]
}

df=pd.DataFrame(data)

df_edit=st.data_editor(df)

# =========================
# Absorción equivalente
# =========================

A_freq={}

for f in frecuencias:

    A=np.sum(df_edit["Area (m2)"]*df_edit[str(f)])

    if A<=0:
        A=1e-6

    A_freq[f]=A

st.subheader("Área de absorción equivalente")

for f in frecuencias:
    st.write(f"A({f} Hz) =",round(A_freq[f],3),"sabines")

# =========================
# RT por banda
# =========================

RT_s=[]
RT_e=[]
RT_m=[]

for f in frecuencias:

    A=A_freq[f]

    alpha=A/S

    alpha=min(alpha,0.999)

    # Sabine
    RTs=0.161*V/A
    RT_s.append(RTs)

    # Eyring
    RTe=0.161*V/(-S*math.log(1-alpha))
    RT_e.append(RTe)

    # Millington
    suma=0

    for i,row in df_edit.iterrows():

        area=row["Area (m2)"]
        a=row[str(f)]

        a=min(a,0.999)

        suma+=area*math.log(1-a)

    if suma==0:
        RTm=RTs
    else:
        RTm=-0.161*V/suma

    RT_m.append(RTm)

# =========================
# Tabla RT
# =========================

st.header("Tiempo de reverberación")

tabla=pd.DataFrame({
"Frecuencia":frecuencias,
"RT Sabine":RT_s,
"RT Eyring":RT_e,
"RT Millington":RT_m
})

st.dataframe(tabla)

# =========================
# Gráfica
# =========================

st.header("Gráfica RT vs Frecuencia")

plt.style.use("dark_background")

fig,ax=plt.subplots(figsize=(8,4))

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

RT_ref=RT_s[2]

l=4*V/S
n=(c*RT_ref)/l
tau=l/c

st.write("Recorrido libre medio l =",round(l,3),"m")
st.write("Número de reflexiones n =",round(n,2))
st.write("Tiempo entre reflexiones τ =",round(tau,5),"s")

# =========================
# Campo directo
# =========================

If=W_fuente/(4*math.pi*r**2)
LI=10*math.log10(If/I0)

st.subheader("Campo directo")

st.write("Intensidad de la fuente If =",If)
st.write("Nivel de intensidad LI =",round(LI,2),"dB")

# =========================
# Campo reverberado
# =========================

A_mid=A_freq[1000]
alpha_mid=A_mid/S

R=A_mid/(1-alpha_mid)

Ir=(4*W_fuente)/R
LIr=10*math.log10(Ir/I0)

st.subheader("Campo reverberado")

st.write("Constante de sala R =",round(R,2))
st.write("Intensidad reverberada Ir =",Ir)
st.write("Nivel reverberado LIr =",round(LIr,2),"dB")

# =========================
# Nivel total
# =========================

Lp=Lw+10*math.log10(Q/(4*math.pi*r**2)+4/R)

st.subheader("Nivel de presión sonora")

st.write("Nivel de presión sonora Lp =",round(Lp,2),"dB")

# =========================
# Distancia crítica
# =========================

Dc=0.057*math.sqrt(Q*R)

st.subheader("Distancia crítica")

st.write("Dc =",round(Dc,2),"m")

# =========================
# Absorción del aire
# =========================

st.subheader("Absorción del aire")

m = st.sidebar.number_input("Coeficiente absorción aire m (dB/m)",0.003)

Lp0 = Lp

Lp_r = Lp0 - 20*math.log10(r) - m*r

st.write("Nivel con absorción del aire Lp(r) =",round(Lp_r,2),"dB")
