"""
NEXUS — CEO AI Assistant
Powered by Claude Sonnet + Streamlit Cloud
"""

import streamlit as st
import anthropic
import json
import os
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
try:
    from duckduckgo_search import DDGS
    WEB_SEARCH_OK = True
except Exception:
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

def salvar_usuarios(users):
    try:
        with open(USERS_FILE,"w",encoding="utf-8") as f: json.dump(users,f,ensure_ascii=False,indent=2)
    except: pass

def criar_usuario(nome, email, senha):
    users = carregar_usuarios()
    email = email.lower().strip()
    if email in users: return False,"E-mail já cadastrado."
    if len(senha)<6: return False,"Senha mínimo 6 caracteres."
    if not nome.strip(): return False,"Nome obrigatório."
    users[email] = {"id":str(uuid.uuid4()),"nome":nome.strip(),"email":email,"senha":hash_senha(senha),"criado_em":datetime.now().isoformat(),"configuracoes":{"idioma":"Português","max_tokens":8192}}
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

def hora_brasil():
    return datetime.now(tz=ZoneInfo("America/Sao_Paulo")).hour

def saudacao():
    h = hora_brasil()
    if h < 12: return "Bom dia"
    elif h < 18: return "Boa tarde"
    else: return "Boa noite"

def is_dia():
    return 6 <= hora_brasil() < 18

# ─── Configuração ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="NEXUS", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

# ─── Pega a API Key das Secrets do Streamlit Cloud ────────────────────────────
def get_api_key():
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return os.environ.get("ANTHROPIC_API_KEY", "")

# ─── CSS Dinâmico Dia/Noite ────────────────────────────────────────────────────
def render_css():
    dia = is_dia()
    # Cores do tema
    bg          = "#ffffff" if dia else "#0c0c0c"
    sidebar_bg  = "#f5f5f5" if dia else "#111111"
    text        = "#111111" if dia else "#dddddd"
    text_muted  = "#888888" if dia else "#555555"
    border      = "#e5e5e5" if dia else "#1e1e1e"
    input_bg    = "#f9f9f9" if dia else "#161616"
    btn_bg      = "#ffffff" if dia else "#181818"
    btn_text    = "#444444" if dia else "#777777"
    btn_hover   = "#f0f0f0" if dia else "#222222"
    code_bg     = "#f3f4f6" if dia else "#161616"
    code_color  = "#1d4ed8" if dia else "#7dd3fc"
    table_head  = "#f3f4f6" if dia else "#161616"
    table_text  = "#333333" if dia else "#aaaaaa"
    history_bg  = "#ffffff" if dia else "#111111"
    settings_bg = "#f7f7f7" if dia else "#141414"
    badge_bg    = "#eeeeee" if dia else "#1a1a1a"
    chat_bottom = bg

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

/* ── FORÇA COR DE FUNDO E FONTE ── */
html, body {{ background-color: {bg} !important; color: {text} !important; }}
.stApp, .stApp > div {{ background-color: {bg} !important; }}
[class*="css"], p, span, div, label, h1, h2, h3, h4, h5, h6, li, td, th {{
    font-family: 'Inter', sans-serif !important;
    color: {text} !important;
}}
/* Streamlit specific text elements */
.stMarkdown, .stText, [data-testid="stMarkdownContainer"] > * {{color: {text} !important;}}
[data-testid="stHeader"], [data-testid="stSidebarContent"] * {{color: {text} !important;}}
.stSelectbox label, .stTextInput label, .stTextArea label, .stSlider label {{color: {text} !important;}}
small, .caption, [data-testid="stCaptionContainer"] {{color: {text_muted} !important;}}
</style>
<style>
/* ── SEGUNDO BLOCO (garante prioridade) ── */
html, body, .stApp {{ background-color: {bg} !important; font-family: 'Inter', sans-serif !important; }}


/* ── SIDEBAR SEMPRE VISÍVEL ── */
section[data-testid="stSidebar"] {{
    display: block !important; visibility: visible !important;
    opacity: 1 !important; transform: none !important;
    background-color: {sidebar_bg} !important;
    border-right: 1px solid {border} !important;
    min-width: 260px !important; max-width: 260px !important;
    width: 260px !important; position: relative !important;
    left: 0 !important; transition: none !important;
}}
section[data-testid="stSidebar"] > div {{ padding: 20px 14px !important; }}
section[data-testid="stSidebar"][aria-expanded="false"] {{
    display: block !important; min-width: 260px !important;
    width: 260px !important; transform: none !important;
}}
button[data-testid="collapsedControl"],
button[data-testid="baseButton-headerNoPadding"],
[data-testid="stSidebarCollapsedControl"],
div[data-testid="collapsedControl"] {{ display: none !important; }}

/* ── IDENTIDADE ── */
.nexus-logo {{ font-size:1.2rem; font-weight:600; color:{text}; letter-spacing:0.08em; }}
.nexus-sub {{ font-size:0.68rem; color:{text_muted}; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:14px; }}
.divider {{ border-top:1px solid {border}; margin:12px 0; }}
.section-label {{ font-size:0.65rem; color:{text_muted}; text-transform:uppercase; letter-spacing:0.1em; margin:12px 0 6px; }}

/* ── BOTÕES ── */
.stButton > button {{
    background:{btn_bg} !important; border:1px solid {border} !important;
    color:{btn_text} !important; border-radius:8px !important; font-size:0.8rem !important;
    white-space:normal !important; height:auto !important; padding:8px 12px !important;
    transition:all 0.15s !important;
}}
.stButton > button:hover {{ border-color:{text_muted} !important; color:{text} !important; background:{btn_hover} !important; }}
.primary-btn > button {{ background:{text} !important; color:{bg} !important; border:none !important; font-weight:500 !important; }}
.primary-btn > button:hover {{ opacity:0.85 !important; }}
.danger-btn > button {{ background:transparent !important; border:1px solid #fca5a5 !important; color:#ef4444 !important; }}
.danger-btn > button:hover {{ background:#fee2e2 !important; }}

/* ── CHAT HEADER ── */
.chat-header {{ text-align:center; padding:60px 20px 36px; }}
.chat-header h1 {{ font-size:1.9rem; font-weight:500; color:{text}; margin-bottom:8px; }}
.chat-header p {{ color:{text_muted}; font-size:0.82rem; font-weight:300; }}

/* ── MENSAGENS ── */
div[data-testid="stChatMessage"] {{ background:transparent !important; }}
.stMarkdown p, .stMarkdown li {{ color:{text}; font-size:0.88rem; line-height:1.75; }}
.stMarkdown h1,.stMarkdown h2,.stMarkdown h3 {{ color:{text}; }}
.stMarkdown strong {{ color:{text}; }}
.stMarkdown code {{ background:{code_bg}; color:{code_color}; border-radius:4px; padding:2px 6px; font-size:0.82rem; }}
.stMarkdown pre {{ background:{code_bg} !important; border:1px solid {border}; border-radius:8px; padding:14px; }}
.stMarkdown table {{ border-collapse:collapse; width:100%; font-size:0.82rem; }}
.stMarkdown th {{ background:{table_head}; color:{text_muted}; padding:8px 12px; border:1px solid {border}; font-weight:500; }}
.stMarkdown td {{ color:{table_text}; padding:7px 12px; border:1px solid {border}; }}

/* ── INPUTS ── */
.stTextInput > div > div > input {{
    background:{input_bg} !important; border:1px solid {border} !important;
    color:{text} !important; border-radius:8px !important; font-size:0.85rem !important;
}}
.stTextInput > div > div > input:focus {{ border-color:{text_muted} !important; box-shadow:none !important; }}
div[data-testid="stChatInput"] > div {{ background:{input_bg} !important; border:1px solid {border} !important; border-radius:12px !important; }}
div[data-testid="stChatInput"] textarea {{ color:{text} !important; background:transparent !important; }}
.stChatFloatingInputContainer {{ background-color:{chat_bottom} !important; padding-bottom:0 !important; }}
[data-testid="stChatInputContainer"] {{ background-color:{chat_bottom} !important; }}
.stBottom, .stBottom > div {{ background-color:{chat_bottom} !important; }}

/* ── HISTÓRICO ── */
.history-card {{ background:{history_bg}; border:1px solid {border}; border-radius:8px; padding:8px 10px; margin-bottom:4px; }}
.history-title {{ font-size:0.78rem; color:{text}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}

/* ── AUTH PAGE ── */
.auth-logo {{ font-size:1.6rem; font-weight:600; color:{text}; text-align:center; margin-bottom:4px; letter-spacing:0.1em; }}
.auth-sub {{ font-size:0.75rem; color:{text_muted}; text-align:center; margin-bottom:24px; text-transform:uppercase; letter-spacing:0.08em; }}

/* ── SETTINGS PAGE ── */
.settings-section {{ background:{settings_bg}; border:1px solid {border}; border-radius:10px; padding:18px; margin-bottom:14px; }}
.settings-title {{ font-size:0.72rem; color:{text_muted}; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:12px; font-weight:500; }}

/* ── SELECT / TABS / TEXTAREA ── */
div[data-baseweb="select"] > div {{ background:{input_bg} !important; border-color:{border} !important; color:{text} !important; }}
div[data-baseweb="tab-list"] {{ background:{sidebar_bg} !important; border-bottom:1px solid {border} !important; }}
button[data-baseweb="tab"] {{ color:{text_muted} !important; }}
button[data-baseweb="tab"][aria-selected="true"] {{ color:{text} !important; border-bottom:2px solid {text} !important; }}
textarea {{ background:{input_bg} !important; color:{text} !important; border:1px solid {border} !important; border-radius:8px !important; }}

/* ── USER BADGE SIDEBAR ── */
.user-badge {{ background:{badge_bg}; border:1px solid {border}; border-radius:8px; padding:8px 10px; margin-bottom:12px; }}
.user-badge-name {{ color:{text}; font-weight:500; font-size:0.82rem; }}
.user-badge-email {{ color:{text_muted}; font-size:0.72rem; }}

#MainMenu, footer, header {{ visibility:hidden; }}
</style>
""", unsafe_allow_html=True)

# ─── Prompt ────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Você é NEXUS — assistente executivo de IA para CEOs, fundadores e líderes empresariais.

Identidade: conselheiro estratégico sênior, direto, objetivo, orientado a dados. Fala sempre em português do Brasil.

Especialidades: estratégia (OKRs, SWOT, Porter, BCG), finanças (DRE, valuation, captação, unit economics), investimentos (renda fixa, ações, FIIs, cripto, VC), gestão de pessoas (RH, salário, equity, cultura), marketing/vendas (GTM, precificação, funil), tecnologia, regulação brasileira.

REGRA DE BUSCA — OBRIGATÓRIO:
- Sempre que o usuário mencionar o nome de qualquer empresa (ex: "Menrad", "Magazine Luiza", "minha empresa X"), use IMEDIATAMENTE a ferramenta buscar_web para pesquisar essa empresa na internet.
- Sempre que pedir notícias, cotações, tendências, mercado ou qualquer dado em tempo real, use buscar_web antes de responder.
- Combine os dados da busca com sua análise para dar uma resposta completa e atualizada.
- Nunca diga que não conhece uma empresa sem antes pesquisar na web.

Padrão de resposta: direto, use dados reais, tabelas para comparações, termine com PRÓXIMOS PASSOS numerados."""

def get_system_prompt():
    return SYSTEM_PROMPT

# ─── Ferramentas ───────────────────────────────────────────────────────────────
TOOLS = [
    {"name":"calcular_metricas_financeiras","description":"Calcula LTV/CAC, EBITDA, valuation, ROI, burn rate, runway, break-even.","input_schema":{"type":"object","properties":{"tipo_calculo":{"type":"string","enum":["ltv_cac","ebitda","valuation_multiplos","roi","break_even","burn_rate","dcf_simples"]},"dados":{"type":"object"}},"required":["tipo_calculo","dados"]}},
    {"name":"analisar_mercado","description":"Análise de mercado: tendências, competidores, oportunidades, riscos por setor.","input_schema":{"type":"object","properties":{"setor":{"type":"string"},"foco":{"type":"string","enum":["competidores","tendencias","oportunidades","riscos","regulatorio","tam_sam_som","completo"]},"regiao":{"type":"string"}},"required":["setor","foco"]}},
    {"name":"analisar_investimentos","description":"Análise de investimentos: renda fixa, ações, FIIs, cripto, VC, carteira.","input_schema":{"type":"object","properties":{"tipo_analise":{"type":"string","enum":["renda_fixa","renda_variavel","fundos","cripto","venture_capital","imoveis","comparativo_carteira"]},"perfil_risco":{"type":"string","enum":["conservador","moderado","arrojado","agressivo"]},"valor_disponivel":{"type":"number"},"prazo_meses":{"type":"integer"},"objetivo":{"type":"string"}},"required":["tipo_analise","perfil_risco"]}},
    {"name":"gestao_rh_equipe","description":"RH: organograma, salário, avaliação, recrutamento, equity, cultura.","input_schema":{"type":"object","properties":{"area":{"type":"string","enum":["organograma","politica_salarial","avaliacao_desempenho","recrutamento","retencao","cultura","equity_plr","lideranca"]},"contexto_empresa":{"type":"string"},"problema_especifico":{"type":"string"}},"required":["area","contexto_empresa"]}},
    {"name":"gerar_framework_estrategico","description":"Frameworks: SWOT, OKR, Canvas, Porter, Ansoff, BCG, BSC.","input_schema":{"type":"object","properties":{"framework":{"type":"string","enum":["swot","okr","business_canvas","porters_five_forces","ansoff","bcg_matrix","balanced_scorecard"]},"empresa_contexto":{"type":"string"},"objetivo":{"type":"string"}},"required":["framework","empresa_contexto"]}},
    {"name":"criar_plano_acao","description":"Plano de ação faseado com KPIs.","input_schema":{"type":"object","properties":{"objetivo":{"type":"string"},"prazo_meses":{"type":"integer"},"tipo_empresa":{"type":"string"}},"required":["objetivo","prazo_meses"]}},
    {"name":"calcular_precificacao","description":"Precificação: cost-plus, value-based, freemium, subscription.","input_schema":{"type":"object","properties":{"metodo":{"type":"string","enum":["cost_plus","value_based","competitivo","freemium","subscription","comparativo"]},"dados_produto":{"type":"object"},"meta_margem":{"type":"number"},"segmento_alvo":{"type":"string"}},"required":["metodo","dados_produto"]}},
    {"name":"due_diligence","description":"Due diligence para M&A, captação, parceria.","input_schema":{"type":"object","properties":{"tipo":{"type":"string","enum":["ma_compra","ma_venda","captacao_investidor","parceria_estrategica","aquisicao_startup"]},"empresa_alvo":{"type":"string"},"area_foco":{"type":"string","enum":["financeiro","juridico","tecnologia","comercial","rh","completo"]}},"required":["tipo","empresa_alvo","area_foco"]}},
    {"name":"benchmark_setor","description":"Benchmarks por setor e porte.","input_schema":{"type":"object","properties":{"setor":{"type":"string"},"metrica":{"type":"string"},"porte":{"type":"string","enum":["startup","pme","mid_market","enterprise"]}},"required":["setor","metrica"]}},
    {"name":"projecao_financeira","description":"Projeções: DRE, crescimento, cenários.","input_schema":{"type":"object","properties":{"tipo_projecao":{"type":"string","enum":["dre_simplificada","crescimento_receita","cenarios_pessimista_otimista"]},"dados_atuais":{"type":"object"},"horizonte_meses":{"type":"integer"}},"required":["tipo_projecao","dados_atuais","horizonte_meses"]}},
    {"name":"buscar_web","description":"Pesquisa informações na internet em tempo real: notícias, empresas, concorrentes, cotações, tendências, qualquer assunto atual.","input_schema":{"type":"object","properties":{"query":{"type":"string","description":"O que pesquisar no Google/web"},"max_results":{"type":"integer","description":"Número de resultados (padrão 6)"}},"required":["query"]}}
]

# ─── Implementação Ferramentas ─────────────────────────────────────────────────
def calcular_metricas_financeiras(tipo, dados):
    if tipo=="ltv_cac":
        r=dados.get("receita_media_mensal",0); ch=dados.get("churn_mensal_pct",1)/100
        m=dados.get("margem_bruta_pct",70)/100; cac=dados.get("cac",0)
        ltv=(r*m)/ch if ch>0 else 0; ratio=ltv/cac if cac>0 else 0
        return {"LTV":f"R$ {ltv:,.2f}","CAC":f"R$ {cac:,.2f}","Ratio_LTV_CAC":f"{ratio:.1f}x","Payback":f"{cac/(r*m):.1f} meses" if r>0 else "N/A","Status":"✅ Saudável" if ratio>=3 else "⚠️ Atenção" if ratio>=1 else "🚨 Crítico"}
    elif tipo=="burn_rate":
        d=dados.get("despesas_mensais",0); r=dados.get("receita_mensal",0); c=dados.get("caixa_disponivel",0)
        burn=d-r; rw=c/burn if burn>0 else float('inf')
        return {"Burn_Liquido":f"R$ {burn:,.2f}/mês","Runway":f"{rw:.1f} meses" if rw!=float('inf') else "Positivo ✅","Alerta":"🚨 URGENTE" if rw<6 else "⚠️ Atenção" if rw<12 else "✅ Seguro"}
    elif tipo=="valuation_multiplos":
        rec=dados.get("receita_anual",0); eb=dados.get("ebitda",0); mr=dados.get("multiplo_receita",5); me=dados.get("multiplo_ebitda",10)
        return {"Valuation_Receita":f"R$ {rec*mr:,.2f} ({mr}x)","Valuation_EBITDA":f"R$ {eb*me:,.2f} ({me}x)" if eb>0 else "N/A"}
    elif tipo=="roi":
        inv=dados.get("investimento",0); ret=dados.get("retorno_esperado",0); m=dados.get("periodo_meses",12)
        roi=((ret-inv)/inv*100) if inv>0 else 0
        return {"ROI":f"{roi:.1f}%","ROI_Anualizado":f"{roi*(12/m):.1f}%","Lucro":f"R$ {ret-inv:,.2f}","Avaliacao":"✅ Excelente" if roi>50 else "✅ Bom" if roi>20 else "⚠️ Marginal" if roi>0 else "🚨 Negativo"}
    elif tipo=="break_even":
        cf=dados.get("custos_fixos_mensais",0); mc=dados.get("margem_contribuicao_pct",0)/100
        return {"Break_Even":f"R$ {cf/mc:,.2f}/mês" if mc>0 else "N/A"}
    return dados

def analisar_mercado(setor, foco, regiao="Brasil"):
    setores={"fintech":{"tam":"R$ 450B+","crescimento":"25-35%/ano","tendencias":["Open Finance","PIX","BaaS"],"margens":"45-65%"},"saude":{"tam":"R$ 850B+","crescimento":"10-15%/ano","tendencias":["Telemedicina","IA","Preventiva"],"margens":"30-50%"},"varejo":{"tam":"R$ 1.8T+","crescimento":"5-12%/ano","tendencias":["Social commerce","Omnichannel"],"margens":"20-45%"},"saas_b2b":{"tam":"R$ 15B+ BR","crescimento":"30-50%/ano","tendencias":["AI-native","Vertical SaaS","PLG"],"margens":"70-85%"},"agro":{"tam":"R$ 2T+","crescimento":"8-15%/ano","tendencias":["Agritech","Precisão","IoT"],"margens":"15-35%"}}
    dados=setores.get(setor.lower().replace(" ","_"),{"tendencias":["Digitalização","ESG","IA"]})
    return {"setor":setor,"regiao":regiao,"foco":foco,"data":datetime.now().strftime("%d/%m/%Y"),**dados}

def analisar_investimentos(tipo, perfil, valor=0, prazo=12, objetivo=""):
    indicadores={"Selic":"10,50%/ano","CDI":"10,40%/ano","IPCA":"~4,5%"}
    alocacoes={"conservador":{"Renda fixa liq.":"60%","Renda fixa prazo":"30%","Renda variável":"5%","Alternativo":"5%"},"moderado":{"Renda fixa":"40%","Ações BR":"25%","Ações EUA":"15%","FIIs":"15%","Cripto":"5%"},"arrojado":{"Renda fixa":"20%","Ações BR":"30%","Ações EUA":"25%","FIIs":"15%","VC/Cripto":"10%"},"agressivo":{"Ações BR":"40%","Ações internac.":"35%","VC":"15%","Cripto":"10%"}}
    return {"tipo":tipo,"perfil":perfil,"valor":f"R$ {valor:,.2f}" if valor>0 else "Não informado","prazo":f"{prazo} meses","indicadores":indicadores,"alocacao_sugerida":alocacoes.get(perfil,{}),"aviso":"⚠️ Consulte um assessor certificado."}

def gestao_rh_equipe(area, contexto, problema=""):
    dados={"organograma":{"modelos":{"até 15":"Flat","15-50":"Funcional","50-200":"Matricial"},"ratio":"1:6-8"},"politica_salarial":{"componentes":["Salário base","Variável 10-30%","Equity","Benefícios"]},"recrutamento":{"etapas":["JD claro","Sourcing","Triagem","STAR","Case","Referências"],"meta":"30-45 dias"},"retencao":{"drivers":["Crescimento","Gestor","Salário","Propósito"],"custo":"1-2x salário anual"},"equity_plr":{"stock_options":"Cliff 1a, vesting 4a","plr":"Lei 10.101/2000"}}
    return {"area":area,"contexto":contexto,"framework":dados.get(area,{})}

def gerar_framework_estrategico(framework, contexto, objetivo=""):
    fs={"okr":{"estrutura":{"Objetivo":"Meta ambiciosa","KRs":"70% = sucesso"},"dicas":["Máx 3-5 KRs","Revisar mensalmente"]},"swot":{"quadrantes":{"S":"Forças","W":"Fraquezas","O":"Oportunidades","T":"Ameaças"},"cruzamentos":"S+O=Ofensiva | W+T=Defensiva"},"business_canvas":{"blocos":["Segmentos","Proposta Valor","Canais","Relacionamento","Receita","Recursos","Atividades","Parcerias","Custos"]},"porters_five_forces":{"forcas":["Rivalidade","Novos entrantes","Substitutos","Poder fornecedor","Poder comprador"]},"ansoff":{"Penetração":"Atual+Atual","Dev.Produto":"Novo+Atual","Dev.Mercado":"Atual+Novo","Diversificação":"Novo+Novo"}}
    return {"framework":framework.upper(),"contexto":contexto,"objetivo":objetivo,"conteudo":fs.get(framework,{})}

def criar_plano_acao(objetivo, prazo, tipo="startup"):
    q=max(1,prazo//4)
    fases=[{"fase":"Fundação","periodo":f"Meses 1-{q}","entregaveis":["Diagnóstico","KPIs","Alinhamento"]},{"fase":"Construção","periodo":f"Meses {q+1}-{prazo//2}","entregaveis":["Iniciativas","Processos"]},{"fase":"Escala","periodo":f"Meses {prazo//2+1}-{prazo*3//4}","entregaveis":["Resultados","Otimizações"]},{"fase":"Consolidação","periodo":f"Meses {prazo*3//4+1}-{prazo}","entregaveis":["Metas validadas","Próximo ciclo"]}] if prazo>3 else [{"fase":"Execução","periodo":f"{prazo} meses","entregaveis":["Diagnóstico","Execução","Medição"]}]
    return {"objetivo":objetivo,"prazo":f"{prazo} meses","fases":fases,"kpis":["MRR","Churn","NPS","CAC","LTV"]}

def calcular_precificacao(metodo, dados, margem=0, segmento=""):
    custo=dados.get("custo_unitario",0); conc=dados.get("preco_concorrente",0); vp=dados.get("valor_percebido_cliente",0)
    res={"metodo":metodo}
    if metodo=="cost_plus" and custo>0: m=margem/100 if margem>0 else 0.5; res["preco"]=f"R$ {custo/(1-m):,.2f}"
    elif metodo=="value_based" and vp>0: res.update({"preco_30pct":f"R$ {vp*0.3:,.2f}","valor_gerado":f"R$ {vp:,.2f}"})
    elif metodo=="competitivo" and conc>0: res.update({"premium":f"R$ {conc*1.05:,.2f}","paridade":f"R$ {conc:,.2f}","desconto":f"R$ {conc*0.85:,.2f}"})
    return res

def due_diligence(tipo, empresa, area):
    cl={"financeiro":["DRE 3 anos","Balanço","Fluxo de Caixa","Contratos","Dívidas","Certidões"],"juridico":["Contrato social","Processos","Contratos key","PI","LGPD"],"tecnologia":["Arquitetura","Segurança","Infraestrutura","Código","Uptime"],"comercial":["Top 10 clientes","Pipeline","NPS","Renovações"],"rh":["Organograma","Contratos","Passivos","Equity","Key man"]}
    areas=list(cl.keys()) if area=="completo" else [area]
    return {"tipo":tipo,"empresa":empresa,"checklists":{a:cl[a] for a in areas if a in cl},"red_flags":["Concentração >40% em 1 cliente","Dívida oculta","Key man risk"]}

def benchmark_setor(setor, metrica, porte="startup"):
    dados={"saas_b2b":{"margem_bruta":{"startup":"65-75%","pme":"70-80%","enterprise":"75-85%"},"churn_anual":{"startup":"15-25%","pme":"8-15%","enterprise":"5-10%"},"ratio_ltv_cac":{"startup":"2-4x","pme":"3-5x","enterprise":"4-8x"}},"ecommerce":{"margem_bruta":{"startup":"25-40%","pme":"30-45%","enterprise":"35-55%"}},"fintech":{"margem_bruta":{"startup":"50-65%","pme":"55-70%","enterprise":"60-75%"}}}
    sk=setor.lower().replace(" ","_"); mk=metrica.lower().replace(" ","_")
    return {"setor":setor,"metrica":metrica,"porte":porte,"benchmark":dados.get(sk,{}).get(mk,{}).get(porte,"Consultar relatório setorial")}

def projecao_financeira(tipo, dados, horizonte):
    if tipo=="crescimento_receita":
        r=dados.get("receita_mensal",0); tc=dados.get("crescimento_mensal_pct",10)/100
        rv=r; proj=[]
        for i in range(1,horizonte+1):
            rv*=(1+tc)
            if i%3==0: proj.append({"mes":i,"receita":f"R$ {rv:,.2f}"})
        return {"inicial":f"R$ {r:,.2f}","final":f"R$ {rv:,.2f}","crescimento":f"{((rv/r)-1)*100:.1f}%" if r>0 else "N/A","trimestres":proj}
    elif tipo=="dre_simplificada":
        rec=dados.get("receita_mensal",0); cogs=dados.get("custos_variaveis_pct",30)/100; opex=dados.get("despesas_fixas_mensais",0)
        mb=rec*(1-cogs); ebitda=mb-opex
        return {"Receita":f"R$ {rec:,.2f}","Margem_Bruta":f"R$ {mb:,.2f}","EBITDA":f"R$ {ebitda:,.2f}","Status":"✅ Lucrativo" if ebitda>0 else "🔴 Queimando caixa"}
    elif tipo=="cenarios_pessimista_otimista":
        rec=dados.get("receita_mensal",0); tc=dados.get("crescimento_mensal_pct",10)/100
        return {"pessimista":f"R$ {rec*(1+tc*0.5)**horizonte:,.2f}","base":f"R$ {rec*(1+tc)**horizonte:,.2f}","otimista":f"R$ {rec*(1+tc*1.5)**horizonte:,.2f}"}
    return {}

def buscar_web(query, max_results=6):
    if not WEB_SEARCH_OK:
        return {"erro": "Busca web não disponível. Instale duckduckgo-search."}
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return [{"titulo": r.get("title",""), "resumo": r.get("body",""), "url": r.get("href","")} for r in results]
    except Exception as e:
        return {"erro": str(e)}

def executar_ferramenta(nome, inputs):
    mapa={
        "calcular_metricas_financeiras":lambda i:calcular_metricas_financeiras(i["tipo_calculo"],i["dados"]),
        "analisar_mercado":lambda i:analisar_mercado(i["setor"],i["foco"],i.get("regiao","Brasil")),
        "analisar_investimentos":lambda i:analisar_investimentos(i["tipo_analise"],i["perfil_risco"],i.get("valor_disponivel",0),i.get("prazo_meses",12),i.get("objetivo","")),
        "gestao_rh_equipe":lambda i:gestao_rh_equipe(i["area"],i["contexto_empresa"],i.get("problema_especifico","")),
        "gerar_framework_estrategico":lambda i:gerar_framework_estrategico(i["framework"],i["empresa_contexto"],i.get("objetivo","")),
        "criar_plano_acao":lambda i:criar_plano_acao(i["objetivo"],i["prazo_meses"],i.get("tipo_empresa","startup")),
        "calcular_precificacao":lambda i:calcular_precificacao(i["metodo"],i["dados_produto"],i.get("meta_margem",0),i.get("segmento_alvo","")),
        "due_diligence":lambda i:due_diligence(i["tipo"],i["empresa_alvo"],i["area_foco"]),
        "benchmark_setor":lambda i:benchmark_setor(i["setor"],i["metrica"],i.get("porte","startup")),
        "projecao_financeira":lambda i:projecao_financeira(i["tipo_projecao"],i["dados_atuais"],i["horizonte_meses"]),
        "buscar_web":lambda i:buscar_web(i["query"],i.get("max_results",6))
    }
    fn=mapa.get(nome)
    return fn(inputs) if fn else {"erro":f"'{nome}' não encontrada"}

# ─── Processar Resposta ────────────────────────────────────────────────────────
def processar_resposta(prompt):
    api_key = get_api_key()
    if not api_key:
        return "⚠️ API Key não configurada. Adicione nas **Secrets** do Streamlit Cloud."

    client = anthropic.Anthropic(api_key=api_key)
    st.session_state.historico.append({"role":"user","content":prompt})
    resposta_final = ""

    with st.spinner(""):
        while True:
            with client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=8192,
                system=[{"type":"text","text":get_system_prompt(),"cache_control":{"type":"ephemeral"}}],
                tools=TOOLS,
                messages=st.session_state.historico
            ) as stream:
                response = stream.get_final_message()

            if response.stop_reason == "tool_use":
                resultados=[]
                for bloco in response.content:
                    if bloco.type=="tool_use":
                        r=executar_ferramenta(bloco.name,bloco.input)
                        resultados.append({"type":"tool_result","tool_use_id":bloco.id,"content":json.dumps(r,ensure_ascii=False,indent=2)})
                st.session_state.historico.append({"role":"assistant","content":response.content})
                st.session_state.historico.append({"role":"user","content":resultados})
            else:
                for bloco in response.content:
                    if hasattr(bloco,"text"): resposta_final+=bloco.text
                st.session_state.historico.append({"role":"assistant","content":response.content})
                break

    return resposta_final

# ─── Session State ─────────────────────────────────────────────────────────────
def init():
    for k,v in {"messages":[],"historico":[],"conv_id":0,"conversas":[],"logged_in":False,"user":None,"page":"chat"}.items():
        if k not in st.session_state: st.session_state[k]=v

def nova_conversa():
    if st.session_state.messages:
        titulo=next((m["content"][:40] for m in st.session_state.messages if m["role"]=="user"),"Conversa")
        st.session_state.conversas.insert(0,{"id":st.session_state.conv_id,"titulo":titulo,"messages":st.session_state.messages.copy()})
        if len(st.session_state.conversas)>30: st.session_state.conversas=st.session_state.conversas[:30]
    st.session_state.messages=[]
    st.session_state.historico=[]
    st.session_state.conv_id+=1

# ─── Tela de Login ─────────────────────────────────────────────────────────────
def tela_auth():
    _,col,_ = st.columns([1,1.2,1])
    with col:
        st.markdown('<div class="auth-logo">◈ NEXUS</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">CEO AI Assistant</div>', unsafe_allow_html=True)
        tab1,tab2 = st.tabs(["Entrar","Criar conta"])
        with tab1:
            with st.form("login"):
                email = st.text_input("E-mail", placeholder="seu@email.com")
                senha = st.text_input("Senha", type="password", placeholder="••••••••")
                if st.form_submit_button("Entrar", use_container_width=True):
                    ok,msg,user = login_usuario(email,senha)
                    if ok:
                        st.session_state.logged_in=True
                        st.session_state.user=user
                        st.rerun()
                    else: st.error(msg)
        with tab2:
            with st.form("register"):
                nome = st.text_input("Nome completo", placeholder="João Silva")
                email_r = st.text_input("E-mail", placeholder="seu@email.com")
                senha_r = st.text_input("Senha", type="password", placeholder="Mínimo 6 caracteres")
                senha_r2 = st.text_input("Confirmar senha", type="password", placeholder="••••••••")
                if st.form_submit_button("Criar conta", use_container_width=True):
                    if senha_r!=senha_r2: st.error("As senhas não coincidem.")
                    else:
                        ok,msg = criar_usuario(nome,email_r,senha_r)
                        st.success(msg+" Faça login.") if ok else st.error(msg)

# ─── Tela de Configurações ─────────────────────────────────────────────────────
def tela_configuracoes():
    st.markdown("## ⚙️ Configurações")
    user = st.session_state.user
    cfg = user.get("configuracoes",{})

    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.markdown('<div class="settings-title">Conta</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1: novo_nome = st.text_input("Nome", value=user["nome"])
    with c2: st.text_input("E-mail", value=user["email"], disabled=True)
    st.markdown('</div>', unsafe_allow_html=True)


    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.markdown('<div class="settings-title">Preferências</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1: max_tokens = st.selectbox("Tamanho das respostas", [4096,8192,16000], index=[4096,8192,16000].index(cfg.get("max_tokens",8192)))
    with c2: idioma = st.selectbox("Idioma", ["Português","English","Español"], index=["Português","English","Español"].index(cfg.get("idioma","Português")))
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.markdown('<div class="settings-title">Dados</div>', unsafe_allow_html=True)
    st.markdown(f"**{len(st.session_state.conversas)}** conversas nesta sessão")
    st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
    if st.button("Apagar histórico da sessão", use_container_width=True):
        st.session_state.conversas=[]; st.session_state.messages=[]; st.session_state.historico=[]
        st.success("Histórico apagado."); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    if st.button("Salvar configurações", use_container_width=True):
        atualizar_usuario(user["email"],{"nome":novo_nome,"configuracoes":{**cfg,"max_tokens":max_tokens,"idioma":idioma}})
        users=carregar_usuarios()
        if user["email"] in users: st.session_state.user=users[user["email"]]
        st.session_state.user["nome"]=novo_nome
        st.success("✅ Salvo com sucesso!")
    st.markdown('</div>', unsafe_allow_html=True)

# ─── App Principal ──────────────────────────────────────────────────────────────
def main():
    init()
    render_css()

    if not st.session_state.logged_in:
        tela_auth(); return

    user = st.session_state.user
    primeiro_nome = user["nome"].split()[0]

    # Configurações
    if st.session_state.page == "configuracoes":
        with st.sidebar:
            st.markdown('<div class="nexus-logo">◈ NEXUS</div>', unsafe_allow_html=True)
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            if st.button("← Voltar ao chat", use_container_width=True):
                st.session_state.page="chat"; st.rerun()
        tela_configuracoes(); return

    # Sidebar do Chat
    with st.sidebar:
        st.markdown('<div class="nexus-logo">◈ NEXUS</div>', unsafe_allow_html=True)
        st.markdown('<div class="nexus-sub">CEO AI Assistant</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="user-badge"><div class="user-badge-name">{user["nome"]}</div><div class="user-badge-email">{user["email"]}</div></div>', unsafe_allow_html=True)

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
                    if st.button("↩ abrir", key=f"o{conv['id']}", use_container_width=True):
                        st.session_state.messages=conv["messages"].copy()
                        st.session_state.historico=[{"role":m["role"],"content":m["content"]} for m in conv["messages"]]
                        st.rerun()
                with cb:
                    if st.button("✕", key=f"d{conv['id']}"):
                        st.session_state.conversas=[c for c in st.session_state.conversas if c["id"]!=conv["id"]]
                        st.rerun()

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Menu</div>', unsafe_allow_html=True)
        if st.button("⚙ Configurações", use_container_width=True):
            st.session_state.page="configuracoes"; st.rerun()
        st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
        if st.button("Sair", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Área principal
    if not st.session_state.messages:
        st.markdown(f'<div class="chat-header"><h1>{saudacao()}, {primeiro_nome} 👋</h1><p>Estratégia · Finanças · Investimentos · Pessoas · Mercado</p></div>', unsafe_allow_html=True)
        sugestoes=[
            ("💰 Analisar LTV/CAC","Receita R$80k/mês, churn 2,5%, CAC R$600 — analise meu LTV/CAC"),
            ("📈 Investir caixa","Quero investir R$200k com perfil moderado por 18 meses"),
            ("👥 Estruturar time","Como monto organograma para SaaS B2B com 15 pessoas?"),
            ("🎯 Análise SWOT","Faça análise SWOT para minha empresa de healthtech"),
            ("💲 Precificação","Como precificar meu SaaS? Custo R$50, concorrente R$400/mês"),
            ("🔍 Due Diligence","Due diligence financeiro para aquisição de startup por R$5M"),
        ]
        cols=st.columns(3)
        for i,(titulo,pergunta) in enumerate(sugestoes):
            with cols[i%3]:
                if st.button(titulo, key=f"s{i}", use_container_width=True):
                    st.session_state.messages.append({"role":"user","content":pergunta})
                    r=processar_resposta(pergunta)
                    st.session_state.messages.append({"role":"assistant","content":r})
                    st.rerun()
    else:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if prompt:=st.chat_input("Pergunte ao NEXUS..."):
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            ph=st.empty()
            ph.markdown('<span style="color:#aaa;font-style:italic;font-size:0.8rem;">analisando...</span>', unsafe_allow_html=True)
            r=processar_resposta(prompt)
            ph.markdown(r)
        st.session_state.messages.append({"role":"assistant","content":r})
        st.rerun()

if __name__=="__main__":
    main()
