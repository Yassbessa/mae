import streamlit as st
import urllib.parse
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- MEMÓRIA DO APP ---
if 'etapa' not in st.session_state:
    st.session_state.etapa = "boas_vindas"
if 'dados_cliente' not in st.session_state:
    st.session_state.dados_cliente = {}

# --- DADOS FIXOS ---
NUMERO_JAQUE = "5521976141210" 

# ==========================================
# TELA 1: BOAS-VINDAS
# ==========================================
if st.session_state.etapa == "boas_vindas":
    st.markdown("<h1 style='text-align: center; color: #E67E22;'>Ja Que É Doce 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    if st.button("✨ ENTRAR E VER CARDÁPIO", use_container_width=True):
        st.session_state.etapa = "identificacao"
        st.rerun()

# ==========================================
# TELA 2: IDENTIFICAÇÃO (LOGIN)
# ==========================================
elif st.session_state.etapa == "identificacao":
    st.title("👤 Identificação")
    nome = st.text_input("Seu Nome:")
    apto = st.text_input("Apartamento / Bloco:")
    # Data de nascimento ligada no início como solicitado
    nasc = st.date_input("Sua Data de Nascimento:", help="Para brindes exclusivos!")

    if st.button("ACESSAR 🚀"):
        if nome and apto:
            st.session_state.dados_cliente = {
                "nome": nome, "apto": apto,
                "nascimento": nasc.strftime("%d/%m")
            }
            st.session_state.etapa = "cardapio"
            st.rerun()
        else:
            st.error("Preencha Nome e Apartamento!")

# ==========================================
# TELA 3: CARDÁPIO INTELIGENTE
# ==========================================
elif st.session_state.etapa == "cardapio":
    cliente = st.session_state.dados_cliente
    hoje = datetime.now().strftime("%d/%m")
    
    # --- VERIFICAÇÃO DE ANIVERSÁRIO ---
    if cliente['nascimento'] == hoje:
        st.balloons()
        st.success(f"🎂 PARABÉNS, {cliente['nome'].upper()}! Hoje o brinde é por nossa conta. Use o cupom: **NIVERDOCE**")

    st.title(f"Olá, {cliente['nome']}! 🍦")
    
    # --- BUSCAR HISTÓRICO (SUGESTÕES) ---
    try:
        # Lê a planilha mestra
        df_historico = conn.read(worksheet="Vendas_Geral")
        # Filtra pelo apartamento do cliente
        meus_pedidos = df_historico[df_historico['APT/END'] == cliente['apto']]
        
        if not meus_pedidos.empty:
            st.subheader("⭐ Sugestões para você")
            # Encontra os 3 itens mais pedidos por ele
            mais_pedidos = meus_pedidos['ITEM'].value_counts().head(3).index.tolist()
            st.write(f"Vimos que você adora: **{', '.join(mais_pedidos)}**. Que tal pedir de novo?")
    except:
        pass # Se a planilha estiver vazia, ignora as sugestões

    # --- BLOCO DE INSTRUÇÕES ---
    st.info("🥧 **Dica do Empadão:** 40 min a 200°C para ficar bem crocante!")

    # --- CARDÁPIO FIXO ---
    cupons = st.text_input("Aplicar Cupom:").strip().upper()
    eh_morador = cupons in ["MACHADORIBEIRO", "GARAGEMLOLA"]
    p_gourmet = 7.0 if eh_morador else 9.0

    total_bruto = 0.0
    pedido_final = []
    dados_venda = []

    st.header("❄️ Sacolés")
    sabores = [("Ninho c/ Nutella", p_gourmet, 5), ("Chicabon", p_gourmet, 4)]
    
    for item, preco, est in sabores:
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.write(f"**{item}** - R$ {preco:.2f}")
        c2.write(f"Est: {est}")
        qtd = c3.number_input("Qtd", 0, est, key=f"q_{item}", label_visibility="collapsed")
        if qtd > 0:
            total_bruto += (qtd * preco)
            pedido_final.append(f"✅ {qtd}x {item}")
            dados_venda.append({"ITEM": item, "QNTD": qtd, "PREÇO": preco})

    # --- FINALIZAÇÃO ---
    if total_bruto > 0:
        st.markdown(f"### Total: R$ {total_bruto:.2f}")
        pagto = st.radio("Pagamento:", ["PIX", "Dinheiro"])
        
        if st.button("🚀 FINALIZAR E SALVAR", type="primary"):
            data_h = datetime.now().strftime("%d/%m/%Y %H:%M")
            # Salva na Tabela Mestra
            df_save = pd.DataFrame([{
                "DATA": data_h, "NOME": cliente['nome'], "APT/END": cliente['apto'],
                "NASCIMENTO": cliente['nascimento'], "ITEM": d['ITEM'], "QNTD": d['QNTD'], 
                "PREÇO": d['PREÇO'], "TOTAL": total_bruto, "PGTO": pagto, "ENTREGA": "Padrão"
            } for d in dados_venda])
            
            conn.create(data=df_save, worksheet="Vendas_Geral")
            
            msg = f"🍦 *PEDIDO*\n👤 {cliente['nome']}\n📍 {cliente['apto']}\n📦 {', '.join(pedido_final)}\n💰 Total: R$ {total_bruto:.2f}"
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'https://wa.me/{NUMERO_JAQUE}?text={urllib.parse.quote(msg)}\' /">', unsafe_allow_html=True)
