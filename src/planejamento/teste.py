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
max_consultas_grafico = st.sidebar.slider("Máximo de Consultas no Gráfico", min_value=20, max_value=200, value=70)


# --- 4. Execução do Cálculo para o cenário atual ---

mcu_atual, rb_atual, cv_atual = calcular_mcu(tac, spread, averbacao, formalizacao, comissao1, comissao2, qtd_consulta_teste, valor_por_consulta)

# --- 5. Exibição dos Indicadores Chave ---

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Receita Bruta (RB)", f"R$ {rb_atual:,.2f}")
with col2:
    st.metric("Custos Variáveis (CV)", f"R$ {cv_atual:,.2f}")
with col3:
    st.metric("MCU Atual (com {qtd_consulta_teste} consultas)", f"R$ {mcu_atual:,.2f}", delta="Positiva" if mcu_atual > 0 else "Negativa")

# Determinação e exibição do Ponto de Ruptura
custos_fixos_sem_consulta = averbacao + formalizacao + comissao1 + comissao2
margem_disponivel_para_consulta = rb_atual - custos_fixos_sem_consulta

if margem_disponivel_para_consulta > 0 and valor_por_consulta > 0:
    ponto_ruptura = margem_disponivel_para_consulta / valor_por_consulta
    # Arredonda para cima para garantir que a MCU não seja zero/negativa
    ponto_ruptura_int = int(np.floor(ponto_ruptura))
    
    # Recalcula a MCU no limite (ponto de ruptura)
    mcu_ruptura, _, _ = calcular_mcu(tac, spread, averbacao, formalizacao, comissao1, comissao2, ponto_ruptura_int, valor_por_consulta)

    with col4:
        st.metric("Ponto de Ruptura (Máx. Consultas)", f"{ponto_ruptura_int} consultas", help=f"A partir de {ponto_ruptura_int + 1} consultas, a MCU se torna negativa. MCU no limite: R$ {mcu_ruptura:.2f}")

else:
    with col4:
        st.error("Não é possível calcular o Ponto de Ruptura.")


st.markdown("---")

# --- 6. Geração do Gráfico de Tendência da MCU ---

st.header("📈 Tendência da Margem de Contribuição Unitária (MCU)")
st.subheader("MCU em função do número de consultas")

# Criação dos dados para o gráfico
consultas = np.arange(1, max_consultas_grafico + 1)
mcus = []

for q in consultas:
    mcu, _, _ = calcular_mcu(tac, spread, averbacao, formalizacao, comissao1, comissao2, q, valor_por_consulta)
    mcus.append(mcu)

df_mcu = pd.DataFrame({'Consultas': consultas, 'MCU': mcus})

# Criação do Gráfico
fig, ax = plt.subplots(figsize=(10, 5))

# Plot da MCU
ax.plot(df_mcu['Consultas'], df_mcu['MCU'], marker='o', linestyle='-', color='skyblue', label='MCU por Consulta')

# Linha de Zero (Ponto de Equilíbrio)
ax.axhline(0, color='red', linestyle='--', linewidth=2, label='Ponto de Equilíbrio (MCU=0)')

# Linha vertical no Ponto de Ruptura (se aplicável)
if 'ponto_ruptura_int' in locals():
    # Desenha o Ponto de Ruptura (Máximo de Consultas Viável)
    ax.axvline(ponto_ruptura_int, color='green', linestyle=':', linewidth=2, label=f'Máximo Viável ({ponto_ruptura_int})')
    # Marca a MCU atual
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
    **Interpretação do Gráfico:**
    <ul>
        <li>A linha **Azul** mostra como a MCU diminui linearmente à medida que o número de consultas aumenta.</li>
        <li>A linha **Vermelha** (eixo X) é o ponto onde a MCU é zero (lucro zero por unidade/transação).</li>
        <li>A linha **Verde** pontilhada mostra o **Ponto de Ruptura**, ou seja, o número máximo de consultas ({ponto_ruptura_int}) antes que a transação comece a gerar prejuízo na unidade.</li>
    </ul>
</div>
""", unsafe_allow_html=True)