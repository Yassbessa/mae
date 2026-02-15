import streamlit as st
import urllib.parse
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import date, datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")
# Conexão que busca o link direto nas Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- REGRAS DE SEGURANÇA (ENDEREÇO) ---
ENDERECO_RESTRITO = ["24 DE MAIO", "VINTE E QUATRO DE MAIO"]
NUMERO_RESTRITO = "85"
CEPS_RESTRITOS = ["20950-085", "20950-090", "20950085", "20950090"]

# --- MEMÓRIA DO APP ---
if 'etapa' not in st.session_state:
    st.session_state.etapa = "boas_vindas"
if 'user' not in st.session_state:
    st.session_state.user = None

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
# TELA 2: LOGIN COM SENHA
# ==========================================
elif st.session_state.etapa == "login":
    st.title("👤 Identificação")
    u_log = st.text_input("Nome cadastrado:")
    p_log = st.text_input("Senha:", type="password")
    
    if st.button("ACESSAR 🚀"):
        try:
            # Lendo a aba de usuários cadastrados
            df_u = conn.read(worksheet="Usuarios")
            match = df_u[(df_u['NOME'] == u_log) & (df_u['SENHA'] == str(p_log))]
            
            if not match.empty:
                st.session_state.user = match.iloc[0].to_dict()
                st.session_state.etapa = "cardapio"; st.rerun()
            else:
                st.error("Nome ou Senha incorretos.")
        except Exception as e:
            st.error(f"Erro ao conectar: {e}. Verifique as Secrets.")

    if st.button("⬅️ Voltar"): st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 3: CADASTRO (COM BAIRRO E DATA 1930)
# ==========================================
elif st.session_state.etapa == "cadastro":
    st.title("📝 Cadastro de Cliente")
    n_nome = st.text_input("Nome Completo:")
    n_pass = st.text_input("Crie uma Senha:", type="password")
    # Data de nascimento desde 1930 para os clientes mais velhos
    n_nasc = st.date_input("Nascimento:", min_value=date(1930, 1, 1), value=date(2000, 1, 1))
    n_end = st.text_input("Endereço (Ex: Rua 24 de Maio, 85):")
    n_bairro = st.text_input("Bairro:") 
    n_cep = st.text_input("CEP:")
    n_inst = st.text_area("Instruções de Entrega (Ex: Apto 902):")

    if st.button("FINALIZAR CADASTRO ✨"):
        if n_nome and n_pass and n_cep and n_bairro:
            try:
                # RESOLVENDO O ERRO DE GRAVAÇÃO (UnsupportedOperation)
                df_old = conn.read(worksheet="Usuarios")
                df_new = pd.DataFrame([{
                    "NOME": n_nome, "SENHA": str(n_pass), "NASCIMENTO": n_nasc.strftime("%d/%m"),
                    "ENDEREÇO": n_end.upper(), "BAIRRO": n_bairro.upper(), "CEP": n_cep, "INSTRUÇÕES": n_inst
                }])
                df_total = pd.concat([df_old, df_new], ignore_index=True)
                conn.update(worksheet="Usuarios", data=df_total)
                st.success("Cadastro realizado! Faça o Login.")
                st.session_state.etapa = "login"; st.rerun()
            except: st.error("Erro ao salvar. Verifique se a aba 'Usuarios' existe na planilha.")
        else: st.error("Preencha todos os campos!")

# ==========================================
# TELA 4: CARDÁPIO INTELIGENTE
# ==========================================
elif st.session_state.etapa == "cardapio":
    u = st.session_state.user
    st.title(f"Olá, {u['NOME']}! 🍦")
    
    # 🎂 Balões no dia do aniversário
    if u['NASCIMENTO'] == date.today().strftime("%d/%m"):
        st.balloons(); st.success("🎉 Parabéns! Hoje você tem brinde especial!")

    # --- SUGESTÕES BASEADAS NO HISTÓRICO ---
    try:
        df_hist = conn.read(worksheet="Vendas_Geral")
        # Filtra compras passadas desse usuário
        meus_fav = df_hist[df_hist['NOME'] == u['NOME']]['ITEM'].value_counts().head(2).index.tolist()
        if meus_fav:
            st.info(f"⭐ **Sugestão para você:** Notamos que você adora {', '.join(meus_fav)}!")
    except: pass

    # --- TRAVA DO DESCONTO MORADOR ---
    cupom = st.text_input("Cupom:").strip().upper()
    eh_morador = False
    if cupom == "MACHADORIBEIRO":
        end_u = str(u['ENDEREÇO']).upper()
        # Aceita "24 de Maio" ou "Vinte e Quatro de Maio"
        valido = any(rua in end_u for rua in ENDERECO_RESTRITO) and NUMERO_RESTRITO in end_u
        if valido and u['CEP'].replace("-","") in [c.replace("-","") for c in CEPS_RESTRITOS]:
            st.success("Desconto morador ativado! ✅")
            eh_morador = True
        else: st.error("Cupom exclusivo para moradores da Rua 24 de Maio, 85.")

    # (Lógica de pedidos e total aqui...)
    total = 0.0 # Exemplo simplificado
    if st.button("🚀 FINALIZAR PEDIDO NO WHATSAPP"):
        # Salva na Vendas_Geral incluindo BAIRRO
        st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'https://wa.me/5521976141210?text=Oi\' /">', unsafe_allow_html=True)
