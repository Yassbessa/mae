import streamlit as st
import urllib.parse
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Jaque é Doce!", page_icon="🐝", layout="centered")

# --- NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'inicio'
if 'eh_morador' not in st.session_state:
    st.session_state.eh_morador = False

# --- CONTATOS ---
NUMERO_YASMIN = "5521981816105" 
NUMERO_JAQUE = "5521976141210" 
CHAVE_PIX = "30.615.725 000155" 

# --- TELA 1: INTERFACE DE BOAS-VINDAS ---
if st.session_state.pagina == 'inicio':
    st.markdown("<h1 style='text-align: center;'>Jaque é Doce! 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # IMAGEM DA LOGO OU CAPA
    st.image("https://images.unsplash.com/photo-1553177595-4de2bb0842b9?q=80&w=500", caption="Doces feitos com amor ❤️", use_container_width=True)
    
    st.markdown("### Bem-vindo(a) ao nosso cardápio digital!")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 SOU MORADOR", use_container_width=True):
            st.session_state.pagina = 'cupom_morador'
            st.rerun()
    with col2:
        if st.button("🍦 VISITANTE / GERAL", use_container_width=True):
            st.session_state.eh_morador = False
            st.session_state.pagina = 'cardapio'
            st.rerun()

# --- TELA 2: VALIDAÇÃO ---
elif st.session_state.pagina == 'cupom_morador':
    st.subheader("🏠 Validação de Morador")
    cupom_validar = st.text_input("Insira o cupom do condomínio:").strip().upper()
    if st.button("Validar"):
        if cupom_validar in ["MACHADORIBEIRO", "GARAGEMLOLA"]:
            st.session_state.eh_morador = True
            st.session_state.pagina = 'cardapio'
            st.rerun()
        else:
            st.error("Cupom inválido!")

# --- TELA 3: CARDÁPIO ---
elif st.session_state.pagina == 'cardapio':
    p_fruta = 5.00 if st.session_state.eh_morador else 8.00
    p_gourmet = 7.00 if st.session_state.eh_morador else 9.00

    st.title("Cardápio Jaque é Doce! 🐝")
    
    # --- CATEGORIA: SACOLÉS FRUTA ---
    st.header("❄️ Sacolés de Fruta")
    st.image("https://images.unsplash.com/photo-1505394033343-431693360211?q=80&w=500", caption="Refrescantes e naturais")
    
    col1, col2 = st.columns(2)
    with col1:
        qtd_goiaba = st.number_input(f"Goiaba - R$ {p_fruta:.2f}", 0, 10, key="goiaba")
    with col2:
        qtd_manga = st.number_input(f"Manga - R$ {p_fruta:.2f}", 0, 10, key="manga")

    # --- CATEGORIA: GOURMET ---
    st.header("🍫 Sacolés Gourmet")
    st.image("https://images.unsplash.com/photo-1481391243133-f96216d51df7?q=80&w=500", caption="Cremosidade incomparável")
    
    col3, col4 = st.columns(2)
    with col3:
        qtd_ninho = st.number_input(f"Ninho c/ Nutella - R$ {p_gourmet:.2f}", 0, 10, key="ninho")
    with col4:
        qtd_chica = st.number_input(f"Chicabon - R$ {p_gourmet:.2f}", 0, 10, key="chica")

    # --- CÁLCULO E FINALIZAÇÃO ---
    total = (qtd_goiaba + qtd_manga) * p_fruta + (qtd_ninho + qtd_chica) * p_gourmet
    
    if total > 0:
        st.divider()
        nome = st.text_input("Seu Nome:")
        apto = st.text_input("Seu Apartamento:")
        
        if st.button("🚀 ENVIAR PEDIDO"):
            destinatario = NUMERO_YASMIN if st.session_state.eh_morador else NUMERO_JAQUE
            msg = f"🍦 *PEDIDO*\n📍 Apto: {apto}\n👤 Nome: {nome}\n💰 Total: R$ {total:.2f}"
            st.write(f"Link gerado para: {'Yasmin' if st.session_state.eh_morador else 'Jaque'}")
            st.markdown(f"[Clique aqui para confirmar no WhatsApp](https://wa.me/{destinatario}?text={urllib.parse.quote(msg)})")
