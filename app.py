import streamlit as st
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Jaque é Doce!", page_icon="🐝", layout="centered")

# --- CONTROLE DE NAVEGAÇÃO ---
if 'abriu_cardapio' not in st.session_state:
    st.session_state.abriu_cardapio = False

# --- DADOS ---
NUMERO_YASMIN = "5521981816105" 
NUMERO_JAQUE = "5521976141210" 
CHAVE_PIX = "30.615.725 000155" 

# --- TELA 1: INTERFACE CONVIDATIVA ---
if not st.session_state.abriu_cardapio:
    st.markdown("<h1 style='text-align: center; color: #E67E22;'>Jaque é Doce! 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # Foto de capa baseada na sua logo e sacolés
    st.image("https://raw.githubusercontent.com/Yassbessa/mae/principal/image_0073e0.jpg", caption="Delícias artesanais feitas com carinho ❤️", use_container_width=True)
    
    st.markdown("<h3 style='text-align: center;'>Bem-vindo(a), vizinho(a)!</h3>", unsafe_allow_html=True)
    st.write("É um prazer ter você aqui. Preparamos nossos sacolés, empadões e bolos com os melhores ingredientes para adoçar o seu dia.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✨ VER CARDÁPIO E ESTOQUE", use_container_width=True):
            st.session_state.abriu_cardapio = True
            st.rerun()
    st.markdown("<p style='text-align: center; font-size: 0.8em; color: gray;'>Retiradas no apto 902 ou Entregas rápidas</p>", unsafe_allow_html=True)

# --- TELA 2: CARDÁPIO COMPLETO ---
else:
    if st.button("⬅️ Voltar para o Início"):
        st.session_state.abriu_cardapio = False
        st.rerun()

    st.title("Nosso Cardápio 🍦")
    
    # Campo de Cupons (Aniversário e Morador)
    cupons_input = st.text_input("Possui cupons? (Ex: MACHADORIBEIRO, ANIVERSARIO)").strip().upper()
    lista_cupons = [c.strip() for c in cupons_input.split(",")]
    
    eh_morador = ("MACHADORIBEIRO" in lista_cupons or "GARAGEMLOLA" in lista_cupons)
    cupom_niver = "ANIVERSARIO" in lista_cupons
    
    # Preços diferenciados conforme o cupom
    p_fruta = 5.00 if eh_morador else 8.00
    p_gourmet = 7.00 if eh_morador else 9.00
    p_alcoolico = 9.00 if eh_morador else 10.00

    if eh_morador:
        st.success("🏠 Vizinho identificado! Preços especiais aplicados.")
    if cupom_niver:
        st.balloons()
        st.info("🎂 Feliz Aniversário! Você ganhou um sacolé de brinde (desconto aplicado no final).")

    pedido = []
    total_bruto = 0.0
    valor_brinde = 0.0

    # --- CATEGORIA: SACOLÉS ---
    st.header("❄️ Sacolés Gourmet & Tropicais")
    st.image("https://raw.githubusercontent.com/Yassbessa/mae/principal/image_0073e0.jpg", caption="Sabores Tropicais, Gourmet e Alcoólicos")
    
    categorias_sacoles = {
        "Tropicais (Sem Lactose)": [{"item": "Goiaba", "p": p_fruta, "est": 4}, {"item": "Manga", "p": p_fruta, "est": 4}, {"item": "Abacaxi com Hortelã", "p": p_fruta, "est": 1}],
        "Gourmet (Cremosos)": [{"item": "Ninho com Nutella", "p": p_gourmet, "est": 5}, {"item": "Coco Cremoso", "p": p_gourmet, "est": 6}, {"item": "Chicabon", "p": p_gourmet, "est": 4}],
        "Alcoólicos (+18)": [{"item": "Caipirinha", "p": p_alcoolico, "est": 2}, {"item": "Piña Colada", "p": p_alcoolico, "est": 1}]
    }

    for cat, itens in categorias_sacoles.items():
        with st.expander(cat, expanded=True):
            for i in itens:
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{i['item']}**\nR$ {i['p']:.2f}")
                c2.write(f"Estoque: {i['est']}")
                if i['est'] > 0:
                    qtd = c3.number_input("Qtd", 0, i['est'], key=f"q_{i['item']}", label_visibility="collapsed")
                    if qtd > 0:
                        total_bruto += (qtd * i['p'])
                        pedido.append(f"✅ {qtd}x {i['item']}")
                        if cupom_niver: valor_brinde = i['p'] # Aplica o desconto do brinde
                else:
                    c3.write("❌")

    # --- CATEGORIA: EMPADÃO ---
    st.header("🥧 Empadão Cremoso")
    st.image("https://raw.githubusercontent.com/Yassbessa/mae/principal/empadão2.jpeg", caption="Massa que desmancha na boca")
    c1, c2, c3 = st.columns([3, 1, 1])
    c1.write("**Empadão Frango (P - 220ml)**\nR$ 12.00")
    c2.write("Estoque: 4")
    qtd_emp = c3.number_input("Qtd", 0, 4, key="q_emp")
    if qtd_emp > 0:
        total_bruto += (qtd_emp * 12.00)
        pedido.append(f"✅ {qtd_emp}x Empadão P")

    # --- CATEGORIA: BOLO ---
    st.header("🍰 Bolo Crunch Cake")
    st.image("https://raw.githubusercontent.com/Yassbessa/mae/principal/bolo.jpeg", caption="Chocolate cremoso e crocante")
    c1, c2, c3 = st.columns([3, 1, 1])
    c1.write("**Crunch Cake (Pote 180g)**\nR$ 10.00")
    c2.write("Estoque: 4")
    qtd_bolo = c3.number_input("Qtd", 0, 4, key="q_bolo")
    if qtd_bolo > 0:
        total_bruto += (qtd_bolo * 10.00)
        pedido.append(f"✅ {qtd_bolo}x Bolo Crunch Cake")

    # --- FINALIZAÇÃO ---
    if total_bruto > 0:
        st.divider()
        total_final = total_bruto - valor_brinde
        st.subheader(f"Total: R$ {total_final:.2f}")
        if valor_brinde > 0: st.info(f"🎁 Desconto brinde aplicado: - R$ {valor_brinde:.2f}")
        
        nome = st.text_input("Seu Nome:")
        apto = st.text_input("Seu Apto / Bloco:")
        entrega = st.radio("Como prefere?", ["Entregar agora", "Buscar no 902", "Agendar"])
        
        if nome and apto:
            destinatario = NUMERO_YASMIN if eh_morador else NUMERO_JAQUE
            lista_itens = "\n".join(pedido)
            msg = f"🍦 *NOVO PEDIDO*\n📍 Local: {apto}\n👤 Nome: {nome}\n🕒 Hora: {entrega}\n\n*ITENS:*\n{lista_itens}\n\n💰 *Total: R$ {total_final:.2f}*"
            
            st.link_button("🚀 ENVIAR PEDIDO NO WHATSAPP", f"https://wa.me/{destinatario}?text={urllib.parse.quote(msg)}", type="primary")
