"""
fase_proclamazione.py — Fase 4: Proclamazione vincitori e Ranking globale
"""
import streamlit as st
import pandas as pd
from data_manager import (
    save_state, get_squadra_by_id, get_atleta_by_id
)
from ui_components import render_winner_banner, render_podio, render_career_card


def render_proclamazione(state):
    st.markdown("## 🏆 Proclamazione")
    
    vincitore = state.get("vincitore")
    podio = state.get("podio", [])
    
    if vincitore:
        # Animazione palloncini!
        if not st.session_state.get("balloons_shown"):
            st.balloons()
            st.session_state.balloons_shown = True
        
        render_winner_banner(state, vincitore)
        
        st.markdown("### 🥇 Podio del Torneo")
        render_podio(state, podio)
    
    st.divider()
    
    tabs = st.tabs(["📊 Ranking Globale", "👤 Schede Carriera", "🔄 Nuovo Torneo"])
    
    with tabs[0]:
        render_ranking_globale(state)
    
    with tabs[1]:
        render_schede_carriera(state)
    
    with tabs[2]:
        _render_nuovo_torneo(state)


def render_ranking_globale(state):
    st.markdown("### 📊 Ranking Globale Atleti")
    
    if not state["atleti"]:
        st.info("Nessun dato disponibile. Completa un torneo per generare il ranking.")
        return
    
    # Costruisci dati ranking
    atleti_stats = []
    for a in state["atleti"]:
        s = a["stats"]
        if s["tornei"] == 0:
            continue
        quoziente = round(s["punti_fatti"] / max(s["set_vinti"], 1), 2)
        win_rate = round(s["vittorie"] / max(s["tornei"], 1) * 100, 1)
        
        # Punteggio ranking: punti per posizioni
        rank_pts = 0
        for _, pos in s["storico_posizioni"]:
            rank_pts += {1: 100, 2: 70, 3: 50}.get(pos, 20)
        
        atleti_stats.append({
            "atleta": a,
            "nome": a["nome"],
            "tornei": s["tornei"],
            "vittorie": s["vittorie"],
            "sconfitte": s["sconfitte"],
            "set_vinti": s["set_vinti"],
            "set_persi": s["set_persi"],
            "quoziente": quoziente,
            "win_rate": win_rate,
            "rank_pts": rank_pts,
        })
    
    if not atleti_stats:
        st.info("Completa il torneo e trasferisci i dati al ranking per visualizzarli.")
        return
    
    atleti_stats.sort(key=lambda x: -x["rank_pts"])
    
    # Podio graficoo top 3
    if len(atleti_stats) >= 3:
        st.markdown("#### 🏅 Top 3 Atleti")
        top3 = atleti_stats[:3]
        col1, col2, col3 = st.columns(3)
        cols = [col2, col1, col3]  # ordine podio: 2° 1° 3°
        medals = {0: ("🥇", "#ffd700"), 1: ("🥈", "#c0c0c0"), 2: ("🥉", "#cd7f32")}
        
        for rank_idx, (col, atleta_data) in enumerate(zip(cols, [top3[1], top3[0], top3[2]])):
            real_pos = [1, 0, 2][rank_idx]
            medal, color = medals[real_pos]
            with col:
                st.markdown(f"""
                <div style="background:var(--bg-card);border:2px solid {color};border-radius:12px;
                    padding:20px;text-align:center;margin-top:{['0','20px','8px'][rank_idx]}">
                    <div style="font-size:2rem">{medal}</div>
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.4rem;
                        font-weight:800;color:{color}">{atleta_data['nome']}</div>
                    <div style="color:var(--text-secondary);font-size:0.8rem;margin-top:4px">
                        {atleta_data['rank_pts']} pts ranking
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabella completa
    html = """
    <table class="rank-table">
    <tr>
        <th>#</th><th style="text-align:left">ATLETA</th>
        <th>PTS RANK</th><th>TORNEI</th><th>V</th><th>P</th>
        <th>SET V</th><th>SET P</th><th>QUOT.</th><th>WIN%</th>
    </tr>"""
    
    pos_cls = {1: "gold", 2: "silver", 3: "bronze"}
    for i, a in enumerate(atleti_stats):
        pos = i + 1
        cls = pos_cls.get(pos, "")
        html += f"""
        <tr>
            <td><span class="rank-pos {cls}">{pos}</span></td>
            <td style="text-align:left;font-weight:600">{a['nome']}</td>
            <td style="font-weight:700;color:var(--accent-gold)">{a['rank_pts']}</td>
            <td>{a['tornei']}</td>
            <td style="color:var(--green)">{a['vittorie']}</td>
            <td style="color:var(--accent-red)">{a['sconfitte']}</td>
            <td>{a['set_vinti']}</td><td>{a['set_persi']}</td>
            <td>{a['quoziente']}</td>
            <td>{a['win_rate']}%</td>
        </tr>"""
    
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)


def render_schede_carriera(state):
    st.markdown("### 👤 Schede Carriera Atleti")
    
    atleti_con_dati = [a for a in state["atleti"] if a["stats"]["tornei"] > 0]
    
    if not atleti_con_dati:
        st.info("Completa un torneo per vedere le schede carriera.")
        return
    
    nomi = [a["nome"] for a in atleti_con_dati]
    selezionato = st.selectbox("🔍 Seleziona Atleta", nomi, key="career_select")
    
    atleta = next((a for a in atleti_con_dati if a["nome"] == selezionato), None)
    if not atleta:
        return
    
    render_career_card(atleta)
    
    # Grafico andamento
    s = atleta["stats"]
    if s["storico_posizioni"]:
        st.markdown("#### 📈 Andamento Posizioni nei Tornei")
        storico = s["storico_posizioni"]
        
        df_data = {
            "Torneo": [t for t, _ in storico],
            "Posizione": [p for _, p in storico],
        }
        df = pd.DataFrame(df_data)
        
        # Line chart (posizione invertita: 1° = più alto)
        df_chart = df.set_index("Torneo")
        df_chart["Posizione Invertita"] = df_chart["Posizione"].max() + 1 - df_chart["Posizione"]
        
        st.line_chart(df_chart["Posizione Invertita"], use_container_width=True,
                      height=200, color="#e8002d")
        
        st.caption("Grafico: più alto = migliore posizione")
        
        # Storico tabella
        st.markdown("##### Storico Tornei")
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        for torneo_nome, pos in storico:
            icon = medals.get(pos, f"#{pos}")
            st.markdown(f"• {icon} **{torneo_nome}** — {pos}° posto")


def _render_nuovo_torneo(state):
    st.markdown("### 🔄 Inizia un Nuovo Torneo")
    st.info("Iniziare un nuovo torneo manterrà gli atleti e il ranking esistente, ma resetterà squadre e partite.")
    
    if st.button("🆕 NUOVO TORNEO", use_container_width=True, type="primary"):
        from data_manager import empty_state
        
        # Preserva atleti con le loro statistiche accumulate
        atleti_preservati = state["atleti"]
        ranking_preservato = state.get("ranking_globale", [])
        
        nuovo = empty_state()
        nuovo["atleti"] = atleti_preservati
        nuovo["ranking_globale"] = ranking_preservato
        
        # Resetta sessione
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        save_state(nuovo)
        st.rerun()
