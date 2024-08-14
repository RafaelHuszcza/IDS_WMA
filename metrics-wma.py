import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error

# Carregar os dados com as previsões
data = pd.read_csv('WMA_predicted.txt', sep='\t')

# Função para calcular NMSE
def calculate_nmse(true_values, predicted_values):
    mse = mean_squared_error(true_values, predicted_values)
    variance = np.var(true_values)
    if variance == 0:
        raise ValueError("A variância dos valores verdadeiros é zero. Não é possível calcular NMSE.")
    nmse = mse / variance
    return nmse

# Função para calcular MAPE
def calculate_mape(true_values, predicted_values):
    # Evitar divisão por zero
    non_zero_indices = true_values != 0
    if np.any(non_zero_indices):
        mape = mean_absolute_percentage_error(true_values[non_zero_indices], predicted_values[non_zero_indices])
    else:
        # Substituir valores zero com a média dos valores verdadeiros
        mean_value = np.mean(true_values[true_values != 0])
        mape = mean_absolute_percentage_error(true_values, predicted_values) if mean_value != 0 else np.nan
    return mape * 100  # Para porcentagem

# Obtendo os valores reais e previstos
true_values = data['packets/s']
predicted_values = data['predict_p/s']

# Calculando as métricas
try:
    nmse = calculate_nmse(true_values, predicted_values)
except ValueError as e:
    print(e)
    nmse = np.nan  # Define NMSE como NaN se ocorrer um erro

mape = calculate_mape(true_values, predicted_values)

# Criar o gráfico para as métricas
plt.figure(figsize=(12, 6))

# Plotar NMSE
plt.subplot(1, 2, 1)
plt.title('Métrica NMSE')
plt.bar(['NMSE'], [nmse], color='blue')
plt.ylabel('Valor')
plt.ylim(0, max(nmse * 1.2, 1))  # Definir limite superior um pouco maior que o NMSE para visualização

# Plotar MAPE
plt.subplot(1, 2, 2)
plt.title('Métrica MAPE')
plt.bar(['MAPE (%)'], [mape], color='green')
plt.ylabel('Percentual (%)')
plt.ylim(0, max(mape * 1.2, 100))  # Definir limite superior um pouco maior que o MAPE para visualização

# Ajustar layout e salvar a imagem das métricas
plt.tight_layout()
plt.savefig('metrics_WMA.png')
plt.show()

print("Arquivo 'metrics_WMA.png' com as métricas de avaliação gerado com sucesso!")
