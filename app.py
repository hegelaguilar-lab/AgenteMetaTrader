import os
from flask import Flask, render_template
import requests

app = Flask(__name__)

# 🛡️ SRE SEGURIDAD: Extracción de variables desde el entorno de Render (Cero Hardcoding)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

@app.route("/")
def index():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return "⚠️ [SRE ERROR] Variables de Entorno SUPABASE_URL y SUPABASE_KEY no configuradas en Render.", 500

    # 1. Extracción de Logística SRE (Filtro Estricto: Solo Músculo Operativo)
    ctrl_url = f"{SUPABASE_URL}/rest/v1/nexus_control?tipo_tarea=eq.AGENTE_TRADING&order=id.asc"
    ctrl_res = requests.get(ctrl_url, headers=HEADERS)
    tasks = ctrl_res.json() if ctrl_res.status_code == 200 else []

    # 2. Extracción de Finanzas (El Historial)
    hist_url = f"{SUPABASE_URL}/rest/v1/trade_history?select=agent_node,profit_usd"
    hist_res = requests.get(hist_url, headers=HEADERS)
    history = hist_res.json() if hist_res.status_code == 200 else []

    # 3. Fusión en Memoria (Agrupación Contable por Nodo)
    stats = {}
    if isinstance(history, list):
        for h in history:
            node = str(h.get('agent_node', 'UNKNOWN')).upper()
            profit = float(h.get('profit_usd', 0.0))
            
            if node not in stats:
                stats[node] = {"pnl_total": 0.0, "trades": 0, "wins": 0}
            
            stats[node]["pnl_total"] += profit
            stats[node]["trades"] += 1
            if profit > 0:
                stats[node]["wins"] += 1

    # 4. Inyección Financiera en la Flota
    agents = []
    if isinstance(tasks, list):
        for c in tasks:
            nombre = str(c.get('nombre_tarea', '')).upper()
            node_key = "UNKNOWN"
            
            # Reconocimiento Geográfico
            if "NY" in nombre: node_key = "NY"
            elif "ASIA" in nombre: node_key = "ASIA"
            elif "EUROP" in nombre: node_key = "EUROPE"
            elif "FOREX" in nombre: node_key = "FOREX"
            
            ag_stats = stats.get(node_key, {"pnl_total": 0.0, "trades": 0, "wins": 0})
            win_rate = (ag_stats["wins"] / ag_stats["trades"] * 100) if ag_stats["trades"] > 0 else 0.0
            
            c['pnl_total'] = round(ag_stats["pnl_total"], 2)
            c['win_rate'] = round(win_rate, 1)
            c['trades_count'] = ag_stats["trades"]
            c['capital_asignado'] = float(c.get('capital_asignado') or 3000.0)
            
            agents.append(c)

    return render_template("index.html", agents=agents)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
