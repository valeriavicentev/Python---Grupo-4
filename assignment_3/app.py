"""¿Dónde llovió más en Peru entre enero y mayo de 2025?

Correr en local:
    uv run streamlit run app.py
"""

from pathlib import Path

import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------------- configuracion
st.set_page_config(page_title="Lluvia en el Perú", page_icon="🌧️", layout="wide")

# La carpeta donde vive este archivo. Los datos se buscan aquí, y no "donde
# sea que se haya lanzado la app": en tu computadora la corres desde esta
# carpeta, pero Streamlit Cloud la corre desde la raíz del repositorio, y ahí
# una ruta suelta como "datos.csv" no existe.
CARPETA = Path(__file__).parent


# ------------------------------------------------------------------ carga datos
# @st.cache_data guarda el resultado: sin esto, el archivo se lee otra vez
# cada vez que alguien mueve un filtro y la app va lentísima.
@st.cache_data
def cargar():
    datos = pd.read_csv(CARPETA / "datos" / "tabla_final.csv", dtype={"ubigeo": str})
    distritos = gpd.read_file(CARPETA / "datos" / "distritos_peru.geojson")
    # El geojson viene por distrito. Los dos primeros dígitos del ubigeo son el
    # departamento, así que se unen los distritos en los 25 departamentos.
    distritos["ubigeo"] = distritos["ubigeo"].str[:2]
    formas = distritos.dissolve(by="ubigeo")[["geometry"]]
    # Al unir distritos quedan huecos diminutos entre ellos (puntitos blancos en
    # el mapa); inflar y desinflar un poquito el contorno los cierra. Luego se
    # simplifica el contorno para que el mapa que se manda al navegador pese menos.
    formas["geometry"] = formas.buffer(0.001).buffer(-0.001).simplify(0.01)
    return datos, formas


datos, formas = cargar()

# ----------------------------------------------------------------------- filtros
st.sidebar.header("Filtros")

departamentos = sorted(datos["departamento"].unique())
elegidos = st.sidebar.multiselect(
    "Departamento", departamentos, default=departamentos
)

lluvia_min = float(datos["lluvia_total_mm"].min())
lluvia_max = float(datos["lluvia_total_mm"].max())
rango = st.sidebar.slider(
    "Lluvia total (mm)", lluvia_min, lluvia_max, (lluvia_min, lluvia_max)
)

filtrado = datos[
    datos["departamento"].isin(elegidos)
    & datos["lluvia_total_mm"].between(rango[0], rango[1])
]

# ------------------------------------------------------------------------ titulo
st.title("🌧️ Lluvias y emergencias por departamento")
st.caption("Lluvia acumulada y declaratorias de emergencia por departamento · Fuente: SENAMHI e INDECI")

if filtrado.empty:
    st.warning("No hay departamentos que cumplan los filtros. Ajusta la selección.")
    st.stop()

# ---------------------------------------------------------------------- metricas
c1, c2, c3, c4 = st.columns(4)
c1.metric("Departamentos", f"{len(filtrado)}")
c2.metric("Lluvia promedio", f"{filtrado['lluvia_total_mm'].mean():,.1f} mm")
c3.metric("Días de lluvia fuerte", f"{int(filtrado['dias_lluvia_fuerte'].sum())}")
c4.metric("Declaratorias de emergencia", f"{int(filtrado['declaratorias'].sum())}")

st.divider()

# ----------------------------------------------------------------------- grafico
st.subheader("¿Más lluvia significa más declaratorias de emergencia?")
st.caption("Cada punto es un departamento. Pasa el mouse para ver el detalle.")


destacados = ["Loreto", "Madre de Dios", "Lima", "Callao", "Tacna"]
graf = filtrado.assign(
    etiqueta=filtrado["departamento"].where(filtrado["departamento"].isin(destacados), "")
)

fig = px.scatter(
    graf, x="lluvia_total_mm", y="declaratorias", text="etiqueta",
    custom_data=["departamento", "capital", "dias_lluvia_fuerte", "prorrogas"],
    labels={"lluvia_total_mm": "Lluvia total (mm)", "declaratorias": "Declaratorias de emergencia"},
)
fig.update_traces(
    marker=dict(size=13, color="#2a78d6", opacity=0.85, line=dict(width=1.5, color="white")),
    
    textposition=["top right" if x < 150 else "top center" for x in graf["lluvia_total_mm"]],
    hovertemplate=(
        "<b>%{customdata[0]}</b> (capital: %{customdata[1]})<br>"
        "Lluvia total: %{x:,.1f} mm<br>"
        "Días de lluvia fuerte: %{customdata[2]}<br>"
        "Declaratorias: %{y}<br>"
        "Prórrogas: %{customdata[3]}<extra></extra>"
    ),
)
fig.update_layout(height=450, yaxis=dict(dtick=1, rangemode="tozero"), xaxis=dict(rangemode="tozero"))
st.plotly_chart(fig, width="stretch")

# -------------------------------------------------------------------------- mapa
st.subheader("Mapa por departamento")


variables = {
    "lluvia_total_mm": ("Lluvia total (mm)", "Blues"),
    "dias_lluvia_fuerte": ("Días de lluvia fuerte", "Blues"),
    "declaratorias": ("Declaratorias de emergencia", "Oranges"),
    "prorrogas": ("Prórrogas", "Oranges"),
}
variable = st.selectbox(
    "Colorear el mapa según", list(variables), format_func=lambda v: variables[v][0]
)
nombre, escala = variables[variable]

mapa = formas.join(filtrado.set_index("ubigeo"), how="inner")

fig = px.choropleth_map(
    mapa, geojson=mapa.geometry, locations=mapa.index, color=variable,
    color_continuous_scale=escala, labels={variable: nombre},
    custom_data=["departamento", "capital", "lluvia_total_mm",
                 "dias_lluvia_fuerte", "declaratorias", "prorrogas"],
    map_style="carto-positron", zoom=4.2, center={"lat": -9.4, "lon": -75.0},
    opacity=0.85, height=600,
)
fig.update_traces(
    marker_line=dict(width=1, color="white"),
    hovertemplate=(
        "<b>%{customdata[0]}</b> (capital: %{customdata[1]})<br>"
        "Lluvia total: %{customdata[2]:,.1f} mm<br>"
        "Días de lluvia fuerte: %{customdata[3]}<br>"
        "Declaratorias: %{customdata[4]}<br>"
        "Prórrogas: %{customdata[5]}<extra></extra>"
    ),
)
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig, width="stretch")

# ------------------------------------------------------------------------- tabla
st.subheader("Datos por departamento")

tabla = filtrado.sort_values("lluvia_total_mm", ascending=False)[
    ["departamento", "capital", "lluvia_total_mm", "dias_lluvia_fuerte",
     "declaratorias", "prorrogas"]
]

st.dataframe(tabla, width="stretch", hide_index=True)

st.download_button(
    "Descargar datos filtrados (CSV)",
    tabla.to_csv(index=False).encode("utf-8"),
    "lluvias_filtrado.csv",
    "text/csv",
)
