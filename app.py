import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Contabilidad Dashboard", page_icon="💼", layout="wide")

COLOR_INGRESOS = "#4CAF50"
COLOR_EGRESOS = "#F44336"
COLOR_SALDO = "#2196F3"
COLOR_BG = "#F5F7FA"
COLOR_CARD = "#FFFFFF"

st.markdown("""
    <style>
        .kpi-card {
            background: #fff;
            border-radius: 14px;
            box-shadow: 0 2px 10px #d3dae3;
            padding: 1.6em 1em 1.1em 1em;
            margin-bottom: 18px;
            text-align: center;
        }
        .kpi-title { color: #555; font-size: 1.1em; margin-bottom: 0.3em; }
        .kpi-value { font-size: 2em; font-weight: bold; }
        .kpi-icon { font-size: 2.2em; padding-bottom: 0.2em; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div style="font-size:2.6em; color:#1A237E; font-weight:bold; letter-spacing:-1px;">💼 Dashboard de Contabilidad</div>', unsafe_allow_html=True)
st.markdown('<div style="color:#3949AB; font-size:1.15em; margin-bottom:2em;">Resumen financiero interactivo con desglose y evolución</div>', unsafe_allow_html=True)

# Cargar datos
df = pd.read_csv("datos_reportes.csv")
df["Fecha"] = pd.to_datetime(df["Fecha"])

# Filtros avanzados en Sidebar
with st.sidebar:
    st.header("Filtros")
    tipo = st.selectbox('Tipo de movimiento', options=['Todos'] + list(df['Tipo'].unique()))
    categoria = st.selectbox('Categoría', options=['Todos'] + list(df['Categoría'].unique()))
    responsable = st.selectbox('Responsable', options=['Todos'] + list(df['Responsable'].unique()))
    estado = st.multiselect('Estado', options=df['Estado'].unique(), default=list(df['Estado'].unique()))
    sucursal = st.selectbox('Sucursal', options=['Todas'] + list(df['Sucursal'].unique()))
    monto_min, monto_max = st.slider('Rango de monto', int(df['Monto'].min()), int(df['Monto'].max()), (int(df['Monto'].min()), int(df['Monto'].max())), step=1000)
    descripcion_text = st.text_input("Buscar en descripción", "")
    rango_fecha = st.date_input("Rango de fechas", [df["Fecha"].min(), df["Fecha"].max()])

# Aplicar filtros avanzados
df_filtrado = df[
    ((df['Tipo'] == tipo) | (tipo == 'Todos')) &
    ((df['Categoría'] == categoria) | (categoria == 'Todos')) &
    ((df['Responsable'] == responsable) | (responsable == 'Todos')) &
    (df['Estado'].isin(estado)) &
    ((df['Sucursal'] == sucursal) | (sucursal == 'Todas')) &
    (df["Monto"] >= monto_min) &
    (df["Monto"] <= monto_max) &
    (df["Fecha"] >= pd.to_datetime(rango_fecha[0])) &
    (df["Fecha"] <= pd.to_datetime(rango_fecha[1])) &
    (df["Descripción"].str.contains(descripcion_text, case=False, na=False))
]

# KPIs
ingresos = df_filtrado[df_filtrado["Tipo"] == "Ingreso"]["Monto"].sum()
egresos = df_filtrado[df_filtrado["Tipo"] == "Egreso"]["Monto"].sum()
saldo = ingresos - egresos
por_cobrar = df_filtrado[(df_filtrado["Tipo"] == "Ingreso") & (df_filtrado["Estado"] == "Pendiente")]["Monto"].sum()
por_pagar = df_filtrado[(df_filtrado["Tipo"] == "Egreso") & (df_filtrado["Estado"] == "Pendiente")]["Monto"].sum()

# Alerta visual por saldo negativo
if saldo < 0:
    saldo_color = "#D32F2F"
    saldo_icon = "⚠️"
    st.error("¡Alerta! El saldo neto es negativo.")
else:
    saldo_color = COLOR_SALDO
    saldo_icon = "🧮"

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">💰</div>
        <div class="kpi-title">Ingresos</div>
        <div class="kpi-value" style="color:{COLOR_INGRESOS};">${ingresos:,.0f}</div></div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">💸</div>
        <div class="kpi-title">Egresos</div>
        <div class="kpi-value" style="color:{COLOR_EGRESOS};">${egresos:,.0f}</div></div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">{saldo_icon}</div>
        <div class="kpi-title">Saldo Neto</div>
        <div class="kpi-value" style="color:{saldo_color};">${saldo:,.0f}</div></div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">📥</div>
        <div class="kpi-title">Por Cobrar</div>
        <div class="kpi-value" style="color:#FF9800;">${por_cobrar:,.0f}</div></div>""", unsafe_allow_html=True)
with col5:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">📤</div>
        <div class="kpi-title">Por Pagar</div>
        <div class="kpi-value" style="color:#9C27B0;">${por_pagar:,.0f}</div></div>""", unsafe_allow_html=True)

st.markdown("---")

# Gráfico 1: Ingresos y Egresos por Sucursal
st.subheader("🏢 Ingresos y Egresos por Sucursal")
df_suc = df_filtrado.groupby(["Sucursal", "Tipo"])["Monto"].sum().reset_index()
if not df_suc.empty:
    fig_suc = px.bar(df_suc, x='Sucursal', y='Monto', color='Tipo', barmode='group',
                     color_discrete_map={"Ingreso": COLOR_INGRESOS, "Egreso": COLOR_EGRESOS},
                     text_auto=True)
    fig_suc.update_layout(xaxis_title="Sucursal", yaxis_title="Monto", plot_bgcolor=COLOR_BG, paper_bgcolor=COLOR_BG)
    st.plotly_chart(fig_suc, use_container_width=True)
else:
    st.info("No hay datos para mostrar por sucursal.")

# Gráfico 2: Egresos por Responsable
st.subheader("👤 Egresos por Responsable")
df_resp = df_filtrado[df_filtrado["Tipo"] == "Egreso"].groupby("Responsable")["Monto"].sum().reset_index()
if not df_resp.empty:
    fig_resp = px.bar(df_resp, x='Responsable', y='Monto', color='Responsable',
                      color_discrete_sequence=px.colors.qualitative.Set2, text_auto=True)
    fig_resp.update_layout(showlegend=False, xaxis_title="Responsable", yaxis_title="Egresos", plot_bgcolor=COLOR_BG, paper_bgcolor=COLOR_BG)
    st.plotly_chart(fig_resp, use_container_width=True)
else:
    st.info("No hay egresos para mostrar por responsable.")

# Gráfico 3: Ingresos y Egresos Mensuales
st.subheader("📊 Ingresos y Egresos Mensuales")
df_mes = df_filtrado.copy()
df_mes["Mes"] = df_mes["Fecha"].dt.to_period("M").astype(str)
df_mes_group = df_mes.groupby(["Mes", "Tipo"])["Monto"].sum().reset_index()
if not df_mes_group.empty:
    fig1 = px.bar(df_mes_group, x='Mes', y='Monto', color='Tipo',
                  barmode='group', text_auto=True,
                  color_discrete_map={"Ingreso": COLOR_INGRESOS, "Egreso": COLOR_EGRESOS})
    fig1.update_layout(xaxis_title="Mes", yaxis_title="Monto", plot_bgcolor=COLOR_BG, paper_bgcolor=COLOR_BG)
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("No hay datos mensuales para mostrar.")

# Gráfico 4: Egresos por Categoría (Pie)
st.subheader("🧾 Distribución de Egresos por Categoría")
df_egresos = df_filtrado[df_filtrado["Tipo"] == "Egreso"]
if not df_egresos.empty:
    fig2 = px.pie(df_egresos, names='Categoría', values='Monto', hole=0.5, color_discrete_sequence=px.colors.sequential.RdBu)
    fig2.update_traces(textinfo='percent+label')
    fig2.update_layout(showlegend=True, plot_bgcolor=COLOR_BG, paper_bgcolor=COLOR_BG)
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No hay egresos en el periodo/selección.")

# Gráfico 5: Evolución del saldo neto (línea)
st.subheader("📈 Evolución del Saldo Neto")
df_evol = df_filtrado.copy()
df_evol["Monto_signed"] = df_evol.apply(lambda x: x["Monto"] if x["Tipo"] == "Ingreso" else -x["Monto"], axis=1)
df_evol = df_evol.sort_values("Fecha")
df_evol["Saldo Neto"] = df_evol["Monto_signed"].cumsum()
if not df_evol.empty:
    fig3 = px.line(df_evol, x='Fecha', y='Saldo Neto', markers=True, line_shape="linear", color_discrete_sequence=[saldo_color])
    fig3.update_layout(xaxis_title="Fecha", yaxis_title="Saldo Neto", plot_bgcolor=COLOR_BG, paper_bgcolor=COLOR_BG)
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No hay movimientos para mostrar evolución.")

st.markdown("---")
st.subheader("📋 Detalle de Movimientos Filtrados")
st.dataframe(df_filtrado, use_container_width=True)