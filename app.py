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
    
    # Foto da Capa (Pode trocar pelo link da sua logo)
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
    if st.button("Voltar"):
        st.session_state.pagina = 'inicio'
        st.rerun()

# --- TELA 3: CARDÁPIO COMPLETO ---
elif st.session_state.pagina == 'cardapio':
    if st.button("⬅️ Voltar"):
        st.session_state.pagina = 'inicio'
        st.rerun()

    # Preços Automáticos
    p_fruta = 5.00 if st.session_state.eh_morador else 8.00
    p_gourmet = 7.00 if st.session_state.eh_morador else 9.00
    p_alcoolico = 9.00 if st.session_state.eh_morador else 10.00

    st.title("Cardápio Jaque é Doce! 🐝")
    if st.session_state.eh_morador:
        st.success("✅ Preços de Morador Ativos")

    pedido = []
    total = 0.0

    # --- CATEGORIA: SACOLÉS FRUTA ---
    st.header("❄️ Sacolés de Fruta")
    st.image("https://images.unsplash.com/photo-1505394033343-431693360211?q=80&w=500")
    itens_fruta = ["Goiaba", "Manga", "Abacaxi com Hortelã", "Frutopia"]
    for item in itens_fruta:
        qtd = st.number_input(f"{item} - R$ {p_fruta:.2f}", 0, 10, key=f"fruta_{item}")
        if qtd > 0:
            total += (qtd * p_fruta)
            pedido.append(f"✅ {qtd}x {item}")

    # --- CATEGORIA: GOURMET ---
    st.header("🍫 Sacolés Gourmet")
    st.image("https://images.unsplash.com/photo-1481391243133-f96216d51df7?q=80&w=500")
    itens_gourmet = ["Ninho c/ Nutella", "Ninho c/ Morango", "Chicabon", "Mousse de Maracujá", "Pudim de Leite", "Açaí Cremoso", "Coco Cremoso"]
    for item in itens_gourmet:
        qtd = st.number_input(f"{item} - R$ {p_gourmet:.2f}", 0, 10, key=f"gourmet_{item}")
        if qtd > 0:
            total += (qtd * p_gourmet)
            pedido.append(f"✅ {qtd}x {item}")

    # --- CATEGORIA: ALCOÓLICOS ---
    st.header("🔞 Alcoólicos (+18)")
    st.image("https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?q=80&w=500")
    itens_alc = ["Piña Colada", "Caipirinha", "Batida de Maracujá", "Batida de Morango"]
    for item in itens_alc:
        qtd = st.number_input(f"{item} - R$ {p_alcoolico:.2f}", 0, 10, key=f"alc_{item}")
        if qtd > 0:
            total += (qtd * p_alcoolico)
            pedido.append(f"✅ {qtd}x {item}")

    # --- CATEGORIA: EMPADÃO ---
    st.header("🥧 Empadão Cremoso")
    st.image("https://images.unsplash.com/photo-1626078436898-90098d5be326?q=80&w=500")
    qtd_emp_p = st.number_input("Empadão Frango (P) - R$ 12.00", 0, 10, key="emp_p")
    qtd_emp_g = st.number_input("Empadão Frango (G) - R$ 18.00", 0, 10, key="emp_g")
    total += (qtd_emp_p * 12.00) + (qtd_emp_g * 18.00)
    if qtd_emp_p > 0: pedido.append(f"✅ {qtd_emp_p}x Empadão P")
    if qtd_emp_g > 0: pedido.append(f"✅ {qtd_emp_g}x Empadão G")

    # --- CATEGORIA: BOLO ---
    st.header("🍰 Sobremesas")
    st.image("https://images.unsplash.com/photo-1587132137056-bfbf0166836e?q=80&w=500")
    qtd_bolo = st.number_input("Crunch Cake (Pote) - R$ 10.00", 0, 10, key="bolo")
    total += (qtd_bolo * 10.00)
    if qtd_bolo > 0: pedido.append(f"✅ {qtd_bolo}x Bolo Pote")

    # --- FINALIZAÇÃO ---
    if total > 0:
        st.divider()
        nome = st.text_input("Seu Nome:")
        apto = st.text_input("Seu Apartamento:")
        entrega = st.radio("Como prefere?", ["Entregar agora", "Buscar no 902", "Agendar"])
        
        st.subheader(f"Total: R$ {total:.2f}")

        if nome and apto:
            destinatario = NUMERO_YASMIN if st.session_state.eh_morador else NUMERO_JAQUE
            lista_itens = "\n".join(pedido)
            msg = f"🍦 *PEDIDO PARA {'YASMIN' if st.session_state.eh_morador else 'JAQUE'}*\n📍 Local: {apto}\n👤 Nome: {nome}\n🕒 Hora: {entrega}\n\n*ITENS:*\n{lista_itens}\n\n💰 *Total: R$ {total:.2f}*"
            
            link = f"https://wa.me/{destinatario}?text={urllib.parse.quote(msg)}"
            st.link_button("🚀 FINALIZAR NO WHATSAPP", link, type="primary")
