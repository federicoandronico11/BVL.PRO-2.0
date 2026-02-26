"""
fase_gironi.py — Fase 2: Fase a Gironi con scoreboard live
"""
import streamlit as st
from data_manager import (
    save_state, simula_partita, aggiorna_classifica_squadra,
    get_squadra_by_id, nome_squadra, genera_bracket_da_gironi
)
from ui_components import render_match_card


def render_gironi(state):
    st.markdown("## 🔵 Fase a Gironi")
    
    # Controllo simulatore ON/OFF
    col_a, col_b, col_c = st.columns([2, 2, 2])
    with col_a:
        state["simulazione_al_ranking"] = st.toggle(
            "📊 Invia dati simulati al Ranking",
            value=state["simulazione_al_ranking"],
            help="Se OFF, la simulazione è solo demo e non aggiorna statistiche atleti"
        )
    with col_b:
        if st.button("🎲 Simula TUTTI i Risultati", use_container_width=True):
            _simula_tutti(state)
    with col_c:
        tutti_confermati = all(
            p["confermata"]
            for g in state["gironi"]
            for p in g["partite"]
        )
        if tutti_confermati:
            if st.button("⚡ AVANZA ALL'ELIMINAZIONE →", use_container_width=True):
                state["bracket"] = genera_bracket_da_gironi(state["gironi"])
                state["fase"] = "eliminazione"
                save_state(state)
                st.rerun()
        else:
            st.info("Conferma tutti i match per avanzare")
    
    st.divider()
    
    # Tabs per girone
    nomi_gironi = [g["nome"] for g in state["gironi"]]
    nomi_gironi.append("📊 Classifiche")
    tabs = st.tabs(nomi_gironi)
    
    for i, g in enumerate(state["gironi"]):
        with tabs[i]:
            _render_girone(state, g, i)
    
    with tabs[-1]:
        _render_classifiche_gironi(state)


def _render_girone(state, girone, girone_idx):
    st.markdown(f"### {girone['nome']}")
    
    for j, partita in enumerate(girone["partite"]):
        render_match_card(state, partita, label=f"{girone['nome']} · Match {j+1}")
        
        if not partita["confermata"]:
            _render_scoreboard_live(state, partita, f"g{girone_idx}_p{j}")
        
        st.markdown("---")


def _render_scoreboard_live(state, partita, key_prefix):
    """Scoreboard interattivo per aggiornare set e punteggi."""
    sq1 = get_squadra_by_id(state, partita["sq1"])
    sq2 = get_squadra_by_id(state, partita["sq2"])
    torneo = state["torneo"]
    formato = torneo["formato_set"]
    pmax = torneo["punteggio_max"]
    
    with st.expander("📝 Inserisci Risultato", expanded=False):
        n_set = 1 if formato == "Set Unico" else 3
        
        punteggi_inseriti = []
        for s in range(n_set):
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                p1 = st.number_input(f"Set {s+1} — {sq1['nome']}", 0, 50, 0,
                                     key=f"{key_prefix}_s{s}_p1")
            with col2:
                st.markdown("<div style='text-align:center;padding-top:28px;color:#666'>vs</div>", unsafe_allow_html=True)
            with col3:
                p2 = st.number_input(f"Set {s+1} — {sq2['nome']}", 0, 50, 0,
                                     key=f"{key_prefix}_s{s}_p2")
            punteggi_inseriti.append((p1, p2))
        
        # Battuta
        battuta = st.radio(
            "🏐 In battuta",
            [sq1["nome"], sq2["nome"]],
            horizontal=True,
            key=f"{key_prefix}_battuta"
        )
        partita["in_battuta"] = 1 if battuta == sq1["nome"] else 2
        
        if st.button("✅ CONFERMA RISULTATO", key=f"{key_prefix}_confirm", use_container_width=True):
            # Calcola set vinti
            s1v, s2v = 0, 0
            punteggi_validi = []
            for p1, p2 in punteggi_inseriti:
                if p1 > 0 or p2 > 0:
                    if p1 > p2: s1v += 1
                    else: s2v += 1
                    punteggi_validi.append((p1, p2))
            
            if not punteggi_validi:
                st.error("Inserisci almeno un set con punteggio.")
                return
            
            partita["punteggi"] = punteggi_validi
            partita["set_sq1"] = s1v
            partita["set_sq2"] = s2v
            partita["vincitore"] = partita["sq1"] if s1v > s2v else partita["sq2"]
            partita["confermata"] = True
            aggiorna_classifica_squadra(state, partita)
            save_state(state)
            st.success("✅ Risultato confermato e classifica aggiornata!")
            st.rerun()
        
        if st.button("🎲 Simula questo match", key=f"{key_prefix}_sim"):
            simula_partita(state, partita)
            if state["simulazione_al_ranking"]:
                aggiorna_classifica_squadra(state, partita)
            save_state(state)
            st.rerun()


def _render_classifiche_gironi(state):
    for girone in state["gironi"]:
        st.markdown(f"### 📊 Classifica {girone['nome']}")
        
        # Calcola classifica dal vivo
        squadre_dati = []
        for sid in girone["squadre"]:
            sq = get_squadra_by_id(state, sid)
            if sq:
                squadre_dati.append(sq)
        
        squadre_ord = sorted(squadre_dati, key=lambda s: (
            -s["punti_classifica"], -s["vittorie"],
            -(s["set_vinti"] - s["set_persi"]),
            -(s["punti_fatti"] - s["punti_subiti"])
        ))
        
        # HTML table
        html = """
        <table class="rank-table">
        <tr>
            <th>#</th><th>SQUADRA</th><th>PTS</th><th>V</th><th>P</th>
            <th>SV</th><th>SP</th><th>PF</th><th>PS</th>
        </tr>"""
        
        pos_cls = {1: "gold", 2: "silver", 3: "bronze"}
        for i, sq in enumerate(squadre_ord):
            pos = i + 1
            cls = pos_cls.get(pos, "")
            qualif = "🟢" if pos <= 2 else ""
            html += f"""
            <tr>
                <td><span class="rank-pos {cls}">{pos}</span></td>
                <td style="text-align:left;font-weight:600">{qualif} {sq['nome']}</td>
                <td style="font-weight:700;color:var(--accent-gold)">{sq['punti_classifica']}</td>
                <td style="color:var(--green)">{sq['vittorie']}</td>
                <td style="color:var(--accent-red)">{sq['sconfitte']}</td>
                <td>{sq['set_vinti']}</td><td>{sq['set_persi']}</td>
                <td>{sq['punti_fatti']}</td><td>{sq['punti_subiti']}</td>
            </tr>"""
        
        html += "</table>"
        st.markdown(html, unsafe_allow_html=True)
        st.caption("🟢 Le prime 2 qualificate ai Playoff")
        st.markdown("---")


def _simula_tutti(state):
    for girone in state["gironi"]:
        for partita in girone["partite"]:
            if not partita["confermata"]:
                simula_partita(state, partita)
                if state["simulazione_al_ranking"]:
                    aggiorna_classifica_squadra(state, partita)
    save_state(state)
    st.success("🎲 Tutti i match simulati!")
    st.rerun()
