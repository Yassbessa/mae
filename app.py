import streamlit as st
import sqlite3
import urllib.parse
from datetime import datetime
import pandas as pd

# ================= CONFIG =================
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")

NUMERO_YASMIN = "5521981816105"
NUMERO_JAQUE = "5521976141210"
CHAVE_PIX = "30.615.725 000155"
EMAIL_COMPROVANTE = "jaqueedoce@gmail.com"

ADMIN_USER = "admin"
ADMIN_PASS = "jqd9191"

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
    "Goiaba": 5, "Uva": 0, "Maracujá": 0, "Manga": 4, "Morango": 0,
    "Abacaxi c/ Hortelã": 1, "Frutopia": 3,
    "Ninho c/ Nutella": 5, "Ninho c/ Morango": 4, "Chicabon": 4,
    "Mousse de Maracujá": 3, "Pudim de Leite": 5,
    "Açaí Cremoso": 4, "Coco Cremoso": 6,
    "Piña Colada": 1, "Sex on the Beach": 0, "Caipirinha": 2,
    "Batida de Maracujá": 2, "Batida de Morango": 1,
    "Empadão Frango P": 4,
    "Empadão Frango G": 0,
    "Crunch Cake": 2
}

# ================= FOTOS =================
FOTOS = {
    "Empadão Frango P": "https://raw.githubusercontent.com/Yassbessa/mae/main/empadao.jpeg",
    "Empadão Frango G": "https://raw.githubusercontent.com/Yassbessa/mae/main/empadão2.jpeg",
    "Crunch Cake": "https://raw.githubusercontent.com/Yassbessa/mae/main/bolo.jpeg"
}

# ================= BANCO =================
conn = sqlite3.connect('doceria.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
    nome TEXT, email TEXT PRIMARY KEY, senha TEXT,
    endereco TEXT, nascimento TEXT, instrucoes TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS vendas (
    data TEXT, cliente TEXT, item TEXT,
    qtd INTEGER, total REAL, pagamento TEXT)''')
conn.commit()

# ================= SESSION =================
if "etapa" not in st.session_state:
    st.session_state.etapa = "boas_vindas"

if "user" not in st.session_state:
    st.session_state.user = None

# ================= BOAS-VINDAS =================
if st.session_state.etapa == "boas_vindas":
    st.markdown("<h1 style='text-align: center; color: #E67E22;'>Ja Que É Doce 🐝</h1>", unsafe_allow_html=True)

    if st.button("🔑 ENTRAR / LOGIN", use_container_width=True):
        st.session_state.etapa = "login"
        st.rerun()

    if st.button("✨ CRIAR CONTA", use_container_width=True):
        st.session_state.etapa = "cadastro"
        st.rerun()

# ================= CADASTRO =================
elif st.session_state.etapa == "cadastro":
    st.title("Cadastro")

    with st.form("cad"):
        nome = st.text_input("Nome")
        email = st.text_input("Email").lower()
        senha = st.text_input("Senha", type="password")
        endereco = st.text_input("Endereço")
        nascimento = st.text_input("Nascimento (dd/mm)")
        instrucoes = st.text_area("Onde deixar")

        if st.form_submit_button("Criar conta"):
            try:
                c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?)",
                          (nome, email, senha, endereco, nascimento, instrucoes))
                conn.commit()
                st.success("Conta criada!")
                st.session_state.etapa = "login"
                st.rerun()
            except:
                st.error("Email já cadastrado")

    if st.button("Voltar"):
        st.session_state.etapa = "boas_vindas"
        st.rerun()

# ================= LOGIN =================
elif st.session_state.etapa == "login":
    st.title("Login")

    email = st.text_input("Email").lower()
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if email == ADMIN_USER and senha == ADMIN_PASS:
            st.session_state.etapa = "admin"
            st.rerun()

        c.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha))
        res = c.fetchone()

        if res:
            st.session_state.user = {
                "nome": res[0],
                "email": res[1],
                "end": res[3],
                "nasc": res[4],
                "inst": res[5]
            }
            st.session_state.etapa = "cardapio"
            st.rerun()
        else:
            st.error("Login inválido")

    if st.button("Voltar"):
        st.session_state.etapa = "boas_vindas"
        st.rerun()
        
# ================= ADMIN =================
elif st.session_state.etapa == "admin":
    st.title("Painel Admin 🐝")

    if st.button("Sair do admin"):
        st.session_state.etapa = "boas_vindas"
        st.rerun()

    st.subheader("📦 Estoque atual")

    for produto, qtd in ESTOQUE.items():
        st.write(f"{produto}: {qtd}")

    st.subheader("📊 Vendas registradas")

    df = pd.read_sql_query("SELECT * FROM vendas", conn)
    st.dataframe(df)

# ================= CARDÁPIO =================
elif st.session_state.etapa == "cardapio":
    u = st.session_state.user

    if st.button("Sair"):
        st.session_state.etapa = "boas_vindas"
        st.rerun()

    st.title(f"Olá, {u['nome']} 🍦")

    # -------- CUPONS --------
    cupom = st.text_input("Possui cupom?").upper()
    eh_morador = "MACHADORIBEIRO" in cupom
    eh_garagem = "GARAGEMLOLA" in cupom
    eh_niver = "NIVERDOCE" in cupom and datetime.now().strftime("%d/%m") == u["nasc"]

    total = 0
    itens = []
    precos_para_brinde = []

         # -------- PREÇOS --------

    # preços por categoria
    PRECOS = {
        "❄️ Frutas (Sem Lactose)": {"normal": 8.0, "morador": 5.0},
        "🍦 Gourmet (Cremosos)": {"normal": 9.0, "morador": 7.0},
        "🍹 Alcoólicos (+18)": {"normal": 10.0, "morador": 9.0},
        "🥧 Salgados e Doces": {"normal": 12.0, "morador": 12.0}  # não muda
    }

    for categoria, lista_produtos in PRODUTOS.items():
        with st.expander(categoria, expanded=True):

            for produto in lista_produtos:
                estoque = ESTOQUE.get(produto, 0)

                # define preço correto
                if eh_morador:
                    preco = PRECOS[categoria]["morador"]
                else:
                    preco = PRECOS[categoria]["normal"]

                col1, col2, col3 = st.columns([3,1,1])

                with col1:
                    st.write(f"**{produto}**  \nR$ {preco:.2f}")
                    if produto in FOTOS:
                        st.image(FOTOS[produto], width=120)

                with col2:
                    st.write(f"Est: {estoque}")

                with col3:
                    if estoque > 0:
                        qtd = st.number_input(
                            "Qtd",
                            min_value=0,
                            max_value=estoque,
                            key=f"qtd_{produto}"
                        )
                        if qtd:
                            total += qtd * preco
                            itens.append((produto, qtd))
                            precos_para_brinde.extend([preco] * qtd)
                    else:
                        st.write("❌")


    # -------- BRINDE ANIVERSÁRIO --------
    if eh_niver and precos_para_brinde:
        desconto = max(precos_para_brinde)
        total -= desconto
        st.success(f"🎂 NIVERDOCE aplicado! 1 item grátis (-R$ {desconto:.2f})")

    st.markdown(f"## 💰 Total: R$ {total:.2f}")

    # -------- ENTREGA --------
    st.header("🚚 Entrega")

    with st.expander("Confirmar dados de entrega", expanded=True):

        nome_recebimento = st.text_input("Nome para recebimento", value=u["nome"])

        if eh_morador:
            apto = st.text_input("Apartamento", value=u["end"])
            modo_entrega = st.radio(
                "Como prefere?",
                ["Entregar agora", "Agendar entrega", "Vou buscar no 902"]
            )

            horario_agendado = ""
            if modo_entrega == "Agendar entrega":
                horario_agendado = st.text_input("Horário desejado")

            detalhe_entrega = f"Apto {apto} | {modo_entrega}"
            if horario_agendado:
                detalhe_entrega += f" às {horario_agendado}"

            destinatario = NUMERO_YASMIN

        else:
            endereco = st.text_input("Endereço", value=u["end"])
            quem_recebe = st.text_input("Quem recebe", value=nome_recebimento)
            instrucoes = st.text_area("Instruções", value=u["inst"])

            detalhe_entrega = f"{endereco} | Recebe: {quem_recebe} | Obs: {instrucoes}"
            destinatario = NUMERO_JAQUE

        # -------- PAGAMENTO --------
    st.header("💳 Pagamento")

    opcoes_pagamento = ["PIX", "Dinheiro"]

    # GARAGEMLOLA adiciona opção extra
    if eh_garagem:
        opcoes_pagamento.append("Acertar na garagem")

    forma_pgto = st.radio("Forma de pagamento:", opcoes_pagamento)

    if forma_pgto == "PIX":
        st.success(f"🔑 Chave PIX: {CHAVE_PIX}")
        st.info(f"📧 Envie o comprovante para: {EMAIL_COMPROVANTE}")

    if forma_pgto == "Acertar na garagem":
        st.info("Pagamento será acertado posteriormente na garagem.")

    # -------- FINALIZAR --------
    if st.button("Finalizar Pedido", type="primary"):
        if not itens:
            st.warning("Escolha ao menos um item")
        else:
            for produto, qtd in itens:
                c.execute("INSERT INTO vendas VALUES (?,?,?,?,?,?)",
                          (datetime.now().strftime("%d/%m %H:%M"),
                           u["nome"], produto, qtd, total, forma_pgto))
            conn.commit()

            lista_txt = "\n".join([f"{qtd}x {prod}" for prod, qtd in itens])

            msg = (
                f"🍦 Pedido de {u['nome']}\n"
                f"📍 {detalhe_entrega}\n"
                f"💳 {forma_pgto}\n\n"
                f"{lista_txt}\n\n"
                f"💰 Total: R$ {total:.2f}"
            )

            link = f"https://wa.me/{destinatario}?text={urllib.parse.quote(msg)}"

            st.success("Pedido registrado!")
            st.link_button("Enviar no WhatsApp", link)
