# 🏐 Beach Volley Tournament Manager Pro — v4

App professionale per la gestione di tornei di beach volley con UI Dark Mode avanzata.

## 🚀 Installazione e Avvio

```bash
git clone https://github.com/tuo-username/beach-volley-manager.git
cd beach-volley-manager
pip install -r requirements.txt
streamlit run app.py
```

L'app si apre su `http://localhost:8501`

## 📦 Dipendenze

```
streamlit>=1.32.0
pandas>=2.0.0
reportlab>=4.0.0
```

## 📁 Struttura File

```
beach_volley_manager/
├── app.py                  ← Entry point, routing, sidebar, bottom nav bar
├── data_manager.py         ← Modelli dati, JSON, trofei, card FIFA, overall
├── theme_manager.py        ← 8 temi, 14+ tabelloni, sponsor/banner, builder custom
├── ui_components.py        ← Componenti riutilizzabili (match card, podio)
├── fase_setup.py           ← Fase 1: Setup + iscrizioni + quote iscrizione
├── fase_gironi.py          ← Fase 2: Gironi + scoreboard + classifiche
├── fase_eliminazione.py    ← Fase 3: Bracket eliminazione
├── fase_proclamazione.py   ← Fase 4: Podio + ranking + carriere
├── segnapunti_live.py      ← Segnapunti LIVE (14+ stili + modalità libera)
├── ranking_page.py         ← Ranking + card FIFA + trofei + carriere + profili
├── incassi.py              ← Pagamenti + export PDF
├── requirements.txt
└── README.md
```

## ✅ Novità v4

### 🃏 Nuovo Sistema Card Giocatori (9 tier)
- **Bronzo Comune** (45-49 OVR) — gradiente caldo
- **Bronzo Raro** (50-54 OVR) — pattern a diamante
- **Argento Comune** (55-59 OVR) — metallico grigio
- **Argento Raro** (60-64 OVR) — blu elettrico ✦✦✦
- **Oro Comune** (65-69 OVR) — oro classico
- **Oro Raro** (70-74 OVR) ✨ — oro con bordo arancio
- **Eroe** (75-79 OVR) ⚡ — viola con effetti radianti
- **Leggenda** (80-84 OVR) 👑 — oro bianco e arancio, doppie fasce
- **Dio dell'Olimpo** (85-99 OVR) 🌩️⚡ — ali, tuoni, animazioni CSS

### 👤 Profili Atleti Migliorati
- Modifica nome, cognome e foto direttamente dalla scheda carriera
- Click su una card → apre direttamente il profilo carriera
- Tutti i trofei (sbloccati + bloccati) in un'unica lista nel profilo
- Statistiche complete: punti, set, partite, vittorie, sconfitte, quozienti

### 🏅 Classifica ELO Sidebar Interattiva
- Click sul nome di ogni atleta → apre mini popup con foto, stats e trofei
- Link diretto al profilo completo dal popup
- Icona tipo card accanto al nome

### 🏆 Sezione Trofei Dedicata
- Pagina trofei con effetto hover (ingrandisce e mostra come ottenerlo)
- 12 trofei totali (nuovi: Iron Man, Cecchino, Veterano, Dominatore)
- Personalizzazione: upload banner, immagini custom

### 🏐 Tabelloni Live (14+ stili)
- 8 stili originali + 6 nuovi: Split Color, Championship Bold, Minimal Duo, Volleyball Pro, Matrix Digital, Sunrise Gradient
- **Builder Tabellone Custom**: crea il tuo da zero
  - Personalizza colori, font, dimensioni, bordi
  - Layout: orizzontale, verticale, split color
  - Aggiungi/togli elementi (set, battuta, timer)
  - Anteprima live in tempo reale

### 💶 Quote Iscrizione nelle Squadre
- Campo quota al momento dell'iscrizione squadra
- Totale quote raccolte visibile nella lista squadre

### 🗑️ .gitignore
```
beach_volley_data.json
beach_volley_theme.json
beach_volley_incassi.json
__pycache__/
*.pyc
```

## 📝 Note
- I `.json` vengono creati al primo avvio
- Reset torneo: pulsante "⚠️ Reset" in sidebar (mantiene atleti e ranking)
- Nuovo torneo: "🏆 Proclamazione" → "🔄 Nuovo Torneo"
