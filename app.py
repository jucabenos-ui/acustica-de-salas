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

L = st.sidebar.number_input("Largo (m)",6.47)
W = st.sidebar.number_input("Ancho (m)",4.54)
H = st.sidebar.number_input("Altura (m)",3.16)

V = L*W*H
S = 2*(L*W + L*H + W*H)

st.sidebar.write("Volumen:",round(V,2),"m³")
st.sidebar.write("Superficie total:",round(S,2),"m²")

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

"125":[0.01,0.01,0.05,0.01,0.05,0.28,0.04,0.15],
"250":[0.01,0.01,0.05,0.01,0.05,0.22,0.04,0.11],
"500":[0.02,0.02,0.05,0.02,0.05,0.15,0.06,0.10],
"1000":[0.02,0.02,0.04,0.02,0.04,0.12,0.07,0.07],
"2000":[0.02,0.02,0.04,0.02,0.04,0.08,0.076,0.05],
"4000":[0.02,0.02,0.04,0.02,0.04,0.06,0.076,0.05]
}

df=pd.DataFrame(data)

df_edit=st.data_editor(df)

# =========================
# Absorción equivalente
# =========================

A_freq={}

for f in frecuencias:

    A=0

    for i,row in df_edit.iterrows():

        area=float(row["Area (m2)"])
        alpha=float(row[str(f)])

        A+=area*alpha

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

        area=float(row["Area (m2)"])
        a=float(row[str(f)])

        a=min(a,0.999)

        suma+=area*math.log(1-a)

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

fig,ax=plt.subplots(figsize=(8,4))

ax.plot(frecuencias,RT_s,"o-",label="Sabine")
ax.plot(frecuencias,RT_e,"o-",label="Eyring")
ax.plot(frecuencias,RT_m,"o-",label="Millington")

ax.set_xlabel("Frecuencia (Hz)")
ax.set_ylabel("RT (s)")
ax.grid(True)
ax.legend()

st.pyplot(fig)

# =========================
# Parámetros estadísticos
# =========================

st.header("Parámetros del campo acústico")

c=343

RT_ref=RT_s[2]

l=4*V/S
n=(c*RT_ref)/l
tau=l/c

st.write("Recorrido libre medio l =",round(l,3),"m")
st.write("Número promedio de reflexiones n =",round(n,2))
st.write("Tiempo entre reflexiones τ =",round(tau,5),"s")
