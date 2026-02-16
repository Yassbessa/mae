import streamlit as st
import sqlite3
import urllib.parse
from datetime import datetime

# ================= CONFIG =================
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")

NUMERO_JAQUE = "5521976141210"
CHAVE_PIX = "30.615.725 000155"
EMAIL_COMPROVANTE = "jaqueedoce@gmail.com"

# ================= BANCO =================
conn = sqlite3.connect('doceria.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
             (nome TEXT, email TEXT PRIMARY KEY, senha TEXT, end TEXT, nasc TEXT, inst TEXT)''')
conn.commit()

# ================= ESTADO =================
if 'etapa' not in st.session_state:
    st.session_state.etapa = "boas_vindas"
if 'user' not in st.session_state:
    st.session_state.user = None

# ================= PRODUTOS =================
PRODUTOS = {
    "❄️ Frutas (Sem Lactose)": ["Goiaba", "Uva", "Maracujá", "Manga", "Morango", "Abacaxi c/ Hortelã", "Frutopia"],
    "🍦 Gourmet (Cremosos)": ["Ninho c/ Nutella", "Ninho c/ Morango", "Chicabon", "Mousse de Maracujá",
                              "Pudim de Leite", "Açaí Cremoso", "Coco Cremoso"],
    "🍹 Alcoólicos (+18)": ["Piña Colada", "Sex on the Beach", "Caipirinha",
                            "Batida de Maracujá", "Batida de Morango"],
    "🥧 Salgados e Doces": ["Empadão Frango P", "Empadão Frango G", "Crunch Cake"]
}

# ================= ESTOQUE =================
ESTOQUE = {
    "Goiaba": 4, "Uva": 0, "Maracujá": 0, "Manga": 4, "Morango": 0,
    "Abacaxi c/ Hortelã": 1, "Frutopia": 3,
    "Ninho c/ Nutella": 5, "Ninho c/ Morango": 4, "Chicabon": 4,
    "Mousse de Maracujá": 3, "Pudim de Leite": 5,
    "Açaí Cremoso": 4, "Coco Cremoso": 6,
    "Piña Colada": 1, "Sex on the Beach": 0, "Caipirinha": 2,
    "Batida de Maracujá": 2, "Batida de Morango": 1,
    "Empadão Frango P": 5,
    "Empadão Frango G": 5,
    "Crunch Cake": 4
}

# ================= FOTOS =================
FOTOS = {
    "Goiaba": "", "Uva": "", "Maracujá": "", "Manga": "", "Morango": "",
    "Abacaxi c/ Hortelã": "", "Frutopia": "",
    "Ninho c/ Nutella": "", "Ninho c/ Morango": "", "Chicabon": "",
    "Mousse de Maracujá": "", "Pudim de Leite": "",
    "Açaí Cremoso": "", "Coco Cremoso": "",
    "Piña Colada": "", "Sex on the Beach": "", "Caipirinha": "",
    "Batida de Maracujá": "", "Batida de Morango": "",
    "Empadão Frango P": "https://raw.githubusercontent.com/Yassbessa/mae/main/empadao.jpeg",
    "Empadão Frango G": "https://raw.githubusercontent.com/Yassbessa/mae/main/empadao.jpeg",
    "Crunch Cake": "https://raw.githubusercontent.com/Yassbessa/mae/main/bolo.jpeg"
}

# ================= PREÇOS =================
def definir_preco(item, categoria, eh_morador):
    if "Frutas" in categoria:
        return 5 if eh_morador else 8
    if "Gourmet" in categoria:
        return 7 if eh_morador else 9
    if "Alcoólicos" in categoria:
        return 9 if eh_morador else 10
    if item == "Empadão Frango P":
        return 12
    if item == "Empadão Frango G":
        return 18
    if item == "Crunch Cake":
        return 10

# ================= TELAS =================
if st.session_state.etapa == "boas_vindas":
    st.markdown("<h1 style='text-align:center;color:#E67E22;'>Ja Que É Doce 🐝</h1>", unsafe_allow_html=True)
    if st.button("Entrar"): st.session_state.etapa = "login"; st.rerun()

elif st.session_state.etapa == "login":
    st.title("Login")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        st.session_state.user = {"nome": email, "end": "Endereço cadastrado", "nasc": "01/01"}
        st.session_state.etapa = "cardapio"; st.rerun()

elif st.session_state.etapa == "cardapio":
    u = st.session_state.user

    st.markdown("<h2 style='text-align:center;'>🍦 Cardápio</h2>", unsafe_allow_html=True)
    st.caption(f"Olá, {u['nome']}")

    cupons_input = st.text_input("Cupons").upper()
    cupons = cupons_input.split()

    eh_morador = any(c in cupons for c in ["MACHADORIBEIRO", "GARAGEMLOLA"])
    eh_niver = "NIVERDOCE" in cupons

    total = 0
    itens = []
    precos = []

    for categoria, lista in PRODUTOS.items():
        with st.expander(categoria, expanded=True):
            for item in lista:
                estoque = ESTOQUE.get(item, 0)
                preco = definir_preco(item, categoria, eh_morador)
                foto = FOTOS.get(item, "")

                col1, col2, col3 = st.columns([3,1,1])

                with col1:
                    st.write(f"**{item}**")
                    st.caption(f"R$ {preco:.2f}")

                with col2:
                    st.write(f"Est: {estoque}")

                with col3:
                    if estoque > 0:
                        q = st.number_input("Qtd", 0, estoque, key=item, label_visibility="collapsed")
                        if q > 0:
                            total += q * preco
                            itens.append(f"{q}x {item}")
                            precos.append(preco)

                            # FOTO aparece somente após selecionar
                            if foto:
                                st.image(foto, width=120)
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

        if st.button("Finalizar Pedido", type="primary", use_container_width=True):
            msg = f"🍦 Pedido\n{u['nome']}\n{u['end']}\n{', '.join(itens)}\nTotal: R$ {total:.2f}"
            st.markdown(
                f'<meta http-equiv="refresh" content="0;URL=https://wa.me/{NUMERO_JAQUE}?text={urllib.parse.quote(msg)}">',
                unsafe_allow_html=True
            )
