import streamlit as st
import urllib.parse
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- DADOS FIXOS DO NEGÓCIO ---
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

    # --- BLOCO FIXO: INSTRUÇÕES ---
    with st.expander("💡 Dicas de Conservação e Consumo", expanded=False):
        st.markdown("""
        * **🍦 Sacolés:** Manter no congelador até o consumo.
        * **🥧 Empadão:** Aquecer no forno ou air-fryer por 10-15 min para ficar crocante.
        * **🍰 Crunch Cake:** Manter refrigerado para melhor sabor.
        """)
    
    # 1. IDENTIFICAÇÃO (CUPOM E NASCIMENTO)
    c1, c2 = st.columns(2)
    with c1:
        cupons = st.text_input("Cupom (Morador ou Niver):").strip().upper()
    with c2:
        data_nasc = st.date_input("Sua Data de Nascimento:", help="Ganhe brindes no seu niver!")

    eh_morador = cupons in ["MACHADORIBEIRO", "GARAGEMLOLA"]
    p_fruta = 5.0 if eh_morador else 8.0
    p_gourmet = 7.0 if eh_morador else 9.0
    p_alcoolico = 9.0 if eh_morador else 10.0

    pedido_itens_zap = []
    dados_venda_mestra = [] 
    total_bruto = 0.0

    # ==========================================
    # BLOCO FIXO 1: SACOLÉS (LISTA COMPLETA)
    # ==========================================
    st.header("❄️ Nossos Sacolés")
    estoque_sacoles = {
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

    for categoria, itens in estoque_sacoles.items():
        with st.expander(categoria, expanded=True):
            for i in itens:
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{i['item']}**\nR$ {i['p']:.2f}")
                c2.write(f"Est: {i['est']}")
                if i['est'] > 0:
                    qtd = c3.number_input("Qtd", 0, i['est'], key=f"sac_{i['item']}", label_visibility="collapsed")
                    if qtd > 0:
                        total_bruto += (qtd * i['p'])
                        pedido_itens_zap.append(f"✅ {qtd}x {i['item']}")
                        dados_venda_mestra.append({"Item": i['item'], "Qtd": qtd, "Preco": i['p']})
                else:
                    c3.write("❌")

    # ==========================================
    # BLOCO FIXO 2: SALGADOS E SOBREMESAS
    # ==========================================
    st.header("🥧 Salgados e Sobremesas")
    estoque_extras = {
        "Salgados": [
            {"item": "Empadão Frango (P)", "p": 12.0, "est": 5, "img": "https://raw.githubusercontent.com/Yassbessa/mae/main/empadao.jpeg"},
            {"item": "Empadão Frango (G)", "p": 18.0, "est": 0, "img": "https://raw.githubusercontent.com/Yassbessa/mae/main/empadao.jpeg"}
        ],
        "Doces": [
            {"item": "Crunch Cake", "p": 10.0, "est": 4, "img": "https://raw.githubusercontent.com/Yassbessa/mae/main/bolo.jpeg"}
        ]
    }

    for categoria, itens in estoque_extras.items():
        st.subheader(categoria)
        for i in itens:
            c_img, c_info, c_qtd = st.columns([1, 2, 1])
            with c_img:
                st.image(i['img'], width=80)
            with c_info:
                st.write(f"**{i['item']}**\nR$ {i['p']:.2f}")
                st.caption(f"Estoque: {i['est']}")
            with c_qtd:
                if i['est'] > 0:
                    qtd = st.number_input("Qtd", 0, i['est'], key=f"extra_{i['item']}", label_visibility="collapsed")
                    if qtd > 0:
                        total_bruto += (qtd * i['p'])
                        pedido_itens_zap.append(f"✅ {qtd}x {i['item']}")
                        dados_venda_mestra.append({"Item": i['item'], "Qtd": qtd, "Preco": i['p']})
                else:
                    st.write("❌")

    # --- FINALIZAÇÃO ---
    if total_bruto > 0:
        st.markdown(f"## 💰 Subtotal: R$ {total_bruto:.2f}") # Exibição 1
        st.divider()

        nome_cli = st.text_input("Seu Nome:")
        apto_cli = st.text_input("Apto / Endereço:")
        pagto = st.radio("Pagamento:", ["PIX", "Dinheiro", "Cartão"])
        entrega_op = st.radio("Como prefere?", ["Entregar agora", "Buscar no 902", "Agendar Entrega"])
        
        if pagto == "PIX":
            st.info(f"🔑 PIX: {CHAVE_PIX} | 📧 Envie o comprovante para {EMAIL_COMPROVANTE}")

        st.markdown(f"### Total Final: R$ {total_bruto:.2f}") # Exibição 2
        
        if st.button("🚀 FINALIZAR E ENVIAR", type="primary"):
            if nome_cli and apto_cli:
                data_h = pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
                niver_s = data_nasc.strftime("%d/%m")

                # Preparando as linhas para a Tabela Mestra (Vendas_Geral)
                linhas = []
                for d in dados_venda_mestra:
                    linhas.append({
                        "DATA": data_h, "NOME": nome_cli, "APT/END": apto_cli,
                        "NASCIMENTO": niver_s, "ITEM": d['Item'], "QNTD": d['Qtd'], 
                        "PREÇO": d['Preco'], "TOTAL": total_bruto,
                        "PGTO": pagto, "ENTREGA": entrega_op
                    })
                
                df_final = pd.DataFrame(linhas)
                
                # SALVANDO NA PLANILHA (Nome da aba deve ser Vendas_Geral ou Página1)
                try:
                    conn.create(data=df_final, worksheet="Vendas_Geral")
                    st.success("Pedido registrado na planilha!")
                except:
                    st.warning("Verifique a configuração das 'Secrets' para salvar na planilha.")

                # WHATSAPP
                msg = f"🍦 *NOVO PEDIDO*\n👤 {nome_cli}\n📍 {apto_cli}\n🎂 Niver: {niver_s}\n📦 {', '.join(pedido_itens_zap)}\n💰 *TOTAL: R$ {total_bruto:.2f}*"
                dest = NUMERO_YASMIN if eh_morador else NUMERO_JAQUE
                st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'https://wa.me/{dest}?text={urllib.parse.quote(msg)}\' /">', unsafe_allow_html=True)
            else:
                st.error("Preencha seu nome e endereço!")
