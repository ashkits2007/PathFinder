import os
import re
from datetime import datetime
import requests
import streamlit as st

# ---------------------------------------------------------
# Configuration & Backend Endpoints
# ---------------------------------------------------------
API_URL = os.getenv("PATHFINDER_API_URL", "http://localhost:8000/api/research")
LIT_API_URL = os.getenv("PATHFINDER_LIT_API_URL", "http://localhost:8000/api/literature")
REQUEST_TIMEOUT = 180

TRANSLATIONS = {
    "English": {
        "tagline": "Research to Implementation Engine",
        "headline": "Where should research take your codebase?",
        "intro": "Synthesize scientific papers, technical specs, or repositories into actionable engineering plans.",
        "workspace": "Workspace",
        "prompt": "Research Objective or Hypothesis",
        "prompt_help": "Describe the technique, paper algorithm, or system optimization you want to implement.",
        "prompt_placeholder": "e.g. Implement late-interaction ColBERT retrieval with hybrid BM25 re-ranking...",
        "repo": "Target GitHub Repository",
        "repo_placeholder": "https://github.com/owner/repository",
        "language": "Response Language",
        "run": "Synthesize Plan",
        "running": "Agent pipeline analyzing domain, retrieving literature & drafting execution plan…",
        "results": "Generated Implementation Architecture",
        "ready": "Ready to Explore",
        "ready_desc": "Configure your objective above or pick an inspiration prompt to begin.",
        "plan": "Implementation Roadmap",
        "trace": "Agent Reasoning & Routing",
        "domain": "Classified Intent",
        "raw": "Retrieved Research Notes",
        "download": "Export Report (.md)",
        "clear": "New Session",
        "empty_prompt": "Please define a research objective or question before proceeding.",
        "bad_repo": "Invalid repository format. Please provide a standard GitHub URL (e.g., https://github.com/owner/repo).",
        "connection": "Unable to connect to Pathfinder backend. Start the service at port 8000: uvicorn main:app --reload",
        "timeout": "Backend analysis timed out. The model or search index took too long to complete.",
        "success": "Synthesis Complete",
        "software": "Software Implementation",
        "theoretical": "Theoretical & Literature Research",
        "history": "Recent Sessions",
        "no_history": "No previous sessions saved.",
        "settings": "Settings & Environment",
        "theme": "Color Scheme",
        "dark": "Obsidian Dark",
        "light": "Clean Light",
        "repo_optional": "Optional for purely theoretical or literature requests.",
        "status": "Pipeline Status",
        "lit_mode": "Literature & Documents",
        "git_mode": "GitHub Codebase",
        "upload_docs": "Upload Reference Papers / Notes (PDF, PPTX, TXT)",
        "doc_link": "Direct Paper / Document URL",
        "suggestions_title": "Or get inspired by typical research-to-code workflows:",
    },
    "Hindi": {
        "tagline": "रिसर्च से इम्प्लीमेंटेशन तक",
        "headline": "रिसर्च को काम करने वाले कोड में बदलें।",
        "intro": "अपने रिसर्च प्रश्न को GitHub repository से जोड़ें और उपयोगी implementation plan पाएँ।",
        "workspace": "वर्कस्पेस",
        "prompt": "रिसर्च उद्देश्य या परिकल्पना",
        "prompt_help": "जिस समस्या या तकनीक को लागू करना है, उसका वर्णन करें।",
        "prompt_placeholder": "जैसे hybrid search से retrieval accuracy बेहतर करना...",
        "repo": "GitHub repository (ज़रूरी नहीं)",
        "repo_placeholder": "https://github.com/owner/repository",
        "language": "जवाब की भाषा",
        "run": "प्लान तैयार करें",
        "running": "Pathfinder आपके अनुरोध का विश्लेषण कर रहा है…",
        "results": "तैयार किया गया प्लान",
        "ready": "शुरू करने के लिए तैयार",
        "ready_desc": "ऊपर दिए गए फॉर्म में अपना रिसर्च प्रश्न लिखें।",
        "plan": "तैयार किया गया प्लान",
        "trace": "Agent Route & Reasoning",
        "domain": "अनुरोध का प्रकार",
        "raw": "रिसर्च नोट्स",
        "download": "रिपोर्ट डाउनलोड करें (.md)",
        "clear": "नया सत्र",
        "empty_prompt": "Agent चलाने से पहले prompt लिखें।",
        "bad_repo": "GitHub repository URL सही नहीं लग रहा।",
        "connection": "FastAPI backend से कनेक्ट नहीं हो पाया।",
        "timeout": "अनुरोध में बहुत समय लगा। दोबारा प्रयास करें।",
        "success": "विश्लेषण पूरा हुआ",
        "software": "सॉफ्टवेयर / इम्प्लीमेंटेशन",
        "theoretical": "रिसर्च / थ्योरी",
        "history": "हाल के सत्र",
        "no_history": "हाल के सत्र यहाँ दिखेंगे।",
        "settings": "सेटिंग्स",
        "theme": "थीम",
        "dark": "डार्क",
        "light": "लाइट",
        "repo_optional": "थ्योरी वाले प्रश्नों के लिए repository ज़रूरी नहीं है।",
        "status": "स्थिति",
        "lit_mode": "रिसर्च पेपर असेसमेंट",
        "git_mode": "गिटहब असेसमेंट",
        "upload_docs": "रेफरेंस डाक्यूमेंट्स अपलोड करें (PDF, PPTX, TXT)",
        "doc_link": "दस्तावेज़ लिंक (URL)",
        "suggestions_title": "या इन रिसर्च उदाहरणों में से चुनें:",
    },
    "Spanish": {
        "tagline": "De la investigación a la implementación",
        "headline": "¿Hacia dónde debería llevar la investigación a tu código?",
        "intro": "Sintetiza artículos científicos y repositorios en planes de implementación prácticos.",
        "workspace": "Espacio de trabajo",
        "prompt": "Objetivo de investigación o hipótesis",
        "prompt_help": "Describe la técnica o problema que deseas abordar.",
        "prompt_placeholder": "p. ej., Búsqueda híbrida con BM25 y embeddings densos...",
        "repo": "Repositorio GitHub",
        "repo_placeholder": "https://github.com/owner/repository",
        "language": "Idioma de respuesta",
        "run": "Sintetizar plan",
        "running": "Analizando solicitud y diseñando plan...",
        "results": "Arquitectura de implementación",
        "ready": "Listo para explorar",
        "ready_desc": "Configura tu objetivo o selecciona una sugerencia.",
        "plan": "Plan de implementación",
        "trace": "Ruta y razonamiento del agente",
        "domain": "Intención clasificada",
        "raw": "Notas de investigación",
        "download": "Descargar informe (.md)",
        "clear": "Nueva sesión",
        "empty_prompt": "Escribe una solicitud antes de continuar.",
        "bad_repo": "URL de GitHub no válida.",
        "connection": "No se pudo conectar con el backend.",
        "timeout": "Tiempo de espera agotado.",
        "success": "Análisis completado",
        "software": "Implementación de Software",
        "theoretical": "Investigación Teórica",
        "history": "Sesiones recientes",
        "no_history": "No hay sesiones previas.",
        "settings": "Ajustes",
        "theme": "Tema",
        "dark": "Oscuro",
        "light": "Claro",
        "repo_optional": "Opcional para preguntas teóricas.",
        "status": "Estado",
        "lit_mode": "Literatura y Documentos",
        "git_mode": "Repositorio GitHub",
        "upload_docs": "Subir referencias (PDF, PPTX, TXT)",
        "doc_link": "Enlace del documento (URL)",
        "suggestions_title": "O prueba una de estas ideas de investigación:",
    },
    "French": {
        "tagline": "De la recherche à l’implémentation",
        "headline": "Donnez vie à la recherche dans votre code.",
        "intro": "Transformez des articles scientifiques ou des dépôts en plans d’ingénierie prêts à l’emploi.",
        "workspace": "Espace de travail",
        "prompt": "Objectif de recherche",
        "prompt_help": "Décrivez la méthode, l'algorithme ou l'idée à appliquer.",
        "prompt_placeholder": "ex. Implémenter un reranker cross-encoder sur un index dense...",
        "repo": "Dépôt GitHub",
        "repo_placeholder": "https://github.com/owner/repository",
        "language": "Langue de réponse",
        "run": "Générer le plan",
        "running": "Synthèse et recherche en cours…",
        "results": "Plan d'implémentation",
        "ready": "Prêt pour l'exploration",
        "ready_desc": "Saisissez votre question ou utilisez une suggestion.",
        "plan": "Plan d’action",
        "trace": "Raisonnement de l’agent",
        "domain": "Intention détectée",
        "raw": "Notes et contexte",
        "download": "Exporter le rapport (.md)",
        "clear": "Nouvelle session",
        "empty_prompt": "Veuillez préciser un objectif avant de lancer l'agent.",
        "bad_repo": "URL de dépôt GitHub invalide.",
        "connection": "Impossible de contacter l'API FastAPI.",
        "timeout": "Délai d'attente dépassé.",
        "success": "Synthèse terminée",
        "software": "Implémentation logicielle",
        "theoretical": "Recherche théorique",
        "history": "Historique des sessions",
        "no_history": "Aucun historique disponible.",
        "settings": "Paramètres",
        "theme": "Thème",
        "dark": "Sombre",
        "light": "Clair",
        "repo_optional": "Optionnel pour les demandes théoriques.",
        "status": "Statut",
        "lit_mode": "Documents & Littérature",
        "git_mode": "Dépôt GitHub",
        "upload_docs": "Documents de référence (PDF, PPTX, TXT)",
        "doc_link": "Lien vers document (URL)",
        "suggestions_title": "Ou commencez par un cas d'usage courant :",
    },
    "German": {
        "tagline": "Von Forschung zur Umsetzung",
        "headline": "Verwandle Forschung in produktiven Code.",
        "intro": "Verknüpfe Paper oder Repositories mit einem praxisnahen Entwicklungsplan.",
        "workspace": "Arbeitsbereich",
        "prompt": "Forschungsziel oder Frage",
        "prompt_help": "Beschreibe die Methode, das Paper oder das Problem.",
        "prompt_placeholder": "z. B. HNSW-Vektorsuche mit Prefetching optimieren…",
        "repo": "GitHub Repository",
        "repo_placeholder": "https://github.com/owner/repository",
        "language": "Antwortsprache",
        "run": "Plan synthetisieren",
        "running": "Analysiere Anfrage und erstelle Roadmap…",
        "results": "Implementierungsplan",
        "ready": "Bereit zum Start",
        "ready_desc": "Gib oben dein Ziel ein oder wähle eine Vorlage.",
        "plan": "Fahrplan & Architektur",
        "trace": "Agenten-Routing & Trace",
        "domain": "Erkannte Absicht",
        "raw": "Recherche-Quellen",
        "download": "Bericht exportieren (.md)",
        "clear": "Neue Sitzung",
        "empty_prompt": "Bitte formuliere zuerst dein Ziel.",
        "bad_repo": "Ungültige GitHub-URL.",
        "connection": "FastAPI-Backend nicht erreichbar.",
        "timeout": "Zeitüberschreitung der Anfrage.",
        "success": "Analyse erfolgreich",
        "software": "Software-Implementierung",
        "theoretical": "Theoretische Forschung",
        "history": "Verlauf",
        "no_history": "Noch keine Sitzungen vorhanden.",
        "settings": "Einstellungen",
        "theme": "Design",
        "dark": "Dunkel",
        "light": "Hell",
        "repo_optional": "Optional für rein theoretische Themen.",
        "status": "Status",
        "lit_mode": "Literatur & Dokumente",
        "git_mode": "GitHub Repository",
        "upload_docs": "Referenzdateien (PDF, PPTX, TXT)",
        "doc_link": "Dokumenten-URL",
        "suggestions_title": "Oder wähle ein vorgeschlagenes Thema:",
    },
    "Mandarin Chinese": {
        "tagline": "从研究到工程落地",
        "headline": "将学术研究与代码仓库无缝融合",
        "intro": "快速把研究论文、前沿想法转化为详细可落地的架构与开发规划。",
        "workspace": "工作台",
        "prompt": "研究目标或技术假设",
        "prompt_help": "描述你想应用的研究论文、优化方案或算法思路。",
        "prompt_placeholder": "例如：结合 BM25 与语义向量检索并应用交叉编码重排序……",
        "repo": "GitHub 目标仓库",
        "repo_placeholder": "https://github.com/owner/repository",
        "language": "回复语言",
        "run": "生成实施方案",
        "running": "智能体正在检索学术上下文并拆解工程实施步骤……",
        "results": "系统架构规划",
        "ready": "准备就绪",
        "ready_desc": "在上方输入研究课题，或点击下方预设方案迅速开始。",
        "plan": "实施路线图",
        "trace": "思考链路 (Agent Trace)",
        "domain": "任务意图",
        "raw": "提取的研究上下文",
        "download": "导出 Markdown 报告",
        "clear": "新建会话",
        "empty_prompt": "请先输入研究目标或问题。",
        "bad_repo": "GitHub 仓库地址格式不正确。",
        "connection": "无法连接到后端 FastAPI 服务。",
        "timeout": "后端服务响应超时，请检查模型运行状态。",
        "success": "分析与规划完成",
        "software": "工程实施方案",
        "theoretical": "学术/理论研究",
        "history": "历史分析",
        "no_history": "暂无历史记录",
        "settings": "系统偏好",
        "theme": "显示主题",
        "dark": "暗色 (Obsidian)",
        "light": "明亮 (Clean)",
        "repo_optional": "纯理论研究可不填代码库。",
        "status": "执行状态",
        "lit_mode": "学术文献与文档",
        "git_mode": "GitHub 代码库评估",
        "upload_docs": "上传参考文档 (PDF, PPTX, TXT)",
        "doc_link": "文献/论文在线链接 (URL)",
        "suggestions_title": "或从以下前沿研究模板开始：",
    },
    "Japanese": {
        "tagline": "研究から本番実装へ",
        "headline": "研究の知見を、動作するコードアーキテクチャへ。",
        "intro": "最新の論文やアイデアをリポジトリと結びつけ、具体的な実装ロードマップを策定します。",
        "workspace": "ワークスペース",
        "prompt": "研究テーマ・実装目標",
        "prompt_help": "導入したい論文手法、アルゴリズム、または改善点を入力してください。",
        "prompt_placeholder": "例：ハイブリッド検索とCross-Encoderによるリランキング実装...",
        "repo": "GitHub リポジトリ",
        "repo_placeholder": "https://github.com/owner/repository",
        "language": "出力言語",
        "run": "プランを生成",
        "running": "エージェントが文献探索および実装設計を実行中…",
        "results": "設計・実装ロードマップ",
        "ready": "分析の準備完了",
        "ready_desc": "上記にリクエストを入力するか、下のテンプレートをクリックしてください。",
        "plan": "実装ロードマップ",
        "trace": "推論ルート (Agent Trace)",
        "domain": "分類された意図",
        "raw": "抽出されたリサーチノート",
        "download": "Markdown形式で書き出し",
        "clear": "新しいセッション",
        "empty_prompt": "プロンプトを入力してください。",
        "bad_repo": "有効な GitHub リポジトリURLを指定してください。",
        "connection": "FastAPIバックエンドに接続できません。",
        "timeout": "処理がタイムアウトしました。",
        "success": "計画生成完了",
        "software": "ソフトウェア実装",
        "theoretical": "理論・文献研究",
        "history": "最近のセッション",
        "no_history": "履歴はありません。",
        "settings": "設定",
        "theme": "テーマ",
        "dark": "ダーク",
        "light": "ライト",
        "repo_optional": "理論分析の場合、リポジトリは不要です。",
        "status": "ステータス",
        "lit_mode": "文献・ドキュメント評価",
        "git_mode": "GitHub リポジトリ評価",
        "upload_docs": "参考資料を添付 (PDF, PPTX, TXT)",
        "doc_link": "ドキュメント/論文URL",
        "suggestions_title": "または代表的なユースケースから選択：",
    },
}

SUGGESTED_PROMPTS = [
    {
        "title": "⚡ Hybrid RAG with ColBERT Late-Interaction",
        "desc": "Design a hybrid BM25 + dense neural search pipeline with token-level ColBERT re-ranking.",
        "mode": "git",
    },
    {
        "title": "🧠 Speculative Decoding for LLM Inference",
        "desc": "Implement speculative sampling with a draft-target model setup to cut generation latency.",
        "mode": "git",
    },
    {
        "title": "📑 Paper Review & Mathematical Core Extraction",
        "desc": "Extract core mathematical assumptions, loss formulations, and benchmarks from recent literature.",
        "mode": "lit",
    },
]

# ---------------------------------------------------------
# Page Configuration & State
# ---------------------------------------------------------
st.set_page_config(
    page_title="PATHFINDER 2.0 | AI Research to Implementation",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"
if "language" not in st.session_state:
    st.session_state.language = "English"
if "result" not in st.session_state:
    st.session_state.result = None
if "history" not in st.session_state:
    st.session_state.history = []
if "input_query" not in st.session_state:
    st.session_state.input_query = ""
if "input_repo" not in st.session_state:
    st.session_state.input_repo = ""
if "input_doc_link" not in st.session_state:
    st.session_state.input_doc_link = ""
if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = "git"

lang = st.session_state.language
t = TRANSLATIONS.get(lang, TRANSLATIONS["English"])
dark = st.session_state.theme == "Dark"

# ---------------------------------------------------------
# Gemini / ChatGPT Style Modern CSS
# ---------------------------------------------------------
if dark:
    bg = "#0B0E14"
    sidebar_bg = "#11151F"
    surface = "#161B26"
    surface_hover = "#1F2636"
    border = "#262E3D"
    text_color = "#E6EDF3"
    text_muted = "#8B949E"
    accent = "#2DD4BF"          # Emerald / Teal
    accent_glow = "rgba(45, 212, 191, 0.12)"
    badge_bg = "#1A2E2B"
    badge_color = "#5EEAD4"
    card_shadow = "0 8px 32px rgba(0, 0, 0, 0.35)"
else:
    bg = "#F8FAFC"
    sidebar_bg = "#FFFFFF"
    surface = "#FFFFFF"
    surface_hover = "#F1F5F9"
    border = "#E2E8F0"
    text_color = "#0F172A"
    text_muted = "#64748B"
    accent = "#0D9488"
    accent_glow = "rgba(13, 148, 136, 0.08)"
    badge_bg = "#E6FFFA"
    badge_color = "#0D9488"
    card_shadow = "0 4px 20px rgba(0, 0, 0, 0.05)"

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {{
    --pf-bg: {bg};
    --pf-sidebar: {sidebar_bg};
    --pf-surface: {surface};
    --pf-surface-hover: {surface_hover};
    --pf-border: {border};
    --pf-text: {text_color};
    --pf-muted: {text_muted};
    --pf-accent: {accent};
    --pf-glow: {accent_glow};
    --pf-badge-bg: {badge_bg};
    --pf-badge-color: {badge_color};
}}

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: var(--pf-bg);
    color: var(--pf-text);
}}

/* Top Streamlit bar styling */
header[data-testid="stHeader"] {{
    background: transparent !important;
}}

/* Modern Sidebar */
[data-testid="stSidebar"] {{
    background-color: var(--pf-sidebar) !important;
    border-right: 1px solid var(--pf-border) !important;
    padding-top: 1rem;
}}

/* Clean typography */
h1, h2, h3, h4 {{
    font-weight: 700 !important;
    letter-spacing: -0.025em;
    color: var(--pf-text) !important;
}}

/* Hero Section */
.hero-container {{
    padding: 2.2rem 0 1.2rem;
    max-width: 900px;
}}
.hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    background: var(--pf-badge-bg);
    color: var(--pf-badge-color);
    border-radius: 9999px;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}}
.hero-title {{
    font-size: clamp(2.0rem, 3.8vw, 3.2rem);
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -0.04em;
    margin-bottom: 0.6rem;
}}
.hero-subtitle {{
    font-size: 1.05rem;
    line-height: 1.6;
    color: var(--pf-muted);
    max-width: 740px;
}}

/* Central Card Workspace */
.workspace-card {{
    background: var(--pf-surface);
    border: 1px solid var(--pf-border);
    border-radius: 20px;
    padding: 24px;
    box-shadow: {card_shadow};
    margin-bottom: 1.5rem;
}}

/* Suggestion Chips */
.chip-container {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 12px;
    margin-top: 1rem;
}}
.chip-item {{
    background: var(--pf-surface);
    border: 1px solid var(--pf-border);
    border-radius: 14px;
    padding: 14px 16px;
    cursor: pointer;
    transition: all 0.2s ease;
}}
.chip-item:hover {{
    border-color: var(--pf-accent);
    transform: translateY(-2px);
    background: var(--pf-surface-hover);
}}
.chip-title {{
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--pf-text);
    margin-bottom: 4px;
}}
.chip-desc {{
    font-size: 0.78rem;
    color: var(--pf-muted);
    line-height: 1.4;
}}

/* Inputs Styling */
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {{
    background-color: var(--pf-bg) !important;
    color: var(--pf-text) !important;
    border: 1px solid var(--pf-border) !important;
    border-radius: 12px !important;
    padding: 12px 14px !important;
    font-family: inherit;
    transition: border-color 0.2s ease;
}}
div[data-testid="stTextArea"] textarea:focus,
div[data-testid="stTextInput"] input:focus {{
    border-color: var(--pf-accent) !important;
    box-shadow: 0 0 0 2px var(--pf-glow) !important;
}}

/* Primary & Action Buttons */
.stButton > button {{
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: all 0.18s ease-in-out !important;
    border: 1px solid var(--pf-border) !important;
}}
.stButton > button[kind="primary"] {{
    background-color: var(--pf-accent) !important;
    border-color: var(--pf-accent) !important;
    color: #0B0E14 !important;
    font-weight: 700 !important;
    padding: 0.5rem 1.4rem !important;
}}
.stButton > button[kind="primary"]:hover {{
    opacity: 0.92;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px var(--pf-glow);
}}

/* Tabs styling */
button[data-baseweb="tab"] {{
    font-weight: 600 !important;
    color: var(--pf-muted) !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
}}
button[aria-selected="true"] {{
    color: var(--pf-accent) !important;
    border-bottom-color: var(--pf-accent) !important;
}}

/* History Card */
.history-btn {{
    text-align: left;
    width: 100%;
    background: transparent;
    border: 1px solid var(--pf-border);
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 6px;
    transition: all 0.15s ease;
}}

/* Metrics & Stats */
div[data-testid="stMetric"] {{
    background: var(--pf-surface);
    border: 1px solid var(--pf-border);
    border-radius: 14px;
    padding: 14px 18px;
}}
div[data-testid="stMetricValue"] {{
    font-size: 1.25rem !important;
    color: var(--pf-accent) !important;
    font-weight: 700 !important;
}}

/* Code blocks */
code, pre {{
    font-family: 'JetBrains Mono', monospace !important;
}}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Sidebar Component (History, Language, Brand)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:12px; margin-bottom: 1.5rem; padding: 4px 2px;">
            <div style="width:38px; height:38px; background:linear-gradient(135deg, {accent}, #3B82F6); 
                        border-radius:10px; display:flex; align-items:center; justify-content:center; 
                        font-size:20px; font-weight:800; color:#0B0E14; box-shadow:0 4px 12px {accent_glow};">
                🧭
            </div>
            <div>
                <div style="font-weight:800; font-size:1.1rem; letter-spacing:-0.03em;">PATHFINDER <span style="color:{accent};">2.0</span></div>
                <div style="font-size:0.75rem; color:{text_muted};">{t['tagline']}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(f"＋ {t['clear']}", use_container_width=True):
        st.session_state.result = None
        st.session_state.input_query = ""
        st.session_state.input_repo = ""
        st.session_state.input_doc_link = ""
        st.rerun()

    st.markdown("---")

    # History List
    st.markdown(f"##### {t['history']}")
    if st.session_state.history:
        for idx, item in enumerate(reversed(st.session_state.history[-8:])):
            label = item["query"][:36] + ("…" if len(item["query"]) > 36 else "")
            domain_icon = "💻" if item.get("domain") == "software" else "📄"
            if st.button(f"{domain_icon} {label}", key=f"hist_{idx}", use_container_width=True):
                st.session_state.result = item["data"]
                st.session_state.input_query = item["query"]
                st.rerun()
    else:
        st.caption(t["no_history"])

    st.markdown("---")

    # Settings Section
    with st.expander(f"⚙️ {t['settings']}", expanded=False):
        st.selectbox(
            t["theme"],
            ["Dark", "Light"],
            key="theme",
            format_func=lambda x: t["dark"] if x == "Dark" else t["light"],
        )

        language_options = [
            "English",
            "Mandarin Chinese",
            "Japanese",
            "Hindi",
            "Spanish",
            "French",
            "German",
        ]
        st.selectbox(t["language"], language_options, key="language")

        st.caption(f"**Research API:** `{API_URL}`")
        st.caption(f"**Literature API:** `{LIT_API_URL}`")

    st.caption("PATHFINDER 2.0 • Autonomous Research-to-Code Framework")

# ---------------------------------------------------------
# Hero Banner
# ---------------------------------------------------------
st.markdown(
    f"""
    <div class="hero-container">
        <div class="hero-badge">⚡ {t['workspace']}</div>
        <div class="hero-title">{t['headline']}</div>
        <div class="hero-subtitle">{t['intro']}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Interactive Prompt Suggestions (Gemini style)
# ---------------------------------------------------------
if not st.session_state.result:
    st.markdown(f"<p style='font-size:0.85rem; color:{text_muted}; font-weight:600;'>{t['suggestions_title']}</p>", unsafe_allow_html=True)
    cols = st.columns(len(SUGGESTED_PROMPTS))
    for i, s in enumerate(SUGGESTED_PROMPTS):
        with cols[i]:
            if st.button(f"{s['title']}\n\n{s['desc']}", key=f"sug_{i}", use_container_width=True):
                st.session_state.input_query = s["desc"]
                st.session_state.selected_mode = s["mode"]
                st.rerun()

# ---------------------------------------------------------
# Main Input Workspace (Unified Tabbed Panel)
# ---------------------------------------------------------
st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

mode_label = st.radio(
    "Assessment Mode",
    options=[t["git_mode"], t["lit_mode"]],
    index=0 if st.session_state.selected_mode == "git" else 1,
    horizontal=True,
    label_visibility="collapsed",
)

is_git_mode = mode_label == t["git_mode"]

with st.container():
    st.markdown(f'<div class="workspace-card">', unsafe_allow_html=True)

    query_input = st.text_area(
        label=t["prompt"],
        value=st.session_state.input_query,
        placeholder=t["prompt_placeholder"],
        help=t["prompt_help"],
        height=110,
    )

    uploaded_files = []
    doc_link_val = ""
    repo_link_val = ""

    if is_git_mode:
        c1, c2 = st.columns([2.5, 1])
        with c1:
            repo_link_val = st.text_input(
                t["repo"],
                value=st.session_state.input_repo,
                placeholder=t["repo_placeholder"],
                help=t["repo_optional"],
            )
        with c2:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            submit_action = st.button(f"🚀 {t['run']}", type="primary", use_container_width=True)
    else:
        c1, c2 = st.columns([1.5, 1])
        with c1:
            uploaded_files = st.file_uploader(
                t["upload_docs"],
                accept_multiple_files=True,
                type=["pdf", "txt", "pptx"],
            )
        with c2:
            doc_link_val = st.text_input(
                t["doc_link"],
                value=st.session_state.input_doc_link,
                placeholder="https://arxiv.org/abs/...",
            )
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            submit_action = st.button(f"🚀 {t['run']}", type="primary", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Action & Execution Logic
# ---------------------------------------------------------
if submit_action:
    query_clean = query_input.strip()
    repo_clean = repo_link_val.strip() if is_git_mode else ""
    link_clean = doc_link_val.strip() if not is_git_mode else ""

    if not query_clean:
        st.warning(t["empty_prompt"])
    elif is_git_mode and repo_clean and not re.match(r"^https?://(www\.)?github\.com/[^/\s]+/[^/\s#?]+/?(?:[?#].*)?$", repo_clean, re.IGNORECASE):
        st.warning(t["bad_repo"])
    else:
        with st.status(t["running"], expanded=True) as status_box:
            st.write("🔍 Classifying request domain and requirements...")
            try:
                if is_git_mode:
                    payload = {
                        "query": query_clean,
                        "repo_link": repo_clean,
                        "response_language": lang,
                    }
                    st.write("🌐 Querying agent graph & repository analyzer...")
                    response = requests.post(API_URL, json=payload, timeout=REQUEST_TIMEOUT)
                else:
                    st.write("📚 Parsing document payloads and reference attachments...")
                    files_payload = []
                    if uploaded_files:
                        for file in uploaded_files:
                            files_payload.append(("files", (file.name, file.getvalue(), file.type)))

                    data_payload = {
                        "query": query_clean,
                        "response_language": lang,
                        "doc_link": link_clean,
                    }

                    if files_payload:
                        response = requests.post(LIT_API_URL, files=files_payload, data=data_payload, timeout=REQUEST_TIMEOUT)
                    else:
                        response = requests.post(LIT_API_URL, data=data_payload, timeout=REQUEST_TIMEOUT)

                if response.ok:
                    data = response.json()
                    data["query"] = query_clean
                    data["repo_link"] = repo_clean if is_git_mode else link_clean

                    if not is_git_mode:
                        parsed_items = []
                        if uploaded_files:
                            parsed_items.extend([f.name for f in uploaded_files])
                        if link_clean:
                            parsed_items.append(link_clean)
                        data["parsed_files"] = parsed_items

                    status_box.update(label=t["success"], state="complete", expanded=False)

                    st.session_state.result = data
                    st.session_state.history.append({
                        "query": query_clean,
                        "time": datetime.now().strftime("%d %b, %H:%M"),
                        "domain": data.get("domain", "unknown"),
                        "data": data,
                    })
                    st.rerun()
                else:
                    try:
                        detail = response.json().get("detail", response.text)
                    except ValueError:
                        detail = response.text
                    status_box.update(label="Analysis Failed", state="error")
                    st.error(f"Error {response.status_code}: {detail}")
            except requests.exceptions.ConnectionError:
                status_box.update(label="Connection Error", state="error")
                st.error(t["connection"])
            except requests.exceptions.Timeout:
                status_box.update(label="Timeout Exceeded", state="error")
                st.error(t["timeout"])
            except requests.exceptions.RequestException as exc:
                status_box.update(label="Unexpected Error", state="error")
                st.error(f"Network request failed: {exc}")

# ---------------------------------------------------------
# Results Presentation (Tabbed Architecture)
# ---------------------------------------------------------
res = st.session_state.result

if res:
    st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)

    # Top summary ribbon
    domain = res.get("domain", "theoretical")
    domain_label = t["software"] if domain == "software" else t["theoretical"]

    col_meta1, col_meta2, col_meta3 = st.columns([2, 1, 1])
    with col_meta1:
        st.markdown(f"#### 🎯 {res.get('query')}")
        if res.get("repo_link"):
            st.caption(f"Source / Context: `{res.get('repo_link')}`")
    with col_meta2:
        st.metric(t["domain"], domain_label)
    with col_meta3:
        st.metric(t["status"], res.get("status", "Active").title())

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    tab_plan, tab_notes, tab_trace, tab_sources = st.tabs([
        f"📋 {t['plan']}",
        f"📑 {t['raw']}",
        f"🧭 {t['trace']}",
        "📁 Source Files",
    ])

    with tab_plan:
        plan_content = res.get("plan", "")
        if plan_content:
            st.markdown(plan_content)
        else:
            st.info("No synthesis roadmap returned by model.")

        st.markdown("---")
        # Export Actions
        export_md = (
            f"# PATHFINDER 2.0 — Research Synthesis Report\n\n"
            f"- **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"- **Query:** {res.get('query', '')}\n"
            f"- **Target Domain:** {domain_label}\n"
            f"- **Repository/Source:** {res.get('repo_link', 'None Provided')}\n\n"
            f"---\n\n"
            f"## {t['plan']}\n\n{plan_content}\n\n"
            f"---\n\n"
            f"## {t['raw']}\n\n{res.get('raw_markdown', 'No context notes attached.')}\n"
        )
        col_dl, _ = st.columns([1, 3])
        with col_dl:
            st.download_button(
                f"📥 {t['download']}",
                data=export_md,
                file_name=f"pathfinder-plan-{datetime.now().strftime('%Y%m%d-%H%M')}.md",
                mime="text/markdown",
                use_container_width=True,
            )

    with tab_notes:
        raw_notes = res.get("raw_markdown", "")
        if raw_notes:
            st.markdown(raw_notes)
        else:
            st.caption("No auxiliary research notes were retrieved for this query.")

    with tab_trace:
        st.markdown(
            f"""
            <div style="background:var(--pf-surface); border:1px solid var(--pf-border); border-radius:14px; padding:18px;">
                <div style="display:flex; gap:16px; align-items:flex-start; margin-bottom:14px;">
                    <span style="background:{badge_bg}; color:{badge_color}; border-radius:50%; width:28px; height:28px; display:inline-flex; align-items:center; justify-content:center; font-weight:700;">1</span>
                    <div>
                        <strong>Intent & Domain Classification</strong>
                        <div style="color:{text_muted}; font-size:0.86rem;">Request classified as <code>{domain}</code> based on semantic tokens and engineering requirements.</div>
                    </div>
                </div>
                <div style="display:flex; gap:16px; align-items:flex-start; margin-bottom:14px;">
                    <span style="background:{badge_bg}; color:{badge_color}; border-radius:50%; width:28px; height:28px; display:inline-flex; align-items:center; justify-content:center; font-weight:700;">2</span>
                    <div>
                        <strong>Context Retrieval & Graph Traversal</strong>
                        <div style="color:{text_muted}; font-size:0.86rem;">Extracted structural repo context and literature notes for synthesis.</div>
                    </div>
                </div>
                <div style="display:flex; gap:16px; align-items:flex-start;">
                    <span style="background:{badge_bg}; color:{badge_color}; border-radius:50%; width:28px; height:28px; display:inline-flex; align-items:center; justify-content:center; font-weight:700;">3</span>
                    <div>
                        <strong>Engineering Roadmap Synthesis</strong>
                        <div style="color:{text_muted}; font-size:0.86rem;">Generated technical architecture, implementation phases, and code stubs.</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tab_sources:
        parsed_files = res.get("parsed_files", [])
        if parsed_files:
            st.markdown("##### Referenced Literature & Attachments:")
            for p in parsed_files:
                st.markdown(f"- 📄 `{p}`")
        else:
            st.caption("No dedicated documents or uploaded files were linked to this session.")
