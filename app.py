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
# Base de datos de materiales
# =========================

material_db = {

"Concreto / baldosa":[0.01,0.01,0.02,0.02,0.03,0.04],
"Drywall":[0.05,0.05,0.05,0.04,0.07,0.09],
"Ladrillo":[0.01,0.01,0.02,0.02,0.03,0.04],
"Vidrio":[0.28,0.22,0.15,0.12,0.08,0.06],
"Madera":[0.15,0.11,0.10,0.07,0.06,0.07],
"Panel acústico":[0.25,0.50,0.80,0.90,0.95,0.95]

}

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

"125":[0]*8,
"250":[0]*8,
"500":[0]*8,
"1000":[0]*8,
"2000":[0]*8,
"4000":[0]*8

}

df=pd.DataFrame(data)

df_edit=st.data_editor(
df,
column_config={
"Tipo": st.column_config.SelectboxColumn(
"Tipo de material",
options=list(material_db.keys())
)
}
)

# =========================
# Actualizar coeficientes automáticamente
# =========================

for i,row in df_edit.iterrows():

    tipo=row["Tipo"]

    if tipo in material_db:

        coef=material_db[tipo]

        df_edit.loc[i,["125","250","500","1000","2000","4000"]]=coef

# =========================
# Absorción equivalente
# =========================

A_freq={}

for f in frecuencias:

    A=np.sum(df_edit["Area (m2)"]*df_edit[str(f)])

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

    # Sabine
    RTs=0.161*V/A
    RT_s.append(RTs)

    # Eyring
    alpha=A/S
    RTe=0.161*V/(-S*math.log(1-alpha))
    RT_e.append(RTe)

    # Millington

    suma=0

    for i,row in df_edit.iterrows():

        area=row["Area (m2)"]
        a=row[str(f)]

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

frecs=[int(f) for f in frecuencias]

fig,ax=plt.subplots()

ax.plot(frecs,RT_s,marker="o",label="Sabine")
ax.plot(frecs,RT_e,marker="o",label="Eyring")
ax.plot(frecs,RT_m,marker="o",label="Millington")

ax.set_xlabel("Frecuencia (Hz)")
ax.set_ylabel("Tiempo de reverberación (s)")
ax.set_title("RT vs Frecuencia")

ax.legend()

st.pyplot(fig)
