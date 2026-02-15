import streamlit as st
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Jaque é Doce!", page_icon="🐝", layout="centered")

# --- SEUS DADOS (EDITE AQUI!) ---
WHATSAPP_NUMBER = "5521976141210" 
NOME_LOJA = "Jaque é Doce! 🐝"
INSTAGRAM = "@jaqueedoce.rj"
CHAVE_PIX = "30.615.725 000155"  # <--- COLOQUE SUA CHAVE PIX AQUI (Celular, CPF ou Email)
NOME_TITULAR_PIX = "Jaqueline Miranda" # <--- Nome que aparece no comprovante

# --- ESTOQUE E PREÇOS ---
cardapio = {
    "❄️ Sacolés Tropicais (Sem Lactose)": [
        {"item": "Goiaba", "preco": 5.00, "estoque": 4},
        {"item": "Uva", "preco": 5.00, "estoque": 0},
        {"item": "Maracujá", "preco": 5.00, "estoque": 0},
        {"item": "Manga", "preco": 5.00, "estoque": 4},
        {"item": "Morango", "preco": 5.00, "estoque": 0},
        {"item": "Abacaxi com Hortelã", "preco": 5.00, "estoque": 1},
        {"item": "Frutopia", "preco": 5.00, "estoque": 3},
    ],
    "🍫 Sacolés Gourmet": [
        {"item": "Ninho com Nutella", "preco": 7.00, "estoque": 5},
        {"item": "Ninho com Morango", "preco": 7.00, "estoque": 4},
        {"item": "Chicabon", "preco": 7.00, "estoque": 4},
        {"item": "Mousse de Maracujá", "preco": 7.00, "estoque": 3},
        {"item": "Pudim de Leite", "preco": 7.00, "estoque": 5},
        {"item": "Açaí Cremoso", "preco": 7.00, "estoque": 4},
        {"item": "Coco Cremoso", "preco": 7.00, "estoque": 6},
    ],
    "🔞 Sacolés Alcoólicos (+18)": [
        {"item": "Piña Colada", "preco": 10.00, "estoque": 1},
        {"item": "Sex on the Beach", "preco": 10.00, "estoque": 0},
        {"item": "Caipirinha de Limão", "preco": 10.00, "estoque": 2},
        {"item": "Batida de Maracujá", "preco": 10.00, "estoque": 2},
        {"item": "Batida de Morango", "preco": 10.00, "estoque": 1},
    ],
    "🥧 Empadão (Pronto e Congelado)": [
        {"item": "Empadão Frango (Pequeno 220ml)", "preco": 12.00, "estoque": 4},
        {"item": "Empadão Frango (Grande 500ml)", "preco": 18.00, "estoque": 0},
    ],
    "🍰 Bolos": [
        {"item": "Crunch Cake (Pote 180g)", "preco": 10.00, "estoque": 4},
    ]
}

# --- VISUAL DO APP ---
st.title(NOME_LOJA)
st.markdown(f"**Faça seu pedido online!** Siga a gente: [{INSTAGRAM}](https://instagram.com/{INSTAGRAM[1:]})")
st.write("---")

pedido_atual = {}
total_compra = 0.0

# --- GERAR LISTA DE PRODUTOS ---
for categoria, itens in cardapio.items():
    st.subheader(categoria)
    for produto in itens:
        col1, col2, col3 = st.columns([3, 1.5, 1.5])
        
        with col1:
            st.write(f"**{produto['item']}**")
            st.caption(f"R$ {produto['preco']:.2f}")
        
        with col2:
            if produto['estoque'] > 0:
                st.info(f"Restam: {produto['estoque']}")
            else:
                st.error("Esgotado")
        
        with col3:
            if produto['estoque'] > 0:
                chave_unica = f"{categoria}_{produto['item']}"
                qtd = st.number_input("Qtd", 0, produto['estoque'], key=chave_unica, label_visibility="collapsed")
                if qtd > 0:
                    pedido_atual[produto['item']] = {"qtd": qtd, "preco": produto['preco']}
                    total_compra += (qtd * produto['preco'])

# --- FINALIZAÇÃO DO PEDIDO ---
st.write("---")

if total_compra > 0:
    st.success(f"💰 **Total do Pedido: R$ {total_compra:.2f}**")
    
    st.markdown("### 📝 Dados para Entrega")
    col_nome, col_apto = st.columns(2)
    with col_nome:
        nome_cliente = st.text_input("Seu Nome:")
    with col_apto:
        apto_cliente = st.text_input("Apartamento / Bloco:")
    
    # Exibe o PIX apenas se preencher os dados
    if nome_cliente and apto_cliente:
        st.markdown("---")
        st.markdown("### 💸 Pagamento via PIX")
        st.code(CHAVE_PIX, language="text")
        st.caption(f"Titular: {NOME_TITULAR_PIX}")
        st.info("Copie a chave acima para pagar no seu banco.")

        # Monta a mensagem
        msg = f"*NOVO PEDIDO - JAQUE É DOCE* 🐝\n\n"
        msg += f"👤 *Cliente:* {nome_cliente}\n"
        msg += f"🏢 *Apto/Bloco:* {apto_cliente}\n\n"
        msg += "*🛒 Itens:*\n"
        for item, dados in pedido_atual.items():
            msg += f"▪️ {dados['qtd']}x {item}\n"
        msg += f"\n💰 *Total: R$ {total_compra:.2f}*\n"
        msg += f"💳 *Pagamento:* Via PIX\n"
        msg += "\n(Envie o comprovante se já tiver pago!)"
        
        # Cria o link
        texto_zap = urllib.parse.quote(msg)
        link_zap = f"https://wa.me/{WHATSAPP_NUMBER}?text={texto_zap}"
        
        st.link_button("🚀 Enviar Pedido e Comprovante", link_zap, type="primary")
    else:
        st.warning("Preencha Nome e Apartamento para ver a chave PIX e finalizar.")

else:
    st.info("Selecione os itens acima para começar.")
