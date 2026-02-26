"""
theme_manager.py — Sistema temi avanzato: 8 temi unici + 8 tabelloni LIVE + sponsor/banner
"""
import streamlit as st
import json, base64
from pathlib import Path

THEMES = {
    "Dynamic DAZN": {
        "bg_primary": "#0a0a0f", "bg_card": "#13131a", "bg_card2": "#1a1a24",
        "accent1": "#e8002d", "accent2": "#0070f3", "accent_gold": "#ffd700",
        "text_primary": "#ffffff", "text_secondary": "#a0a0b0", "border": "#2a2a3a",
        "green": "#00c851", "font_display": "Barlow Condensed", "font_body": "Barlow",
        "font_url": "https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;800&family=Barlow:wght@400;500;600&display=swap",
        "card_radius": "12px", "sidebar_bg": "#13131a",
        "header_gradient": "linear-gradient(135deg,#0a0a0f 0%,#1a1a2e 50%,#0a0a0f 100%)",
        "description": "Dark professionale stile broadcaster sportivo", "preview_icon": "📺",
        "extra_css": ""
    },
    "Futuristico Neon": {
        "bg_primary": "#020212", "bg_card": "#080820", "bg_card2": "#0d0d28",
        "accent1": "#00f5ff", "accent2": "#bf00ff", "accent_gold": "#f0e040",
        "text_primary": "#e0eeff", "text_secondary": "#5060a0", "border": "#1a1a50",
        "green": "#00ff88", "font_display": "Orbitron", "font_body": "Exo 2",
        "font_url": "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600&display=swap",
        "card_radius": "4px", "sidebar_bg": "#080820",
        "header_gradient": "linear-gradient(135deg,#020212,#0a0030,#020212)",
        "description": "Futuristico con glow neon e font tech", "preview_icon": "🚀",
        "extra_css": ".tournament-title{color:var(--accent1)!important;text-shadow:0 0 30px rgba(0,245,255,0.6)!important;}.stButton>button{background:transparent!important;border:1px solid var(--accent1)!important;color:var(--accent1)!important;}.stButton>button:hover{background:var(--accent1)!important;color:#000!important;}"
    },
    "Beach Sunset": {
        "bg_primary": "#1a0a00", "bg_card": "#2d1500", "bg_card2": "#3d2010",
        "accent1": "#ff6b1a", "accent2": "#ffcc00", "accent_gold": "#ff9900",
        "text_primary": "#fff8f0", "text_secondary": "#c0905a", "border": "#4a2a10",
        "green": "#80ff40", "font_display": "Playfair Display", "font_body": "Lato",
        "font_url": "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Lato:wght@300;400;700&display=swap",
        "card_radius": "16px", "sidebar_bg": "#2d1500",
        "header_gradient": "linear-gradient(135deg,#3d1000 0%,#7a3010 40%,#ff6b1a 100%)",
        "description": "Tramonto sulla spiaggia — caldi e dorati", "preview_icon": "🌅",
        "extra_css": ".tournament-title{color:#ffcc00!important;text-shadow:2px 2px 8px rgba(255,107,26,0.8)!important;}.stButton>button{background:linear-gradient(135deg,#ff6b1a,#ff9900)!important;color:#000!important;font-weight:800!important;}"
    },
    "Ice Crystal": {
        "bg_primary": "#f0f8ff", "bg_card": "#ffffff", "bg_card2": "#e8f4ff",
        "accent1": "#0057b8", "accent2": "#00aaff", "accent_gold": "#1a6bb5",
        "text_primary": "#001530", "text_secondary": "#4a7aa0", "border": "#c0d8f0",
        "green": "#007733", "font_display": "Montserrat", "font_body": "Open Sans",
        "font_url": "https://fonts.googleapis.com/css2?family=Montserrat:wght@500;700;900&family=Open+Sans:wght@300;400;600&display=swap",
        "card_radius": "20px", "sidebar_bg": "#ffffff",
        "header_gradient": "linear-gradient(135deg,#e0f0ff 0%,#c0e0ff 50%,#e0f0ff 100%)",
        "description": "Pulito e cristallino — luminoso e professionale", "preview_icon": "❄️",
        "extra_css": "html,body,[class*='css']{background-color:#f0f8ff!important;color:#001530!important;}.tournament-title{color:#0057b8!important;}.stButton>button{background:#0057b8!important;}"
    },
    "FC Ultimate": {
        "bg_primary": "#050d1a", "bg_card": "#0a1628", "bg_card2": "#112035",
        "accent1": "#10d9a8", "accent2": "#ff5733", "accent_gold": "#ffc72c",
        "text_primary": "#ffffff", "text_secondary": "#6688aa", "border": "#1a2e45",
        "green": "#10d9a8", "font_display": "Bebas Neue", "font_body": "Rajdhani",
        "font_url": "https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@400;500;600;700&display=swap",
        "card_radius": "8px", "sidebar_bg": "#0a1628",
        "header_gradient": "linear-gradient(135deg,#050d1a 0%,#0d2040 50%,#050d1a 100%)",
        "description": "Stile videogioco calcio — bold e dinamico", "preview_icon": "⚽",
        "extra_css": ".tournament-title{font-size:3.5rem!important;letter-spacing:5px!important;}.match-card-header{background:var(--accent1)!important;color:#000!important;}.stButton>button{background:var(--accent1)!important;color:#000!important;font-weight:900!important;}"
    },
    "Retro Arcade": {
        "bg_primary": "#0f0f23", "bg_card": "#1a1a2e", "bg_card2": "#16213e",
        "accent1": "#ff6b6b", "accent2": "#ffd93d", "accent_gold": "#ffd93d",
        "text_primary": "#e8e8e8", "text_secondary": "#7f7f9f", "border": "#2a2a4a",
        "green": "#6bcb77", "font_display": "Press Start 2P", "font_body": "VT323",
        "font_url": "https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323:wght@400&display=swap",
        "card_radius": "0px", "sidebar_bg": "#1a1a2e",
        "header_gradient": "linear-gradient(180deg,#0f0f23,#1a1a2e)",
        "description": "8-bit retro gaming — pixelato e nostalgico", "preview_icon": "🕹️",
        "extra_css": ".tournament-title{font-size:1.2rem!important;letter-spacing:3px!important;}.match-card{border:3px solid var(--accent1)!important;border-radius:0!important;box-shadow:5px 5px 0 var(--accent2)!important;}.stButton>button{border-radius:0!important;border:3px solid var(--accent1)!important;background:#0f0f23!important;color:var(--accent1)!important;box-shadow:3px 3px 0 var(--accent1)!important;font-size:0.5rem!important;}"
    },
    "Elegante Marble": {
        "bg_primary": "#1a1612", "bg_card": "#252018", "bg_card2": "#2e2820",
        "accent1": "#c9a84c", "accent2": "#8b6914", "accent_gold": "#c9a84c",
        "text_primary": "#f5f0e8", "text_secondary": "#908060", "border": "#403828",
        "green": "#5a8a3a", "font_display": "Cormorant Garamond", "font_body": "EB Garamond",
        "font_url": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700;800&family=EB+Garamond:wght@400;500&display=swap",
        "card_radius": "2px", "sidebar_bg": "#252018",
        "header_gradient": "linear-gradient(135deg,#1a1612,#2e2820,#1a1612)",
        "description": "Lusso ed eleganza — oro e marmo scuro", "preview_icon": "🏛️",
        "extra_css": ".tournament-title{color:var(--accent1)!important;font-style:italic!important;}.match-card{border-left:3px solid var(--accent1)!important;border-radius:0!important;}.stButton>button{background:var(--accent1)!important;color:#1a1612!important;border-radius:0!important;}"
    },
    "Ocean Breeze": {
        "bg_primary": "#001f3f", "bg_card": "#00294f", "bg_card2": "#003360",
        "accent1": "#00c8ff", "accent2": "#00ff88", "accent_gold": "#ffe033",
        "text_primary": "#e0f0ff", "text_secondary": "#6090b0", "border": "#004878",
        "green": "#00ff88", "font_display": "Nunito", "font_body": "Nunito",
        "font_url": "https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;700;900&display=swap",
        "card_radius": "24px", "sidebar_bg": "#00294f",
        "header_gradient": "linear-gradient(135deg,#001f3f 0%,#003d7a 50%,#001f3f 100%)",
        "description": "Mare e spiaggia — fresco e acquatico", "preview_icon": "🌊",
        "extra_css": ".tournament-title{color:var(--accent1)!important;text-shadow:0 0 20px rgba(0,200,255,0.4)!important;}.match-card{border-radius:24px!important;}.stButton>button{border-radius:50px!important;background:linear-gradient(135deg,#00c8ff,#0090cc)!important;}"
    },
}

SCOREBOARD_STYLES = {
    "Classic Stadium": {
        "description": "Tabellone classico stile stadio — bianco su nero",
        "preview_icon": "🏟️", "bg": "#000000", "text1": "#ffffff", "text2": "#ffdd00",
        "score_bg": "#1a1a1a", "score_color": "#ffffff", "team_size": "2.2rem",
        "score_size": "8rem", "border_style": "3px solid #555",
        "extra": "border-radius:4px;font-family:'Courier New',monospace;"
    },
    "DAZN Live": {
        "description": "Stile broadcaster moderno — rosso e bianco",
        "preview_icon": "📺", "bg": "#0a0a0f", "text1": "#e8002d", "text2": "#0070f3",
        "score_bg": "#13131a", "score_color": "#ffffff", "team_size": "2rem",
        "score_size": "7rem", "border_style": "2px solid #e8002d",
        "extra": "border-radius:12px;"
    },
    "Neon Arena": {
        "description": "Glow neon fluorescente — futuro vibrante",
        "preview_icon": "💜", "bg": "#020212", "text1": "#00f5ff", "text2": "#bf00ff",
        "score_bg": "#080820", "score_color": "#00f5ff", "team_size": "2rem",
        "score_size": "7.5rem", "border_style": "2px solid #00f5ff",
        "extra": "border-radius:4px;box-shadow:0 0 40px rgba(0,245,255,0.2);"
    },
    "Beach Vibes": {
        "description": "Colori tropicali — arancio e sole",
        "preview_icon": "🏖️", "bg": "#1a0a00", "text1": "#ff6b1a", "text2": "#ffcc00",
        "score_bg": "#2d1500", "score_color": "#ffcc00", "team_size": "2rem",
        "score_size": "7rem", "border_style": "3px solid #ff6b1a",
        "extra": "border-radius:16px;"
    },
    "Ice Cold": {
        "description": "Freddo cristallino — azzurro su bianco",
        "preview_icon": "🧊", "bg": "#f0f8ff", "text1": "#0057b8", "text2": "#00aaff",
        "score_bg": "#ffffff", "score_color": "#0057b8", "team_size": "2rem",
        "score_size": "7rem", "border_style": "3px solid #0057b8",
        "extra": "border-radius:20px;box-shadow:0 10px 40px rgba(0,87,184,0.15);"
    },
    "Pixel Retro": {
        "description": "8-bit pixelato — retro gaming",
        "preview_icon": "👾", "bg": "#0f0f23", "text1": "#ff6b6b", "text2": "#ffd93d",
        "score_bg": "#1a1a2e", "score_color": "#ffd93d", "team_size": "1.2rem",
        "score_size": "5rem", "border_style": "4px solid #ff6b6b",
        "extra": "border-radius:0;box-shadow:6px 6px 0 #ffd93d;"
    },
    "Golden Prestige": {
        "description": "Elegante e lussuoso — oro e marmo",
        "preview_icon": "🏆", "bg": "#1a1612", "text1": "#c9a84c", "text2": "#f5f0e8",
        "score_bg": "#252018", "score_color": "#c9a84c", "team_size": "2.2rem",
        "score_size": "7rem", "border_style": "2px solid #c9a84c",
        "extra": "border-radius:2px;"
    },
    "Split Color": {
        "description": "Due colori divisi verticalmente — essenziale e pulito",
        "preview_icon": "⬛", "bg": "#111111", "text1": "#ffffff", "text2": "#ffffff",
        "score_bg": "#000000", "score_color": "#ffffff", "team_size": "2.5rem",
        "score_size": "9rem", "border_style": "none",
        "extra": "border-radius:0;"
    },
    "Championship Bold": {
        "description": "Grandi numeri, stile campionato internazionale",
        "preview_icon": "🏟️", "bg": "#001a33", "text1": "#FFD700", "text2": "#00AAFF",
        "score_bg": "#000d1a", "score_color": "#FFD700", "team_size": "2.8rem",
        "score_size": "10rem", "border_style": "4px solid #FFD700",
        "extra": "border-radius:0;font-family:'Impact',sans-serif;"
    },
    "Minimal Duo": {
        "description": "Solo punteggi e colori — massima leggibilità",
        "preview_icon": "🔲", "bg": "#1a1a1a", "text1": "#ff4444", "text2": "#4444ff",
        "score_bg": "#1a1a1a", "score_color": "#ffffff", "team_size": "2rem",
        "score_size": "8rem", "border_style": "none",
        "extra": "border-radius:0;"
    },
    "Volleyball Pro": {
        "description": "Stile ufficiale beach volley — bicolore con logo sport",
        "preview_icon": "🏐", "bg": "#002244", "text1": "#FFD700", "text2": "#FF6600",
        "score_bg": "#001122", "score_color": "#FFD700", "team_size": "2.2rem",
        "score_size": "8rem", "border_style": "3px solid #FFD700",
        "extra": "border-radius:8px;"
    },
    "Matrix Digital": {
        "description": "Verde digitale su nero — hacker terminal style",
        "preview_icon": "💻", "bg": "#000500", "text1": "#00ff41", "text2": "#00aa20",
        "score_bg": "#001000", "score_color": "#00ff41", "team_size": "2rem",
        "score_size": "7rem", "border_style": "1px solid #00ff41",
        "extra": "border-radius:0;font-family:'Courier New',monospace;text-shadow:0 0 8px #00ff41;"
    },
    "Sunrise Gradient": {
        "description": "Gradiente aurora boreale — colorato e vivace",
        "preview_icon": "🌄", "bg": "linear-gradient(135deg,#1a0040,#400040,#800020)", "text1": "#ff88ff", "text2": "#ffaa00",
        "score_bg": "rgba(0,0,0,0.4)", "score_color": "#ffffff", "team_size": "2rem",
        "score_size": "7rem", "border_style": "1px solid rgba(255,136,255,0.4)",
        "extra": "border-radius:16px;"
    },
    "Minimal Pro": {
        "description": "Ultra minimalista — bianco e nero pulito",
        "preview_icon": "⬜", "bg": "#ffffff", "text1": "#1a1a1a", "text2": "#555555",
        "score_bg": "#f5f5f5", "score_color": "#1a1a1a", "team_size": "2rem",
        "score_size": "6.5rem", "border_style": "2px solid #1a1a1a",
        "extra": "border-radius:0;"
    },
}

THEME_FILE = "beach_volley_theme.json"

def load_theme_config():
    if Path(THEME_FILE).exists():
        with open(THEME_FILE, "r") as f:
            return json.load(f)
    return {
        "theme_name": "Dynamic DAZN",
        "color_primary": "#e8002d", "color_secondary": "#0070f3", "color_detail": "#ffd700",
        "logo_b64": None, "logo_name": None,
        "scoreboard_style": "DAZN Live",
        "sponsors": [], "banner_b64": None,
        "banner_position": "Sotto l'header",
        "sidebar_width": "normale", "card_size": "normale",
        "show_bottom_nav": True, "show_sponsors_sidebar": True,
        "header_style": "Grande con gradiente", "animations": True, "show_weather": False,
    }

def save_theme_config(cfg):
    with open(THEME_FILE, "w") as f:
        json.dump(cfg, f)

def get_active_theme(cfg):
    t = THEMES.get(cfg.get("theme_name", "Dynamic DAZN"), THEMES["Dynamic DAZN"]).copy()
    t["accent1"] = cfg.get("color_primary", t["accent1"])
    t["accent2"] = cfg.get("color_secondary", t["accent2"])
    t["accent_gold"] = cfg.get("color_detail", t["accent_gold"])
    return t

def get_active_scoreboard(cfg):
    return SCOREBOARD_STYLES.get(cfg.get("scoreboard_style", "DAZN Live"), SCOREBOARD_STYLES["DAZN Live"])

def inject_theme_css(cfg):
    t = get_active_theme(cfg)
    logo_b64 = cfg.get("logo_b64")
    if logo_b64:
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:60px;object-fit:contain;margin-bottom:8px">'
    else:
        logo_html = '<div style="font-size:3rem">🏐</div>'

    css = f"""
    <style>
    @import url('{t["font_url"]}');
    :root {{
        --bg-primary:{t["bg_primary"]};--bg-card:{t["bg_card"]};--bg-card2:{t["bg_card2"]};
        --accent1:{t["accent1"]};--accent-red:{t["accent1"]};--accent2:{t["accent2"]};
        --accent-blue:{t["accent2"]};--accent-gold:{t["accent_gold"]};
        --text-primary:{t["text_primary"]};--text-secondary:{t["text_secondary"]};
        --border:{t["border"]};--green:{t["green"]};--radius:{t["card_radius"]};
        --font-display:'{t["font_display"]}',sans-serif;--font-body:'{t["font_body"]}',sans-serif;
    }}
    html,body,[class*="css"]{{background-color:var(--bg-primary)!important;color:var(--text-primary)!important;font-family:var(--font-body)!important;}}
    #MainMenu,footer,header{{visibility:hidden;}}
    .block-container{{padding-top:0.5rem!important;max-width:1400px!important;padding-bottom:80px!important;}}

    /* BOTTOM NAV */
    .bottom-nav{{position:fixed;bottom:0;left:0;right:0;background:var(--bg-card);border-top:2px solid var(--accent1);display:flex;justify-content:space-around;align-items:center;padding:8px 0;z-index:9999;backdrop-filter:blur(10px);}}
    .bottom-nav-item{{display:flex;flex-direction:column;align-items:center;gap:2px;cursor:pointer;padding:6px 12px;border-radius:8px;transition:all 0.2s;min-width:60px;}}
    .bottom-nav-item:hover{{background:var(--bg-card2);}}
    .bottom-nav-item.active{{background:var(--accent1)!important;}}
    .bottom-nav-item.active .nav-icon,.bottom-nav-item.active .nav-label{{color:white!important;}}
    .nav-icon{{font-size:1.4rem;}}
    .nav-label{{font-size:0.5rem;letter-spacing:1px;text-transform:uppercase;color:var(--text-secondary);font-weight:600;}}

    /* HEADER */
    .tournament-header{{background:{t["header_gradient"]};border-bottom:3px solid var(--accent1);padding:20px 30px;text-align:center;margin-bottom:20px;position:relative;overflow:hidden;}}
    .tournament-header::before{{content:'';position:absolute;top:0;left:-100%;width:300%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.03),transparent);animation:shimmer 4s infinite;}}
    @keyframes shimmer{{to{{left:100%;}}}}
    .tournament-title{{font-family:var(--font-display)!important;font-size:2.8rem!important;font-weight:800!important;letter-spacing:3px!important;text-transform:uppercase!important;color:var(--text-primary)!important;margin:0!important;}}
    .tournament-subtitle{{color:var(--accent1);font-size:0.85rem;letter-spacing:4px;text-transform:uppercase;font-weight:600;margin-top:4px;}}

    /* FASE BADGE */
    .fase-badge{{display:inline-flex;align-items:center;gap:8px;background:var(--bg-card2);border:1px solid var(--border);border-radius:20px;padding:6px 16px;font-size:0.75rem;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--text-secondary);margin:4px;}}
    .fase-badge.active{{background:var(--accent1);border-color:var(--accent1);color:white;}}
    .fase-badge.done{{background:var(--bg-card2);border-color:var(--green);color:var(--green);}}

    /* MATCH CARD */
    .match-card{{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:0;margin-bottom:12px;overflow:hidden;transition:border-color 0.2s;}}
    .match-card:hover{{border-color:var(--accent1);}}
    .match-card.confirmed{{border-left:4px solid var(--green);}}
    .match-card-header{{background:var(--bg-card2);padding:8px 16px;font-size:0.7rem;letter-spacing:2px;text-transform:uppercase;color:var(--text-secondary);font-weight:600;}}
    .match-body{{padding:16px;display:flex;align-items:center;gap:12px;}}
    .team-side{{flex:1;text-align:center;}}
    .team-name{{font-family:var(--font-display);font-size:1.4rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;}}
    .team-red .team-name{{color:var(--accent1);}}
    .team-blue .team-name{{color:var(--accent2);}}
    .team-players{{font-size:0.75rem;color:var(--text-secondary);margin-top:4px;}}
    .score-center{{text-align:center;min-width:100px;}}
    .score-sets{{font-family:var(--font-display);font-size:3rem;font-weight:800;color:white;line-height:1;}}
    .score-sets span{{color:var(--text-secondary);font-size:2rem;}}
    .score-parziale{{font-size:0.75rem;color:var(--text-secondary);margin-top:4px;}}

    /* RANK TABLE */
    .rank-table{{width:100%;border-collapse:collapse;}}
    .rank-table th{{background:var(--bg-card2);color:var(--text-secondary);font-size:0.7rem;letter-spacing:2px;text-transform:uppercase;padding:10px 14px;text-align:center;border-bottom:1px solid var(--border);}}
    .rank-table td{{padding:12px 14px;text-align:center;border-bottom:1px solid var(--border);font-size:0.9rem;}}
    .rank-table tr:hover td{{background:var(--bg-card2);}}
    .rank-pos{{font-family:var(--font-display);font-weight:800;font-size:1.2rem;}}
    .rank-pos.gold{{color:var(--accent-gold);}}
    .rank-pos.silver{{color:#c0c0c0;}}
    .rank-pos.bronze{{color:#cd7f32;}}

    /* PODIO */
    .podio-container{{display:flex;align-items:flex-end;justify-content:center;gap:12px;padding:30px 0;}}
    .podio-step{{text-align:center;border-radius:8px 8px 0 0;padding:20px 24px 16px;min-width:150px;}}
    .podio-1{{background:linear-gradient(180deg,#b8860b,#ffd700);height:180px;display:flex;flex-direction:column;justify-content:flex-end;}}
    .podio-2{{background:linear-gradient(180deg,#808080,#c0c0c0);height:140px;display:flex;flex-direction:column;justify-content:flex-end;}}
    .podio-3{{background:linear-gradient(180deg,#8b4513,#cd7f32);height:110px;display:flex;flex-direction:column;justify-content:flex-end;}}
    .podio-rank{{font-family:var(--font-display);font-size:2rem;font-weight:800;color:rgba(0,0,0,0.7);}}
    .podio-name{{font-weight:700;font-size:0.9rem;color:rgba(0,0,0,0.9);text-transform:uppercase;letter-spacing:1px;}}

    /* WINNER BANNER */
    .winner-banner{{background:linear-gradient(135deg,#b8860b,#ffd700,#b8860b);border-radius:var(--radius);padding:30px;text-align:center;margin:20px 0;animation:pulse-gold 2s ease-in-out infinite;}}
    @keyframes pulse-gold{{0%,100%{{box-shadow:0 0 20px rgba(255,215,0,0.4);}}50%{{box-shadow:0 0 50px rgba(255,215,0,0.8);}}}}
    .winner-title{{font-family:var(--font-display);font-size:1rem;letter-spacing:4px;text-transform:uppercase;color:rgba(0,0,0,0.7);font-weight:700;}}
    .winner-name{{font-family:var(--font-display);font-size:3rem;font-weight:800;color:#1a0a00;text-transform:uppercase;letter-spacing:4px;}}
    .winner-players{{color:rgba(0,0,0,0.6);font-size:1rem;margin-top:4px;}}

    /* CAREER CARD */
    .career-card{{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:24px;margin-bottom:16px;}}
    .career-name{{font-family:var(--font-display);font-size:2rem;font-weight:700;color:var(--text-primary);text-transform:uppercase;letter-spacing:2px;}}
    .stat-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:16px;}}
    .stat-box{{background:var(--bg-card2);border-radius:var(--radius);padding:12px;text-align:center;}}
    .stat-value{{font-family:var(--font-display);font-size:1.8rem;font-weight:700;color:var(--accent2);}}
    .stat-label{{font-size:0.65rem;letter-spacing:1.5px;text-transform:uppercase;color:var(--text-secondary);margin-top:4px;}}

    /* SIDEBAR */
    [data-testid="stSidebar"]{{background:{t["sidebar_bg"]}!important;border-right:2px solid var(--border)!important;}}

    /* BUTTONS */
    .stButton>button{{background:var(--accent1)!important;color:white!important;border:none!important;border-radius:var(--radius)!important;font-family:var(--font-display)!important;font-weight:700!important;letter-spacing:1.5px!important;text-transform:uppercase!important;font-size:0.85rem!important;padding:10px 20px!important;transition:all 0.2s!important;}}
    .stButton>button:hover{{opacity:0.85!important;transform:translateY(-1px)!important;}}
    .stTextInput>div>div>input,.stSelectbox>div>div,.stNumberInput>div>div>input{{background:var(--bg-card2)!important;border:1px solid var(--border)!important;color:var(--text-primary)!important;border-radius:var(--radius)!important;}}
    .stTabs [data-baseweb="tab-list"]{{background:transparent!important;gap:4px!important;}}
    .stTabs [data-baseweb="tab"]{{background:var(--bg-card2)!important;color:var(--text-secondary)!important;border-radius:var(--radius) var(--radius) 0 0!important;border:1px solid var(--border)!important;font-family:var(--font-display)!important;font-weight:600!important;letter-spacing:1px!important;text-transform:uppercase!important;}}
    .stTabs [aria-selected="true"]{{background:var(--accent1)!important;color:white!important;border-color:var(--accent1)!important;}}
    [data-testid="metric-container"]{{background:var(--bg-card)!important;border:1px solid var(--border)!important;border-radius:var(--radius)!important;padding:12px!important;}}
    hr{{border-color:var(--border)!important;}}

    /* SEGNAPUNTI */
    .segnapunti-overlay{{background:var(--bg-primary);border:2px solid var(--accent1);border-radius:16px;padding:30px;margin-bottom:20px;}}
    .segnapunti-score{{font-family:var(--font-display);font-size:7rem;font-weight:900;line-height:1;text-align:center;}}
    .segnapunti-team{{font-family:var(--font-display);font-size:2rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;text-align:center;}}

    /* FIFA CARD */
    .fifa-card{{border-radius:12px;padding:16px;text-align:center;position:relative;overflow:hidden;min-height:280px;cursor:pointer;transition:transform 0.3s;}}
    .fifa-card:hover{{transform:scale(1.05) rotate(1deg);}}
    .fifa-card-bronze{{background:linear-gradient(135deg,#5C3317 0%,#CD853F 40%,#5C3317 100%);}}
    .fifa-card-silver{{background:linear-gradient(135deg,#555 0%,#C0C0C0 40%,#555 100%);}}
    .fifa-card-gold{{background:linear-gradient(135deg,#8B6914 0%,#FFD700 40%,#8B6914 100%);}}
    .fifa-card-rare-silver{{background:linear-gradient(135deg,#1C3A7A 0%,#4169E1 40%,#1C3A7A 100%);}}
    .fifa-card-rare-gold{{background:linear-gradient(135deg,#7B4F00 0%,#FFD700 40%,#B8860B 100%);}}
    .fifa-card-overall{{font-size:3rem;font-weight:900;line-height:1;font-family:var(--font-display);}}
    .fifa-card-pos{{font-size:0.7rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;}}
    .fifa-card-name{{font-size:1.1rem;font-weight:800;text-transform:uppercase;letter-spacing:1px;margin:8px 0;border-top:1px solid rgba(0,0,0,0.2);padding-top:8px;}}
    .fifa-card-stats{{display:grid;grid-template-columns:repeat(2,1fr);gap:4px;font-size:0.75rem;font-weight:700;}}
    .fifa-stat{{display:flex;justify-content:space-between;padding:2px 4px;}}

    /* TROPHIES */
    .trophy-item{{background:var(--bg-card2);border:1px solid var(--border);border-radius:var(--radius);padding:12px;text-align:center;transition:all 0.3s;}}
    .trophy-unlocked{{border-color:var(--accent-gold)!important;box-shadow:0 0 15px rgba(255,215,0,0.2)!important;background:linear-gradient(135deg,var(--bg-card2),rgba(255,215,0,0.05))!important;}}
    .trophy-locked{{opacity:0.35;filter:grayscale(100%);}}

    {t.get("extra_css", "")}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    return logo_html


def render_banner(cfg):
    """Renderizza il banner sponsor se presente."""
    if cfg.get("banner_b64") and cfg.get("banner_position") == "Sotto l'header":
        st.markdown(f"""
        <div style="text-align:center;margin:-10px 0 20px">
            <img src="data:image/png;base64,{cfg['banner_b64']}"
                style="max-width:100%;max-height:120px;object-fit:contain;border-radius:8px">
        </div>
        """, unsafe_allow_html=True)


def render_sponsors_sidebar(cfg):
    """Renderizza i loghi sponsor nella sidebar."""
    sponsors = cfg.get("sponsors", [])
    if not sponsors or not cfg.get("show_sponsors_sidebar", True):
        return
    
    st.markdown("""
    <div style="font-size:0.6rem;letter-spacing:3px;text-transform:uppercase;
        color:var(--accent1);font-weight:700;margin-bottom:8px;padding:0 2px">
        🤝 SPONSOR
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(min(len(sponsors), 2))
    for i, sp in enumerate(sponsors):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background:var(--bg-card2);border:1px solid var(--border);
                border-radius:var(--radius);padding:8px;text-align:center;margin-bottom:8px">
                <img src="data:image/png;base64,{sp['logo']}"
                    style="max-height:36px;max-width:100%;object-fit:contain">
                <div style="font-size:0.55rem;color:var(--text-secondary);margin-top:4px">{sp['nome']}</div>
            </div>
            """, unsafe_allow_html=True)



def _render_custom_scoreboard_builder(cfg):
    """Builder visuale per creare tabelloni personalizzati."""
    st.markdown("### 🛠️ Costruttore Tabellone Personalizzato")
    st.caption("Crea il tuo tabellone da zero: personalizza colori, font, dimensioni e layout degli elementi.")

    if "custom_sb" not in st.session_state:
        st.session_state.custom_sb = {
            "bg_color": "#0a0a0f",
            "team1_color": "#e8002d",
            "team2_color": "#0070f3",
            "score_color": "#ffffff",
            "score_bg": "#1a1a1a",
            "border_color": "#e8002d",
            "font_style": "Barlow Condensed",
            "score_size": 9,
            "team_size": 2.2,
            "border_radius": 12,
            "show_set": True,
            "show_battuta": True,
            "show_timer": False,
            "layout": "horizontal",
            "extra_elements": [],
        }
    sb = st.session_state.custom_sb

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🎨 Colori")
        sb["bg_color"] = st.color_picker("Sfondo tabellone", sb["bg_color"], key="csb_bg")
        sb["team1_color"] = st.color_picker("Colore Squadra 1", sb["team1_color"], key="csb_t1")
        sb["team2_color"] = st.color_picker("Colore Squadra 2", sb["team2_color"], key="csb_t2")
        sb["score_color"] = st.color_picker("Colore punteggio", sb["score_color"], key="csb_sc")
        sb["score_bg"] = st.color_picker("Sfondo punteggio", sb["score_bg"], key="csb_sbg")
        sb["border_color"] = st.color_picker("Colore bordo", sb["border_color"], key="csb_bc")

    with col2:
        st.markdown("#### 📐 Dimensioni e Font")
        sb["font_style"] = st.selectbox("Font", ["Barlow Condensed","Impact","Arial","Courier New","Georgia","Orbitron"], key="csb_font",
            index=["Barlow Condensed","Impact","Arial","Courier New","Georgia","Orbitron"].index(sb["font_style"]))
        sb["score_size"] = st.slider("Dimensione punteggio (rem)", 4, 15, sb["score_size"], key="csb_ss")
        sb["team_size"] = st.slider("Dimensione nome squadra (rem)", 1, 5, int(sb["team_size"]), key="csb_ts")
        sb["border_radius"] = st.slider("Arrotondamento bordi (px)", 0, 40, sb["border_radius"], key="csb_br")
        sb["layout"] = st.radio("Layout", ["horizontal","vertical","split"], horizontal=True, key="csb_layout")

        st.markdown("#### ➕ Elementi aggiuntivi")
        sb["show_set"] = st.checkbox("Mostra Set", sb["show_set"], key="csb_set")
        sb["show_battuta"] = st.checkbox("Mostra Battuta 🏐", sb["show_battuta"], key="csb_batt")
        sb["show_timer"] = st.checkbox("Mostra Timer ⏱️", sb["show_timer"], key="csb_timer")

    # Anteprima live
    st.markdown("#### 👁️ Anteprima Live")
    set_html = '<div style="font-size:0.8rem;margin-top:4px;opacity:0.7">SET: 1 - 0</div>' if sb["show_set"] else ""
    battuta_html = '<div style="font-size:0.9rem;margin-top:4px">🏐 In battuta</div>' if sb["show_battuta"] else ""
    timer_html = '<div style="font-size:1rem;margin-top:4px">⏱️ 00:00</div>' if sb["show_timer"] else ""

    if sb["layout"] == "split":
        preview = f"""
        <div style="background:linear-gradient(90deg,{sb['team1_color']} 50%,{sb['team2_color']} 50%);
            border:{sb['border_color']} 3px solid;border-radius:{sb['border_radius']}px;
            padding:30px;display:grid;grid-template-columns:1fr 1fr;font-family:'{sb['font_style']}',sans-serif">
            <div style="text-align:center;color:white">
                <div style="font-size:{sb['team_size']}rem;font-weight:900">TEAM A</div>
                <div style="font-size:{sb['score_size']}rem;font-weight:900;line-height:1">{'{'}score1{'}'}</div>
                {battuta_html}{set_html}
            </div>
            <div style="text-align:center;color:white">
                <div style="font-size:{sb['team_size']}rem;font-weight:900">TEAM B</div>
                <div style="font-size:{sb['score_size']}rem;font-weight:900;line-height:1">{'{'}score2{'}'}</div>
            </div>
            {timer_html}
        </div>
        """.replace("{score1}", "12").replace("{score2}", "9")
    else:
        preview = f"""
        <div style="background:{sb['bg_color']};border:3px solid {sb['border_color']};
            border-radius:{sb['border_radius']}px;padding:24px;font-family:'{sb['font_style']}',sans-serif">
            <div style="display:flex;justify-content:space-around;align-items:center">
                <div style="text-align:center">
                    <div style="font-size:{sb['team_size']}rem;font-weight:900;color:{sb['team1_color']}">TEAM A</div>
                    <div style="font-size:{sb['score_size']}rem;font-weight:900;color:{sb['score_color']};background:{sb['score_bg']};padding:10px 20px;line-height:1">12</div>
                    {battuta_html.replace('color:white','color:'+sb['team1_color'])}
                    {set_html.replace('opacity:0.7','color:'+sb['team1_color'])}
                </div>
                <div style="font-size:1.5rem;color:{sb['border_color']};opacity:0.5">VS</div>
                <div style="text-align:center">
                    <div style="font-size:{sb['team_size']}rem;font-weight:900;color:{sb['team2_color']}">TEAM B</div>
                    <div style="font-size:{sb['score_size']}rem;font-weight:900;color:{sb['score_color']};background:{sb['score_bg']};padding:10px 20px;line-height:1">9</div>
                </div>
            </div>
            {timer_html}
        </div>
        """

    st.markdown(preview, unsafe_allow_html=True)

    if st.button("✅ SALVA COME TABELLONE CUSTOM", use_container_width=True, type="primary"):
        cfg["custom_scoreboard"] = sb.copy()
        cfg["scoreboard_style"] = "Custom"
        SCOREBOARD_STYLES["Custom"] = {
            "description": "Tabellone personalizzato",
            "preview_icon": "🛠️",
            "bg": sb["bg_color"],
            "text1": sb["team1_color"],
            "text2": sb["team2_color"],
            "score_bg": sb["score_bg"],
            "score_color": sb["score_color"],
            "team_size": f"{sb['team_size']}rem",
            "score_size": f"{sb['score_size']}rem",
            "border_style": f"3px solid {sb['border_color']}",
            "extra": f"border-radius:{sb['border_radius']}px;font-family:'{sb['font_style']}',sans-serif;",
            "custom_data": sb,
        }
        save_theme_config(cfg)
        st.success("✅ Tabellone custom salvato e attivato!")
        st.rerun()


def render_personalization_page(cfg):
    """Pagina completa di personalizzazione avanzata tema."""
    st.markdown("## 🎨 Personalizzazione App")

    tabs = st.tabs(["🖼️ Tema Grafico", "🏐 Tabellone Live", "🏢 Sponsor & Banner", "📐 Layout", "👁️ Anteprima"])

    with tabs[0]:
        st.markdown("### Scegli il tuo tema")
        tema_corrente = cfg.get("theme_name", "Dynamic DAZN")
        cols = st.columns(4)
        for i, (nome, info) in enumerate(THEMES.items()):
            with cols[i % 4]:
                is_sel = (nome == tema_corrente)
                border = f"3px solid {info['accent1']}" if is_sel else "1px solid #333"
                glow = f"box-shadow:0 0 20px {info['accent1']}40;" if is_sel else ""
                st.markdown(f"""
                <div style="background:{info['bg_card']};border:{border};border-radius:12px;
                    padding:14px;margin-bottom:8px;{glow}transition:all 0.2s">
                    <div style="text-align:center;margin-bottom:6px;font-size:2rem">{info['preview_icon']}</div>
                    <div style="font-size:0.72rem;font-weight:700;color:{info['accent1']};text-align:center;
                        margin-bottom:4px;text-transform:uppercase;letter-spacing:1px">{nome}</div>
                    <div style="font-size:0.58rem;color:{info['text_secondary']};text-align:center;line-height:1.4;margin-bottom:8px">
                        {info['description']}</div>
                    <div style="display:flex;gap:4px;justify-content:center">
                        <div style="width:14px;height:14px;border-radius:50%;background:{info['accent1']}"></div>
                        <div style="width:14px;height:14px;border-radius:50%;background:{info['accent2']}"></div>
                        <div style="width:14px;height:14px;border-radius:50%;background:{info['accent_gold']}"></div>
                        <div style="width:24px;height:14px;border-radius:4px;background:{info['bg_primary']};border:1px solid #555"></div>
                    </div>
                    {"<div style='text-align:center;margin-top:6px;font-size:0.6rem;color:#00c851;font-weight:700'>✓ ATTIVO</div>" if is_sel else ""}
                </div>
                """, unsafe_allow_html=True)
                btn_label = "✓ Selezionato" if is_sel else "Seleziona"
                if st.button(btn_label, key=f"theme_btn_{nome}", use_container_width=True):
                    cfg["theme_name"] = nome
                    cfg["color_primary"] = info["accent1"]
                    cfg["color_secondary"] = info["accent2"]
                    cfg["color_detail"] = info["accent_gold"]
                    save_theme_config(cfg)
                    st.rerun()

        st.divider()
        st.markdown("### 🎨 Personalizza Colori")
        c1, c2, c3 = st.columns(3)
        with c1:
            cfg["color_primary"] = st.color_picker("🔴 Colore Primario", cfg.get("color_primary", "#e8002d"))
        with c2:
            cfg["color_secondary"] = st.color_picker("🔵 Colore Secondario", cfg.get("color_secondary", "#0070f3"))
        with c3:
            cfg["color_detail"] = st.color_picker("✨ Dettagli/Oro", cfg.get("color_detail", "#ffd700"))

        st.markdown("### 🖼️ Logo Personalizzato")
        col_l, col_r = st.columns(2)
        with col_l:
            if cfg.get("logo_b64"):
                st.markdown("**Logo attuale:**")
                st.markdown(f'<img src="data:image/png;base64,{cfg["logo_b64"]}" style="max-height:80px;border-radius:8px;border:1px solid #333">', unsafe_allow_html=True)
                if st.button("🗑️ Rimuovi Logo"):
                    cfg["logo_b64"] = None; cfg["logo_name"] = None
                    save_theme_config(cfg); st.rerun()
        with col_r:
            logo_file = st.file_uploader("Carica Logo (PNG/JPG/WebP)", type=["png","jpg","jpeg","webp"], key="logo_uploader")
            if logo_file:
                b64 = base64.b64encode(logo_file.read()).decode()
                cfg["logo_b64"] = b64; cfg["logo_name"] = logo_file.name
                st.success(f"✅ Logo '{logo_file.name}' caricato!")

    with tabs[1]:
        st.markdown("### 🏐 Scegli lo Stile del Tabellone Live")
        st.caption("Clicca sulla miniatura per selezionare il tabellone segnapunti")
        sb_corrente = cfg.get("scoreboard_style", "DAZN Live")
        cols_sb = st.columns(4)
        for i, (nome, style) in enumerate(SCOREBOARD_STYLES.items()):
            with cols_sb[i % 4]:
                is_sel = (nome == sb_corrente)
                border = "3px solid #00c851" if is_sel else "1px solid #333"
                st.markdown(f"""
                <div style="border:{border};border-radius:10px;overflow:hidden;margin-bottom:6px">
                    <div style="background:{style['bg']};padding:10px;{style['extra']}">
                        <div style="text-align:center;margin-bottom:4px">
                            <span style="font-size:0.48rem;color:{style['text1']};letter-spacing:2px;text-transform:uppercase;font-weight:700">LIVE</span>
                        </div>
                        <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:4px;align-items:center">
                            <div style="text-align:center">
                                <div style="color:{style['text1']};font-size:0.55rem;font-weight:700">TEAM A</div>
                                <div style="color:{style['score_color']};background:{style['score_bg']};font-size:1.8rem;font-weight:900;padding:4px;text-align:center">12</div>
                            </div>
                            <div style="color:{style['text2']};font-size:0.65rem;font-weight:700;text-align:center">VS</div>
                            <div style="text-align:center">
                                <div style="color:{style['text2']};font-size:0.55rem;font-weight:700">TEAM B</div>
                                <div style="color:{style['score_color']};background:{style['score_bg']};font-size:1.8rem;font-weight:900;padding:4px;text-align:center">8</div>
                            </div>
                        </div>
                    </div>
                    <div style="background:#1a1a1a;padding:6px 10px">
                        <div style="font-size:0.62rem;font-weight:700;color:{'#00c851' if is_sel else 'white'}">{style['preview_icon']} {nome}</div>
                        <div style="font-size:0.52rem;color:#888">{style['description']}</div>
                        {"<div style='font-size:0.6rem;color:#00c851;font-weight:700'>✓ ATTIVO</div>" if is_sel else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"{'✓ Attivo' if is_sel else 'Seleziona'}", key=f"sb_btn_{nome}", use_container_width=True):
                    cfg["scoreboard_style"] = nome
                    save_theme_config(cfg); st.rerun()

    with tabs[2]:
        _render_custom_scoreboard_builder(cfg)

    with tabs[3]:
        st.markdown("### 🏢 Gestione Sponsor e Banner")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("#### 📸 Banner Principale")
            if cfg.get("banner_b64"):
                st.markdown(f'<img src="data:image/png;base64,{cfg["banner_b64"]}" style="width:100%;border-radius:8px;border:1px solid #333;margin-bottom:8px">', unsafe_allow_html=True)
                if st.button("🗑️ Rimuovi Banner"):
                    cfg["banner_b64"] = None; save_theme_config(cfg); st.rerun()
            banner_file = st.file_uploader("Carica Banner (ideale 1200×200px)", type=["png","jpg","jpeg","webp"], key="banner_uploader")
            if banner_file:
                b64 = base64.b64encode(banner_file.read()).decode()
                cfg["banner_b64"] = b64; st.success("✅ Banner caricato!")
            pos_opts = ["Sopra l'header", "Sotto l'header", "Nella sidebar", "In fondo alla pagina"]
            banner_position = st.selectbox("Posizione Banner", pos_opts,
                index=pos_opts.index(cfg.get("banner_position", "Sotto l'header")))
            cfg["banner_position"] = banner_position
        with col_s2:
            st.markdown("#### 🤝 Loghi Sponsor (max 4)")
            sponsors = cfg.get("sponsors", [])
            for i, sp in enumerate(sponsors):
                col_sp, col_del = st.columns([3, 1])
                with col_sp:
                    st.markdown(f"""<div style="display:flex;align-items:center;gap:8px;background:var(--bg-card2);border-radius:8px;padding:8px;margin-bottom:4px">
                        <img src="data:image/png;base64,{sp['logo']}" style="height:28px;object-fit:contain">
                        <span style="font-size:0.8rem">{sp['nome']}</span></div>""", unsafe_allow_html=True)
                with col_del:
                    if st.button("🗑️", key=f"del_sp_{i}"):
                        sponsors.pop(i); cfg["sponsors"] = sponsors; save_theme_config(cfg); st.rerun()
            if len(sponsors) < 4:
                sp_nome = st.text_input("Nome sponsor", key="sp_nome", placeholder="es. Decathlon")
                sp_file = st.file_uploader("Logo sponsor", type=["png","jpg","jpeg","webp"], key="sp_logo")
                if st.button("➕ Aggiungi Sponsor") and sp_nome and sp_file:
                    b64 = base64.b64encode(sp_file.read()).decode()
                    sponsors.append({"nome": sp_nome, "logo": b64})
                    cfg["sponsors"] = sponsors; save_theme_config(cfg)
                    st.success(f"✅ Sponsor '{sp_nome}' aggiunto!"); st.rerun()

    with tabs[4]:
        st.markdown("### 📐 Impostazioni Layout")
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            cfg["sidebar_width"] = st.select_slider("Larghezza Sidebar", options=["stretta","normale","larga"], value=cfg.get("sidebar_width","normale"))
            cfg["card_size"] = st.select_slider("Dimensione Card", options=["compatta","normale","grande"], value=cfg.get("card_size","normale"))
            cfg["show_bottom_nav"] = st.toggle("Barra Navigazione in Basso", value=cfg.get("show_bottom_nav", True))
            cfg["show_sponsors_sidebar"] = st.toggle("Sponsor nella Sidebar", value=cfg.get("show_sponsors_sidebar", True))
        with col_l2:
            h_opts = ["Grande con gradiente","Compatto minimalista","Solo testo"]
            cfg["header_style"] = st.selectbox("Stile Header", h_opts, index=h_opts.index(cfg.get("header_style","Grande con gradiente")))
            cfg["animations"] = st.toggle("Animazioni e Transizioni", value=cfg.get("animations", True))

    with tabs[5]:
        st.markdown("### 👁️ Anteprima Completa del Tema Selezionato")
        t = get_active_theme(cfg)
        st.markdown(f"""
        <div style="background:{t['bg_primary']};border:2px solid {t['accent1']};border-radius:16px;overflow:hidden">
            <div style="background:{t['header_gradient']};padding:20px;text-align:center;border-bottom:3px solid {t['accent1']}">
                <div style="font-family:'{t['font_display']}',sans-serif;font-size:2rem;font-weight:800;color:{t['accent1']};letter-spacing:3px;text-transform:uppercase">
                    🏐 BEACH VOLLEY TOURNAMENT</div>
                <div style="color:{t['text_secondary']};font-size:0.75rem;letter-spacing:4px;margin-top:4px">TOURNAMENT MANAGER PRO</div>
            </div>
            <div style="padding:20px;display:grid;grid-template-columns:1fr 1fr;gap:16px">
                <div style="background:{t['bg_card']};border:1px solid {t['accent1']};border-radius:{t['card_radius']};overflow:hidden">
                    <div style="background:{t['bg_card2']};padding:8px 14px;font-size:0.62rem;letter-spacing:2px;text-transform:uppercase;color:{t['text_secondary']}">GIRONE A · MATCH 1</div>
                    <div style="padding:16px;display:flex;justify-content:space-between;align-items:center">
                        <div style="text-align:center;flex:1">
                            <div style="font-family:'{t['font_display']}',sans-serif;font-size:1.1rem;font-weight:700;color:{t['accent1']};text-transform:uppercase">TEAM RED</div>
                            <div style="font-size:0.65rem;color:{t['text_secondary']}">Rossi / Bianchi</div>
                        </div>
                        <div style="text-align:center;min-width:70px">
                            <div style="font-size:2rem;font-weight:800;color:white">
                                <span style="color:{t['accent1']}">2</span><span style="color:{t['text_secondary']}">–</span><span style="color:{t['accent2']}">1</span>
                            </div>
                        </div>
                        <div style="text-align:center;flex:1">
                            <div style="font-family:'{t['font_display']}',sans-serif;font-size:1.1rem;font-weight:700;color:{t['accent2']};text-transform:uppercase">TEAM BLU</div>
                        </div>
                    </div>
                </div>
                <div style="background:{t['bg_card']};border:1px solid {t['border']};border-radius:{t['card_radius']};overflow:hidden">
                    <div style="background:{t['bg_card2']};padding:8px 14px;font-size:0.62rem;letter-spacing:2px;text-transform:uppercase;color:{t['text_secondary']}">CLASSIFICA</div>
                    <div style="padding:10px;font-size:0.75rem">
                        <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid {t['border']}"><span style="color:{t['accent_gold']};font-weight:800">1. TEAM RED</span><span style="color:{t['accent_gold']};font-weight:700">9 pts</span></div>
                        <div style="display:flex;justify-content:space-between;padding:5px 0"><span style="color:{t['text_primary']}">2. TEAM BLU</span><span style="color:{t['text_secondary']}">6 pts</span></div>
                    </div>
                </div>
            </div>
            <div style="padding:10px 20px;background:{t['bg_card2']};display:flex;gap:8px;align-items:center">
                <span style="font-size:0.6rem;color:{t['text_secondary']};letter-spacing:2px">PALETTE:</span>
                {''.join([f'<div style="background:{c};width:20px;height:20px;border-radius:50%"></div>' for c in [t['accent1'],t['accent2'],t['accent_gold'],t['green'],t['bg_primary']]])}
                <span style="font-size:0.6rem;color:{t['text_secondary']};margin-left:8px">Font: {t['font_display']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    col_save, col_reset = st.columns([3, 1])
    with col_save:
        if st.button("💾 SALVA TUTTE LE IMPOSTAZIONI", use_container_width=True, type="primary"):
            save_theme_config(cfg)
            st.success("✅ Impostazioni salvate! Ricarica la pagina per le modifiche complete.")
            st.rerun()
    with col_reset:
        if st.button("🔄 Reset Default", use_container_width=True):
            default = {
                "theme_name": "Dynamic DAZN", "color_primary": "#e8002d",
                "color_secondary": "#0070f3", "color_detail": "#ffd700",
                "logo_b64": None, "logo_name": None,
                "scoreboard_style": "DAZN Live", "sponsors": [], "banner_b64": None,
                "banner_position": "Sotto l'header", "sidebar_width": "normale",
                "card_size": "normale", "show_bottom_nav": True, "show_sponsors_sidebar": True,
                "header_style": "Grande con gradiente", "animations": True, "show_weather": False,
            }
            save_theme_config(default); st.rerun()
