"""
ranking_page.py — Ranking globale + card FIFA + trofei + schede carriera
"""
import streamlit as st
import pandas as pd
from data_manager import (
    get_atleta_by_id, get_squadra_by_id,
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

    # Tabella con tooltip statistiche al hover
    html = """
    <table class="rank-table">
    <tr>
        <th>#</th><th style="text-align:left">ATLETA</th>
        <th>OVR</th><th>PTS</th><th>T</th><th>🥇</th><th>🥈</th><th>🥉</th>
        <th>V</th><th>P</th><th>SV</th><th>SP</th><th>WIN%</th>
    </tr>"""
    pos_cls = {1: "gold", 2: "silver", 3: "bronze"}
    for i, a in enumerate(ranking):
        pos = i + 1
        cls = pos_cls.get(pos, "")
        card_icons = {"bronze":"🟫","silver":"⬜","gold":"🟨","rare-silver":"🔵","rare-gold":"🌟"}
        card_icon = card_icons.get(a["card_type"], "")
        html += f"""<tr>
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

    # Statistiche rapide al click
    st.divider()
    st.markdown("### 📊 Statistiche Dettagliate")
    sel_nome = st.selectbox("Seleziona giocatore per statistiche rapide", [a["nome"] for a in ranking], key="quick_stats_sel")
    a_sel = next((a for a in ranking if a["nome"] == sel_nome), None)
    if a_sel:
        _render_quick_stats(a_sel, state)


def _render_quick_stats(a, state):
    """Mini dashboard statistiche."""
    s = a["atleta"]["stats"]
    cols = st.columns(4)
    metrics = [
        ("🏆 Rank Pts", a["rank_pts"], ""),
        ("🎮 Tornei", a["tornei"], ""),
        ("🥇 Vittorie", a["vittorie"], f"{a['win_rate']}%"),
        ("📊 Overall", a["overall"], a["card_type"].upper()),
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
    """Griglia di card stile FIFA/EAFC."""
    st.markdown("### 🃏 Card Giocatori")
    st.caption("Le card riflettono le statistiche accumulate nei tornei. Vinci tornei per far crescere la tua carta!")

    card_backgrounds = {
        "bronze": "linear-gradient(135deg,#5C3317 0%,#CD853F 40%,#5C3317 100%)",
        "silver": "linear-gradient(135deg,#555 0%,#C0C0C0 40%,#555 100%)",
        "gold": "linear-gradient(135deg,#8B6914 0%,#FFD700 40%,#8B6914 100%)",
        "rare-silver": "linear-gradient(135deg,#1C3A7A 0%,#4169E1 40%,#1C3A7A 100%)",
        "rare-gold": "linear-gradient(135deg,#7B4F00 0%,#FFD700 40%,#B8860B 100%)",
    }
    card_text_colors = {
        "bronze": "rgba(0,0,0,0.85)", "silver": "rgba(0,0,0,0.85)",
        "gold": "rgba(0,0,0,0.9)", "rare-silver": "rgba(255,255,255,0.95)",
        "rare-gold": "rgba(0,0,0,0.9)",
    }
    card_labels = {
        "bronze": "BRONZO", "silver": "ARGENTO",
        "gold": "ORO", "rare-silver": "ORO RARO ✨", "rare-gold": "LEGGENDA 🌟",
    }

    cols_per_row = 4
    for row_start in range(0, len(ranking), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, a in enumerate(ranking[row_start:row_start+cols_per_row]):
            with cols[j]:
                s = a["atleta"]["stats"]
                overall = a["overall"]
                ct = a["card_type"]
                bg = card_backgrounds.get(ct, card_backgrounds["bronze"])
                tc = card_text_colors.get(ct, "rgba(0,0,0,0.85)")
                label = card_labels.get(ct, "BRONZO")

                foto_html = ""
                if a["atleta"].get("foto_b64"):
                    foto_html = f'<img src="data:image/png;base64,{a["atleta"]["foto_b64"]}" style="width:60px;height:60px;border-radius:50%;object-fit:cover;border:3px solid rgba(255,255,255,0.4);margin-bottom:6px">'
                else:
                    foto_html = '<div style="width:60px;height:60px;border-radius:50%;background:rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;font-size:1.8rem;margin:0 auto 6px">👤</div>'

                attrs_html = ""
                for attr, icon in [("attacco","ATT"),("difesa","DIF"),("muro","MUR"),("ricezione","RIC"),("battuta","BAT"),("alzata","ALZ")]:
                    val = s.get(attr, 50)
                    attrs_html += f'<div class="fifa-stat"><span>{icon}</span><span style="font-weight:900">{val}</span></div>'

                st.markdown(f"""
                <div style="background:{bg};border-radius:12px;padding:14px;text-align:center;
                    color:{tc};margin-bottom:8px;cursor:pointer;transition:transform 0.3s;
                    box-shadow:0 4px 20px rgba(0,0,0,0.4)">
                    <div style="font-size:0.55rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;opacity:0.7;margin-bottom:4px">{label}</div>
                    <div style="font-size:2.8rem;font-weight:900;line-height:1;font-family:var(--font-display)">{overall}</div>
                    <div style="font-size:0.6rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;opacity:0.7">BV</div>
                    <div style="margin:8px 0">{foto_html}</div>
                    <div style="font-size:0.9rem;font-weight:800;text-transform:uppercase;letter-spacing:1px;
                        border-top:1px solid rgba(0,0,0,0.2);border-bottom:1px solid rgba(0,0,0,0.2);
                        padding:4px 0;margin-bottom:8px">{a['nome']}</div>
                    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:2px;font-size:0.7rem;font-weight:700">
                        {attrs_html}
                    </div>
                    <div style="margin-top:8px;font-size:0.6rem;opacity:0.7">
                        🥇{a['oro']} · 🎮{a['tornei']} tornei · {a['win_rate']}% WR
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Upload foto
                foto_up = st.file_uploader(f"📷 {a['nome']}", type=["png","jpg","jpeg"], key=f"foto_{a['id']}", label_visibility="collapsed")
                if foto_up:
                    import base64
                    a["atleta"]["foto_b64"] = base64.b64encode(foto_up.read()).decode()
                    from data_manager import save_state
                    from data_manager import load_state
                    save_state(state)
                    st.rerun()


def _render_trofei_page(state, ranking):
    """Pagina trofei per giocatore."""
    st.markdown("### 🏅 Trofei Giocatori")

    if not ranking:
        st.info("Completa tornei per sbloccare trofei.")
        return

    nomi = [a["nome"] for a in ranking] + [a["nome"] for a in build_ranking_data_all(state) if a["nome"] not in [r["nome"] for r in ranking]]
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

    # Barra progresso
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
            <div style="background:{trofeo['sfondo'] if sbloccato else 'var(--bg-card2)'};
                border:2px solid {tc if sbloccato else 'var(--border)'};
                border-radius:12px;padding:16px;text-align:center;margin-bottom:8px;
                {locked_filter}
                {'box-shadow:0 0 20px ' + tc + '40;' if sbloccato else ''}
                transition:all 0.3s">
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

    # Tutti i trofei per tutti i giocatori
    st.divider()
    st.markdown("### 🏆 Bacheca Globale Trofei")
    _render_global_trophy_board(state, ranking)


def _render_global_trophy_board(state, ranking):
    if not ranking:
        return
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
                tn = trofeo["nome"]
                html += f'<td title="{tn}">✅</td>'
            else:
                html += '<td style="opacity:0.2">🔒</td>'
        html += '</tr>'
    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)


def build_ranking_data_all(state):
    """Ritorna dati ranking anche per atleti senza tornei."""
    return build_ranking_data(state)


def _render_schede_atleti(state, ranking):
    if not ranking:
        return
    nomi = [a["nome"] for a in ranking]
    sel = st.selectbox("🔍 Seleziona Atleta", nomi, key="rank_career_sel")
    a = next((x for x in ranking if x["nome"] == sel), None)
    if not a: return

    col_card, col_stats = st.columns([1, 2])
    with col_card:
        _render_mini_card(a)
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
            </div>
        </div>
        """, unsafe_allow_html=True)

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


def _render_mini_card(a):
    ct = a["card_type"]
    bgs = {
        "bronze": "linear-gradient(135deg,#5C3317,#CD853F,#5C3317)",
        "silver": "linear-gradient(135deg,#555,#C0C0C0,#555)",
        "gold": "linear-gradient(135deg,#8B6914,#FFD700,#8B6914)",
        "rare-silver": "linear-gradient(135deg,#1C3A7A,#4169E1,#1C3A7A)",
        "rare-gold": "linear-gradient(135deg,#7B4F00,#FFD700,#B8860B)",
    }
    bg = bgs.get(ct, bgs["bronze"])
    tc = "rgba(0,0,0,0.9)" if ct in ["bronze","silver","gold","rare-gold"] else "white"
    s = a["atleta"]["stats"]
    foto_html = ""
    if a["atleta"].get("foto_b64"):
        foto_html = f'<img src="data:image/png;base64,{a["atleta"]["foto_b64"]}" style="width:70px;height:70px;border-radius:50%;object-fit:cover;border:3px solid rgba(255,255,255,0.4);margin-bottom:8px">'
    else:
        foto_html = '<div style="width:70px;height:70px;border-radius:50%;background:rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;font-size:2rem;margin:0 auto 8px">👤</div>'

    attrs_html = "".join([
        f'<div style="display:flex;justify-content:space-between;padding:2px 6px;font-size:0.72rem;font-weight:700"><span>{lbl}</span><span>{s.get(attr,50)}</span></div>'
        for attr, lbl in [("attacco","ATT"),("difesa","DIF"),("muro","MUR"),("ricezione","RIC"),("battuta","BAT"),("alzata","ALZ")]
    ])

    st.markdown(f"""
    <div style="background:{bg};border-radius:14px;padding:16px;text-align:center;color:{tc};
        max-width:180px;margin:0 auto;box-shadow:0 6px 25px rgba(0,0,0,0.5)">
        <div style="font-size:0.55rem;font-weight:700;letter-spacing:2px;opacity:0.7;margin-bottom:2px">BEACH VOLLEY</div>
        <div style="font-size:3rem;font-weight:900;line-height:1;font-family:var(--font-display)">{a['overall']}</div>
        <div style="font-size:0.6rem;font-weight:700;letter-spacing:1px;opacity:0.7;margin-bottom:8px">OVR</div>
        {foto_html}
        <div style="font-weight:800;font-size:0.95rem;text-transform:uppercase;letter-spacing:1px;
            border-top:1px solid rgba(0,0,0,0.2);padding-top:6px;margin-bottom:6px">{a['nome']}</div>
        <div style="background:rgba(0,0,0,0.15);border-radius:8px;padding:4px">{attrs_html}</div>
    </div>
    """, unsafe_allow_html=True)


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
