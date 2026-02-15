import streamlit as st
import urllib.parse
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Jaque é Doce!", page_icon="🐝", layout="centered")

# --- INICIALIZAÇÃO DE VARIÁVEIS DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'inicio'
if 'eh_morador' not in st.session_state:
    st.session_state.eh_morador = False

# --- DADOS ---
NUMERO_YASMIN = "5521981816105" 
NUMERO_JAQUE = "5521976141210" 
CHAVE_PIX = "30.615.725 000155" 

# --- TELA 1: INTERFACE DE BOAS-VINDAS ---
if st.session_state.pagina == 'inicio':
    st.markdown("<h1 style='text-align: center;'>Jaque é Doce! 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    st.image("https://i.imgur.com/vHqY7pT.png", use_container_width=True) # Você pode colocar o link da sua logo aqui
    st.markdown("### Bem-vindo(a) ao nosso cardápio digital!")
    st.write("Escolha uma das opções abaixo para continuar:")

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

# --- TELA 2: VALIDAÇÃO DE MORADOR ---
elif st.session_state.pagina == 'cupom_morador':
    st.subheader("🏠 Validação de Morador")
    cupom_validar = st.text_input("Insira o cupom do condomínio para liberar preços especiais:").strip().upper()
    
    col_v1, col_v2 = st.columns(2)
    if col_v1.button("Voltar"):
        st.session_state.pagina = 'inicio'
        st.rerun()
        
    if col_v2.button("Validar"):
        if cupom_validar in ["MACHADORIBEIRO", "GARAGEMLOLA"]:
            st.session_state.eh_morador = True
            st.session_state.pagina = 'cardapio'
            st.success("Acesso liberado!")
            st.rerun()
        else:
            st.error("Cupom inválido!")

# --- TELA 3: CARDÁPIO PRINCIPAL ---
elif st.session_state.pagina == 'cardapio':
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.pagina = 'inicio'
        st.rerun()

    # Preços Automáticos
    p_fruta = 5.00 if st.session_state.eh_morador else 8.00
    p_gourmet = 7.00 if st.session_state.eh_morador else 9.00
    p_frutopia = 7.00 if st.session_state.eh_morador else 9.00
    p_alcoolico = 9.00 if st.session_state.eh_morador else 10.00

    cardapio = {
        "❄️ Sacolés Fruta": [{"item": "Goiaba", "preco": p_fruta}, {"item": "Manga", "preco": p_fruta}],
        "🍫 Sacolés Gourmet": [{"item": "Ninho c/ Nutella", "preco": p_gourmet}, {"item": "Chicabon", "preco": p_gourmet}],
        "🔞 Alcoólicos": [{"item": "Piña Colada", "preco": p_alcoolico}],
        "🥧 Comidas": [{"item": "Empadão Frango (P)", "preco": 12.00}, {"item": "Crunch Cake (Pote)", "preco": 10.00}]
    }

    st.title("Jaque é Doce! 🐝")
    if st.session_state.eh_morador:
        st.success("✅ Preços exclusivos para moradores ativos!")

    pedido_atual = []
    total_bruto = 0.0

    for cat, itens in cardapio.items():
        st.subheader(cat)
        for p in itens:
            col_prod, col_qtd = st.columns([4, 1])
            qtd = col_qtd.number_input(f"Qtd", 0, 20, key=f"q_{p['item']}")
            col_prod.write(f"**{p['item']}** - R$ {p['preco']:.2f}")
            if qtd > 0:
                for _ in range(qtd):
                    pedido_atual.append({"Sabor": p['item'], "Preco": p['preco'], "Categoria": cat})
                total_bruto += (qtd * p['preco'])

    if total_bruto > 0:
        st.divider()
        nome = st.text_input("Seu Nome:")
        apto = st.text_input("Apartamento / Bloco:")
        entrega = st.radio("Opção de entrega:", ["Entregar agora", "Buscar no 902", "Agendar"])
        
        st.subheader(f"Total: R$ {total_bruto:.2f}")

        if nome and apto:
            destinatario = NUMERO_YASMIN if st.session_state.eh_morador else NUMERO_JAQUE
            msg = f"🍦 *NOVO PEDIDO*\n📍 *APTO:* {apto}\n👤 *NOME:* {nome}\n🕒 *HORA:* {entrega}\n"
            msg += "------------------\n"
            for sabor in set([x['Sabor'] for x in pedido_atual]):
                q = len([x for x in pedido_atual if x['Sabor'] == sabor])
                msg += f"✅ {q}x {sabor}\n"
            msg += f"------------------\n💰 *TOTAL: R$ {total_bruto:.2f}*"
            
            st.link_button("🚀 ENVIAR PEDIDO", f"https://wa.me/{destinatario}?text={urllib.parse.quote(msg)}")
