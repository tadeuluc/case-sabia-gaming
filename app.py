import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração da Página
st.set_page_config(
    page_title="Lucas Tadeu SEO | iGaming Intelligence Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Customizada Executiva
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e222d; padding: 15px; border-radius: 10px; border: 1px solid #2e3440; }
    .brand-card { background-color: #1e222d; padding: 20px; border-radius: 10px; border-left: 5px solid #00E676; margin-bottom: 15px; }
    .jarvis-box { background-color: #111b27; border: 1px solid #1E88E5; padding: 22px; border-radius: 12px; border-left: 6px solid #00BCD4; margin-top: 15px; }
    .alert-box { background-color: #2b171a; border: 1px solid #FF5252; padding: 20px; border-radius: 10px; border-left: 6px solid #FF1744; margin-bottom: 20px; }
    .step-card { background-color: #181d28; padding: 18px; border-radius: 8px; border: 1px solid #2a3142; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SIDEBAR / BRANDING
# -----------------------------------------------------------------------------
with st.sidebar:
    try:
        st.image("assets/logo_lucas_tadeu.png", width=220)
    except:
        st.markdown("## 🚀 **Lucas Tadeu SEO**")
    
    st.caption("Especialista Sênior em SEO & Growth para iGaming")
    st.markdown("---")
    st.markdown("🤖 **Status do Gêmeo Digital:** `ONLINE` (Jarvis Mode)")
    st.markdown("📊 **Marcas Auditadas:** BR4Bet | LotoGreen | Goldebet")
    st.markdown("🚨 **Protocolo Ativo:** Migração de Emergência (MP)")
    st.markdown("---")
    st.info("💡 **Objetivo:** Consultoria de SEO completa, incluindo diagnóstico de palavras-chave, autoridade e protocolo de migração 301 de emergência.")

# -----------------------------------------------------------------------------
# NAVEGAÇÃO POR ABAS
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📌 Contexto & Desafio",
    "📊 Diagnóstico 3 Marcas",
    "🔗 Link Building & Autoridade",
    "🔄 Migração de Domínio (MP)",
    "⚡ SEO Técnico Vivo (AI)",
    "🛡️ E-E-A-T & GEO (AI Search)",
    "📈 Simulador de Oportunidades"
])

# -----------------------------------------------------------------------------
# ABA 1: CONTEXTO & DESAFIO
# -----------------------------------------------------------------------------
with tab1:
    st.title("📌 Contexto do Mercado de iGaming no Brasil & Desafio Estratégico")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Mercado Est. Brasil (2026)", "R$ 120+ Bi", "Mercado Regulamentado")
    col2.metric("Dependência Tráfego Branded", "~98%", "- Gargalo Crítico")
    col3.metric("Oportunidade Non-Branded", "+450k Buscas/mês", "Oceano Azul")

    st.markdown("---")
    st.markdown("""
    ### 🎯 O Desafio Central das Marcas
    As operadoras **BR4Bet**, **LotoGreen** e **Goldebet** consolidaram presenças fortes em tráfego direto e navegacional, mas compartilham a mesma vulnerabilidade orgânica:
    
    * **Dependência Excessiva de Marca:** Mais de 96% a 99% das visitas de busca orgânica dependem de usuários que já conhecem e digitam o nome das plataformas (`lotogreen`, `gol de bet`, `br4bet`).
    * **Inexistência no Funil de Descoberta:** Palavras-chave genéricas e altamente lucrativas (*jogos de cassino*, *apostas futebol*, *plataforma de apostas*) não figuram no Top 3.
    * **Risco de Bloqueios e Regulação (MP):** A recente aplicação de restrições operacionais/governamentais exige capacidade imediata de **migração segura de tráfego para novos domínios** sem perda de equidade de ranking.
    """)

# -----------------------------------------------------------------------------
# ABA 2: DIAGNÓSTICO COMPARATIVO
# -----------------------------------------------------------------------------
with tab2:
    st.title("📊 Diagnóstico Comparativo de Tráfego e Palavras-Chave")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("BR4Bet", "1.098 Keywords", "Tráfego Est: 122.780/mês")
    c2.metric("LotoGreen", "254 Keywords", "Tráfego Est: 161.082/mês")
    c3.metric("Goldebet", "315 Keywords", "Tráfego Est: 108.068/mês")
    
    st.markdown("---")
    st.subheader(" Proporção de Tráfego: Branded (Marca) vs. Non-Branded (Genéricos)")
    
    brands_data = {
        'Marca': ['BR4Bet', 'LotoGreen', 'Goldebet'],
        'Branded (%)': [96.3, 98.7, 99.1],
        'Non-Branded (%)': [3.7, 1.3, 0.9]
    }
    df_brands = pd.DataFrame(brands_data)
    
    fig_pie = go.Figure()
    fig_pie.add_trace(go.Bar(name='Branded (Nome da Marca)', x=df_brands['Marca'], y=df_brands['Branded (%)'], text=df_brands['Branded (%)'].apply(lambda x: f"{x}%"), textposition='auto', marker_color='#1E88E5'))
    fig_pie.add_trace(go.Bar(name='Non-Branded (Genéricos)', x=df_brands['Marca'], y=df_brands['Non-Branded (%)'], text=df_brands['Non-Branded (%)'].apply(lambda x: f"{x}%"), textposition='auto', marker_color='#00E676'))
    
    fig_pie.update_layout(barmode='group', yaxis_title="Porcentagem de Tráfego (%)", template="plotly_dark", height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("📋 Amostra de Palavras-Chave de Maior Impacto")
    top_kw_sample = pd.DataFrame({
        'Marca': ['BR4Bet', 'BR4Bet', 'LotoGreen', 'LotoGreen', 'Goldebet', 'Goldebet'],
        'Palavra-Chave': ['br4bet', 'bet 4 cassino', 'lotogreen', 'lotto green', 'goldbet', 'goldabet'],
        'Posição': [2, 3, 1, 1, 1, 1],
        'Volume Busca': [165000, 3600, 135000, 1300, 49500, 480],
        'Tráfego Est.': [21780, 64, 108000, 1040, 39600, 119],
        'Tipo': ['Branded', 'Non-Branded', 'Branded', 'Non-Branded', 'Branded', 'Non-Branded']
    })
    st.dataframe(top_kw_sample, use_container_width=True)

# -----------------------------------------------------------------------------
# ABA 3: LINK BUILDING & AUTORIDADE DE DOMÍNIO
# -----------------------------------------------------------------------------
with tab3:
    st.title("🔗 Pillar de Link Building & Autoridade de Domínio (Semrush Insights)")
    st.markdown("Métricas de autoridade de domínio (**Authority Score - AS**) do Semrush integradas ao diagnóstico.")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.markdown("""
        <div class="brand-card">
            <h3>BR4Bet (br4.bet.br)</h3>
            <h1 style="color: #00E676;">AS 35</h1>
            <p><b>Badge Semrush:</b> <i>High traffic to backlink ratio</i></p>
            <p>Maior autoridade do grupo. Sustentada pelo alto volume de busca direta da marca, mas com perfil de backlinks frágil para termos genéricos.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="brand-card" style="border-left-color: #FFB300;">
            <h3>LotoGreen (lotogreen.bet.br)</h3>
            <h1 style="color: #FFB300;">AS 33</h1>
            <p><b>Badge Semrush:</b> <i>High traffic to backlink ratio</i></p>
            <p>Autoridade intermediária. Apresenta tráfego elevado focado na marca, com escassez de links em portais relevantes do setor.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_c:
        st.markdown("""
        <div class="brand-card" style="border-left-color: #FF5252;">
            <h3>Goldebet (goldebet.bet.br)</h3>
            <h1 style="color: #FF5252;">AS 31</h1>
            <p><b>Badge Semrush:</b> <i>High traffic to backlink ratio</i></p>
            <p>Menor pontuação de autoridade do grupo. Exige atuação urgente em Digital PR e aquisição estratégica de links qualificados.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="jarvis-box">
        <h4>🤖 Diagnóstico do Consultor (Lucas Tadeu SEO AI - Gêmeo Digital)</h4>
        <p><b>Análise Estratégica de Autoridade e Link Building:</b></p>
        <ul>
            <li><b>A 'Falsa' Ilusão de Força:</b> As três marcas receberam o selo <i>"High traffic to backlink ratio"</i> no Semrush. Isso comprova que o tráfego orgânico atual é mantido pela força da marca e mídia off-site, enquanto o <b>perfil de backlinks externos é fraco e desequilibrado</b>.</li>
            <li><b>O Gargalo da Primeira Página:</b> Sem autoridade de backlinks em portais de esportes, notícias e finanças, nenhuma das três operadoras conseguirá desbancar os concorrentes consolidados no Top 3 de termos genéricos (*cassino online*, *apostas em futebol*).</li>
            <li><b>Plano de Ação de Link Building para iGaming:</b>
                <ol>
                    <li><b>Digital PR com Pesquisas de Dados:</b> Produzir estudos de tendências de apostas no Brasil para conquistar links editoriais espontâneos na grande imprensa.</li>
                    <li><b>Guest Posts & Parcerias de Co-Marketing:</b> Adquirir backlinks contextuais em domínios de alta autoridade (AS > 40) com variação de textos âncora comerciais e de cauda longa.</li>
                    <li><b>Recuperação de Menções (Unlinked Brand Mentions):</b> Mapear citações do nome das marcas na web sem hyperlink e convertê-las em backlinks.</li>
                </ol>
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ABA 4: ESTRATÉGIA DE MIGRAÇÃO DE DOMÍNIO (MP / RISCO REGULATÓRIO)
# -----------------------------------------------------------------------------
with tab4:
    st.title("🔄 Protocolo Avançado de Migração de Domínio (Resposta a MP / Bloqueios)")
    
    st.markdown("""
    <div class="alert-box">
        <h3>🚨 Plano de Contingência SEO Pós-Medida Provisória</h3>
        <p>Com as restrições temporárias impostas pelo governo brasileiro a domínios de apostas (<code>.bet.br</code>), a transferência rápida e segura de tráfego para um novo domínio é vital para mitigar perdas de receita e preservar o patrimônio de SEO acumulado.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🛠️ Roteiro Tático de Migração em 5 Etapas")
    
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        st.markdown("""
        <div class="step-card">
            <h4>Etapa 1: Mapeamento 1:1 & Inventário de URLs</h4>
            <p>• Extração completa do mapa de URLs via Screaming Frog / GSC.<br>
            • Criação da planilha de redirecionamento de exata correspondência (<i>De: URL Antiga -> Para: URL Nova</i>).<br>
            • <b>Proibido:</b> Redirecionar todas as páginas internas para a Homepage do novo domínio (isso causa destruição de autoridade por Soft 404).</p>
        </div>
        <div class="step-card">
            <h4>Etapa 2: Infraestrutura DNS & Redirecionamento 301 Nátivo</h4>
            <p>• Configuração dos Redirecionamentos <b>301 Permanentes</b> via Edge Rules na Cloudflare ou Nginx.<br>
            • Manutenção ativa dos certificados SSL no domínio antigo para garantir HTTPS contínuo nos redirects.<br>
            • Preservação da estrutura de parâmetros UTM de afiliados durante o redirecionamento.</p>
        </div>
        <div class="step-card">
            <h4>Etapa 3: Integração no Google Search Console (GSC)</h4>
            <p>• Verificação da propriedade do novo domínio no GSC.<br>
            • Acionamento formal da ferramenta <b>"Mudança de Endereço" (Change of Address)</b> do Google.<br>
            • Envio imediato dos novos XML Sitemaps no novo domínio para acelerar a reindexação.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_m2:
        st.markdown("""
        <div class="step-card">
            <h4>Etapa 4: Atualização do Ecossistema Off-Page & Ancoragem</h4>
            <p>• Atualização de URLs de destino em campanhas de afiliados, redes sociais (Bio/Linktree) e anúncios.<br>
            • Contato com parceiros de Mídia e PR para atualizar os backlinks mais fortes apontando para o novo domínio.<br>
            • Inclusão de notas e dados estruturados indicando a mudança de marca/domínio oficial.</p>
        </div>
        <div class="step-card">
            <h4>Etapa 5: Monitoramento de Transição & Preservação Navegacional</h4>
            <p>• Acompanhamento diário da migração de impressões e cliques do domínio antigo para o novo no GSC.<br>
            • Monitoramento do arquivo de erros 404 e canonicals inconsistentes.<br>
            • Comunicação em popup transparente para o usuário: <i>"Redirecionamos você para o nosso novo endereço oficial!"</i>.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Seção Interativa com o Gêmeo Digital
    st.subheader("🤖 Consultoria de Crise do Gêmeo Digital (Lucas Tadeu AI)")
    
    brand_migration_choice = st.selectbox("Selecione a marca para simular o plano de migração:", ["BR4Bet", "LotoGreen", "Goldebet"])
    new_domain_input = st.text_input("Insira o NOVO domínio de destino (ex: novabr4.com):", f"nova-{brand_migration_choice.lower()}.com")
    
    st.markdown(f"""
    <div class="jarvis-box">
        <h4>⚡ Recomendações Estratégicas para Migração da {brand_migration_choice} -> <code>{new_domain_input}</code></h4>
        <p><b>Análise do Lucas Tadeu SEO AI:</b></p>
        <ul>
            <li><b>Preservação do Tráfego Navegacional (Branded):</b> Como a <b>{brand_migration_choice}</b> possui cerca de ~98% do tráfego dependente da marca, os usuários continuarão buscando pelo nome antigo no Google. Para não perder essa demanda, o novo domínio deve manter tags <code>&lt;title&gt;</code> combinadas durante os primeiros 90 dias (ex: <i>"{brand_migration_choice} Oficial | Novo Acesso em {new_domain_input}"</i>).</li>
            <li><b>Evite a Perda de CTR na SERP:</b> Ao mudar de domínio, o Google testa a nova URL nas buscas. Mantenha os snippets e metas de descrição consistentes para garantir que a taxa de cliques (CTR) não caia durante o período de transição.</li>
            <li><b>Velocidade de Processamento do Google:</b> Utilizando o recurso <i>Change of Address</i> no GSC + Sitemaps atualizados, a transferência dos sinais de ranking leva entre <b>7 e 21 dias</b> para estabilizar.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ABA 5: SEO TÉCNICO VIVO (PAGESPEED + AI)
# -----------------------------------------------------------------------------
with tab5:
    st.title("⚡ SEO Técnico em Tempo Real + Análise do Gêmeo Digital")
    st.write("Auditoria ao vivo de Core Web Vitals conectada diretamente à API do Google PageSpeed.")
    
    target_url = st.text_input("Insira a URL para auditoria técnica (ex: https://br4.bet.br):", "https://br4.bet.br")
    
    if st.button("Executar Diagnóstico Técnico com IA", type="primary"):
        with st.spinner("Conectando ao Google PageSpeed API e ativando o Lucas Tadeu AI..."):
            try:
                api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={target_url}&strategy=mobile"
                res = requests.get(api_url).json()
                metrics = res.get('lighthouseResult', {}).get('audits', {})
                
                lcp = metrics.get('largest-contentful-paint', {}).get('displayValue', 'N/A')
                cls = metrics.get('cumulative-layout-shift', {}).get('displayValue', 'N/A')
                speed_idx = metrics.get('speed-index', {}).get('displayValue', 'N/A')
                
                c1, c2, c3 = st.columns(3)
                c1.metric("LCP (Largest Contentful Paint)", lcp)
                c2.metric("CLS (Cumulative Layout Shift)", cls)
                c3.metric("Speed Index", speed_idx)
                
                st.markdown("---")
                st.markdown(f"""
                <div class="jarvis-box">
                    <h4>🤖 Diagnóstico Técnico do Lucas Tadeu SEO AI</h4>
                    <p><b>Relatório de Core Web Vitals para <code>{target_url}</code>:</b></p>
                    <ul>
                        <li><b>LCP ({lcp}):</b> No setor de iGaming, LCPs elevados costumam ser causados por iFrames de provedores de jogos e carregamento síncrono de banners de apostas ao vivo.</li>
                        <li><b>CLS ({cls}):</b> A instabilidade visual afeta diretamente a conversão. Adicione dimensões fixas para os blocos de iFrames e pop-ups promocionais.</li>
                        <li><b>Ação Imediata:</b> Configurar aditamento de execução de scripts de terceiros (GTM, Pixel de Afiliados, Live Chat) após a primeira interação do usuário na página.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Erro na conexão com a API do Google: {e}")

# -----------------------------------------------------------------------------
# ABA 6: E-E-A-T & GEO (SEARCH BY AI)
# -----------------------------------------------------------------------------
with tab6:
    st.title("🛡️ E-E-A-T & Generative Engine Optimization (GEO)")
    st.markdown("""
    A avaliação do Google e dos novos motores de busca por IA (ChatGPT, Google Gemini, Perplexity) para sites de iGaming segue o padrão estrito de **YMYL (Your Money Your Life)**.
    """)
    
    e1, e2 = st.columns(2)
    with e1:
        st.markdown("""
        ### 🏛️ Estrutura de E-E-A-T em Apostas
        * **Experiência e Especialização:** Criar páginas de autores com biografia comprovada em análise esportiva ou iGaming.
        * **Confiabilidade e Transparência:** Exibir o número da licença de operação nacional, selos de Jogo Responsável (18+) e políticas transparentes de saque e depósito.
        """)
    with e2:
        st.markdown("""
        ### 🤖 Otimização para Motores Generativos (GEO)
        * **Citação em Fontes Primárias:** A IA consulta dados de portais de imprensa e sites de reputação (Reclame Aqui, iGB) para indicar marcas de apostas seguras.
        * **Dados Estruturados Schema.org:** Implementar marcações do tipo `Organization`, `FAQPage` e `FinancialProduct` para facilitar a indexação por LLMs.
        """)

# -----------------------------------------------------------------------------
# ABA 7: SIMULADOR DE OPORTUNIDADES
# -----------------------------------------------------------------------------
with tab7:
    st.title("📈 Simulador de Crescimento de Tráfego Non-Branded")
    st.write("Projete o ganho de tráfego orgânico ao conquistar o Top 3 para termos genéricos no setor de apostas.")
    
    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        v_buscas = st.slider("Volume Mensal de Buscas Estimado das Palavras Alvo:", 50000, 1000000, 300000, step=25000)
    with col_sim2:
        ctr_target = st.slider("CTR Médio Alvo para Posições Top 3 (%):", 5.0, 35.0, 18.0, step=1.0)
    
    trafego_ganho = int(v_buscas * (ctr_target / 100))
    
    st.markdown("---")
    st.success(f"🚀 **Projeção de Incremento:** +{trafego_ganho:,} novos visitantes qualificados por mês sem custo adicional de mídia!")
