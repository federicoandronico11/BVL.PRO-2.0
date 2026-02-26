"""
segnapunti_live.py — Segnapunti LIVE gigante con 8 stili e modalità libera
"""
import streamlit as st
from data_manager import (
    save_state, get_squadra_by_id, aggiorna_classifica_squadra
)
from theme_manager import get_active_scoreboard


def render_segnapunti_live(state, theme_cfg=None):
    """Segnapunti a schermo intero con pulsanti giganti."""
    sb_style = get_active_scoreboard(theme_cfg or {})

    st.markdown(f"""
    <div style="text-align:center;margin-bottom:10px">
        <span style="font-family:var(--font-display);font-size:0.7rem;letter-spacing:4px;
            text-transform:uppercase;color:var(--accent1);font-weight:700">
            🔴 SEGNAPUNTI LIVE — {(theme_cfg or {}).get('scoreboard_style','DAZN Live')}
        </span>
    </div>
    """, unsafe_allow_html=True)

    fase = state.get("fase", "setup")
    torneo_avviato = fase in ["gironi", "eliminazione", "proclamazione"]

    # ── MODALITÀ LIBERA (torneo non ancora iniziato) ────────────────────────
    if not torneo_avviato:
        st.info("⚡ **Modalità Libera** — Il torneo non è ancora iniziato. Puoi usare il segnapunti per partite libere. I risultati non verranno salvati nel tabellone.")
        _render_segnapunti_libero(state, sb_style)
        return

    # ── MODALITÀ TORNEO: selezione partita ──────────────────────────────────
    partite_disponibili = _get_partite_disponibili(state)
    if not partite_disponibili:
        st.info("⏳ Nessuna partita disponibile. Vai alla fase Gironi o Eliminazione.")
        st.divider()
        st.markdown("**Oppure usa la modalità libera:**")
        _render_segnapunti_libero(state, sb_style)
        return

    nomi_partite = [p["label"] for p in partite_disponibili]
    idx_sel = st.session_state.get("segnapunti_partita_idx", 0)
    sel = st.selectbox(
        "Seleziona Partita",
        range(len(nomi_partite)),
        format_func=lambda i: nomi_partite[i],
        index=min(idx_sel, len(nomi_partite)-1),
        key="segnapunti_sel"
    )
    st.session_state.segnapunti_partita_idx = sel
    partita_info = partite_disponibili[sel]
    partita = partita_info["partita"]

    if partita["confermata"]:
        sq_v = get_squadra_by_id(state, partita["vincitore"])
        st.success(f"✅ Partita conclusa. Vincitore: **{sq_v['nome'] if sq_v else '?'}**")
        return

    sq1 = get_squadra_by_id(state, partita["sq1"])
    sq2 = get_squadra_by_id(state, partita["sq2"])
    _render_scoreboard_partita(state, partita, sq1, sq2, sb_style, torneo=True)


def _render_segnapunti_libero(state, sb_style):
    """Segnapunti completamente libero senza partita registrata."""
    key_base = "libero_match"

    if f"{key_base}_s1" not in st.session_state:
        st.session_state[f"{key_base}_nome1"] = "SQUADRA A"
        st.session_state[f"{key_base}_nome2"] = "SQUADRA B"
        st.session_state[f"{key_base}_s1"] = 0
        st.session_state[f"{key_base}_s2"] = 0
        st.session_state[f"{key_base}_p1"] = 0
        st.session_state[f"{key_base}_p2"] = 0
        st.session_state[f"{key_base}_battuta"] = 1
        st.session_state[f"{key_base}_punteggi_sets"] = []

    col_n1, col_n2 = st.columns(2)
    with col_n1:
        nome1 = st.text_input("Nome Squadra 1", value=st.session_state[f"{key_base}_nome1"], key=f"{key_base}_edit_nome1")
        st.session_state[f"{key_base}_nome1"] = nome1
    with col_n2:
        nome2 = st.text_input("Nome Squadra 2", value=st.session_state[f"{key_base}_nome2"], key=f"{key_base}_edit_nome2")
        st.session_state[f"{key_base}_nome2"] = nome2

    pmax = state["torneo"].get("punteggio_max", 21)
    formato = state["torneo"].get("formato_set", "Set Unico")

    class MockSq:
        def __init__(self, nome):
            self.nome = nome
            self["nome"] = nome
        def __getitem__(self, k):
            return self.nome if k == "nome" else []
        def get(self, k, d=None):
            return self.nome if k == "nome" else ([] if k == "atleti" else d)

    sq1_mock = {"nome": nome1, "atleti": []}
    sq2_mock = {"nome": nome2, "atleti": []}
    _render_scoreboard_core(state, key_base, sq1_mock, sq2_mock, sb_style, pmax, formato, torneo=False)


def _render_scoreboard_partita(state, partita, sq1, sq2, sb_style, torneo=True):
    key_base = f"live_{partita['id']}"
    if f"{key_base}_s1" not in st.session_state:
        st.session_state[f"{key_base}_s1"] = 0
        st.session_state[f"{key_base}_s2"] = 0
        st.session_state[f"{key_base}_p1"] = 0
        st.session_state[f"{key_base}_p2"] = 0
        st.session_state[f"{key_base}_battuta"] = 1
        st.session_state[f"{key_base}_punteggi_sets"] = []

    pmax = state["torneo"]["punteggio_max"]
    formato = state["torneo"]["formato_set"]
    _render_scoreboard_core(state, key_base, sq1, sq2, sb_style, pmax, formato, torneo=torneo, partita=partita)


def _render_scoreboard_core(state, key_base, sq1, sq2, sb_style, pmax, formato, torneo=False, partita=None):
    s1 = st.session_state[f"{key_base}_s1"]
    s2 = st.session_state[f"{key_base}_s2"]
    p1 = st.session_state[f"{key_base}_p1"]
    p2 = st.session_state[f"{key_base}_p2"]
    battuta = st.session_state[f"{key_base}_battuta"]

    nome1 = sq1.get("nome", "?") if isinstance(sq1, dict) else sq1["nome"]
    nome2 = sq2.get("nome", "?") if isinstance(sq2, dict) else sq2["nome"]

    battuta_icon1 = "🏐" if battuta == 1 else ""
    battuta_icon2 = "🏐" if battuta == 2 else ""

    bg = sb_style["bg"]
    text1 = sb_style["text1"]
    text2 = sb_style["text2"]
    score_bg = sb_style["score_bg"]
    score_color = sb_style["score_color"]
    score_size = sb_style["score_size"]
    team_size = sb_style["team_size"]
    border_style = sb_style["border_style"]
    extra = sb_style["extra"]

    # Giocatori
    players1_html = ""
    players2_html = ""
    if isinstance(sq1, dict) and sq1.get("atleti"):
        from data_manager import get_atleta_by_id as _gab
        names1 = [_gab(state, aid)["nome"] for aid in sq1["atleti"] if _gab(state, aid)]
        players1_html = f"<div style='font-size:0.75rem;color:{text1}88;margin-top:4px'>{' · '.join(names1)}</div>"
    if isinstance(sq2, dict) and sq2.get("atleti"):
        from data_manager import get_atleta_by_id as _gab
        names2 = [_gab(state, aid)["nome"] for aid in sq2["atleti"] if _gab(state, aid)]
        players2_html = f"<div style='font-size:0.75rem;color:{text2}88;margin-top:4px'>{' · '.join(names2)}</div>"

    st.markdown(f"""
    <div style="background:{bg};border:{border_style};{extra}padding:30px;margin-bottom:20px;">
        <div style="text-align:center;margin-bottom:16px">
            <span style="background:{score_bg};padding:6px 20px;border-radius:20px;
                font-size:0.75rem;letter-spacing:3px;text-transform:uppercase;color:{text1}88">
                SET CORRENTE · {s1} – {s2}
            </span>
        </div>
        <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:20px;align-items:center">
            <div style="text-align:center">
                <div style="font-family:var(--font-display);font-size:{team_size};font-weight:700;
                    text-transform:uppercase;letter-spacing:2px;color:{text1}">
                    {battuta_icon1} {nome1}
                </div>
                {players1_html}
                <div style="font-family:var(--font-display);font-size:{score_size};font-weight:900;
                    line-height:1;text-align:center;color:{score_color};background:{score_bg};
                    border-radius:12px;padding:10px;margin-top:12px">
                    {p1}
                </div>
            </div>
            <div style="text-align:center;min-width:80px">
                <div style="font-family:var(--font-display);font-size:0.7rem;letter-spacing:3px;
                    color:{text1}55;text-transform:uppercase">VS</div>
                <div style="font-size:1.5rem;margin:10px 0;color:{text1}33">|</div>
                <div style="font-size:0.7rem;color:{text1}55;letter-spacing:2px">MAX {pmax}</div>
            </div>
            <div style="text-align:center">
                <div style="font-family:var(--font-display);font-size:{team_size};font-weight:700;
                    text-transform:uppercase;letter-spacing:2px;color:{text2}">
                    {battuta_icon2} {nome2}
                </div>
                {players2_html}
                <div style="font-family:var(--font-display);font-size:{score_size};font-weight:900;
                    line-height:1;text-align:center;color:{score_color};background:{score_bg};
                    border-radius:12px;padding:10px;margin-top:12px">
                    {p2}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── PULSANTI CONTROLLO ──────────────────────────────────────────────────
    col1, col_mid, col2 = st.columns([5, 1, 5])
    with col1:
        st.markdown(f"<div style='text-align:center;color:var(--accent1);font-family:var(--font-display);font-weight:700;font-size:1.1rem;margin-bottom:8px'>{nome1}</div>", unsafe_allow_html=True)
        c1a, c1b, c1c = st.columns([2, 2, 1])
        with c1a:
            if st.button("➕ PUNTO", key=f"{key_base}_add1", use_container_width=True):
                st.session_state[f"{key_base}_p1"] += 1
                st.session_state[f"{key_base}_battuta"] = 1
                _check_set_win(state, key_base, pmax, formato)
                st.rerun()
        with c1b:
            if st.button("➖ Annulla", key=f"{key_base}_sub1", use_container_width=True):
                st.session_state[f"{key_base}_p1"] = max(0, st.session_state[f"{key_base}_p1"] - 1)
                st.rerun()
        with c1c:
            if st.button("🏐", key=f"{key_base}_batt1", use_container_width=True, help="Assegna battuta"):
                st.session_state[f"{key_base}_battuta"] = 1; st.rerun()

    with col_mid:
        st.markdown("<div style='text-align:center;padding-top:40px;color:var(--text-secondary)'>|</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div style='text-align:center;color:var(--accent2);font-family:var(--font-display);font-weight:700;font-size:1.1rem;margin-bottom:8px'>{nome2}</div>", unsafe_allow_html=True)
        c2a, c2b, c2c = st.columns([2, 2, 1])
        with c2a:
            if st.button("➕ PUNTO", key=f"{key_base}_add2", use_container_width=True):
                st.session_state[f"{key_base}_p2"] += 1
                st.session_state[f"{key_base}_battuta"] = 2
                _check_set_win(state, key_base, pmax, formato)
                st.rerun()
        with c2b:
            if st.button("➖ Annulla", key=f"{key_base}_sub2", use_container_width=True):
                st.session_state[f"{key_base}_p2"] = max(0, st.session_state[f"{key_base}_p2"] - 1)
                st.rerun()
        with c2c:
            if st.button("🏐", key=f"{key_base}_batt2", use_container_width=True, help="Assegna battuta"):
                st.session_state[f"{key_base}_battuta"] = 2; st.rerun()

    # ── SET HISTORY ─────────────────────────────────────────────────────────
    sets_history = st.session_state.get(f"{key_base}_punteggi_sets", [])
    if sets_history:
        st.markdown("**Set Giocati:**")
        html_sets = ""
        for i, (a, b) in enumerate(sets_history):
            winner = nome1 if a > b else nome2
            col = "var(--accent1)" if a > b else "var(--accent2)"
            html_sets += f'<span style="background:var(--bg-card2);border-radius:4px;padding:4px 12px;margin-right:8px;font-size:0.85rem">Set {i+1}: <strong style="color:var(--accent1)">{a}</strong> – <strong style="color:var(--accent2)">{b}</strong> <span style="color:{col};font-size:0.75rem;margin-left:6px">({winner})</span></span>'
        st.markdown(html_sets, unsafe_allow_html=True)

    st.divider()

    col_a, col_b, col_c = st.columns([2, 2, 2])
    with col_a:
        if st.button("🔄 Reset Set Corrente", use_container_width=True):
            st.session_state[f"{key_base}_p1"] = 0
            st.session_state[f"{key_base}_p2"] = 0; st.rerun()
    with col_b:
        if st.button("🔄 Reset TUTTO", use_container_width=True):
            for k in [f"{key_base}_s1",f"{key_base}_s2",f"{key_base}_p1",f"{key_base}_p2",f"{key_base}_battuta",f"{key_base}_punteggi_sets"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()
    with col_c:
        s1 = st.session_state.get(f"{key_base}_s1", 0)
        s2 = st.session_state.get(f"{key_base}_s2", 0)
        if torneo and partita and sets_history and (s1 > s2 or s2 > s1):
            if st.button("📤 INVIA AL TABELLONE ✅", use_container_width=True):
                _invia_al_tabellone(state, partita, key_base)
                save_state(state)
                st.success("✅ Dati inviati al tabellone!")
                st.rerun()
        elif not torneo:
            if s1 > 0 or s2 > 0:
                winner = st.session_state.get(f"{key_base}_nome1","?") if s1 > s2 else st.session_state.get(f"{key_base}_nome2","?")
                st.success(f"🏆 Vince: **{winner}** ({s1}–{s2} set)")


def _check_set_win(state, key_base, pmax, formato):
    p1 = st.session_state[f"{key_base}_p1"]
    p2 = st.session_state[f"{key_base}_p2"]
    s1 = st.session_state[f"{key_base}_s1"]
    s2 = st.session_state[f"{key_base}_s2"]
    set_corrente = s1 + s2
    is_tiebreak = (formato == "Best of 3" and set_corrente == 2)
    limit = 15 if is_tiebreak else pmax
    if p1 >= limit and p1 - p2 >= 2:
        st.session_state[f"{key_base}_punteggi_sets"].append((p1, p2))
        st.session_state[f"{key_base}_s1"] += 1
        st.session_state[f"{key_base}_p1"] = 0
        st.session_state[f"{key_base}_p2"] = 0
    elif p2 >= limit and p2 - p1 >= 2:
        st.session_state[f"{key_base}_punteggi_sets"].append((p1, p2))
        st.session_state[f"{key_base}_s2"] += 1
        st.session_state[f"{key_base}_p1"] = 0
        st.session_state[f"{key_base}_p2"] = 0


def _invia_al_tabellone(state, partita, key_base):
    sets = st.session_state.get(f"{key_base}_punteggi_sets", [])
    p1_curr = st.session_state.get(f"{key_base}_p1", 0)
    p2_curr = st.session_state.get(f"{key_base}_p2", 0)
    if p1_curr > 0 or p2_curr > 0:
        sets = sets + [(p1_curr, p2_curr)]
    if not sets: return
    s1v = sum(1 for a, b in sets if a > b)
    s2v = sum(1 for a, b in sets if b > a)
    partita["punteggi"] = sets
    partita["set_sq1"] = s1v; partita["set_sq2"] = s2v
    partita["vincitore"] = partita["sq1"] if s1v >= s2v else partita["sq2"]
    partita["in_battuta"] = st.session_state.get(f"{key_base}_battuta", 1)
    partita["confermata"] = True
    aggiorna_classifica_squadra(state, partita)
    for k in [f"{key_base}_s1",f"{key_base}_s2",f"{key_base}_p1",f"{key_base}_p2",f"{key_base}_battuta",f"{key_base}_punteggi_sets"]:
        if k in st.session_state: del st.session_state[k]


def _get_partite_disponibili(state):
    partite = []
    fase = state["fase"]
    if fase in ["gironi", "eliminazione", "proclamazione"]:
        for g in state.get("gironi", []):
            for p in g["partite"]:
                sq1 = get_squadra_by_id(state, p["sq1"])
                sq2 = get_squadra_by_id(state, p["sq2"])
                if sq1 and sq2:
                    partite.append({
                        "partita": p,
                        "label": f"[{g['nome']}] {sq1['nome']} vs {sq2['nome']} {'✅' if p['confermata'] else '🔴'}"
                    })
    if fase in ["eliminazione", "proclamazione"]:
        for p in state.get("bracket", []):
            sq1 = get_squadra_by_id(state, p["sq1"])
            sq2 = get_squadra_by_id(state, p["sq2"])
            if sq1 and sq2:
                partite.append({
                    "partita": p,
                    "label": f"[Playoff] {sq1['nome']} vs {sq2['nome']} {'✅' if p['confermata'] else '🔴'}"
                })
    return partite
