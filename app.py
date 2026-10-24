import os
import re
from datetime import datetime

import requests
import streamlit as st

# Set PATHFINDER_API_URL if your FastAPI backend is hosted somewhere else.
API_URL = os.getenv("PATHFINDER_API_URL", "http://localhost:8000/api/research")
REQUEST_TIMEOUT = 180

TRANSLATIONS = {
    "English": {
        "tagline": "Research to implementation",
        "headline": "Turn research into working code.",
        "intro": "Connect a research question to your repository and get an actionable plan.",
        "workspace": "WORKSPACE",
        "prompt": "What would you like to improve?",
        "prompt_help": "Describe the research idea, problem, or technique you want to apply.",
        "prompt_placeholder": "e.g. Improve retrieval accuracy using hybrid search...",
        "repo": "GitHub repository (optional for theoretical research)",
        "repo_placeholder": "https://github.com/owner/repository",
        "language": "Response language",
        "run": "Run Pathfinder",
        "running": "Pathfinder is thinking through your request…",
        "results": "Your results",
        "ready": "Ready to explore",
        "ready_desc": "Your research plan, reasoning route, and source notes will appear here.",
        "plan": "Generated plan",
        "trace": "Agent route",
        "domain": "Classified intent",
        "raw": "Fetched research notes",
        "download": "Download results",
        "clear": "Clear workspace",
        "empty_prompt": "Add a prompt before running the agent.",
        "bad_repo": "That doesn't look like a GitHub repository URL. Use https://github.com/owner/repository.",
        "connection": "Couldn't reach the FastAPI backend. Start it in a second terminal with: uvicorn main:app --reload --port 8000",
        "timeout": "The request took too long. Try again or check whether the backend/LLM is still running.",
        "success": "Analysis completed",
        "software": "Software / implementation",
        "theoretical": "Research / theory",
        "history": "Recent runs",
        "no_history": "Your recent runs will appear here.",
        "copied_hint": "Use the copy control in the code block, or download the full result below.",
        "settings": "Appearance & language",
        "theme": "Appearance",
        "dark": "Dark",
        "light": "Light",
        "repo_optional": "A repository is optional for theory-focused questions.",
        "status": "Status",
    },
    "Hindi": {
        "tagline": "रिसर्च से इम्प्लीमेंटेशन तक",
        "headline": "रिसर्च को काम करने वाले कोड में बदलें।",
        "intro": "अपने रिसर्च प्रश्न को GitHub repository से जोड़ें और उपयोगी implementation plan पाएँ।",
        "workspace": "वर्कस्पेस", "prompt": "आप क्या बेहतर करना चाहते हैं?",
        "prompt_help": "जिस समस्या या तकनीक को लागू करना है, उसका वर्णन करें।",
        "prompt_placeholder": "जैसे hybrid search से retrieval accuracy बेहतर करना...",
        "repo": "GitHub repository (ज़रूरी नहीं)", "repo_placeholder": "https://github.com/owner/repository",
        "language": "जवाब की भाषा", "run": "Pathfinder चलाएँ", "running": "Pathfinder आपके अनुरोध पर काम कर रहा है…",
        "results": "आपके परिणाम", "ready": "शुरू करने के लिए तैयार",
        "ready_desc": "आपका research plan, agent route और research notes यहाँ दिखेंगे।",
        "plan": "तैयार किया गया प्लान", "trace": "Agent route", "domain": "अनुरोध का प्रकार",
        "raw": "रिसर्च नोट्स", "download": "परिणाम डाउनलोड करें", "clear": "वर्कस्पेस साफ़ करें",
        "empty_prompt": "Agent चलाने से पहले prompt लिखें।",
        "bad_repo": "GitHub repository URL सही नहीं लग रहा। https://github.com/owner/repository इस्तेमाल करें।",
        "connection": "FastAPI backend से कनेक्ट नहीं हो पाया। दूसरे terminal में चलाएँ: uvicorn main:app --reload --port 8000",
        "timeout": "अनुरोध में बहुत समय लगा। दोबारा प्रयास करें या backend/LLM जाँचें।",
        "success": "विश्लेषण पूरा हुआ", "software": "सॉफ्टवेयर / इम्प्लीमेंटेशन",
        "theoretical": "रिसर्च / थ्योरी", "history": "हाल के रन", "no_history": "हाल के रन यहाँ दिखेंगे।",
        "copied_hint": "Code block के copy control का उपयोग करें या पूरा परिणाम डाउनलोड करें।",
        "settings": "दिखावट और भाषा", "theme": "दिखावट", "dark": "डार्क", "light": "लाइट",
        "repo_optional": "थ्योरी वाले प्रश्नों के लिए repository ज़रूरी नहीं है।", "status": "स्थिति",
    },
    "Spanish": {
        "tagline": "De la investigación a la implementación",
        "headline": "Convierte la investigación en código funcional.",
        "intro": "Conecta una pregunta de investigación con tu repositorio y obtén un plan práctico.",
        "workspace": "ESPACIO DE TRABAJO", "prompt": "¿Qué quieres mejorar?",
        "prompt_help": "Describe la idea, el problema o la técnica que quieres aplicar.",
        "prompt_placeholder": "p. ej., mejorar la recuperación con búsqueda híbrida...",
        "repo": "Repositorio de GitHub (opcional)", "repo_placeholder": "https://github.com/owner/repository",
        "language": "Idioma de respuesta", "run": "Ejecutar Pathfinder", "running": "Pathfinder está analizando tu solicitud…",
        "results": "Tus resultados", "ready": "Listo para explorar",
        "ready_desc": "Tu plan, la ruta del agente y las notas aparecerán aquí.",
        "plan": "Plan generado", "trace": "Ruta del agente", "domain": "Intención clasificada",
        "raw": "Notas de investigación", "download": "Descargar resultados", "clear": "Limpiar espacio",
        "empty_prompt": "Escribe una solicitud antes de ejecutar el agente.",
        "bad_repo": "La URL no parece un repositorio de GitHub válido.",
        "connection": "No se pudo conectar con FastAPI. Ejecuta: uvicorn main:app --reload --port 8000",
        "timeout": "La solicitud tardó demasiado. Comprueba el backend e inténtalo de nuevo.",
        "success": "Análisis completado", "software": "Software / implementación",
        "theoretical": "Investigación / teoría", "history": "Ejecuciones recientes",
        "no_history": "Tus ejecuciones recientes aparecerán aquí.", "copied_hint": "Puedes copiar desde el bloque de código o descargar el resultado.",
        "settings": "Apariencia e idioma", "theme": "Apariencia", "dark": "Oscuro", "light": "Claro",
        "repo_optional": "El repositorio es opcional para preguntas teóricas.", "status": "Estado",
    },
    "French": {
        "tagline": "De la recherche à l’implémentation",
        "headline": "Transformez la recherche en code fonctionnel.",
        "intro": "Reliez une question de recherche à votre dépôt et obtenez un plan concret.",
        "workspace": "ESPACE DE TRAVAIL", "prompt": "Que souhaitez-vous améliorer ?",
        "prompt_help": "Décrivez l’idée, le problème ou la technique à appliquer.",
        "prompt_placeholder": "ex. améliorer la recherche avec une approche hybride…",
        "repo": "Dépôt GitHub (facultatif)", "repo_placeholder": "https://github.com/owner/repository",
        "language": "Langue de réponse", "run": "Lancer Pathfinder", "running": "Pathfinder analyse votre demande…",
        "results": "Vos résultats", "ready": "Prêt à explorer",
        "ready_desc": "Le plan, le parcours de l’agent et les notes apparaîtront ici.",
        "plan": "Plan généré", "trace": "Parcours de l’agent", "domain": "Intention classée",
        "raw": "Notes de recherche", "download": "Télécharger les résultats", "clear": "Effacer l’espace",
        "empty_prompt": "Saisissez une demande avant de lancer l’agent.",
        "bad_repo": "Cette URL ne semble pas être un dépôt GitHub valide.",
        "connection": "Connexion au backend FastAPI impossible. Lancez : uvicorn main:app --reload --port 8000",
        "timeout": "La requête a pris trop de temps. Vérifiez le backend et réessayez.",
        "success": "Analyse terminée", "software": "Logiciel / implémentation",
        "theoretical": "Recherche / théorie", "history": "Exécutions récentes",
        "no_history": "Vos exécutions récentes apparaîtront ici.", "copied_hint": "Copiez depuis le bloc de code ou téléchargez le résultat.",
        "settings": "Apparence et langue", "theme": "Apparence", "dark": "Sombre", "light": "Clair",
        "repo_optional": "Le dépôt est facultatif pour les questions théoriques.", "status": "État",
    },
    "German": {
        "tagline": "Von Forschung zur Umsetzung",
        "headline": "Mache aus Forschung funktionierenden Code.",
        "intro": "Verbinde eine Forschungsfrage mit deinem Repository und erhalte einen umsetzbaren Plan.",
        "workspace": "ARBEITSBEREICH", "prompt": "Was möchtest du verbessern?",
        "prompt_help": "Beschreibe die Idee, das Problem oder die Technik.",
        "prompt_placeholder": "z. B. Retrieval mit hybrider Suche verbessern…",
        "repo": "GitHub-Repository (optional)", "repo_placeholder": "https://github.com/owner/repository",
        "language": "Antwortsprache", "run": "Pathfinder starten", "running": "Pathfinder analysiert deine Anfrage…",
        "results": "Deine Ergebnisse", "ready": "Bereit zum Erkunden",
        "ready_desc": "Plan, Agentenablauf und Forschungsnotizen erscheinen hier.",
        "plan": "Erstellter Plan", "trace": "Agentenablauf", "domain": "Erkannte Absicht",
        "raw": "Forschungsnotizen", "download": "Ergebnisse herunterladen", "clear": "Arbeitsbereich leeren",
        "empty_prompt": "Gib eine Anfrage ein, bevor du den Agenten startest.",
        "bad_repo": "Das scheint keine gültige GitHub-Repository-URL zu sein.",
        "connection": "FastAPI-Backend nicht erreichbar. Starte: uvicorn main:app --reload --port 8000",
        "timeout": "Die Anfrage dauerte zu lange. Prüfe das Backend und versuche es erneut.",
        "success": "Analyse abgeschlossen", "software": "Software / Umsetzung",
        "theoretical": "Forschung / Theorie", "history": "Letzte Durchläufe",
        "no_history": "Deine letzten Durchläufe erscheinen hier.", "copied_hint": "Nutze die Kopierfunktion im Codeblock oder lade das Ergebnis herunter.",
        "settings": "Darstellung und Sprache", "theme": "Darstellung", "dark": "Dunkel", "light": "Hell",
        "repo_optional": "Für theoretische Fragen ist kein Repository nötig.", "status": "Status",
    },
    "Mandarin Chinese": {
        "tagline": "从研究到实现",
        "headline": "将研究转化为可运行的代码。",
        "intro": "将研究问题与代码仓库关联，获取可执行的实施计划。",
        "workspace": "工作区", "prompt": "你想改进什么？",
        "prompt_help": "描述你想应用的研究思路、问题或技术。",
        "prompt_placeholder": "例如：使用混合搜索提高检索准确率……",
        "repo": "GitHub 仓库（可选）", "repo_placeholder": "https://github.com/owner/repository",
        "language": "回复语言", "run": "运行 Pathfinder", "running": "Pathfinder 正在分析你的请求……",
        "results": "分析结果", "ready": "准备开始探索",
        "ready_desc": "研究计划、智能体流程和研究笔记将在这里显示。",
        "plan": "生成的计划", "trace": "智能体流程", "domain": "请求类型",
        "raw": "研究资料", "download": "下载结果", "clear": "清空工作区",
        "empty_prompt": "请先输入问题，再运行智能体。",
        "bad_repo": "这似乎不是有效的 GitHub 仓库地址。请使用 https://github.com/owner/repository。",
        "connection": "无法连接 FastAPI 后端。请在另一个终端运行：uvicorn main:app --reload --port 8000",
        "timeout": "请求耗时过长。请检查后端或模型是否仍在运行，然后重试。",
        "success": "分析完成", "software": "软件 / 实现", "theoretical": "研究 / 理论",
        "history": "最近运行记录", "no_history": "最近的运行记录会显示在这里。",
        "copied_hint": "可以使用代码块中的复制控件，或下载完整结果。",
        "settings": "外观与语言", "theme": "外观", "dark": "深色", "light": "浅色",
        "repo_optional": "理论类问题无需提供代码仓库。", "status": "状态",
    },
    "Japanese": {
        "tagline": "研究から実装へ",
        "headline": "研究を実際に動くコードへ。",
        "intro": "研究課題をリポジトリと結び付け、実行可能な実装計画を作成します。",
        "workspace": "ワークスペース", "prompt": "何を改善したいですか？",
        "prompt_help": "適用したい研究アイデア、問題、技術について説明してください。",
        "prompt_placeholder": "例：ハイブリッド検索で検索精度を向上させる……",
        "repo": "GitHub リポジトリ（任意）", "repo_placeholder": "https://github.com/owner/repository",
        "language": "回答言語", "run": "Pathfinder を実行", "running": "Pathfinder がリクエストを分析しています……",
        "results": "分析結果", "ready": "準備完了",
        "ready_desc": "研究計画、エージェントの処理経路、研究メモがここに表示されます。",
        "plan": "生成された計画", "trace": "エージェントの処理経路", "domain": "分類された意図",
        "raw": "取得した研究メモ", "download": "結果をダウンロード", "clear": "ワークスペースをクリア",
        "empty_prompt": "エージェントを実行する前に、プロンプトを入力してください。",
        "bad_repo": "有効な GitHub リポジトリ URL ではないようです。https://github.com/owner/repository を使用してください。",
        "connection": "FastAPI バックエンドに接続できません。別のターミナルで実行してください：uvicorn main:app --reload --port 8000",
        "timeout": "リクエストがタイムアウトしました。バックエンドやモデルの状態を確認して再試行してください。",
        "success": "分析が完了しました", "software": "ソフトウェア / 実装", "theoretical": "研究 / 理論",
        "history": "最近の実行", "no_history": "最近の実行履歴がここに表示されます。",
        "copied_hint": "コードブロックのコピー機能を使うか、結果全体をダウンロードしてください。",
        "settings": "外観と言語", "theme": "外観", "dark": "ダーク", "light": "ライト",
        "repo_optional": "理論的な質問ではリポジトリは任意です。", "status": "ステータス",
    },
}

st.set_page_config(page_title="PATHFINDER 2.0", page_icon="🧭", layout="wide", initial_sidebar_state="expanded")

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"
if "language" not in st.session_state:
    st.session_state.language = "English"
if "result" not in st.session_state:
    st.session_state.result = None
if "history" not in st.session_state:
    st.session_state.history = []

lang = st.session_state.language
t = TRANSLATIONS[lang]
dark = st.session_state.theme == "Dark"

if dark:
    bg, panel, card, text, muted, border, accent = "#0D0F12", "#15181D", "#191D23", "#F3F5F7", "#A0A8B5", "#2B3038", "#25B7A8"
else:
    bg, panel, card, text, muted, border, accent = "#F5F7FA", "#FFFFFF", "#FFFFFF", "#171B23", "#657184", "#E0E5EC", "#087F78"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {{ --pf-bg:{bg}; --pf-panel:{panel}; --pf-card:{card}; --pf-text:{text}; --pf-muted:{muted}; --pf-border:{border}; --pf-accent:{accent}; }}
.stApp {{ background:var(--pf-bg); color:var(--pf-text); font-family:'DM Sans',sans-serif; }}
[data-testid="stHeader"] {{ background:transparent; }}
[data-testid="stSidebar"] {{ background:var(--pf-panel); border-right:1px solid var(--pf-border); }}
[data-testid="stSidebar"] > div {{ padding-top:1.1rem; }}
h1,h2,h3 {{ font-family:'Manrope','DM Sans',sans-serif !important; color:var(--pf-text) !important; letter-spacing:-.035em; }}
p, label, [data-testid="stMarkdownContainer"] {{ color:var(--pf-text); }}
.pf-brand {{ display:flex; align-items:center; gap:12px; margin:.2rem 0 2.2rem; }}
.pf-logo {{ width:42px;height:42px;display:flex;align-items:center;justify-content:center;background:var(--pf-accent);color:#fff;border-radius:13px;font-size:23px;box-shadow:0 7px 22px #00000018; }}
.pf-name {{ font-family:'Manrope',sans-serif;font-weight:800;font-size:1.12rem;letter-spacing:-.04em;color:var(--pf-text); }}
.pf-tag {{ font-size:.78rem;color:var(--pf-muted);margin-top:2px; }}
.pf-eyebrow {{ color:var(--pf-accent);font-size:.73rem;font-weight:700;letter-spacing:.16em;margin-bottom:.7rem; }}
.pf-hero {{ font-family:'Manrope',sans-serif;font-size:clamp(2rem,3.3vw,3.25rem);font-weight:800;line-height:1.12;letter-spacing:-.055em;color:var(--pf-text);max-width:850px;margin:0 0 1rem; }}
.pf-subtitle {{ font-size:1.02rem;line-height:1.7;color:var(--pf-muted);max-width:720px;margin-bottom:2rem; }}
.pf-card {{ background:var(--pf-card);border:1px solid var(--pf-border);border-radius:18px;padding:22px 24px;margin:0 0 16px; }}
.pf-card-title {{ font-family:'Manrope',sans-serif;font-weight:700;font-size:1rem;margin-bottom:5px;color:var(--pf-text); }}
.pf-muted {{ color:var(--pf-muted);font-size:.88rem;line-height:1.55; }}
div[data-testid="stTextArea"] textarea, div[data-testid="stTextInput"] input {{ background:var(--pf-bg)!important;color:var(--pf-text)!important;border:1px solid var(--pf-border)!important;border-radius:11px!important; }}
div[data-testid="stTextArea"] textarea:focus, div[data-testid="stTextInput"] input:focus {{ border-color:var(--pf-accent)!important;box-shadow:0 0 0 1px var(--pf-accent)!important; }}
.stButton > button[kind="primary"], .stButton > button {{ border-radius:10px;border:1px solid var(--pf-border);font-weight:600;min-height:43px;transition:all .15s ease; }}
.stButton > button[kind="primary"] {{ background:var(--pf-accent);border-color:var(--pf-accent);color:white; }}
.stButton > button:hover {{ transform:translateY(-1px);border-color:var(--pf-accent); }}
div[data-testid="stAlert"] {{ border-radius:12px; }}
hr {{ border-color:var(--pf-border)!important; }}
[data-testid="stExpander"] {{ border:1px solid var(--pf-border);border-radius:12px; }}
[data-testid="stMetric"] {{ background:var(--pf-card);padding:16px;border:1px solid var(--pf-border);border-radius:14px; }}
[data-testid="stMarkdownContainer"] code {{ border-radius:5px; }}
footer {{ visibility:hidden; }}
#MainMenu {{ visibility:hidden; }}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"""
    <div class="pf-brand">
      <div class="pf-logo">⌖</div>
      <div><div class="pf-name">PATHFINDER <span style="color:{accent}">2.0</span></div>
      <div class="pf-tag">{t['tagline']}</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"#### {t['settings']}")
    st.selectbox(t["theme"], ["Dark", "Light"], key="theme", format_func=lambda x: t["dark"] if x == "Dark" else t["light"])
    # Keep Mandarin and Japanese near the top so they are easy to find.
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
    st.markdown("---")
    st.markdown(f"#### {t['workspace']}")
    with st.form("pathfinder_form", clear_on_submit=False):
        query = st.text_area(
            t["prompt"],
            height=150,
            help=t["prompt_help"],
            placeholder=t["prompt_placeholder"],
        )
        repo_link = st.text_input(t["repo"], placeholder=t["repo_placeholder"])
        st.caption(t["repo_optional"])
        submit_btn = st.form_submit_button(t["run"], type="primary", use_container_width=True)

    if st.button(t["clear"], use_container_width=True):
        st.session_state.result = None
        st.rerun()

    st.markdown("---")
    st.caption("PATHFINDER 2.0 · Research-to-code assistant")
    st.caption("Backend: " + API_URL)

# Refresh translations after sidebar selection changes.
lang = st.session_state.language
t = TRANSLATIONS[lang]
dark = st.session_state.theme == "Dark"

st.markdown(f'<div class="pf-eyebrow">{t["workspace"]} / RESEARCH AGENT</div>', unsafe_allow_html=True)
st.markdown(f'<div class="pf-hero">{t["headline"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="pf-subtitle">{t["intro"]}</div>', unsafe_allow_html=True)

left, right = st.columns([1.55, 1], gap="large")
with left:
    st.markdown(f'<div class="pf-card"><div class="pf-card-title">{t["results"]}</div><div class="pf-muted">{t["ready_desc"]}</div></div>', unsafe_allow_html=True)
    result = st.session_state.result
    if result:
        st.success(t["success"])
        domain = result.get("domain", "N/A")
        domain_label = t["software"] if domain == "software" else t["theoretical"] if domain == "theoretical" else domain
        m1, m2 = st.columns(2)
        m1.metric(t["status"], result.get("status", "success").title())
        m2.metric(t["domain"], domain_label)
        st.markdown(f"### {t['plan']}")
        plan = result.get("plan", "")
        st.markdown(plan if plan else "_No plan was returned._")
        st.caption(t["copied_hint"])
        export = (
            f"# PATHFINDER 2.0 — Research Results\n\n"
            f"**Prompt:** {result.get('query', '')}\n\n"
            f"**Repository:** {result.get('repo_link', '') or 'Not provided'}\n\n"
            f"**Intent:** {domain_label}\n\n## {t['plan']}\n\n{plan}\n\n"
            f"## {t['raw']}\n\n{result.get('raw_markdown', '')}\n"
        )
        st.download_button(t["download"], data=export, file_name="pathfinder-results.md", mime="text/markdown", use_container_width=True)
    else:
        st.markdown(f"""
        <div style="border:1px dashed {border};border-radius:18px;min-height:300px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:35px;background:{panel};">
          <div style="font-size:2.2rem;margin-bottom:12px;">✳</div>
          <div style="font-family:Manrope,sans-serif;font-size:1.2rem;font-weight:700;color:{text};margin-bottom:8px;">{t['ready']}</div>
          <div style="font-size:.92rem;color:{muted};max-width:400px;line-height:1.6;">{t['ready_desc']}</div>
        </div>
        """, unsafe_allow_html=True)

    if result:
        with st.expander(t["raw"], expanded=False):
            st.markdown(result.get("raw_markdown", "") or "_No fetched notes returned._")

with right:
    st.markdown(f"### {t['trace']}")
    st.markdown(f'<div class="pf-muted" style="margin-bottom:14px;">How your request moved through the agent.</div>', unsafe_allow_html=True)
    steps = [
        ("01", "Intent analysis", "Classify the request as software-focused or theoretical."),
        ("02", "Research retrieval", "Collect context for the requested technique."),
        ("03", "Synthesis", "Produce an implementation plan or concept synthesis."),
    ]
    for number, title, desc in steps:
        st.markdown(f"""
        <div style="display:flex;gap:14px;padding:15px 0;border-bottom:1px solid {border};">
          <div style="flex:0 0 34px;height:34px;border:1px solid {border};border-radius:10px;display:flex;align-items:center;justify-content:center;color:{accent};font-weight:700;font-size:.8rem;">{number}</div>
          <div><div style="font-weight:700;color:{text};margin:1px 0 4px;">{title}</div>
          <div style="color:{muted};font-size:.85rem;line-height:1.5;">{desc}</div></div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown(f"### {t['history']}")
    if st.session_state.history:
        for item in reversed(st.session_state.history[-5:]):
            with st.expander(item["query"][:55] + ("…" if len(item["query"]) > 55 else "")):
                st.caption(item["time"] + " · " + item.get("domain", "unknown"))
                st.markdown(item.get("plan", ""))
    else:
        st.markdown(f'<div class="pf-muted">{t["no_history"]}</div>', unsafe_allow_html=True)

if submit_btn:
    query_clean = query.strip()
    repo_clean = repo_link.strip()
    if not query_clean:
        st.sidebar.warning(t["empty_prompt"])
    elif repo_clean and not re.match(r"^https?://(www\.)?github\.com/[^/\s]+/[^/\s#?]+/?(?:[?#].*)?$", repo_clean, re.IGNORECASE):
        st.sidebar.warning(t["bad_repo"])
    else:
        payload = {"query": query_clean, "repo_link": repo_clean, "response_language": lang}
        with st.spinner(t["running"]):
            try:
                response = requests.post(API_URL, json=payload, timeout=REQUEST_TIMEOUT)
                if response.ok:
                    data = response.json()
                    data["query"] = query_clean
                    data["repo_link"] = repo_clean
                    st.session_state.result = data
                    st.session_state.history.append({
                        "query": query_clean,
                        "time": datetime.now().strftime("%d %b %Y, %H:%M"),
                        "domain": data.get("domain", "unknown"),
                        "plan": data.get("plan", ""),
                    })
                    st.rerun()
                else:
                    try:
                        detail = response.json().get("detail", response.text)
                    except ValueError:
                        detail = response.text
                    st.error(f"API error {response.status_code}: {detail}")
            except requests.exceptions.ConnectionError:
                st.error(t["connection"])
            except requests.exceptions.Timeout:
                st.error(t["timeout"])
            except requests.exceptions.RequestException as exc:
                st.error(f"Request failed: {exc}")
