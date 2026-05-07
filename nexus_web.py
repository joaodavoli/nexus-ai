"""NEXUS — CEO AI Assistant"""

import streamlit as st
import anthropic
import json, os, hashlib, uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
try:
    from duckduckgo_search import DDGS
    WEB_SEARCH_OK = True
except:
    WEB_SEARCH_OK = False

# ─── Dados ─────────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "nexus_data"
USERS_FILE = DATA_DIR / "users.json"
try: DATA_DIR.mkdir(exist_ok=True)
except: pass

def hash_senha(s): return hashlib.sha256(s.encode()).hexdigest()

def carregar_usuarios():
    try:
        if USERS_FILE.exists():
            with open(USERS_FILE,"r",encoding="utf-8") as f: return json.load(f)
    except: pass
    return {}

def salvar_usuarios(u):
    try:
        with open(USERS_FILE,"w",encoding="utf-8") as f: json.dump(u,f,ensure_ascii=False,indent=2)
    except: pass

def criar_usuario(nome, email, senha):
    users = carregar_usuarios()
    email = email.lower().strip()
    if email in users: return False,"E-mail já cadastrado."
    if len(senha)<6: return False,"Senha mínimo 6 caracteres."
    if not nome.strip(): return False,"Nome obrigatório."
    users[email] = {"id":str(uuid.uuid4()),"nome":nome.strip(),"email":email,
                    "senha":hash_senha(senha),"criado_em":datetime.now().isoformat(),
                    "configuracoes":{"max_tokens":8192}}
    salvar_usuarios(users)
    return True,"Conta criada!"

def login_usuario(email, senha):
    users = carregar_usuarios()
    email = email.lower().strip()
    if email not in users: return False,"E-mail não encontrado.",{}
    if users[email]["senha"] != hash_senha(senha): return False,"Senha incorreta.",{}
    return True,"OK",users[email]

def atualizar_usuario(email, dados):
    users = carregar_usuarios()
    if email in users:
        for k,v in dados.items(): users[email][k]=v
        salvar_usuarios(users)

def saudacao():
    h = datetime.now(tz=ZoneInfo("America/Sao_Paulo")).hour
    if h < 12: return "Bom dia"
    elif h < 18: return "Boa tarde"
    else: return "Boa noite"

# ─── Configuração ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="NEXUS", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

# ─── Tema ──────────────────────────────────────────────────────────────────────
def get_tema():
    return st.session_state.get("dark_mode", False)

def apply_css():
    dark = get_tema()
    bg        = "#0c0c0c" if dark else "#ffffff"
    sidebar   = "#111111" if dark else "#f5f5f5"
    txt       = "#dddddd" if dark else "#111111"
    txt2      = "#666666" if dark else "#888888"
    brd       = "#1e1e1e" if dark else "#e5e5e5"
    inp       = "#181818" if dark else "#f9f9f9"
    btn       = "#1a1a1a" if dark else "#ffffff"
    btn_txt   = "#888888" if dark else "#555555"
    code_bg   = "#1a1a1a" if dark else "#f3f4f6"
    code_c    = "#7dd3fc" if dark else "#1d4ed8"

    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
html, body, .stApp, [data-testid="stAppViewContainer"] {{
    background-color: {bg} !important;
    font-family: 'Inter', sans-serif !important;
}}
/* ── TEXTO ── */
body, p, span, div, label, h1, h2, h3, h4, h5, h6, li, td, th,
.stMarkdown, .stMarkdown *, [data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] *, [data-testid="stText"],
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *,
.stTextInput label, .stSelectbox label, .stTextArea label {{
    color: {txt} !important;
    font-family: 'Inter', sans-serif !important;
}}
/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {{
    background-color: {sidebar} !important;
    border-right: 1px solid {brd} !important;
    min-width: 260px !important; max-width: 260px !important;
    width: 260px !important; display: block !important;
    transform: none !important; transition: none !important;
}}
section[data-testid="stSidebar"] * {{ color: {txt} !important; }}
button[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {{ display: none !important; }}
/* ── INPUTS ── */
input, textarea,
.stTextInput input, .stTextArea textarea,
[data-testid="stChatInput"] textarea {{
    background-color: {inp} !important;
    color: {txt} !important;
    border: 1px solid {brd} !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}}
input::placeholder, textarea::placeholder {{ color: {txt2} !important; }}
/* ── CHAT INPUT AREA ── */
[data-testid="stChatInput"] > div {{
    background-color: {inp} !important;
    border: 1px solid {brd} !important;
    border-radius: 12px !important;
}}
.stChatFloatingInputContainer, [data-testid="stChatInputContainer"],
.stBottom, .stBottom > div {{
    background-color: {bg} !important;
}}
/* ── BOTÕES ── */
.stButton > button {{
    background: {btn} !important; border: 1px solid {brd} !important;
    color: {btn_txt} !important; border-radius: 8px !important;
    font-size: 0.8rem !important; padding: 8px 12px !important;
    transition: all 0.15s !important;
}}
.stButton > button:hover {{ color: {txt} !important; border-color: {txt2} !important; }}
.primary-btn > button {{ background: {txt} !important; color: {bg} !important; border: none !important; font-weight: 500 !important; }}
.danger-btn > button {{ color: #ef4444 !important; border-color: #fca5a5 !important; }}
/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {{ background: transparent !important; }}
[data-testid="stChatMessage"] * {{ color: {txt} !important; }}
/* ── CÓDIGO E TABELAS ── */
code {{ background: {code_bg} !important; color: {code_c} !important; border-radius: 4px !important; padding: 2px 6px !important; }}
pre {{ background: {code_bg} !important; border: 1px solid {brd} !important; border-radius: 8px !important; padding: 14px !important; }}
th {{ background: {code_bg} !important; border: 1px solid {brd} !important; padding: 8px 12px !important; }}
td {{ border: 1px solid {brd} !important; padding: 7px 12px !important; color: {txt} !important; }}
/* ── TABS E SELECT ── */
[data-baseweb="tab-list"] {{ background: {sidebar} !important; border-bottom: 1px solid {brd} !important; }}
[data-baseweb="tab"] {{ color: {txt2} !important; }}
[data-baseweb="tab"][aria-selected="true"] {{ color: {txt} !important; border-bottom: 2px solid {txt} !important; }}
[data-baseweb="select"] div {{ background: {inp} !important; color: {txt} !important; border-color: {brd} !important; }}
/* ── LAYOUT ── */
.chat-header {{ text-align: center; padding: 60px 20px 36px; }}
.chat-header h1 {{ font-size: 1.9rem; font-weight: 500; color: {txt} !important; }}
.chat-header p {{ color: {txt2} !important; font-size: 0.82rem; }}
.divider {{ border-top: 1px solid {brd}; margin: 12px 0; }}
.section-label {{ font-size: 0.65rem; color: {txt2} !important; text-transform: uppercase; letter-spacing: 0.1em; margin: 12px 0 6px; }}
.history-card {{ background: {btn}; border: 1px solid {brd}; border-radius: 8px; padding: 8px 10px; margin-bottom: 4px; }}
.history-title {{ font-size: 0.78rem; color: {txt} !important; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.user-badge {{ background: {inp}; border: 1px solid {brd}; border-radius: 8px; padding: 8px 10px; margin-bottom: 12px; }}
.settings-box {{ background: {sidebar}; border: 1px solid {brd}; border-radius: 10px; padding: 18px; margin-bottom: 14px; }}
.auth-wrap {{ background: {bg}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
</style>""", unsafe_allow_html=True)

# ─── API Key ───────────────────────────────────────────────────────────────────
def get_api_key():
    try: return st.secrets["ANTHROPIC_API_KEY"]
    except: return os.environ.get("ANTHROPIC_API_KEY","")

# ─── Prompt ────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Você é NEXUS — assistente executivo de IA para CEOs e líderes empresariais.

Identidade: conselheiro estratégico sênior, direto, orientado a dados. Fala em português do Brasil.

Especialidades: estratégia (OKRs, SWOT, BCG), finanças (DRE, valuation, unit economics), investimentos (renda fixa, ações, FIIs, cripto, VC), RH, marketing/vendas, tecnologia, regulação brasileira.

REGRAS DE BUSCA — NUNCA IGNORE:
1. Se o usuário mencionar QUALQUER nome de empresa (ex: "Menrad", "Ambev", "minha empresa X"): chame buscar_web IMEDIATAMENTE com o nome da empresa. NÃO pergunte o que é a empresa. NÃO peça mais informações. PESQUISE primeiro, responda depois.
2. Para notícias, cotações, preços, tendências ou dados atuais: use buscar_web antes de responder.
3. Se a busca retornar erro ou resultado vazio: use seu conhecimento interno e informe que os dados podem não ser os mais recentes. NUNCA peça ao usuário para descrever a empresa.
4. PROIBIDO perguntar "o que é essa empresa?" ou "pode me dar mais detalhes sobre a empresa?". Pesquise e descubra sozinho.

Formato: resposta direta, tabelas para comparações, finalize com PRÓXIMOS PASSOS numerados."""

# ─── Ferramentas ───────────────────────────────────────────────────────────────
TOOLS = [
    {"name":"buscar_web","description":"Pesquisa qualquer empresa, notícia, cotação ou dado em tempo real na internet.","input_schema":{"type":"object","properties":{"query":{"type":"string"},"max_results":{"type":"integer"}},"required":["query"]}},
    {"name":"calcular_metricas_financeiras","description":"Calcula LTV/CAC, EBITDA, valuation, ROI, burn rate, break-even.","input_schema":{"type":"object","properties":{"tipo_calculo":{"type":"string","enum":["ltv_cac","ebitda","valuation_multiplos","roi","break_even","burn_rate"]},"dados":{"type":"object"}},"required":["tipo_calculo","dados"]}},
    {"name":"analisar_mercado","description":"Análise de mercado: tendências, competidores, oportunidades por setor.","input_schema":{"type":"object","properties":{"setor":{"type":"string"},"foco":{"type":"string","enum":["competidores","tendencias","oportunidades","riscos","tam_sam_som","completo"]},"regiao":{"type":"string"}},"required":["setor","foco"]}},
    {"name":"analisar_investimentos","description":"Análise de investimentos: renda fixa, ações, FIIs, cripto, VC.","input_schema":{"type":"object","properties":{"tipo_analise":{"type":"string","enum":["renda_fixa","renda_variavel","fundos","cripto","venture_capital","comparativo_carteira"]},"perfil_risco":{"type":"string","enum":["conservador","moderado","arrojado","agressivo"]},"valor_disponivel":{"type":"number"},"prazo_meses":{"type":"integer"}},"required":["tipo_analise","perfil_risco"]}},
    {"name":"gerar_framework_estrategico","description":"Frameworks: SWOT, OKR, Canvas, Porter, Ansoff, BCG.","input_schema":{"type":"object","properties":{"framework":{"type":"string","enum":["swot","okr","business_canvas","porters_five_forces","ansoff","bcg_matrix"]},"empresa_contexto":{"type":"string"},"objetivo":{"type":"string"}},"required":["framework","empresa_contexto"]}},
    {"name":"criar_plano_acao","description":"Plano de ação faseado com KPIs.","input_schema":{"type":"object","properties":{"objetivo":{"type":"string"},"prazo_meses":{"type":"integer"},"tipo_empresa":{"type":"string"}},"required":["objetivo","prazo_meses"]}},
    {"name":"projecao_financeira","description":"Projeções: DRE, crescimento, cenários.","input_schema":{"type":"object","properties":{"tipo_projecao":{"type":"string","enum":["dre_simplificada","crescimento_receita","cenarios_pessimista_otimista"]},"dados_atuais":{"type":"object"},"horizonte_meses":{"type":"integer"}},"required":["tipo_projecao","dados_atuais","horizonte_meses"]}},
    {"name":"benchmark_setor","description":"Benchmarks por setor e porte.","input_schema":{"type":"object","properties":{"setor":{"type":"string"},"metrica":{"type":"string"},"porte":{"type":"string","enum":["startup","pme","mid_market","enterprise"]}},"required":["setor","metrica"]}},
]

# ─── Implementações ────────────────────────────────────────────────────────────
def buscar_web(query, max_results=6):
    if not WEB_SEARCH_OK:
        return {"status":"busca_indisponivel","instrucao":"Use seu conhecimento interno sobre o assunto pesquisado e informe que os dados podem não ser os mais recentes. NÃO peça ao usuário para descrever a empresa.","query":query}
    try:
        with DDGS() as d:
            r = list(d.text(query, max_results=max_results))
        if not r:
            return {"status":"sem_resultados","instrucao":"Use seu conhecimento interno. NÃO peça ao usuário para descrever a empresa.","query":query}
        return [{"titulo":x.get("title",""),"resumo":x.get("body",""),"url":x.get("href","")} for x in r]
    except Exception as e:
        return {"status":"erro","instrucao":"Use seu conhecimento interno. NÃO peça ao usuário para descrever a empresa.","query":query,"detalhe":str(e)}

def calcular_metricas(tipo, dados):
    if tipo=="ltv_cac":
        r=dados.get("receita_media_mensal",0); ch=dados.get("churn_mensal_pct",1)/100
        m=dados.get("margem_bruta_pct",70)/100; cac=dados.get("cac",0)
        ltv=(r*m)/ch if ch>0 else 0; ratio=ltv/cac if cac>0 else 0
        return {"LTV":f"R${ltv:,.2f}","CAC":f"R${cac:,.2f}","Ratio":f"{ratio:.1f}x","Status":"✅ Saudável" if ratio>=3 else "⚠️ Atenção" if ratio>=1 else "🚨 Crítico"}
    elif tipo=="burn_rate":
        d=dados.get("despesas_mensais",0); r=dados.get("receita_mensal",0); c=dados.get("caixa_disponivel",0)
        burn=d-r; rw=c/burn if burn>0 else float('inf')
        return {"Burn":f"R${burn:,.2f}/mês","Runway":f"{rw:.1f} meses" if rw!=float('inf') else "Positivo ✅","Alerta":"🚨 URGENTE" if rw<6 else "✅ OK"}
    elif tipo=="roi":
        inv=dados.get("investimento",0); ret=dados.get("retorno_esperado",0)
        roi=((ret-inv)/inv*100) if inv>0 else 0
        return {"ROI":f"{roi:.1f}%","Lucro":f"R${ret-inv:,.2f}"}
    elif tipo=="valuation_multiplos":
        rec=dados.get("receita_anual",0); mr=dados.get("multiplo_receita",5)
        return {"Valuation":f"R${rec*mr:,.2f} ({mr}x receita)"}
    elif tipo=="break_even":
        cf=dados.get("custos_fixos_mensais",0); mc=dados.get("margem_contribuicao_pct",0)/100
        return {"Break_Even":f"R${cf/mc:,.2f}/mês" if mc>0 else "N/A"}
    return dados

def executar_ferramenta(nome, inputs):
    mapa = {
        "buscar_web": lambda i: buscar_web(i["query"], i.get("max_results",6)),
        "calcular_metricas_financeiras": lambda i: calcular_metricas(i["tipo_calculo"],i["dados"]),
        "analisar_mercado": lambda i: {"setor":i["setor"],"foco":i["foco"],"regiao":i.get("regiao","Brasil"),"tendencias":["Digitalização","IA","ESG"],"nota":"Use buscar_web para dados em tempo real"},
        "analisar_investimentos": lambda i: {"tipo":i["tipo_analise"],"perfil":i["perfil_risco"],"Selic":"10,50%","CDI":"10,40%","aviso":"⚠️ Consulte assessor certificado"},
        "gerar_framework_estrategico": lambda i: {"framework":i["framework"].upper(),"contexto":i["empresa_contexto"]},
        "criar_plano_acao": lambda i: {"objetivo":i["objetivo"],"prazo":f"{i['prazo_meses']} meses","fases":["Diagnóstico","Execução","Escala","Consolidação"]},
        "projecao_financeira": lambda i: {"tipo":i["tipo_projecao"],"horizonte":f"{i['horizonte_meses']} meses"},
        "benchmark_setor": lambda i: {"setor":i["setor"],"metrica":i["metrica"],"porte":i.get("porte","pme")},
    }
    fn = mapa.get(nome)
    return fn(inputs) if fn else {"erro":f"'{nome}' não encontrada"}

# ─── Processar Resposta ────────────────────────────────────────────────────────
def processar_resposta(prompt):
    api_key = get_api_key()
    if not api_key:
        return "⚠️ Configure a ANTHROPIC_API_KEY nas Secrets do Streamlit Cloud."
    client = anthropic.Anthropic(api_key=api_key)
    st.session_state.historico.append({"role":"user","content":prompt})
    resposta_final = ""
    with st.spinner(""):
        while True:
            with client.messages.stream(
                model="claude-sonnet-4-6", max_tokens=8192,
                system=[{"type":"text","text":SYSTEM_PROMPT,"cache_control":{"type":"ephemeral"}}],
                tools=TOOLS, messages=st.session_state.historico
            ) as s:
                response = s.get_final_message()
            if response.stop_reason == "tool_use":
                resultados = []
                for b in response.content:
                    if b.type == "tool_use":
                        r = executar_ferramenta(b.name, b.input)
                        resultados.append({"type":"tool_result","tool_use_id":b.id,"content":json.dumps(r,ensure_ascii=False)})
                st.session_state.historico.append({"role":"assistant","content":response.content})
                st.session_state.historico.append({"role":"user","content":resultados})
            else:
                for b in response.content:
                    if hasattr(b,"text"): resposta_final += b.text
                st.session_state.historico.append({"role":"assistant","content":response.content})
                break
    return resposta_final

# ─── Session State ─────────────────────────────────────────────────────────────
def init():
    for k,v in {"messages":[],"historico":[],"conv_id":0,"conversas":[],
                "logged_in":False,"user":None,"page":"chat","dark_mode":False}.items():
        if k not in st.session_state: st.session_state[k] = v

def nova_conversa():
    if st.session_state.messages:
        titulo = next((m["content"][:40] for m in st.session_state.messages if m["role"]=="user"),"Conversa")
        st.session_state.conversas.insert(0,{"id":st.session_state.conv_id,"titulo":titulo,"messages":st.session_state.messages.copy()})
        if len(st.session_state.conversas)>30: st.session_state.conversas=st.session_state.conversas[:30]
    st.session_state.messages = []
    st.session_state.historico = []
    st.session_state.conv_id += 1

# ─── Tela de Login ─────────────────────────────────────────────────────────────
def tela_auth():
    _,col,_ = st.columns([1,1.2,1])
    with col:
        dark = get_tema()
        st.markdown(f'<div style="text-align:center;font-size:1.6rem;font-weight:600;color:{"#ddd" if dark else "#111"};margin-bottom:4px;letter-spacing:0.1em;">◈ NEXUS</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center;font-size:0.75rem;color:#888;margin-bottom:24px;text-transform:uppercase;letter-spacing:0.08em;">CEO AI Assistant</div>', unsafe_allow_html=True)
        tab1,tab2 = st.tabs(["Entrar","Criar conta"])
        with tab1:
            with st.form("login"):
                email = st.text_input("E-mail", placeholder="seu@email.com")
                senha = st.text_input("Senha", type="password", placeholder="••••••••")
                if st.form_submit_button("Entrar", use_container_width=True):
                    ok,msg,user = login_usuario(email,senha)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.rerun()
                    else: st.error(msg)
        with tab2:
            with st.form("register"):
                nome = st.text_input("Nome completo", placeholder="João Silva")
                email_r = st.text_input("E-mail", placeholder="seu@email.com")
                senha_r = st.text_input("Senha", type="password", placeholder="Mínimo 6 caracteres")
                senha_r2 = st.text_input("Confirmar senha", type="password", placeholder="••••••••")
                if st.form_submit_button("Criar conta", use_container_width=True):
                    if senha_r != senha_r2: st.error("Senhas não coincidem.")
                    else:
                        ok,msg = criar_usuario(nome,email_r,senha_r)
                        st.success(msg+" Faça login.") if ok else st.error(msg)

# ─── Tela de Configurações ─────────────────────────────────────────────────────
def tela_configuracoes():
    st.markdown("## ⚙️ Configurações")
    user = st.session_state.user
    cfg = user.get("configuracoes",{})
    st.markdown('<div class="settings-box">', unsafe_allow_html=True)
    st.markdown("**Conta**")
    c1,c2 = st.columns(2)
    with c1: novo_nome = st.text_input("Nome", value=user["nome"])
    with c2: st.text_input("E-mail", value=user["email"], disabled=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="settings-box">', unsafe_allow_html=True)
    st.markdown("**Preferências**")
    max_tokens = st.selectbox("Tamanho das respostas", [4096,8192,16000],
                              index=[4096,8192,16000].index(cfg.get("max_tokens",8192)))
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="settings-box">', unsafe_allow_html=True)
    st.markdown("**Dados**")
    st.markdown(f"**{len(st.session_state.conversas)}** conversas nesta sessão")
    st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
    if st.button("Apagar histórico", use_container_width=True):
        st.session_state.conversas=[]; st.session_state.messages=[]; st.session_state.historico=[]
        st.success("Apagado."); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    if st.button("Salvar", use_container_width=True):
        atualizar_usuario(user["email"],{"nome":novo_nome,"configuracoes":{**cfg,"max_tokens":max_tokens}})
        users = carregar_usuarios()
        if user["email"] in users: st.session_state.user = users[user["email"]]
        st.session_state.user["nome"] = novo_nome
        st.success("✅ Salvo!")
    st.markdown('</div>', unsafe_allow_html=True)

# ─── App Principal ──────────────────────────────────────────────────────────────
def main():
    init()
    apply_css()

    if not st.session_state.logged_in:
        tela_auth(); return

    user = st.session_state.user
    primeiro_nome = user["nome"].split()[0]
    dark = get_tema()

    if st.session_state.page == "configuracoes":
        with st.sidebar:
            st.markdown("**◈ NEXUS**")
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            if st.button("← Voltar", use_container_width=True):
                st.session_state.page="chat"; st.rerun()
        tela_configuracoes(); return

    with st.sidebar:
        st.markdown("**◈ NEXUS**")
        st.markdown('<div style="font-size:0.68rem;color:#888;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:14px;">CEO AI Assistant</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="user-badge"><div style="font-weight:500;font-size:0.82rem;">{user["nome"]}</div><div style="font-size:0.72rem;color:#888;">{user["email"]}</div></div>', unsafe_allow_html=True)

        # Botão tema claro/escuro
        tema_label = "☀️ Modo claro" if dark else "🌙 Modo escuro"
        if st.button(tema_label, use_container_width=True):
            st.session_state.dark_mode = not dark; st.rerun()

        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("+ Nova conversa", use_container_width=True):
            nova_conversa(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        if st.session_state.conversas:
            st.markdown('<div class="section-label">Histórico</div>', unsafe_allow_html=True)
            for conv in st.session_state.conversas:
                st.markdown(f'<div class="history-card"><div class="history-title">{conv["titulo"]}</div></div>', unsafe_allow_html=True)
                ca,cb = st.columns([5,1])
                with ca:
                    if st.button("↩", key=f"o{conv['id']}", use_container_width=True):
                        st.session_state.messages = conv["messages"].copy()
                        st.session_state.historico = [{"role":m["role"],"content":m["content"]} for m in conv["messages"]]
                        st.rerun()
                with cb:
                    if st.button("✕", key=f"d{conv['id']}"):
                        st.session_state.conversas = [c for c in st.session_state.conversas if c["id"]!=conv["id"]]
                        st.rerun()
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        if st.button("⚙ Configurações", use_container_width=True):
            st.session_state.page="configuracoes"; st.rerun()
        st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
        if st.button("Sair", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Área principal ──
    if not st.session_state.messages:
        st.markdown(f'<div class="chat-header"><h1>{saudacao()}, {primeiro_nome} 👋</h1><p>Estratégia · Finanças · Investimentos · Pessoas · Mercado</p></div>', unsafe_allow_html=True)
        sugestoes = [
            ("💰 LTV/CAC","Receita R$80k/mês, churn 2,5%, CAC R$600 — analise meu LTV/CAC"),
            ("📈 Investimentos","Quero investir R$200k com perfil moderado por 18 meses"),
            ("🔍 Pesquisar empresa","Pesquise a empresa Magazine Luiza e me dê um briefing"),
            ("🎯 Análise SWOT","Faça análise SWOT para minha empresa de healthtech"),
            ("👥 Organograma","Como monto organograma para empresa com 15 pessoas?"),
            ("📋 Plano de ação","Quero aumentar faturamento 40% em 6 meses. Como?"),
        ]
        cols = st.columns(3)
        for i,(titulo,pergunta) in enumerate(sugestoes):
            with cols[i%3]:
                if st.button(titulo, key=f"s{i}", use_container_width=True):
                    st.session_state.messages.append({"role":"user","content":pergunta})
                    r = processar_resposta(pergunta)
                    st.session_state.messages.append({"role":"assistant","content":r})
                    st.rerun()
    else:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if prompt := st.chat_input("Pergunte ao NEXUS... (ex: pesquise a empresa Menrad)"):
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            ph = st.empty()
            ph.markdown("_analisando..._")
            r = processar_resposta(prompt)
            ph.markdown(r)
        st.session_state.messages.append({"role":"assistant","content":r})
        st.rerun()

main()
