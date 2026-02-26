"""
fase_setup.py — Fase 1: Configurazione torneo e iscrizione squadre (v2 con impostazioni avanzate)
"""
import streamlit as st
from data_manager import (
    new_atleta, new_squadra, get_atleta_by_id,
    save_state, genera_gironi
)


def render_setup(state):
    st.markdown("## ⚙️ Configurazione Torneo")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 📋 Impostazioni Generali")
        nome = st.text_input("Nome Torneo", value=state["torneo"]["nome"], placeholder="es. Summer Cup 2025")
        state["torneo"]["nome"] = nome

        tipo = st.selectbox("Tipo Tabellone", ["Gironi + Playoff", "Doppia Eliminazione"],
                            index=["Gironi + Playoff", "Doppia Eliminazione"].index(state["torneo"]["tipo_tabellone"]))
        state["torneo"]["tipo_tabellone"] = tipo

        formato = st.selectbox("Formato Set", ["Set Unico", "Best of 3"],
                               index=["Set Unico", "Best of 3"].index(state["torneo"]["formato_set"]))
        state["torneo"]["formato_set"] = formato

        pmax = st.number_input("Punteggio Massimo Set", min_value=11, max_value=30,
                               value=state["torneo"]["punteggio_max"])
        state["torneo"]["punteggio_max"] = pmax

        data = st.date_input("Data Torneo")
        state["torneo"]["data"] = str(data)

        # ── IMPOSTAZIONI AVANZATE ────────────────────────────────────────────
        with st.expander("⚙️ Impostazioni Avanzate", expanded=False):
            st.markdown("#### Formato di Gioco")
            tipo_gioco = st.selectbox(
                "Giocatori per Squadra",
                ["2x2", "3x3", "4x4"],
                index=["2x2", "3x3", "4x4"].index(state["torneo"].get("tipo_gioco", "2x2")),
                help="Definisce quanti giocatori per squadra"
            )
            state["torneo"]["tipo_gioco"] = tipo_gioco

            usa_ranking = st.toggle(
                "🏅 Usa Ranking in-app per Teste di Serie",
                value=state["torneo"].get("usa_ranking_teste_serie", False),
                help="Le squadre vengono divise nei gironi in base al ranking storico degli atleti"
            )
            state["torneo"]["usa_ranking_teste_serie"] = usa_ranking

            if usa_ranking:
                st.info("✅ Le squadre saranno distribuite nei gironi secondo il ranking globale degli atleti.")

            st.markdown("#### Regole Speciali")
            regola_set = st.selectbox(
                "Regola Tie-Break",
                ["Standard (differenza 2 punti)", "No tie-break", "Cap a +5"],
                index=0
            )

    with col2:
        st.markdown("### 👤 Gestione Atleti")
        _render_atleti_manager(state)

    st.divider()
    st.markdown("### 🏐 Iscrizione Squadre")
    _render_squadre_manager(state)

    # ── ORDINE SQUADRE NEL TABELLONE ─────────────────────────────────────────
    if state["squadre"] and len(state["squadre"]) >= 2:
        st.divider()
        with st.expander("📋 Ordina Squadre nel Tabellone (trascina)", expanded=False):
            st.caption("Modifica l'ordine delle squadre — influenza la distribuzione nei gironi")
            _render_squadre_ordine(state)

    st.divider()
    n_squadre = len(state["squadre"])
    tipo_gioco = state["torneo"].get("tipo_gioco", "2x2")
    min_sq = 4

    col_a, col_b = st.columns([2, 1])
    with col_a:
        if n_squadre < min_sq:
            st.warning(f"⚠️ Servono almeno {min_sq} squadre per avviare il torneo. ({n_squadre}/{min_sq})")
        elif not nome:
            st.warning("⚠️ Inserisci il nome del torneo.")
        else:
            st.success(f"✅ {n_squadre} squadre iscritte ({tipo_gioco}). Pronto per avviare!")

    with col_b:
        if n_squadre >= min_sq and nome:
            if st.button("🚀 AVVIA TORNEO →", use_container_width=True):
                ids = [s["id"] for s in state["squadre"]]
                num_gironi = max(2, n_squadre // 4)
                use_ranking = state["torneo"].get("usa_ranking_teste_serie", False)
                state["gironi"] = genera_gironi(ids, num_gironi, use_ranking=use_ranking, state=state)
                state["fase"] = "gironi"
                save_state(state)
                st.rerun()


def _render_atleti_manager(state):
    nomi_esistenti = [a["nome"] for a in state["atleti"]]
    with st.expander("➕ Aggiungi Nuovo Atleta", expanded=False):
        col_nome, col_foto = st.columns([2, 1])
        with col_nome:
            nuovo_nome = st.text_input("Nome Atleta", key="new_atleta_name", placeholder="Nome Cognome")
        with col_foto:
            foto_file = st.file_uploader("Foto (opz.)", type=["png","jpg","jpeg"], key="new_atleta_foto")

        if st.button("Aggiungi Atleta", key="btn_add_atleta"):
            if nuovo_nome.strip() and nuovo_nome.strip() not in nomi_esistenti:
                nuovo = new_atleta(nuovo_nome.strip())
                if foto_file:
                    import base64
                    nuovo["foto_b64"] = base64.b64encode(foto_file.read()).decode()
                state["atleti"].append(nuovo)
                save_state(state)
                st.success(f"✅ {nuovo_nome} aggiunto!")
                st.rerun()
            elif nuovo_nome.strip() in nomi_esistenti:
                st.error("Atleta già presente.")
            else:
                st.error("Inserisci un nome valido.")

    if state["atleti"]:
        st.markdown(f"**Atleti registrati:** {len(state['atleti'])}")
        for a in state["atleti"][:6]:
            col_a, col_del = st.columns([4, 1])
            with col_a:
                foto_html = ""
                if a.get("foto_b64"):
                    foto_html = f'<img src="data:image/png;base64,{a["foto_b64"]}" style="height:20px;width:20px;border-radius:50%;object-fit:cover;margin-right:6px;vertical-align:middle">'
                st.markdown(f"<span style='font-size:0.85rem'>{foto_html}• {a['nome']}</span>", unsafe_allow_html=True)
            with col_del:
                if st.button("✕", key=f"del_a_{a['id']}"):
                    state["atleti"] = [x for x in state["atleti"] if x["id"] != a["id"]]
                    save_state(state); st.rerun()
        if len(state["atleti"]) > 6:
            st.caption(f"... e altri {len(state['atleti'])-6}")


def _render_squadre_manager(state):
    atleti_nomi = [a["nome"] for a in state["atleti"]]
    tipo_gioco = state["torneo"].get("tipo_gioco", "2x2")
    n_giocatori = int(tipo_gioco[0])

    if len(state["atleti"]) < n_giocatori:
        st.info(f"Aggiungi almeno {n_giocatori} atleti per creare una squadra {tipo_gioco}.")
        return

    cols = st.columns(n_giocatori)
    atleti_selezionati = []
    atleti_usati = set()
    for i in range(n_giocatori):
        with cols[i]:
            disponibili = [n for n in atleti_nomi if n not in atleti_selezionati]
            sel = st.selectbox(f"Atleta {i+1}", disponibili, key=f"sq_a{i}")
            atleti_selezionati.append(sel)

    nome_automatico = st.toggle("Nome automatico squadra", value=True, key="toggle_nome_auto")
    if nome_automatico:
        nome_sq = "/".join([a.split()[0] for a in atleti_selezionati])
        st.text_input("Nome Squadra (auto)", value=nome_sq, disabled=True, key="sq_nome_auto")
    else:
        nome_sq = st.text_input("Nome Squadra", placeholder="es. Team Sabbia", key="sq_nome_manual")

    if st.button("➕ Iscrive Squadra", key="btn_add_squadra"):
        atleti_objs = [next((a for a in state["atleti"] if a["nome"] == n), None) for n in atleti_selezionati]
        if any(a is None for a in atleti_objs):
            st.error("Atleti non trovati.")
        elif not nome_sq:
            st.error("Inserisci il nome della squadra.")
        else:
            atleti_in_squadra = [aid for sq in state["squadre"] for aid in sq["atleti"]]
            conflitti = [a for a in atleti_objs if a["id"] in atleti_in_squadra]
            if conflitti:
                st.warning(f"⚠️ {conflitti[0]['nome']} è già in un'altra squadra.")
            else:
                sq = new_squadra(nome_sq, [a["id"] for a in atleti_objs])
                state["squadre"].append(sq)
                save_state(state)
                st.success(f"✅ Squadra '{nome_sq}' iscritta!")
                st.rerun()

    if state["squadre"]:
        st.markdown(f"#### Squadre Iscritte ({len(state['squadre'])})")
        for i, sq in enumerate(state["squadre"]):
            a_names = [get_atleta_by_id(state, aid)["nome"] for aid in sq["atleti"] if get_atleta_by_id(state, aid)]
            col_s, col_btn = st.columns([4, 1])
            with col_s:
                st.markdown(f"**{sq['nome']}** — {' / '.join(a_names)}")
            with col_btn:
                if st.button("🗑️", key=f"del_sq_{i}"):
                    state["squadre"].pop(i)
                    save_state(state); st.rerun()


def _render_squadre_ordine(state):
    """Permette di riordinare le squadre nel tabellone."""
    squadre = state["squadre"]
    nomi = [sq["nome"] for sq in squadre]

    st.markdown("Usa i pulsanti ↑↓ per cambiare l'ordine delle squadre:")
    for i, sq in enumerate(squadre):
        a_names = [get_atleta_by_id(state, aid)["nome"] for aid in sq["atleti"] if get_atleta_by_id(state, aid)]
        col_pos, col_nome, col_up, col_down = st.columns([1, 4, 1, 1])
        with col_pos:
            st.markdown(f"<div style='padding-top:8px;color:var(--text-secondary);font-weight:700'>#{i+1}</div>", unsafe_allow_html=True)
        with col_nome:
            st.markdown(f"<div style='padding-top:8px'><strong>{sq['nome']}</strong> <span style='color:var(--text-secondary);font-size:0.8rem'>{' / '.join(a_names)}</span></div>", unsafe_allow_html=True)
        with col_up:
            if i > 0 and st.button("↑", key=f"up_{i}"):
                state["squadre"][i], state["squadre"][i-1] = state["squadre"][i-1], state["squadre"][i]
                save_state(state); st.rerun()
        with col_down:
            if i < len(squadre)-1 and st.button("↓", key=f"down_{i}"):
                state["squadre"][i], state["squadre"][i+1] = state["squadre"][i+1], state["squadre"][i]
                save_state(state); st.rerun()
