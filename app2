import streamlit as st
import urllib.parse
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- DADOS FIXOS ---
NUMERO_YASMIN = "5521981816105" 
NUMERO_JAQUE = "5521976141210" 
CHAVE_PIX = "30.615.725 000155" 
EMAIL_COMPROVANTE = "jaqueedoce@gmail.com"

if 'abriu_cardapio' not in st.session_state:
    st.session_state.abriu_cardapio = False

# --- TELA 1: BOAS-VINDAS ---
if not st.session_state.abriu_cardapio:
    st.markdown("<h1 style='text-align: center; color: #E67E22;'>Ja Que É Doce 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    st.markdown("<h3 style='text-align: center;'>Feitos artesanalmente para você. ❤️</h3>", unsafe_allow_html=True)
    
    col_v = st.columns([1, 2, 1])
    if col_v[1].button("✨ VER CARDÁPIO E ESTOQUE", use_container_width=True):
        st.session_state.abriu_cardapio = True
        st.rerun()

# --- TELA 2: CARDÁPIO ---
else:
    if st.button("⬅️ Voltar"):
        st.session_state.abriu_cardapio = False
        st.rerun()

    st.title("Cardápio do Dia 🍦")
    
    # Sistema de Cupom e Nascimento
    c1, c2 = st.columns(2)
    with c1:
        cupons = st.text_input("Cupom (Morador ou Niver):").strip().upper()
    with c2:
        data_nasc = st.date_input("Sua Data de Nascimento:", help="Cadastre-se para o cupom aniversário!")

    eh_morador = cupons in ["MACHADORIBEIRO", "GARAGEMLOLA"]
    p_fruta = 5.0 if eh_morador else 8.0
    p_gourmet = 7.0 if eh_morador else 9.0
    p_alcoolico = 9.0 if eh_morador else 10.0

    pedido_itens_zap = []
    dados_venda_detalhada = [] 
    total_bruto = 0.0

    # --- BLOCO: SACOLÉS ---
    st.header("❄️ Sacolés")
    estoque_full = {
        "Frutas": [("Goiaba", p_fruta, 4), ("Manga", p_fruta, 4), ("Frutopia", p_fruta, 3)],
        "Gourmet": [("Ninho c/ Nutella", p_gourmet, 5), ("Chicabon", p_gourmet, 4), ("Pudim", p_gourmet, 5)],
        "Alcoólicos": [("Piña Colada", p_alcoolico, 1), ("Caipirinha", p_alcoolico, 2)]
    }

    for cat, itens in estoque_full.items():
        with st.expander(cat, expanded=True):
            for nome_i, preco_i, est_i in itens:
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.write(f"**{nome_i}**\nR$ {preco_i:.2f}")
                col2.write(f"Est: {est_i}")
                qtd = col3.number_input("Qtd", 0, est_i, key=f"q_{nome_i}", label_visibility="collapsed")
                if qtd > 0:
                    total_bruto += (qtd * preco_i)
                    pedido_itens_zap.append(f"✅ {qtd}x {nome_i}")
                    dados_venda_detalhada.append({"Item": nome_i, "Qtd": qtd, "Preco": preco_i})

    # --- BLOCO: SALGADOS E BOLO ---
    st.header("🥧 Salgados e Doces")
    col_img, col_txt = st.columns([1, 2])
    with col_img:
        st.image("https://raw.githubusercontent.com/Yassbessa/mae/main/empadao.jpeg")
    with col_txt:
        q_p = st.number_input("Empadão P (R$ 12,00)", 0, 5, key="q_p")
        q_g = st.number_input("Empadão G (R$ 18,00)", 0, 2, key="q_g")
    
    col_img2, col_txt2 = st.columns([1, 2])
    with col_img2:
        st.image("https://raw.githubusercontent.com/Yassbessa/mae/main/bolo.jpeg")
    with col_txt2:
        q_b = st.number_input("Crunch Cake (R$ 10,00)", 0, 4, key="q_b")

    # Registro de Salgados/Bolo
    if q_p > 0:
        total_bruto += (q_p * 12.0); pedido_itens_zap.append(f"✅ {q_p}x Empadão P"); dados_venda_detalhada.append({"Item": "Empadão P", "Qtd": q_p, "Preco": 12.0})
    if q_g > 0:
        total_bruto += (q_g * 18.0); pedido_itens_zap.append(f"✅ {q_g}x Empadão G"); dados_venda_detalhada.append({"Item": "Empadão G", "Qtd": q_g, "Preco": 18.0})
    if q_b > 0:
        total_bruto += (q_b * 10.0); pedido_itens_zap.append(f"✅ {q_b}x Bolo Pote"); dados_venda_detalhada.append({"Item": "Bolo Pote", "Qtd": q_b, "Preco": 10.0})

    # --- FINALIZAÇÃO ---
    if total_bruto > 0:
        st.divider()
        st.subheader(f"Total: R$ {total_bruto:.2f}")
        nome_cli = st.text_input("Seu Nome:")
        apto_cli = st.text_input("Apto / Bloco:")
        
        # Lógica de entrega
        entrega_op = st.radio("Como prefere?", ["Entregar agora", "Buscar no 902", "Agendar Entrega"])
        horario = st.text_input("Horário (se agendou):") if entrega_op == "Agendar Entrega" else ""
        
        pagto = st.radio("Pagamento:", ["PIX", "Dinheiro", "Cartão"])
        if pagto == "PIX":
            st.info(f"🔑 PIX: {CHAVE_PIX} | 📧 Comprovante: {EMAIL_COMPROVANTE}")

        # BOTÃO FINAL - SALVA NAS 4 ABAS E ABRE WHATSAPP
        if st.button("🚀 FINALIZAR E ENVIAR", type="primary"):
            if nome_cli and apto_cli:
                data_str = pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
                niver_str = data_nasc.strftime("%d/%m")

                # 1. ABA VENDAS
                df_v = pd.DataFrame([{"Data": data_str, "Nome": nome_cli, "Apto": apto_cli, "Total": total_bruto, "Pagto": pagto, "Entrega": f"{entrega_op} {horario}"}])
                # conn.create(worksheet="Vendas", data=df_v)

                # 2. ABA ITENS_VENDIDOS
                df_i = pd.DataFrame([{"Data": data_str, "Apto": apto_cli, "Item": d['Item'], "Qtd": d['Qtd'], "Preco_Unit": d['Preco']} for d in dados_venda_detalhada])
                # conn.create(worksheet="Itens_Vendidos", data=df_i)

                # 3. ABA CLIENTES
                df_c = pd.DataFrame([{"Nome": nome_cli, "Apto": apto_cli, "Nascimento": niver_str}])
                # conn.create(worksheet="Clientes", data=df_c)

                # 4. ABA PRODUTOS_MAIS_VENDIDOS (Soma de Itens)
                df_p = pd.DataFrame([{"Item": d['Item'], "Qtd_Total": d['Qtd']} for d in dados_venda_detalhada])
                # conn.create(worksheet="Produtos_Mais_Vendidos", data=df_p)

                # WHATSAPP
                msg = f"🍦 *NOVO PEDIDO*\n👤 {nome_cli}\n📍 Apto: {apto_cli}\n🎂 Niver: {niver_str}\n📦 {', '.join(pedido_itens_zap)}\n💰 *TOTAL: R$ {total_bruto:.2f}*"
                dest = NUMERO_YASMIN if eh_morador else NUMERO_JAQUE
                st.success("Tudo certo! Redirecionando...")
                st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'https://wa.me/{dest}?text={urllib.parse.quote(msg)}\' /">', unsafe_allow_html=True)
            else:
                st.error("Preencha Nome e Apto!")
