import streamlit as st
import urllib.parse
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ja Que É Doce", page_icon="🐝", layout="centered")

if 'abriu_cardapio' not in st.session_state:
    st.session_state.abriu_cardapio = False

# --- CONTATOS E DADOS FIXOS ---
NUMERO_YASMIN = "5521981816105" 
NUMERO_JAQUE = "5521976141210" 
CHAVE_PIX = "30.615.725 000155" 

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

    pedido_lista = [] # Para a mensagem do WhatsApp
    dados_venda = []  # Para as tabelas de relatório da Yasmin
    total_bruto = 0.0

    # --- CATEGORIA: SACOLÉS ---
    st.header("❄️ Sacolés")
    estoque_sacoles = {
        "Frutas (Sem Lactose)": [
            {"item": "Goiaba", "p": p_fruta, "est": 4},
            {"item": "Manga", "p": p_fruta, "est": 4},
            {"item": "Abacaxi c/ Hortelã", "p": p_fruta, "est": 1},
            {"item": "Frutopia", "p": p_fruta, "est": 3}
        ],
        "Gourmet (Cremosos)": [
            {"item": "Ninho c/ Nutella", "p": p_gourmet, "est": 5},
            {"item": "Ninho c/ Morango", "p": p_gourmet, "est": 4},
            {"item": "Chicabon", "p": p_gourmet, "est": 4},
            {"item": "Pudim de Leite", "p": p_gourmet, "est": 5},
            {"item": "Coco Cremoso", "p": p_gourmet, "est": 6}
        ],
        "Alcoólicos (+18)": [
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

    # --- CATEGORIA: SALGADOS (COM EMPADÃO GRANDE) ---
    st.header("🥧 Salgados (Prontos e Congelados)")
    col_img_e, col_txt_e = st.columns([1, 1.5])
    with col_img_e:
        st.image("https://raw.githubusercontent.com/Yassbessa/mae/main/empadao.jpeg")
    with col_txt_e:
        # Pequeno
        st.write("**Empadão Frango (P - 220ml)**")
        st.write("R$ 12.00 | Estoque: 5")
        q_emp_p = st.number_input("Qtd Pequeno", 0, 5, key="q_emp_p")
        
        st.write("---")
        
        # Grande (Estoque 0 conforme solicitado)
        st.write("**Empadão Frango (G - 500ml)**")
        st.write("R$ 18.00 | Estoque: 0")
        q_emp_g = st.number_input("Qtd Grande", 0, 0, key="q_emp_g") # Limitado a 0

    if q_emp_p > 0:
        total_bruto += (q_emp_p * 12.00)
        pedido_lista.append(f"✅ {q_emp_p}x Empadão P")
        dados_venda.append({"Item": "Empadão Frango (P)", "Tipo": "Salgado", "Quantidade": q_emp_p, "Subtotal": q_emp_p * 12.00})

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

    # --- FINALIZAÇÃO E DADOS DE ENTREGA ---
    if total_bruto > 0:
        st.divider()
        st.subheader(f"Total: R$ {total_bruto:.2f}")
        
        nome = st.text_input("Seu Nome:")
        
        if eh_morador:
            # Opções exclusivas para vizinhos
            apto = st.text_input("Seu Apartamento:")
            entrega_op = st.radio("Opção de Entrega/Retirada:", ["Entregar agora", "Buscar no 902", "Agendar Entrega"])
            detalhe_agendamento = ""
            if entrega_op == "Agendar Entrega":
                detalhe_agendamento = st.text_input("Para qual horário deseja agendar?")
            info_entrega = f"Apto: {apto} | Opção: {entrega_op} {detalhe_agendamento}"
        else:
            # Opções para clientes externos
            apto = "Externo"
            st.markdown("### 🏠 Informações para Entrega")
            endereco = st.text_input("Endereço Completo:")
            quem_recebe = st.text_input("Com quem podemos deixar o pedido?")
            instrucoes = st.text_area("Instruções Adicionais (onde bater/interfonar, etc.):")
            info_entrega = f"Endereço: {endereco}\nRecebedor: {quem_recebe}\nInstruções: {instrucoes}"

        if nome and (apto != "" or endereco != ""):
            destinatario = NUMERO_YASMIN if eh_morador else NUMERO_JAQUE
            lista_msg = "\n".join(pedido_lista)
            msg = f"🍦 *NOVO PEDIDO*\n👤 Nome: {nome}\n📍 {info_entrega}\n\n*ITENS:*\n{lista_msg}\n\n💰 *Total: R$ {total_bruto:.2f}*"
            
            st.link_button("🚀 ENVIAR PEDIDO NO WHATSAPP", f"https://wa.me/{destinatario}?text={urllib.parse.quote(msg)}", type="primary")

            # --- ÁREA DA YASMIN: RELATÓRIOS ---
            with st.expander("📊 Área da Yasmin (Relatório de Vendas)"):
                st.write(f"### 📈 Resumo do Pedido Atual: {nome}")
                
                # Tabela 1: Quantidade e Sabor
                df_detalhado = pd.DataFrame(dados_venda)
                st.write("**Tabela de Itens Selecionados:**")
                st.table(df_detalhado)
                
                # Tabela 2: Resumo para o Ranking
                st.write("**Ranking por Apartamento (Registro desta venda):**")
                ranking_df = pd.DataFrame([{"Apartamento": apto, "Total Itens": sum(item['Quantidade'] for item in dados_venda), "Total Gasto": total_bruto}])
                st.table(ranking_df)
                
                st.info("Nota: Para acumular as vendas de todos os dias em uma tabela única, precisaremos conectar ao Google Sheets.")
