import os
from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route("/")
def index():
    # 🛡️ SRE FEDERACIÓN DE DATOS: Detección dinámica de múltiples bases de datos
    db_configs = []
    
    # 1. BD Principal (Mantiene tu configuración actual intacta)
    if os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_KEY"):
        db_configs.append((os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY")))
        
    # 2. BDs Adicionales Dinámicas (Soporta clústeres infinitos SUPABASE_URL_1, _2, _3...)
    for i in range(1, 10):
        url = os.environ.get(f"SUPABASE_URL_{i}")
        key = os.environ.get(f"SUPABASE_KEY_{i}")
        if url and key:
            db_configs.append((url, key))
            
    if not db_configs:
        return "⚠️ [SRE ERROR] No hay variables de entorno SUPABASE configuradas en Render.", 500

    all_agents = []

    # 🔄 Bucle de Extracción Distribuida (Sharding)
    for db_url, db_key in db_configs:
        headers = {
            "apikey": db_key,
            "Authorization": f"Bearer {db_key}",
            "Content-Type": "application/json"
        }
        
        # 1. Extracción de Logística SRE (Filtro Estricto)
        ctrl_url = f"{db_url}/rest/v1/nexus_control?tipo_tarea=eq.AGENTE_TRADING&order=id.asc"
        try:
            ctrl_res = requests.get(ctrl_url, headers=headers, timeout=5)
            tasks = ctrl_res.json() if ctrl_res.status_code == 200 else []
        except: tasks = []

        # 2. Extracción de Finanzas (El Historial)
        hist_url = f"{db_url}/rest/v1/trade_history?select=agent_node,profit_usd"
        try:
            hist_res = requests.get(hist_url, headers=headers, timeout=5)
            history = hist_res.json() if hist_res.status_code == 200 else []
        except: history = []

        # 3. Fusión en Memoria
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

        # 4. Inyección Financiera en la Flota Unificada
        if isinstance(tasks, list):
            for c in tasks:
                nombre = str(c.get('nombre_tarea', '')).upper()
                
                # 🛡️ CERO HARDCODING GEOGRÁFICO: Detección dinámica de identidad
                # Ejemplo: Si el bot se llama "Agente Alpaca", node_key será "ALPACA"
                node_key = nombre.split()[-1] if " " in nombre else nombre
                
                # Retrocompatibilidad SRE para los 4 Biomas Clásicos de MT5
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
                
                all_agents.append(c)

    return render_template("index.html", agents=all_agents)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))