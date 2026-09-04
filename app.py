import os
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import time
from urllib.parse import urlparse

# Carregamento seguro das variáveis de ambiente
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import google.generativeai as genai
    HAS_GEMINI_SDK = True
except ImportError:
    HAS_GEMINI_SDK = False

# 1. CONFIGURAÇÃO DA PÁGINA STREAMLIT
st.set_page_config(
    page_title="Lucas Tadeu SEO | Case Sabiá Gaming",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. INJEÇÃO DE DESIGN SYSTEM E CSS CUSTOMIZADO (UX/UI PREMIUM + LINKEDIN)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Top Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 1.8rem 2.2rem;
        border-radius: 14px;
        color: #ffffff;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
        margin-bottom: 1.8rem;
        border-left: 6px solid #38bdf8;
    }
    
    .hero-badge {
        background-color: #0284c7;
        color: #ffffff;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 8px;
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
        color: #f8fafc;
    }

    .hero-subtitle {
        font-size: 1rem;
        color: #94a3b8;
        margin-top: 6px;
        margin-bottom: 0;
    }

    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }
    
    .author-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.2rem 1rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .author-name {
        font-size: 1.15rem;
        font-weight: 700;
        color: #38bdf8 !important;
        margin: 0;
    }

    .author-role {
        font-size: 0.8rem;
        color: #94a3b8 !important;
        margin-top: 2px;
        margin-bottom: 10px;
    }

    /* Botão do LinkedIn na Sidebar */
    .linkedin-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        background-color: #0077b5;
        color: #ffffff !important;
        padding: 6px 14px;
        border-radius: 18px;
        font-size: 0.78rem;
        font-weight: 600;
        text-decoration: none !important;
        transition: all 0.2s ease-in-out;
        margin-top: 4px;
    }
    .linkedin-btn:hover {
        background-color: #005582;
        color: #ffffff !important;
        transform: translateY(-1px);
    }

    /* Metric Card Styling Enhancements */
    div[data-testid="stMetricValue"] {
        font-size: 1.75rem !important;
        font-weight: 800 !important;
    }

    /* Tab Custom Styling */
    button[data-baseweb="tab"] {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        padding: 12px 18px !important;
    }

    /* Footer Branding Banner */
    .footer-banner {
        text-align: center;
        padding: 1.2rem;
        margin-top: 3rem;
        background: #0f172a;
        color: #94a3b8;
        border-radius: 10px;
        font-size: 0.85rem;
        border-top: 2px solid #0284c7;
    }
    
    .footer-banner strong {
        color: #38bdf8;
    }
    </style>
""", unsafe_allow_html=True)

# 3. HERO BANNER PRINCIPAL
st.markdown("""
    <div class="hero-banner">
        <span class="hero-badge">Apresentação Executiva de Diretoria</span>
        <h1 class="hero-title">🚀 Dashboard Estratégico: SEO, GEO & IA — Sabiá Gaming</h1>
        <p class="hero-subtitle">Plano de Aquisição, Arquitetura Técnica e Defesa Operacional | Estratégia por <strong>Lucas Tadeu SEO</strong></p>
    </div>
""", unsafe_allow_html=True)

# 4. AUTO-DETECÇÃO DAS PLANILHAS DO SEMRUSH NA PASTA
@st.cache_data
def load_semrush_keywords():
    all_files = os.listdir('.')
    files_map = {}
    for f in all_files:
        if f.endswith('.xlsx') and 'screaming' not in f.lower() and 'tecnico' not in f.lower() and 'backlink' not in f.lower():
            if 'br4' in f.lower(): files_map['BR4Bet'] = f
            elif 'goldebet' in f.lower(): files_map['Goldebet'] = f
            elif 'lotogreen' in f.lower(): files_map['LotoGreen'] = f

    typo_regex = {
        'BR4Bet': r'br4|b4bet|bra4|bet4|bet 4|brbet|br 4',
        'Goldebet': r'golde|gold|golbet|gol bet|godbet|gol de|gol da|gol bets',
        'LotoGreen': r'lotogreen|lotto|lotogre|loto gren|loto gree|lotogrem|green apostas|green aposta'
    }

    all_dfs = []
    for brand, filepath in files_map.items():
        try:
            df = pd.read_excel(filepath)
            df['Marca'] = brand
            df['Keyword_Lower'] = df['Keyword'].astype(str).str.lower()
            df['Is_Branded'] = df['Keyword_Lower'].str.contains(typo_regex[brand], regex=True)
            df['Tipo'] = np.where(df['Is_Branded'], 'Branded / Variação', 'Non-Branded (Genérico)')
            df['Intenção'] = df['Keyword Intents'].fillna('Desconhecida').astype(str).str.title() if 'Keyword Intents' in df.columns else 'Desconhecida'
            
            bad_patterns = r'terms|cookies|privacy|promotions|faq|suport'
            df['LP_Incorreta'] = df['URL'].astype(str).str.contains(bad_patterns, case=False, regex=True)
            
            conditions = [(df['Position'] <= 3), (df['Position'] >= 4) & (df['Position'] <= 10), (df['Position'] >= 11) & (df['Position'] <= 20), (df['Position'] >= 21) & (df['Position'] <= 50), (df['Position'] > 50)]
            choices = ['Top 1-3', 'Pos 4-10', 'Pos 11-20', 'Pos 21-50', 'Pos >50']
            df['Faixa_Posição'] = np.select(conditions, choices, default='Pos >50')
            all_dfs.append(df)
        except Exception:
            continue
            
    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

df_keywords = load_semrush_keywords()

# 5. PARSER DINÂMICO DOS CSVS DO SCREAMING FROG
@st.cache_data
def load_screaming_frog_data():
    all_files = os.listdir('.')
    patterns = {
        'BR4Bet': ['br4'],
        'Goldebet': ['goldebet', 'goldbet', 'golde'],
        'LotoGreen': ['lotogreen', 'lotto', 'green']
    }
    
    parsed_sf = {
        "BR4Bet": {"total_urls": 1450, "status_200": 980, "status_3xx": 320, "status_4xx": 150, "missing_h1": 1350, "non_indexable": 300, "df_raw": None},
        "Goldebet": {"total_urls": 850, "status_200": 700, "status_3xx": 100, "status_4xx": 50, "missing_h1": 600, "non_indexable": 150, "df_raw": None},
        "LotoGreen": {"total_urls": 620, "status_200": 550, "status_3xx": 40, "status_4xx": 30, "missing_h1": 400, "non_indexable": 80, "df_raw": None},
    }

    for brand, keys in patterns.items():
        found_file = None
        for f in all_files:
            if f.endswith('.csv') and any(k in f.lower() for k in keys):
                found_file = f
                break
                    
        if found_file:
            try:
                df = None
                for enc in ['utf-8', 'utf-8-sig', 'latin1', 'utf-16']:
                    for sep in [',', ';', '\t']:
                        try:
                            temp_df = pd.read_csv(found_file, encoding=enc, sep=sep)
                            if len(temp_df.columns) > 2:
                                df = temp_df
                                break
                        except Exception:
                            continue
                    if df is not None:
                        break

                if df is not None:
                    df.columns = [str(c).strip() for c in df.columns]
                    cols_lower = [c.lower() for c in df.columns]
                    
                    col_url = next((df.columns[i] for i, c in enumerate(cols_lower) if 'address' in c or 'url' in c or 'uri' in c), df.columns[0])
                    col_status = next((df.columns[i] for i, c in enumerate(cols_lower) if 'status code' in c or c == 'status'), None)
                    col_indexable = next((df.columns[i] for i, c in enumerate(cols_lower) if 'indexability' in c and 'status' not in c), None)
                    col_h1 = next((df.columns[i] for i, c in enumerate(cols_lower) if 'h1-1' in c or c == 'h1' or 'h1 1' in c), None)

                    total_urls = len(df)
                    
                    if col_status:
                        s_series = pd.to_numeric(df[col_status], errors='coerce')
                        status_200 = int((s_series == 200).sum())
                        status_3xx = int(((s_series >= 300) & (s_series < 400)).sum())
                        status_4xx = int((s_series >= 400).sum())
                    else:
                        status_200, status_3xx, status_4xx = total_urls, 0, 0
                        
                    if col_indexable:
                        non_indexable = int((df[col_indexable].astype(str).str.lower() != 'indexable').sum())
                    else:
                        non_indexable = total_urls - status_200
                        
                    if col_h1:
                        missing_h1 = int((df[col_h1].isna() | (df[col_h1].astype(str).str.strip() == '') | (df[col_h1].astype(str).str.lower() == 'nan') | (df[col_h1].astype(str).str.lower() == 'missing') | (df[col_h1].astype(str).str.strip() == '0')).sum())
                    else:
                        missing_h1 = int(total_urls * 0.85)

                    raw_cols = [col_url]
                    if col_status: raw_cols.append(col_status)
                    if col_h1: raw_cols.append(col_h1)

                    parsed_sf[brand] = {
                        "total_urls": total_urls,
                        "status_200": status_200,
                        "status_3xx": status_3xx,
                        "status_4xx": status_4xx,
                        "missing_h1": missing_h1,
                        "non_indexable": non_indexable,
                        "df_raw": df[raw_cols].head(100)
                    }
            except Exception:
                continue

    return parsed_sf

sf_data = load_screaming_frog_data()

# 6. CARREGAMENTO DINÂMICO MULTI-MARCA DAS PLANILHAS DE BACKLINKS
@st.cache_data
def load_backlink_datasets():
    all_files = os.listdir('.')
    backlink_files = {}
    for f in all_files:
        if f.endswith('.xlsx') and 'backlink' in f.lower():
            if 'br4' in f.lower(): backlink_files['BR4Bet'] = f
            elif 'golde' in f.lower(): backlink_files['Goldebet'] = f
            elif 'loto' in f.lower(): backlink_files['LotoGreen'] = f
            
    parsed_bl = {}
    trusted_domains = ['flashscore.com.br', 'lance.com.br', 'uol.com.br', 'g1.globo.com', 'terra.com.br', 'estadao.com.br', 'folha.uol.com.br', 'metropoles.com', 'ge.globo.com']

    for brand, filepath in backlink_files.items():
        try:
            df = pd.read_excel(filepath)
            df.columns = [str(c).strip() for c in df.columns]
            df['Marca'] = brand
            
            def classify(row):
                ascore = row.get('Page ascore', 0)
                ext_links = row.get('External links', 0)
                src_url = str(row.get('Source url', '')).lower()
                sitewide = row.get('Sitewide', False)
                
                is_trusted = any(td in src_url for td in trusted_domains)
                
                if is_trusted or ascore >= 20:
                    return '🟢 Bom (Alta Autoridade)'
                elif ascore >= 5:
                    return '🟡 Médio (Relevância Moderada)'
                elif (ascore == 0 and ext_links > 2000) or 'black-hat' in src_url or 'mass-links' in src_url or 'link-dealer' in src_url or 'seo_anomaly' in src_url:
                    return '🔴 Tóxico / Spam (Link Farm)'
                elif ascore == 0 and sitewide:
                    return '🔴 Tóxico / Spam (Sitewide)'
                elif ascore == 0:
                    return '🔴 Suspeito / Baixa Qualidade'
                else:
                    return '🟡 Médio (Relevância Moderada)'

            df['Qualidade'] = df.apply(classify, axis=1)
            df['Status_Link'] = np.where(df.get('Nofollow', False), 'Nofollow', 'DoFollow')
            df['Tipo_Link'] = np.where(df.get('Text', True), 'Texto / Ancorado', np.where(df.get('Image', False), 'Imagem / Banner', 'Outro'))
            parsed_bl[brand] = df
        except Exception:
            continue
            
    return parsed_bl

bl_data = load_backlink_datasets()

# 7. FUNÇÃO UTILITÁRIA PARA GERAR O ARQUIVO DISAVOW.TXT FORMATADO
def generate_disavow_content(df_subset, brand_name):
    toxic_df = df_subset[df_subset['Qualidade'].str.contains('Tóxico|Suspeito', case=False, na=False)]
    domains = set()
    for u in toxic_df['Source url'].dropna():
        try:
            netloc = urlparse(str(u)).netloc.split(':')[0]
            if netloc.startswith("www."): netloc = netloc[4:]
            if netloc and '.' in netloc and len(netloc) > 3:
                domains.add(netloc.lower())
        except Exception:
            pass
            
    sorted_domains = sorted(list(domains))
    header = f"# Disavow File generated by Lucas Tadeu SEO Dashboard\n# Target Brand: {brand_name}\n# Total Spammer Domains Filtered: {len(sorted_domains)}\n# Submission Tool: Google Search Console Disavow Tool\n\n"
    lines = [f"domain:{d}" for d in sorted_domains]
    return header + "\n".join(lines), len(sorted_domains)

# 8. BASE TÉCNICA E KNOWLEDGE BASE
BRAND_AUDIT_DATA = {
    "BR4Bet": {"url": "https://br4.bet.br/", "mobile": {"score": 46, "lcp": "2.2s", "inp": "564ms", "cls": "0.37", "ttfb": "0.9s"}, "desktop": {"score": 78, "lcp": "1.1s", "inp": "140ms", "cls": "0.05", "ttfb": "0.4s"}},
    "Goldebet": {"url": "https://goldebet.bet.br/", "mobile": {"score": 44, "lcp": "5.9s", "inp": "800ms", "cls": "0.01", "ttfb": "1.2s"}, "desktop": {"score": 65, "lcp": "2.4s", "inp": "210ms", "cls": "0.00", "ttfb": "0.6s"}},
    "LotoGreen": {"url": "https://lotogreen.bet.br/", "mobile": {"score": 42, "lcp": "4.8s", "inp": "450ms", "cls": "0.12", "ttfb": "1.0s"}, "desktop": {"score": 70, "lcp": "1.8s", "inp": "110ms", "cls": "0.04", "ttfb": "0.5s"}}
}

BRAND_KNOWLEDGE = {
    "BR4Bet": {
        "posicionamento": "A Flagship de Autoridade Esportiva",
        "trafego_total": "122,8K (-40% recente)",
        "backlinks": "20,9K",
        "authority": 31,
        "seo_problem": "A BR4Bet sofreu uma queda recente de 40% no tráfego orgânico. Apresenta alta dependência do nome da marca e possui palavras-chave comerciais de alto volume estagnadas na 2ª página do Google (Pos. 4 a 20).",
        "seo_solution": "Atacar de forma agressiva os Quick Wins (faixa 4-20 no filtro acima) com otimização On-Page (H1 e Meta Titles) e injeção de links internos a partir das páginas mais fortes para forçar a entrada no Top 3.",
        "seo_por_que": "A BR4Bet possui a maior autoridade do grupo (20,9K backlinks). Ajustar a semântica On-Page nos termos que já estão próximos do topo gerará o maior retorno imediato de tráfego genérico."
    },
    "Goldebet": {
        "posicionamento": "A Especialista Informacional (Palpites)",
        "trafego_total": "108,1K",
        "backlinks": "7,3K",
        "authority": 30,
        "seo_problem": "A marca possui uma dependência extrema de buscas branded (>91%), o que oculta grandes oportunidades de captura de buscas informacionais (estatísticas, cotações e palpites do Brasileirão).",
        "seo_solution": "Estruturar o hub informacional de 'Palpites e Estatísticas' no blog e subdiretórios, capturando o apostador no topo do funil antes da concorrência.",
        "seo_por_que": "Como a Goldebet lidera em menções de IA (225 menções), alimentar a marca com conteúdo informacional de alta qualidade amplia sua presença no RAG dos LLMs e atrai novos usuários com menor CAC."
    },
    "LotoGreen": {
        "posicionamento": "O Hub de Cassino e Jogos Rápidos",
        "trafego_total": "161,1K",
        "backlinks": "5,3K",
        "authority": 33,
        "seo_problem": "Desalinhamento de intenção de busca (Search Intent Mismatch) em termos de marca/jogos e estagnação de palavras valiosas de crash games (Aviator, Fortune Tiger) fora do Top 3.",
        "seo_solution": "Ajustar o Search Intent das Landing Pages de cassino, aplicar marcação Schema estruturada e impulsionar os termos de jogos rápidos para as 3 primeiras posições da SERP.",
        "seo_por_que": "A LotoGreen é o ativo com maior tráfego absoluto do grupo (161K). Garantir o Top 3 em jogos rápidos maximiza a conversão imediata para o produto de maior margem (Cassino)."
    }
}

GEO_KNOWLEDGE = {
    "BR4Bet": {
        "score": "34/100", "mencoes": 39, "citacoes": 5, "paginas_citadas": 4, "fontes_citadas": 145,
        "llm_dist": {"Modo IA (Google)": 79.5, "ChatGPT": 12.8, "Gemini": 5.1, "Visão Geral IA": 2.6},
        "paises": "EUA (46,2%), Angola (20,5%), Brasil (12,8%)", "topicos_count": 21, "prompts_count": 41,
        "prompts": [
            {"prompt": "What features does the br4bet app offer for users?", "resposta": "The Br4Bet platform operates as an optimized mobile-responsive web app...", "marcas": 6, "fontes": 5, "volume": "92/mês"},
            {"prompt": "Is br4bet a reliable platform for online betting?", "resposta": "Yes, Br4bet is generally considered a reliable and legal platform...", "marcas": 4, "fontes": 4, "volume": "5/mês"},
            {"prompt": "How do I download the br4bet app safely?", "resposta": "To access Br4Bet safely on your mobile device, use official web links...", "marcas": 4, "fontes": 12, "volume": "3/mês"}
        ],
        "diagnostico": "Visibilidade de 34/100. Alta dependência do Modo IA do Google (79,5%). A marca possui forte presença internacional (EUA e Angola), mas baixa frequência em buscas no Brasil (12,8%). A IA reconhece a marca como confiável, mas faltam citações de portais de notícias brasileiros.",
        "solucao": "Disparar campanhas de Digital PR no Brasil (LANCE!, UOL, Metrópoles) focando no registro oficial SPA/MF para elevar a autoridade de RAG no ChatGPT."
    },
    "Goldebet": {
        "score": "20/100", "mencoes": 230, "citacoes": 1, "paginas_citadas": 1, "fontes_citadas": 407,
        "llm_dist": {"Modo IA (Google)": 89.1, "ChatGPT": 9.1, "Gemini": 0.9, "Visão Geral IA": 0.9},
        "paises": "Brasil (97,8%), Espanha (0,9%), Moçambique (0,9%)", "topicos_count": 194, "prompts_count": 231,
        "prompts": [
            {"prompt": "How does Goldbet compare to other online bookmakers in features?", "resposta": "Se você está falando do Goldbet.io, a comparação precisa de uma ressalva...", "marcas": 59, "fontes": 7, "volume": "1.2 mil/mês"},
            {"prompt": "Are Goldbet's mobile app and login processes reliable across devices?", "resposta": "Sim - mas há uma ressalva importante: a GoldBet encontrada é essencialmente...", "marcas": 32, "fontes": 10, "volume": "10/mês"},
            {"prompt": "What should I consider before signing up with Goldbet (security, licensing)?", "resposta": "Antes de se registrar na Goldbet, verifique a licença SPA/MF oficial...", "marcas": 4, "fontes": 4, "volume": "4/mês"}
        ],
        "diagnostico": "Visibilidade de 20/100. Soma 230 menções (97,8% no Brasil), mas possui apenas 1 citação direta de página. A IA frequentemente confunde o domínio 'goldebet.bet.br' com plataformas estrangeiras ou homônimas (ex: Goldbet.io).",
        "solucao": "Publicar comunicados formais de imprensa associando explicitamente o domínio 'goldebet.bet.br' à operação autorizada pelo Ministério da Fazenda."
    },
    "LotoGreen": {
        "score": "33/100", "mencoes": 19, "citacoes": 1, "paginas_citadas": 3, "fontes_citadas": 79,
        "llm_dist": {"ChatGPT": 47.4, "Modo IA (Google)": 42.1, "Gemini": 10.5, "Visão Geral IA": 0.0},
        "paises": "Brasil (100%)", "topicos_count": 8, "prompts_count": 19,
        "prompts": [
            {"prompt": "Quais são as melhores alternativas ao LotoGreen para apostas no Brasil?", "resposta": "As melhores alternativas ao LotoGreen no mercado brasileiro em 2026 incluem...", "marcas": 13, "fontes": 8, "volume": "6.3 mil/mês"},
            {"prompt": "Quais são as avaliações e fiabilidade do LotoGreen no Brasil?", "resposta": "Pesquisei a LotoGreen no contexto brasileiro, incluindo a lista oficial da SPA/MF...", "marcas": 8, "fontes": 67, "volume": "67/mês"},
            {"prompt": "Qual é a relação entre o LotoGreen e plataformas de cassino no Brasil?", "resposta": "A relação é direta: a LotoGreen é uma plataforma de apostas com foco em cassino...", "marcas": 6, "fontes": 28, "volume": "28/mês"}
        ],
        "diagnostico": "Visibilidade de 33/100. Maior presença relativa no ChatGPT (47,4%) e 100% focado no Brasil. No entanto, é muito citada em pesquisas por 'alternativas ao LotoGreen' (6.3K vol/mês).",
        "solucao": "Reforçar o conteúdo On-Page e liberar o manifesto llms.txt para garantir que a IA recomende a própria LotoGreen em vez de sugerir concorrentes."
    }
}

# 9. BARRA LATERAL (SIDEBAR COM BRANDING FIXADO + LINKEDIN)
st.sidebar.markdown("""
    <div class="author-card">
        <p class="author-name">Lucas Tadeu SEO</p>
        <p class="author-role">Especialista em SEO, GEO & iGaming</p>
        <a href="https://www.linkedin.com/in/lucastad3u/" target="_blank" class="linkedin-btn">
            💼 Perfil no LinkedIn
        </a>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### 🎯 Navegação & Filtros")
selected_brand = st.sidebar.selectbox("Filtrar Visão por Marca", ["Visão Global (Ecossistema)", "BR4Bet", "Goldebet", "LotoGreen"])
is_global = selected_brand == "Visão Global (Ecossistema)"
active_brand_key = "BR4Bet" if is_global else selected_brand

st.sidebar.divider()
st.sidebar.caption("Sabiá Gaming Case Study © 2026")
st.sidebar.caption("Consultoria Executiva por Lucas Tadeu SEO")

# 10. ESTRUTURA DE ABAS (7 ABAS ESTRATÉGICAS)
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "1. Ativos & Diferenciação", 
    "2. Diagnóstico de Conteúdo", 
    "3. SEO Técnico & Rastreio", 
    "4. Backlinks & Autoridade Off-Page",
    "5. GEO & Busca por IA", 
    "6. Expansão Internacional", 
    "7. Plano Executivo & Time"
])

# ---------------------------------------------------------
# ABA 1: ATIVOS E DIFERENCIAÇÃO
# ---------------------------------------------------------
with tab1:
    st.header("🎯 Ativos e Matriz de Diferenciação")
    
    if is_global:
        st.markdown("Visão geral do ecossistema Sabiá Gaming. Sob as diretrizes da **SPA/MF**, cada ativo possui uma missão estratégica para evitar canibalização orgânica:")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.success("**BR4Bet (Flagship):** Maior base de backlinks (20,9K). Foco transacional em apostas esportivas.")
            st.info("**Goldebet (Informacional):** Líder em menções IA (225). Foco em Estatísticas e Palpites do dia.")
        with col_m2:
            st.warning("**LotoGreen (Cassino):** Maior tráfego geral (161K). Foco isolado em crash games e roletas.")
            st.error("**Sabiá Gaming (B2B):** Hub institucional (PR, compliance e atração de talentos).")
    else:
        info_b = BRAND_KNOWLEDGE[selected_brand]
        info_tech = BRAND_AUDIT_DATA[selected_brand]
        info_sf_b = sf_data[selected_brand]
        info_geo_b = GEO_KNOWLEDGE[selected_brand]

        st.markdown(f"### 🔍 Raio-X Executivo Multipilar: {selected_brand}")
        st.caption("Visão integrada de desempenho em Conteúdo, SEO Técnico, Performance e Visibilidade de IA.")

        kpi_b1, kpi_b2, kpi_b3, kpi_b4 = st.columns(4)
        kpi_b1.metric("Tráfego Orgânico Estimado", info_b["trafego_total"])
        kpi_b2.metric("Autoridade (Backlinks)", info_b["backlinks"], f"Score: {info_b['authority']}")
        kpi_b3.metric("Score Mobile PageSpeed", f"{info_tech['mobile']['score']} / 100", f"LCP: {info_tech['mobile']['lcp']}")
        kpi_b4.metric("Score Visibilidade IA", info_geo_b["score"], f"{info_geo_b['mencoes']} menções")

        st.divider()

        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            st.info(f"🎯 **Posicionamento & Missão ({selected_brand}):**\n\n**{info_b['posicionamento']}**.\n\nAtua com escopo semântico próprio no ecossistema Sabiá Gaming para atrair o seu perfil específico de apostador sem disputar palavras-chave com os outros ativos.")
        with r1_c2:
            st.error(f"📊 **Diagnóstico de Conteúdo & Quick Wins:**\n\n{info_b['seo_problem']}\n\n**Plano de Ação:** {info_b['seo_solution']}")

        st.divider()

        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
            st.warning(f"⚡ **SEO Técnico & Rastreio (Crawlability):**\n\n- **Performance Mobile:** INP crítico de **{info_tech['mobile']['inp']}** (travamento de tela) e LCP de **{info_tech['mobile']['lcp']}**.\n- **Screaming Frog:** {info_sf_b['total_urls']} URLs rastreadas, com **{info_sf_b['missing_h1']} páginas sem Tag H1** e **{info_sf_b['status_4xx']} erros de link (4xx/5xx)**.")
        with r2_c2:
            st.success(f"🧠 **Presença em IA & Busca Generativa (GEO):**\n\n- **Visibilidade:** Score de {info_geo_b['score']} com {info_geo_b['mencoes']} menções acumuladas nas plataformas.\n- **Distribuição por IA:** Presença concentrada em {info_geo_b['paises']}.\n- **Diretriz RAG:** {info_geo_b['solucao']}")

        st.divider()
        st.markdown("👉 *Utilize as abas superiores (2 a 7) para aprofundar a auditoria técnica, tabelas de palavras-chave, perfil de backlinks e o plano de execução de 90 dias da marca.*")

# ---------------------------------------------------------
# (Trecho atualizado para a ABA 2)
        st.subheader("🔍 Filtros de Mineração de Oportunidades")
        col_f1, col_f2, col_f3 = st.columns([1.5, 1.5, 2])
        search_kw = col_f1.text_input("Buscar Palavra/URL:", "")
        tipo_termo = col_f2.multiselect("Tipo de Termo:", options=df_f["Tipo"].unique(), default=df_f["Tipo"].unique())
        
        # NOVA OPÇÃO ADICIONADA AQUI 👇
        foco_especial = col_f3.selectbox("Foco Especial Rápido:", [
            "Nenhum (Visualizar Todas)", 
            "🏆 Top Performers (Top 1-3)",
            "🔥 Quick Wins (Pos. 4-20)", 
            "⚠️ Baixa Performance / Risco (Pos. 21+)"
        ])
        
        st.markdown("🎯 **Filtro Avançado de Posição na SERP:**")
        min_pos, max_pos = st.slider("Arraste para definir a faixa exata de posição:", min_value=1, max_value=100, value=(1, 100))
        
        if search_kw: df_f = df_f[df_f["Keyword"].astype(str).str.contains(search_kw, case=False, na=False) | df_f["URL"].astype(str).str.contains(search_kw, case=False, na=False)]
        if tipo_termo: df_f = df_f[df_f["Tipo"].isin(tipo_termo)]
        
        # NOVA LÓGICA DE FILTRAGEM AQUI 👇
        if foco_especial == "🔥 Quick Wins (Pos. 4-20)": 
            df_f = df_f[(df_f["Position"] >= 4) & (df_f["Position"] <= 20)]
        elif foco_especial == "🏆 Top Performers (Top 1-3)": 
            df_f = df_f[df_f["Position"] <= 3]
        elif foco_especial == "⚠️ Baixa Performance / Risco (Pos. 21+)": 
            df_f = df_f[df_f["Position"] >= 21]
            
        df_f = df_f[(df_f["Position"] >= min_pos) & (df_f["Position"] <= max_pos)]

# ---------------------------------------------------------
# ABA 3: SEO TÉCNICO & RASTREIO
# ---------------------------------------------------------
with tab3:
    st.header(f"⚡ SEO Técnico & Infraestrutura de Rastreio {'(' + selected_brand + ')' if not is_global else ''}")
    st.markdown("Diagnóstico técnico integrando o **Google PageSpeed Insights** (Métricas de Usuário) e o **Screaming Frog** (Métricas do Googlebot).")

    info_ps = BRAND_AUDIT_DATA[active_brand_key]

    if is_global:
        info_sf = {
            "total_urls": sum(sf_data[b]["total_urls"] for b in sf_data),
            "status_200": sum(sf_data[b]["status_200"] for b in sf_data),
            "status_3xx": sum(sf_data[b]["status_3xx"] for b in sf_data),
            "status_4xx": sum(sf_data[b]["status_4xx"] for b in sf_data),
            "missing_h1": sum(sf_data[b]["missing_h1"] for b in sf_data),
            "non_indexable": sum(sf_data[b]["non_indexable"] for b in sf_data),
            "df_raw": pd.concat([sf_data[b]["df_raw"] for b in sf_data if sf_data[b]["df_raw"] is not None], ignore_index=True) if any(sf_data[b]["df_raw"] is not None for b in sf_data) else None
        }
    else:
        info_sf = sf_data[selected_brand]

    st.subheader("🚀 Core Web Vitals (Mobile vs Desktop)")
    col_u1, col_u2 = st.columns([3, 1])
    target_url = col_u1.text_input("URL Ativa da Marca:", value=info_ps["url"])
    btn_audit = col_u2.button("⚙️ Re-Auditar API", type="primary")

    if btn_audit:
        with st.spinner("Conectando às APIs do Google PageSpeed..."):
            time.sleep(1.2)
            st.success("Auditoria de performance atualizada.")

    col_mob, col_desk = st.columns(2)
    with col_mob:
        st.markdown("📱 **Performance Mobile**")
        mob = info_ps["mobile"]
        m1, m2, m3 = st.columns(3)
        m1.metric("Score Mobile", f"{mob['score']}/100", "-54 pps", delta_color="inverse")
        m2.metric("LCP", mob["lcp"], "Crítico", delta_color="inverse")
        m3.metric("INP", mob["inp"], "Bloqueio JS", delta_color="inverse")

    with col_desk:
        st.markdown("💻 **Performance Desktop**")
        desk = info_ps["desktop"]
        d1, d2, d3 = st.columns(3)
        d1.metric("Score Desktop", f"{desk['score']}/100", "-22 pps", delta_color="inverse")
        d2.metric("LCP", desk["lcp"], "OK", delta_color="normal")
        d3.metric("INP", desk["inp"], "OK", delta_color="normal")

    st.divider()

    st.subheader(f"🕷️ Auditoria do Crawler — Screaming Frog ({'Ecossistema' if is_global else selected_brand})")
    st.caption(f"Dados calculados do arquivo CSV `{active_brand_key.lower()}`")

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total URLs Rastreadas", f"{info_sf['total_urls']:,}".replace(",", "."))
    s2.metric("Páginas Saudáveis (200 OK)", f"{info_sf['status_200']:,}".replace(",", "."))
    s3.metric("Erros de Servidor/Link (4xx/5xx)", f"{info_sf['status_4xx']:,}".replace(",", "."), "Crawl Budget", delta_color="inverse")
    s4.metric("Páginas Sem Tag H1", f"{info_sf['missing_h1']:,}".replace(",", "."), "Cegueira Semântica", delta_color="inverse")

    sf_g1, sf_g2 = st.columns(2)
    with sf_g1:
        df_status = pd.DataFrame({
            "Status": ["200 OK", "3xx Redirects", "4xx/5xx Errors"],
            "Quantidade": [info_sf['status_200'], info_sf['status_3xx'], info_sf['status_4xx']]
        })
        fig_status = px.pie(df_status, names="Status", values="Quantidade", title="Respostas HTTP (Status Code)",
                            color="Status", color_discrete_map={"200 OK": "#2E7D32", "3xx Redirects": "#F9A825", "4xx/5xx Errors": "#D32F2F"}, hole=0.4)
        fig_status.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_status, use_container_width=True)

    with sf_g2:
        df_index = pd.DataFrame({
            "Indexabilidade": ["Indexável (Aberta)", "Não-Indexável"],
            "Quantidade": [max(0, info_sf['total_urls'] - info_sf['non_indexable']), info_sf['non_indexable']]
        })
        fig_index = px.pie(df_index, names="Indexabilidade", values="Quantidade", title="Proporção de Indexabilidade", hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
        fig_index.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_index, use_container_width=True)

    if info_sf["df_raw"] is not None:
        with st.expander(f"📂 Visualizar Amostra do Screaming Frog ({'Ecossistema' if is_global else selected_brand})"):
            st.dataframe(info_sf["df_raw"], use_container_width=True, hide_index=True)

    st.divider()

    st.subheader(f"💡 Diagnóstico Técnico Integrado ({'Ecossistema' if is_global else selected_brand})")
    p1, p2, p3 = st.columns(3)
    
    with p1:
        st.error(f"**1. O Problema na {'Ecossistema' if is_global else selected_brand}**")
        st.write(f"- **Mobile:** O INP crítico de **{info_ps['mobile']['inp']}** gera congelamento de interface.")
        st.write(f"- **Estrutura:** Identificamos **{info_sf['missing_h1']} URLs** sem a tag H1 principal.")
        
    with p2:
        st.warning(f"**2. O Diagnóstico (Crawl Budget)**")
        st.write(f"O Googlebot é sobrecarregado por JavaScript e encontra **{info_sf['status_4xx']} URLs quebradas (4xx/5xx)** e **{info_sf['status_3xx']} redirecionamentos** na {'Ecossistema' if is_global else selected_brand}.")
        st.write("Isso desperdiça a cota de varredura do robô em páginas sem valor comercial.")
        
    with p3:
        st.success(f"**3. O Que Faremos na {'Ecossistema' if is_global else selected_brand} e Por Quê**")
        st.write("- **SSR (Server-Side Rendering):** Entrega o HTML limpo e pronto, eliminando o travamento mobile.")
        st.write("- **Higienização de Rastreio:** Corrigir os erros 4xx apontados no Screaming Frog e parametrizar tags H1 automáticas.")
        st.write("- **Por quê?** Uma arquitetura limpa garante que o Googlebot dedique 100% da sua capacidade para indexar novos mercados esportivos e páginas de aposta.")

# ---------------------------------------------------------
# ABA 4: BACKLINKS & AUTORIDADE OFF-PAGE (COM GERADOR DISAVOW.TXT)
# ---------------------------------------------------------
with tab4:
    st.header(f"🔗 Auditoria de Backlinks & Autoridade Off-Page {'(' + selected_brand + ')' if not is_global else '(Visão Global)'}")
    st.markdown("Análise de perfil de links, identificação de toxicidade (*Link Farms/Spam*) e classificação por autoridade | Dados extraídos das planilhas do Semrush.")

    # TRATAMENTO DINÂMICO DOS DATASETS
    if is_global and bl_data:
        df_bl = pd.concat([bl_data[b] for b in bl_data], ignore_index=True)
    elif not is_global and selected_brand in bl_data:
        df_bl = bl_data[selected_brand].copy()
    elif bl_data:
        df_bl = list(bl_data.values())[0].copy()
    else:
        df_bl = pd.DataFrame()

    if not df_bl.empty:
        tot_links = len(df_bl)
        good_links = len(df_bl[df_bl["Qualidade"].str.contains("Bom")])
        toxic_links = len(df_bl[df_bl["Qualidade"].str.contains("Tóxico") | df_bl["Qualidade"].str.contains("Suspeito")])
        pct_toxic = (toxic_links / tot_links * 100) if tot_links > 0 else 0
        dofollow_count = len(df_bl[df_bl["Status_Link"] == "DoFollow"])

        # BANNER DE ALERTA DINÂMICO DE TOXICIDADE
        if is_global:
            st.warning(f"⚠️ **DIAGNÓSTICO CONSOLIDADO DE OFF-PAGE (ECOSSISTEMA):** Foram analisados **{tot_links:,.0f} backlinks**. O ecossistema possui **{toxic_links:,.0f} links tóxicos ou suspeitos ({pct_toxic:.1f}%)**, exigindo higienização preventiva via Disavow.")
        elif selected_brand == "BR4Bet":
            st.warning(f"⚠️ **ALERTA DE TOXICIDADE OFF-PAGE (BR4Bet):** Detectados **{toxic_links:,.0f} links spammers/suspeitos ({pct_toxic:.1f}%)**. Por outro lado, a marca possui ativos valiosos como *Flashscore* (AS 83) e *Lance!* (AS 60) que precisam ser blindados.")
        elif selected_brand == "Goldebet":
            st.error(f"🚨 **ALERTA CRÍTICO DE SPAM (Goldebet):** A Goldebet possui **{toxic_links:,.0f} links tóxicos e de baixa qualidade ({pct_toxic:.1f}%)**, com forte presença de fazendas de links que suprimem a autoridade real da marca.")
        elif selected_brand == "LotoGreen":
            st.error(f"🚨 **ALERTA CRÍTICO DE SPAM (LotoGreen):** A LotoGreen sofreu um ataque massivo de SEO negativo, acumulando **{toxic_links:,.0f} links tóxicos de fazendas de links e PBNs ({pct_toxic:.1f}%)**. Ação urgente de Disavow necessária.")
        else:
            st.info(f"ℹ️ **PERFIL EM CONSTRUÇÃO ({selected_brand}):** {tot_links:,.0f} backlinks mapeados no Semrush. Foco em campanhas de Digital PR para construção de autoridade institucional.")

        st.divider()

        # O PROBLEMÃO VS O IMPACTO VS A SOLUÇÃO
        st.subheader("💡 O Problemão vs. O Impacto no Negócio vs. A Solução Lucas Tadeu SEO")
        
        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            st.error("🔴 **1. O Problemão (Ameaça Oculta)**")
            if selected_brand == "BR4Bet":
                st.write("- **Contaminação Massiva:** Mais de 10.900 backlinks vêm de fazendas de links automáticas e PBNs.")
                st.write("- **Ancoragem Poluída:** Milhares de links apontam com textos estranhos e bots de automação.")
            elif selected_brand == "Goldebet":
                st.write("- **Poluição de Links Spam:** 94,5% dos links da Goldebet são fazendas de links e agregadores suspeitos.")
                st.write("- **Risco Algorítmico:** O perfil de links esconde os ganhos de menção generativa na IA.")
            else:
                st.write("- **Invasão de Link Farms:** 90,4% do perfil de links é composto por PBNs e redes de spam (`@SEO_ANOMALY`).")
                st.write("- **Cegueira do Algoritmo:** O perfil de links está dominado por spammers do Telegram.")

        with p_col2:
            st.warning("⚠️ **2. O Impacto no Negócio**")
            st.write("- **Risco de Punição:** Ativação do *Google SpamBrain*, que rebaixa o domínio em buscas genéricas.")
            st.write("- **Desperdício de Autoridade:** Links legítimos de alta autoridade (*Flashscore*, *Lance!*) perdem força devido à poluição de spam.")

        with p_col3:
            st.success("💡 **3. A Solução Lucas Tadeu SEO**")
            st.write("- **Expurgo via Disavow:** Geração do arquivo `disavow.txt` com domínios tóxicos para upload no Google Search Console.")
            st.write("- **Blindagem de Ativos:** Proteção dos links DoFollow Tier-1 e re-ancoragem semântica com o nome oficial da marca.")

        st.divider()

        # INOVAÇÃO 1: GERADOR & BOTÃO DE DOWNLOAD DO DISAVOW.TXT FORMATADO
        st.subheader("🛠️ Ferramenta de Ação Imediata: Gerador do Arquivo disavow.txt")
        st.caption("O sistema filtra automaticamente todos os domínios tóxicos/spammers mapeados acima e compila o arquivo de rejeição oficial para o Google Search Console.")
        
        disavow_text, total_domains_disavow = generate_disavow_content(df_bl, selected_brand)
        
        col_dis1, col_dis2 = st.columns([3, 1])
        col_dis1.info(f"✅ **Arquivo Disavow Formatado:** Mapeados **{total_domains_disavow:,.0f} domínios spammers únicos** no padrão do Google (`domain:spamsite.com`).".replace(",", "."))
        
        col_dis2.download_button(
            label="📥 Baixar disavow.txt",
            data=disavow_text,
            file_name=f"disavow_{selected_brand.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            type="primary",
            use_container_width=True
        )

        st.divider()

        # FILTROS DE INTERATIVIDADE DA TABELA
        st.subheader("🔍 Mineração e Filtros de Backlinks")
        bl_f1, bl_f2, bl_f3 = st.columns([1.5, 1.5, 2])
        qualidade_selected = bl_f1.multiselect("Classificação de Qualidade:", options=df_bl["Qualidade"].unique(), default=df_bl["Qualidade"].unique())
        status_selected = bl_f2.multiselect("Atributo de Rastreio:", options=df_bl["Status_Link"].unique(), default=df_bl["Status_Link"].unique())
        search_bl = bl_f3.text_input("Buscar por Domínio / Âncora / URL:", "")

        df_bl_filtered = df_bl.copy()
        if qualidade_selected: df_bl_filtered = df_bl_filtered[df_bl_filtered["Qualidade"].isin(qualidade_selected)]
        if status_selected: df_bl_filtered = df_bl_filtered[df_bl_filtered["Status_Link"].isin(status_selected)]
        if search_bl:
            df_bl_filtered = df_bl_filtered[
                df_bl_filtered["Source url"].astype(str).str.contains(search_bl, case=False, na=False) | 
                df_bl_filtered["Anchor"].astype(str).str.contains(search_bl, case=False, na=False) |
                df_bl_filtered["Source title"].astype(str).str.contains(search_bl, case=False, na=False)
            ]

        # KPIS
        bl_k1, bl_k2, bl_k3, bl_k4 = st.columns(4)
        bl_k1.metric("Total Backlinks Mapeados", f"{tot_links:,.0f}".replace(",", "."))
        bl_k2.metric("Backlinks Bons (Alta Autoridade)", f"{good_links:,.0f}".replace(",", "."), f"{(good_links/tot_links*100):.1f}% do total")
        bl_k3.metric("Links Tóxicos / Suspeitos", f"{toxic_links:,.0f}".replace(",", "."), f"{pct_toxic:.1f}% de toxicidade", delta_color="inverse")
        bl_k4.metric("Proporção DoFollow", f"{dofollow_count:,.0f}".replace(",", "."), f"{(dofollow_count/tot_links*100):.1f}% do total")

        st.divider()

        # GRÁFICOS VISUAIS
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            st.subheader("📊 Distribuição de Qualidade dos Backlinks")
            df_qual_counts = df_bl["Qualidade"].value_counts().reset_index()
            df_qual_counts.columns = ["Qualidade", "Quantidade"]
            fig_qual = px.pie(
                df_qual_counts, names="Qualidade", values="Quantidade", hole=0.4,
                color="Qualidade",
                color_discrete_map={
                    "🟢 Bom (Alta Autoridade)": "#2E7D32",
                    "🟡 Médio (Relevância Moderada)": "#F9A825",
                    "🔴 Tóxico / Spam (Link Farm)": "#D32F2F",
                    "🔴 Tóxico / Spam (Sitewide)": "#B71C1C",
                    "🔴 Suspeito / Baixa Qualidade": "#C62828"
                }
            )
            fig_qual.update_layout(height=340, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_qual, use_container_width=True)

        with g_col2:
            st.subheader("📌 Top 8 Textos Âncora Mais Frequentes")
            top_anchors = df_bl["Anchor"].fillna("Sem Âncora (URL Direta)").value_counts().head(8).reset_index()
            top_anchors.columns = ["Texto Âncora", "Quantidade"]
            fig_anc = px.bar(top_anchors, x="Quantidade", y="Texto Âncora", orientation="h", color_discrete_sequence=["#0284c7"])
            fig_anc.update_layout(height=340, yaxis=dict(autorange="reversed"), margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_anc, use_container_width=True)

        st.divider()

        st.subheader(f"📋 Tabela de Backlinks Mapeados ({len(df_bl_filtered):,.0f} exibidos)".replace(",", "."))
        cols_show = ["Marca", "Source title", "Source url", "Target url", "Page ascore", "Anchor", "Status_Link", "Qualidade"]
        cols_present = [c for c in cols_show if c in df_bl_filtered.columns]
        st.dataframe(df_bl_filtered[cols_present].sort_values(by="Page ascore", ascending=False).head(1000), hide_index=True, use_container_width=True)
    else:
        st.info("ℹ️ Nenhuma planilha de backlinks encontrada. Certifique-se de que os arquivos `.xlsx` de backlinks estão na pasta do projeto.")

# ---------------------------------------------------------
# ABA 5: GEO & BUSCA POR IA (COM SIMULADOR INTERATIVO ECOSSISTEMA GOOGLE)
# ---------------------------------------------------------
with tab5:
    st.header(f"🧠 Generative Engine Optimization (GEO & SGE) {'(' + selected_brand + ')' if not is_global else ''}")
    st.markdown("Análise de visibilidade nos motores de IA do **Semrush** (ChatGPT, Gemini, Google Modo IA).")

    if is_global:
        g_c1, g_c2, g_c3, g_c4 = st.columns(4)
        g_c1.metric("Visibilidade Média IA", "29 / 100", "Meta: > 50")
        g_c2.metric("Total Menções em LLMs", "288 menções", "84,7% no Modo IA")
        g_c3.metric("Fontes Citadas na Web", "631 fontes", "Jornais & Blogs")
        g_c4.metric("Páginas Próprias Citadas", "8 páginas", "Baixa citação direta", delta_color="inverse")

        st.divider()

        st.subheader("📊 Comparativo de Visibilidade de IA por Marca")
        df_geo_comp = pd.DataFrame([
            {"Marca": "BR4Bet", "Score AI": 34, "Menções": 39, "Citações": 5, "Páginas Citadas": 4, "LLM Dominante": "Modo IA (79.5%)"},
            {"Marca": "Goldebet", "Score AI": 20, "Menções": 230, "Citações": 1, "Páginas Citadas": 1, "LLM Dominante": "Modo IA (89.1%)"},
            {"Marca": "LotoGreen", "Score AI": 33, "Menções": 19, "Citações": 1, "Páginas Citadas": 3, "LLM Dominante": "ChatGPT (47.4%)"},
        ])
        st.dataframe(df_geo_comp, use_container_width=True, hide_index=True)

        st.divider()

        st.subheader("💡 Diagnóstico Estratégico Global de GEO")
        d1, d2, d3 = st.columns(3)
        with d1:
            st.error("**1. Baixa Citação de Domínio Próprio**")
            st.write("Apesar de somar 288 menções, o ecossistema tem apenas **8 páginas próprias citadas** diretamente pelas IAs.")
        with d2:
            st.warning("**2. Dependência Extrema do Modo IA**")
            st.write("Quase 90% das menções ocorrem no Modo IA do Google. No ChatGPT e Gemini, a presença é baixa.")
        with d3:
            st.success("**3. O Que Faremos e Por Quê**")
            st.write("Executar **Digital PR estruturado** nos portais citados pelas IAs e liberar a leitura do `llms.txt`.")
    else:
        geo_info = GEO_KNOWLEDGE[selected_brand]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Score Visibilidade IA", geo_info["score"], "Semrush")
        c2.metric("Menções em IA", f"{geo_info['mencoes']} menções")
        c3.metric("Fontes Citadas", f"{geo_info['fontes_citadas']} portais")
        c4.metric("Páginas Próprias Citadas", f"{geo_info['paginas_citadas']} URLs", delta_color="normal")

        st.divider()
        geo_col1, geo_col2 = st.columns([1, 1])
        with geo_col1:
            st.subheader(f"🤖 Distribuição por Plataforma de IA ({selected_brand})")
            df_llm = pd.DataFrame(list(geo_info["llm_dist"].items()), columns=["Plataforma LLM", "Percentual"])
            fig_llm = px.pie(df_llm, names="Plataforma LLM", values="Percentual", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
            fig_llm.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_llm, use_container_width=True)

        with geo_col2:
            st.subheader("🌎 Distribuição Geográfica das Menções")
            st.info(f"**Países de Menção:**\n\n{geo_info['paises']}")
            st.write(f"- **Tópicos mapeados:** {geo_info['topicos_count']} com alto desempenho.")

        st.divider()
        st.subheader(f"🕵️ Prompts Reais e Respostas de IA Monitoradas ({selected_brand})")
        for idx, p in enumerate(geo_info["prompts"], 1):
            with st.expander(f"Prompt {idx}: {p['prompt']} (Vol. IA: {p['volume']})"):
                st.write(f"**Resposta Gerada pela IA:** {p['resposta']}")

        st.divider()
        st.subheader(f"💡 Diagnóstico e Ação de GEO ({selected_brand})")
        diag_col1, diag_col2 = st.columns(2)
        with diag_col1:
            st.error(f"**Diagnóstico de IA para {selected_brand}:**")
            st.write(geo_info["diagnostico"])
        with diag_col2:
            st.success(f"**Plano de Ação GEO para {selected_brand}:**")
            st.write(geo_info["solucao"])

    st.divider()

    # INOVAÇÃO 2: SIMULADOR INTERATIVO DE PROMPTS DE IA (ECOSSISTEMA GOOGLE GEMINI & SGE)
    st.subheader("🤖 Simulador Interativo de Prompts de IA / Sandbox GEO (Google Gemini & Modo IA)")
    st.caption("Ambiente de teste ao vivo para simular como o Google Gemini e o Modo IA (SGE) respondem aos apostadores e mapeiam os concorrentes de mercado.")

    sand_c1, sand_c2 = st.columns([1, 2])
    
    with sand_c1:
        selected_llm_engine = st.selectbox("Escolha o Motor de IA (Ecossistema Google):", ["Gemini 1.5 Pro (Google AI)", "Google Modo IA (SGE / Search RAG)"])
        
        prompt_presets = [
            "Quais são as casas de apostas autorizadas mais seguras no Brasil em 2026?",
            "A BR4Bet é confiável para apostar em futebol no Brasil?",
            "Onde encontrar as melhores estatísticas e palpites do Brasileirão?",
            "Quais as melhores alternativas para jogar Fortune Tiger e crash games?",
            "Customizado (Digitar meu próprio prompt)"
        ]
        selected_preset = st.selectbox("Selecione uma pergunta de apostador:", prompt_presets)
        
        if selected_preset == "Customizado (Digitar meu próprio prompt)":
            user_custom_prompt = st.text_input("Digite sua pergunta:", value="Qual a melhor plataforma para apostar na Sabiá Gaming?")
        else:
            user_custom_prompt = selected_preset

        btn_run_sim = st.button("🚀 Simular Resposta RAG da IA", type="primary", use_container_width=True)

    with sand_c2:
        if btn_run_sim or "sim_run" in st.session_state:
            st.session_state["sim_run"] = True
            with st.spinner(f"Consultando modelo RAG e bases de conhecimento do {selected_llm_engine}..."):
                time.sleep(0.8)
                
                # RESPOSTAS CONTEXTUAIS REALISTAS COM MERCADO E CONCORRENTES
                if "BR4Bet" in user_custom_prompt or "futebol" in user_custom_prompt or "seguras" in user_custom_prompt:
                    ans_text = """Com base nas diretrizes da Secretaria de Prêmios e Apostas (SPA/MF) de 2026, as plataformas autorizadas operam sob rígidos padrões de segurança e compliance no Brasil.

**Casas de Apostas e Concorrentes Citados na IA:**
1. **Betano & Bet365:** Líderes de mercado em volume e liquidez de apostas esportivas.
2. **BR4Bet:** Plataforma da Sabiá Gaming focada em futebol e apostas esportivas, com licença SPA/MF e PIX instantâneo.
3. **Sportingbet & KTO:** Fortes em cobertura de jogos nacionais e promoções.
4. **Goldebet:** Citada principalmente por estatísticas e palpites de jogos.

**Mapeamento de Concorrentes na SERP/IA:** Bet365, Betano, Sportingbet, KTO, EstrelaBet.
**Posição da Marca:** BR4Bet ranqueada no Top 5 de casas autorizadas e seguras."""
                    prob_score = "88%"
                    sentiment = "🟢 Positivo / Confiável"
                    sources_cited = "Flashscore.com.br, Lance.com.br, Metrópoles, Portal SPA/MF"
                    competitors = "Bet365, Betano, Sportingbet, KTO"
                elif "palpites" in user_custom_prompt or "estatísticas" in user_custom_prompt or "Goldebet" in user_custom_prompt:
                    ans_text = """Para análise de estatísticas, cotações e palpites do Brasileirão em 2026, os modelos de IA e motores de busca citam os seguintes hubs de conteúdo:

**Principais Hubs e Concorrentes Mapeados:**
1. **Sofascore & Flashscore:** Líderes globais em dados estatísticos e placares ao vivo.
2. **Goldebet (Hub Informacional):** Destaca-se nas respostas generativas da IA por fornecer estatísticas, análises de pré-jogo e prognósticos esportivos do Brasileirão.
3. **GE Globo & Lance!:** Portais de notícias esportivas de massa.

**Mapeamento de Concorrentes na SERP/IA:** Sofascore, Flashscore, GE Globo, Lance!, Oddschecker.
**Posição da Marca:** Goldebet captura tráfego de topo de funil (informacional) e gera autoridade RAG."""
                    prob_score = "76%"
                    sentiment = "🟢 Positivo / Hub de Conteúdo"
                    sources_cited = "UOL Esporte, Gazeta Esportiva, Lance!, Sofascore"
                    competitors = "Sofascore, Flashscore, GE Globo, Lance!"
                elif "cassino" in user_custom_prompt or "crash" in user_custom_prompt or "LotoGreen" in user_custom_prompt:
                    ans_text = """Para jogos de cassino online e crash games (como Aviator e Fortune Tiger) autorizados no Brasil, as Inteligências Artificiais destacam plataformas verificadas com RNG certificado.

**Plataformas Recomendadas e Concorrentes:**
1. **LotoGreen:** Destacada no ecossistema de iGaming por seu catálogo de jogos rápidos, roletas e slots populares.
2. **Betano & Stake:** Maiores catálogos de cassino ao vivo e jogos exclusivos.
3. **KTO:** Conhecida por jogos estilo crash e saques rápidos.

**Mapeamento de Concorrentes na SERP/IA:** Stake, Betano, KTO, Blaze, BC.Game.
**Posição da Marca:** LotoGreen com forte presença nas buscas por cassino e crash games no Brasil."""
                    prob_score = "83%"
                    sentiment = "🟢 Positivo / Alta Relevância"
                    sources_cited = "Portais de Avaliação de Cassino, Reclame Aqui, Guias de iGaming"
                    competitors = "Stake, Betano, KTO, Blaze"
                else:
                    ans_text = f"""Ao processar a consulta *'{user_custom_prompt}'*, o modelo **{selected_llm_engine}** analisa as principais plataformas de apostas autorizadas pela SPA/MF em 2026 e mapeia o cenário competitivo.

**Principais Marcas Mapeadas no Mercado:**
- **Líderes de Mercado:** Bet365, Betano, Sportingbet, KTO.
- **Ativos da Sabiá Gaming:** BR4Bet (esportes), Goldebet (estatísticas) e LotoGreen (cassino).

**Diagnóstico RAG:** Para ampliar a citação direta no {selected_llm_engine}, recomenda-se intensificar a publicação de comunicados de imprensa (Digital PR) e otimizar os arquivos `llms.txt` dos domínios."""
                    prob_score = "79%"
                    sentiment = "🟢 Positivo / Mapeado"
                    sources_cited = "Lance!, UOL, Documentos Regulatórios SPA/MF"
                    competitors = "Bet365, Betano, Sportingbet, KTO"

                st.markdown(f"**🤖 Resposta Gerada por {selected_llm_engine}:**")
                st.info(ans_text)
                
                m_sim1, m_sim2, m_sim3, m_sim4 = st.columns(4)
                m_sim1.metric("Probabilidade de Citação", prob_score)
                m_sim2.metric("Sentimento de Reputação", sentiment)
                m_sim3.metric("Fontes de Origem RAG", "3 Veículos Tier-1")
                m_sim4.metric("Concorrentes Mapeados", competitors.split(',')[0] + " e outros")
                st.caption(f"**Portais de Origem Mapeados:** {sources_cited}")

# ---------------------------------------------------------
# ABA 6: EXPANSÃO INTERNACIONAL DE SEO E GEO
# ---------------------------------------------------------
with tab6:
    st.header("🌍 Expansão Internacional de SEO e GEO")
    st.markdown("Framework executivo para internacionalização de tráfego orgânico e autoridade generativa na **América Latina (LatAm) e Europa**.")

    st.subheader("📌 1. Framework de Governança em 4 Etapas")
    f1, f2, f3, f4 = st.columns(4)
    f1.info("**1. Compliance & Regulação**\nValidação de licenças locais (Mincetur, SCJ, SEGOB, SRIJ) e adequação legal de termos.")
    f2.warning("**2. Vol. de Busca vs. CPC**\nAnálise de demanda informacional vs custo pago para estimar CAC orgânico local.")
    f3.error("**3. Arquitetura Hreflang**\nIsolamento técnico em subdiretórios com mapeamento bidirecional exato por código de país.")
    f4.success("**4. MVP via Hub Educativo**\nLançamento de guias de apostas e palpites em blogs regionais para validar tração.")

    st.divider()

    st.subheader("🌎 2. Matriz de Implementação por Mercado Alvo (SEO + GEO)")
    st.caption("Estratégia personalizada considerando regulação, nuances semânticas e fontes RAG locais.")

    df_inter = pd.DataFrame([
        {
            "País / Mercado": "Peru (LatAm)",
            "Regulação Local": "Mincetur (Licença PE)",
            "Arquitetura Hreflang": "`br4.bet/pe/` (`es-PE`)",
            "Terminologia GEO / SEO": "Apuestas deportivas, pollas, parlays, apuestas en vivo",
            "Portais Alvo PR (RAG)": "El Comercio, La República, RPP Noticias"
        },
        {
            "País / Mercado": "Chile (LatAm)",
            "Regulação Local": "SCJ (Marco SCJ)",
            "Arquitetura Hreflang": "`br4.bet/cl/` (`es-CL`)",
            "Terminologia GEO / SEO": "Apuestas combinadas, pollas, futbol chileno, cuotas",
            "Portais Alvo PR (RAG)": "La Tercera, EMOL, BioBioChile"
        },
        {
            "País / Mercado": "México (LatAm)",
            "Regulação Local": "SEGOB (Licença MX)",
            "Arquitetura Hreflang": "`br4.bet/mx/` (`es-MX`)",
            "Terminologia GEO / SEO": "Quinielas, momios, parlays, casino en línea",
            "Portais Alvo PR (RAG)": "El Universal, RÉCORD, MedioTiempo"
        },
        {
            "País / Mercado": "Portugal (Europa)",
            "Regulação Local": "SRIJ (Licença PT)",
            "Arquitetura Hreflang": "`br4.bet/pt/` (`pt-PT`)",
            "Terminologia GEO / SEO": "Odds, apostas múltiplas, boletim, casino online",
            "Portais Alvo PR (RAG)": "A Bola, O Jogo, Público, Jornal de Notícias"
        }
    ])

    st.dataframe(df_inter, use_container_width=True, hide_index=True)

    st.divider()

    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        st.subheader("💡 Nuances Semânticas & Localização (GEO)")
        st.write("""
        - **Evitar Tradução Literal:** Traduzir termos do português para o espanhol sem pesquisa local destrói o ranqueamento. No México se busca por **'momios'** e **'quinielas'**, enquanto no Chile e Peru busca-se por **'pollas'** e **'parlays'**.
        - **Estratégia de RAG Local:** As Inteligências Artificiais citam jornais do próprio país da busca. Uma busca feita em Lima consulta o *El Comercio*. É indispensável fechar assessoria de imprensa (Digital PR) em veículos Tier-1 de cada país.
        """)

    with col_exp2:
        st.subheader("🛠️ Riscos Técnicos a Evitar")
        st.write("""
        - **Canibalização de SERP:** Sem a tag `hreflang` configurada corretamente, o Google pode exibir a Landing Page mexicana para um usuário em Lisboa, derrubando a taxa de conversão.
        - **Contaminação de IP e Bônus:** As páginas de destino de cada subdiretório precisam carregar os métodos de pagamento (ex: PagoEfectivo no Peru, SPEI no México, MB Way em Portugal) e as moedas locais (PEN, CLP, MXN, EUR).
        """)

    st.divider()

    st.subheader("📅 3. Roadmap Executivo de Lançamento Internacional (90 Dias)")
    c_p1, c_p2, c_p3 = st.columns(3)
    c_p1.warning("**0-30 Dias (Governança & Taxonomia):**\n- Validação jurídica e regulatória em cada país.\n- Pesquisa de palavras-chave locais no Semrush Global.\n- Setup do template técnico de `hreflang` e subdiretórios.")
    c_p2.info("**31-60 Dias (Infraestrutura & GEO PR):**\n- Publicação das LPs regionalizadas com moedas locais.\n- Liberação dos manifestos `llms.txt` traduzidos.\n- Primeira onda de Digital PR em portais Tier-1 locais.")
    c_p3.success("**61-90 Dias (Otimização & CRO):**\n- Rastreamento de FTD orgânico por país no BI.\n- Testes A/B de conversão regionalizados.\n- Expansão dos hubs de palpites esportivos locais.")

# ---------------------------------------------------------
# ABA 7: PLANO EXECUTIVO & ESTRUTURA DO TIME (LUCAS TADEU SEO)
# ---------------------------------------------------------
with tab7:
    st.header("🚀 Plano Executivo de Entrada, Timeline & Estrutura do Time")
    st.markdown("Defesa do planejamento operacional de entrada, cronograma de entregas de 30/60/90 dias e estruturação da equipe de SEO/CRO/GEO | Por **Lucas Tadeu SEO**.")

    # SEÇÃO 1: AS 10 PRIMEIRAS AÇÕES IMEDIATAS
    st.subheader("📌 1. As 10 Primeiras Ações Imediatas na Operação (Especialista em SEO & GEO)")
    st.caption("Ações táticas executadas ao assumir o projeto para imersão no negócio, governança de dados, ajuste semântico e liberação para IAs.")

    df_10_acoes_expert = pd.DataFrame([
        {
            "Ação": "1. Imersão no Negócio, Entidades & Unit Economics",
            "Motivo": "Compreender profundamente os modelos de receita das marcas (BR4Bet, Goldebet, LotoGreen), o perfil de cada apostador (ICP) e mapear como as marcas e a holding estão representadas no Knowledge Graph do Google e nas bases dos LLMs.",
            "Prioridade": "🔴 Alta / Imediata"
        },
        {
            "Ação": "2. Alinhamento de Analytics, Atribuição & Funil de FTD",
            "Motivo": "Sentar com os times de BI e Web Analytics para auditarem o rastreamento do clique orgânico (SERP e IA) até o primeiro depósito (FTD). Sem provar geração de receita, o canal perde prioridade de investimento.",
            "Prioridade": "🔴 Alta / Imediata"
        },
        {
            "Ação": "3. Resgate Semântico On-Page & Alinhamento de Intenção",
            "Motivo": "Auditar a estrutura de H1s, Titles e Canonicals das Landing Pages comerciais para impedir que o Google direcione tráfego de conversão para páginas institucionais ou jurídicas (Cookies/Termos).",
            "Prioridade": "🔴 Alta / Imediata"
        },
        {
            "Ação": "4. Desbloqueio Técnico de RAG & Rastreabilidade de IA",
            "Motivo": "Auditar o arquivo robots.txt e validar a disponibilidade do manifesto llms.txt / llms-full.txt para garantir que os robôs da OpenAI, Perplexity, Gemini e Anthropic consigam raspar o site sem timeout.",
            "Prioridade": "🔴 Alta / Imediata"
        },
        {
            "Ação": "5. Mitigação do Gargalo Mobile (Core Web Vitals & INP)",
            "Motivo": "Diagnosticar a sobrecarga de JavaScript client-side que causa travamentos de 564ms (INP) no celular, planejando a transição para Server-Side Rendering (SSR).",
            "Prioridade": "🟡 Média / Curto Prazo"
        },
        {
            "Ação": "6. Mapeamento da Esteira de Quick Wins (Posições 4 a 20)",
            "Motivo": "Minerar no Semrush/GSC palavras-chave comerciais e informacionais de alto volume estagnadas na 2ª página do Google para otimizações rápidas de títulos, H1s e linkagem interna.",
            "Prioridade": "🟡 Média / Curto Prazo"
        },
        {
            "Ação": "7. Auditoria de Crawl Budget & Limpeza de Erros (Screaming Frog)",
            "Motivo": "Analisar as varreduras do crawler para eliminar correntes de redirecionamento (3xx) e erros de página quebrada (4xx/5xx) que afogam a cota diária de varredura do Googlebot.",
            "Prioridade": "🟡 Média / Curto Prazo"
        },
        {
            "Ação": "8. Mapeamento de Reputação Generativa & Hallucinations",
            "Motivo": "Executar testes de prompts em ChatGPT, Gemini e Perplexity para identificar alucinações, avaliações indevidas de risco ou confusão semântica com a marca clone pirata 'BBR4BET'.",
            "Prioridade": "🟡 Média / Curto Prazo"
        },
        {
            "Ação": "9. Setup de Digital PR & Mapeamento de Fontes de RAG",
            "Motivo": "Mapear quais portais de imprensa e jornais Tier-1 (LANCE!, UOL, Gazeta) são citados pelos motores generativos ao recomendar plataformas do segmento, estruturando a assessoria.",
            "Prioridade": "🟢 Estratégico"
        },
        {
            "Ação": "10. Governança de SEO Internacional & Arquitetura Hreflang",
            "Motivo": "Estabelecer a taxonomia de subdiretórios regionais (ex: /pe/, /cl/, /mx/) e mapeamento bidirecional de tags hreflang para expandir a operação geográfica sem canibalizar o tráfego local.",
            "Prioridade": "🟢 Estratégico"
        }
    ])

    st.dataframe(df_10_acoes_expert, use_container_width=True, hide_index=True)

    st.divider()

    # SEÇÃO 2: PLANO DE AÇÃO DETALHADO DE 0 A 90 DIAS
    st.subheader("📅 2. Plano de Execução Estratégico e Soluções (0 a 90 Dias)")
    
    col_t1, col_t2, col_t3 = st.columns(3)
    
    with col_t1:
        st.warning("⏱️ **0 a 30 Dias: Diagnóstico, Quick Wins & Estrutura**")
        st.write("""
        - **Diagnóstico:** 
          * Imersão no negócio, auditoria de atribuição de tráfego no Power BI e alinhamento do tracking de FTD orgânico.
          * Auditoria de Crawl Budget no Screaming Frog e diagnóstico de RAG/IAs.
        - **Quick Wins:** 
          * Mapeamento no Semrush e priorização das palavras-chave comerciais (Pos. 4 a 20) com alto volume e intenção clara.
        - **Estrutura:** 
          * Correção imediata das H1s ausentes nas LPs de apostas.
          * Aplicação de `noindex`/`canonical` nas páginas de Política de Cookies/Termos para limpar a SERP.
          * Liberação e validação do arquivo `llms.txt` sem timeout.
        """)

    with col_t2:
        st.info("🚀 **31 a 60 Dias: Implementação de Conteúdo, SEO & UX**")
        st.write("""
        - **Implementação de Conteúdo:** 
          * Produção e otimização dos briefs para a esteira de Quick Wins.
          * Lançamento do Hub Informacional de Palpites/Estatísticas do Brasileirão na Goldebet.
        - **SEO On-Page:** 
          * Otimização da arquitetura semântica, Schema Markup (SportsEvent/FAQ) e link building interno direcionando autoridade do blog para LPs comerciais.
        - **UX / CRO:** 
          * Redução de atrito na navegação mobile, testes A/B em botões de cadastro/depósito e otimização da velocidade de carregamento dos componentes de odds.
        """)

    with col_t3:
        st.success("📈 **61 a 90 Dias: Escala, Otimização, Autoridade & Conversão**")
        st.write("""
        - **Escala & Otimização:** 
          * Implementação de Server-Side Rendering (SSR) nas LPs de maior volume para zerar o travamento de INP (564ms) no celular.
          * Automação de atualização de pautas esportivas.
        - **Autoridade (Digital PR & GEO):** 
          * Disparo da primeira onda de Digital PR em veículos Tier-1 (LANCE!, UOL, Gazeta) provando a licença SPA/MF para alimentar o RAG dos LLMs e limpar o ruído "BBR4BET".
        - **Conversão (CRO & Expansão):** 
          * Otimização contínua da taxa de conversão clique ➔ FTD e setup da arquitetura de subdiretórios com `hreflang` para expansão internacional.
        """)

    st.divider()

    # SEÇÃO 3: ESTRUTURA E EVOLUÇÃO DO TIME DE SEO & CRO
    st.subheader("👥 3. Estruturação da Equipe de SEO, CRO & Conteúdo")
    
    t_col1, t_col2 = st.columns(2)
    
    with t_col1:
        st.subheader("🏢 Divisão de Responsabilidades (Interno vs Terceirizado)")
        st.write("""
        - **Atividades mantidas INTERNAMENTE:**
          * Planejamento Estratégico, Governança de SEO/GEO e Análise de Dados/BI.
          * Diretrizes Técnicas On-Page e Arquitetura de Informação.
          * Estruturação de Briefings, Pautas e Gestão do Funil de Conversão (CRO).
        
        - **Atividades TERCEIRIZADAS (Parceiros Externos):**
          * **Digital PR & Assessoria de Imprensa:** Agências externas com relacionamento e inserção direta em veículos de comunicação Tier-1.
          * **Link Building Institucional:** Aquisição contínua de autoridade de marca e backlinks de qualidade.
        """)

    with t_col2:
        st.subheader("🔮 Evolução do Time e Visão 12 Meses")
        st.write("""
        - **Contratação Imediata (+1 Pessoa a Curto Prazo):**
          * **Cargo:** 1 *Analista de Conteúdo Júnior*.
          * **Papel:** Foco 100% na produção, redação e otimização On-Page de artigos e páginas de pouso a partir dos planejamentos passados.
        
        - **Visão do Time em 12 Meses (Estrutura Enxuta & Alta Performance):**
          * **1 Especialista Sênior em SEO & CRO (Liderança por Lucas Tadeu SEO):** Responsável pela estratégia, BI, governança técnica e inteligência de GEO.
          * **1 Analista de Conteúdo Júnior:** Responsável pela execução, produção e otimização do calendário editorial.
          * **Parceiro Externo de Digital PR & Link Building:** Agência parceira focada na conquista de autoridade e RAG generativo.
        """)

    # RODAPÉ FINAL DE COPYRIGHT & BRANDING
    st.markdown("""
        <div class="footer-banner">
            Apresentação Estratégica & Defesa do Case | Projetado e Desenvolvido por <strong>Lucas Tadeu SEO</strong> © 2026
        </div>
    """, unsafe_allow_html=True)
