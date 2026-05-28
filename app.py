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

        # 2. Extracción de Finanzas Clásicas (MetaTrader) - Límite extendido a 5000
        hist_url = f"{db_url}/rest/v1/trade_history?select=agent_node,profit_usd&limit=5000"
        try:
            hist_res = requests.get(hist_url, headers=headers, timeout=5)
            history = hist_res.json() if hist_res.status_code == 200 else []
        except: history = []

        # 🛡️ ADAPTADOR ETL SRE 1: Tabla Trinidad (Agentes 1, 2 y 3)
        trin_url = f"{db_url}/rest/v1/trinidad_dashboard?select=agente,pnl_usdt&limit=5000"
        try:
            trin_res = requests.get(trin_url, headers=headers, timeout=5)
            trin_data = trin_res.json() if trin_res.status_code == 200 else []
            for d in trin_data:
                val_pnl = d.get("pnl_usdt")
                history.append({
                    "agent_node": d.get("agente", "UNKNOWN"),
                    "profit_usd": float(val_pnl) if val_pnl is not None else 0.0
                })
        except: pass

        # 🛡️ ADAPTADOR ETL SRE 2: Tabla Radar (Agente ScanPump)
        radar_url = f"{db_url}/rest/v1/nexus_radar_history?select=price_delta,cluster&limit=5000"
        try:
            radar_res = requests.get(radar_url, headers=headers, timeout=5)
            radar_data = radar_res.json() if radar_res.status_code == 200 else []
            for r in radar_data:
                # Filtro SRE: Destruir operaciones fantasma de simuladores
                if str(r.get("cluster", "")) == "Backtest_Discovery":
                    continue
                
                val_delta = r.get("price_delta")
                history.append({
                    "agent_node": "SCANPUMP", # 🛡️ Identidad Inyectada a la fuerza
                    "profit_usd": float(val_delta) if val_delta is not None else 0.0
                })
        except: pass

        # 3. Fusión en Memoria
        stats = {}
        if isinstance(history, list):
            for h in history:
                node = str(h.get('agent_node', 'UNKNOWN')).upper()
                val_profit = h.get('profit_usd')
                profit = float(val_profit) if val_profit is not None else 0.0
                
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
                ag_stats = {"pnl_total": 0.0, "trades": 0, "wins": 0}
                
                # 🛡️ ALGORITMO DE FUSIÓN SRE (Fuzzy Matching Alfanumérico)
                clean_nombre = ''.join(e for e in nombre if e.isalnum())
                
                for db_node, s in stats.items():
                    clean_node = ''.join(e for e in db_node if e.isalnum())
                    
                    # Coincidencia cruzada tolerante a espacios y guiones bajos
                    if clean_node in clean_nombre or clean_nombre in clean_node:
                        ag_stats = s; break
                    # Retrocompatibilidad SRE Biomas y Abreviaturas
                    if "NY" in clean_nombre and "NY" in clean_node: ag_stats = s; break
                    if "ASIA" in clean_nombre and "ASIA" in clean_node: ag_stats = s; break
                    if "EUROP" in clean_nombre and "EUROP" in clean_node: ag_stats = s; break
                    if "FOREX" in clean_nombre and "FOREX" in clean_node: ag_stats = s; break
                    if "MM" in clean_node and "MARKETMAKER" in clean_nombre: ag_stats = s; break
                win_rate = (ag_stats["wins"] / ag_stats["trades"] * 100) if ag_stats["trades"] > 0 else 0.0
                
                c['pnl_total'] = round(ag_stats["pnl_total"], 2)
                c['win_rate'] = round(win_rate, 1)
                c['trades_count'] = ag_stats["trades"]
                c['capital_asignado'] = float(c.get('capital_asignado') or 3000.0)
                
                all_agents.append(c)

    return render_template("index.html", agents=all_agents)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))