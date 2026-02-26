"""
app.py — Beach Volley Tournament Manager Pro v3
Avvia con: streamlit run app.py
"""
import streamlit as st
from data_manager import load_state, save_state, get_trofei_atleta, calcola_overall_fifa
from theme_manager import (
    load_theme_config, save_theme_config, inject_theme_css,
    render_personalization_page, render_banner, render_sponsors_sidebar
)
from ranking_page import build_ranking_data
from fase_setup import render_setup
from fase_gironi import render_gironi
from fase_eliminazione import render_eliminazione
from fase_proclamazione import render_proclamazione
from segnapunti_live import render_segnapunti_live
from ranking_page import render_ranking_page
from incassi import render_incassi

st.set_page_config(
    page_title="🏐 Beach Volley Tournament",
    page_icon="🏐",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "state" not in st.session_state:
    st.session_state.state = load_state()
if "theme_cfg" not in st.session_state:
    st.session_state.theme_cfg = load_theme_config()
if "current_page" not in st.session_state:
    st.session_state.current_page = "torneo"
if "segnapunti_open" not in st.session_state:
    st.session_state.segnapunti_open = False

state = st.session_state.state
theme_cfg = st.session_state.theme_cfg
logo_html = inject_theme_css(theme_cfg)


def render_header():
    nome = state["torneo"]["nome"] or "Beach Volley"
    header_style = theme_cfg.get("header_style", "Grande con gradiente")
    if header_style == "Solo testo":
        st.markdown(f"<h1 style='font-family:var(--font-display);font-size:2rem;font-weight:800;text-transform:uppercase;color:var(--accent1)'>{nome}</h1>", unsafe_allow_html=True)
    else:
        compact = header_style == "Compatto minimalista"
        padding = "12px 20px" if compact else "20px 30px"
        title_size = "1.8rem" if compact else "2.8rem"
        st.markdown(f"""
        <div class="tournament-header" style="padding:{padding}">
            {logo_html}
            <div class="tournament-title" style="font-size:{title_size}">🏐 {nome}</div>
            <div class="tournament-subtitle">Tournament Manager Pro</div>
        </div>
        """, unsafe_allow_html=True)
    render_banner(theme_cfg)
    fasi_ord = ["setup","gironi","eliminazione","proclamazione"]
    fase_corrente = state["fase"]
    idx_corrente = fasi_ord.index(fase_corrente)
    fasi_label = [("setup","⚙️ Setup"),("gironi","🔵 Gironi"),("eliminazione","⚡ Eliminazione"),("proclamazione","🏆 Finale")]
    html = '<div style="display:flex;justify-content:center;flex-wrap:wrap;gap:8px;margin-bottom:20px;">'
    for i, (k, label) in enumerate(fasi_label):
        if i < idx_corrente: css="fase-badge done"; icon="✓ "
        elif i == idx_corrente: css="fase-badge active"; icon=""
        else: css="fase-badge"; icon=""
        html += f'<span class="{css}">{icon}{label}</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_bottom_nav():
    if not theme_cfg.get("show_bottom_nav", True):
        return
    current = st.session_state.current_page
    is_segna = st.session_state.segnapunti_open
    nav_items = [
        ("torneo","🏐","Torneo"), ("ranking","🏅","Ranking"), ("profili","👤","Profili"),
        ("incassi","💰","Incassi"), ("live","🔴" if is_segna else "📊","Live"), ("theme","🎨","Tema"),
    ]
    html = '<div class="bottom-nav">'
    for page_id, icon, label in nav_items:
        if page_id == "live":
            active = "active" if is_segna else ""
        else:
            active = "active" if (current == page_id and not is_segna) else ""
        html += f'<div class="bottom-nav-item {active}"><span class="nav-icon">{icon}</span><span class="nav-label">{label}</span></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
    # Pulsanti invisibili per navigazione reale (il CSS bottom-nav è solo display)
    cols = st.columns(6)
    labels = ["🏐 Torneo","🏅 Ranking","👤 Profili","💰 Incassi","📊/🔴 Live","🎨 Tema"]
    pages = ["torneo","ranking","profili","incassi","live","theme"]
    for col, page_id, lbl in zip(cols, pages, labels):
        with col:
            if st.button(lbl, key=f"bottom_nav_{page_id}", use_container_width=True):
                if page_id == "live":
                    st.session_state.segnapunti_open = not st.session_state.segnapunti_open
                    st.session_state.current_page = "torneo"
                else:
                    st.session_state.current_page = page_id
                    st.session_state.segnapunti_open = False
                st.rerun()


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:16px 0 12px">
        {logo_html}
        <div style="font-family:var(--font-display);font-size:1.3rem;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:var(--text-primary)">Beach Volley</div>
        <div style="color:var(--accent1);font-size:0.6rem;letter-spacing:4px;text-transform:uppercase;font-weight:700;margin-top:2px">Tournament Manager Pro</div>
    </div>
    """, unsafe_allow_html=True)

    if theme_cfg.get("banner_position") == "Nella sidebar" and theme_cfg.get("banner_b64"):
        st.markdown(f'<img src="data:image/png;base64,{theme_cfg["banner_b64"]}" style="width:100%;border-radius:8px;margin-bottom:8px">', unsafe_allow_html=True)

    st.markdown("<hr style='border-color:var(--border);margin:0 0 12px'>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.6rem;letter-spacing:3px;text-transform:uppercase;color:var(--accent1);font-weight:700;margin-bottom:8px">⚡ NAVIGAZIONE TORNEO</div>', unsafe_allow_html=True)

    fase_corrente = state["fase"]
    fasi_ord = ["setup","gironi","eliminazione","proclamazione"]
    idx_attuale = fasi_ord.index(fase_corrente)
    nav_items_torneo = [
        ("setup","⚙️  Setup & Iscrizioni"), ("gironi","🔵  Fase a Gironi"),
        ("eliminazione","⚡  Eliminazione Diretta"), ("proclamazione","🏆  Proclamazione"),
    ]
    for i, (k, label) in enumerate(nav_items_torneo):
        disabled = i > idx_attuale
        if disabled:
            st.markdown(f'<div style="padding:9px 14px;margin-bottom:4px;border-radius:var(--radius);border:1px solid var(--border);opacity:0.3;cursor:not-allowed;font-size:0.82rem;color:var(--text-secondary)">🔒 {label}</div>', unsafe_allow_html=True)
        else:
            is_active = (k == fase_corrente and st.session_state.current_page == "torneo" and not st.session_state.segnapunti_open)
            if is_active:
                st.markdown(f'<div style="padding:9px 14px;margin-bottom:4px;border-radius:var(--radius);background:var(--accent1);font-weight:700;font-size:0.82rem;color:white">▶ {label}</div>', unsafe_allow_html=True)
            else:
                if st.button(label, key=f"nav_{k}", use_container_width=True):
                    state["fase"] = k; st.session_state.current_page = "torneo"
                    st.session_state.segnapunti_open = False; save_state(state); st.rerun()

    st.markdown("<hr style='border-color:var(--border);margin:14px 0 12px'>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.6rem;letter-spacing:3px;text-transform:uppercase;color:var(--accent1);font-weight:700;margin-bottom:8px">🛠️ STRUMENTI</div>', unsafe_allow_html=True)

    segna_label = "🔴 Chiudi Segnapunti" if st.session_state.segnapunti_open else "📊 SEGNAPUNTI LIVE"
    if st.button(segna_label, use_container_width=True, key="btn_segnapunti"):
        st.session_state.segnapunti_open = not st.session_state.segnapunti_open
        st.session_state.current_page = "torneo"; st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏅 Ranking", use_container_width=True, key="btn_ranking"):
            st.session_state.current_page = "ranking"; st.session_state.segnapunti_open = False; st.rerun()
    with c2:
        if st.button("👤 Profili", use_container_width=True, key="btn_profili"):
            st.session_state.current_page = "profili"; st.session_state.segnapunti_open = False; st.rerun()
    c3, c4 = st.columns(2)
    with c3:
        if st.button("💰 Incassi", use_container_width=True, key="btn_incassi"):
            st.session_state.current_page = "incassi"; st.session_state.segnapunti_open = False; st.rerun()
    with c4:
        if st.button("🎨 Tema", use_container_width=True, key="btn_theme"):
            st.session_state.current_page = "theme"; st.session_state.segnapunti_open = False; st.rerun()

    st.markdown("<hr style='border-color:var(--border);margin:14px 0 12px'>", unsafe_allow_html=True)

    # INFO TORNEO
    if state["torneo"]["nome"]:
        st.markdown('<div style="font-size:0.6rem;letter-spacing:3px;text-transform:uppercase;color:var(--accent1);font-weight:700;margin-bottom:8px">📋 TORNEO ATTIVO</div>', unsafe_allow_html=True)
        tipo_gioco = state["torneo"].get("tipo_gioco","2x2")
        st.markdown(f"""
        <div style="background:var(--bg-card2);border:1px solid var(--border);border-radius:var(--radius);padding:12px;margin-bottom:12px">
            <div style="font-family:var(--font-display);font-size:1.05rem;font-weight:700;color:var(--text-primary);margin-bottom:8px">{state['torneo']['nome']}</div>
            <div style="display:flex;flex-direction:column;gap:4px">
                <div style="font-size:0.78rem;color:var(--text-secondary)">📅 {state['torneo']['data']}</div>
                <div style="font-size:0.78rem;color:var(--text-secondary)">🏐 {tipo_gioco} · {state['torneo']['formato_set']} · Max {state['torneo']['punteggio_max']} pt</div>
                <div style="font-size:0.78rem;color:var(--text-secondary)">📊 {state['torneo']['tipo_tabellone']}</div>
                <div style="font-size:0.78rem;color:var(--text-secondary)">👥 {len(state['squadre'])} squadre · {len(state['atleti'])} atleti</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # TOP RANKING
    ranking_data = build_ranking_data(state)
    if ranking_data:
        st.markdown('<div style="font-size:0.6rem;letter-spacing:3px;text-transform:uppercase;color:var(--accent1);font-weight:700;margin-bottom:8px">🏅 TOP RANKING</div>', unsafe_allow_html=True)
        medals = {0:"🥇",1:"🥈",2:"🥉"}
        rhtml = '<div style="background:var(--bg-card2);border:1px solid var(--border);border-radius:var(--radius);padding:10px;margin-bottom:8px">'
        for i, a in enumerate(ranking_data[:5]):
            icon = medals.get(i, f"#{i+1}")
            border_b = "border-bottom:1px solid var(--border);" if i < min(4,len(ranking_data)-1) else ""
            rhtml += f'<div style="display:flex;justify-content:space-between;align-items:center;padding:5px 0;{border_b}font-size:0.78rem"><span>{icon} <span style="color:var(--text-primary);font-weight:600">{a["nome"]}</span></span><span style="color:var(--accent-gold);font-weight:800;font-family:var(--font-display)">{a["rank_pts"]}</span></div>'
        rhtml += '</div>'
        st.markdown(rhtml, unsafe_allow_html=True)
        if st.button("→ Classifica Completa", key="btn_rank_full", use_container_width=True):
            st.session_state.current_page = "ranking"; st.rerun()

    # PROSSIMI TROFEI
    atleti_con_dati = [a for a in state["atleti"] if a["stats"]["tornei"] > 0]
    if atleti_con_dati:
        st.markdown("<hr style='border-color:var(--border);margin:12px 0'>", unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.6rem;letter-spacing:3px;text-transform:uppercase;color:var(--accent1);font-weight:700;margin-bottom:8px">🏆 TROFEI DA SBLOCCARE</div>', unsafe_allow_html=True)
        thtml = '<div style="background:var(--bg-card2);border:1px solid var(--border);border-radius:var(--radius);padding:10px;margin-bottom:8px">'
        shown = 0
        for atleta in atleti_con_dati[:3]:
            trofei = get_trofei_atleta(atleta)
            prossimo = next((t for t, u in trofei if not u), None)
            if prossimo and shown < 3:
                thtml += f'<div style="display:flex;gap:8px;align-items:center;padding:5px 0;border-bottom:1px solid var(--border);font-size:0.73rem"><span style="font-size:1rem;opacity:0.35">{prossimo["icona"]}</span><div><div style="font-weight:600">{atleta["nome"]}</div><div style="font-size:0.58rem;color:var(--text-secondary)">{prossimo["descrizione"]}</div></div></div>'
                shown += 1
        thtml += '</div>'
        if shown > 0:
            st.markdown(thtml, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:var(--border);margin:14px 0 12px'>", unsafe_allow_html=True)
    render_sponsors_sidebar(theme_cfg)

    # SALVATAGGIO
    st.markdown("<hr style='border-color:var(--border);margin:14px 0 12px'>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.6rem;letter-spacing:3px;text-transform:uppercase;color:var(--accent1);font-weight:700;margin-bottom:8px">💾 DATI</div>', unsafe_allow_html=True)
    cs1, cs2 = st.columns(2)
    with cs1:
        if st.button("💾 Salva", use_container_width=True, key="btn_save"):
            save_state(state); st.toast("✅ Salvato!", icon="💾")
    with cs2:
        if st.button("⚠️ Reset", use_container_width=True, key="btn_reset_toggle"):
            st.session_state.show_reset = not st.session_state.get("show_reset", False); st.rerun()
    if st.session_state.get("show_reset", False):
        st.warning("⚠️ Cancellerà il torneo corrente. Atleti e ranking mantenuti.")
        if st.button("🔴 CONFERMA RESET", use_container_width=True, key="btn_reset_confirm"):
            from data_manager import empty_state
            atleti_bkp = state["atleti"]
            nuovo = empty_state(); nuovo["atleti"] = atleti_bkp
            st.session_state.state = nuovo; save_state(nuovo)
            st.session_state.show_reset = False; st.session_state.current_page = "torneo"; st.rerun()
    st.markdown('<div style="font-size:0.65rem;color:var(--text-secondary);text-align:center;margin-top:4px">📁 beach_volley_data.json</div>', unsafe_allow_html=True)


# ─── MAIN ROUTING ────────────────────────────────────────────────────────────

page = st.session_state.current_page

# Segnapunti Live overlay
if st.session_state.segnapunti_open:
    st.markdown("""
    <div style="background:linear-gradient(90deg,rgba(232,0,45,0.1),transparent,rgba(232,0,45,0.1));
        border:1px solid var(--accent1);border-radius:8px;padding:8px 20px;margin-bottom:16px;text-align:center">
        <span style="font-family:var(--font-display);font-size:0.65rem;letter-spacing:4px;text-transform:uppercase;color:var(--accent1);font-weight:700">
            🔴 LIVE · SEGNAPUNTI ATTIVO
        </span>
    </div>
    """, unsafe_allow_html=True)
    render_segnapunti_live(state, theme_cfg)
    st.divider()

if page == "torneo":
    render_header()
    fase = state["fase"]
    if fase == "setup": render_setup(state)
    elif fase == "gironi": render_gironi(state)
    elif fase == "eliminazione": render_eliminazione(state)
    elif fase == "proclamazione": render_proclamazione(state)

elif page == "ranking":
    render_header()
    render_ranking_page(state)

elif page == "profili":
    render_header()
    st.markdown("## 👤 Profili Giocatori")
    from ranking_page import _render_carte_fifa, _render_trofei_page, _render_schede_atleti
    ranking = build_ranking_data(state)
    if not ranking:
        st.info("Completa almeno un torneo per vedere i profili.")
    else:
        ptabs = st.tabs(["🃏 Card FIFA", "🏅 Trofei", "📊 Carriera"])
        with ptabs[0]:
            _render_carte_fifa(state, ranking)
        with ptabs[1]:
            _render_trofei_page(state, ranking)
        with ptabs[2]:
            _render_schede_atleti(state, ranking)

elif page == "incassi":
    render_header()
    render_incassi(state)

elif page == "theme":
    render_personalization_page(theme_cfg)
    st.session_state.theme_cfg = theme_cfg

# Bottom nav bar (visible su tutte le pagine)
st.markdown("<br><br>", unsafe_allow_html=True)
render_bottom_nav()

# Autosave
save_state(state)
