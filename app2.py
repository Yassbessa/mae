import streamlit as st
import urllib.parse
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")

# --- CONEXÃO COM GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- DADOS DO NEGÓCIO ---
NUMERO_YASMIN = "5521981816105" 
NUMERO_JAQUE = "5521976141210" 
CHAVE_PIX = "30.615.725 000155" 
EMAIL_COMPROVANTE = "jaqueedoce@gmail.com"

if 'abriu_cardapio' not in st.session_state:
    st.session_state.abriu_cardapio = False

# --- TELA 1: BOAS-VINDAS ---
if not st.session_state.abriu_cardapio:
    st.markdown("<h1 style='text-align: center; color: #E67E22;'>Ja Que É Doce 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    st.markdown("<h3 style='text-align: center;'>Feitos artesanalmente para você. ❤️</h3>", unsafe_allow_html=True)
    
    col_v = st.columns([1, 2, 1])
    if col_v[1].button("✨ VER CARDÁPIO E ESTOQUE", use_container_width=True):
        st.session_state.abriu_cardapio = True
        st.rerun()

# --- TELA 2: CARDÁPIO ---
else:
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.abriu_cardapio = False
        st.rerun()

    st.title("Cardápio do Dia 🍦")
    
    # 1. IDENTIFICAÇÃO (CUPOM E NASCIMENTO LOGO NO INÍCIO)
    c1, c2 = st.columns(2)
    with c1:
        cupons = st.text_input("Cupom (Morador ou Niver):").strip().upper()
    with c2:
        data_nasc = st.date_input("Sua Data de Nascimento:", help="Cadastre-se para o cupom aniversário!")

    eh_morador = cupons in ["MACHADORIBEIRO", "GARAGEMLOLA"]
    p_fruta = 5.0 if eh_morador else 8.0
    p_gourmet = 7.0 if eh_morador else 9.0
    p_alcoolico = 9.0 if eh_morador else 10.0

    pedido_itens_zap = []
    dados_venda_mestra = [] # Para a Tabela Gigante
    total_bruto = 0.0

    # --- CATEGORIA: SACOLÉS (BLOCO FIXO) ---
    st.header("❄️ Sacolés")
    estoque_full = {
        "Frutas": [("Goiaba", p_fruta, 4), ("Manga", p_fruta, 4), ("Frutopia", p_fruta, 3), ("Abacaxi c/ Hortelã", p_fruta, 1)],
        "Gourmet": [("Ninho c/ Nutella", p_gourmet, 5), ("Chicabon", p_gourmet, 4), ("Pudim de Leite", p_gourmet, 5), ("Coco Cremoso", p_gourmet, 6)],
        "Alcoólicos": [("Piña Colada", p_alcoolico, 1), ("Caipirinha", p_alcoolico, 2)]
    }

    for cat, itens in estoque_full.items():
        with st.expander(cat, expanded=True):
            for nome_i, preco_i, est_i in itens:
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.write(f"**{nome_i}**\nR$ {preco_i:.2f}")
                col2.write(f"Est: {est_i}")
                if est_i > 0:
                    qtd = col3.number_input("Qtd", 0, est_i, key=f"q_{nome_i}", label_visibility="collapsed")
                    if qtd > 0:
                        total_bruto += (qtd * preco_i)
                        pedido_itens_zap.append(f"✅ {qtd}x {nome_i}")
                        dados_venda_mestra.append({"Item": nome_i, "Qtd": qtd, "Preco": preco_i})
                else:
                    col3.write("❌")

    # --- CATEGORIA: SALGADOS (COM FOTO AO LADO) ---
    st.header("🥧 Salgados")
    col_img_e, col_txt_e = st.columns([1, 1.5])
    with col_img_e:
        st.image("https://raw.githubusercontent.com/Yassbessa/mae/main/empadao.jpeg")
    with col_txt_e:
        st.write("**Empadão Frango (P)**")
        q_p = st.number_input("Qtd Pequeno (R$ 12,00)", 0, 5, key="q_emp_p")
        st.write("**Empadão Frango (G)**")
        q_g = st.number_input("Qtd Grande (R$ 18,00)", 0, 0, key="q_emp_g") # Estoque 0 solicitado

    # --- CATEGORIA: BOLO (COM FOTO AO LADO) ---
    st.header("🍰 Sobremesas")
    col_img_b, col_txt_b = st.columns([1, 1.5])
    with col_img_b:
        st.image("https://raw.githubusercontent.com/Yassbessa/mae/main/bolo.jpeg")
    with col_txt_b:
        st.write("**Crunch Cake (Pote)**")
        q_b = st.number_input("Qtd Bolo (R$ 10,00)", 0, 4, key="q_bolo")

    # Registro de Salgados/Bolo
    if q_p > 0:
        total_bruto += (q_p * 12.0); pedido_itens_zap.append(f"✅ {q_p}x Empadão P"); dados_venda_mestra.append({"Item": "Empadão P", "Qtd": q_p, "Preco": 12.0})
    if q_g > 0:
        total_bruto += (q_g * 18.0); pedido_itens_zap.append(f"✅ {q_g}x Empadão G"); dados_venda_mestra.append({"Item": "Empadão G", "Qtd": q_g, "Preco": 18.0})
    if q_b > 0:
        total_bruto += (q_b * 10.0); pedido_itens_zap.append(f"✅ {q_b}x Bolo Pote"); dados_venda_mestra.append({"Item": "Bolo Pote", "Qtd": q_b, "Preco": 10.0})

    # --- FINALIZAÇÃO ---
    if total_bruto > 0:
        st.markdown(f"## 💰 Subtotal: R$ {total_bruto:.2f}") # Exibição 1
        st.divider()

        st.header("🚚 Informações de Entrega")
        nome_cli = st.text_input("Seu Nome:")
        
        if eh_morador:
            apto_cli = st.text_input("Seu Apartamento:")
            entrega_op = st.radio("Como prefere?", ["Entregar agora", "Buscar no 902", "Agendar Entrega"])
            h_agenda = st.text_input("Horário do Agendamento:") if entrega_op == "Agendar Entrega" else ""
            obs_entrega = f"{entrega_op} {h_agenda}"
        else:
            apto_cli = "Externo"
            endereco = st.text_input("Endereço Completo:")
            recebe = st.text_input("Com quem deixar?")
            instrucoes = st.text_area("Instruções de entrega:")
            obs_entrega = f"Endereço: {endereco} | Recebe: {recebe} | Obs: {instrucoes}"

        pagto = st.radio("Pagamento:", ["PIX", "Dinheiro", "Cartão"])
        if pagto == "PIX":
            st.success(f"🔑 PIX: {CHAVE_PIX}")
            st.info(f"📧 Comprovante para: {EMAIL_COMPROVANTE}\n📝 Assunto: Comprovante Apto {apto_cli}")

        st.markdown(f"### Total Final: R$ {total_bruto:.2f}") # Exibição 2
        
        if st.button("🚀 FINALIZAR E ENVIAR", type="primary"):
            if nome_cli and (apto_cli or endereco):
                data_hoje = pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
                niver = data_nasc.strftime("%d/%m")

                # Criando as linhas para a Tabela Mestra (Tabela Gigante que você pediu)
                linhas_planilha = []
                for d in dados_venda_mestra:
                    linhas_planilha.append({
                        "Data": data_hoje, "Nome": nome_cli, "Apto/Endereço": apto_cli if eh_morador else endereco,
                        "Nascimento": niver, "Item": d['Item'], "Qtd": d['Qtd'], 
                        "Preço_Unit": d['Preco'], "Total_Pedido": total_bruto,
                        "Pagto": pagto, "Entrega/Obs": obs_entrega
                    })
                
                df_final = pd.DataFrame(linhas_planilha)
                
                # COMANDO PARA SALVAR NA PLANILHA (Worksheet: Vendas_Geral)
                try:
                    conn.create(worksheet="Vendas_Geral", data=df_final)
                    st.success("Venda registrada com sucesso!")
                except:
                    st.warning("Aguardando conexão final com a planilha...")

                # WHATSAPP
                msg = f"🍦 *NOVO PEDIDO*\n👤 {nome_cli}\n📍 {apto_cli}\n🎂 Niver: {niver}\n\n*ITENS:*\n" + "\n".join(pedido_itens_zap) + f"\n\n💰 *Total: R$ {total_bruto:.2f}*"
                dest = NUMERO_YASMIN if eh_morador else NUMERO_JAQUE
                
                st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'https://wa.me/{dest}?text={urllib.parse.quote(msg)}\' /">', unsafe_allow_html=True)
            else:
                st.error("Preencha seu nome e local de entrega!")
