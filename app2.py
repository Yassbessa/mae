import streamlit as st
import urllib.parse
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import date, datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- REGRAS DE ENDEREÇO PARA O CUPOM ---
ENDERECO_OFICIAL = "RUA VINTE E QUATRO DE MAIO"
NUMERO_OFICIAL = "85"
CEPS_VALIDOS = ["20950-085", "20950-090"]

# --- MEMÓRIA DO APP ---
if 'etapa' not in st.session_state:
    st.session_state.etapa = "boas_vindas"
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

# ==========================================
# TELA 1: BOAS-VINDAS
# ==========================================
if st.session_state.etapa == "boas_vindas":
    st.markdown("<h1 style='text-align: center; color: #E67E22;'>Ja Que É Doce 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    c1, c2 = st.columns(2)
    if c1.button("🔑 LOGIN CLIENTE", use_container_width=True):
        st.session_state.etapa = "login"
        st.rerun()
    if c2.button("✨ NOVO CADASTRO", use_container_width=True):
        st.session_state.etapa = "cadastro"
        st.rerun()

# ==========================================
# TELA 2: LOGIN
# ==========================================
elif st.session_state.etapa == "login":
    st.title("👤 Identificação")
    user_log = st.text_input("Nome:")
    pass_log = st.text_input("Senha:", type="password")
    
    if st.button("ACESSAR 🚀"):
        try:
            df_users = conn.read(worksheet="Usuarios")
            # Procura o usuário
            match = df_users[(df_users['NOME'] == user_log) & (df_users['SENHA'] == str(pass_log))]
            if not match.empty:
                st.session_state.usuario = match.iloc[0].to_dict()
                st.session_state.etapa = "cardapio"
                st.rerun()
            else:
                st.error("Nome ou Senha incorretos.")
        except:
            st.error("Erro ao carregar banco de dados.")

    if st.button("⬅️ Voltar"):
        st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 3: CADASTRO (COM DATA DESDE 1930)
# ==========================================
elif st.session_state.etapa == "cadastro":
    st.title("📝 Cadastro de Cliente")
    n_nome = st.text_input("Nome Completo:")
    n_pass = st.text_input("Crie uma Senha:", type="password")
    # Ajuste para data desde 1930 como solicitado
    n_nasc = st.date_input("Sua Data de Nascimento:", 
                           min_value=date(1930, 1, 1), 
                           max_value=date.today(),
                           value=date(2000, 1, 1))
    n_end = st.text_input("Endereço (Ex: Rua Vinte e Quatro de Maio, 85):")
    n_cep = st.text_input("CEP:")
    n_inst = st.text_area("Instruções (Ex: Apto 902, Deixar na portaria):")

    if st.button("FINALIZAR CADASTRO ✨"):
        if n_nome and n_pass and n_cep:
            # Resolvendo o erro de UnsupportedOperationError usando update
            df_old = conn.read(worksheet="Usuarios")
            df_new = pd.DataFrame([{
                "NOME": n_nome, "SENHA": n_pass, "NASCIMENTO": n_nasc.strftime("%d/%m"),
                "ENDERECO": n_end.upper(), "CEP": n_cep, "INSTRUCOES": n_inst
            }])
            df_total = pd.concat([df_old, df_new], ignore_index=True)
            conn.update(worksheet="Usuarios", data=df_total)
            
            st.success("Cadastro realizado! Faça seu login.")
            st.session_state.etapa = "login"; st.rerun()
        else:
            st.error("Preencha todos os campos!")

# ==========================================
# TELA 4: CARDÁPIO COM TRAVA DE CUPOM
# ==========================================
elif st.session_state.etapa == "cardapio":
    u = st.session_state.usuario
    st.title(f"Olá, {u['NOME']}! 🍦")
    
    # Check Aniversário
    hoje = date.today().strftime("%d/%m")
    if u['NASCIMENTO'] == hoje:
        st.balloons(); st.success("🎂 PARABÉNS! Hoje você tem direito ao brinde de aniversário!")

    # LOGICA DO CUPOM RESTRITO
    cupom = st.text_input("Possui Cupom?").strip().upper()
    desconto_morador = False
    
    if cupom == "MACHADORIBEIRO":
        # Validação do endereço e CEP
        if ENDERECO_OFFICIAL in u['ENDERECO'] and NUMERO_OFFICIAL in u['ENDERECO'] and u['CEP'] in CEPS_VALIDOS:
            st.success("Desconto morador aplicado! ✅")
            desconto_morador = True
        else:
            st.error("Este cupom é exclusivo para moradores da Rua Vinte e Quatro de Maio, 85.")

    # ... (Resto do código do cardápio com preços p_gourmet = 7 se desconto_morador else 9)
