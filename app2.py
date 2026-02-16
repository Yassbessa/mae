import streamlit as st
import pandas as pd
import sqlite3
import urllib.parse
from datetime import datetime

# ================= CONFIG =================
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")

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

# =========================================================
# 1️⃣ LISTA FIXA DE PRODUTOS (NÃO MEXER)
# =========================================================
PRODUTOS = {
    "Frutas (Sem Lactose)": ["Goiaba", "Uva", "Maracujá", "Manga", "Morango", "Abacaxi c/ Hortelã", "Frutopia"],
    "Gourmet (Cremosos)": ["Ninho c/ Nutella", "Ninho c/ Morango", "Chicabon", "Mousse de Maracujá",
                           "Pudim de Leite", "Açaí Cremoso", "Coco Cremoso"],
    "Alcoólicos (+18)": ["Piña Colada", "Sex on the Beach", "Caipirinha",
                         "Batida de Maracujá", "Batida de Morango"],
    "Salgados e Doces": ["Empadão Frango P", "Crunch Cake"]
}

# =========================================================
# 2️⃣ ESTOQUE (SÓ MUDAR NÚMEROS)
# =========================================================
ESTOQUE = {
    "Goiaba": 4,
    "Uva": 0,
    "Maracujá": 0,
    "Manga": 4,
    "Morango": 0,
    "Abacaxi c/ Hortelã": 1,
    "Frutopia": 3,
    "Ninho c/ Nutella": 5,
    "Ninho c/ Morango": 4,
    "Chicabon": 4,
    "Mousse de Maracujá": 3,
    "Pudim de Leite": 5,
    "Açaí Cremoso": 4,
    "Coco Cremoso": 6,
    "Piña Colada": 1,
    "Sex on the Beach": 0,
    "Caipirinha": 2,
    "Batida de Maracujá": 2,
    "Batida de Morango": 1,
    "Empadão Frango P": 5,
    "Crunch Cake": 4
}

# =========================================================
# 3️⃣ FOTOS (SÓ COLAR LINKS)
# =========================================================
FOTOS = {
    "Goiaba": "",
    "Uva": "",
    "Maracujá": "",
    "Manga": "",
    "Morango": "",
    "Abacaxi c/ Hortelã": "",
    "Frutopia": "",
    "Ninho c/ Nutella": "",
    "Ninho c/ Morango": "",
    "Chicabon": "",
    "Mousse de Maracujá": "",
    "Pudim de Leite": "",
    "Açaí Cremoso": "",
    "Coco Cremoso": "",
    "Piña Colada": "",
    "Sex on the Beach": "",
    "Caipirinha": "",
    "Batida de Maracujá": "",
    "Batida de Morango": "",
    "Empadão Frango P": "https://raw.githubusercontent.com/Yassbessa/mae/main/empadao.jpeg",
    "Crunch Cake": "https://raw.githubusercontent.com/Yassbessa/mae/main/bolo.jpeg"
}

# =========================================================
# 4️⃣ FUNÇÃO DE PREÇO
# =========================================================
def definir_preco(item, categoria, eh_morador):
    if categoria == "Frutas (Sem Lactose)":
        return 5 if eh_morador else 8
    if categoria == "Gourmet (Cremosos)":
        return 7 if eh_morador else 9
    if categoria == "Alcoólicos (+18)":
        return 9 if eh_morador else 10
    if item == "Empadão Frango P":
        return 12
    if item == "Crunch Cake":
        return 10

# =========================================================
# TELAS
# =========================================================
if st.session_state.etapa == "boas_vindas":
    st.markdown("<h1 style='text-align: center; color: #E67E22;'>Ja Que É Doce 🐝</h1>", unsafe_allow_html=True)
    if st.button("🔑 Entrar"): st.session_state.etapa = "login"; st.rerun()
    if st.button("✨ Criar Conta"): st.session_state.etapa = "cadastro"; st.rerun()

elif st.session_state.etapa == "cadastro":
    st.title("Cadastro")
    with st.form("cad"):
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        end = st.text_input("Endereço")
        nasc = st.text_input("Nascimento (DD/MM)")
        if st.form_submit_button("Cadastrar"):
            c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?)",
                      (nome, email.lower(), senha, end, nasc, ""))
            conn.commit()
            st.success("Conta criada!")
            st.session_state.etapa = "login"; st.rerun()

elif st.session_state.etapa == "login":
    st.title("Login")
    email = st.text_input("Email").lower()
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        c.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha))
        res = c.fetchone()
        if res:
            st.session_state.user = {"nome": res[0], "end": res[3], "nasc": res[4]}
            st.session_state.etapa = "cardapio"; st.rerun()
        else:
            st.error("Login inválido")

elif st.session_state.etapa == "cardapio":
    u = st.session_state.user
    st.title(f"Olá, {u['nome']} 🍦")

    cupons_input = st.text_input("Cupons").upper()
    cupons = [c.strip() for c in cupons_input.replace(",", " ").split() if c.strip()]

    eh_morador = any(c in cupons for c in ["MACHADORIBEIRO", "GARAGEMLOLA"])
    eh_niver = ("NIVERDOCE" in cupons and datetime.now().strftime("%d/%m") == u['nasc'])

    total = 0
    itens = []
    precos = []

    for categoria, lista in PRODUTOS.items():
        st.subheader(categoria)

        for item in lista:
            estoque = ESTOQUE.get(item, 0)
            preco = definir_preco(item, categoria, eh_morador)
            foto = FOTOS.get(item, "")

            col_img, col_txt, col_est, col_qtd = st.columns([1,2,1,1])

            with col_img:
                if foto:
                    st.image(foto, width=70)

            with col_txt:
                st.write(f"**{item}**")
                st.write(f"R$ {preco:.2f}")

            with col_est:
                st.write(f"Est: {estoque}")

            with col_qtd:
                if estoque > 0:
                    q = st.number_input("Qtd", 0, estoque, key=item)
                    if q > 0:
                        total += q * preco
                        itens.append(f"{q}x {item}")
                        for _ in range(q): precos.append(preco)
                else:
                    st.write("❌")

    if eh_niver and precos:
        desconto = max(precos)
        total -= desconto
        st.info(f"🎂 NiverDoce aplicado (-R$ {desconto:.2f})")

    if total > 0:
        st.markdown(f"## 💰 Total: R$ {total:.2f}")

        forma = st.radio("Pagamento", ["PIX", "Dinheiro", "Cartão"])
        if forma == "PIX":
            st.success(f"🔑 Chave PIX: {CHAVE_PIX}")
            st.info(f"📧 Enviar comprovante para: {EMAIL_COMPROVANTE}")

        if st.button("Finalizar Pedido"):
            msg = f"🍦 Pedido\n{u['nome']}\n{u['end']}\n{', '.join(itens)}\nTotal: R$ {total:.2f}"
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=https://wa.me/{NUMERO_JAQUE}?text={urllib.parse.quote(msg)}">', unsafe_allow_html=True)
