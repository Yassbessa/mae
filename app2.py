import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import date, datetime

st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")

# URL DO SEU APPS SCRIPT (Versão 2)
URL_WEB_APP = "https://script.google.com/macros/s/AKfycbyByTKemIrdGk7y6HnHAGC-d8Vgxu_WoeVAdsBh8mLcR44-XQbSKY3E827lFT49i1YhBA/exec"

if 'etapa' not in st.session_state: st.session_state.etapa = "boas_vindas"
if 'user' not in st.session_state: st.session_state.user = None

def ler_dados(aba):
    try:
        response = requests.get(f"{URL_WEB_APP}?aba={aba}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1:
                return pd.DataFrame(data[1:], columns=data[0])
            else:
                st.warning(f"A aba '{aba}' está vazia ou sem cabeçalhos.")
        else:
            st.error(f"Erro no Script: Status {response.status_code}")
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
    return pd.DataFrame()

# TELA DE LOGIN
if st.session_state.etapa == "login":
    st.title("👤 Login")
    email_log = st.text_input("E-mail cadastrado:").strip().lower()
    p_log = st.text_input("Senha:", type="password").strip()
    
    col_l1, col_l2 = st.columns(2)
    if col_l1.button("ACESSAR 🚀", type="primary", use_container_width=True):
        with st.spinner('Verificando credenciais...'):
            df_u = ler_dados("Usuarios")
            
            if not df_u.empty:
                # Limpa espaços e garante que a comparação seja justa
                df_u['EMAIL'] = df_u['EMAIL'].str.strip().str.lower()
                df_u['SENHA'] = df_u['SENHA'].astype(str).str.strip()
                
                match = df_u[(df_u['EMAIL'] == email_log) & (df_u['SENHA'] == p_log)]
                
                if not match.empty:
                    st.session_state.user = match.iloc[0].to_dict()
                    st.session_state.etapa = "cardapio"
                    st.rerun()
                else:
                    # Se não abriu o cardápio, ele vai mostrar este erro aqui:
                    st.error("❌ E-mail ou Senha não encontrados. Verifique se você já se cadastrou ou se digitou corretamente.")
            else:
                st.info("💡 Dica: Verifique se você criou a aba 'Usuarios' na sua planilha do Google.")

# ... (Restante do código de Cadastro e Cardápio continua igual)
