import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os
import unicodedata
import base64

# Configuração da página Streamlit
st.set_page_config(
    page_title="Controle de Estoque - Cerâmica Simonassi",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# FUNÇÃO PARA DATA EM PORTUGUÊS
# -------------------------------------------------------------
MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def obter_data_portugues():
    hoje = datetime.now()
    mes_nome = MESES_PT[hoje.month]
    return f"{hoje.day} de {mes_nome} de {hoje.year}"

# -------------------------------------------------------------
# ESTILIZAÇÃO VISUAL CORPORATIVA
# -------------------------------------------------------------
st.markdown("""
    <style>
    .stApp {
        background-color: #F8FAFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #0B2545;
        color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    [data-testid="stSidebar"] .stRadio label, [data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] span {
        color: #CBD5E1 !important;
    }
    h1, h2, h3 {
        color: #0B2545 !important;
        font-weight: 700;
    }
    .stButton>button, form button {
        background-color: #F97316 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 2px 4px rgba(249, 115, 22, 0.2);
    }
    .stButton>button:hover, form button:hover {
        background-color: #EA580C !important;
        transform: translateY(-1px);
    }
    .kpi-card {
        background-color: #FFFFFF;
        padding: 22px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        border-left: 4px solid #F97316;
        margin-bottom: 16px;
    }
    .produto-card {
        background-color: #FFFFFF;
        padding: 8px 10px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        height: 165px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 12px;
    }
    .produto-titulo {
        color: #0B2545;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        height: 24px;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        line-height: 1.1;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# GESTÃO DE ARQUIVOS LOCAIS (CSV)
# -------------------------------------------------------------
ARQUIVO_ESTOQUE = "estoque.csv"
ARQUIVO_HISTORICO = "historico.csv"
PASTA_IMAGENS = "imagens"

if not os.path.exists(PASTA_IMAGENS):
    os.makedirs(PASTA_IMAGENS)

if not os.path.exists(ARQUIVO_ESTOQUE):
    dados_iniciais = {
        "Produto": [
            "Telha Premium 1 Face", "Telha Premium 2 Face", "Telha Clara", "Telha Matizada", "Telha Vermelha", "Telha Tipo B", "Telha Tipo C",
            "Bloco 09x19x29 (Grande)", "Bloco 09x19x29 (Pequeno)", "Bloco 09x19x14", "Bloco de 09 Tipo B",
            "Bloco 11,5x19x29 (Grande)", "Bloco 11,5x19x29 (Pequeno)", "Bloco 11,5x19x14", "Bloco de 11,5 Tipo B",
            "Cumeeira Premium", "Cumeeira Clara", "Cumeeira Matizada", "Cumeeira Vermelha",
            "Jerusalém Claro", "Jerusalém Matizado", "Siena Claro", "Loreto", "Lanciano"
        ],
        "Categoria": [
            "Telhas", "Telhas", "Telhas", "Telhas", "Telhas", "Telhas", "Telhas",
            "Blocos", "Blocos", "Blocos", "Blocos",
            "Blocos", "Blocos", "Blocos", "Blocos",
            "Cumeeiras", "Cumeeiras", "Cumeeiras", "Cumeeiras",
            "Revestimentos", "Revestimentos", "Revestimentos", "Revestimentos", "Revestimentos"
        ],
        "Unidade_Medida": [
            "Palete (468 un)", "Palete (468 un)", "Palete (468 un)", "Palete (468 un)", "Palete (468 un)", "Palete (468 un)", "Palete (468 un)",
            "Palete (468 un)", "Palete (234 un)", "Palete (250 un)", "Palete (234 un)",
            "Palete (360 un)", "Palete (180 un)", "Palete (270 un)", "Palete (180 un)",
            "Unidade", "Unidade", "Unidade", "Unidade",
            "Caixa", "Caixa", "Caixa", "Caixa", "Caixa"
        ],
        "Quantidade": [0.0] * 24,
        "Estoque_Minimo": [2340, 2340, 4680, 4680, 2340, 0, 0, 2340, 1170, 1250, 234, 1080, 720, 540, 180, 200, 600, 600, 300, 0, 0, 0, 0, 0]
    }
    pd.DataFrame(dados_iniciais).to_csv(ARQUIVO_ESTOQUE, index=False)

if not os.path.exists(ARQUIVO_HISTORICO):
    pd.DataFrame(columns=["Data_Hora", "Produto", "Operação", "Quantidade"]).to_csv(ARQUIVO_HISTORICO, index=False)

# -------------------------------------------------------------
# FATORES DE CONVERSÃO EXATOS POR PRODUTO
# -------------------------------------------------------------
FATORES_PALETE = {
    "Telha Premium 1 Face": 468, "Telha Premium 2 Face": 468, "Telha Clara": 468,
    "Telha Matizada": 468, "Telha Vermelha": 468, "Telha Tipo B": 468, "Telha Tipo C": 468,
    "Bloco 09x19x29 (Grande)": 468, "Bloco 09x19x29 (Pequeno)": 234, "Bloco 09x19x14": 250, "Bloco de 09 Tipo B": 234,
    "Bloco 11,5x19x29 (Grande)": 360, "Bloco 11,5x19x29 (Pequeno)": 180, "Bloco 11,5x19x14": 270, "Bloco de 11,5 Tipo B": 180,
    "Cumeeira Premium": 1, "Cumeeira Clara": 1, "Cumeeira Matizada": 1, "Cumeeira Vermelha": 1
}

def obter_fator(produto: str) -> int:
    return FATORES_PALETE.get(produto, 468)

def obter_caminho_imagem(produto: str) -> str:
    nfkd_form = unicodedata.normalize('NFKD', produto)
    produto_sem_acento = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    
    nome_arquivo = produto_sem_acento.lower().replace(" ", "_").replace("(", "").replace(")", "").replace(",", "") + ".png"
    caminho = os.path.join(PASTA_IMAGENS, nome_arquivo)
    return caminho if os.path.exists(caminho) else None

# -------------------------------------------------------------
# FUNÇÕES DE SUPORTE A NÚMEROS
# -------------------------------------------------------------
def converter_para_float(valor) -> float:
    if pd.isna(valor) or valor is None or valor == "":
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    
    val_str = str(valor).strip().replace(',', '.')
    try:
        return float(val_str)
    except ValueError:
        return 0.0

def carregar_dados_estoque() -> pd.DataFrame:
    df = pd.read_csv(ARQUIVO_ESTOQUE)
    if not df.empty and "Quantidade" in df.columns:
        df["Quantidade"] = [converter_para_float(v) for v in df["Quantidade"]]
        df["Quantidade"] = df["Quantidade"].astype(float)
    return df

def salvar_estoque_local(df: pd.DataFrame):
    df.to_csv(ARQUIVO_ESTOQUE, index=False)

def carregar_dados_historico() -> pd.DataFrame:
    try:
        return pd.read_csv(ARQUIVO_HISTORICO)
    except Exception:
        return pd.DataFrame(columns=["Data_Hora", "Produto", "Operação", "Quantidade"])

def adicionar_historico(data_hora, produto, operacao, quantidade):
    df_hist = carregar_dados_historico()
    nova_linha = pd.DataFrame([[data_hora, produto, operacao, quantidade]], columns=["Data_Hora", "Produto", "Operação", "Quantidade"])
    df_hist = pd.concat([df_hist, nova_linha], ignore_index=True)
    df_hist.to_csv(ARQUIVO_HISTORICO, index=False)

try:
    df_estoque = carregar_dados_estoque()
except Exception as err:
    st.error(f"Erro ao ler o arquivo de estoque: {err}")
    st.stop()

# -------------------------------------------------------------
# CABEÇALHO DO PAINEL
# -------------------------------------------------------------
def exibir_cabecalho():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<h1 style='margin-bottom: 0px; font-size: 28px;'>Controle de Estoque</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748B; margin-top: 4px;'>Acompanhe em tempo real o saldo dos produtos.</p>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='text-align: right; color: #334155; font-size: 13px; padding-top: 12px;'><b>{obter_data_portugues()}</b></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# TELA DE LOGIN
# -------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.perfil = None

if not st.session_state.autenticado:
    exibir_cabecalho()
    st.markdown("---")
    _, col_centro, _ = st.columns([1, 1.2, 1])
    with col_centro:
        st.markdown("""
            <div style="background: white; padding: 30px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                <h3 style="margin-top: 0; color: #0B2545;">🔐 Acesso ao Sistema</h3>
        """, unsafe_allow_html=True)
        with st.form("form_login"):
            usuario = st.text_input("Utilizador:")
            senha = st.text_input("Palavra-passe:", type="password")
            botao_login = st.form_submit_button("Entrar no Sistema", use_container_width=True)
            
            if botao_login:
                if usuario == "vendas" and senha == "vendas123":
                    st.session_state.autenticado = True
                    st.session_state.perfil = "Vendas"
                    st.rerun()
                elif usuario == "patio" and senha == "patio123":
                    st.session_state.autenticado = True
                    st.session_state.perfil = "Pátio"
                    st.rerun()
                elif usuario == "adm" and senha == "ceramica123":
                    st.session_state.autenticado = True
                    st.session_state.perfil = "Administrador"
                    st.rerun()
                else:
                    st.error("Utilizador ou palavra-passe incorretos.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# -------------------------------------------------------------
# MENU LATERAL E NAVEGAÇÃO
# -------------------------------------------------------------
exibir_cabecalho()
st.sidebar.markdown("### 👤 Utilizador")
st.sidebar.markdown(f"Perfil: **{st.session_state.perfil}**")

if st.sidebar.button("🚪 Terminar Sessão", use_container_width=True):
    st.session_state.autenticado = False
    st.session_state.perfil = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### Navegação")
if st.session_state.perfil == "Vendas":
    opcoes_menu = ["📦 Estoque", "ℹ️ Ficha Técnica"]
elif st.session_state.perfil == "Pátio":
    opcoes_menu = ["📦 Estoque", "⚙️ Lançamentos", "ℹ️ Ficha Técnica"]
else:
    opcoes_menu = ["📦 Estoque", "⚙️ Lançamentos", "📜 Histórico", "ℹ️ Ficha Técnica"]

opcao = st.sidebar.radio("Menu", opcoes_menu, label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.caption("Cerâmica Simonassi © 2026")

# -------------------------------------------------------------
# 1. PAINEL DE ESTOQUE (DASHBOARD)
# -------------------------------------------------------------
if opcao == "📦 Estoque":
    st.markdown("---")
    
    if st.session_state.perfil == "Administrador":
        total_unidades_geral = sum(
            converter_para_float(row["Quantidade"]) * obter_fator(row["Produto"]) 
            if row["Categoria"] in ["Telhas", "Blocos"] 
            else converter_para_float(row["Quantidade"])
            for _, row in df_estoque.iterrows()
        )

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"""
            <div class="kpi-card">
                <div style="color: #64748B; font-size: 12px; font-weight: 700; letter-spacing: 0.5px;">ESTOQUE TOTAL GERAL</div>
                <div style="color: #0B2545; font-size: 24px; font-weight: 700; margin-top: 6px;">{int(total_unidades_geral):,} unidades</div>
            </div>
        """, unsafe_allow_html=True)
        
        c2.markdown(f"""
            <div class="kpi-card" style="border-left-color: #10B981;">
                <div style="color: #64748B; font-size: 12px; font-weight: 700; letter-spacing: 0.5px;">GRUPOS DE PRODUTOS</div>
                <div style="color: #0B2545; font-size: 24px; font-weight: 700; margin-top: 6px;">{len(df_estoque['Categoria'].unique())} categorias</div>
            </div>
        """, unsafe_allow_html=True)
        
        c3.markdown(f"""
            <div class="kpi-card" style="border-left-color: #3B82F6;">
                <div style="color: #64748B; font-size: 12px; font-weight: 700; letter-spacing: 0.5px;">ESTADO DA LIGAÇÃO</div>
                <div style="color: #10B981; font-size: 18px; font-weight: 700; margin-top: 8px;">● Armazenamento Local Estável</div>
            </div>
        """, unsafe_allow_html=True)

    ordem_desejada = ['Telhas', 'Blocos', 'Cumeeiras', 'Revestimentos']
    df_estoque['Categoria_Ordem'] = pd.Categorical(df_estoque['Categoria'], categories=ordem_desejada, ordered=True)
    df_estoque = df_estoque.sort_values('Categoria_Ordem').reset_index(drop=True)

    categorias = ["Todas"] + [c for c in ordem_desejada if c in df_estoque["Categoria"].unique()]
    cat_selecionada = st.selectbox("Filtrar Categoria:", categorias)
    
    df_exibicao = df_estoque.copy()
    if cat_selecionada != "Todas":
        df_exibicao = df_exibicao[df_exibicao["Categoria"] == cat_selecionada]
        
    cols = st.columns(7)
    for idx, (_, row) in enumerate(df_exibicao.iterrows()):
        col_atual = cols[idx % 7]
        
        produto_nome = row['Produto']
        qtd_informada = converter_para_float(row['Quantidade'])
        estoque_min = converter_para_float(row.get('Estoque_Minimo', 0))
        categoria = row['Categoria']
        
        if categoria in ["Telhas", "Blocos"]:
            fator = obter_fator(produto_nome)
            total_unidades = int(round(qtd_informada * fator))
            
            if qtd_informada.is_integer():
                valor_principal = f"{int(qtd_informada)}"
            else:
                valor_principal = f"{qtd_informada:.1f}".replace(".", ",")
                
            unidade_texto = "paletes"
            detalhe_sub = f"Total: {total_unidades:,} un".replace(".", ",")
        elif categoria == "Cumeeiras":
            total_unidades = int(qtd_informada)
            if qtd_informada.is_integer():
                valor_principal = f"{int(qtd_informada):,}".replace(".", ",")
            else:
                valor_principal = f"{qtd_informada:.1f}".replace(".", ",")
            unidade_texto = "unidades"
            detalhe_sub = "Estoque Unidades"
        elif categoria == "Revestimentos":
            total_unidades = int(qtd_informada)
            if qtd_informada.is_integer():
                valor_principal = f"{int(qtd_informada):,}".replace(".", ",")
            else:
                valor_principal = f"{qtd_informada:.1f}".replace(".", ",")
            unidade_texto = "caixas"
            detalhe_sub = "Estoque Caixas"
        else:
            total_unidades = int(qtd_informada)
            valor_principal = f"{total_unidades:,}".replace(".", ",")
            unidade_texto = "unidades"
            detalhe_sub = "Estoque Geral"
        
        alerta_html = ""
        if total_unidades < estoque_min:
            alerta_html = '<div style="background-color: #FEE2E2; color: #991B1B; padding: 1px 3px; border-radius: 4px; font-size: 7px; font-weight: bold; margin-top: 1px; text-align: center;">⚠️ ABAIXO DO MÍNIMO</div>'
        
        caminho_img = obter_caminho_imagem(produto_nome)
        img_html = ""
        if caminho_img:
            with open(caminho_img, "rb") as img_file:
                encoded_img = base64.b64encode(img_file.read()).decode()
            img_html = f"<div style='text-align: center; height: 75px; display: flex; align-items: center; justify-content: center; margin-bottom: 2px;'><img src='data:image/png;base64,{encoded_img}' style='max-height: 75px; max-width: 75px; object-fit: contain;'/></div>"
        else:
            img_html = "<div style='text-align: center; height: 75px; display: flex; align-items: center; justify-content: center; font-size: 26px; margin-bottom: 2px;'>📦</div>"

        card_html = f"""<div class="produto-card"><div>{img_html}<div class="produto-titulo" title="{produto_nome}">{produto_nome}</div><div style="color: #64748B; font-size: 8px; margin-bottom: 2px;">{categoria}</div></div><div><div style="color: #0B2545; font-size: 15px; font-weight: 800; line-height: 1.1;">{valor_principal} <span style="font-size: 10px; font-weight: 600; color: #64748B;">{unidade_texto}</span></div><div style="color: #059669; font-size: 10px; font-weight: 700; margin-top: 1px;">{detalhe_sub}</div>{alerta_html}</div></div>"""

        with col_atual:
            st.markdown(card_html, unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. ÁREA DE LANÇAMENTOS
# -------------------------------------------------------------
elif opcao == "⚙️ Lançamentos":
    st.markdown("### ⚙️ Registo de Movimentações")
    st.markdown("---")
    
    produto_sel = st.selectbox("Selecione o Produto:", df_estoque["Produto"].tolist())
    row_prod = df_estoque[df_estoque["Produto"] == produto_sel].iloc[0]
    cat_prod = row_prod["Categoria"]
    fator_atual = obter_fator(produto_sel)
    
    if st.session_state.perfil == "Pátio":
        opcoes_operacao = ["✏️ Ajuste manual (correção)"]
    else:
        opcoes_operacao = ["➕ Entrada (Nova Fornada)", "➖ Saída (Venda/Entrega)", "✏️ Ajuste manual (correção)"]
        
    tipo_movimento = st.radio("Operação:", opcoes_operacao, horizontal=True)
    
    tipo_unidade_saida = "Paletes"
    if cat_prod in ["Telhas", "Blocos"] and "Saída" in tipo_movimento:
        tipo_unidade_saida = st.radio("Formato de Saída:", ["Paletes", "Unidades Avulsas"], horizontal=True)

    with st.form("form_movimentacao"):
        qtd_lancada = 0.0
        novo_valor_texto = ""
        num_requisicao = ""
        num_flyer = ""
        
        if "Saída" in tipo_movimento:
            num_requisicao = st.text_input("Número da Requisição / Pedido (Ex: 40507/01):")

        if cat_prod in ["Telhas", "Blocos"] and "Entrada" in tipo_movimento:
            num_flyer = st.text_input("Número do Flyer / Palete (Ex: 5705):")
            if cat_prod == "Blocos":
                st.info("ℹ️ Os blocos aceitam apenas lotes fechados de 1 palete na entrada.")
                qtd_lancada = 1.0
            else:
                qtd_opcao = st.selectbox("Quantidade do Flyer:", [0.5, 1.0], format_func=lambda x: f"{x} Palete ({int(x * fator_atual)} unidades)")
                qtd_lancada = float(qtd_opcao)

        if "Ajuste manual" in tipo_movimento:
            qt_atual_form = converter_para_float(row_prod["Quantidade"])
            val_inicial_str = f"{qt_atual_form:.1f}".replace('.', ',')
            novo_valor_texto = st.text_input(
                f"Novo Total Correto ({'em Paletes' if cat_prod in ['Telhas', 'Blocos'] else 'em Unidades/Caixas'}):", 
                value=val_inicial_str
            )
        else:
            if cat_prod in ["Telhas", "Blocos"] and "Saída" in tipo_movimento and tipo_unidade_saida == "Paletes":
                qtd_lancada = st.number_input(f"Paletes de Saída ({fator_atual} un cada):", min_value=0.5, step=0.5, format="%.1f")
            elif cat_prod in ["Telhas", "Blocos"] and "Saída" in tipo_movimento:
                qtd_lancada = st.number_input("Unidades Avulsas de Saída:", min_value=1.0, step=1.0)
            elif cat_prod == "Revestimentos":
                qtd_lancada = st.number_input("Quantidade em Caixas:", min_value=1.0, step=1.0)
            else:
                qtd_lancada = st.number_input("Quantidade em Unidades:", min_value=1.0, step=1.0)
        
        submeter = st.form_submit_button("Confirmar e Registar Movimentação")
        
        if submeter:
            idx = df_estoque[df_estoque["Produto"] == produto_sel].index[0]
            qt_atual = converter_para_float(df_estoque.loc[idx, "Quantidade"])
            data_hora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            if "Ajuste manual" in tipo_movimento:
                nova_qtd = converter_para_float(novo_valor_texto)
                operacao_str = "Ajuste Manual"
                quantidade_str = f"{nova_qtd:.1f} paletes".replace('.', ',') if cat_prod in ["Telhas", "Blocos"] else f"{int(nova_qtd)} un"
            else:
                if cat_prod in ["Telhas", "Blocos"] and "Saída" in tipo_movimento and tipo_unidade_saida == "Unidades Avulsas":
                    paletes_exatos = float(qtd_lancada) / fator_atual
                    paletes_arredondados = round(paletes_exatos * 2) / 2
                    if paletes_arredondados == 0:
                        paletes_arredondados = 0.5
                    nova_qtd = qt_atual - paletes_arredondados
                    req_info = f" - Pedido: {num_requisicao}" if num_requisicao.strip() else ""
                    operacao_str = f"Saída (Unidades Avulsas){req_info}"
                    quantidade_str = f"-{int(qtd_lancada)} un"
                else:
                    if "Entrada" in tipo_movimento:
                        nova_qtd = qt_atual + float(qtd_lancada)
                        flyer_info = f" - Flyer: {num_flyer}" if num_flyer.strip() else ""
                        operacao_str = f"Entrada{flyer_info}" if cat_prod in ["Telhas", "Blocos"] else "Entrada"
                        quantidade_str = f"+{float(qtd_lancada)} paletes".replace('.', ',') if cat_prod in ["Telhas", "Blocos"] else f"+{int(qtd_lancada)} un"
                    else:
                        nova_qtd = qt_atual - float(qtd_lancada)
                        req_info = f" - Pedido: {num_requisicao}" if num_requisicao.strip() else ""
                        operacao_str = f"Saída{req_info}"
                        quantidade_str = f"-{float(qtd_lancada)} paletes".replace('.', ',') if cat_prod in ["Telhas", "Blocos"] else f"-{float(qtd_lancada)} un"
                    
            if nova_qtd < 0:
                st.error("Erro: O estoque não pode ficar com valores negativos!")
            else:
                df_estoque.loc[idx, "Quantidade"] = round(float(nova_qtd), 2)
                salvar_estoque_local(df_estoque)
                adicionar_historico(data_hora_str, str(produto_sel), str(operacao_str), str(quantidade_str))
                
                st.success(f"Estoque de **{produto_sel}** atualizado com sucesso!")
                time.sleep(1.5)
                st.rerun()

# -------------------------------------------------------------
# 3. HISTÓRICO DE MOVIMENTAÇÕES
# -------------------------------------------------------------
elif opcao == "📜 Histórico":
    st.markdown("### 📜 Histórico de Movimentações")
    st.markdown("Auditoria completa das entradas e saídas do pátio.")
    st.markdown("---")
    
    try:
        df_hist_exibicao = carregar_dados_historico()
        if not df_hist_exibicao.empty:
            st.dataframe(df_hist_exibicao, use_container_width=True, hide_index=True)
            
            if st.session_state.perfil == "Administrador":
                st.markdown("---")
                st.subheader("🛠️ Gestão do Histórico")
                opcoes_linhas = [f"Linha {i} | Data: {row['Data_Hora']} | Produto: {row['Produto']} | Op: {row['Operação']}" for i, row in df_hist_exibicao.iterrows()]
                linha_selecionada = st.selectbox("Selecione o registo para excluir:", opcoes_linhas)
                
                if st.button("🗑️ Remover Registo Selecionado"):
                    idx_para_remover = int(linha_selecionada.split()[1])
                    df_hist_atualizado = df_hist_exibicao.drop(index=idx_para_remover).reset_index(drop=True)
                    df_hist_atualizado.to_csv(ARQUIVO_HISTORICO, index=False)
                    st.success("Registo removido com sucesso!")
                    time.sleep(1.5)
                    st.rerun()
        else:
            st.info("Ainda não existem movimentações registadas.")
    except Exception as e:
        st.warning(f"Erro ao carregar o histórico: {e}")

# -------------------------------------------------------------
# 4. FICHA TÉCNICA DOS PRODUTOS
# -------------------------------------------------------------
elif opcao == "ℹ️ Ficha Técnica":
    st.markdown("### ℹ️ Ficha Técnica e Especificações")
    st.markdown("Consulte o peso, rendimento e galga mínima dos produtos da Cerâmica Simonassi.")
    st.markdown("---")
    
    fichas_tecnicas = [
        {"Produto": "Bloco 09x19x29 (Grande)", "Peso": "4,125 kg", "Rendimento": "16 / m²", "Galga": "—", "Categoria": "Blocos"},
        {"Produto": "Bloco 11,5x19x29 (Grande)", "Peso": "5 kg", "Rendimento": "16 / m²", "Galga": "—", "Categoria": "Blocos"},
        {"Produto": "Telha Clara", "Peso": "3,4 kg", "Rendimento": "11,5 T / m²", "Galga": "38,3 cm", "Categoria": "Telhas"},
        {"Produto": "Telha Vermelha", "Peso": "3,1 kg", "Rendimento": "12 T / m²", "Galga": "37,4 cm", "Categoria": "Telhas"},
        {"Produto": "Cumeeira Clara", "Peso": "2,720 kg", "Rendimento": "3 por metro linear", "Galga": "—", "Categoria": "Cumeeiras"},
        {"Produto": "Jerusalém Claro", "Peso": "21,6 kg (caixa)", "Rendimento": "83 peças / m²", "Galga": "—", "Categoria": "Revestimentos"}
    ]
    
    cols_tec = st.columns(4)
    for idx, item in enumerate(fichas_tecnicas):
        col_atual = cols_tec[idx % 4]
        
        prod_nome = item["Produto"]
        peso = item["Peso"]
        rendimento = item["Rendimento"]
        galga = item["Galga"]
        cat = item["Categoria"]
        
        caminho_img = obter_caminho_imagem(prod_nome)
        img_html = ""
        if caminho_img:
            with open(caminho_img, "rb") as img_file:
                encoded_img = base64.b64encode(img_file.read()).decode()
            img_html = f"<div style='text-align: center; height: 75px; display: flex; align-items: center; justify-content: center; margin-bottom: 2px;'><img src='data:image/png;base64,{encoded_img}' style='max-height: 75px; max-width: 75px; object-fit: contain;'/></div>"
        else:
            img_html = "<div style='text-align: center; height: 75px; display: flex; align-items: center; justify-content: center; font-size: 26px; margin-bottom: 2px;'>🧱</div>"

        # Altura aumentada para 220px e letras ajustadas para 12px
        card_tec_html = f"""
        <div class="produto-card" style="height: 220px;">
            <div>
                {img_html}
                <div class="produto-titulo" style="font-size: 11px;" title="{prod_nome}">{prod_nome}</div>
                <div style="color: #64748B; font-size: 9px; margin-bottom: 4px;">{cat}</div>
            </div>
            <div style="border-top: 1px solid #E2E8F0; padding-top: 4px;">
                <div style="color: #0B2545; font-size: 12px;">⚖️ Peso: <b>{peso}</b></div>
                <div style="color: #0B2545; font-size: 12px;">📐 Rend.: <b>{rendimento}</b></div>
                <div style="color: #0B2545; font-size: 12px;">📏 Galga: <b>{galga}</b></div>
            </div>
        </div>
        """

        with col_atual:
            st.markdown(card_tec_html, unsafe_allow_html=True)