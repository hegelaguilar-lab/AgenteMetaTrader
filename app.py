import streamlit as st
import requests
import pandas as pd

# ==========================================
# CONFIGURACIÓN SRE DEL ENTORNO
# ==========================================
st.set_page_config(page_title="Nexus C2 Panel", page_icon="🛡️", layout="wide")

# Extracción segura de credenciales
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    st.error("⚠️ [SRE ERROR] Credenciales de Supabase ausentes. Configura los st.secrets.")
    st.stop()

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

st.title("🛡️ NEXUS CLUSTER - COMMAND & CONTROL")
st.markdown("---")

# ==========================================
# MÓDULO 1: MATRIZ DE AGENTES Y CAPITAL
# ==========================================
st.header("⚙️ Matriz de Ignición y Capital Dinámico")

@st.cache_data(ttl=5) # Caché con expiración de 5s para evitar DDoS a Supabase
def fetch_agents():
    url = f"{SUPABASE_URL}/rest/v1/nexus_control?tipo_tarea=eq.AGENTE_TRADING&order=nombre_tarea.asc"
    res = requests.get(url, headers=HEADERS)
    return res.json() if res.status_code == 200 else []

agentes = fetch_agents()

if agentes:
    # Crear columnas dinámicas según la cantidad de agentes
    cols = st.columns(len(agentes))
    for idx, agente in enumerate(agentes):
        with cols[idx]:
            st.subheader(agente.get('nombre_tarea', 'UNKNOWN'))
            
            estado = "🟢 ONLINE" if agente.get('esta_activo') else "🔴 OFFLINE"
            st.markdown(f"**Estado:** {estado}")
            st.markdown(f"**Ventana (NY):** {agente.get('hora_inicio_ny')} - {agente.get('hora_cierre_ny')}")
            
            cap_actual = float(agente.get('capital_asignado', 3000.0))
            nuevo_cap = st.number_input("Capital Operativo ($)", value=cap_actual, step=500.0, key=f"cap_{agente['id']}")
            
            if st.button("Inyectar Presupuesto", key=f"btn_{agente['id']}"):
                patch_url = f"{SUPABASE_URL}/rest/v1/nexus_control?id=eq.{agente['id']}"
                payload = {"capital_asignado": nuevo_cap}
                headers_patch = HEADERS.copy()
                headers_patch["Prefer"] = "return=minimal"
                
                req = requests.patch(patch_url, headers=headers_patch, json=payload)
                if req.status_code == 204:
                    st.success("✅ ADN de Capital inyectado. El Agente ajustará lotes en el próximo tick.")
                    st.rerun()
                else:
                    st.error(f"❌ Fallo API: {req.text}")
else:
    st.info("No se encontraron agentes de trading en Supabase.")

st.markdown("---")

# ==========================================
# MÓDULO 2: INTELIGENCIA CONTABLE (PNL)
# ==========================================
st.header("📊 Inteligencia Contable y Performance")

@st.cache_data(ttl=10) # Refresco cada 10 segundos
def fetch_trades():
    url = f"{SUPABASE_URL}/rest/v1/trade_history?order=created_at.desc"
    res = requests.get(url, headers=HEADERS)
    return res.json() if res.status_code == 200 else []

trades = fetch_trades()

if trades:
    df_trades = pd.DataFrame(trades)
    
    # Conversión de zona horaria de UTC a Local para mejor lectura
    df_trades['created_at'] = pd.to_datetime(df_trades['created_at']).dt.tz_convert('America/New_York').dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Matemáticas de Rendimiento
    total_pnl = df_trades['profit_usd'].sum()
    total_trades = len(df_trades)
    ganadoras = len(df_trades[df_trades['profit_usd'] > 0])
    win_rate = (ganadoras / total_trades) * 100 if total_trades > 0 else 0
    
    # Renderizado de KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Equidad Neta (PnL)", f"${total_pnl:.2f}")
    c2.metric("Operaciones Históricas", total_trades)
    c3.metric("Win Rate", f"{win_rate:.1f}%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Modificar estilos de la tabla
    df_trades = df_trades.rename(columns={
        "created_at": "Fecha (NY)", 
        "agent_node": "Nodo", 
        "symbol": "Activo", 
        "profit_usd": "PnL ($)"
    })
    
    st.dataframe(
        df_trades[["Fecha (NY)", "Nodo", "Activo", "trade_type", "PnL ($)"]], 
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Aún no hay operaciones cerradas registradas en el ecosistema.")