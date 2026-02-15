import streamlit as st
import pandas as pd
import requests
import urllib.parse
from datetime import date, datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")
URL_WEB_APP = "https://script.google.com/macros/s/AKfycbyByTKemIrdGk7y6HnHAGC-d8Vgxu_WoeVAdsBh8mLcR44-XQbSKY3E827lFT49i1YhBA/exec"

# --- MEMÓRIA DO APP ---
if 'etapa' not in st.session_state: st.session_state.etapa = "boas_vindas"
if 'user' not in st.session_state: st.session_state.user = None

def salvar_dados(lista, aba):
    requests.post(f"{URL_WEB_APP}?aba={aba}", json=lista)

def ler_dados(aba):
    try:
        response = requests.get(f"{URL_WEB_APP}?aba={aba}")
        data = response.json()
        return pd.DataFrame(data[1:], columns=data[0])
    except: return pd.DataFrame()

# ==========================================
# TELA 1: BOAS-VINDAS
# ==========================================
if st.session_state.etapa == "boas_vindas":
    st.markdown("<h1 style='text-align: center; color: #E67E22;'>Ja Que É Doce 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    c1, c2 = st.columns(2)
    if c1.button("🔑 ENTRAR (LOGIN)", use_container_width=True):
        st.session_state.etapa = "login"; st.rerun()
    if c2.button("✨ CADASTRAR", use_container_width=True):
        st.session_state.etapa = "cadastro"; st.rerun()

# ==========================================
# TELA 2: LOGIN (AGORA POR E-MAIL)
# ==========================================
elif st.session_state.etapa == "login":
    st.title("👤 Login")
    email_log = st.text_input("E-mail cadastrado:").strip().lower()
    p_log = st.text_input("Senha:", type="password")
    
    col_l1, col_l2 = st.columns(2)
    if col_l1.button("ACESSAR 🚀", type="primary"):
        df_u = ler_dados("Usuarios")
        if not df_u.empty:
            # Busca pelo E-MAIL agora
            match = df_u[(df_u['EMAIL'] == email_log) & (df_u['SENHA'].astype(str) == str(p_log))]
            if not match.empty:
                st.session_state.user = match.iloc[0].to_dict()
                st.session_state.etapa = "cardapio"; st.rerun()
            else: st.error("E-mail ou Senha incorretos.")
    
    if col_l2.button("⬅️ Voltar"):
        st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 3: CADASTRO (COM E-MAIL E VOLTAR)
# ==========================================
elif st.session_state.etapa == "cadastro":
    if st.button("⬅️ Cancelar e Voltar"):
        st.session_state.etapa = "boas_vindas"; st.rerun()
        
    st.title("📝 Cadastro de Cliente")
    with st.form("form_cad"):
        n_nome = st.text_input("Nome Completo:")
        n_email = st.text_input("Seu melhor E-mail (será seu login):").strip().lower() # Novo identificador
        n_pass = st.text_input("Crie uma Senha:", type="password")
        n_nasc = st.date_input("Nascimento:", min_value=date(1930, 1, 1), value=date(2000, 1, 1))
        n_end = st.text_input("Endereço:")
        n_bairro = st.text_input("Bairro:")
        n_cep = st.text_input("CEP:")
        n_inst = st.text_area("Instruções de Entrega:")
        
        submit = st.form_submit_button("FINALIZAR CADASTRO ✨")

    if submit:
        if n_nome and n_email and n_pass and n_end:
            # Salva na ordem da nova coluna EMAIL
            dados = [n_nome, n_email, str(n_pass), n_nasc.strftime("%d/%m"), n_end.upper(), n_bairro.upper(), n_cep, n_inst]
            salvar_dados(dados, "Usuarios")
            st.success("Cadastro realizado com sucesso! Redirecionando...")
            st.session_state.etapa = "login"
            st.rerun() # Passagem direta para o login
        else: st.error("Preencha todos os campos obrigatórios!")

# ==========================================
# TELA 4: CARDÁPIO (SÓ ENTRA COM LOGIN)
# ==========================================
elif st.session_state.etapa == "cardapio":
    u = st.session_state.user
    st.title(f"Olá, {u['NOME']}! 🍦")
    
    if st.button("⬅️ Sair (Logout)"):
        st.session_state.user = None
        st.session_state.etapa = "boas_vindas"; st.rerun()

    # Trava do Cupom morador
    cupom = st.text_input("Possui Cupom?").strip().upper()
    eh_morador = False
    if cupom == "MACHADORIBEIRO":
        end_u = str(u['ENDEREÇO']).upper()
        if ("24 DE MAIO" in end_u or "VINTE E QUATRO DE MAIO" in end_u) and "85" in end_u:
            st.success("Desconto morador ativado! ✅"); eh_morador = True
        else: st.error("Cupom restrito a moradores da Rua 24 de Maio, 85.")

    # (Exemplo de compra rápida)
    p_gourmet = 7.0 if eh_morador else 9.0
    qtd = st.number_input(f"Ninho c/ Nutella (R$ {p_gourmet:.2f})", 0, 10)
    
    if qtd > 0:
        if st.button("🚀 FINALIZAR"):
            dt = datetime.now().strftime("%d/%m/%Y %H:%M")
            # Salva na Vendas_Geral
            venda = [dt, u['NOME'], u['ENDEREÇO'], u['NASCIMENTO'], "Ninho c/ Nutella", qtd, p_gourmet, qtd*p_gourmet, "PIX", u['INSTRUÇÕES']]
            salvar_dados(venda, "Vendas_Geral")
            st.success("Pedido gravado! Enviando para o WhatsApp...")
