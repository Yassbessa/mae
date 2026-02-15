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
if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = None

# --- DADOS FIXOS ---
NUMERO_JAQUE = "5521976141210"
ENDERECO_RESTRITO = "RUA VINTE E QUATRO DE MAIO, 85"
CEPS_VALIDOS = ["20950-085", "20950-090"]

# ==========================================
# TELA 1: BOAS-VINDAS
# ==========================================
if st.session_state.etapa == "boas_vindas":
    st.markdown("<h1 style='text-align: center; color: #E67E22;'>Ja Que É Doce 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    col1, col2 = st.columns(2)
    if col1.button("🔑 JÁ SOU CLIENTE (LOGIN)", use_container_width=True):
        st.session_state.etapa = "login"
        st.rerun()
    if col2.button("✨ NOVO POR AQUI (CADASTRO)", use_container_width=True):
        st.session_state.etapa = "cadastro"
        st.rerun()

# ==========================================
# TELA 2: LOGIN COM SENHA
# ==========================================
elif st.session_state.etapa == "login":
    st.title("👤 Login")
    user_input = st.text_input("Nome cadastrado:")
    pass_input = st.text_input("Senha:", type="password")
    
    if st.button("ACESSAR 🚀"):
        try:
            df_users = conn.read(worksheet="Usuarios")
            # Busca o usuário na planilha
            user_data = df_users[(df_users['NOME'] == user_input) & (df_users['SENHA'] == pass_input)]
            
            if not user_data.empty:
                st.session_state.usuario_logado = user_data.iloc[0].to_dict()
                st.session_state.etapa = "cardapio"
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
        except:
            st.error("Erro ao conectar com a base de usuários.")
    
    if st.button("⬅️ Voltar"):
        st.session_state.etapa = "boas_vindas"
        st.rerun()

# ==========================================
# TELA 3: CADASTRO DE NOVO USUÁRIO
# ==========================================
elif st.session_state.etapa == "cadastro":
    st.title("📝 Novo Cadastro")
    novo_nome = st.text_input("Seu Nome Completo:")
    nova_senha = st.text_input("Crie uma Senha:", type="password")
    novo_nasc = st.date_input("Data de Nascimento:")
    novo_end = st.text_input("Endereço (Ex: Rua Vinte e Quatro de Maio, 85):")
    novo_cep = st.text_input("CEP (Ex: 20950-085):")
    novas_inst = st.text_area("Instruções (Ex: Deixar na portaria, Apto 902):")

    if st.button("FINALIZAR CADASTRO ✨"):
        if novo_nome and nova_senha and novo_cep:
            df_novo = pd.DataFrame([{
                "NOME": novo_nome, "SENHA": nova_senha, "NASCIMENTO": novo_nasc.strftime("%d/%m"),
                "ENDEREÇO": novo_end.upper(), "CEP": novo_cep, "INSTRUÇÕES": novas_inst
            }])
            conn.create(data=df_novo, worksheet="Usuarios")
            st.success("Cadastro realizado! Agora faça o Login.")
            st.session_state.etapa = "login"
            st.rerun()
        else:
            st.error("Preencha todos os campos obrigatórios!")

# ==========================================
# TELA 4: CARDÁPIO INTELIGENTE
# ==========================================
elif st.session_state.etapa == "cardapio":
    u = st.session_state.usuario_logado
    hoje = datetime.now().strftime("%d/%m")
    
    # Parabéns e Sugestões
    if u['NASCIMENTO'] == hoje:
        st.balloons()
        st.success(f"🎂 PARABÉNS! Use o cupom NIVERDOCE para ganhar um brinde!")

    st.title(f"Bem-vindo(a), {u['NOME']}! 🍦")
    st.info(f"📍 Entregaremos em: {u['ENDEREÇO']} ({u['CEP']})")

    # --- TRAVA DO CUPOM MACHADORIBEIRO ---
    cupom = st.text_input("Cupom de Desconto:").strip().upper()
    eh_morador = False
    
    if cupom == "MACHADORIBEIRO":
        if ENDERECO_RESTRITO in u['ENDEREÇO'] and u['CEP'] in CEPS_VALIDOS:
            st.success("Cupom morador aplicado! ✅")
            eh_morador = True
        else:
            st.error("Este cupom é exclusivo para moradores do endereço cadastrado.")
    
    # Lógica de Preços
    p_gourmet = 7.0 if eh_morador else 9.0
    total_bruto = 0.0
    pedido_itens = []

    # Seletor de Produtos (Exemplo)
    with st.expander("❄️ Sacolés Gourmet", expanded=True):
        qtd = st.number_input("Ninho c/ Nutella (R$ 7,00/9,00)", 0, 10)
        if qtd > 0:
            total_bruto += (qtd * p_gourmet)
            pedido_itens.append(f"{qtd}x Ninho c/ Nutella")

    # Finalização
    if total_bruto > 0:
        st.markdown(f"### Total: R$ {total_bruto:.2f}")
        if st.button("🚀 ENVIAR PEDIDO", type="primary"):
            # Salva na Vendas_Geral
            # ... (código de salvamento igual ao anterior)
            msg = f"🍦 *PEDIDO DE {u['NOME']}*\n📍 {u['ENDEREÇO']}\n📦 {', '.join(pedido_itens)}\n💰 Total: R$ {total_bruto:.2f}"
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'https://wa.me/{NUMERO_JAQUE}?text={urllib.parse.quote(msg)}\' /">', unsafe_allow_html=True)
