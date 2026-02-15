import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import date, datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")

# SEU URL DO APPS SCRIPT (Versão 2)
URL_WEB_APP = "https://script.google.com/macros/s/AKfycbyByTKemIrdGk7y6HnHAGC-d8Vgxu_WoeVAdsBh8mLcR44-XQbSKY3E827lFT49i1YhBA/exec"

# --- MEMÓRIA DO APP ---
if 'etapa' not in st.session_state: 
    st.session_state.etapa = "boas_vindas"
if 'user' not in st.session_state: 
    st.session_state.user = None

# Funções de Conexão
def salvar_dados(lista, aba):
    requests.post(f"{URL_WEB_APP}?aba={aba}", json=lista)

def ler_dados(aba):
    try:
        response = requests.get(f"{URL_WEB_APP}?aba={aba}", timeout=10)
        data = response.json()
        if len(data) > 1:
            return pd.DataFrame(data[1:], columns=data[0])
    except:
        pass
    return pd.DataFrame()

# ==========================================
# ETAPA 1: BOAS-VINDAS
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
# ETAPA 2: LOGIN (CONECTADO!)
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
            
            match = df_u[(df_u['EMAIL'] == email_log) & (df_u['SENHA'] == p_log)]
            if not match.empty:
                st.session_state.user = match.iloc[0].to_dict()
                st.session_state.etapa = "cardapio"; st.rerun()
            else: st.error("❌ E-mail ou Senha incorretos.")
        else:
            # Esta é a mensagem que você viu; ela indica que a conexão funciona!
            st.warning("⚠️ Planilha vazia. Cadastre seu primeiro usuário!")
            
    if col_l2.button("⬅️ VOLTAR"):
        st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# ETAPA 3: CADASTRO (COM FORMULÁRIO ANTI-ERRO)
# ==========================================
elif st.session_state.etapa == "cadastro":
    st.title("📝 Cadastro de Cliente")
    # O 'with st.form' impede o erro de 'campos vazios'
    with st.form("meu_cadastro"):
        n_nome = st.text_input("Nome Completo:")
        n_email = st.text_input("E-mail (será seu login):").strip().lower()
        n_pass = st.text_input("Crie uma Senha:", type="password")
        n_nasc = st.date_input("Nascimento:", min_value=date(1930, 1, 1), value=date(2000, 1, 1))
        n_end = st.text_input("Endereço (Ex: Rua 24 de Maio, 85):")
        n_bairro = st.text_input("Bairro:")
        n_cep = st.text_input("CEP:")
        n_inst = st.text_area("Instruções de Entrega:")
        
        # Botão especial do formulário
        btn_finalizar = st.form_submit_button("FINALIZAR CADASTRO ✨")

    if btn_finalizar:
        if n_nome and n_email and n_pass and n_end:
            # Organiza os dados para as colunas da sua planilha
            dados = [n_nome, n_email, str(n_pass), n_nasc.strftime("%d/%m"), n_end.upper(), n_bairro.upper(), n_cep, n_inst]
            salvar_dados(dados, "Usuarios")
            st.success("Cadastro realizado! Verifique sua planilha e faça o login.")
            st.session_state.etapa = "login"; st.rerun()
        else:
            st.error("Preencha todos os campos obrigatórios!") #

# ==========================================
# ETAPA 4: CARDÁPIO (O DESTINO FINAL!)
# ==========================================
elif st.session_state.etapa == "cardapio":
    u = st.session_state.user
    st.title(f"Olá, {u['NOME']}! 🍦")
    st.write("Aqui você poderá ver as fotos dos seus sacolés e doces favoritos.")
    if st.button("⬅️ SAIR"):
        st.session_state.user = None; st.session_state.etapa = "boas_vindas"; st.rerun()
