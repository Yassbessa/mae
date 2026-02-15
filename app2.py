import streamlit as st
import pandas as pd
import sqlite3
import urllib.parse
from datetime import datetime

# --- CONFIGURAÇÃO (CENTRALIZADO) ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")

# --- BANCO DE DADOS LOCAL ---
conn = sqlite3.connect('doceria.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
             (nome TEXT, email TEXT PRIMARY KEY, senha TEXT, end TEXT, nasc TEXT, inst TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS vendas 
             (data TEXT, cliente TEXT, sabor TEXT, total REAL, pagamento TEXT)''')
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
    st.markdown("<h1 style='text-align: center;'>Ja Que É Doce 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    if st.button("🔑 ENTRAR / LOGIN", use_container_width=True):
        st.session_state.etapa = "login"; st.rerun()
    if st.button("✨ CRIAR CONTA", use_container_width=True):
        st.session_state.etapa = "cadastro"; st.rerun()

# ==========================================
# TELA 2: CADASTRO (DIRETO PRO LOGIN)
# ==========================================
elif st.session_state.etapa == "cadastro":
    st.title("📝 Cadastro")
    with st.form("cad"):
        n_nome = st.text_input("Nome Completo:")
        n_email = st.text_input("E-mail:")
        n_pass = st.text_input("Senha:", type="password")
        n_end = st.text_input("Endereço:")
        n_nasc = st.text_input("Data de Nascimento (Ex: 15/02):")
        n_inst = st.text_area("Onde deixar a encomenda?")
        if st.form_submit_button("FINALIZAR ✨"):
            try:
                c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?)", (n_nome, n_email.lower(), n_pass, n_end, n_nasc, n_inst))
                conn.commit()
                st.success("Conta criada! Redirecionando...")
                st.session_state.etapa = "login"; st.rerun()
            except: st.error("E-mail já cadastrado!")
    if st.button("⬅️ Voltar"): st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 3: LOGIN
# ==========================================
elif st.session_state.etapa == "login":
    st.title("👤 Login")
    email_in = st.text_input("E-mail:").lower()
    pass_in = st.text_input("Senha:", type="password")
    if st.button("ACESSAR 🚀", type="primary"):
        if email_in == ADMIN_USER and pass_in == ADMIN_PASS:
            st.session_state.etapa = "painel_admin"; st.rerun()
        c.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email_in, pass_in))
        res = c.fetchone()
        if res:
            st.session_state.user = {"nome": res[0], "email": res[1], "end": res[3], "nasc": res[4], "inst": res[5]}
            st.session_state.etapa = "cardapio"; st.rerun()
        else: st.error("Login inválido!")
    if st.button("⬅️ Voltar"): st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 4: CARDÁPIO (AGUARDANDO SEU APP.PY)
# ==========================================
elif st.session_state.etapa == "cardapio":
    u = st.session_state.user
    st.title(f"Olá, {u['nome']}! 🍦")
    
    # --- LOGICA DE CUPONS ---
    cupom = st.text_input("Cupom de Desconto:").strip().upper()
    preco_unid = 9.0
    metodo_pgto = "PIX / Dinheiro"
    
    if cupom == "MACHADORIBEIRO":
        if "85" in u['end'] and "24 DE MAIO" in u['end'].upper():
            preco_unid = 7.0
            st.success("Cupom Morador 85 ativado! ✅")
        else: st.error("Cupom inválido para seu endereço.")
        
    elif cupom == "GARAGEMLOLA":
        metodo_pgto = "ACERTO NA GARAGEM (PAGAMENTO POSTERIOR)"
        st.warning("Atenção: Compra autorizada para acerto com a Jaqueline! 💳")
        
    elif cupom == "NIVERDOCE":
        hoje = datetime.now().strftime("%d/%m")
        if hoje == u['nasc']:
            preco_unid = 6.0
            st.success("Parabéns! Desconto de aniversário ativado! 🎂")
        else: st.error("O cupom NIVERDOCE só vale no dia do seu aniversário!")

    st.info(f"Preço por unidade: R$ {preco_unid:.2f}")
    
    # --- ESPAÇO PARA O SEU CARDÁPIO ---
    st.write("### 🍨 Escolha seus doces:")
    st.write("(Cole aqui o código do seu app.py para eu listar os produtos!)")
    
    if st.button("🚀 FINALIZAR"):
        # Aqui o código envia o valor para a Jaqueline pelo Zap
        msg = f"🍦 *NOVO PEDIDO*\n👤 {u['nome']}\n📍 {u['end']}\n💰 PGTO: {metodo_pgto}"
        st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'https://wa.me/5521976141210?text={urllib.parse.quote(msg)}\' /">', unsafe_allow_html=True)

# ==========================================
# TELA 5: PAINEL ADMIN (INTELIGÊNCIA)
# ==========================================
elif st.session_state.etapa == "painel_admin":
    st.title("👑 Painel da Jaqueline & Yasmin")
    if st.button("⬅️ Sair"): st.session_state.etapa = "boas_vindas"; st.rerun()
    
    df_v = pd.read_sql("SELECT * FROM vendas", conn)
    st.subheader("📊 Resumo das Vendas")
    st.dataframe(df_v, use_container_width=True)
    # Aqui entrarão os gráficos de sabores e apartamentos
