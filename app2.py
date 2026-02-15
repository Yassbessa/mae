import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import date, datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Painel Ja Que É Doce", page_icon="🐝", layout="wide")

# SEU URL DO APPS SCRIPT
URL_WEB_APP = "https://script.google.com/macros/s/AKfycbyl8rhT4ucrbMj9010RCw9Y94KOs-apa-DW9qmDSDFEhP3vT-UiD7Wzz6tdq0ja46Ga7Q/exec"

# --- LOGIN DO MODERADOR ---
EMAIL_ADMIN = "admin"
SENHA_ADMIN = "jqd9191" 

# --- MEMÓRIA DO APP ---
if 'etapa' not in st.session_state: st.session_state.etapa = "boas_vindas"
if 'user' not in st.session_state: st.session_state.user = None

# --- FUNÇÕES DE CONEXÃO ---
def salvar_dados(lista, aba):
    try:
        r = requests.post(f"{URL_WEB_APP}?aba={aba}", json=lista, timeout=15)
        return True if "Sucesso" in r.text else False
    except: return False

def ler_dados(aba):
    try:
        response = requests.get(f"{URL_WEB_APP}?aba={aba}", timeout=10)
        data = response.json()
        if len(data) > 1: return pd.DataFrame(data[1:], columns=data[0])
    except: pass
    return pd.DataFrame()

# ==========================================
# TELA 1: BOAS-VINDAS
# ==========================================
if st.session_state.etapa == "boas_vindas":
    st.markdown("<h1 style='text-align: center; color: #E67E22;'>Ja Que É Doce 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    c1, c2 = st.columns(2)
    if c1.button("🔑 ENTRAR / LOGIN", use_container_width=True):
        st.session_state.etapa = "login"; st.rerun()
    if c2.button("✨ CADASTRAR NOVO CLIENTE", use_container_width=True):
        st.session_state.etapa = "cadastro"; st.rerun()

# ==========================================
# TELA 2: LOGIN (CLIENTE OU MODERADOR)
# ==========================================
elif st.session_state.etapa == "login":
    st.title("👤 Identificação")
    email_log = st.text_input("E-mail:").strip().lower()
    p_log = st.text_input("Senha:", type="password").strip()
    
    col_l1, col_l2 = st.columns(2)
    if col_l1.button("ACESSAR 🚀", type="primary", use_container_width=True):
        # 1. Tenta Login de Moderador
        if email_log == EMAIL_ADMIN and p_log == SENHA_ADMIN:
            st.session_state.etapa = "moderador"; st.rerun()
        
        # 2. Tenta Login de Cliente
        else:
            df_u = ler_dados("Usuarios")
            if not df_u.empty:
                df_u['EMAIL'] = df_u['EMAIL'].astype(str).str.strip().str.lower()
                df_u['SENHA'] = df_u['SENHA'].astype(str).str.strip()
                match = df_u[(df_u['EMAIL'] == email_log) & (df_u['SENHA'] == p_log)]
                if not match.empty:
                    st.session_state.user = match.iloc[0].to_dict()
                    st.session_state.etapa = "cardapio"; st.rerun()
                else: st.error("❌ E-mail ou Senha incorretos.")
            else: st.warning("⚠️ Ninguém cadastrado ainda.")

    if col_l2.button("⬅️ VOLTAR", use_container_width=True):
        st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 3: CADASTRO DE CLIENTE
# ==========================================
elif st.session_state.etapa == "cadastro":
    st.title("📝 Cadastro de Cliente")
    with st.form("form_registro"):
        n_nome = st.text_input("Nome Completo:")
        n_email = st.text_input("E-mail (será seu login):")
        n_pass = st.text_input("Crie uma Senha:", type="password")
        n_nasc = st.date_input("Nascimento:", min_value=date(1930, 1, 1), value=date(2000, 1, 1))
        n_end = st.text_input("Endereço (Ex: Rua 24 de Maio, 85):")
        n_bairro = st.text_input("Bairro:")
        n_cep = st.text_input("CEP:")
        n_inst = st.text_area("Instruções de Entrega:")
        if st.form_submit_button("FINALIZAR CADASTRO ✨"):
            if n_nome and n_email and n_pass and n_end:
                dados = [n_nome, n_email.strip().lower(), str(n_pass), n_nasc.strftime("%d/%m"), n_end.upper(), n_bairro.upper(), n_cep, n_inst]
                if salvar_dados(dados, "Usuarios"):
                    st.success("✅ Cadastrado! Agora faça o login.")
                    st.session_state.etapa = "login"; st.rerun()
                else: st.error("Erro ao salvar. Verifique se a aba 'Usuarios' existe.")
            else: st.error("Preencha os campos obrigatórios!")
    if st.button("⬅️ Cancelar"): st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 4: CARDÁPIO (VISÃO DO CLIENTE)
# ==========================================
elif st.session_state.etapa == "cardapio":
    u = st.session_state.user
    st.title(f"Olá, {u['NOME']}! 🍦")
    st.info("💡 Bem-vindo à nossa lojinha!")
    
    # Exemplo de Item
    st.subheader("❄️ Sacolés Gourmet")
    qtd = st.number_input("Ninho com Nutella (R$ 9,00)", 0, 10)
    
    if qtd > 0:
        if st.button("🚀 FINALIZAR PEDIDO NO WHATSAPP"):
            venda = [datetime.now().strftime("%d/%m/%Y %H:%M"), u['NOME'], u['ENDEREÇO'], u['NASCIMENTO'], "Ninho com Nutella", qtd, 9.0, qtd*9.0, "PIX", u['INSTRUÇÕES']]
            salvar_dados(venda, "Vendas_Geral")
            msg = f"🍦 *NOVO PEDIDO*\n👤 {u['NOME']}\n📦 {qtd}x Ninho c/ Nutella"
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'https://wa.me/5521976141210?text={urllib.parse.quote(msg)}\' /">', unsafe_allow_html=True)

    if st.button("⬅️ Sair (Logout)"):
        st.session_state.user = None; st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 5: PAINEL DO MODERADOR (EXCLUSIVO PARA VOCÊ E SUA MÃE)
# ==========================================
elif st.session_state.etapa == "moderador":
    st.title("👑 Painel de Controle - Ja Que É Doce")
    st.write("Aqui você e sua mãe gerenciam o negócio.")
    
    if st.button("⬅️ Sair do Painel"):
        st.session_state.etapa = "boas_vindas"; st.rerun()

    tab1, tab2 = st.tabs(["👥 Lista de Clientes", "💰 Histórico de Vendas"])
    
    with tab1:
        st.subheader("Clientes Cadastrados")
        df_clientes = ler_dados("Usuarios")
        if not df_clientes.empty:
            st.dataframe(df_clientes, use_container_width=True)
            # Botão para baixar a lista
            csv = df_clientes.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar Lista de Clientes (CSV)", csv, "clientes.csv", "text/csv")
        else: st.info("Nenhum cliente cadastrado ainda.")

    with tab2:
        st.subheader("Pedidos Realizados")
        df_vendas = ler_dados("Vendas_Geral")
        if not df_vendas.empty:
            st.write(f"Total de pedidos no sistema: **{len(df_vendas)}**")
            st.dataframe(df_vendas, use_container_width=True)
            csv_v = df_vendas.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar Relatório de Vendas (CSV)", csv_v, "vendas.csv", "text/csv")
        else: st.info("Nenhuma venda registrada ainda.")
