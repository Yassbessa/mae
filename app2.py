import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Ja Que É Doce - Gestão", page_icon="🐝", layout="wide")

# --- LOGIN ADMIN ---
ADMIN_USER = "admin"
ADMIN_PASS = "jqd9191"

# --- FUNÇÕES DE BANCO DE DADOS LOCAL (SEM SHEETS!) ---
def carregar_dados(arquivo, colunas):
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo)
    return pd.DataFrame(columns=colunas)

def salvar_dados(df, arquivo):
    df.to_csv(arquivo, index=False)

# Inicializando arquivos
ARQUIVO_VENDAS = "historico_vendas.csv"
ARQUIVO_CLIENTES = "base_clientes.csv"

# --- MEMÓRIA DA SESSÃO ---
if 'etapa' not in st.session_state: st.session_state.etapa = "boas_vindas"
if 'usuario' not in st.session_state: st.session_state.user = None

# ==========================================
# TELA 1: BOAS-VINDAS
# ==========================================
if st.session_state.etapa == "boas_vindas":
    st.markdown("<h1 style='text-align: center;'>Ja Que É Doce 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    c1, c2 = st.columns(2)
    if c1.button("🛍️ FAZER PEDIDO", use_container_width=True):
        st.session_state.etapa = "cadastro"; st.rerun()
    if c2.button("👑 PAINEL ADMIN", use_container_width=True):
        st.session_state.etapa = "login_admin"; st.rerun()

# ==========================================
# TELA 2: LOGIN ADMIN
# ==========================================
elif st.session_state.etapa == "login_admin":
    st.title("🔑 Acesso Administrativo")
    u = st.text_input("Usuário:")
    p = st.text_input("Senha:", type="password")
    if st.button("ENTRAR 🚀"):
        if u == ADMIN_USER and p == SENHA_ADMIN: # Use jqd9191
            st.session_state.etapa = "painel_admin"; st.rerun()
        else: st.error("Incorreto!")
    if st.button("⬅️ Voltar"): st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 3: CADASTRO DO CLIENTE
# ==========================================
elif st.session_state.etapa == "cadastro":
    st.title("📝 Seus Dados")
    with st.form("cad"):
        nome = st.text_input("Nome:")
        end = st.text_input("Endereço/Apto:")
        bairro = st.text_input("Bairro:")
        if st.form_submit_button("IR PARA O CARDÁPIO"):
            if nome and end:
                # Salva o cliente na base histórica
                df_c = carregar_dados(ARQUIVO_CLIENTES, ["Nome", "Endereço", "Bairro"])
                if nome not in df_c['Nome'].values:
                    nova_linha = pd.DataFrame([{"Nome": nome, "Endereço": end, "Bairro": bairro}])
                    df_c = pd.concat([df_c, nova_linha], ignore_index=True)
                    salvar_dados(df_c, ARQUIVO_CLIENTES)
                
                st.session_state.user = {"nome": nome, "end": end, "bairro": bairro}
                st.session_state.etapa = "cardapio"; st.rerun()
            else: st.error("Preencha tudo!")

# ==========================================
# TELA 4: CARDÁPIO E PEDIDO
# ==========================================
elif st.session_state.etapa == "cardapio":
    u = st.session_state.user
    st.title(f"Olá, {u['nome']}!")
    
    sabores = {
        "Ninho c/ Nutella": 9.0,
        "Morango c/ Leite Moça": 8.0,
        "Paçoca": 7.5
    }
    
    pedido = {}
    for s, p in sabores.items():
        qtd = st.number_input(f"{s} (R$ {p:.2f})", 0, 10, key=s)
        if qtd > 0: pedido[s] = qtd

    if pedido:
        total = sum(sabores[s] * q for s, q in pedido.items())
        st.markdown(f"### Total: R$ {total:.2f}")
        
        if st.button("✅ FINALIZAR"):
            # GRAVA A VENDA NO BANCO DE DADOS INTERNO
            df_v = carregar_dados(ARQUIVO_VENDAS, ["Data", "Cliente", "Endereço", "Sabor", "Qtd", "Total"])
            for s, q in pedido.items():
                nova_venda = pd.DataFrame([{
                    "Data": datetime.now().strftime("%d/%m/%Y"),
                    "Cliente": u['nome'],
                    "Endereço": u['end'],
                    "Sabor": s,
                    "Qtd": q,
                    "Total": q * sabores[s]
                }])
                df_v = pd.concat([df_v, nova_venda], ignore_index=True)
            salvar_dados(df_v, ARQUIVO_VENDAS)
            
            # Zap
            msg = f"🍦 *NOVO PEDIDO*\n👤 {u['nome']}\n📦 {pedido}\n💰 Total: R$ {total:.2f}"
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'https://wa.me/5521976141210?text={urllib.parse.quote(msg)}\' /">', unsafe_allow_html=True)

# ==========================================
# TELA 5: PAINEL ADMIN (INTELIGÊNCIA)
# ==========================================
elif st.session_state.etapa == "painel_admin":
    st.title("👑 Painel de Inteligência Ja Que É Doce")
    if st.button("⬅️ SAIR"): st.session_state.etapa = "boas_vindas"; st.rerun()
    
    df_v = carregar_dados(ARQUIVO_VENDAS, [])
    
    if not df_v.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Sabores Mais Vendidos")
            ranking = df_v.groupby("Sabor")["Qtd"].sum().sort_values(ascending=False)
            st.bar_chart(ranking)
            
        with col2:
            st.subheader("📍 Onde pedem mais?")
            locais = df_v.groupby("Endereço")["Total"].sum().sort_values(ascending=False)
            st.table(locais)

        st.subheader("📋 Histórico Completo")
        st.dataframe(df_v, use_container_width=True)
    else:
        st.info("Aguardando as primeiras vendas!")
