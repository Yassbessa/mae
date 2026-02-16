import streamlit as st
import sqlite3
import urllib.parse
import os
import re
import pdfplumber
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# ========= ENV ==================
load_dotenv()

ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASS = os.getenv("ADMIN_PASS")

NUMERO_YASMIN = os.getenv("NUMERO_YASMIN")
NUMERO_JAQUE = os.getenv("NUMERO_JAQUE")
CHAVE_PIX = "30.615.725 000155"

CUPOM_MORADOR = os.getenv("CUPOM_MORADOR")
CUPOM_GARAGEM = os.getenv("CUPOM_GARAGEM")

# =========== LER PIX =====================

def extrair_dados_pix(caminho_pdf):
    texto = ""

    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            conteudo = pagina.extract_text()
            if conteudo:
                texto += conteudo + "\n"

    # extrai valor em formato R$ 10,00 ou R$10.00
    valor = None
    match_valor = re.search(r"R\$\s?([\d\.,]+)", texto)

    if match_valor:
        valor = match_valor.group(1)

    return valor

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
    "Empadão Frango P (220mL)": 4,
    "Empadão Frango G (500mL)": 0,
    "Crunch Cake (180g)": 2
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

    # ___________ ALERTA DE ESTOQUE _________________
    st.subheader("📦 Status do Estoque")

    produtos_esgotados = {p: q for p, q in ESTOQUE.items() if q == 0}
    produtos_criticos = {p: q for p, q in ESTOQUE.items() if q == 1}

    if produtos_esgotados:
        st.error("❌ Produtos esgotados")
        st.write(produtos_esgotados)

    if produtos_criticos:
        st.warning("⚠️ Última unidade em estoque")
        st.write(produtos_criticos)

    if not produtos_esgotados and not produtos_criticos:
        st.success("✅ Estoque saudável")

    if st.button("⬅️ Sair do Painel"):
        st.session_state.etapa = "boas_vindas"
        st.rerun()

    # ===== CARREGA DADOS =====
    df_vendas = pd.read_sql_query("SELECT * FROM vendas", conn)
    df_users = pd.read_sql_query(
        "SELECT nome, email, endereco, tipo_cliente, nascimento FROM usuarios", conn
    )

    if df_vendas.empty:
        st.info("Ainda não temos vendas registradas.")
        st.stop()

    # Junta vendas com usuários
    df = df_vendas.merge(df_users, left_on="cliente_email", right_on="email", how="left")

    # Cria coluna mês
    df["mes"] = df["data"].str[3:5]

    # ===== SEPARAÇÃO DE PÚBLICO =====
    df_moradores = df[df["tipo_cliente"] == "Morador"]
    df_externos = df[df["tipo_cliente"] == "Externo"]

    tab_moradores, tab_externos, tab_geral = st.tabs(
        ["🏢 Machado Ribeiro", "🐝 Clientes JQD", "📊 Visão Geral"]
    )
    
    # _____________________🏢 MORADORES_______________________
    with tab_moradores:
        st.subheader("🏢 Moradores do Machado Ribeiro")

        faturamento = df_moradores["total"].sum()
        st.metric("💰 Faturamento Total", f"R$ {faturamento:.2f}")

        # Ranking
        st.subheader("🏆 Sabores Campeões")
        ranking = df_moradores.groupby("item")["qtd"].sum().sort_values(ascending=False)
        st.bar_chart(ranking)

        # Gasto por apto / cliente
        st.subheader("💰 Gasto por cliente")
        gasto_cliente = df_moradores.groupby("nome")["total"].sum().sort_values(ascending=False)
        st.dataframe(gasto_cliente)

        # Comportamento mensal
        st.subheader("📅 Comportamento mensal")
        mensal = df_moradores.groupby(["nome", "mes"])["total"].sum().reset_index()
        st.dataframe(mensal)

        # 🎂 Aniversariantes
        st.subheader("🎂 Aniversariantes do mês")
        mes_atual = datetime.now().strftime("%m")

        aniversariantes = df_users[
            (df_users["tipo_cliente"] == "Morador") &
            (df_users["nascimento"].str[3:5] == mes_atual)
        ]

        if not aniversariantes.empty:
            for _, row in aniversariantes.iterrows():
                nome = row["nome"]
                data = row["nascimento"]

                total_cliente = df_moradores[df_moradores["nome"] == nome]["total"].sum()

                st.success(f"🎉 {nome} faz aniversário em {data}")
                st.write(f"💰 Total gasto: R$ {total_cliente:.2f}")

                msg = (
                    f"Olá {nome}! 🎉\n"
                    "Seu aniversário está chegando e queremos comemorar com você! 🎂\n"
                    "Use o cupom *NIVERDOCE* e ganhe um sacolé à sua escolha grátis 🍦\n"
                    "Esperamos você! 💛"
                )
                st.code(msg)
        else:
            st.info("Nenhum aniversariante este mês.")

    # _____________🐝 CLIENTES EXTERNOS_________________________
    
    with tab_externos:
        st.subheader("🐝 Clientes JQD")

        faturamento = df_externos["total"].sum()
        st.metric("💰 Faturamento Total", f"R$ {faturamento:.2f}")

        # Ranking
        st.subheader("🏆 Sabores Campeões")
        ranking = df_externos.groupby("item")["qtd"].sum().sort_values(ascending=False)
        st.bar_chart(ranking)

        # Gasto por cliente
        st.subheader("💰 Gasto por cliente")
        gasto_cliente = df_externos.groupby("nome")["total"].sum().sort_values(ascending=False)
        st.dataframe(gasto_cliente)

        # Comportamento mensal
        st.subheader("📅 Comportamento mensal")
        mensal = df_externos.groupby(["nome", "mes"])["total"].sum().reset_index()
        st.dataframe(mensal)

        # 🎂 Aniversariantes
        st.subheader("🎂 Aniversariantes do mês")

        aniversariantes = df_users[
            (df_users["tipo_cliente"] == "Externo") &
            (df_users["nascimento"].str[3:5] == mes_atual)
        ]

        if not aniversariantes.empty:
            for _, row in aniversariantes.iterrows():
                nome = row["nome"]
                data = row["nascimento"]

                total_cliente = df_externos[df_externos["nome"] == nome]["total"].sum()

                st.success(f"🎉 {nome} faz aniversário em {data}")
                st.write(f"💰 Total gasto: R$ {total_cliente:.2f}")
                
                msg = (
                    f"Olá {nome}! 🎉\n"
                    "Seu aniversário está chegando e queremos comemorar com você! 🎂\n"
                    "Use o cupom *NIVERDOCE* e ganhe um sacolé à sua escolha grátis 🍦\n"
                    "Esperamos você! 💛"
                )
                st.code(msg)
        else:
            st.info("Nenhum aniversariante este mês.")


    # 📊 VISÃO GERAL
    with tab_geral:
        st.subheader("📊 Visão Geral")

        col1, col2 = st.columns(2)
        col1.metric("Moradores", f"R$ {df_moradores['total'].sum():.2f}")
        col2.metric("Externos", f"R$ {df_externos['total'].sum():.2f}")

        # Exportação mensal
        st.subheader("📥 Exportar relatório mensal")
        meses = sorted(df["mes"].unique())
        mes_escolhido = st.selectbox("Escolha o mês", meses)

        df_mes = df[df["mes"] == mes_escolhido]

        st.download_button(
            "📄 Baixar planilha do mês",
            df_mes.to_csv(index=False),
            file_name=f"relatorio_mes_{mes_escolhido}.csv",
            mime="text/csv"
        )

        # Tabelas completas
        st.subheader("📊 Histórico completo")
        st.dataframe(df)

        # 🧹 Excluir vendas de teste
        st.subheader("🧹 Limpar vendas de teste")
        if st.button("Excluir vendas com cliente vazio"):
            c.execute("DELETE FROM vendas WHERE cliente_email IS NULL")
            conn.commit()
            st.success("Vendas de teste removidas!")
            st.rerun()

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
    PRECOS = {
        "❄️ Frutas (Sem Lactose)": {"normal": 8.0, "morador": 5.0},
        "🍦 Gourmet (Cremosos)": {"normal": 9.0, "morador": 7.0},
        "🍹 Alcoólicos (+18)": {"normal": 10.0, "morador": 9.0},
        "🥧 Salgados e Doces": {"normal": 12.0, "morador": 12.0}
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

        # interface única para todos
        modo_entrega = st.radio(
            "Como prefere receber?",
            ["Entregar agora", "Agendar entrega", "Retirar no local"]
        )

        horario_agendado = ""
        if modo_entrega == "Agendar entrega":
            horario_agendado = st.text_input("Horário desejado")

        # dados específicos por tipo de cliente
        if eh_morador:
            apto = st.text_input("Apartamento", value=u["end"])
            detalhe_entrega = f"Apto {apto} | {modo_entrega}"
            destinatario = NUMERO_YASMIN
        else:
            endereco = st.text_input("Endereço", value=u["end"])
            quem_recebe = st.text_input("Quem recebe", value=nome_recebimento)
            instrucoes = st.text_area("Instruções", value=u["inst"])

            detalhe_entrega = f"{endereco} | Recebe: {quem_recebe} | Obs: {instrucoes} | {modo_entrega}"
            destinatario = NUMERO_JAQUE

        if horario_agendado:
            detalhe_entrega += f" às {horario_agendado}"


           # -------- PAGAMENTO SEGURO --------
    st.header("💳 Pagamento")

    opcoes_pagamento = ["PIX", "Dinheiro"]

    if eh_garagem:
        opcoes_pagamento.append("Acertar na garagem")

    forma_pgto = st.radio("Forma de pagamento:", opcoes_pagamento)

    comprovante = None

    if forma_pgto == "PIX":
        st.success(f"🔑 Chave PIX: 30.615.725 000155")
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
        caminho_comprovante = ""
        if comprovante is not None:
            pasta = "comprovantes"
            os.makedirs(pasta, exist_ok=True)

            caminho_comprovante = os.path.join(pasta, comprovante.name)

            with open(caminho_comprovante, "wb") as f:
                f.write(comprovante.getbuffer())

        # ===== STATUS DO PAGAMENTO =====
        status_pagamento = "Pendente"

        if forma_pgto == "PIX" and caminho_comprovante.endswith(".pdf"):
            valor_pdf = extrair_dados_pix(caminho_comprovante)

            if valor_pdf:
                try:
                    valor_pdf_float = float(valor_pdf.replace(".", "").replace(",", "."))
                    if abs(valor_pdf_float - total) < 0.01:
                        status_pagamento = "Pago Confirmado"
                    else:
                        status_pagamento = "⚠️ Valor Divergente"
                except:
                    status_pagamento = "Erro ao ler valor"
            else:
                status_pagamento = "Valor não encontrado"

        elif forma_pgto == "PIX":
            status_pagamento = "Comprovante enviado"

        elif forma_pgto == "Dinheiro":
            status_pagamento = "Pagamento na entrega"

        # ===== SALVA NO BANCO =====
        for produto, qtd in itens:
            categoria = next(cat for cat, lista in PRODUTOS.items() if produto in lista)

            c.execute("""
                INSERT INTO vendas (data, cliente_email, item, categoria, qtd, total, cupom, status_pagamento)
                VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                datetime.now().strftime("%d/%m %H:%M"),
                u["email"],
                produto,
                categoria,
                qtd,
                total,
                cupom,
                status_pagamento
            ))

        conn.commit()

        # ===== MENSAGEM WHATSAPP =====
        nome = u["nome"]

        msg = f"Oi Jaque! Sou *{nome}* e fiz meu pedido pelo app:\n\n"

        for produto, qtd in itens:
            msg += f"▪️ {qtd}x {produto}\n"

        msg += (
            f"\n Entrega: {detalhe_entrega}"
            f"\n Pagamento: {forma_pgto}"
            f"\n Status: {status_pagamento}"
            f"\n\n*Total: R$ {total:.2f}*"
        )

        if forma_pgto == "PIX":
            msg += (
                "\n\n Enviei o comprovante pelo app."
                "\nSe não aparecer para você, posso reenviar por aqui."
            )

        link = f"https://wa.me/{destinatario}?text={urllib.parse.quote(msg)}"

        st.success("Pedido registrado com segurança!")
        st.link_button("Enviar pedido no WhatsApp", link)
