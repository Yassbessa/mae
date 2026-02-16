import streamlit as st
import pandas as pd
import sqlite3
import urllib.parse
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")

# --- BANCO DE DADOS ---
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
    if st.button("✨ CRIAR UMA CONTA", use_container_width=True):
        st.session_state.etapa = "cadastro"; st.rerun()

# ==========================================
# TELA 2: CADASTRO -> LOGIN
# ==========================================
elif st.session_state.etapa == "cadastro":
    st.title("📝 Cadastro")
    with st.form("form_cad"):
        n_nome = st.text_input("Nome Completo:")
        n_email = st.text_input("E-mail:")
        n_pass = st.text_input("Senha:", type="password")
        n_end = st.text_input("Endereço (Ex: Rua 24 de Maio, 85 / Apto 101):")
        n_nasc = st.text_input("Nascimento (Ex: 15/02):")
        n_inst = st.text_area("Onde deixar a encomenda?")
        if st.form_submit_button("FINALIZAR CADASTRO ✨"):
            if n_nome and n_email and n_pass:
                try:
                    c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?)", (n_nome, n_email.lower(), n_pass, n_end, n_nasc, n_inst))
                    conn.commit()
                    st.success("Conta criada! Vamos para o login...")
                    st.session_state.etapa = "login"; st.rerun()
                except: st.error("E-mail já cadastrado!")
    if st.button("⬅️ Voltar"): st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 3: LOGIN
# ==========================================
elif st.session_state.etapa == "login":
    st.title("👤 Login")
    email_in = st.text_input("E-mail:").lower().strip()
    pass_in = st.text_input("Senha:", type="password").strip()
    if st.button("ACESSAR 🚀", type="primary", use_container_width=True):
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
# TELA 4: CARDÁPIO COMPLETO (SABORES TOTAIS)
# ==========================================
elif st.session_state.etapa == "cardapio":
    u = st.session_state.user
    if st.button("⬅️ Sair (Logout)"): st.session_state.etapa = "boas_vindas"; st.rerun()
    st.title(f"Olá, {u['nome']}! 🍦")
    
    # --- CUPONS ACUMULATIVOS ---
    cupom_txt = st.text_input("Tem um cupom?").strip().upper()
    metodo_pgto = "PIX / Dinheiro"
    eh_morador = ("MACHADORIBEIRO" in cupom_txt or "GARAGEMLOLA" in cupom_txt)
    eh_niver = ("NIVERDOCE" in cupom_txt and datetime.now().strftime("%d/%m") == u['nasc'])
    
    if "GARAGEMLOLA" in cupom_txt: metodo_pgto = "ACERTO NA GARAGEM (POSTERIOR)"

    # Preços Originais do seu app.py
    p_fru = 5.0 if eh_morador else 8.0
    p_gou = 7.0 if eh_morador else 9.0
    p_alc = 9.0 if eh_morador else 10.0

    total_bruto = 0.0
    pedido_itens = []
    lista_precos_brinde = []

    # --- LISTA COMPLETA DE PRODUTOS DO SEU APP.PY ---
    estoque_full = {
        "❄️ Frutas (Sem Lactose)": [
            {"item": "Goiaba", "p": p_fru, "est": 4}, {"item": "Uva", "p": p_fru, "est": 0},
            {"item": "Maracujá", "p": p_fru, "est": 0}, {"item": "Manga", "p": p_fru, "est": 4},
            {"item": "Morango", "p": p_fru, "est": 0}, {"item": "Abacaxi c/ Hortelã", "p": p_fru, "est": 1},
            {"item": "Frutopia", "p": p_fru, "est": 3}
        ],
        "🍦 Gourmet (Cremosos)": [
            {"item": "Ninho c/ Nutella", "p": p_gou, "est": 5}, {"item": "Ninho c/ Morango", "p": p_gou, "est": 4},
            {"item": "Chicabon", "p": p_gou, "est": 4}, {"item": "Mousse de Maracujá", "p": p_gou, "est": 3},
            {"item": "Pudim de Leite", "p": p_gou, "est": 5}, {"item": "Açaí Cremoso", "p": p_gou, "est": 4},
            {"item": "Coco Cremoso", "p": p_gou, "est": 6}
        ],
        "🍹 Alcoólicos (+18)": [
            {"item": "Piña Colada", "p": p_alc, "est": 1}, {"item": "Sex on the Beach", "p": p_alc, "est": 0},
            {"item": "Caipirinha", "p": p_alc, "est": 2}, {"item": "Batida de Maracujá", "p": p_alc, "est": 2},
            {"item": "Batida de Morango", "p": p_alc, "est": 1}
        ]
    }

    for cat, itens in estoque_full.items():
        with st.expander(cat, expanded=True):
            for i in itens:
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{i['item']}**\nR$ {i['p']:.2f}")
                c2.write(f"Est: {i['est']}")
                if i['est'] > 0:
                    q = c3.number_input("Qtd", 0, i['est'], key=f"s_{i['item']}")
                    if q > 0:
                        total_bruto += (q * i['p'])
                        pedido_itens.append(f"{q}x {i['item']}")
                        for _ in range(q): lista_precos_brinde.append(i['p'])
                else: c3.write("❌")

    # --- SALGADOS E DOCES (EMPADÃO E BOLO) ---
    st.header("🥧 Salgados e Doces")
    
    # EMPADÃO
    col_e1, col_e2 = st.columns([1, 1.5])
    with col_e1: st.image("https://raw.githubusercontent.com/Yassbessa/mae/main/empadao.jpeg")
    with col_e2:
        st.write("**Empadão de Frango**")
        q_p = st.number_input("Qtd Pequeno (R$ 12,00)", 0, 5, key="q_emp_p")
        q_g = st.number_input("Qtd Grande (R$ 18,00)", 0, 0, key="q_emp_g")
        if q_p > 0:
            total_bruto += (q_p * 12.0)
            pedido_itens.append(f"{q_p}x Empadão Frango P")
        if q_g > 0:
            total_bruto += (q_g * 18.0)
            pedido_itens.append(f"{q_g}x Empadão Frango G")

    # BOLO
    col_b1, col_b2 = st.columns([1, 1.5])
    with col_b1: st.image("https://raw.githubusercontent.com/Yassbessa/mae/main/bolo.jpeg")
    with col_b2:
        st.write("**Crunch Cake (Pote)**")
        q_b = st.number_input("Qtd Bolo (R$ 10,00)", 0, 4, key="q_bolo")
        if q_b > 0:
            total_bruto += (q_b * 10.0)
            pedido_itens.append(f"{q_b}x Crunch Cake")

    # --- LÓGICA DE BRINDE NIVER ---
    desconto_niver = 0.0
    if eh_niver and lista_precos_brinde:
        desconto_niver = max(lista_precos_brinde)
        st.info(f"🎂 NIVERDOCE: 1 sacolé grátis (-R$ {desconto_niver:.2f})")

    total_final = total_bruto - desconto_niver

    if total_bruto > 0:
        st.divider()
        st.markdown(f"## Total Final: R$ {total_final:.2f}")
        op = st.radio("Como prefere?", ["Entregar agora", "Vou buscar no 902", "Agendar"])
        
        if st.button("🚀 FINALIZAR PEDIDO", type="primary"):
            # Salva no Banco de Dados (Salgados e Bolos agora aparecem aqui!)
            for item in pedido_itens:
                c.execute("INSERT INTO vendas VALUES (?,?,?,?,?,?,?)", 
                          (datetime.now().strftime("%d/%m %H:%M"), u['nome'], u['end'], item, 1, total_final, metodo_pgto))
            conn.commit()
            
            # WhatsApp
            msg = f"🍦 *NOVO PEDIDO*\n👤 {u['nome']}\n📍 {u['end']}\n💬 {op}\n📦 {', '.join(pedido_itens)}\n💰 Total: R$ {total_final:.2f}\n💳 PGTO: {metodo_pgto}"
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'https://wa.me/{NUMERO_JAQUE}?text={urllib.parse.quote(msg)}\' /">', unsafe_allow_html=True)

# ==========================================
# TELA 5: PAINEL ADMIN (INTELIGÊNCIA COMPLETA)
# ==========================================
elif st.session_state.etapa == "painel_admin":
    st.title("👑 Painel Admin Ja Que É Doce")
    if st.button("⬅️ Sair"): st.session_state.etapa = "boas_vindas"; st.rerun()
    df_v = pd.read_sql("SELECT * FROM vendas", conn)
    if not df_v.empty:
        st.subheader("🏆 O que mais saiu (Sacolés, Bolos e Empadões)")
        st.bar_chart(df_v.groupby("sabor")["qtd"].sum())
        st.subheader("📋 Histórico Completo")
        st.dataframe(df_v, use_container_width=True)
