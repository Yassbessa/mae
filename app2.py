import streamlit as st
import pandas as pd
import sqlite3
import urllib.parse
from datetime import datetime
import os

# --- 1. CONFIGURAÇÃO (CENTRALIZADO) ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")

# --- 2. BANCO DE DADOS (SQLite - O "Cofre" do App) ---
conn = sqlite3.connect('doceria.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
             (nome TEXT, email TEXT PRIMARY KEY, senha TEXT, end TEXT, nasc TEXT, inst TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS vendas 
             (data TEXT, cliente TEXT, end TEXT, sabor TEXT, qtd INTEGER, total REAL, pgto TEXT)''')
conn.commit()

# --- DADOS DO NEGÓCIO ---
NUMERO_YASMIN = "5521981816105" 
NUMERO_JAQUE = "5521976141210" 
CHAVE_PIX = "30.615.725 000155" 
EMAIL_COMPROVANTE = "jaqueedoce@gmail.com"
ADMIN_USER = "admin"
ADMIN_PASS = "jqd9191"

# --- CONTROLE DE NAVEGAÇÃO ---
if 'etapa' not in st.session_state: st.session_state.etapa = "boas_vindas"
if 'user' not in st.session_state: st.session_state.user = None

# ==========================================
# TELA 1: BOAS-VINDAS
# ==========================================
if st.session_state.etapa == "boas_vindas":
    st.markdown("<h1 style='text-align: center; color: #E67E22;'>Ja Que É Doce 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    st.markdown("<h3 style='text-align: center;'>Feitos artesanalmente para você. ❤️</h3>", unsafe_allow_html=True)
    
    if st.button("🔑 ENTRAR / LOGIN", use_container_width=True):
        st.session_state.etapa = "login"; st.rerun()
    if st.button("✨ CRIAR UMA CONTA", use_container_width=True):
        st.session_state.etapa = "cadastro"; st.rerun()

# ==========================================
# TELA 2: CADASTRO (DIRETO PRO LOGIN)
# ==========================================
elif st.session_state.etapa == "cadastro":
    st.title("📝 Cadastro")
    with st.form("form_cad"):
        n_nome = st.text_input("Nome Completo:")
        n_email = st.text_input("E-mail:")
        n_pass = st.text_input("Crie uma Senha:", type="password")
        n_end = st.text_input("Endereço (Ex: Rua 24 de Maio, 85 / Apto 101):")
        n_nasc = st.text_input("Data de Nascimento (Ex: 15/02):")
        n_inst = st.text_area("Instruções de Entrega (Onde deixar?):")
        if st.form_submit_button("FINALIZAR CADASTRO ✨"):
            if n_nome and n_email and n_pass:
                try:
                    c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?)", (n_nome, n_email.lower(), n_pass, n_end, n_nasc, n_inst))
                    conn.commit()
                    st.success("Conta criada! Redirecionando para o login...")
                    st.session_state.etapa = "login"; st.rerun()
                except: st.error("E-mail já cadastrado!")
            else: st.error("Preencha os campos obrigatórios!")
    if st.button("⬅️ Voltar"): st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 3: LOGIN (CLIENTE OU ADMIN)
# ==========================================
elif st.session_state.etapa == "login":
    st.title("👤 Login")
    email_in = st.text_input("E-mail:").lower()
    pass_in = st.text_input("Senha:", type="password")
    
    if st.button("ACESSAR 🚀", type="primary", use_container_width=True):
        if email_in == ADMIN_USER and pass_in == ADMIN_PASS:
            st.session_state.etapa = "painel_admin"; st.rerun()
        
        c.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email_in, pass_in))
        res = c.fetchone()
        if res:
            st.session_state.user = {"nome": res[0], "email": res[1], "end": res[3], "nasc": res[4], "inst": res[5]}
            st.session_state.etapa = "cardapio"; st.rerun()
        else: st.error("Login ou senha inválidos!")
    if st.button("⬅️ Voltar"): st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 4: CARDÁPIO (O SEU CÓDIGO MELHORADO)
# ==========================================
elif st.session_state.etapa == "cardapio":
    u = st.session_state.user
    if st.button("⬅️ Sair (Logout)"): st.session_state.etapa = "boas_vindas"; st.rerun()
    
    st.title(f"Olá, {u['nome']}! 🍦")
    
    # --- SISTEMA DE CUPONS ---
    cupom = st.text_input("Possui cupom de desconto?").strip().upper()
    metodo_pagto = "PIX / Dinheiro"
    
    # Regras de Preço
    eh_morador_85 = (cupom == "MACHADORIBEIRO" and "85" in u['end'] and "24 DE MAIO" in u['end'].upper())
    eh_niver = (cupom == "NIVERDOCE" and datetime.now().strftime("%d/%m") == u['nasc'])
    
    if cupom == "GARAGEMLOLA":
        metodo_pagto = "GARAGEM LOLA (Acerto Posterior)"
        st.warning("⚠️ Cupom GARAGEMLOLA ativado: Acerto de valor com a Jaqueline.")

    p_fruta = 5.00 if eh_morador_85 else (4.00 if eh_niver else 8.00)
    p_gourmet = 7.00 if eh_morador_85 else (6.00 if eh_niver else 9.00)
    p_alcoolico = 9.00 if eh_morador_85 else (8.00 if eh_niver else 10.00)

    if eh_morador_85: st.success("Cupom MACHADORIBEIRO Ativado! ✅")
    if eh_niver: st.success("Parabéns! Cupom NIVERDOCE Ativado! 🎂")

    pedido_itens = []
    total_bruto = 0.0

    # --- ESTOQUE E ITENS ---
    estoque = {
        "❄️ Sacolés Fruta": [{"item": "Goiaba", "p": p_fruta, "est": 4}, {"item": "Manga", "p": p_fruta, "est": 4}],
        "🍦 Sacolés Gourmet": [{"item": "Ninho c/ Nutella", "p": p_gourmet, "est": 5}, {"item": "Pudim de Leite", "p": p_gourmet, "est": 5}],
        "🍹 Alcoólicos": [{"item": "Caipirinha", "p": p_alcoolico, "est": 2}]
    }

    for cat, itens in estoque.items():
        with st.expander(cat, expanded=True):
            for i in itens:
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.write(f"**{i['item']}**\nR$ {i['p']:.2f}")
                if i['est'] > 0:
                    qtd = col3.number_input("Qtd", 0, i['est'], key=f"s_{i['item']}")
                    if qtd > 0:
                        sub = qtd * i['p']
                        total_bruto += sub
                        pedido_itens.append(f"{qtd}x {i['item']}")
                        # Grava para o Banco de Dados
                        c.execute("INSERT INTO vendas VALUES (?,?,?,?,?,?,?)", 
                                  (datetime.now().strftime("%d/%m %H:%M"), u['nome'], u['end'], i['item'], qtd, sub, metodo_pagto))
                else: col3.write("❌")

    # --- SALGADOS E DOCES COM FOTO ---
    st.header("🥧 Salgados e Doces")
    c_e1, c_e2 = st.columns([1, 1.5])
    with c_e1: st.image("https://raw.githubusercontent.com/Yassbessa/mae/main/empadao.jpeg")
    with c_e2:
        q_emp = st.number_input("Empadão Frango P (R$ 12,00)", 0, 5)
        if q_emp > 0: 
            total_bruto += (q_emp * 12.0)
            pedido_itens.append(f"{q_emp}x Empadão P")

    if total_bruto > 0:
        st.divider()
        st.subheader(f"💰 Total: R$ {total_bruto:.2f}")
        opcao = st.radio("Como prefere?", ["Entregar agora", "Vou buscar no 902", "Agendar"])
        
        if st.button("🚀 FINALIZAR E ENVIAR WHATSAPP", type="primary"):
            conn.commit() # Salva as vendas no banco de dados local
            msg = f"🍦 *NOVO PEDIDO*\n👤 {u['nome']}\n📍 {u['end']}\n💬 {opcao}\n📦 {', '.join(pedido_itens)}\n💰 Total: R$ {total_bruto:.2f}\n💳 PGTO: {metodo_pagto}"
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'https://wa.me/{NUMERO_JAQUE}?text={urllib.parse.quote(msg)}\' /">', unsafe_allow_html=True)

# ==========================================
# TELA 5: PAINEL ADMIN (INTELIGÊNCIA)
# ==========================================
elif st.session_state.etapa == "painel_admin":
    st.title("👑 Painel de Inteligência - Ja Que É Doce")
    if st.button("⬅️ Sair"): st.session_state.etapa = "boas_vindas"; st.rerun()
    
    df_v = pd.read_sql("SELECT * FROM vendas", conn)
    
    if not df_v.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🏆 Sabores Mais Vendidos")
            st.bar_chart(df_v.groupby("sabor")["qtd"].sum())
        with c2:
            st.subheader("📍 Ranking por Apartamento")
            st.dataframe(df_v.groupby("end")["total"].sum().sort_values(ascending=False))
            
        st.subheader("📋 Histórico Completo de Pedidos")
        st.dataframe(df_v, use_container_width=True)
    else: st.info("Aguardando as primeiras vendas!")
