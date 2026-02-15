import streamlit as st
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ja Que é Doce!", page_icon="🐝", layout="centered")

# --- CONTROLE DE NAVEGAÇÃO ---
if 'foi_para_cardapio' not in st.session_state:
    st.session_state.foi_para_cardapio = False

# --- CONTATOS ---
NUMERO_YASMIN = "5521981816105" 
NUMERO_JAQUE = "5521976141210" 
CHAVE_PIX = "30.615.725 000155" 

# --- TELA 1: INTERFACE CONVIDATIVA (BOAS-VINDAS) ---
if not st.session_state.foi_para_cardapio:
    st.markdown("<h1 style='text-align: center; color: #E67E22;'>Jaque é Doce! 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # Aqui você pode colocar uma foto bem bonita da produção quando tiver
    st.markdown("<h3 style='text-align: center;'>Feitos com amor, para adoçar o seu dia. ❤️</h3>", unsafe_allow_html=True)
    
    st.write("")
    st.write("Olá, vizinho(a)! É um prazer ter você por aqui. Preparamos tudo de forma artesanal, com ingredientes selecionados e muito carinho.")
    st.write("Nossos sacolés, empadões e bolos estão te esperando.")
    st.write("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✨ VER CARDÁPIO COMPLETO", use_container_width=True):
            st.session_state.foi_para_cardapio = True
            st.rerun()
            
    st.markdown("<p style='text-align: center; font-size: 0.8em; color: gray;'>Atendimento das 10h às 20h</p>", unsafe_allow_html=True)

# --- TELA 2: CARDÁPIO DIRETÃO ---
else:
    if st.button("⬅️ Voltar"):
        st.session_state.foi_para_cardapio = False
        st.rerun()

    st.title("Cardápio do Dia 🍦")
    
    # Espaço para o cupom de morador (MACHADORIBEIRO)
    cupom = st.text_input("Possui um cupom de desconto?").strip().upper()
    
    eh_morador = (cupom == "MACHADORIBEIRO" or cupom == "GARAGEMLOLA")
    
    # Definição de Preços
    p_fruta = 5.00 if eh_morador else 8.00
    p_gourmet = 7.00 if eh_morador else 9.00
    p_frutopia = 7.00 if eh_morador else 9.00
    p_alcoolico = 9.00 if eh_morador else 10.00

    if eh_morador:
        st.success("🏠 Vizinho identificado! Preços especiais aplicados.")

    pedido = []
    total = 0.0

    # --- CATEGORIAS ---
    st.header("❄️ Sacolés")
    
    # Tropicais
    with st.expander("Sacolés de Fruta (Sem Lactose)", expanded=True):
        for s in ["Goiaba", "Manga", "Abacaxi com Hortelã", "Frutopia"]:
            pr = p_frutopia if s == "Frutopia" else p_fruta
            qtd = st.number_input(f"{s} - R$ {pr:.2f}", 0, 20, key=f"f_{s}")
            if qtd > 0:
                total += (qtd * pr)
                pedido.append(f"✅ {qtd}x {s}")

    # Gourmet
    with st.expander("Sacolés Gourmet (Cremosos)", expanded=True):
        for s in ["Ninho c/ Nutella", "Ninho c/ Morango", "Chicabon", "Pudim de Leite", "Coco Cremoso"]:
            qtd = st.number_input(f"{s} - R$ {p_gourmet:.2f}", 0, 20, key=f"g_{s}")
            if qtd > 0:
                total += (qtd * p_gourmet)
                pedido.append(f"✅ {qtd}x {s}")

    # Salgados e Bolos
    st.header("🥧 Salgados e Sobremesas")
    qtd_emp = st.number_input("Empadão Frango (P) - R$ 12.00", 0, 10, key="emp_p")
    qtd_bolo = st.number_input("Crunch Cake (Pote) - R$ 10.00", 0, 10, key="bolo")
    
    total += (qtd_emp * 12.00) + (qtd_bolo * 10.00)
    if qtd_emp > 0: pedido.append(f"✅ {qtd_emp}x Empadão P")
    if qtd_bolo > 0: pedido.append(f"✅ {qtd_bolo}x Bolo Pote")

    # --- FINALIZAÇÃO ---
    if total > 0:
        st.divider()
        st.subheader(f"Total: R$ {total:.2f}")
        nome = st.text_input("Seu Nome:")
        apto = st.text_input("Seu Apartamento:")
        entrega = st.radio("Como prefere?", ["Entregar agora", "Buscar no 902", "Agendar"])
        
        if nome and apto:
            destinatario = NUMERO_YASMIN if eh_morador else NUMERO_JAQUE
            lista_itens = "\n".join(pedido)
            msg = f"🍦 *PEDIDO*\n📍 Local: {apto}\n👤 Nome: {nome}\n🕒 Hora: {entrega}\n\n*ITENS:*\n{lista_itens}\n\n💰 *Total: R$ {total:.2f}*"
            
            link = f"https://wa.me/{destinatario}?text={urllib.parse.quote(msg)}"
            st.link_button("🚀 ENVIAR PEDIDO", link, type="primary")
