import streamlit as st
import urllib.parse
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")

# --- DADOS DO NEGÓCIO ---
NUMERO_YASMIN = "5521981816105" 
NUMERO_JAQUE = "5521976141210" 
CHAVE_PIX = "30.615.725 000155" 
EMAIL_COMPROVANTE = "jaqueedoce@gmail.com"

# --- CONTROLE DE NAVEGAÇÃO ---
if 'abriu_cardapio' not in st.session_state:
    st.session_state.abriu_cardapio = False

# --- TELA 1: BOAS-VINDAS ---
if not st.session_state.abriu_cardapio:
    st.markdown("<h1 style='text-align: center; color: #E67E22;'>Ja Que É Doce 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    st.markdown("<h3 style='text-align: center;'>Feitos artesanalmente para você. ❤️</h3>", unsafe_allow_html=True)
    
    col_v1, col_v2, col_v3 = st.columns([1, 2, 1])
    with col_v2:
        if st.button("✨ VER CARDÁPIO E ESTOQUE", use_container_width=True):
            st.session_state.abriu_cardapio = True
            st.rerun()

# --- TELA 2: CARDÁPIO E PEDIDO ---
else:
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.abriu_cardapio = False
        st.rerun()

    st.title("Cardápio do Dia 🍦")
    
    # Sistema de Cupom
    cupons_input = st.text_input("Possui cupom de morador?").strip().upper()
    eh_morador = ("MACHADORIBEIRO" in cupons_input or "GARAGEMLOLA" in cupons_input)
    
    p_fruta = 5.00 if eh_morador else 8.00
    p_gourmet = 7.00 if eh_morador else 9.00
    p_alcoolico = 9.00 if eh_morador else 10.00

    pedido_lista_zap = []
    dados_para_tabela = []
    total_bruto = 0.0

    # --- BLOCO FIXO: SACOLÉS ---
    st.header("❄️ Nossos Sacolés")
    estoque_full = {
        "Frutas (Sem Lactose)": [
            {"item": "Goiaba", "p": p_fruta, "est": 4},
            {"item": "Uva", "p": p_fruta, "est": 0},
            {"item": "Maracujá", "p": p_fruta, "est": 0},
            {"item": "Manga", "p": p_fruta, "est": 4},
            {"item": "Morango", "p": p_fruta, "est": 0},
            {"item": "Abacaxi c/ Hortelã", "p": p_fruta, "est": 1},
            {"item": "Frutopia", "p": p_fruta, "est": 3}
        ],
        "Gourmet (Cremosos)": [
            {"item": "Ninho c/ Nutella", "p": p_gourmet, "est": 5},
            {"item": "Ninho c/ Morango", "p": p_gourmet, "est": 4},
            {"item": "Chicabon", "p": p_gourmet, "est": 4},
            {"item": "Mousse de Maracujá", "p": p_gourmet, "est": 3},
            {"item": "Pudim de Leite", "p": p_gourmet, "est": 5},
            {"item": "Açaí Cremoso", "p": p_gourmet, "est": 4},
            {"item": "Coco Cremoso", "p": p_gourmet, "est": 6}
        ],
        "Alcoólicos (+18)": [
            {"item": "Piña Colada", "p": p_alcoolico, "est": 1},
            {"item": "Sex on the Beach", "p": p_alcoolico, "est": 0},
            {"item": "Caipirinha", "p": p_alcoolico, "est": 2},
            {"item": "Batida de Maracujá", "p": p_alcoolico, "est": 2},
            {"item": "Batida de Morango", "p": p_alcoolico, "est": 1}
        ]
    }

    for categoria, itens in estoque_full.items():
        with st.expander(categoria, expanded=True):
            for i in itens:
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{i['item']}**\nR$ {i['p']:.2f}")
                c2.write(f"Est: {i['est']}")
                if i['est'] > 0:
                    qtd = c3.number_input("Qtd", 0, i['est'], key=f"sac_{i['item']}", label_visibility="collapsed")
                    if qtd > 0:
                        total_bruto += (qtd * i['p'])
                        pedido_lista_zap.append(f"✅ {qtd}x {i['item']}")
                        dados_para_tabela.append({"Item": i['item'], "Tipo": "Sacolé", "Qtd": qtd, "Subtotal": qtd * i['p']})
                else:
                    c3.write("❌")

    # --- BLOCO: SALGADOS E SOBREMESAS ---
    st.header("🥧 Salgados e Doces")
    
    # Empadão com Foto
    col_img_e, col_txt_e = st.columns([1, 1.5])
    with col_img_e:
        st.image("https://raw.githubusercontent.com/Yassbessa/mae/main/empadao.jpeg")
    with col_txt_e:
        st.write("**Empadão Frango (P)**")
        q_p = st.number_input("Qtd Pequeno (R$ 12,00)", 0, 5, key="emp_p")
        st.write("**Empadão Frango (G)**")
        q_g = st.number_input("Qtd Grande (R$ 18,00)", 0, 0, key="emp_g") # Estoque 0

    # Bolo com Foto
    col_img_b, col_txt_b = st.columns([1, 1.5])
    with col_img_b:
        st.image("https://raw.githubusercontent.com/Yassbessa/mae/main/bolo.jpeg")
    with col_txt_b:
        st.write("**Crunch Cake (Pote)**")
        q_b = st.number_input("Qtd Bolo (R$ 10,00)", 0, 4, key="bolo_p")

    # Cálculos Salgados/Bolo
    if q_p > 0:
        total_bruto += (q_p * 12.0)
        pedido_lista_zap.append(f"✅ {q_p}x Empadão P")
        dados_para_tabela.append({"Item": "Empadão P", "Tipo": "Salgado", "Qtd": q_p, "Subtotal": q_p * 12.0})
    if q_b > 0:
        total_bruto += (q_b * 10.0)
        pedido_lista_zap.append(f"✅ {q_b}x Bolo Pote")
        dados_para_tabela.append({"Item": "Crunch Cake", "Tipo": "Bolo", "Qtd": q_b, "Subtotal": q_b * 10.0})

    # --- EXIBIÇÃO DO TOTAL (ANTES DOS DADOS) ---
    if total_bruto > 0:
        st.markdown(f"## 💰 Subtotal: R$ {total_bruto:.2f}")
        st.divider()

        # --- DADOS DE ENTREGA ---
        st.header("🚚 Informações de Entrega")
        nome = st.text_input("Seu Nome:")
        
        if eh_morador:
            apto = st.text_input("Seu Apartamento:")
            opcao = st.radio("Como prefere?", ["Entregar agora", "Vou buscar no 902", "Agendar Entrega"])
            detalhe_ent = f"Apto {apto} | Modo: {opcao}"
            if opcao == "Agendar Entrega":
                h = st.text_input("Horário do Agendamento:")
                detalhe_ent += f" ({h})"
        else:
            apto = "Externo"
            end = st.text_input("Endereço Completo:")
            recebe = st.text_input("Quem recebe no local?")
            obs = st.text_area("Instruções (onde bater/interfonar):")
            detalhe_ent = f"Endereço: {end} | Recebe: {recebe} | Obs: {obs}"

        # --- PAGAMENTO ---
        st.header("💳 Pagamento")
        forma = st.radio("Forma de Pagamento:", ["PIX", "Dinheiro", "Cartão"])
        
        if forma == "PIX":
            st.success(f"🔑 **Chave PIX:** {CHAVE_PIX}")
            st.info(f"📧 Envie o comprovante para: **{EMAIL_COMPROVANTE}**\n📝 **Assunto:** Comprovante Apto {apto}")

        # --- FINALIZAÇÃO ---
        st.markdown(f"### Total Final: R$ {total_bruto:.2f}")
        
        if nome and (eh_morador and apto or not eh_morador and end):
            destinatario = NUMERO_YASMIN if eh_morador else NUMERO_JAQUE
            txt_pedido = "\n".join(pedido_lista_zap)
            link_msg = f"🍦 *NOVO PEDIDO*\n👤 Nome: {nome}\n📍 {detalhe_ent}\n💳 Pagto: {forma}\n\n*ITENS:*\n{txt_pedido}\n\n💰 *TOTAL: R$ {total_bruto:.2f}*"
            
            st.link_button("🚀 ENVIAR PEDIDO NO WHATSAPP", f"https://wa.me/{destinatario}?text={urllib.parse.quote(link_msg)}", type="primary")

    # --- ÁREA DA YASMIN (DASHBOARD ESCONDIDO NA SIDEBAR) ---
    with st.sidebar:
        st.title("📊 Gestão Interna")
        if st.checkbox("Exibir Relatório de Vendas (Yasmin)"):
            if total_bruto > 0:
                st.write(f"### Pedido de: {nome}")
                df = pd.DataFrame(dados_para_tabela)
                st.subheader("Tabela de Sabores")
                st.table(df)
                
                st.subheader("Tabela por Apartamento")
                df_apto = pd.DataFrame([{"Apartamento": apto, "Qtd Itens": sum(d['Qtd'] for d in dados_para_tabela), "Total": total_bruto}])
                st.table(df_apto)
            else:
                st.info("Nenhum item selecionado para gerar relatório.")
