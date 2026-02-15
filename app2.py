import streamlit as st
import urllib.parse
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import date, datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")
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
    if c1.button("🔑 LOGIN", use_container_width=True):
        st.session_state.etapa = "login"; st.rerun()
    if c2.button("✨ CADASTRO", use_container_width=True):
        st.session_state.etapa = "cadastro"; st.rerun()

# ==========================================
# TELA 2: LOGIN
# ==========================================
elif st.session_state.etapa == "login":
    st.title("👤 Identificação")
    u_log = st.text_input("Nome:")
    p_log = st.text_input("Senha:", type="password")
    if st.button("ACESSAR 🚀"):
        try:
            df_u = conn.read(worksheet="Usuarios")
            match = df_u[(df_u['NOME'] == u_log) & (df_u['SENHA'] == str(p_log))]
            if not match.empty:
                st.session_state.user = match.iloc[0].to_dict()
                st.session_state.etapa = "cardapio"; st.rerun()
            else:
                st.error("Nome ou Senha incorretos.")
        except: st.error("Erro ao conectar com a base de dados.")
    if st.button("⬅️ Voltar"): st.session_state.etapa = "boas_vindas"; st.rerun()

# ==========================================
# TELA 3: CADASTRO (COM BAIRRO E DATA 1930)
# ==========================================
elif st.session_state.etapa == "cadastro":
    st.title("📝 Cadastro de Cliente")
    n_nome = st.text_input("Nome Completo:")
    n_pass = st.text_input("Crie uma Senha:", type="password")
    # Data de nascimento desde 1930 como solicitado
    n_nasc = st.date_input("Nascimento:", min_value=date(1930, 1, 1), value=date(2000, 1, 1))
    n_end = st.text_input("Endereço:")
    n_bairro = st.text_input("Bairro:") # NOVO CAMPO
    n_cep = st.text_input("CEP:")
    n_inst = st.text_area("Instruções (Ex: Apto 201 ou Portaria):")

    if st.button("FINALIZAR CADASTRO ✨"):
        if n_nome and n_pass and n_cep and n_bairro:
            try:
                # Evita erro de UnsupportedOperationError
                df_old = conn.read(worksheet="Usuarios")
                df_new = pd.DataFrame([{
                    "NOME": n_nome, "SENHA": n_pass, "NASCIMENTO": n_nasc.strftime("%d/%m"),
                    "ENDEREÇO": n_end.upper(), "BAIRRO": n_bairro.upper(), "CEP": n_cep, "INSTRUÇÕES": n_inst
                }])
                df_total = pd.concat([df_old, df_new], ignore_index=True)
                conn.update(worksheet="Usuarios", data=df_total)
                st.success("Cadastrado! Faça o Login.")
                st.session_state.etapa = "login"; st.rerun()
            except: st.error("Erro ao salvar. Verifique a aba 'Usuarios'.")
        else: st.error("Preencha todos os campos!")

# ==========================================
# TELA 4: CARDÁPIO INTELIGENTE
# ==========================================
elif st.session_state.etapa == "cardapio":
    u = st.session_state.user
    hoje = date.today().strftime("%d/%m")
    
    if u['NASCIMENTO'] == hoje:
        st.balloons(); st.success(f"🎂 Parabéns, {u['NOME']}! Use o cupom NIVERDOCE!")

    st.title(f"Olá, {u['NOME']}!")
    st.info(f"📍 Entrega: {u['ENDEREÇO']}, {u['BAIRRO']}")

    # --- TRAVA DO CUPOM ---
    cupom = st.text_input("Cupom:").strip().upper()
    eh_morador = False
    if cupom == "MACHADORIBEIRO":
        end_u = str(u['ENDEREÇO']).upper()
        cep_u = str(u['CEP']).replace("-", "")
        # Validação robusta de endereço e CEP
        valido = any(rua in end_u for rua in ENDERECO_RESTRITO) and NUMERO_RESTRITO in end_u and cep_u in [c.replace("-","") for c in CEPS_RESTRITOS]
        if valido:
            st.success("Desconto morador aplicado! ✅")
            eh_morador = True
        else: st.error("Cupom exclusivo para moradores da Rua 24 de Maio, 85.")

    p_gourmet = 7.0 if eh_morador else 9.0
    total = 0.0
    pedidos_zap = []
    dados_venda = []

    # Exemplo de seletor
    st.header("❄️ Sacolés")
    qtd = st.number_input("Ninho c/ Nutella", 0, 10)
    if qtd > 0:
        total += (qtd * p_gourmet)
        pedidos_zap.append(f"✅ {qtd}x Ninho c/ Nutella")
        dados_venda.append({"ITEM": "Ninho c/ Nutella", "QNTD": qtd, "PREÇO": p_gourmet})

    if total > 0:
        st.markdown(f"### Total: R$ {total:.2f}")
        if st.button("🚀 ENVIAR PEDIDO", type="primary"):
            dt = datetime.now().strftime("%d/%m/%Y %H:%M")
            # Salva na Tabela Mestra incluindo o BAIRRO
            df_v = pd.DataFrame([{
                "DATA": dt, "NOME": u['NOME'], "APT/END": u['ENDEREÇO'], "BAIRRO": u['BAIRRO'],
                "NASCIMENTO": u['NASCIMENTO'], "ITEM": d['ITEM'], "QNTD": d['QNTD'], 
                "PREÇO": d['PREÇO'], "TOTAL": total, "PGTO": "PIX", "ENTREGA": u['INSTRUÇÕES']
            } for d in dados_venda])
            conn.create(data=df_v, worksheet="Vendas_Geral") # Tenta salvar na mestra
            
            msg = f"🍦 *PEDIDO DE {u['NOME']}*\n📍 {u['ENDEREÇO']}, {u['BAIRRO']}\n📦 {', '.join(pedidos_zap)}\n💰 Total: R$ {total:.2f}"
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'https://wa.me/5521976141210?text={urllib.parse.quote(msg)}\' /">', unsafe_allow_html=True)
