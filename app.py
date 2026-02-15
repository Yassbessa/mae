import streamlit as st
import urllib.parse
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")

if 'abriu_cardapio' not in st.session_state:
    st.session_state.abriu_cardapio = False

# --- DADOS FIXOS ---
NUMERO_YASMIN = "5521981816105" 
NUMERO_JAQUE = "5521976141210" 
CHAVE_PIX = "30.615.725 000155" 
EMAIL_COMPROVANTE = "jaqueedoce@gmail.com"

# --- TELA 1: BOAS-VINDAS ---
if not st.session_state.abriu_cardapio:
    st.markdown("<h1 style='text-align: center; color: #E67E22;'>Ja Que É Doce 🐝</h1>", unsafe_allow_html=True)
    st.write("---")
    st.markdown("<h3 style='text-align: center;'>Feitos artesanalmente para você. ❤️</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✨ VER CARDÁPIO E ESTOQUE", use_container_width=True):
            st.session_state.abriu_cardapio = True
            st.rerun()

# --- TELA 2: CARDÁPIO ---
else:
    if st.button("⬅️ Voltar"):
        st.session_state.abriu_cardapio = False
        st.rerun()

    st.title("Cardápio do Dia 🍦")
    
    cupons_input = st.text_input("Possui cupons?").strip().upper()
    eh_morador = ("MACHADORIBEIRO" in cupons_input or "GARAGEMLOLA" in cupons_input)
    
    p_fruta = 5.00 if eh_morador else 8.00
    p_gourmet = 7.00 if eh_morador else 9.00
    p_alcoolico = 9.00 if eh_morador else 10.00

    pedido_lista = [] 
    dados_venda = []  
    total_bruto = 0.0

    # --- CATEGORIA: SACOLÉS ---
    st.header("❄️ Sacolés")
    estoque_sacoles = {
        "Frutas": [
            {"item": "Goiaba", "p": p_fruta, "est": 4},
            {"item": "Manga", "p": p_fruta, "est": 4},
            {"item": "Abacaxi c/ Hortelã", "p": p_fruta, "est": 1},
            {"item": "Frutopia", "p": p_fruta, "est": 3}
        ],
        "Gourmet": [
            {"item": "Ninho c/ Nutella", "p": p_gourmet, "est": 5},
            {"item": "Chicabon", "p": p_gourmet, "est": 4},
            {"item": "Pudim de Leite", "p": p_gourmet, "est": 5},
            {"item": "Coco Cremoso", "p": p_gourmet, "est": 6}
        ],
        "Alcoólicos": [
            {"item": "Piña Colada", "p": p_alcoolico, "est": 1},
            {"item": "Caipirinha", "p": p_alcoolico, "est": 2}
        ]
    }

    for cat, itens in estoque_sacoles.items():
        with st.expander(cat, expanded=True):
            for i in itens:
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{i['item']}**\nR$ {i['p']:.2f}")
                c2.write(f"Est: {i['est']}")
                if i['est'] > 0:
                    q = c3.number_input("Qtd", 0, i['est'], key=f"q_{i['item']}", label_visibility="collapsed")
                    if q > 0:
                        total_bruto += (q * i['p'])
                        pedido_lista.append(f"✅ {q}x {i['item']}")
                        dados_venda.append({"Item": i['item'], "Tipo": "Sacolé", "Quantidade": q, "Subtotal": q * i['p']})
                else:
                    c3.write("❌")

    # --- CATEGORIA: SALGADOS ---
    st.header("🥧 Salgados")
    col_img_e, col_txt_e = st.columns([1, 1.5])
    with col_img_e:
        st.image("https://raw.githubusercontent.com/Yassbessa/mae/main/empadao.jpeg")
    with col_txt_e:
        st.write("**Empadão Frango (P - 220ml)**")
        st.write("R$ 12.00 | Estoque: 5")
        q_p = st.number_input("Qtd Pequeno", 0, 5, key="q_emp_p")
        st.write("---")
        st.write("**Empadão Frango (G - 500ml)**")
        st.write("R$ 18.00 | Estoque: 0")
        q_g = st.number_input("Qtd Grande", 0, 0, key="q_emp_g") # Estoque 0

    if q_p > 0:
        total_bruto += (q_p * 12.00)
        pedido_lista.append(f"✅ {q_p}x Empadão P")
        dados_venda.append({"Item": "Empadão (P)", "Tipo": "Salgado", "Quantidade": q_p, "Subtotal": q_p * 12.00})
    if q_g > 0:
        total_bruto += (q_g * 18.00)
        pedido_lista.append(f"✅ {q_g}x Empadão G")
        dados_venda.append({"Item": "Empadão (G)", "Tipo": "Salgado", "Quantidade": q_g, "Subtotal": q_g * 18.00})

    # --- CATEGORIA: BOLO ---
    st.header("🍰 Sobremesas")
    col_img_b, col_txt_b = st.columns([1, 1.5])
    with col_img_b:
        st.image("https://raw.githubusercontent.com/Yassbessa/mae/main/bolo.jpeg")
    with col_txt_b:
        st.write("**Crunch Cake (Pote)**")
        st.write("R$ 10.00 | Estoque: 4")
        q_bolo = st.number_input("Quantidade", 0, 4, key="q_bolo")
        if q_bolo > 0:
            total_bruto += (q_bolo * 10.00)
            pedido_lista.append(f"✅ {q_bolo}x Bolo Pote")
            dados_venda.append({"Item": "Crunch Cake", "Tipo": "Bolo", "Quantidade": q_bolo, "Subtotal": q_bolo * 10.00})

    # --- FINALIZAÇÃO ---
    if total_bruto > 0:
        st.divider()
        st.subheader("🏁 Finalizar Pedido")
        nome = st.text_input("Seu Nome:")
        
        if eh_morador:
            apto = st.text_input("Seu Apartamento:")
            entrega_op = st.radio("Entrega:", ["Entregar agora", "Buscar no 902", "Agendar Entrega"])
            detalhe_entrega = f"Apto: {apto} | Modo: {entrega_op}"
            if entrega_op == "Agendar Entrega":
                horario = st.text_input("Horário desejado:")
                detalhe_entrega += f" ({horario})"
        else:
            apto = "Externo"
            endereco = st.text_input("Endereço de Entrega:")
            quem = st.text_input("Quem recebe?")
            instrucoes = st.text_area("Instruções (onde bater/interfonar):")
            detalhe_entrega = f"Endereço: {endereco} | Recebe: {quem} | Obs: {instrucoes}"

        # --- PAGAMENTO ---
        st.markdown("### 💰 Pagamento")
        forma_pagto = st.radio("Forma de Pagamento:", ["PIX", "Dinheiro", "Cartão"])
        
        if forma_pagto == "PIX":
            st.info(f"🔑 **Chave PIX:** {CHAVE_PIX}\n\n📧 Envie o comprovante para **{EMAIL_COMPROVANTE}**\n📝 **Título do e-mail:** Comprovante Apto {apto if eh_morador else 'Externo'}")

        if nome and (eh_morador and apto or not eh_morador and endereco):
            destinatario = NUMERO_YASMIN if eh_morador else NUMERO_JAQUE
            lista_msg = "\n".join(pedido_lista)
            msg = f"🍦 *NOVO PEDIDO*\n👤 Nome: {nome}\n📍 {detalhe_entrega}\n💳 Pagto: {forma_pagto}\n\n*ITENS:*\n{lista_msg}\n\n💰 *TOTAL: R$ {total_bruto:.2f}*"
            
            st.link_button("🚀 ENVIAR PEDIDO NO WHATSAPP", f"https://wa.me/{destinatario}?text={urllib.parse.quote(msg)}", type="primary")

            # --- ÁREA DA YASMIN: TABELAS ---
            with st.expander("📊 Área da Yasmin (Relatório de Vendas)"):
                st.write(f"### 📈 Relatório do Pedido: {nome}")
                
                # Tabela 1: Detalhe por Sabor
                df_detalhado = pd.DataFrame(dados_venda)
                st.write("**Itens e Sabores Selecionados:**")
                st.table(df_detalhado)
                
                # Tabela 2: Ranking (Simulado para esta venda)
                st.write("**Ranking por Apartamento (Registro desta venda):**")
                ranking_df = pd.DataFrame([{"Apto/Local": apto, "Itens": sum(d['Quantidade'] for d in dados_venda), "Total": f"R$ {total_bruto:.2f}"}])
                st.table(ranking_df)
                
                st.info("Nota: Para salvar o histórico de todos os dias e ver quem é o campeão de compras do mês, precisamos conectar ao Google Sheets.")
