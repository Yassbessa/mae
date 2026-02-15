import streamlit as st
import urllib.parse
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Jaque é Doce!", page_icon="🐝", layout="centered")

# --- CONTATOS ---
NUMERO_YASMIN = "5521981816105" 
NUMERO_JAQUE = "5521976141210" 
CHAVE_PIX = "30.615.725 000155" 

# --- SISTEMA DE CUPONS ---
st.sidebar.title("🎟️ Cupons e Promoções")
cupons_digitados = st.sidebar.text_input("Digite seus cupons (separe por vírgula):").upper()

# Verifica quais cupons estão ativos
lista_cupons = [c.strip() for c in cupons_digitados.split(",")]
eh_morador = "MACHADORIBEIRO" in lista_cupons or "GARAGEMLOLA" in lista_cupons
cupom_garagem = "GARAGEMLOLA" in lista_cupons
cupom_niver = "ANIVERSARIO" in lista_cupons

# Definição de preços
p_fruta = 5.00 if eh_morador else 8.00
p_gourmet = 7.00 if eh_morador else 9.00
p_frutopia = 7.00 if eh_morador else 9.00
p_alcoolico = 9.00 if eh_morador else 10.00

# --- CARDÁPIO ---
cardapio = {
    "❄️ Sacolés Fruta": [
        {"item": "Goiaba", "preco": p_fruta},
        {"item": "Manga", "preco": p_fruta},
        {"item": "Abacaxi c/ Hortelã", "preco": p_fruta},
    ],
    "🍫 Sacolés Gourmet": [
        {"item": "Ninho c/ Nutella", "preco": p_gourmet},
        {"item": "Chicabon", "preco": p_gourmet},
        {"item": "Pudim de Leite", "preco": p_gourmet},
    ],
    "🔞 Alcoólicos": [
        {"item": "Piña Colada", "preco": p_alcoolico},
        {"item": "Batida Morango", "preco": p_alcoolico},
    ],
    "🥧 Comidas": [
        {"item": "Empadão Frango (P)", "preco": 12.00},
        {"item": "Crunch Cake (Pote)", "preco": 10.00},
    ]
}

st.title("Jaque é Doce! 🐝")
if eh_morador: st.success("🏠 Preços de Morador Ativados!")
if cupom_niver: st.balloons(); st.info("🎂 Parabéns! 1 Sacolé de brinde aplicado!")

# --- SELEÇÃO DE PRODUTOS ---
pedido_atual = []
total_bruto = 0.0

for cat, itens in cardapio.items():
    st.subheader(cat)
    for p in itens:
        col1, col2 = st.columns([4, 1])
        qtd = col2.number_input(f"Qtd", 0, 20, key=p['item'])
        col1.write(f"**{p['item']}** - R$ {p['preco']:.2f}")
        if qtd > 0:
            for _ in range(qtd):
                pedido_atual.append({"Sabor": p['item'], "Preco": p['preco'], "Categoria": cat})
            total_bruto += (qtd * p['preco'])

# --- LÓGICA DE DESCONTOS ACUMULADOS ---
valor_desconto = 0.0
if cupom_niver and len(pedido_atual) > 0:
    # Acha o sacolé mais barato para dar de brinde
    apenas_sacoles = [p for p in pedido_atual if "Sacolé" in p['Categoria'] or "Alcoólico" in p['Categoria']]
    if apenas_sacoles:
        brinde = min(apenas_sacoles, key=lambda x: x['Preco'])
        valor_desconto = brinde['Preco']

total_com_descontos = total_bruto - valor_desconto

# --- FINALIZAÇÃO ---
if total_bruto > 0:
    st.divider()
    nome = st.text_input("Nome:")
    apto = st.text_input("Apartamento:")
    entrega = st.radio("Entrega:", ["Agora", "Buscar no 902", "Agendar"])
    
    st.write(f"**Subtotal:** R$ {total_bruto:.2f}")
    if valor_desconto > 0: st.write(f"🎁 **Brinde Niver:** - R$ {valor_desconto:.2f}")
    st.subheader(f"Total: R$ {total_com_descontos:.2f}")

    if nome and apto:
        destinatario = NUMERO_YASMIN if eh_morador else NUMERO_JAQUE
        msg = f"🚚 *PEDIDO - {'YASMIN' if eh_morador else 'JAQUE'}*\n📍 *APTO:* {apto} ({nome})\n🕒 *HORA:* {entrega}\n"
        msg += "------------------\n"
        for p in set([x['Sabor'] for x in pedido_atual]):
            qtd_item = len([x for x in pedido_atual if x['Sabor'] == p])
            msg += f"✅ {qtd_item}x {p}\n"
        msg += f"------------------\n💰 *TOTAL: R$ {total_com_descontos:.2f}*"
        
        st.link_button("🚀 ENVIAR PEDIDO", f"https://wa.me/{destinatario}?text={urllib.parse.quote(msg)}")

# --- RELATÓRIOS (DASHBOARD DA YASMIN) ---
with st.expander("📊 Relatórios de Vendas (Área Administrativa)"):
    if nome and apto and len(pedido_atual) > 0:
        st.write("### Venda Atual Detalhada")
        df_venda = pd.DataFrame(pedido_atual)
        st.dataframe(df_venda)
        
        st.write("### Ranking por Apartamento (Simulação)")
        # Quando tivermos a planilha, aqui mostrará quem compra mais
        st.bar_chart({"Apto 901": 5, f"Apto {apto}": len(pedido_atual)})
