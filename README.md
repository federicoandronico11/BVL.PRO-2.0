# 🏐 Beach Volley Tournament Manager Pro — v3

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
├── theme_manager.py        ← 8 temi, 8 stili tabellone, sponsor/banner
├── ui_components.py        ← Componenti riutilizzabili (match card, podio)
├── fase_setup.py           ← Fase 1: Setup + iscrizioni + impostazioni avanzate
├── fase_gironi.py          ← Fase 2: Gironi + scoreboard + classifiche
├── fase_eliminazione.py    ← Fase 3: Bracket eliminazione
├── fase_proclamazione.py   ← Fase 4: Podio + ranking + carriere
├── segnapunti_live.py      ← Segnapunti LIVE (8 stili + modalità libera)
├── ranking_page.py         ← Ranking + card FIFA + trofei + carriere
├── incassi.py              ← Pagamenti + export PDF
├── requirements.txt
├── .gitignore
└── README.md

# Generati automaticamente — NON committare (già in .gitignore):
# beach_volley_data.json
# beach_volley_theme.json
# beach_volley_incassi.json
```

## ✅ Funzionalità v3

### 🎨 Personalizzazione Tema
- 8 temi completamente diversi con anteprima cliccabile
- Upload logo e banner sponsor con scelta di posizione
- Fino a 4 loghi sponsor nella sidebar
- Impostazioni layout (larghezza sidebar, stile header, animazioni)

### 🏐 Tabellone Segnapunti LIVE
- 8 stili grafici con miniatura anteprima selezionabile
- Modalità libera (funziona anche senza torneo avviato)

### ⚙️ Setup Avanzato
- Formato 2x2 · 3x3 · 4x4
- Teste di serie da ranking in-app
- Riordino squadre nel tabellone prima dell'avvio

### 🃏 Card FIFA/EAFC
- 5 rarità: Bronzo · Argento · Oro · Oro Raro · Leggenda
- Overall 45–99 calcolato da statistiche reali
- Upload foto profilo sulla card

### 🏆 8 Trofei sbloccabili
Principiante → Dilettante → Esordiente → Esperto → Campione → Eroe → Leggenda → Nell'Olimpo

### 📱 Navigazione
- Barra in basso stile Instagram (6 sezioni)
- Sidebar con OVR, prossimi trofei, sponsor

## 📝 Note
- I `.json` vengono creati al primo avvio e sono già in `.gitignore`
- Reset torneo: pulsante "⚠️ Reset" in sidebar (mantiene atleti e ranking)
- Nuovo torneo: "🏆 Proclamazione" → "🔄 Nuovo Torneo"
