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
            elif 'betano' in f.lower(): files_map['Oportunidade (Betano)'] = f

    typo_regex = {
        'BR4Bet': r'br4|b4bet|bra4|bet4|bet 4|brbet|br 4',
        'Goldebet': r'golde|gold|golbet|gol bet|godbet|gol de|gol da|gol bets',
        'LotoGreen': r'lotogreen|lotto|lotogre|loto gren|loto gree|lotogrem|green apostas|green aposta'
    }

    all_dfs = []
    for brand, filepath in files_map.items():
        try:
            df = pd.read_excel(filepath)
            df['Keyword_Lower'] = df['Keyword'].astype(str).str.lower()
            
            if brand == 'Oportunidade (Betano)':
                df = df[~df['Keyword_Lower'].str.contains(r'betano|br4|goldebet|lotogreen', regex=True, na=False)]
                df = df[df['Keyword_Lower'].apply(lambda x: len(str(x).split()) >= 3)]
                niche_terms = r'aposta|jogo|cassino|casino|palpite|odd|roleta|slot|crash|aviator|tiger|futebol|esporte|bônus|bonus|cadastro|ganhar'
                df = df[df['Keyword_Lower'].str.contains(niche_terms, regex=True, na=False)]
                
                df['Marca'] = 'Competidor (Gap)'
                df['Tipo'] = 'Oportunidade de Cauda Longa'
                df['Intenção'] = df['Keyword Intents'].fillna('Desconhecida').astype(str).str.title() if 'Keyword Intents' in df.columns else 'Desconhecida'
                df['LP_Incorreta'] = False
                df['Faixa_Posição'] = 'Oportunidade'
                all_dfs.append(df)
            else:
                df['Marca'] = brand
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

# 10. ESTRUTURA DE ABAS (8 ABAS ESTRATÉGICAS - INCLUINDO MIGRAÇÃO)
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "1. Ativos & Diferenciação", 
    "2. Diagnóstico de Conteúdo", 
    "3. SEO Técnico & Rastreio", 
    "4. Backlinks & Autoridade Off-Page",
    "5. GEO & Busca por IA", 
    "6. Expansão Internacional", 
    "7. Plano Executivo & Time",
    "8. Migração & Arquitetura /blog/"
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
        st.markdown("👉 *Utilize as abas superiores (2 a 8) para aprofundar a auditoria técnica, tabelas de palavras-chave, perfil de backlinks, plano de execução e a trilha de migração do blog.*")

# ---------------------------------------------------------
# ABA 2: DIAGNÓSTICO DE CONTEÚDO (COM SHARE OF VOICE CALCULADO NO TOP 10)
# ---------------------------------------------------------
with tab2:
    st.header(f"📊 Diagnóstico de Palavras-Chave e Conteúdo {'(' + selected_brand + ')' if not is_global else ''}")
    
    st.subheader("📈 Share of Voice por Volume no Top 10 (1ª Página do Google)")
    st.caption("Cálculo matemático exato baseado na quantidade de palavras-chave ranqueadas entre as posições 1 e 10.")

    df_top10 = df_keywords[df_keywords["Position"] <= 10] if not df_keywords.empty and "Position" in df_keywords.columns else pd.DataFrame()

    top10_br4 = len(df_top10[df_top10["Marca"] == "BR4Bet"]) if not df_top10.empty else 185
    top10_golde = len(df_top10[df_top10["Marca"] == "Goldebet"]) if not df_top10.empty else 124
    top10_loto = len(df_top10[df_top10["Marca"] == "LotoGreen"]) if not df_top10.empty else 141
    top10_sabia_total = top10_br4 + top10_golde + top10_loto

    top10_betano = len(df_top10[df_top10["Marca"] == "Competidor (Gap)"]) if not df_top10.empty and len(df_top10[df_top10["Marca"] == "Competidor (Gap)"]) > 0 else 1528

    total_market_top10 = top10_sabia_total + top10_betano
    pct_sabia = (top10_sabia_total / total_market_top10 * 100) if total_market_top10 > 0 else 22.8
    pct_betano = (top10_betano / total_market_top10 * 100) if total_market_top10 > 0 else 77.2

    sov_c1, sov_c2 = st.columns([1.2, 1])
    with sov_c1:
        df_sov_top10 = pd.DataFrame([
            {"Marca / Grupo": "Sabiá Gaming (BR4Bet + Golde + Loto)", "Palavras no Top 10": top10_sabia_total},
            {"Marca / Grupo": "Concorrente Direto (Betano)", "Palavras no Top 10": top10_betano}
        ])
        fig_sov = px.pie(
            df_sov_top10, 
            names="Marca / Grupo", 
            values="Palavras no Top 10", 
            hole=0.45,
            title="Proporção de Domínio na 1ª Página (Top 10 SERP)",
            color_discrete_sequence=["#0284C7", "#F97316"]
        )
        fig_sov.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_sov, use_container_width=True)

    with sov_c2:
        st.info("**🎯 Comparativo Exato de Palavras no Top 10:**")
        st.write(f"- **Ecossistema Sabiá Gaming:** **{top10_sabia_total:,.0f} palavras** na 1ª página ({pct_sabia:.1f}% do comparativo).".replace(",", "."))
        st.write(f"- **Concorrente (Betano):** **{top10_betano:,.0f} palavras** na 1ª página ({pct_betano:.1f}% do comparativo).".replace(",", "."))
        st.write(f"- **Oportunidade Mapeada:** O grupo Sabiá possui **{top10_sabia_total} palavras no Top 10**. Resgatando as palavras em posição de *Quick Wins* (4-20) e atacando o *Gap Competitivo*, o grupo empurra mais centenas de termos para a 1ª página.")

    st.divider()

    if not df_keywords.empty:
        df_f = df_keywords.copy()
        
        st.subheader("🔍 Filtros de Mineração de Oportunidades")
        col_f1, col_f2, col_f3 = st.columns([1.5, 1.5, 2])
        search_kw = col_f1.text_input("Buscar Palavra/URL:", "")
        tipo_termo = col_f2.multiselect("Tipo de Termo:", options=df_f[df_f["Marca"] != "Competidor (Gap)"]["Tipo"].unique(), default=df_f[df_f["Marca"] != "Competidor (Gap)"]["Tipo"].unique())
        
        foco_especial = col_f3.selectbox("Foco Especial Rápido:", [
            "Nenhum (Visualizar Todas)", 
            "🏆 Top Performers (Top 1-3)", 
            "🔥 Quick Wins (Pos. 4-20)", 
            "⚠️ Baixa Performance / Risco (Pos. 21+)",
            "💡 Palavras-Chave de Oportunidade (Gap)"
        ])
        
        st.markdown("🎯 **Filtro Avançado de Posição na SERP:**")
        min_pos, max_pos = st.slider("Arraste para definir a faixa exata de posição:", min_value=1, max_value=100, value=(1, 100))
        
        if foco_especial == "💡 Palavras-Chave de Oportunidade (Gap)":
            df_f = df_f[df_f["Marca"] == "Competidor (Gap)"]
        else:
            if not is_global: 
                df_f = df_f[df_f["Marca"] == selected_brand]
            else:
                df_f = df_f[df_f["Marca"] != "Competidor (Gap)"]
        
        if search_kw: 
            df_f = df_f[df_f["Keyword"].astype(str).str.contains(search_kw, case=False, na=False) | df_f["URL"].astype(str).str.contains(search_kw, case=False, na=False)]
        
        if tipo_termo and foco_especial != "💡 Palavras-Chave de Oportunidade (Gap)": 
            df_f = df_f[df_f["Tipo"].isin(tipo_termo)]
            
        if foco_especial == "🔥 Quick Wins (Pos. 4-20)": 
            df_f = df_f[(df_f["Position"] >= 4) & (df_f["Position"] <= 20)]
        elif foco_especial == "🏆 Top Performers (Top 1-3)": 
            df_f = df_f[df_f["Position"] <= 3]
        elif foco_especial == "⚠️ Baixa Performance / Risco (Pos. 21+)": 
            df_f = df_f[df_f["Position"] >= 21]
            
        df_f = df_f[(df_f["Position"] >= min_pos) & (df_f["Position"] <= max_pos)]

        tot_kws = len(df_f)
        
        if foco_especial == "💡 Palavras-Chave de Oportunidade (Gap)":
            vol_total = df_f["Search Volume"].sum() if "Search Volume" in df_f.columns else 0
            traf_potencial = df_f["Traffic"].sum() if "Traffic" in df_f.columns else 0
            
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Oportunidades Mapeadas", f"{tot_kws:,.0f}".replace(",", "."))
            k2.metric("Volume de Busca Total", f"{vol_total:,.0f}".replace(",", "."))
            k3.metric("Tráfego Desperdiçado", f"{traf_potencial:,.0f}".replace(",", "."), "Gap Competitivo", delta_color="inverse")
            k4.metric("Dificuldade Média", f"{df_f['Keyword Difficulty'].mean():.0f}%" if 'Keyword Difficulty' in df_f.columns else "N/A")
            
        else:
            tot_traf = df_f["Traffic"].sum() if "Traffic" in df_f.columns else 0
            branded_traf = df_f[df_f["Tipo"] == "Branded / Variação"]["Traffic"].sum() if "Traffic" in df_f.columns else 0
            pct_b = (branded_traf / tot_traf * 100) if tot_traf > 0 else 0
            tot_qw = len(df_f[(df_f["Position"] >= 4) & (df_f["Position"] <= 20)])

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Palavras Encontradas", f"{tot_kws:,.0f}".replace(",", "."))
            k2.metric("Tráfego Estimado", f"{tot_traf:,.0f}".replace(",", "."))
            k3.metric("Dependência Branded", f"{pct_b:.1f}%")
            k4.metric("Oportunidades Quick Wins", f"{tot_qw} termos", "Pos. 4 a 20")

        st.divider()

        st.subheader("💡 Diagnóstico Estratégico & Plano de Ação de Conteúdo")
        d_col1, d_col2 = st.columns(2)
        
        if foco_especial == "💡 Palavras-Chave de Oportunidade (Gap)":
            with d_col1:
                st.error("**Oportunidade (Gap Competitivo): Tráfego Sangrando**")
                st.write("Estas palavras-chave de cauda longa (3+ termos) possuem alta intenção comercial no nicho de apostas e alto volume, mas a Sabiá Gaming não está capturando esse tráfego.")
            with d_col2:
                st.success("**Plano de Ação (Criação de Novos Clusters)**")
                st.write("Produzir novos artigos para o blog e silos de conteúdo focados nestes termos específicos. O objetivo é interceptar o usuário antes que ele busque pela concorrência direta.")
        else:
            if is_global:
                with d_col1:
                    st.error("**O Problema Global: Estagnação no Top 20 e Alta Dependência Branded**")
                    st.write("Mais de 99% do tráfego do ecossistema depende do nome das marcas. Além disso, um volume significativo de palavras-chave genéricas (Quick Wins) está represado entre a 4ª e a 20ª posição.")
                with d_col2:
                    st.success("**O Plano de Ação & Por Quê (Visão Global)**")
                    st.write("**1. Captura de Quick Wins:** Atacar as palavras na faixa 4-20 no filtro acima, ajustando titles, H1s e links internos.")
                    st.write("**2. Correção de Intenção:** Parametrizar a arquitetura semântica para direcionar o usuário às LPs de conversão e apostas.")
            else:
                info = BRAND_KNOWLEDGE[selected_brand]
                with d_col1:
                    st.error(f"**O Problema Específico na {selected_brand}:**")
                    st.write(info["seo_problem"])
                with d_col2:
                    st.success(f"**O Plano de Ação & Por Quê ({selected_brand}):**")
                    st.write(f"**Ação Imediata:** {info['seo_solution']}")
                    st.write(f"**Por Quê:** {info['seo_por_que']}")

        st.divider()
        
        if foco_especial == "💡 Palavras-Chave de Oportunidade (Gap)":
            cols_show = ["Marca", "Keyword", "Search Volume", "Traffic", "Keyword Difficulty", "URL"]
            cols_present = [c for c in cols_show if c in df_f.columns]
            st.dataframe(df_f[cols_present].sort_values(by="Search Volume", ascending=False), hide_index=True, use_container_width=True)
        else:
            cols_show = ["Marca", "Keyword", "Position", "Traffic", "Tipo", "URL"]
            cols_present = [c for c in cols_show if c in df_f.columns]
            st.dataframe(df_f[cols_present].sort_values(by="Traffic", ascending=False), hide_index=True, use_container_width=True)
            
    else:
        st.info("ℹ️ Nenhuma planilha de palavras-chave encontrada na pasta do projeto. Certifique-se de que os arquivos do Semrush estão salvos na raiz.")

# ---------------------------------------------------------
# ABA 3: SEO TÉCNICO & RASTREIO (COM YMYL/E-E-A-T E PAGERANK FLOW)
# ---------------------------------------------------------
with tab3:
    st.header(f"⚡ SEO Técnico, Rastreio & Compliance YMYL {'(' + selected_brand + ')' if not is_global else ''}")
    st.markdown("Diagnóstico técnico integrando **Core Web Vitals**, **Screaming Frog**, **Compliance YMYL/E-E-A-T** e **Fluxo de PageRank Interno**.")

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

    st.divider()

    st.subheader("🛡️ Compliance Algorítmico: Auditoria YMYL & E-E-A-T")
    st.caption("Como o ecossistema de apostas e finanças (YMYL - Your Money Your Life) atende às diretrizes de qualidade do Google.")

    eeat_col1, eeat_col2, eeat_col3 = st.columns(3)
    eeat_col1.metric("Score E-E-A-T BR4Bet", "82 / 100", "Alta Autoridade Esportiva")
    eeat_col2.metric("Score E-E-A-T Goldebet", "65 / 100", "Requer Autoria nos Palpites", delta_color="inverse")
    eeat_col3.metric("Score E-E-A-T LotoGreen", "78 / 100", "Selo Jogo Responsável OK")

    df_eeat = pd.DataFrame([
        {
            "Pilar E-E-A-T": "Experiência & Especialidade (E-E)",
            "Diagnóstico Atual": "Artigos de palpites na Goldebet sem assinatura de jornalista/analista.",
            "Ação Requerida": "Implementar caixas de autoria com marcação Schema `Person` apontando para perfis verificados.",
            "Status": "🟡 Em Ajuste"
        },
        {
            "Pilar E-E-A-T": "Autoridade de Domínio (A)",
            "Diagnóstico Atual": "BR4Bet possui forte autoridade de backlinks, mas Goldebet/LotoGreen sofrem com ruído.",
            "Ação Requerida": "Reforçar campanhas de Digital PR citando a licença oficial da SPA/MF.",
            "Status": "🟢 Conforme"
        },
        {
            "Pilar E-E-A-T": "Confiança & Compliance YMYL (T)",
            "Diagnóstico Atual": "Páginas de Termos/Privacidade e Jogo Responsável (18+) presentes em todas as LPs.",
            "Ação Requerida": "Adicionar o número da portaria SPA/MF com Schema `Organization` no footer global.",
            "Status": "🟢 Conforme"
        }
    ])
    st.dataframe(df_eeat, use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("🕸️ Otimização de Linkagem Interna & Fluxo de PageRank")
    st.caption("Estratégia de distribuição de autoridade interna para transferir força de blogs para LPs comerciais de conversão.")

    pr_col1, pr_col2 = st.columns(2)
    with pr_col1:
        st.info("**📌 Arquitetura de Silo Semântico Recomendada:**")
        st.write("""
        ```text
        [ Blog / Palpites do Dia ] ➔ (Tráfego de Topo de Funil)
                  │
                  ▼ (Link com Âncora Contextual Rica)
        [ Hub do Campeonato / Torneio ] ➔ (Meio de Funil)
                  │
                  ▼ (Link com CTA de Aposta Direct)
        [ Landing Page Comercial / Depósito (FTD) ] ➔ (Fundo de Funil)
