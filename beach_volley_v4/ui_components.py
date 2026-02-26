"""
ui_components.py — Stile DAZN Dark Mode + componenti riutilizzabili
"""
import streamlit as st
from data_manager import nome_squadra, get_squadra_by_id

# ─── CSS DARK MODE STILE DAZN ────────────────────────────────────────────────

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;800&family=Barlow:wght@400;500;600&display=swap');

    :root {
        --bg-primary: #0a0a0f;
        --bg-card: #13131a;
        --bg-card2: #1a1a24;
        --accent-red: #e8002d;
        --accent-blue: #0070f3;
        --accent-gold: #ffd700;
        --text-primary: #ffffff;
        --text-secondary: #a0a0b0;
        --border: #2a2a3a;
        --green: #00c851;
    }

    html, body, [class*="css"] {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-family: 'Barlow', sans-serif !important;
    }

    /* Nasconde elementi Streamlit di default */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1rem !important; max-width: 1200px !important; }

    /* HEADER TORNEO */
    .tournament-header {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #0a0a0f 100%);
        border-bottom: 3px solid var(--accent-red);
        padding: 20px 30px;
        text-align: center;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .tournament-header::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 300%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(232,0,45,0.05), transparent);
        animation: shimmer 4s infinite;
    }
    @keyframes shimmer { to { left: 100%; } }
    .tournament-title {
        font-family: 'Barlow Condensed', sans-serif !important;
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        letter-spacing: 3px !important;
        text-transform: uppercase !important;
        color: var(--text-primary) !important;
        margin: 0 !important;
    }
    .tournament-subtitle {
        color: var(--accent-red);
        font-size: 0.85rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        font-weight: 600;
        margin-top: 4px;
    }

    /* FASE BADGE */
    .fase-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: var(--bg-card2);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 6px 16px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--text-secondary);
        margin: 4px;
    }
    .fase-badge.active {
        background: var(--accent-red);
        border-color: var(--accent-red);
        color: white;
    }
    .fase-badge.done {
        background: var(--bg-card2);
        border-color: var(--green);
        color: var(--green);
    }

    /* MATCH CARD */
    .match-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0;
        margin-bottom: 12px;
        overflow: hidden;
        transition: border-color 0.2s;
    }
    .match-card:hover { border-color: #444; }
    .match-card.confirmed { border-left: 4px solid var(--green); }
    .match-card-header {
        background: var(--bg-card2);
        padding: 8px 16px;
        font-size: 0.7rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--text-secondary);
        font-weight: 600;
    }
    .match-body {
        padding: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .team-side {
        flex: 1;
        text-align: center;
    }
    .team-name {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .team-red .team-name { color: var(--accent-red); }
    .team-blue .team-name { color: var(--accent-blue); }
    .team-players {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin-top: 4px;
    }
    .score-center {
        text-align: center;
        min-width: 100px;
    }
    .score-sets {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: white;
        line-height: 1;
    }
    .score-sets span { color: var(--text-secondary); font-size: 2rem; }
    .score-parziale {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin-top: 4px;
    }
    .vs-label {
        font-size: 0.7rem;
        letter-spacing: 2px;
        color: var(--text-secondary);
        text-transform: uppercase;
    }

    /* CLASSIFICA TABLE */
    .rank-table { width: 100%; border-collapse: collapse; }
    .rank-table th {
        background: var(--bg-card2);
        color: var(--text-secondary);
        font-size: 0.7rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        padding: 10px 14px;
        text-align: center;
        border-bottom: 1px solid var(--border);
    }
    .rank-table td {
        padding: 12px 14px;
        text-align: center;
        border-bottom: 1px solid var(--border);
        font-size: 0.9rem;
    }
    .rank-table tr:hover td { background: var(--bg-card2); }
    .rank-pos { font-family: 'Barlow Condensed', sans-serif; font-weight: 800; font-size: 1.2rem; }
    .rank-pos.gold { color: var(--accent-gold); }
    .rank-pos.silver { color: #c0c0c0; }
    .rank-pos.bronze { color: #cd7f32; }

    /* PODIO */
    .podio-container {
        display: flex;
        align-items: flex-end;
        justify-content: center;
        gap: 12px;
        padding: 30px 0;
    }
    .podio-step {
        text-align: center;
        border-radius: 8px 8px 0 0;
        padding: 20px 24px 16px;
        min-width: 150px;
    }
    .podio-1 { background: linear-gradient(180deg, #b8860b, #ffd700); height: 180px; display: flex; flex-direction: column; justify-content: flex-end; }
    .podio-2 { background: linear-gradient(180deg, #808080, #c0c0c0); height: 140px; display: flex; flex-direction: column; justify-content: flex-end; }
    .podio-3 { background: linear-gradient(180deg, #8b4513, #cd7f32); height: 110px; display: flex; flex-direction: column; justify-content: flex-end; }
    .podio-rank { font-family: 'Barlow Condensed', sans-serif; font-size: 2rem; font-weight: 800; color: rgba(0,0,0,0.7); }
    .podio-name { font-weight: 700; font-size: 0.9rem; color: rgba(0,0,0,0.9); text-transform: uppercase; letter-spacing: 1px; }

    /* WINNER BANNER */
    .winner-banner {
        background: linear-gradient(135deg, #b8860b, #ffd700, #b8860b);
        border-radius: 12px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
        animation: pulse-gold 2s ease-in-out infinite;
    }
    @keyframes pulse-gold {
        0%, 100% { box-shadow: 0 0 20px rgba(255,215,0,0.4); }
        50% { box-shadow: 0 0 50px rgba(255,215,0,0.8); }
    }
    .winner-title {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 1rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: rgba(0,0,0,0.7);
        font-weight: 600;
    }
    .winner-name {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: #000;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .winner-players { color: rgba(0,0,0,0.8); font-size: 1rem; font-weight: 600; }

    /* CAREER CARD */
    .career-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
    }
    .career-name {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
        gap: 12px;
        margin-top: 16px;
    }
    .stat-box {
        background: var(--bg-card2);
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    .stat-value {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--accent-blue);
    }
    .stat-label {
        font-size: 0.65rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--text-secondary);
        margin-top: 4px;
    }

    /* BUTTONS */
    .stButton > button {
        background: var(--accent-red) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-family: 'Barlow Condensed', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        font-size: 0.85rem !important;
        padding: 10px 20px !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: #ff1a45 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(232,0,45,0.4) !important;
    }

    /* INPUTS */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        background: var(--bg-card2) !important;
        border: 1px solid var(--border) !important;
        color: white !important;
        border-radius: 6px !important;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background: var(--bg-card) !important;
        border-right: 1px solid var(--border) !important;
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] { background: transparent !important; gap: 4px !important; }
    .stTabs [data-baseweb="tab"] {
        background: var(--bg-card2) !important;
        color: var(--text-secondary) !important;
        border-radius: 6px 6px 0 0 !important;
        border: 1px solid var(--border) !important;
        font-family: 'Barlow Condensed', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--accent-red) !important;
        color: white !important;
        border-color: var(--accent-red) !important;
    }

    /* DIVIDER */
    hr { border-color: var(--border) !important; }

    /* METRIC */
    [data-testid="metric-container"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ─── HEADER ──────────────────────────────────────────────────────────────────

def render_header(state):
    nome = state["torneo"]["nome"] or "Beach Volley"
    st.markdown(f"""
    <div class="tournament-header">
        <div class="tournament-title">🏐 {nome}</div>
        <div class="tournament-subtitle">Tournament Manager Pro</div>
    </div>
    """, unsafe_allow_html=True)
    
    fasi = [("setup","⚙️ Setup"), ("gironi","🔵 Gironi"), ("eliminazione","⚡ Eliminazione"), ("proclamazione","🏆 Finale")]
    stati = []
    fase_corrente = state["fase"]
    ordine = ["setup","gironi","eliminazione","proclamazione"]
    idx_corrente = ordine.index(fase_corrente)
    
    html = '<div style="display:flex;justify-content:center;flex-wrap:wrap;gap:8px;margin-bottom:20px;">'
    for i, (k, label) in enumerate(fasi):
        if i < idx_corrente:
            css = "fase-badge done"
            icon = "✓ "
        elif i == idx_corrente:
            css = "fase-badge active"
            icon = ""
        else:
            css = "fase-badge"
            icon = ""
        html += f'<span class="{css}">{icon}{label}</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ─── MATCH CARD ──────────────────────────────────────────────────────────────

def render_match_card(state, partita, label=""):
    sq1 = get_squadra_by_id(state, partita["sq1"])
    sq2 = get_squadra_by_id(state, partita["sq2"])
    if not sq1 or not sq2:
        return
    
    def players_str(sq):
        from data_manager import get_atleta_by_id
        names = [get_atleta_by_id(state, aid)["nome"] for aid in sq["atleti"] if get_atleta_by_id(state, aid)]
        return " / ".join(names)
    
    parziali = " | ".join([f"{p[0]}-{p[1]}" for p in partita["punteggi"]]) if partita["punteggi"] else "—"
    confirmed_class = "confirmed" if partita["confermata"] else ""
    
    st.markdown(f"""
    <div class="match-card {confirmed_class}">
        <div class="match-card-header">{label} {'✅ CONFERMATA' if partita["confermata"] else '🔴 LIVE'}</div>
        <div class="match-body">
            <div class="team-side team-red">
                <div class="team-name">{sq1['nome']}</div>
                <div class="team-players">{players_str(sq1)}</div>
            </div>
            <div class="score-center">
                <div class="score-sets">
                    <span style="color:var(--accent-red)">{partita['set_sq1']}</span>
                    <span>–</span>
                    <span style="color:var(--accent-blue)">{partita['set_sq2']}</span>
                </div>
                <div class="score-parziale">{parziali}</div>
            </div>
            <div class="team-side team-blue">
                <div class="team-name">{sq2['nome']}</div>
                <div class="team-players">{players_str(sq2)}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── PODIO ───────────────────────────────────────────────────────────────────

def render_podio(state, podio):
    """podio = [(pos, sq_id), ...]"""
    def sq_info(sid):
        sq = get_squadra_by_id(state, sid)
        from data_manager import get_atleta_by_id
        if not sq: return "?", "?"
        names = [get_atleta_by_id(state, aid)["nome"] for aid in sq["atleti"] if get_atleta_by_id(state, aid)]
        return sq["nome"], " / ".join(names)
    
    podio_dict = {pos: sid for pos, sid in podio}
    
    items = []
    for pos in [2, 1, 3]:
        if pos in podio_dict:
            nome_sq, players = sq_info(podio_dict[pos])
            items.append((pos, nome_sq, players))
    
    html = '<div class="podio-container">'
    for pos, nome_sq, players in items:
        css = f"podio-{pos}"
        medal = {1:"🥇",2:"🥈",3:"🥉"}[pos]
        html += f"""
        <div class="podio-step {css}">
            <div class="podio-name">{nome_sq}</div>
            <div style="font-size:0.7rem;color:rgba(0,0,0,0.7);margin-top:2px">{players}</div>
            <div class="podio-rank">{medal}</div>
        </div>"""
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ─── WINNER BANNER ───────────────────────────────────────────────────────────

def render_winner_banner(state, vincitore_sq_id):
    sq = get_squadra_by_id(state, vincitore_sq_id)
    if not sq: return
    from data_manager import get_atleta_by_id
    names = [get_atleta_by_id(state, aid)["nome"] for aid in sq["atleti"] if get_atleta_by_id(state, aid)]
    st.markdown(f"""
    <div class="winner-banner">
        <div class="winner-title">🏆 Campioni del Torneo 🏆</div>
        <div class="winner-name">{sq['nome']}</div>
        <div class="winner-players">{' & '.join(names)}</div>
    </div>
    """, unsafe_allow_html=True)


# ─── CAREER CARD ─────────────────────────────────────────────────────────────

def render_career_card(atleta):
    s = atleta["stats"]
    quoziente = round(s["punti_fatti"] / max(s["set_vinti"], 1), 2)
    win_rate = round(s["vittorie"] / max(s["tornei"], 1) * 100, 1)
    
    st.markdown(f"""
    <div class="career-card">
        <div class="career-name">👤 {atleta['nome']}</div>
        <div class="stat-grid">
            <div class="stat-box"><div class="stat-value">{s['tornei']}</div><div class="stat-label">Tornei</div></div>
            <div class="stat-box"><div class="stat-value" style="color:var(--green)">{s['vittorie']}</div><div class="stat-label">Vinti</div></div>
            <div class="stat-box"><div class="stat-value" style="color:var(--accent-red)">{s['sconfitte']}</div><div class="stat-label">Persi</div></div>
            <div class="stat-box"><div class="stat-value">{s['set_vinti']}</div><div class="stat-label">Set Vinti</div></div>
            <div class="stat-box"><div class="stat-value">{s['set_persi']}</div><div class="stat-label">Set Persi</div></div>
            <div class="stat-box"><div class="stat-value" style="color:var(--accent-gold)">{quoziente}</div><div class="stat-label">Quot. Punti/Set</div></div>
            <div class="stat-box"><div class="stat-value">{win_rate}%</div><div class="stat-label">Win Rate</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
