import streamlit as st
import pandas as pd
import sqlite3
import urllib.parse
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão Ja Que É Doce", page_icon="🐝", layout="wide")

# --- CONEXÃO COM O BANCO DE DADOS (O NOSSO COFRE DIGITAL) ---
conn = sqlite3.connect('doceria.db', check_same_thread=False)
c = conn.cursor()

# Criando as tabelas se elas não existirem
c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
             (nome TEXT, email TEXT PRIMARY KEY, senha TEXT, endereco TEXT, bairro TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS vendas 
             (data TEXT, cliente_email TEXT, endereco TEXT, sabor TEXT, qtd INTEGER, total REAL)''')
conn.commit()

# --- LOGIN DO MODERADOR ---
ADMIN_USER = "admin"
ADMIN_PASS = "jqd9191"

# --- MEMÓRIA DA SESSÃO ---
if 'etapa' not in st.session_state: st.session_state.etapa = "boas_vindas"
if 'user' not in st.session_state: st.session_state.user = None

# ==========================================
# TELA 1: BOAS-VINDAS
# ==========================================
if st.session_state.etapa == "boas_vindas":
    st.markdown("<h1 style='text-align: center; color: #E67E22;'>Ja Que É Doce 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    c1, c2 = st.columns(2)
    if c1.button("🔑 ENTRAR / LOGIN", use_container_width=True):
        st.session_state.etapa = "login"; st.rerun()
    if c2.button("✨ CADASTRAR NOVA CONTA", use_container_width=True):
        st.session_state.etapa = "cadastro"; st.rerun()

# ==========================================
# TELA 2: LOGIN (CLIENTE OU ADMIN)
# ==========================================
elif st.session_state.etapa == "login":
    st.title("👤 Identificação")
    email_input = st.text_input("E-mail:").strip().lower()
    pass_input = st.text_input("Senha:", type="password")
    
    if st.button("ACESSAR 🚀", type="primary"):
        # 1. VERIFICA SE É ADMIN (YASMIN/MÃE)
        if email_input == ADMIN_USER and pass_input == ADMIN_PASS:
            st.session_state.etapa = "painel_admin"; st.rerun()
        
        # 2. VERIFICA SE É CLIENTE NO BANCO
        c.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email_input, pass_input))
        res = c.fetchone()
        if res:
            st.session_state.user = {"nome": res[0], "email": res[1], "end": res[3], "bairro": res[4]}
            st.session_state.etapa = "cardapio"; st.rerun()
        else:
            st.error("E-mail ou Senha incorretos!")
            
    if st.button("⬅️ Voltar"): st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 3: CADASTRO DE CLIENTE
# ==========================================
elif st.session_state.etapa == "cadastro":
    st.title("📝 Crie sua conta")
    with st.form("form_cad"):
        n_nome = st.text_input("Nome Completo:")
        n_email = st.text_input("E-mail:")
        n_pass = st.text_input("Senha:", type="password")
        n_end = st.text_input("Endereço (Ex: Apto 302 / Casa 10):")
        n_bairro = st.text_input("Bairro:")
        if st.form_submit_button("FINALIZAR CADASTRO"):
            try:
                c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?)", (n_nome, n_email.lower(), n_pass, n_end, n_bairro))
                conn.commit()
                st.success("Conta criada! Faça o login.")
                st.session_state.etapa = "login"; st.rerun()
            except:
                st.error("Este e-mail já está cadastrado!")

# ==========================================
# TELA 4: CARDÁPIO (PRODUÇÃO DE DADOS)
# ==========================================
elif st.session_state.etapa == "cardapio":
    u = st.session_state.user
    st.title(f"Olá, {u['nome']}! 🍦")
    
    sabores = {"Ninho c/ Nutella": 9.0, "Morango": 8.0, "Paçoca": 8.0}
    c1, c2, c3 = st.columns(3)
    pedidos = {}
    
    # Interface de compra
    for i, (sabor, preco) in enumerate(sabores.items()):
        qtd = [c1, c2, c3][i].number_input(f"{sabor} (R${preco})", 0, 10, key=sabor)
        if qtd > 0: pedidos[sabor] = qtd

    if pedidos:
        total = sum(sabores[s] * q for s, q in pedidos.items())
        st.write(f"### Total: R$ {total:.2f}")
        if st.button("🚀 FINALIZAR PEDIDO"):
            data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
            for s, q in pedidos.items():
                c.execute("INSERT INTO vendas VALUES (?,?,?,?,?,?)", 
                          (data_hoje, u['email'], u['end'], s, q, q * sabores[s]))
            conn.commit()
            
            # Link para o Zap
            msg = f"🍦 *NOVO PEDIDO*\n👤 {u['nome']}\n📍 {u['end']}\n📦 {pedidos}\n💰 Total: R$ {total:.2f}"
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'https://wa.me/5521976141210?text={urllib.parse.quote(msg)}\' /">', unsafe_allow_html=True)

# ==========================================
# TELA 5: PAINEL ADMIN (INTELIGÊNCIA DE NEGÓCIO)
# ==========================================
elif st.session_state.etapa == "painel_admin":
    st.title("👑 Painel Administrativo - Ja Que É Doce")
    if st.button("⬅️ SAIR"): st.session_state.etapa = "boas_vindas"; st.rerun()
    
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn)
    df_clientes = pd.read_sql("SELECT * FROM usuarios", conn)
    
    if not df_vendas.empty:
        col1, col2, col3 = st.columns(3)
        
        # 1. RANKING DE SABORES
        with col1:
            st.subheader("🏆 Sabores Campeões")
            ranking = df_vendas.groupby("sabor")["qtd"].sum().sort_values(ascending=False)
            st.bar_chart(ranking)

        # 2. RANKING DE APARTAMENTOS/ENDEREÇOS
        with col2:
            st.subheader("📍 Onde pedem mais?")
            locais = df_vendas.groupby("endereco")["total"].sum().sort_values(ascending=False)
            st.dataframe(locais)

        # 3. QUEM É O MELHOR CLIENTE?
        with col3:
            st.subheader("👤 Top Clientes")
            top_clientes = df_vendas.groupby("cliente_email")["total"].sum().sort_values(ascending=False)
            st.write(top_clientes)

        st.write("---")
        st.subheader("📋 Todas as Vendas")
        st.dataframe(df_vendas, use_container_width=True)
    else:
        st.info("Ainda não temos vendas registradas.")
