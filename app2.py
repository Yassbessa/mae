import streamlit as st
import pandas as pd
import sqlite3
import urllib.parse
from datetime import datetime

# ================= CONFIG =================
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")

NUMERO_YASMIN = "5521981816105"
NUMERO_JAQUE = "5521976141210"
CHAVE_PIX = "30.615.725 000155"
EMAIL_COMPROVANTE = "jaqueedoce@gmail.com"
ADMIN_USER = "admin"
ADMIN_PASS = "jqd9191"

# ================= BANCO =================
conn = sqlite3.connect('doceria.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
             (nome TEXT, email TEXT PRIMARY KEY, senha TEXT, end TEXT, nasc TEXT, inst TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS vendas 
             (data TEXT, cliente TEXT, end TEXT, item TEXT, qtd INTEGER, total REAL, pgto TEXT)''')
conn.commit()

# ================= ESTADO =================
if 'etapa' not in st.session_state: st.session_state.etapa = "boas_vindas"
if 'user' not in st.session_state: st.session_state.user = None

# ================= PRODUTOS =================
def obter_estoque(p_fruta, p_gourmet, p_alcoolico):
    return {
        "Frutas (Sem Lactose)": [
            {"item": "Goiaba", "p": p_fruta, "est": 4},
            {"item": "Uva", "p": p_fruta, "est": 0},
            {"item": "Maracujá", "p": p_fruta, "est": 0},
            {"item": "Manga", "p": p_fruta, "est": 4},
            {"item": "Morango", "p": p_fruta, "est": 0},
            {"item": "Abacaxi c/ Hortelã", "p": p_fruta, "est": 1},
            {"item": "Frutopia", "p": p_fruta, "est": 3}
        ],
        "Gourmet (Cremosos)": [
            {"item": "Ninho c/ Nutella", "p": p_gourmet, "est": 5},
            {"item": "Ninho c/ Morango", "p": p_gourmet, "est": 4},
            {"item": "Chicabon", "p": p_gourmet, "est": 4},
            {"item": "Mousse de Maracujá", "p": p_gourmet, "est": 3},
            {"item": "Pudim de Leite", "p": p_gourmet, "est": 5},
            {"item": "Açaí Cremoso", "p": p_gourmet, "est": 4},
            {"item": "Coco Cremoso", "p": p_gourmet, "est": 6}
        ],
        "Alcoólicos (+18)": [
            {"item": "Piña Colada", "p": p_alcoolico, "est": 1},
            {"item": "Sex on the Beach", "p": p_alcoolico, "est": 0},
            {"item": "Caipirinha", "p": p_alcoolico, "est": 2},
            {"item": "Batida de Maracujá", "p": p_alcoolico, "est": 2},
            {"item": "Batida de Morango", "p": p_alcoolico, "est": 1}
        ]
    }

# ================= TELA BOAS-VINDAS =================
if st.session_state.etapa == "boas_vindas":
    st.markdown("<h1 style='text-align: center; color: #E67E22;'>Ja Que É Doce 🐝</h1>", unsafe_allow_html=True)
    if st.button("🔑 Entrar / Login"): st.session_state.etapa = "login"; st.rerun()
    if st.button("✨ Criar Conta"): st.session_state.etapa = "cadastro"; st.rerun()

# ================= CADASTRO =================
elif st.session_state.etapa == "cadastro":
    st.title("Cadastro")
    with st.form("cad"):
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        end = st.text_input("Endereço")
        nasc = st.text_input("Nascimento (DD/MM)")
        inst = st.text_area("Instruções")
        if st.form_submit_button("Cadastrar"):
            try:
                c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?)",
                          (nome, email.lower(), senha, end, nasc, inst))
                conn.commit()
                st.success("Conta criada!")
                st.session_state.etapa = "login"; st.rerun()
            except:
                st.error("Email já cadastrado")

# ================= LOGIN =================
elif st.session_state.etapa == "login":
    st.title("Login")
    email = st.text_input("Email").lower()
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if email == ADMIN_USER and senha == ADMIN_PASS:
            st.session_state.etapa = "admin"; st.rerun()
        c.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha))
        res = c.fetchone()
        if res:
            st.session_state.user = {"nome": res[0], "end": res[3], "nasc": res[4]}
            st.session_state.etapa = "cardapio"; st.rerun()
        else:
            st.error("Login inválido")

# ================= CARDÁPIO (FUSÃO) =================
elif st.session_state.etapa == "cardapio":
    u = st.session_state.user
    st.title(f"Olá, {u['nome']} 🍦")
    if st.button("Logout"): st.session_state.etapa = "boas_vindas"; st.rerun()

    cupom = st.text_input("Cupom").upper()
    eh_morador = ("MACHADORIBEIRO" in cupom or "GARAGEMLOLA" in cupom)
    eh_niver = ("NIVERDOCE" in cupom and datetime.now().strftime("%d/%m") == u['nasc'])

    p_fruta = 5.0 if eh_morador else 8.0
    p_gourmet = 7.0 if eh_morador else 9.0
    p_alcoolico = 9.0 if eh_morador else 10.0

    estoque = obter_estoque(p_fruta, p_gourmet, p_alcoolico)

    total = 0.0
    itens = []
    precos = []

    # SACOLÉS
    for cat, lista in estoque.items():
        with st.expander(cat, True):
            for i in lista:
                c1, c2, c3 = st.columns([3,1,1])
                c1.write(f"**{i['item']}** — R$ {i['p']:.2f}")
                c2.write(f"Est: {i['est']}")
                if i['est'] > 0:
                    q = c3.number_input("Qtd", 0, i['est'], key=f"{cat}{i['item']}")
                    if q > 0:
                        total += q*i['p']
                        itens.append(f"{q}x {i['item']}")
                        for _ in range(q): precos.append(i['p'])
                else:
                    c3.write("❌")

    # EMPADÃO
    st.header("Salgados e Doces")
    q_emp = st.number_input("Empadão P (R$12)", 0, 5)
    q_bolo = st.number_input("Bolo Pote (R$10)", 0, 4)

    if q_emp > 0:
        total += q_emp*12
        itens.append(f"{q_emp}x Empadão")

    if q_bolo > 0:
        total += q_bolo*10
        itens.append(f"{q_bolo}x Bolo")

    # BRINDE ANIVERSÁRIO
    if eh_niver and precos:
        desconto = max(precos)
        total -= desconto
        st.info(f"🎂 NiverDoce aplicado (-R$ {desconto:.2f})")

    if total > 0:
        st.markdown(f"## Total: R$ {total:.2f}")
        forma = st.radio("Pagamento", ["PIX", "Dinheiro", "Cartão"])

        if st.button("Finalizar Pedido"):
            for item in itens:
                c.execute("INSERT INTO vendas VALUES (?,?,?,?,?,?,?)",
                          (datetime.now().strftime("%d/%m %H:%M"), u['nome'], u['end'], item, 1, total, forma))
            conn.commit()

            msg = f"🍦 Pedido\n{u['nome']}\n{u['end']}\n{', '.join(itens)}\nTotal: R$ {total:.2f}"
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=https://wa.me/{NUMERO_JAQUE}?text={urllib.parse.quote(msg)}">', unsafe_allow_html=True)

# ================= ADMIN =================
elif st.session_state.etapa == "admin":
    st.title("Painel Admin")
    df = pd.read_sql("SELECT * FROM vendas", conn)
    st.dataframe(df)
