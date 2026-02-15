import streamlit as st
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ja Que é Doce!", page_icon="🐝", layout="centered")

if 'abriu_cardapio' not in st.session_state:
    st.session_state.abriu_cardapio = False

# --- CONTATOS ---
NUMERO_YASMIN = "5521981816105" 
NUMERO_JAQUE = "5521976141210" 
CHAVE_PIX = "30.615.725 000155" 

# --- TELA 1: BOAS-VINDAS ---
if not st.session_state.abriu_cardapio:
    st.markdown("<h1 style='text-align: center; color: #E67E22;'>Jaque é Doce! 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    st.markdown("<h3 style='text-align: center;'>Feitos artesanalmente para você. ❤️</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✨ VER CARDÁPIO E ESTOQUE", use_container_width=True):
            st.session_state.abriu_cardapio = True
            st.rerun()

# --- TELA 2: CARDÁPIO ---
else:
    if st.button("⬅️ Voltar"):
        st.session_state.abriu_cardapio = False
        st.rerun()

    st.title("Cardápio do Dia 🍦")
    
    cupons_input = st.text_input("Possui cupons?").strip().upper()
    eh_morador = ("MACHADORIBEIRO" in cupons_input or "GARAGEMLOLA" in cupons_input)
    cupom_niver = "ANIVERSARIO" in cupons_input
    
    p_fruta = 5.00 if eh_morador else 8.00
    p_gourmet = 7.00 if eh_morador else 9.00
    p_alcoolico = 9.00 if eh_morador else 10.00

    pedido = []
    total_bruto = 0.0

    # --- SACOLÉS (SEM FOTO) ---
    st.header("❄️ Sacolés")
    estoque_sacoles = {
        "Frutas (Sem Lactose)": [{"item": "Goiaba", "p": p_fruta, "est": 4}, {"item": "Manga", "p": p_fruta, "est": 4}, {"item": "Abacaxi c/ Hortelã", "p": p_fruta, "est": 1}],
        "Gourmet (Cremosos)": [{"item": "Ninho c/ Nutella", "p": p_gourmet, "est": 5}, {"item": "Chicabon", "p": p_gourmet, "est": 4}, {"item": "Coco Cremoso", "p": p_gourmet, "est": 6}],
        "Alcoólicos (+18)": [{"item": "Piña Colada", "p": p_alcoolico, "est": 1}, {"item": "Caipirinha", "p": p_alcoolico, "est": 2}]
    }

    for cat, itens in estoque_sacoles.items():
        with st.expander(cat, expanded=True):
            for i in itens:
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{i['item']}** - R$ {i['p']:.2f}")
                c2.write(f"Estoque: {i['est']}")
                q = c3.number_input("Qtd", 0, i['est'], key=f"q_{i['item']}", label_visibility="collapsed")
                if q > 0:
                    total_bruto += (q * i['p'])
                    pedido.append(f"✅ {q}x {i['item']}")

    # --- EMPADÃO (COM FOTO AO LADO) ---
    st.header("🥧 Salgados")
    col_img_e, col_txt_e = st.columns([1, 1.5])
    with col_img_e:
        st.image("https://raw.githubusercontent.com/Yassbessa/mae/principal/empadão2.jpeg")
    with col_txt_e:
        st.write("**Empadão Frango (P)**")
        st.write("R$ 12.00 | Estoque: 4")
        q_emp = st.number_input("Quantidade", 0, 4, key="q_emp_p")
        if q_emp > 0:
            total_bruto += (q_emp * 12.00)
            pedido.append(f"✅ {q_emp}x Empadão P")

    # --- BOLO (COM FOTO AO LADO) ---
    st.header("🍰 Sobremesas")
    col_img_b, col_txt_b = st.columns([1, 1.5])
    with col_img_b:
        st.image("https://raw.githubusercontent.com/Yassbessa/mae/principal/bolo.jpeg")
    with col_txt_b:
        st.write("**Crunch Cake (Pote)**")
        st.write("R$ 10.00 | Estoque: 4")
        q_bolo = st.number_input("Quantidade", 0, 4, key="q_bolo")
        if q_bolo > 0:
            total_bruto += (q_bolo * 10.00)
            pedido.append(f"✅ {q_bolo}x Bolo Pote")

    # --- FINALIZAÇÃO ---
    if total_bruto > 0:
        st.divider()
        st.subheader(f"Total: R$ {total_bruto:.2f}")
        nome = st.text_input("Seu Nome:")
        apto = st.text_input("Seu Apto / Bloco:")
        entrega = st.radio("Como prefere?", ["Entregar agora", "Buscar no 902", "Agendar"])
        
        if nome and apto:
            destinatario = NUMERO_YASMIN if eh_morador else NUMERO_JAQUE
            msg = f"🍦 *NOVO PEDIDO*\n📍 Apto: {apto}\n👤 Nome: {nome}\n🕒 Hora: {entrega}\n\n*ITENS:*\n" + "\n".join(pedido)
            st.link_button("🚀 ENVIAR PEDIDO", f"https://wa.me/{destinatario}?text={urllib.parse.quote(msg)}", type="primary")
