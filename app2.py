import streamlit as st
import pandas as pd
import sqlite3
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURAÇÃO (CENTRALIZADO AGORA) ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")

# --- 2. BANCO DE DADOS (COM CAMPO DE INSTRUÇÕES) ---
conn = sqlite3.connect('doceria.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
             (nome TEXT, email TEXT PRIMARY KEY, senha TEXT, endereco TEXT, bairro TEXT, instrucoes TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS vendas 
             (data TEXT, cliente_email TEXT, endereco TEXT, sabor TEXT, qtd INTEGER, total REAL, obs TEXT)''')
conn.commit()

# --- ADMIN ---
ADMIN_USER = "admin"
ADMIN_PASS = "jqd9191"

if 'etapa' not in st.session_state: st.session_state.etapa = "boas_vindas"
if 'user' not in st.session_state: st.session_state.user = None

# ==========================================
# TELA 1: BOAS-VINDAS
# ==========================================
if st.session_state.etapa == "boas_vindas":
    st.markdown("<h1 style='text-align: center; color: #E67E22;'>Ja Que É Doce 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    
    if st.button("🛍️ FAZER LOGIN / ENTRAR", use_container_width=True):
        st.session_state.etapa = "login"; st.rerun()
        
    if st.button("✨ CRIAR UMA CONTA NOVO", use_container_width=True):
        st.session_state.etapa = "cadastro"; st.rerun()

# ==========================================
# TELA 2: REGISTO (VAI DIRETO PRO LOGIN DEPOIS)
# ==========================================
elif st.session_state.etapa == "cadastro":
    st.title("📝 Cria a tua conta")
    with st.form("form_registo"):
        n_nome = st.text_input("Nome Completo:")
        n_email = st.text_input("E-mail:")
        n_pass = st.text_input("Escolhe uma Senha:", type="password")
        n_end = st.text_input("Endereço (Ex: Apto 302):")
        n_bairro = st.text_input("Bairro:")
        n_inst = st.text_area("Onde deixar a encomenda? (Ex: Portaria, Vaso de flores, Pendurar na porta)")
        
        if st.form_submit_button("FINALIZAR REGISTO ✨"):
            if n_nome and n_email and n_pass:
                try:
                    c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?)", 
                             (n_nome, n_email.lower(), n_pass, n_end, n_bairro, n_inst))
                    conn.commit()
                    st.success("Conta criada! A levar-te para o Login...")
                    st.session_state.etapa = "login" # VAI DIRETO PRO LOGIN
                    st.rerun()
                except:
                    st.error("Este e-mail já existe!")
            else:
                st.error("Preenche os campos obrigatórios!")
    
    if st.button("⬅️ Voltar"): st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 3: LOGIN
# ==========================================
elif st.session_state.etapa == "login":
    st.title("👤 Identificação")
    email_in = st.text_input("E-mail:").strip().lower()
    pass_in = st.text_input("Senha:", type="password")
    
    if st.button("ENTRAR 🚀", type="primary"):
        if email_in == ADMIN_USER and pass_in == ADMIN_PASS:
            st.session_state.etapa = "painel_admin"; st.rerun()
        
        c.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email_in, pass_in))
        res = c.fetchone()
        if res:
            st.session_state.user = {"nome": res[0], "email": res[1], "end": res[3], "inst": res[5]}
            st.session_state.etapa = "cardapio"; st.rerun()
        else:
            st.error("Dados incorretos!")

    if st.button("⬅️ Voltar"): st.session_state.etapa = "boas_vindas"; st.rerun()

# --- AGUARDANDO O TEU CÓDIGO PARA MONTAR O CARDÁPIO ---
elif st.session_state.etapa == "cardapio":
    st.title(f"Olá, {st.session_state.user['nome']}!")
    st.write("Manda o código do teu `app.py` para eu colocar os teus produtos aqui!")
    if st.button("Sair"): st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 4: PAINEL ADMIN (INTELIGÊNCIA)
# ==========================================
elif st.session_state.etapa == "painel_admin":
    st.title("👑 Painel da Yasmin & Mãe")
    if st.button("⬅️ Voltar"): st.session_state.etapa = "boas_vindas"; st.rerun()
    
    df_v = pd.read_sql("SELECT * FROM vendas", conn)
    if not df_v.empty:
        st.subheader("📊 Resumo de Vendas")
        st.bar_chart(df_v.groupby("sabor")["qtd"].sum())
        st.dataframe(df_v, use_container_width=True)
    else:
        st.info("Ainda não houve vendas.")
