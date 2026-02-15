import streamlit as st
import urllib.parse
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CONTATOS ---
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
    
    # 1. IDENTIFICAÇÃO E DATA DE NASCIMENTO (INÍCIO)
    c1, c2 = st.columns(2)
    with c1:
        cupons = st.text_input("Cupom (Morador ou Niver):").strip().upper()
    with c2:
        data_nasc = st.date_input("Sua Data de Nascimento:", help="Ganhe brindes no seu niver!")

    eh_morador = cupons in ["MACHADORIBEIRO", "GARAGEMLOLA"]
    p_fruta = 5.0 if eh_morador else 8.0
    p_gourmet = 7.0 if eh_morador else 9.0
    
    pedido_zap = []
    dados_venda_lista = [] 
    total_bruto = 0.0

    # --- CATEGORIA: SACOLÉS ---
    st.header("❄️ Sacolés")
    estoque = {
        "Gourmet": [("Ninho c/ Nutella", p_gourmet, 5), ("Chicabon", p_gourmet, 4)],
        "Frutas": [("Goiaba", p_fruta, 4), ("Manga", p_fruta, 4)]
    }

    for cat, itens in estoque.items():
        with st.expander(cat, expanded=True):
            for nome_i, preco_i, est_i in itens:
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.write(f"**{nome_i}**\nR$ {preco_i:.2f}")
                col2.write(f"Est: {est_i}")
                qtd = col3.number_input("Qtd", 0, est_i, key=f"q_{nome_i}", label_visibility="collapsed")
                if qtd > 0:
                    total_bruto += (qtd * preco_i)
                    pedido_zap.append(f"✅ {qtd}x {nome_i}")
                    dados_venda_lista.append({"ITEM": nome_i, "QNTD": qtd, "PREÇO": preco_i})

    # --- CATEGORIA: SALGADOS E BOLOS ---
    st.header("🥧 Salgados e Doces")
    c_img, c_txt = st.columns([1, 2])
    with c_img: st.image("https://raw.githubusercontent.com/Yassbessa/mae/main/empadao.jpeg")
    with c_txt:
        q_p = st.number_input("Empadão P (R$ 12,00)", 0, 5, key="q_p")
        if q_p > 0:
            total_bruto += (q_p * 12.0); pedido_zap.append(f"✅ {q_p}x Empadão P"); dados_venda_lista.append({"ITEM": "Empadão P", "QNTD": q_p, "PREÇO": 12.0})

    # --- TOTAL 1 (SUBTOTAL) ---
    if total_bruto > 0:
        st.markdown(f"## 💰 Subtotal: R$ {total_bruto:.2f}")
        st.divider()

        # --- DADOS DE ENTREGA ---
        nome_cli = st.text_input("Seu Nome:")
        apto_cli = st.text_input("Apto / Endereço:")
        pagto = st.radio("Pagamento:", ["PIX", "Dinheiro", "Cartão"])
        entrega_op = st.radio("Entrega:", ["Entregar agora", "Buscar no 902", "Agendar"])
        
        # --- TOTAL 2 (FINAL) ---
        st.markdown(f"### Total Final: R$ {total_bruto:.2f}")

        if st.button("🚀 FINALIZAR E ENVIAR", type="primary"):
            if nome_cli and apto_cli:
                data_h = pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
                niver_s = data_nasc.strftime("%d/%m")

                # Criando as linhas para a planilha (uma linha por item)
                df_rows = []
                for d in dados_venda_lista:
                    df_rows.append({
                        "DATA": data_h, "NOME": nome_cli, "APT/END": apto_cli,
                        "NASCIMENTO": niver_s, "ITEM": d['ITEM'], "QNTD": d['QNTD'], 
                        "PREÇO": d['PREÇO'], "TOTAL": total_bruto,
                        "PGTO": pagto, "ENTREGA": entrega_op
                    })
                
                # ENVIO SILENCIOSO PARA A PLANILHA
                try:
                    df_final = pd.DataFrame(df_rows)
                    conn.create(data=df_final, worksheet="Página1") # Use o nome da aba que aparece no rodapé da sua planilha
                    st.success("Pedido registrado!")
                except:
                    st.info("Aguardando configuração de Secrets para salvar...")

                # WHATSAPP
                msg = f"🍦 *PEDIDO*\n👤 {nome_cli}\n📍 {apto_cli}\n🎂 Niver: {niver_s}\n📦 {', '.join(pedido_zap)}\n💰 *TOTAL: R$ {total_bruto:.2f}*"
                dest = NUMERO_YASMIN if eh_morador else NUMERO_JAQUE
                st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'https://wa.me/{dest}?text={urllib.parse.quote(msg)}\' /">', unsafe_allow_html=True)
