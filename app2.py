import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import date, datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")

# SEU NOVO URL QUE VOCÊ ACABOU DE MANDAR
URL_WEB_APP = "https://script.google.com/macros/s/AKfycbyl8rhT4ucrbMj9010RCw9Y94KOs-apa-DW9qmDSDFEhP3vT-UiD7Wzz6tdq0ja46Ga7Q/exec"

# --- MEMÓRIA DO APP ---
if 'etapa' not in st.session_state: 
    st.session_state.etapa = "boas_vindas"
if 'user' not in st.session_state: 
    st.session_state.user = None

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
    if c1.button("🔑 ENTRAR (LOGIN)", use_container_width=True):
        st.session_state.etapa = "login"; st.rerun()
    if c2.button("✨ CADASTRAR", use_container_width=True):
        st.session_state.etapa = "cadastro"; st.rerun()

# ==========================================
# TELA 2: LOGIN (IDENTIFICAÇÃO)
# ==========================================
elif st.session_state.etapa == "login":
    st.title("👤 Identificação")
    email_log = st.text_input("E-mail cadastrado:").strip().lower()
    p_log = st.text_input("Senha:", type="password").strip()
    
    col_l1, col_l2 = st.columns(2)
    if col_l1.button("ACESSAR 🚀", type="primary", use_container_width=True):
        df_u = ler_dados("Usuarios")
        if not df_u.empty:
            df_u['EMAIL'] = df_u['EMAIL'].astype(str).str.strip().str.lower()
            df_u['SENHA'] = df_u['SENHA'].astype(str).str.strip()
            # O Login agora é feito pelo E-MAIL
            match = df_u[(df_u['EMAIL'] == email_log) & (df_u['SENHA'] == p_log)]
            if not match.empty:
                st.session_state.user = match.iloc[0].to_dict()
                st.session_state.etapa = "cardapio"; st.rerun()
            else: st.error("❌ E-mail ou Senha incorretos.")
        else: st.warning("⚠️ Planilha vazia. Cadastre-se primeiro!")

    if col_l2.button("⬅️ VOLTAR", use_container_width=True):
        st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 3: CADASTRO (RESOLVENDO O ERRO DE CAMPOS VAZIOS)
# ==========================================
elif st.session_state.etapa == "cadastro":
    st.title("📝 Cadastro de Cliente")
    with st.form("form_final"):
        n_nome = st.text_input("Nome Completo:")
        n_email = st.text_input("E-mail (será seu Login):") # CAMPO ESSENCIAL!
        n_pass = st.text_input("Crie uma Senha:", type="password")
        n_nasc = st.date_input("Nascimento:", min_value=date(1930, 1, 1), value=date(2000, 1, 1))
        n_end = st.text_input("Endereço (Ex: Rua 24 de Maio, 85):")
        n_bairro = st.text_input("Bairro:")
        n_cep = st.text_input("CEP:")
        n_inst = st.text_area("Instruções de Entrega:")
        btn_cad = st.form_submit_button("FINALIZAR CADASTRO ✨")

    if btn_cad:
        # Verifica se o E-mail e os outros campos principais estão lá
        if n_nome and n_email and n_pass and n_end:
            # Ordem exata das colunas na sua planilha
            dados = [n_nome, n_email.strip().lower(), str(n_pass), n_nasc.strftime("%d/%m"), n_end.upper(), n_bairro.upper(), n_cep, n_inst]
            if salvar_dados(dados, "Usuarios"):
                st.success("✅ Tudo certo! Agora você pode entrar com seu e-mail.")
                st.session_state.etapa = "login"; st.rerun()
            else: st.error("Erro ao salvar na planilha. Tente novamente.")
        else: st.error("⚠️ Por favor, preencha Nome, E-mail, Senha e Endereço!")

# ==========================================
# TELA 4: CARDÁPIO (O DESTINO FINAL!)
# ==========================================
elif st.session_state.etapa == "cardapio":
    u = st.session_state.user
    st.title(f"Olá, {u['NOME']}! 🍦")
    st.success("Login realizado com sucesso!")
    # Aqui você pode colocar a lista de sacolés
    if st.button("⬅️ SAIR (LOGOUT)"):
        st.session_state.user = None; st.session_state.etapa = "boas_vindas"; st.rerun()
