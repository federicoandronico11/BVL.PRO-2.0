"""
ranking_page.py — Ranking globale + card FIFA + trofei + schede carriera v4
"""
import streamlit as st
import pandas as pd
from data_manager import (
    get_atleta_by_id, get_squadra_by_id, save_state,
    calcola_overall_fifa, get_card_type, get_trofei_atleta, TROFEI_DEFINIZIONE
)


def calcola_punti_ranking(pos, n_squadre):
    pts_massimi = n_squadre * 10
    return max(0, pts_massimi - ((pos - 1) * 10))


def build_ranking_data(state):
    atleti_stats = []
    for a in state["atleti"]:
        s = a["stats"]
        if s["tornei"] == 0:
            continue
        rank_pts = sum(
            calcola_punti_ranking(pos, _get_n_squadre_torneo(state, tn))
            for tn, pos in s["storico_posizioni"]
        )
        quoziente_punti = round(s["punti_fatti"] / max(s["set_vinti"] + s["set_persi"], 1), 2)
        quoziente_set = round(s["set_vinti"] / max(s["set_persi"], 1), 2)
        win_rate = round(s["vittorie"] / max(s["tornei"], 1) * 100, 1)
        medaglie_oro = sum(1 for _, pos in s["storico_posizioni"] if pos == 1)
        medaglie_argento = sum(1 for _, pos in s["storico_posizioni"] if pos == 2)
        medaglie_bronzo = sum(1 for _, pos in s["storico_posizioni"] if pos == 3)
        overall = calcola_overall_fifa(a)
        card_type = get_card_type(overall, s["tornei"], s["vittorie"])
        atleti_stats.append({
            "atleta": a, "id": a["id"], "nome": a["nome"],
            "tornei": s["tornei"], "vittorie": s["vittorie"], "sconfitte": s["sconfitte"],
            "set_vinti": s["set_vinti"], "set_persi": s["set_persi"],
            "punti_fatti": s["punti_fatti"], "punti_subiti": s["punti_subiti"],
            "quoziente_punti": quoziente_punti, "quoziente_set": quoziente_set,
            "win_rate": win_rate, "rank_pts": rank_pts,
            "oro": medaglie_oro, "argento": medaglie_argento, "bronzo": medaglie_bronzo,
            "storico": s["storico_posizioni"],
            "overall": overall, "card_type": card_type,
        })
    atleti_stats.sort(key=lambda x: (-x["rank_pts"], -x["oro"], -x["argento"], -x["win_rate"]))
    return atleti_stats


def _get_n_squadre_torneo(state, torneo_nome):
    return max(len(state["squadre"]), 4)


def render_ranking_page(state):
    st.markdown("## 🏅 Ranking Globale")
    ranking = build_ranking_data(state)
    if not ranking:
        st.info("Completa almeno un torneo per visualizzare il ranking.")
        return
    tabs = st.tabs(["🏆 Classifica", "🃏 Card Giocatori", "🏅 Trofei", "👤 Carriera", "📄 Esporta PDF"])
    with tabs[0]:
        _render_classifica_completa(state, ranking)
    with tabs[1]:
        _render_carte_fifa(state, ranking)
    with tabs[2]:
        _render_trofei_page(state, ranking)
    with tabs[3]:
        _render_schede_atleti(state, ranking)
    with tabs[4]:
        _render_export_ranking_pdf(state, ranking)


def build_ranking_data_all(state):
    return build_ranking_data(state)


# ─── CARD HTML GENERATOR ─────────────────────────────────────────────────────

CARD_CONFIGS = {
    "bronzo_comune": {
        "label": "BRONZO",
        "bg": "linear-gradient(160deg,#3d2200 0%,#7a4a1a 35%,#CD853F 60%,#5C3317 100%)",
        "tc": "rgba(255,240,200,0.95)",
        "border": "#8B5A2B",
        "glow": "rgba(139,90,43,0.4)",
        "badge_bg": "rgba(0,0,0,0.3)",
        "badge_color": "#FFD580",
        "extra_html": "",
    },
    "bronzo_raro": {
        "label": "BRONZO RARO",
        "bg": "linear-gradient(160deg,#2d1500 0%,#8B4513 30%,#D2691E 55%,#FF8C00 75%,#8B4513 100%)",
        "tc": "rgba(255,240,200,0.95)",
        "border": "#FF8C00",
        "glow": "rgba(255,140,0,0.5)",
        "badge_bg": "rgba(255,100,0,0.25)",
        "badge_color": "#FF8C00",
        "extra_html": '<div style="position:absolute;top:0;left:0;right:0;bottom:0;background:repeating-linear-gradient(45deg,transparent,transparent 8px,rgba(255,140,0,0.05) 8px,rgba(255,140,0,0.05) 16px);border-radius:14px;pointer-events:none"></div>',
    },
    "argento_comune": {
        "label": "ARGENTO",
        "bg": "linear-gradient(160deg,#2a2a2a 0%,#666 35%,#C0C0C0 60%,#888 100%)",
        "tc": "rgba(255,255,255,0.95)",
        "border": "#C0C0C0",
        "glow": "rgba(192,192,192,0.4)",
        "badge_bg": "rgba(255,255,255,0.15)",
        "badge_color": "#E8E8E8",
        "extra_html": "",
    },
    "argento_raro": {
        "label": "ARGENTO RARO",
        "bg": "linear-gradient(160deg,#0a1628 0%,#1C3A7A 30%,#4169E1 55%,#6495ED 75%,#1C3A7A 100%)",
        "tc": "rgba(220,240,255,0.95)",
        "border": "#4169E1",
        "glow": "rgba(65,105,225,0.6)",
        "badge_bg": "rgba(65,105,225,0.25)",
        "badge_color": "#87CEEB",
        "extra_html": '<div style="position:absolute;top:4px;right:4px;font-size:0.5rem;opacity:0.6;color:#87CEEB">✦ ✦ ✦</div>',
    },
    "oro_comune": {
        "label": "ORO",
        "bg": "linear-gradient(160deg,#3d2e00 0%,#8B6914 30%,#FFD700 55%,#B8860B 100%)",
        "tc": "rgba(0,0,0,0.9)",
        "border": "#FFD700",
        "glow": "rgba(255,215,0,0.5)",
        "badge_bg": "rgba(255,215,0,0.25)",
        "badge_color": "#8B6914",
        "extra_html": "",
    },
    "oro_raro": {
        "label": "ORO RARO ✨",
        "bg": "linear-gradient(160deg,#2d1a00 0%,#7B4F00 25%,#FFD700 45%,#FFA500 65%,#7B4F00 100%)",
        "tc": "rgba(0,0,0,0.9)",
        "border": "#FFA500",
        "glow": "rgba(255,165,0,0.7)",
        "badge_bg": "rgba(255,165,0,0.25)",
        "badge_color": "#FF8C00",
        "extra_html": '<div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,transparent,#FFD700,#FFA500,#FFD700,transparent);border-radius:14px 14px 0 0"></div>',
    },
    "eroe": {
        "label": "⚡ EROE",
        "bg": "linear-gradient(160deg,#1a0033 0%,#4a0080 30%,#8B00FF 55%,#CC00FF 75%,#4a0080 100%)",
        "tc": "rgba(240,200,255,0.95)",
        "border": "#CC00FF",
        "glow": "rgba(150,0,255,0.7)",
        "badge_bg": "rgba(200,0,255,0.2)",
        "badge_color": "#E066FF",
        "extra_html": '<div style="position:absolute;top:0;left:0;right:0;bottom:0;background:radial-gradient(ellipse at 50% 30%,rgba(200,0,255,0.15),transparent 70%);border-radius:14px;pointer-events:none"></div><div style="position:absolute;top:3px;left:50%;transform:translateX(-50%);font-size:0.55rem;color:#E066FF;letter-spacing:3px;opacity:0.8">⬡ ⬡ ⬡ ⬡ ⬡</div>',
    },
    "leggenda": {
        "label": "👑 LEGGENDA",
        "bg": "linear-gradient(160deg,#1a1000 0%,#4a3800 20%,#F0E0A0 45%,#FFF8DC 60%,#FF8C00 80%,#4a3800 100%)",
        "tc": "rgba(0,0,0,0.9)",
        "border": "#FFF8DC",
        "glow": "rgba(255,248,220,0.8)",
        "badge_bg": "rgba(255,200,0,0.2)",
        "badge_color": "#8B6914",
        "extra_html": '<div style="position:absolute;top:0;left:0;right:0;bottom:0;background:radial-gradient(ellipse at 50% 20%,rgba(255,248,220,0.3),transparent 60%);border-radius:14px;pointer-events:none"></div><div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,#FFF8DC,#FF8C00,#FFF8DC,transparent);border-radius:14px 14px 0 0"></div><div style="position:absolute;bottom:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,#FF8C00,#FFF8DC,#FF8C00,transparent);border-radius:0 0 14px 14px"></div>',
    },
    "dio_olimpo": {
        "label": "⚡🌩️ DIO DELL'OLIMPO",
        "bg": "linear-gradient(160deg,#000510 0%,#001a40 20%,#0040A0 40%,#0080FF 55%,#00C0FF 65%,#FFD700 80%,#001a40 100%)",
        "tc": "rgba(220,245,255,0.97)",
        "border": "#00C8FF",
        "glow": "rgba(0,200,255,0.9)",
        "badge_bg": "rgba(0,150,255,0.2)",
        "badge_color": "#00E5FF",
        "extra_html": '<div style="position:absolute;top:0;left:0;right:0;bottom:0;pointer-events:none;border-radius:14px;overflow:hidden"><div style="position:absolute;top:0;left:0;right:0;bottom:0;background:radial-gradient(ellipse at 50% 0%,rgba(0,200,255,0.3),transparent 60%);animation:pulse_glow 2s ease-in-out infinite"></div><div style="position:absolute;top:-5px;left:-5px;right:-5px;bottom:-5px;border:2px solid rgba(0,200,255,0.4);border-radius:16px;animation:border_pulse 2s ease-in-out infinite"></div><div style="position:absolute;top:2px;left:10px;font-size:0.6rem;color:rgba(0,200,255,0.7);animation:float_wings 3s ease-in-out infinite">🪶</div><div style="position:absolute;top:2px;right:10px;font-size:0.6rem;color:rgba(0,200,255,0.7);animation:float_wings 3s ease-in-out infinite 0.5s">🪶</div><div style="position:absolute;bottom:8px;left:8px;font-size:0.55rem;color:rgba(255,215,0,0.5)">⚡</div><div style="position:absolute;bottom:8px;right:8px;font-size:0.55rem;color:rgba(255,215,0,0.5)">⚡</div></div>',
    },
}

CARD_ANIMATIONS = """
<style>
@keyframes pulse_glow { 0%,100%{opacity:0.5} 50%{opacity:1} }
@keyframes border_pulse { 0%,100%{box-shadow:0 0 10px rgba(0,200,255,0.3)} 50%{box-shadow:0 0 25px rgba(0,200,255,0.7)} }
@keyframes float_wings { 0%,100%{transform:translateY(0) rotate(-15deg)} 50%{transform:translateY(-3px) rotate(-10deg)} }
@keyframes card_hover { from{transform:scale(1) translateY(0)} to{transform:scale(1.03) translateY(-4px)} }
</style>
"""

def render_card_html(a, size="normal", clickable=True):
    """Genera HTML per una card giocatore con nuovo sistema tier."""
    ct = a["card_type"]
    cfg = CARD_CONFIGS.get(ct, CARD_CONFIGS["bronzo_comune"])
    s = a["atleta"]["stats"]
    overall = a["overall"]

    card_w = "200px" if size == "normal" else "160px"
    card_p = "0 0 14px 0" if size == "normal" else "0 0 10px 0"
    ovr_size = "3.5rem" if size == "normal" else "2.8rem"
    name_size = "1rem" if size == "normal" else "0.85rem"
    attr_size = "0.72rem" if size == "normal" else "0.62rem"

    foto_html = ""
    foto_height = "90px" if size == "normal" else "75px"
    if a["atleta"].get("foto_b64"):
        foto_html = f'<img src="data:image/png;base64,{a["atleta"]["foto_b64"]}" style="width:100%;height:{foto_height};object-fit:cover;display:block">'
    else:
        foto_html = f'<div style="width:100%;height:{foto_height};background:linear-gradient(180deg,rgba(0,0,0,0.4),rgba(0,0,0,0.6));display:flex;align-items:center;justify-content:center;font-size:2rem">👤</div>'

    attrs_html = ""
    for attr, icon in [("attacco","ATT"),("difesa","DIF"),("muro","MUR"),("ricezione","RIC"),("battuta","BAT"),("alzata","ALZ")]:
        val = s.get(attr, 50)
        attrs_html += f'<div style="display:flex;justify-content:space-between;padding:1px 6px;font-size:{attr_size};font-weight:800"><span style="opacity:0.8">{icon}</span><span>{val}</span></div>'

    cursor = "cursor:pointer;" if clickable else ""
    hover_id = f"card_{a['id']}"

    return f"""
<div id="{hover_id}" style="position:relative;background:{cfg['bg']};border:2px solid {cfg['border']};
    border-radius:14px;width:{card_w};padding:{card_p};text-align:center;color:{cfg['tc']};
    box-shadow:0 6px 30px {cfg['glow']},0 2px 8px rgba(0,0,0,0.6);
    transition:transform 0.25s ease,box-shadow 0.25s ease;{cursor}overflow:hidden;
    font-family:'Barlow Condensed',sans-serif"
    onmouseover="this.style.transform='scale(1.04) translateY(-4px)';this.style.boxShadow='0 12px 40px {cfg['glow']},0 4px 15px rgba(0,0,0,0.8)'"
    onmouseout="this.style.transform='scale(1) translateY(0)';this.style.boxShadow='0 6px 30px {cfg['glow']},0 2px 8px rgba(0,0,0,0.6)'">
    {cfg['extra_html']}
    <!-- Foto superiore -->
    <div style="position:relative;overflow:hidden;border-radius:12px 12px 0 0">
        {foto_html}
        <!-- OVR overlay in alto a destra -->
        <div style="position:absolute;top:4px;right:6px;background:rgba(0,0,0,0.65);backdrop-filter:blur(4px);
            border-radius:6px;padding:1px 6px;line-height:1">
            <div style="font-size:{ovr_size};font-weight:900;line-height:1;color:{cfg['badge_color']};
                font-family:'Barlow Condensed',sans-serif;text-shadow:0 2px 6px rgba(0,0,0,0.8)">{overall}</div>
            <div style="font-size:0.5rem;letter-spacing:2px;font-weight:700;opacity:0.9">OVR</div>
        </div>
        <!-- Label tipo in alto a sinistra -->
        <div style="position:absolute;top:4px;left:6px;background:{cfg['badge_bg']};
            backdrop-filter:blur(4px);border-radius:4px;padding:2px 5px">
            <div style="font-size:0.42rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;opacity:0.9">{cfg['label']}</div>
        </div>
    </div>
    <!-- Nome giocatore -->
    <div style="font-size:{name_size};font-weight:900;text-transform:uppercase;letter-spacing:1.5px;
        padding:7px 6px 5px;border-bottom:1px solid rgba(255,255,255,0.15)">{a['nome']}</div>
    <!-- Attributi -->
    <div style="background:rgba(0,0,0,0.2);padding:4px 0;margin-top:2px">{attrs_html}</div>
    <!-- Footer stats -->
    <div style="font-size:0.55rem;opacity:0.75;padding:4px 6px 0;display:flex;justify-content:space-around">
        <span>🥇{a['oro']}</span>
        <span>🎮{a['tornei']}</span>
        <span>{a['win_rate']}%WR</span>
    </div>
</div>
"""


def _render_classifica_completa(state, ranking):
    n_sq = len(state["squadre"])
    st.markdown(f"""
    <div style="background:var(--bg-card2);border:1px solid var(--border);border-radius:var(--radius);
        padding:12px 20px;margin-bottom:20px;font-size:0.8rem;color:var(--text-secondary)">
        💡 <strong>Formula punti:</strong> {n_sq} squadre × 10 =
        <strong style="color:var(--accent-gold)">{n_sq*10} pt per il 1°</strong>
        · Ogni posizione successiva: -10 pt
    </div>
    """, unsafe_allow_html=True)

    if len(ranking) >= 3:
        col1, col2, col3 = st.columns(3)
        podio_cols = [(col2, ranking[0], "🥇", "#ffd700", "1°"),
                      (col1, ranking[1], "🥈", "#c0c0c0", "2°"),
                      (col3, ranking[2], "🥉", "#cd7f32", "3°")]
        for col, atleta, medal, color, pos in podio_cols:
            with col:
                overall = atleta["overall"]
                st.markdown(f"""
                <div style="background:var(--bg-card);border:2px solid {color};
                    border-radius:var(--radius);padding:20px;text-align:center;
                    margin-top:{'0' if pos=='1°' else '20px'}">
                    <div style="font-size:2.5rem">{medal}</div>
                    <div style="font-family:var(--font-display);font-size:1.3rem;font-weight:800;color:{color}">{atleta['nome']}</div>
                    <div style="color:var(--text-secondary);font-size:0.85rem;margin:4px 0">{atleta['rank_pts']} pt</div>
                    <div style="font-size:0.75rem;color:{color}">🥇{atleta['oro']} 🥈{atleta['argento']} 🥉{atleta['bronzo']}</div>
                    <div style="background:rgba(255,215,0,0.15);border-radius:8px;padding:4px 10px;margin-top:8px;display:inline-block">
                        <span style="font-weight:800;color:var(--accent-gold);font-size:0.9rem">OVR {overall}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabella con link a profilo
    st.markdown("""
    <style>
    .rank-row-link { cursor:pointer; transition:background 0.2s; }
    .rank-row-link:hover { background:rgba(232,0,45,0.08) !important; }
    </style>
    """, unsafe_allow_html=True)

    html = """
    <table class="rank-table">
    <tr>
        <th>#</th><th style="text-align:left">ATLETA</th>
        <th>OVR</th><th>PTS</th><th>T</th><th>🥇</th><th>🥈</th><th>🥉</th>
        <th>V</th><th>P</th><th>SV</th><th>SP</th><th>WIN%</th>
    </tr>"""
    pos_cls = {1: "gold", 2: "silver", 3: "bronze"}
    card_icons = {
        "bronzo_comune":"🟫","bronzo_raro":"🟤","argento_comune":"⬜","argento_raro":"🔵",
        "oro_comune":"🟨","oro_raro":"🌟","eroe":"💜","leggenda":"🤍","dio_olimpo":"⚡"
    }
    for i, a in enumerate(ranking):
        pos = i + 1
        cls = pos_cls.get(pos, "")
        card_icon = card_icons.get(a["card_type"], "")
        html += f"""<tr class="rank-row-link" onclick="window.parent.postMessage({{type:'profile_click',id:'{a['id']}'}}, '*')">
            <td><span class="rank-pos {cls}">{pos}</span></td>
            <td style="text-align:left;font-weight:700">{card_icon} {a['nome']}</td>
            <td style="font-weight:800;color:var(--accent-gold)">{a['overall']}</td>
            <td style="font-weight:800;color:var(--accent-gold)">{a['rank_pts']}</td>
            <td>{a['tornei']}</td>
            <td style="color:#ffd700">{a['oro']}</td>
            <td style="color:#c0c0c0">{a['argento']}</td>
            <td style="color:#cd7f32">{a['bronzo']}</td>
            <td style="color:var(--green)">{a['vittorie']}</td>
            <td style="color:var(--accent1)">{a['sconfitte']}</td>
            <td>{a['set_vinti']}</td><td>{a['set_persi']}</td>
            <td>{a['win_rate']}%</td>
        </tr>"""
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

    st.divider()
    st.markdown("### 📊 Statistiche Rapide — Clicca un atleta")
    sel_nome = st.selectbox("Seleziona giocatore", [a["nome"] for a in ranking], key="quick_stats_sel")
    a_sel = next((a for a in ranking if a["nome"] == sel_nome), None)
    if a_sel:
        col_card, col_stats = st.columns([1, 2])
        with col_card:
            st.markdown(CARD_ANIMATIONS, unsafe_allow_html=True)
            st.markdown(render_card_html(a_sel, size="normal", clickable=False), unsafe_allow_html=True)
        with col_stats:
            _render_quick_stats(a_sel, state)
        if st.button("👤 Vai al Profilo Completo →", key="goto_profile_quick"):
            st.session_state.profilo_atleta_id = a_sel["id"]
            st.session_state.current_page = "profili"
            st.rerun()


def _render_quick_stats(a, state):
    s = a["atleta"]["stats"]
    cols = st.columns(4)
    metrics = [
        ("🏆 Rank Pts", a["rank_pts"], ""),
        ("🎮 Tornei", a["tornei"], ""),
        ("🥇 Vittorie", a["vittorie"], f"{a['win_rate']}%"),
        ("📊 Overall", a["overall"], a["card_type"].replace("_"," ").upper()),
    ]
    for col, (label, val, delta) in zip(cols, metrics):
        with col:
            st.metric(label, val, delta if delta else None)

    col_stats = st.columns(6)
    attrs = ["attacco","difesa","muro","ricezione","battuta","alzata"]
    icons = ["⚡","🛡️","🧱","🤲","🏐","🎯"]
    for col, attr, icon in zip(col_stats, attrs, icons):
        with col:
            val = s.get(attr, 50)
            color = "#00c851" if val >= 75 else "#ffd700" if val >= 65 else "#a0a0b0"
            st.markdown(f"""
            <div style="background:var(--bg-card2);border-radius:var(--radius);padding:10px;text-align:center">
                <div style="font-size:1.2rem">{icon}</div>
                <div style="font-family:var(--font-display);font-size:1.5rem;font-weight:800;color:{color}">{val}</div>
                <div style="font-size:0.6rem;color:var(--text-secondary);letter-spacing:1px;text-transform:uppercase">{attr}</div>
            </div>
            """, unsafe_allow_html=True)


def _render_carte_fifa(state, ranking):
    st.markdown("### 🃏 Card Giocatori")
    st.markdown(CARD_ANIMATIONS, unsafe_allow_html=True)
    st.caption("Le card riflettono le statistiche accumulate nei tornei. Clicca una card per andare al profilo!")

    cols_per_row = 4
    for row_start in range(0, len(ranking), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, a in enumerate(ranking[row_start:row_start+cols_per_row]):
            with cols[j]:
                st.markdown(render_card_html(a, size="normal", clickable=True), unsafe_allow_html=True)
                if st.button(f"👤 Profilo", key=f"card_goto_{a['id']}", use_container_width=True):
                    st.session_state.profilo_atleta_id = a["id"]
                    st.session_state.current_page = "profili"
                    st.rerun()
                foto_up = st.file_uploader(f"📷 Foto", type=["png","jpg","jpeg"], key=f"foto_{a['id']}", label_visibility="collapsed")
                if foto_up:
                    import base64
                    a["atleta"]["foto_b64"] = base64.b64encode(foto_up.read()).decode()
                    save_state(state)
                    st.rerun()


def _render_trofei_page(state, ranking):
    st.markdown("### 🏅 Trofei Giocatori")
    if not ranking:
        st.info("Completa tornei per sbloccare trofei.")
        return

    tutti_atleti = {a["nome"]: a["atleta"] for a in ranking}
    sel = st.selectbox("Seleziona giocatore", list(tutti_atleti.keys()), key="trofei_sel")
    atleta = tutti_atleti[sel]
    trofei = get_trofei_atleta(atleta)

    sbloccati = sum(1 for _, unlocked in trofei if unlocked)
    st.markdown(f"""
    <div style="background:var(--bg-card2);border:1px solid var(--border);border-radius:var(--radius);
        padding:14px 20px;margin-bottom:20px;display:flex;justify-content:space-between;align-items:center">
        <div>
            <div style="font-family:var(--font-display);font-size:1.5rem;font-weight:800">{atleta['nome']}</div>
            <div style="color:var(--text-secondary);font-size:0.8rem">{sbloccati}/{len(trofei)} trofei sbloccati</div>
        </div>
        <div style="text-align:center">
            <div style="font-size:2rem;font-weight:900;color:var(--accent-gold)">{sbloccati}</div>
            <div style="font-size:0.7rem;color:var(--text-secondary);letter-spacing:2px">TROFEI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    perc = int(sbloccati / len(trofei) * 100)
    st.markdown(f"""
    <div style="background:var(--border);border-radius:10px;height:8px;margin-bottom:20px;overflow:hidden">
        <div style="background:linear-gradient(90deg,var(--accent1),var(--accent-gold));height:100%;width:{perc}%;border-radius:10px;transition:width 0.5s"></div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    for i, (trofeo, sbloccato) in enumerate(trofei):
        with cols[i % 4]:
            rarità_colors = {
                "comune": "#cd7f32", "non comune": "#c0c0c0",
                "raro": "#ffd700", "epico": "#e040fb", "leggendario": "#00f5ff"
            }
            tc = rarità_colors.get(trofeo["rarità"], "#888")
            locked_filter = "" if sbloccato else "filter:grayscale(100%) opacity(0.4);"

            st.markdown(f"""
            <div title="{trofeo['descrizione']}" style="background:{trofeo['sfondo'] if sbloccato else 'var(--bg-card2)'};
                border:2px solid {tc if sbloccato else 'var(--border)'};
                border-radius:12px;padding:16px;text-align:center;margin-bottom:8px;
                {locked_filter}
                {'box-shadow:0 0 20px ' + tc + '40;' if sbloccato else ''}
                transition:all 0.3s;cursor:help">
                <div style="font-size:2.5rem;margin-bottom:6px">{trofeo['icona']}</div>
                <div style="font-weight:800;font-size:0.85rem;color:{'rgba(0,0,0,0.9)' if sbloccato else 'var(--text-primary)'};
                    text-transform:uppercase;letter-spacing:1px">{trofeo['nome']}</div>
                <div style="font-size:0.65rem;margin-top:4px;color:{'rgba(0,0,0,0.7)' if sbloccato else 'var(--text-secondary)'}">
                    {trofeo['descrizione']}</div>
                <div style="margin-top:8px;font-size:0.55rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;
                    color:{'rgba(0,0,0,0.6)' if sbloccato else tc}">
                    {trofeo['rarità'].upper()}</div>
                {'<div style="margin-top:6px;font-size:0.8rem;font-weight:700;color:rgba(0,0,0,0.8)">✓ SBLOCCATO</div>' if sbloccato else '<div style="margin-top:6px;font-size:0.7rem;color:var(--text-secondary)">🔒 Bloccato</div>'}
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🏆 Bacheca Globale Trofei")
    _render_global_trophy_board(state, ranking)


def _render_global_trophy_board(state, ranking):
    if not ranking: return
    html = '<table class="rank-table"><tr><th style="text-align:left">GIOCATORE</th>'
    for t in TROFEI_DEFINIZIONE:
        html += f'<th title="{t["descrizione"]}">{t["icona"]}</th>'
    html += '</tr>'
    for a_data in ranking:
        atleta = a_data["atleta"]
        trofei = get_trofei_atleta(atleta)
        html += f'<tr><td style="text-align:left;font-weight:700">{atleta["nome"]}</td>'
        for trofeo, sbloccato in trofei:
            if sbloccato:
                html += f'<td title="{trofeo["nome"]}">✅</td>'
            else:
                html += '<td style="opacity:0.2">🔒</td>'
        html += '</tr>'
    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)


def _render_schede_atleti(state, ranking, atleta_id_preselect=None):
    if not ranking: return

    # Gestione navigazione diretta da card
    nomi = [a["nome"] for a in ranking]
    default_idx = 0
    if atleta_id_preselect:
        for i, a in enumerate(ranking):
            if a["id"] == atleta_id_preselect:
                default_idx = i
                break
    elif st.session_state.get("profilo_atleta_id"):
        for i, a in enumerate(ranking):
            if a["id"] == st.session_state.profilo_atleta_id:
                default_idx = i
                break

    sel = st.selectbox("🔍 Seleziona Atleta", nomi, index=default_idx, key="rank_career_sel")
    a = next((x for x in ranking if x["nome"] == sel), None)
    if not a: return

    # Sezione modifica profilo
    with st.expander("✏️ Modifica Profilo Atleta", expanded=False):
        _render_modifica_profilo(state, a["atleta"])

    col_card, col_stats = st.columns([1, 2])
    with col_card:
        st.markdown(CARD_ANIMATIONS, unsafe_allow_html=True)
        st.markdown(render_card_html(a, size="normal", clickable=False), unsafe_allow_html=True)
    with col_stats:
        s = a["atleta"]["stats"]
        st.markdown(f"""
        <div class="career-card">
            <div class="career-name">👤 {a['nome']}</div>
            <div style="color:var(--accent-gold);font-size:0.85rem;margin-top:4px">
                🏅 {a['rank_pts']} punti ranking · OVR {a['overall']}
            </div>
            <div class="stat-grid">
                <div class="stat-box"><div class="stat-value" style="color:var(--accent-gold)">{a['rank_pts']}</div><div class="stat-label">Rank Pts</div></div>
                <div class="stat-box"><div class="stat-value">{a['tornei']}</div><div class="stat-label">Tornei</div></div>
                <div class="stat-box"><div class="stat-value" style="color:var(--green)">{a['vittorie']}</div><div class="stat-label">Vittorie</div></div>
                <div class="stat-box"><div class="stat-value">{a['win_rate']}%</div><div class="stat-label">Win Rate</div></div>
                <div class="stat-box"><div class="stat-value">{a['set_vinti']}</div><div class="stat-label">Set Vinti</div></div>
                <div class="stat-box"><div class="stat-value">{a['set_persi']}</div><div class="stat-label">Set Persi</div></div>
                <div class="stat-box"><div class="stat-value">{a['quoziente_set']}</div><div class="stat-label">Q.Set</div></div>
                <div class="stat-box"><div class="stat-value">{a['quoziente_punti']}</div><div class="stat-label">Q.Punti</div></div>
                <div class="stat-box"><div class="stat-value">{a['punti_fatti']}</div><div class="stat-label">Pt Fatti</div></div>
                <div class="stat-box"><div class="stat-value">{a['punti_subiti']}</div><div class="stat-label">Pt Subiti</div></div>
                <div class="stat-box"><div class="stat-value">{a['oro']}</div><div class="stat-label">🥇 Ori</div></div>
                <div class="stat-box"><div class="stat-value">{a['argento']}</div><div class="stat-label">🥈 Argenti</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Attributi FIFA
    st.markdown("#### 🎮 Attributi")
    col_attrs = st.columns(6)
    attrs = ["attacco","difesa","muro","ricezione","battuta","alzata"]
    icons = ["⚡","🛡️","🧱","🤲","🏐","🎯"]
    for col, attr, icon in zip(col_attrs, attrs, icons):
        with col:
            val = s.get(attr, 50)
            color = "#00c851" if val >= 75 else "#ffd700" if val >= 65 else "#a0a0b0"
            st.markdown(f"""
            <div style="background:var(--bg-card2);border-radius:8px;padding:10px;text-align:center">
                <div style="font-size:1.1rem">{icon}</div>
                <div style="font-size:1.6rem;font-weight:900;color:{color}">{val}</div>
                <div style="font-size:0.6rem;color:var(--text-secondary);letter-spacing:1px;text-transform:uppercase">{attr}</div>
            </div>
            """, unsafe_allow_html=True)

    # TROFEI ATLETA — Lista completa
    st.markdown("#### 🏆 Trofei")
    trofei = get_trofei_atleta(a["atleta"])
    sbloccati_count = sum(1 for _, u in trofei if u)
    st.caption(f"{sbloccati_count}/{len(trofei)} sbloccati")
    tcols = st.columns(6)
    for i, (trofeo, sbloccato) in enumerate(trofei):
        with tcols[i % 6]:
            tc = {"comune":"#cd7f32","non comune":"#c0c0c0","raro":"#ffd700","epico":"#e040fb","leggendario":"#00f5ff"}.get(trofeo["rarità"],"#888")
            locked_filter = "" if sbloccato else "filter:grayscale(100%) opacity(0.35);"
            st.markdown(f"""
            <div title="{trofeo['descrizione']} ({'SBLOCCATO' if sbloccato else 'Bloccato'})"
                style="background:{trofeo['sfondo'] if sbloccato else 'var(--bg-card2)'};
                border:1px solid {tc if sbloccato else 'var(--border)'};
                border-radius:8px;padding:8px;text-align:center;margin-bottom:6px;
                {locked_filter}cursor:help">
                <div style="font-size:1.5rem">{trofeo['icona']}</div>
                <div style="font-size:0.55rem;font-weight:700;margin-top:2px;color:{'rgba(0,0,0,0.85)' if sbloccato else 'var(--text-primary)'}">{trofeo['nome']}</div>
                <div style="font-size:0.45rem;margin-top:1px;color:{'rgba(0,0,0,0.6)' if sbloccato else tc};letter-spacing:1px">{trofeo['rarità'].upper()}</div>
            </div>
            """, unsafe_allow_html=True)

    # Grafici storico
    if a["storico"]:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📈 Andamento Posizioni")
            df_pos = pd.DataFrame({"Torneo": [t for t, _ in a["storico"]], "Posizione": [p for _, p in a["storico"]]}).set_index("Torneo")
            max_pos = df_pos["Posizione"].max()
            df_pos["Inv"] = max_pos + 1 - df_pos["Posizione"]
            st.line_chart(df_pos["Inv"], height=200, color="#e8002d")
            st.caption("↑ = Migliore posizione")
        with col2:
            st.markdown("#### 📊 Punti per Torneo")
            n_sq = len(state["squadre"]) or 8
            df_pts = pd.DataFrame({"Torneo": [t for t, _ in a["storico"]], "Punti": [calcola_punti_ranking(p, n_sq) for _, p in a["storico"]]}).set_index("Torneo")
            st.bar_chart(df_pts, height=200, color="#ffd700")

        st.markdown("#### 📋 Storico Tornei")
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        n_sq_curr = len(state["squadre"]) or 8
        for t_nome, pos in a["storico"]:
            icon = medals.get(pos, f"#{pos}")
            pts = calcola_punti_ranking(pos, n_sq_curr)
            st.markdown(f"• {icon} **{t_nome}** — {pos}° posto → +{pts} pt ranking")


def _render_modifica_profilo(state, atleta):
    """Form per modificare nome, cognome e foto di un atleta."""
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        nuovo_nome = st.text_input("Nome", value=atleta.get("nome_proprio", atleta["nome"].split()[0] if atleta["nome"] else ""), key=f"edit_nome_{atleta['id']}")
    with col2:
        nuovo_cognome = st.text_input("Cognome", value=atleta.get("cognome", atleta["nome"].split()[-1] if len(atleta["nome"].split()) > 1 else ""), key=f"edit_cognome_{atleta['id']}")
    with col3:
        foto_up = st.file_uploader("📷 Foto", type=["png","jpg","jpeg"], key=f"edit_foto_{atleta['id']}")

    if st.button("💾 Salva Modifiche Profilo", key=f"save_profile_{atleta['id']}"):
        full_name = f"{nuovo_nome} {nuovo_cognome}".strip()
        if full_name:
            atleta["nome"] = full_name
            atleta["nome_proprio"] = nuovo_nome
            atleta["cognome"] = nuovo_cognome
        if foto_up:
            import base64
            atleta["foto_b64"] = base64.b64encode(foto_up.read()).decode()
        save_state(state)
        st.success("✅ Profilo aggiornato!")
        st.rerun()


def _render_export_ranking_pdf(state, ranking):
    st.markdown("### 📄 Esporta Ranking in PDF")
    if st.button("🖨️ GENERA PDF RANKING", use_container_width=True):
        try:
            pdf_path = _genera_pdf_ranking(state, ranking)
            with open(pdf_path, "rb") as f:
                st.download_button("⬇️ SCARICA PDF RANKING", f, file_name="ranking_beach_volley.pdf", mime="application/pdf", use_container_width=True)
        except Exception as e:
            st.error(f"Errore: {e}")
            import traceback; st.code(traceback.format_exc())


def _genera_pdf_ranking(state, ranking):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import mm

    pdf_path = "/tmp/ranking_beach_volley.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=20*mm, bottomMargin=20*mm)
    DARK=colors.HexColor("#0a0a0f");RED=colors.HexColor("#e8002d");GOLD=colors.HexColor("#ffd700")
    LIGHT=colors.HexColor("#f0f0f0");WHITE=colors.white
    styles=getSampleStyleSheet()
    title_s=ParagraphStyle("title",fontName="Helvetica-Bold",fontSize=24,textColor=RED,spaceAfter=4,alignment=1)
    sub_s=ParagraphStyle("sub",fontName="Helvetica",fontSize=11,textColor=colors.grey,spaceAfter=12,alignment=1)
    h2_s=ParagraphStyle("h2",fontName="Helvetica-Bold",fontSize=14,textColor=DARK,spaceBefore=14,spaceAfter=8)
    story=[]
    story.append(Paragraph("🏐 BEACH VOLLEY RANKING GLOBALE",title_s))
    story.append(Paragraph(f"{state['torneo']['nome'] or 'Stagione'} · {len(ranking)} atleti classificati",sub_s))
    story.append(HRFlowable(width="100%",thickness=3,color=RED))
    story.append(Spacer(1,10))
    full_data=[["#","ATLETA","OVR","PTS","T","V","P","SV","SP","WIN%"]]
    for i,a in enumerate(ranking):
        full_data.append([str(i+1),a["nome"],str(a["overall"]),str(a["rank_pts"]),str(a["tornei"]),
                          str(a["vittorie"]),str(a["sconfitte"]),str(a["set_vinti"]),str(a["set_persi"]),f"{a['win_rate']}%"])
    ft=Table(full_data,colWidths=[10*mm,52*mm,14*mm,18*mm,10*mm,10*mm,10*mm,12*mm,12*mm,16*mm])
    ft.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),DARK),("TEXTCOLOR",(0,0),(-1,0),WHITE),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[LIGHT,WHITE]),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),("ALIGN",(1,0),(1,-1),"LEFT"),
        ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#dddddd")),
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("BACKGROUND",(0,1),(-1,1),colors.HexColor("#fff8dc")),
        ("FONTNAME",(0,1),(-1,1),"Helvetica-Bold"),
    ]))
    story.append(ft)
    story.append(Spacer(1,10))
    story.append(Paragraph("Documento generato da Beach Volley Tournament Manager Pro",
                            ParagraphStyle("footer",fontName="Helvetica",fontSize=7,textColor=colors.grey,alignment=1)))
    doc.build(story)
    return pdf_path
