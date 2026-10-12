"""Dashboard de dengue y capacidad de respuesta en salud.

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
    formas = gpd.read_file(CARPETA / "datos" / "distritos_peru.geojson")
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

# ---------------------------------------------------------------------- graficos
izq, der = st.columns(2)

with izq:
    st.subheader("Casos por departamento")
    por_depto = (
        filtrado.groupby("departamento")["casos_dengue"].sum().reset_index()
        .sort_values("casos_dengue")
    )
    fig = px.bar(
        por_depto, x="casos_dengue", y="departamento", orientation="h",
        color="casos_dengue", color_continuous_scale="Reds",
        labels={"casos_dengue": "Casos", "departamento": ""},
    )
    fig.update_layout(coloraxis_showscale=False, template="plotly_white", height=400)
    st.plotly_chart(fig, width="stretch")

with der:
    st.subheader("Casos vs. establecimientos de salud")
    fig = px.scatter(
        filtrado[filtrado["casos_dengue"] > 0],
        x="n_establecimientos", y="casos_dengue",
        color="departamento", hover_name="distrito", log_y=True,
        labels={"n_establecimientos": "Establecimientos", "casos_dengue": "Casos (log)"},
    )
    fig.update_layout(template="plotly_white", height=400)
    st.plotly_chart(fig, width="stretch")

# -------------------------------------------------------------------------- mapa
st.subheader("Mapa distrital")

formas_filtradas = formas[formas["ubigeo"].isin(filtrado["ubigeo"])]

fig = px.choropleth_map(
    formas_filtradas,
    geojson=formas_filtradas.geometry,
    locations=formas_filtradas.index,
    color="casos_dengue",
    color_continuous_scale="YlOrRd",
    map_style="carto-positron",
    zoom=4.5,
    center={"lat": -9.2, "lon": -75.0},
    opacity=0.7,
    hover_name="distrito",
    hover_data={"departamento": True, "casos_dengue": True, "n_establecimientos": True},
    height=550,
)
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig, width="stretch")

# ------------------------------------------------------------------------- tabla
st.subheader("Distritos con mayor presión sobre el sistema de salud")

tabla = filtrado.copy()
tabla["casos_por_establecimiento"] = (
    tabla["casos_dengue"] / tabla["n_establecimientos"].replace(0, pd.NA)
).round(1)

st.dataframe(
    tabla.sort_values("casos_por_establecimiento", ascending=False)[
        ["departamento", "provincia", "distrito", "casos_dengue",
         "n_establecimientos", "casos_por_establecimiento"]
    ].head(20),
    width="stretch",
    hide_index=True,
)

st.download_button(
    "Descargar datos filtrados (CSV)",
    tabla.to_csv(index=False).encode("utf-8"),
    "dengue_filtrado.csv",
    "text/csv",
)
