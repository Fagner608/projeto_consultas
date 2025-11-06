import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm

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

negbin_model = sm.load("negbin_model.pkl")

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

# Certifique-se de que negbin_model está carregado no Streamlit antes deste ponto
# Se você está usando a versão com intercepto zero:
# negbin_model = smf.glm(formula="qtd_finalizadas ~ qtd_nao_finalizadas + 0", data=df, family=sm.families.NegativeBinomial()).fit()

# --- Cabeçalho ---
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.header("📉 Curva de Retorno Marginal e Ponto de Platô")

# ===============================
# 🎚️ CONTROLES INTERATIVOS
# ===============================
with st.expander("⚙️ Ajustar parâmetros do modelo"):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        TAXA_CONVERSAO = st.slider(
            "Taxa de Conversão",
            min_value=0.00010,
            max_value=0.1,
            value=0.0069,
            step=0.0001,
            format="%.4f"
        )
    with col2:
        MCU = st.slider(
            "MCU (R$)",
            min_value=-30.00,
            max_value=30.0,
            value=8.60,
            step=1.0
        )
    with col3:
        CUSTO_CONSULTA = st.slider(
            "Custo p/ Consulta (R$)",
            min_value=0.10,
            max_value=1.00,
            value=0.25,
            step=0.01
        )
    with col4:
        MEAN_CONSULTA = st.slider(
            "Qtd Atual de Consultas",
            min_value=1000.0,
            max_value=75000.0,
            value=10000.0,
            step=500.0
        )

# ===============================
# 🧮 CÁLCULOS DO MODELO
# ===============================
LIMIAR = 0.001

dados = pd.DataFrame({"consulta": np.linspace(1000, 75000, 100)})
dados["custo"] = dados["consulta"] * CUSTO_CONSULTA
dados["mcu"] = round((dados["consulta"]) * MCU, 2)
dados["dif"] = round(dados["mcu"] - dados["custo"].shift(), 2)
dados["retorno_dif"] = round(dados["dif"] / dados["dif"].shift(), 2)
dados["retorno_dif_smooth"] = dados["retorno_dif"].rolling(window=3, center=True).mean()
dados["delta_ret_marginal_smooth"] = dados["retorno_dif_smooth"].diff().abs()
dados = dados.iloc[2:, :]

# --- Detecção do platô ---
plato = dados[dados["delta_ret_marginal_smooth"] < LIMIAR]
if not plato.empty:
    ponto_plato = plato.iloc[0]["consulta"]
    dif_no_plato = dados.loc[dados["consulta"] >= ponto_plato, "dif"].iloc[0]
else:
    ponto_plato = np.nan
    dif_no_plato = np.nan

# ===============================
# 🎯 IDENTIFICAÇÃO DO CENÁRIO ATUAL
# ===============================
# Localiza o valor mais próximo de MEAN_CONSULTA
idx_atual = (dados["consulta"] - MEAN_CONSULTA).abs().idxmin()
retorno_atual = dados.loc[idx_atual, "retorno_dif_smooth"]

# ===============================
# 📊 GRÁFICO
# ===============================
fig, ax = plt.subplots(figsize=(10, 5))

# Linha principal
ax.plot(
    dados["consulta"],
    dados["retorno_dif_smooth"],
    color='blue',
    linestyle='--',
    linewidth=2,
    label="Retorno Suavizado"
)

# Região e linha do platô
if not np.isnan(ponto_plato):
    if dif_no_plato > 0:
        cor_plato = "lightgreen"
        texto_plato = "Platô da Eficiência (Lucro)"
        cor_linha = "green"
    else:
        cor_plato = "lightcoral"
        texto_plato = "Platô da Ineficiência (Prejuízo)"
        cor_linha = "red"

    ax.axvspan(ponto_plato, dados["consulta"].max(), color=cor_plato, alpha=0.3, label=texto_plato)
    ax.axvline(x=ponto_plato, color=cor_linha, linestyle=':', linewidth=2, label=f"Ponto de Platô ({int(ponto_plato)})")

# --- Marca o ponto atual ---
ax.scatter(
    MEAN_CONSULTA, retorno_atual,
    s=120, color='purple', edgecolor='white', zorder=5,
    label=f"Cenário Atual ({int(MEAN_CONSULTA)} consultas)"
)

# Linha vertical tracejada do cenário atual
ax.axvline(x=MEAN_CONSULTA, color='purple', linestyle='--', alpha=0.6)

# Texto com seta para o ponto
ax.annotate(
    f"{int(MEAN_CONSULTA)} consultas\nRetorno: {retorno_atual:.2f}",
    xy=(MEAN_CONSULTA, retorno_atual),
    xytext=(MEAN_CONSULTA + 5000, retorno_atual + 0.05),
    arrowprops=dict(arrowstyle="->", color='purple'),
    color='purple',
    fontsize=9,
    bbox=dict(boxstyle="round,pad=0.3", fc="lavender", ec="purple", alpha=0.6)
)

# --- Estilo geral ---
ax.set_xlabel("Número de Consultas")
ax.set_ylabel("Retorno marginal (ΔDif / ΔDif anterior)")
ax.set_title("Curva de Retorno Marginal com Identificação de Eficiência, Ineficiência e Cenário Atual")
ax.legend()
ax.grid(True, linestyle='--', alpha=0.6)

st.pyplot(fig)

# ===============================
# 🧭 FEEDBACK DINÂMICO
# ===============================
if not np.isnan(ponto_plato):
    if dif_no_plato > 0:
        st.success(f"✅ Platô de **eficiência (lucro)** detectado a partir de **{int(ponto_plato)} consultas**.")
    else:
        st.error(f"⚠️ Platô de **ineficiência (prejuízo)** detectado a partir de **{int(ponto_plato)} consultas**.")
else:
    st.warning("Nenhum ponto de platô detectado com o limiar atual.")

# ===============================
# 📋 PARÂMETROS ATUAIS
# ===============================
st.markdown(f"""
**Parâmetros Atuais:**
- Taxa de Conversão: `{TAXA_CONVERSAO:.4f}`
- MCU Unitário: `R$ {MCU:.2f}`
- Custo por Consulta: `R$ {CUSTO_CONSULTA:.2f}`
- Consultas Atuais: `{int(MEAN_CONSULTA)}`
""")
