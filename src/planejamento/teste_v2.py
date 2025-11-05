import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- 1. Definição da Função de Cálculo ---
def calcular_mcu(tac, spread, averbacao, formalizacao, comissao1, comissao2, qtd_consulta, valor_por_consulta):
    """Calcula a Margem de Contribuição Unitária (MCU)."""
    
    # 1. Receita Bruta (RB)
    receita_bruta = tac + spread
    
    # 2. Custos Variáveis (CV)
    custos_variaveis_fixos = averbacao + formalizacao + comissao1 + comissao2
    custo_consulta = qtd_consulta * valor_por_consulta
    custos_variaveis_total = custos_variaveis_fixos + custo_consulta
    
    # 3. Margem de Contribuição Unitária (MCU)
    mcu = receita_bruta - custos_variaveis_total
    
    return mcu, receita_bruta, custos_variaveis_total

# --- 2. Configuração do Streamlit ---
st.set_page_config(layout="wide", page_title="Análise da Margem de Contribuição")

st.title("💰 Análise Interativa da Margem de Contribuição (MCU)")
st.markdown("Use a barra lateral para ajustar os parâmetros financeiros e veja o impacto na MCU e no ponto de ruptura.")

# --- 3. Sidebar (Inputs para o Usuário) ---
st.sidebar.header("Parâmetros Financeiros")

# Valores Padrão
tac_default = 39.04
spread_default = 10.42
averbacao_default = 0.65
formalizacao_default = 2.85
comissao1_default = 35.29
comissao2_default = 2.05
valor_consulta_default = 0.25
qtd_consulta_teste_default = 1
taxa_aprovacao_default = 0.006 # 0.6%

# Sliders e Inputs
tac = st.sidebar.number_input("TAC (Taxa de Abertura de Crédito)", min_value=0.0, value=tac_default, step=0.01, format="%.2f")
spread = st.sidebar.number_input("SPREAD (Margem de Lucro)", min_value=0.0, value=spread_default, step=0.01, format="%.2f")

st.sidebar.markdown("---")
st.sidebar.subheader("Custos Operacionais Variáveis (por unidade)")
averbacao = st.sidebar.number_input("Averbação", min_value=0.0, value=averbacao_default, step=0.01, format="%.2f")
formalizacao = st.sidebar.number_input("Formalização", min_value=0.0, value=formalizacao_default, step=0.01, format="%.2f")
comissao1 = st.sidebar.number_input("Comissão 1", min_value=0.0, value=comissao1_default, step=0.01, format="%.2f")
comissao2 = st.sidebar.number_input("Comissão 2", min_value=0.0, value=comissao2_default, step=0.01, format="%.2f")

st.sidebar.markdown("---")
st.sidebar.subheader("Custo Variável por Consulta")
valor_por_consulta = st.sidebar.number_input("Custo por Consulta (R$)", min_value=0.01, value=valor_consulta_default, step=0.01, format="%.2f")
qtd_consulta_teste = st.sidebar.slider("Quantidade de Consultas para Teste", min_value=1, max_value=150, value=qtd_consulta_teste_default)
max_consultas_grafico = st.sidebar.slider("Máximo de Consultas no Gráfico MCU", min_value=20, max_value=200, value=70)

st.sidebar.markdown("---")
st.sidebar.subheader("Parâmetro de Rentabilidade Agregada")
taxa_aprovacao = st.sidebar.number_input("Taxa de Aprovação (Ex: 0.006 para 0.6%)", min_value=0.0001, max_value=1.0, value=taxa_aprovacao_default, step=0.0001, format="%.4f")


# --- 4. Execução do Cálculo para o cenário atual ---

mcu_atual, rb_atual, cv_atual = calcular_mcu(tac, spread, averbacao, formalizacao, comissao1, comissao2, qtd_consulta_teste, valor_por_consulta)
custos_fixos_sem_consulta = averbacao + formalizacao + comissao1 + comissao2
mcu_maxima_calculada = (tac + spread) - custos_fixos_sem_consulta # MCU com 0 consultas

# Valor fixo solicitado pelo usuário para o cálculo do Lucro Bruto Total (R$ 8,35)
MCU_MAXIMA_FIXA = 8.35 

# --- 5. Exibição dos Indicadores Chave ---

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Receita Bruta (RB)", f"R$ {rb_atual:,.2f}")
with col2:
    st.metric("Custos Variáveis (CV)", f"R$ {cv_atual:,.2f}")
with col3:
    st.metric(f"MCU Atual (com {qtd_consulta_teste} consultas)", f"R$ {mcu_atual:,.2f}", delta="Positiva" if mcu_atual > 0 else "Negativa")

# Determinação e exibição do Ponto de Ruptura
margem_disponivel_para_consulta = rb_atual - custos_fixos_sem_consulta

if margem_disponivel_para_consulta > 0 and valor_por_consulta > 0:
    ponto_ruptura = margem_disponivel_para_consulta / valor_por_consulta
    ponto_ruptura_int = int(np.floor(ponto_ruptura))
    mcu_ruptura, _, _ = calcular_mcu(tac, spread, averbacao, formalizacao, comissao1, comissao2, ponto_ruptura_int, valor_por_consulta)

    with col4:
        st.metric("Ponto de Ruptura (Máx. Consultas)", f"{ponto_ruptura_int} consultas", help=f"A partir de {ponto_ruptura_int + 1} consultas, a MCU se torna negativa. MCU no limite: R$ {mcu_ruptura:.2f}")

else:
    with col4:
        st.error("Não é possível calcular o Ponto de Ruptura.")


st.markdown("---")

# --- 6. Geração do Gráfico de Tendência da MCU (Unitário) ---

st.header("📈 Tendência da Margem de Contribuição Unitária (MCU)")
st.subheader("MCU em função do número de consultas (Unitário)")

consultas_unitarias = np.arange(1, max_consultas_grafico + 1)
mcus_unitarias = [calcular_mcu(tac, spread, averbacao, formalizacao, comissao1, comissao2, q, valor_por_consulta)[0] for q in consultas_unitarias]

df_mcu = pd.DataFrame({'Consultas': consultas_unitarias, 'MCU': mcus_unitarias})

fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(df_mcu['Consultas'], df_mcu['MCU'], marker='o', linestyle='-', color='skyblue', label='MCU por Consulta')
ax.axhline(0, color='red', linestyle='--', linewidth=2, label='Ponto de Equilíbrio (MCU=0)')

if 'ponto_ruptura_int' in locals():
    ax.axvline(ponto_ruptura_int, color='green', linestyle=':', linewidth=2, label=f'Máximo Viável ({ponto_ruptura_int})')
    ax.plot(qtd_consulta_teste, mcu_atual, 'o', color='purple', markersize=8, label=f'Cenário Atual ({qtd_consulta_teste} consultas)')

ax.set_title(f'MCU em Função do Número de Consultas (Máx. {max_consultas_grafico})')
ax.set_xlabel('Quantidade de Consultas por Contrato')
ax.set_ylabel('Margem de Contribuição Unitária (R$)')
ax.grid(True, linestyle='--')
ax.legend()
plt.tight_layout()

st.pyplot(fig)

st.markdown(f"""
<div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px;">
    **Interpretação do Gráfico MCU:** Mostra o impacto das consultas na margem de contribuição de **uma única transação**. MCU Máxima (0 consultas): **R$ {mcu_maxima_calculada:,.2f}**
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- 7. NOVO GRÁFICO: Lucro Bruto Total Gerado (Fórmula Solicitada) ---

st.header("💵 Geração de Lucro Bruto Total (Agregado)")
st.subheader(f"Cálculo: N_Consultas x Taxa Aprovação ({taxa_aprovacao*100:.3f}%) x Lucro Fixo por Aprovada (R$ {MCU_MAXIMA_FIXA:.2f})")

# Definir o range máximo de consultas para o gráfico de tendência
MAX_CONSULTAS_TREND = 3000000 
consultas_tendencia = np.linspace(0, MAX_CONSULTAS_TREND, 100) # De 0 a 3 milhões, 100 pontos

# Cálculo da linha de tendência
# Lucro Bruto Total = n_consultas * taxa_aprovacao * MCU_MAXIMA_FIXA
fator_lucro_fixo = taxa_aprovacao * MCU_MAXIMA_FIXA
lucro_bruto_total_tendencia = consultas_tendencia * fator_lucro_fixo

# Criação do DataFrame
df_lucro_tendencia = pd.DataFrame({
    'Consultas': consultas_tendencia,
    'Lucro Bruto Total (R$)': lucro_bruto_total_tendencia
})

# Criação do Gráfico
fig_lucro, ax_lucro = plt.subplots(figsize=(10, 5))

# Plotar a linha de tendência
ax_lucro.plot(df_lucro_tendencia['Consultas'], df_lucro_tendencia['Lucro Bruto Total (R$)'], color='green', linestyle='-', linewidth=2, label='Lucro Bruto Total Gerado')

# Linha de Gasto Total de Consultas (Linha 1 do pedido anterior, que você quer visualizar)
custo_total_tendencia = consultas_tendencia * valor_por_consulta
ax_lucro_custo = ax_lucro.twinx() # Cria um segundo eixo Y para o custo
color_custo = 'tab:red'
ax_lucro_custo.plot(consultas_tendencia, custo_total_tendencia, color=color_custo, linestyle='--', label='Custo Total de Consultas')
ax_lucro_custo.set_ylabel('Custo Total de Consultas (R$)', color=color_custo)
ax_lucro_custo.tick_params(axis='y', labelcolor=color_custo)
ax_lucro_custo.ticklabel_format(style='plain', axis='y')


# Configurações do Gráfico
ax_lucro.set_title(f'Tendência do Lucro Bruto Total vs. Custo Total (Lucro Fixo: R$ {MCU_MAXIMA_FIXA:.2f})')
ax_lucro.set_xlabel('Quantidade Total de Consultas')
ax_lucro.set_ylabel('Lucro Bruto Total (R$)', color='green')
ax_lucro.tick_params(axis='y', labelcolor='green')
ax_lucro.grid(True, linestyle='--')
ax_lucro.ticklabel_format(style='plain', axis='y')
ax_lucro.ticklabel_format(style='plain', axis='x')

# Juntar as legendas
lines, labels = ax_lucro.get_legend_handles_labels()
lines2, labels2 = ax_lucro_custo.get_legend_handles_labels()
ax_lucro_custo.legend(lines + lines2, labels + labels2, loc='upper left')

# SLIDER ABAIXO DO GRÁFICO para setar o volume atual
st.markdown("---")
col_slider, col_metric_lucro, col_metric_custo = st.columns([2, 1, 1])

with col_slider:
    volume_consultas_atual = st.slider(
        "Selecione o Volume Total de Consultas para Análise", 
        min_value=0, 
        max_value=MAX_CONSULTAS_TREND, 
        value=2200000, 
        step=50000
    )

# Cálculo do valor do ponto do slider
lucro_no_volume = volume_consultas_atual * fator_lucro_fixo
custo_no_volume = volume_consultas_atual * valor_por_consulta

# Adicionar um ponto no gráfico
ax_lucro.plot(volume_consultas_atual, lucro_no_volume, 'o', color='darkgreen', markersize=8)
ax_lucro_custo.plot(volume_consultas_atual, custo_no_volume, 'o', color='darkred', markersize=8)
ax_lucro.axvline(volume_consultas_atual, color='gray', linestyle=':', linewidth=1)

# Exibição dos valores calculados
with col_metric_lucro:
    aprovacoes_calculadas = volume_consultas_atual * taxa_aprovacao
    st.metric(
        "Lucro Bruto Total (R$ 8.35/aprovada)", 
        f"R$ {lucro_no_volume:,.2f}", 
        help=f"Baseado em {aprovacoes_calculadas:,.0f} aprovações esperadas."
    )
with col_metric_custo:
    st.metric(
        f"Custo Total de Consultas (R$ {valor_por_consulta:.2f}/consulta)", 
        f"R$ {custo_no_volume:,.2f}", 
        delta=f"Perda de R$ {custo_no_volume - lucro_no_volume:,.2f}" if custo_no_volume > lucro_no_volume else None,
        delta_color="inverse" if custo_no_volume > lucro_no_volume else "normal"
    )

plt.tight_layout()
st.pyplot(fig_lucro)

st.markdown(f"""
<div style="background-color: #fff3cd; padding: 10px; border-radius: 5px; border-left: 5px solid orange;">
    **Interpretação da Tendência Agregada:**
    <ul>
        <li>A linha **Verde** (Eixo Y Esquerdo) mostra o **Lucro Bruto Total** gerado. Ela representa a receita potencial baseada no volume de consultas e na taxa de aprovação, usando o lucro fixo de **R$ {MCU_MAXIMA_FIXA:.2f}** por contrato aprovado.</li>
        <li>A linha **Vermelha** (Eixo Y Direito) mostra o **Custo Total** de todas as consultas.</li>
        <li>No volume de {volume_consultas_atual:,.0f} consultas, a diferença entre o Custo Total (R$ {custo_no_volume:,.2f}) e o Lucro Bruto Total (R$ {lucro_no_volume:,.2f}) é de **R$ {custo_no_volume - lucro_no_volume:,.2f}**, evidenciando o prejuízo operacional na unidade de consulta/aprovado.</li>
    </ul>
</div>
""", unsafe_allow_html=True)