import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import date, datetime

# --- CONFIGURAÇÃO (VOLTAMOS PARA O MODO CENTRALIZADO) ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")

# SEU URL DO APPS SCRIPT
URL_WEB_APP = "https://script.google.com/macros/s/AKfycbyl8rhT4ucrbMj9010RCw9Y94KOs-apa-DW9qmDSDFEhP3vT-UiD7Wzz6tdq0ja46Ga7Q/exec"

# --- LOGIN DO MODERADOR (VOCÊ E SUA MÃE) ---
EMAIL_ADMIN = "admin"
SENHA_ADMIN = "jqd9191" 

# --- MEMÓRIA DO APP ---
if 'etapa' not in st.session_state: st.session_state.etapa = "boas_vindas"
if 'user' not in st.session_state: st.session_state.user = None

# Funções de Conexão
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
    if c2.button("✨ CADASTRAR", use_container_width=True):
        st.session_state.etapa = "cadastro"; st.rerun()

# ==========================================
# TELA 2: LOGIN (AGORA COM ACESSO MODERADOR)
# ==========================================
elif st.session_state.etapa == "login":
    st.title("👤 Identificação")
    email_log = st.text_input("E-mail:").strip().lower()
    p_log = st.text_input("Senha:", type="password").strip()
    
    if st.button("ACESSAR 🚀", type="primary", use_container_width=True):
        # 1. Tenta entrar como Moderadora (Admin)
        if email_log == EMAIL_ADMIN and p_log == SENHA_ADMIN:
            st.session_state.etapa = "moderador"; st.rerun()
        
        # 2. Tenta entrar como Cliente comum
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
            else: 
                # Esta é a mensagem que você já viu!
                st.warning("⚠️ Planilha vazia. Cadastre-se primeiro!")

    if st.button("⬅️ VOLTAR"): st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 3: CADASTRO (FICOU MENOR E MELHOR AGORA!)
# ==========================================
elif st.session_state.etapa == "cadastro":
    st.title("📝 Cadastro de Cliente")
    with st.form("form_cad"):
        n_nome = st.text_input("Nome Completo:")
        n_email = st.text_input("E-mail (será seu login):") 
        n_pass = st.text_input("Crie uma Senha:", type="password")
        n_nasc = st.date_input("Nascimento:", min_value=date(1930, 1, 1), value=date(2000, 1, 1))
        n_end = st.text_input("Endereço (Rua e Número):")
        n_bairro = st.text_input("Bairro:")
        n_cep = st.text_input("CEP:")
        n_inst = st.text_area("Instruções de Entrega:")
        btn_cad = st.form_submit_button("FINALIZAR CADASTRO ✨")

    if btn_cad:
        if n_nome and n_email and n_pass and n_end:
            dados = [n_nome, n_email.strip().lower(), str(n_pass), n_nasc.strftime("%d/%m"), n_end.upper(), n_bairro.upper(), n_cep, n_inst]
            if salvar_dados(dados, "Usuarios"):
                st.success("✅ Tudo certo! Agora faça o login.")
                st.session_state.etapa = "login"; st.rerun()
            else: st.error("Erro técnico ao salvar. Tente de novo.")
        else: st.error("⚠️ Preencha todos os campos obrigatórios!")

# ==========================================
# TELA 5: PAINEL DA MODERADORA (SÓ VOCÊ E SUA MÃE)
# ==========================================
elif st.session_state.etapa == "moderador":
    st.title("👑 Painel de Controle - Moderadoras")
    st.write("Bem-vinda, Yasmin! Aqui vocês veem tudo sem abrir o Google.")
    
    if st.button("⬅️ SAIR DO PAINEL"):
        st.session_state.etapa = "boas_vindas"; st.rerun()

    tab1, tab2 = st.tabs(["👥 Clientes Cadastrados", "💰 Pedidos"])
    
    with tab1:
        df_c = ler_dados("Usuarios")
        if not df_c.empty: st.dataframe(df_c, use_container_width=True)
        else: st.info("Nenhum cliente cadastrado ainda.")

    with tab2:
        df_v = ler_dados("Vendas_Geral")
        if not df_v.empty: st.dataframe(df_v, use_container_width=True)
        else: st.info("Nenhuma venda realizada ainda.")
