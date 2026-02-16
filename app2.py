import streamlit as st
import pandas as pd
import sqlite3
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")

# --- 2. BANCO DE DADOS ---
conn = sqlite3.connect('doceria.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
             (nome TEXT, email TEXT PRIMARY KEY, senha TEXT, end TEXT, nasc TEXT, inst TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS vendas 
             (data TEXT, cliente TEXT, end TEXT, sabor TEXT, qtd INTEGER, total REAL, pgto TEXT)''')
conn.commit()

# --- DADOS DO NEGÓCIO ---
NUMERO_JAQUE = "5521976141210" 
CHAVE_PIX = "30.615.725 000155" 
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
    if st.button("🔑 ENTRAR / LOGIN", use_container_width=True):
        st.session_state.etapa = "login"; st.rerun()
    if st.button("✨ CRIAR CONTA", use_container_width=True):
        st.session_state.etapa = "cadastro"; st.rerun()

# ==========================================
# TELA 2: CADASTRO -> LOGIN
# ==========================================
elif st.session_state.etapa == "cadastro":
    st.title("📝 Cadastro")
    with st.form("form_cad"):
        n_nome = st.text_input("Nome Completo:")
        n_email = st.text_input("E-mail:")
        n_pass = st.text_input("Crie uma Senha:", type="password")
        n_end = st.text_input("Endereço (Ex: Rua 24 de Maio, 85 / Apto 101):")
        n_nasc = st.text_input("Nascimento (Ex: 15/02):")
        n_inst = st.text_area("Onde deixar a encomenda?")
        if st.form_submit_button("FINALIZAR ✨"):
            if n_nome and n_email and n_pass:
                try:
                    c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?)", (n_nome, n_email.lower(), n_pass, n_end, n_nasc, n_inst))
                    conn.commit()
                    st.success("Conta criada! Redirecionando...")
                    st.session_state.etapa = "login"; st.rerun()
                except: st.error("E-mail já cadastrado!")
            else: st.error("Preencha os campos!")
    if st.button("⬅️ Voltar"): st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 3: LOGIN
# ==========================================
elif st.session_state.etapa == "login":
    st.title("👤 Identificação")
    email_in = st.text_input("E-mail:").lower()
    pass_in = st.text_input("Senha:", type="password")
    if st.button("ACESSAR 🚀", type="primary", use_container_width=True):
        if email_in == ADMIN_USER and pass_in == ADMIN_PASS:
            st.session_state.etapa = "painel_admin"; st.rerun()
        c.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email_in, pass_in))
        res = c.fetchone()
        if res:
            st.session_state.user = {"nome": res[0], "email": res[1], "end": res[2], "nasc": res[4], "inst": res[5]}
            st.session_state.etapa = "cardapio"; st.rerun()
        else: st.error("Login inválido!")
    if st.button("⬅️ Voltar"): st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 4: CARDÁPIO (LÓGICA DE PREÇOS ORIGINAL)
# ==========================================
elif st.session_state.etapa == "cardapio":
    u = st.session_state.user
    if st.button("⬅️ Sair (Logout)"): st.session_state.etapa = "boas_vindas"; st.rerun()
    
    st.title(f"Olá, {u['nome']}! 🍦")
    
    # --- LOGICA DE CUPONS DO APP.PY ---
    cupom = st.text_input("Cupom de Desconto:").strip().upper()
    metodo_pgto = "PIX / Dinheiro"
    
    # 1. Verifica Morador (Segue seu app.py: MACHADORIBEIRO ou GARAGEMLOLA)
    eh_morador = (cupom == "MACHADORIBEIRO" or cupom == "GARAGEMLOLA")
    
    # 2. Verifica Aniversário (NIVERDOCE)
    eh_niver = (cupom == "NIVERDOCE" and datetime.now().strftime("%d/%m") == u['nasc'])

    # 3. TABELA DE PREÇOS DINÂMICA
    if eh_niver:
        p_fruta, p_gourmet, p_alcoolico = 4.0, 6.0, 8.0
        st.success("🎂 Desconto de Aniversário Ativado!")
    elif eh_morador:
        p_fruta, p_gourmet, p_alcoolico = 5.0, 7.0, 9.0
        st.success("🏠 Desconto de Morador Ativado!")
        if cupom == "GARAGEMLOLA":
            metodo_pgto = "ACERTO POSTERIOR (GARAGEM LOLA)"
            st.warning("💳 Pagamento posterior autorizado.")
    else:
        p_fruta, p_gourmet, p_alcoolico = 8.0, 9.0, 10.0

    total_bruto = 0.0
    pedido_itens = []

    # --- LISTA DE PRODUTOS ---
    estoque = {
        "❄️ Sacolés Fruta": [
            {"item": "Goiaba", "p": p_fruta, "est": 4}, {"item": "Manga", "p": p_fruta, "est": 4},
            {"item": "Abacaxi c/ Hortelã", "p": p_fruta, "est": 1}, {"item": "Frutopia", "p": p_fruta, "est": 3}
        ],
        "🍦 Sacolés Gourmet": [
            {"item": "Ninho c/ Nutella", "p": p_gourmet, "est": 5}, {"item": "Ninho c/ Morango", "p": p_gourmet, "est": 4},
            {"item": "Chicabon", "p": p_gourmet, "est": 4}, {"item": "Pudim de Leite", "p": p_gourmet, "est": 5},
            {"item": "Coco Cremoso", "p": p_gourmet, "est": 6}
        ],
        "🍹 Alcoólicos": [
            {"item": "Caipirinha", "p": p_alcoolico, "est": 2}, {"item": "Batida de Maracujá", "p": p_alcoolico, "est": 2}
        ]
    }

    for cat, itens in estoque.items():
        with st.expander(cat, expanded=True):
            for i in itens:
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{i['item']}**\nR$ {i['p']:.2f}")
                if i['est'] > 0:
                    q = c3.number_input("Qtd", 0, i['est'], key=f"p_{i['item']}")
                    if q > 0:
                        total_bruto += (q * i['p'])
                        pedido_itens.append(f"{q}x {i['item']}")
                else: c3.write("❌")

    # --- SALGADOS E DOCES ---
    st.header("🥧 Salgados e Doces")
    col_e1, col_e2 = st.columns([1, 1.5])
    with col_e1: st.image("https://raw.githubusercontent.com/Yassbessa/mae/main/empadao.jpeg")
    with col_e2:
        st.write("**Empadão de Frango**")
        q_p = st.number_input("Pequeno (R$ 12,00)", 0, 5)
        q_g = st.number_input("Grande (R$ 18,00)", 0, 0)
        if q_p > 0:
            total_bruto += (q_p * 12.0)
            pedido_itens.append(f"{q_p}x Empadão Frango P")
        if q_g > 0:
            total_bruto += (q_g * 18.0)
            pedido_itens.append(f"{q_g}x Empadão Frango G")

    col_b1, col_b2 = st.columns([1, 1.5])
    with col_b1: st.image("https://raw.githubusercontent.com/Yassbessa/mae/main/bolo.jpeg")
    with col_b2:
        st.write("**Crunch Cake (Pote)**")
        q_b = st.number_input("Qtd (R$ 10,00)", 0, 4)
        if q_b > 0:
            total_bruto += (q_b * 10.0)
            pedido_itens.append(f"{q_b}x Crunch Cake")

    if total_bruto > 0:
        st.divider()
        st.markdown(f"## Total Final: R$ {total_bruto:.2f}")
        op = st.radio("Entrega:", ["Entregar agora", "Vou buscar no 902", "Agendar"])
        
        if st.button("🚀 FINALIZAR PEDIDO", type="primary"):
            # Salva no Banco de Dados para a Yasmin e Jaque verem
            for item in pedido_itens:
                c.execute("INSERT INTO vendas VALUES (?,?,?,?,?,?,?)", 
                          (datetime.now().strftime("%d/%m %H:%M"), u['nome'], u['end'], item, 1, total_bruto, metodo_pgto))
            conn.commit()
            
            # Zap
            msg = f"🍦 *NOVO PEDIDO*\n👤 {u['nome']}\n📍 {u['end']}\n💬 {op}\n📦 {', '.join(pedido_itens)}\n💰 Total: R$ {total_bruto:.2f}\n💳 PGTO: {metodo_pgto}"
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'https://wa.me/{NUMERO_JAQUE}?text={urllib.parse.quote(msg)}\' /">', unsafe_allow_html=True)

# ==========================================
# TELA 5: PAINEL ADMIN (HISTÓRICO)
# ==========================================
elif st.session_state.etapa == "painel_admin":
    st.title("👑 Painel de Inteligência")
    if st.button("⬅️ Sair"): st.session_state.etapa = "boas_vindas"; st.rerun()
    df_v = pd.read_sql("SELECT * FROM vendas", conn)
    if not df_v.empty:
        st.subheader("🏆 O que mais sai?")
        st.bar_chart(df_v.groupby("sabor")["qtd"].sum())
        st.subheader("📋 Histórico Completo")
        st.dataframe(df_v, use_container_width=True)
