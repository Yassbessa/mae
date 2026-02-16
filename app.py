import streamlit as st
import sqlite3
import urllib.parse
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASS = os.getenv("ADMIN_PASS")

NUMERO_YASMIN = os.getenv("NUMERO_YASMIN")
NUMERO_JAQUE = os.getenv("NUMERO_JAQUE")
CHAVE_PIX = os.getenv("CHAVE_PIX")

CUPOM_MORADOR = os.getenv("CUPOM_MORADOR")
CUPOM_GARAGEM = os.getenv("CUPOM_GARAGEM")

# ================= CONFIG =================
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")


# ================= PRODUTOS =================
PRODUTOS = {
    "❄️ Frutas (Sem Lactose)": ["Goiaba", "Uva", "Maracujá", "Manga", "Morango", "Abacaxi c/ Hortelã", "Frutopia"],
    "🍦 Gourmet (Cremosos)": ["Ninho c/ Nutella", "Ninho c/ Morango", "Chicabon", "Mousse de Maracujá",
                              "Pudim de Leite", "Açaí Cremoso", "Coco Cremoso"],
    "🍹 Alcoólicos (+18)": ["Piña Colada", "Sex on the Beach", "Caipirinha",
                            "Batida de Maracujá", "Batida de Morango"],
    "🥧 Salgados e Doces": ["Empadão Frango P (220mL)", "Empadão Frango G (500mL)", "Crunch Cake (180g)"]
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
    "Empadão Frango P (220mL)": "https://raw.githubusercontent.com/Yassbessa/mae/main/empadao.jpeg",
    "Empadão Frango G (500mL)": "https://raw.githubusercontent.com/Yassbessa/mae/main/empadão2.jpeg",
    "Crunch Cake (180g)": "https://raw.githubusercontent.com/Yassbessa/mae/main/bolo.jpeg"
}

# ================= BANCO =================
conn = sqlite3.connect('doceria.db', check_same_thread=False)
c = conn.cursor()

# ===== CRIA TABELAS SE NÃO EXISTIREM =====

c.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    nome TEXT,
    email TEXT PRIMARY KEY,
    senha TEXT,
    endereco TEXT,
    nascimento TEXT,
    instrucoes TEXT,
    tipo_cliente TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS vendas (
    data TEXT,
    cliente_email TEXT,
    item TEXT,
    categoria TEXT,
    qtd INTEGER,
    total REAL,
    cupom TEXT,
    status_pagamento TEXT
)
''')

conn.commit()

# garante coluna status_pagamento
try:
    c.execute("ALTER TABLE vendas ADD COLUMN status_pagamento TEXT")
except:
    pass

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
                tipo_cliente = "Morador" if "85" in endereco else "Externo"

                c.execute("""
                    INSERT INTO usuarios (nome, email, senha, endereco, nascimento, instrucoes, tipo_cliente)
                    VALUES (?,?,?,?,?,?,?)
                """, (nome, email, senha, endereco, nascimento, instrucoes, tipo_cliente))

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
            st.session_state.etapa = "painel_admin"
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
        
# =============== ADMIN =====================
elif st.session_state.etapa == "painel_admin":
    st.title("👑 Painel Admin - Ja Que É Doce")

    if st.button("⬅️ Sair do Painel"):
        st.session_state.etapa = "boas_vindas"
        st.rerun()

    # ----- DADOS -----
    df_vendas = pd.read_sql_query("SELECT * FROM vendas", conn)
    df_users = pd.read_sql_query("SELECT nome, email, endereco, tipo_cliente FROM usuarios", conn)

    if not df_vendas.empty:

        # 🔗 Junta vendas com usuários
        df = df_vendas.merge(df_users, left_on="cliente_email", right_on="email", how="left")

        # --- 1. PERFIL DE VENDAS ---
        st.subheader("👥 Perfil de Vendas")

        col1, col2 = st.columns(2)

        vendas_morador = df[df["tipo_cliente"] == "Morador"]["total"].sum()
        vendas_externo = df[df["tipo_cliente"] == "Externo"]["total"].sum()

        col1.metric("Faturamento Moradores", f"R$ {vendas_morador:.2f}")
        col2.metric("Faturamento Externos", f"R$ {vendas_externo:.2f}")

        st.divider()

        # --- 2. RANKING DE PRODUTOS ---
        st.subheader("🏆 Sabores Campeões")

        ranking = df.groupby("item")["qtd"].sum().sort_values(ascending=False)
        st.bar_chart(ranking)

        st.divider()

        # --- 3. RADAR DE MARKETING ---
        st.subheader("🎯 Radar de Marketing")

        preferencia = (
            df.groupby(["cliente_email", "nome", "item"])["qtd"]
            .sum()
            .reset_index()
        )

        top = preferencia.sort_values("qtd", ascending=False).drop_duplicates("cliente_email")

        for _, row in top.iterrows():
            nome_cliente = row["nome"]
            favorito = row["item"]

            frase = f"Olá {nome_cliente.split()[0]}, percebemos que você adorou nosso {favorito}! 😍"

            with st.expander(f"👤 {nome_cliente}"):
                st.write(f"💖 Favorito: {favorito}")
                st.code(frase)

        st.divider()

        # --- 4. TABELAS DETALHADAS ---
        tab1, tab2 = st.tabs(["📊 Histórico de Vendas", "👥 Usuários"])

        with tab1:
            st.dataframe(df_vendas, use_container_width=True)

        with tab2:
            st.dataframe(df_users, use_container_width=True)

    else:
        st.info("Ainda não temos vendas registo.")

# ================= CARDÁPIO =================
elif st.session_state.etapa == "cardapio":
    u = st.session_state.user

    if st.button("Sair"):
        st.session_state.etapa = "boas_vindas"
        st.rerun()

    st.title(f"Olá, {u['nome']} 🍦")

  # -------- CUPONS --------
cupom = st.text_input("Possui cupom?").upper()

eh_morador = CUPOM_MORADOR and CUPOM_MORADOR in cupom
eh_garagem = CUPOM_GARAGEM and CUPOM_GARAGEM in cupom
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




           # -------- PAGAMENTO SEGURO --------
    st.header("💳 Pagamento")

    opcoes_pagamento = ["PIX", "Dinheiro"]

    if eh_garagem:
        opcoes_pagamento.append("Acertar na garagem")

    forma_pgto = st.radio("Forma de pagamento:", opcoes_pagamento)

    comprovante = None

    if forma_pgto == "PIX":
        st.success(f"🔑 Chave PIX: {CHAVE_PIX}")
        comprovante = st.file_uploader(
            "Envie o comprovante do PIX",
            type=["png", "jpg", "jpeg", "pdf"]
        )

    # -------- FINALIZAR --------
    if st.button("Finalizar Pedido", type="primary"):
        if not itens:
            st.warning("Escolha ao menos um item")
            st.stop()

        # 🔒 exige comprovante para PIX
        if forma_pgto == "PIX" and comprovante is None:
            st.error("⚠️ Envie o comprovante do PIX para finalizar o pedido.")
            st.stop()

        # 💾 salva comprovante
        import os

        caminho_comprovante = ""
        if comprovante is not None:
            pasta = "comprovantes"
            os.makedirs(pasta, exist_ok=True)

            caminho_comprovante = os.path.join(pasta, comprovante.name)

            with open(caminho_comprovante, "wb") as f:
                f.write(comprovante.getbuffer())

        # define status do pagamento
        status_pagamento = "Pago" if forma_pgto == "PIX" else "Pendente"

        for produto, qtd in itens:
            categoria = next(cat for cat, lista in PRODUTOS.items() if produto in lista)

            c.execute("""
                INSERT INTO vendas (data, cliente_email, item, categoria, qtd, total, cupom, status_pagamento)
                VALUES (?,?,?,?,?,?,?,?)
            """,
            (datetime.now().strftime("%d/%m %H:%M"),
             u["email"], produto, categoria, qtd, total, cupom, status_pagamento))

        conn.commit()

        lista_txt = "\n".join([f"{qtd}x {prod}" for prod, qtd in itens])

       # -------- MENSAGEM WHATSAPP --------
        nome = u["nome"]
        
        msg = f"Oi Jaque! Sou *{nome}* e fiz meu pedido pelo app:\n\n"
        
        for produto, qtd in itens:
            msg += f"▪️ {qtd}x {produto}\n"
        
        msg += (
            f"\n Entrega: {detalhe_entrega}"
            f"\nPagamento: {forma_pgto}"
            f"\n Status: {status_pagamento}"
            f"\n\n*Total: R$ {total:.2f}*"
        )
        
        # 🔒 instruções extras para PIX
        if forma_pgto == "PIX":
            msg += (
                "\n\n O comprovante foi enviado pelo app."
                "\nSe não aparecer para você, posso reenviar por aqui."
            )
        
        link = f"https://wa.me/{destinatario}?text={urllib.parse.quote(msg)}"
        
        st.success("Pedido registrado com segurança!")
        st.link_button("Enviar pedido no WhatsApp", link)
