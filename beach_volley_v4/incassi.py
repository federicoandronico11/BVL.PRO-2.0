"""
incassi.py — Gestione incassi torneo + PDF grafici
"""
import streamlit as st
import json
from pathlib import Path
from data_manager import save_state, get_squadra_by_id, get_atleta_by_id

INCASSI_FILE = "beach_volley_incassi.json"


def load_incassi():
    if Path(INCASSI_FILE).exists():
        with open(INCASSI_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tornei": {}}

def save_incassi(data):
    with open(INCASSI_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def render_incassi(state):
    st.markdown("## 💰 Gestione Incassi")
    
    incassi_data = load_incassi()
    torneo_nome = state["torneo"]["nome"] or "Torneo Senza Nome"
    torneo_data = state["torneo"].get("data", "")
    
    if torneo_nome not in incassi_data["tornei"]:
        incassi_data["tornei"][torneo_nome] = {
            "data": torneo_data,
            "quota_iscrizione": 20.0,
            "pagamenti": []
        }
    
    torneo_inc = incassi_data["tornei"][torneo_nome]
    
    tabs = st.tabs(["💳 Torneo Corrente", "📊 Storico & Grafici", "📄 Esporta PDF"])
    
    with tabs[0]:
        _render_torneo_corrente(state, torneo_inc, torneo_nome, incassi_data)
    
    with tabs[1]:
        _render_storico(incassi_data)
    
    with tabs[2]:
        _render_export_pdf(state, incassi_data)


def _render_torneo_corrente(state, torneo_inc, torneo_nome, incassi_data):
    st.markdown(f"### 💰 Incassi — {torneo_nome}")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        quota = st.number_input(
            "💶 Quota Iscrizione per Squadra (€)",
            min_value=0.0, max_value=10000.0,
            value=float(torneo_inc.get("quota_iscrizione", 20.0)),
            step=5.0
        )
        torneo_inc["quota_iscrizione"] = quota
    
    with col2:
        n_squadre = len(state["squadre"])
        totale_atteso = quota * n_squadre
        st.metric("Totale Atteso", f"€ {totale_atteso:.2f}")
    
    st.divider()
    
    # Lista squadre con stato pagamento
    st.markdown("### 📋 Pagamenti per Squadra")
    
    pagamenti = {p["squadra_id"]: p for p in torneo_inc.get("pagamenti", [])}
    
    for sq in state["squadre"]:
        pag = pagamenti.get(sq["id"], {"squadra_id": sq["id"], "pagato": False, "importo": quota, "note": ""})
        
        col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
        
        # Nomi atleti
        atleti_nomi = [get_atleta_by_id(state, aid)["nome"] for aid in sq["atleti"] if get_atleta_by_id(state, aid)]
        
        with col1:
            st.markdown(f"""
            <div style="padding:8px 0">
                <span style="font-weight:700">{sq['nome']}</span>
                <span style="color:var(--text-secondary);font-size:0.8rem;margin-left:8px">{' / '.join(atleti_nomi)}</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            importo = st.number_input("€", value=float(pag.get("importo", quota)), key=f"imp_{sq['id']}", label_visibility="collapsed", min_value=0.0)
            pag["importo"] = importo
        
        with col3:
            pagato = st.checkbox("✅ Pagato", value=pag.get("pagato", False), key=f"pag_{sq['id']}")
            pag["pagato"] = pagato
        
        with col4:
            note = st.text_input("Note", value=pag.get("note", ""), key=f"note_{sq['id']}", placeholder="es. bonifico", label_visibility="collapsed")
            pag["note"] = note
        
        pagamenti[sq["id"]] = pag
    
    torneo_inc["pagamenti"] = list(pagamenti.values())
    
    # Salva
    if st.button("💾 Salva Incassi", use_container_width=True):
        save_incassi(incassi_data)
        st.success("✅ Incassi salvati!")
    
    st.divider()
    
    # Riepilogo
    pag_list = list(pagamenti.values())
    pagati = [p for p in pag_list if p["pagato"]]
    non_pagati = [p for p in pag_list if not p["pagato"]]
    totale_incassato = sum(p["importo"] for p in pagati)
    totale_da_incassare = sum(p["importo"] for p in non_pagati)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Incassato", f"€ {totale_incassato:.2f}", f"{len(pagati)} squadre")
    with col2:
        st.metric("⏳ Da Incassare", f"€ {totale_da_incassare:.2f}", f"{len(non_pagati)} squadre")
    with col3:
        perc = round(totale_incassato / totale_atteso * 100, 1) if totale_atteso > 0 else 0
        st.metric("📊 % Incassato", f"{perc}%")


def _render_storico(incassi_data):
    st.markdown("### 📊 Storico Incassi Tornei")
    
    if not incassi_data["tornei"]:
        st.info("Nessun torneo registrato ancora.")
        return
    
    # Tabella riassuntiva
    dati_tornei = []
    for nome, t in incassi_data["tornei"].items():
        pag = t.get("pagamenti", [])
        incassato = sum(p["importo"] for p in pag if p.get("pagato"))
        da_incassare = sum(p["importo"] for p in pag if not p.get("pagato"))
        n_sq = len(pag)
        dati_tornei.append({
            "Torneo": nome,
            "Data": t.get("data", "—"),
            "Squadre": n_sq,
            "Incassato (€)": incassato,
            "Da Incassare (€)": da_incassare,
            "Totale (€)": incassato + da_incassare,
        })
    
    # HTML table
    totale_gen = sum(d["Incassato (€)"] for d in dati_tornei)
    
    html = """
    <table class="rank-table">
    <tr>
        <th style="text-align:left">TORNEO</th><th>DATA</th><th>SQUADRE</th>
        <th>INCASSATO</th><th>DA INCASSARE</th><th>TOTALE</th>
    </tr>"""
    for d in dati_tornei:
        html += f"""<tr>
            <td style="text-align:left;font-weight:700">{d['Torneo']}</td>
            <td>{d['Data']}</td><td>{d['Squadre']}</td>
            <td style="color:var(--green);font-weight:700">€ {d['Incassato (€)']:.2f}</td>
            <td style="color:var(--accent1)">€ {d['Da Incassare (€)']:.2f}</td>
            <td style="font-weight:700;color:var(--accent-gold)">€ {d['Totale (€)']:.2f}</td>
        </tr>"""
    html += f"""<tr style="border-top:2px solid var(--accent-gold)">
        <td colspan="3" style="text-align:right;font-weight:700;font-family:var(--font-display)">TOTALE GENERALE</td>
        <td colspan="3" style="font-weight:800;color:var(--accent-gold);font-size:1.1rem;font-family:var(--font-display)">
            € {totale_gen:.2f}
        </td>
    </tr>"""
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)
    
    st.divider()
    
    # Grafico incassi mensili
    import pandas as pd
    from collections import defaultdict
    
    mensili = defaultdict(float)
    for nome, t in incassi_data["tornei"].items():
        data_str = t.get("data", "")
        if data_str and len(data_str) >= 7:
            mese = data_str[:7]  # "YYYY-MM"
            incassato = sum(p["importo"] for p in t.get("pagamenti", []) if p.get("pagato"))
            mensili[mese] += incassato
    
    if mensili:
        st.markdown("### 📈 Incassi Mensili")
        df = pd.DataFrame([{"Mese": k, "Incassi (€)": v} for k, v in sorted(mensili.items())])
        df = df.set_index("Mese")
        st.bar_chart(df, color="#00c851", height=250, use_container_width=True)


def _render_export_pdf(state, incassi_data):
    st.markdown("### 📄 Esporta in PDF")
    
    st.info("Genera un PDF completo con tutti gli incassi e i dettagli dei pagamenti.")
    
    torneo_nome = state["torneo"]["nome"] or "Torneo"
    
    col1, col2 = st.columns(2)
    with col1:
        includi_dettaglio = st.checkbox("Includi dettaglio per atleta", value=True)
    with col2:
        includi_storico = st.checkbox("Includi storico tutti i tornei", value=True)
    
    if st.button("🖨️ GENERA PDF INCASSI", use_container_width=True):
        try:
            pdf_path = _genera_pdf_incassi(state, incassi_data, torneo_nome, includi_dettaglio, includi_storico)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "⬇️ SCARICA PDF",
                    f,
                    file_name=f"incassi_{torneo_nome.replace(' ','_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"Errore generazione PDF: {e}")


def _genera_pdf_incassi(state, incassi_data, torneo_nome, includi_dettaglio, includi_storico):
    """Genera PDF con reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    
    pdf_path = f"/tmp/incassi_{torneo_nome.replace(' ','_')}.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    
    styles = getSampleStyleSheet()
    
    DARK = colors.HexColor("#0a0a0f")
    RED = colors.HexColor("#e8002d")
    BLUE = colors.HexColor("#0070f3")
    GOLD = colors.HexColor("#ffd700")
    GREEN = colors.HexColor("#00c851")
    LIGHT = colors.HexColor("#f0f0f0")
    WHITE = colors.white
    
    title_style = ParagraphStyle("title", parent=styles["Title"],
                                  fontName="Helvetica-Bold", fontSize=22,
                                  textColor=RED, spaceAfter=4)
    h2_style = ParagraphStyle("h2", parent=styles["Heading2"],
                               fontName="Helvetica-Bold", fontSize=14,
                               textColor=DARK, spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle("body", parent=styles["Normal"],
                                 fontName="Helvetica", fontSize=10, spaceAfter=4)
    
    story = []
    
    # Header
    story.append(Paragraph("🏐 BEACH VOLLEY TOURNAMENT MANAGER", title_style))
    story.append(Paragraph(f"Report Incassi — {torneo_nome}", h2_style))
    story.append(HRFlowable(width="100%", thickness=2, color=RED))
    story.append(Spacer(1, 8))
    
    # Torneo corrente
    if torneo_nome in incassi_data["tornei"]:
        t = incassi_data["tornei"][torneo_nome]
        pag_list = t.get("pagamenti", [])
        quota = t.get("quota_iscrizione", 0)
        
        story.append(Paragraph(f"Torneo: {torneo_nome} | Data: {t.get('data','—')} | Quota: €{quota:.2f}/squadra", body_style))
        story.append(Spacer(1, 6))
        
        # Tabella pagamenti
        table_data = [["SQUADRA", "ATLETI", "IMPORTO", "STATO", "NOTE"]]
        totale_inc = 0
        totale_pend = 0
        
        for p in pag_list:
            sq = get_squadra_by_id(state, p["squadra_id"])
            if not sq:
                continue
            atleti = [get_atleta_by_id(state, aid)["nome"] for aid in sq["atleti"] if get_atleta_by_id(state, aid)]
            stato = "✓ PAGATO" if p.get("pagato") else "⏳ PENDENTE"
            if p.get("pagato"):
                totale_inc += p["importo"]
            else:
                totale_pend += p["importo"]
            table_data.append([
                sq["nome"],
                " / ".join(atleti),
                f"€ {p['importo']:.2f}",
                stato,
                p.get("note", "")
            ])
        
        # Totali
        table_data.append(["", "", "", "", ""])
        table_data.append(["TOTALE INCASSATO", "", f"€ {totale_inc:.2f}", "✓", ""])
        table_data.append(["TOTALE PENDENTE", "", f"€ {totale_pend:.2f}", "⏳", ""])
        table_data.append(["TOTALE GENERALE", "", f"€ {totale_inc + totale_pend:.2f}", "", ""])
        
        tbl = Table(table_data, colWidths=[45*mm, 60*mm, 25*mm, 25*mm, 25*mm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ALIGN", (0, 0), (1, -1), "LEFT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -4), [LIGHT, WHITE]),
            ("BACKGROUND", (0, -3), (-1, -3), colors.HexColor("#e8f5e9")),
            ("BACKGROUND", (0, -2), (-1, -2), colors.HexColor("#fff3e0")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#fff9c4")),
            ("FONTNAME", (0, -3), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(tbl)
    
    # Storico
    if includi_storico and len(incassi_data["tornei"]) > 1:
        story.append(Spacer(1, 12))
        story.append(HRFlowable(width="100%", thickness=1, color=BLUE))
        story.append(Paragraph("STORICO TUTTI I TORNEI", h2_style))
        
        storico_data = [["TORNEO", "DATA", "SQUADRE", "INCASSATO", "PENDENTE", "TOTALE"]]
        for nome, t in incassi_data["tornei"].items():
            pag = t.get("pagamenti", [])
            inc = sum(p["importo"] for p in pag if p.get("pagato"))
            pend = sum(p["importo"] for p in pag if not p.get("pagato"))
            storico_data.append([nome, t.get("data","—"), str(len(pag)),
                                  f"€{inc:.2f}", f"€{pend:.2f}", f"€{inc+pend:.2f}"])
        
        tot_gen = sum(
            sum(p["importo"] for p in t.get("pagamenti",[]) if p.get("pagato"))
            for t in incassi_data["tornei"].values()
        )
        storico_data.append(["TOTALE", "", "", f"€{tot_gen:.2f}", "", ""])
        
        tbl2 = Table(storico_data, colWidths=[55*mm, 25*mm, 20*mm, 25*mm, 25*mm, 25*mm])
        tbl2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [LIGHT, WHITE]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#fff9c4")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(tbl2)
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("Documento generato da Beach Volley Tournament Manager Pro", 
                            ParagraphStyle("footer", fontName="Helvetica", fontSize=8, textColor=colors.grey)))
    
    doc.build(story)
    return pdf_path
