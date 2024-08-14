import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# Carregar o arquivo processado com as colunas timestamp, packets/s e real_label
data = pd.read_csv('results_with_labels.txt', sep=r'\s+', header=0, names=['timestamp', 'packets/s', 'real-label'], engine='python')

# Função para calcular WMA com janela deslizante
def calculate_wma(series, window_size, decimal_places=2):
    weights = np.arange(1, window_size + 1)
    wma = series.rolling(window=window_size, min_periods=1).apply(
        lambda values: round(np.dot(values, weights[-len(values):]) / weights[-len(values):].sum(), decimal_places),
        raw=True
    )
    return wma

def percentage_prediction(data, window_size, threshold_percentage):
    data['predict_p/s'] = calculate_wma(data['packets/s'], window_size)
    # Calcular limiares com base no na porcentagem de limiar
    upper_threshold = data['predict_p/s'] + (data['predict_p/s'] * threshold_percentage / 100)
    lower_threshold = data['predict_p/s'] - (data['predict_p/s'] * threshold_percentage / 100)
    # Adicionar a coluna de previsão
    data['predict-label'] = np.where((data['packets/s'] > upper_threshold) | (data['packets/s'] < lower_threshold), 1, 0)
    return data

def std_prediction(data, window_size, threshold_factor=2):
    data['predict_p/s'] = calculate_wma(data['packets/s'], window_size)
    # Calcular o desvio padrão da janela deslizante
    std_dev = data['predict_p/s'].rolling(window=window_size, min_periods=1).std()
    # Limiar superior e inferior com base no desvio padrão
    upper_threshold = data['predict_p/s']  + threshold_factor * std_dev
    lower_threshold = data['predict_p/s']  - threshold_factor * std_dev
    # Adicionar a coluna de previsão
    data['predict-label'] = np.where((data['packets/s'] > upper_threshold) | (data['packets/s'] < lower_threshold), 1, 0)
    return data

# Calcular a previsão por porcentagem
# data = percentage_prediction(data.copy(), window_size=10, threshold_percentage=10)

# Calcular a previsão por desvio padrão
data = std_prediction(data.copy(), window_size=10, threshold_factor=2)

# Calcular a matriz de confusão
y_true = data['real-label']
y_pred = data['predict-label']
conf_matrix = confusion_matrix(y_true, y_pred)
tn, fp, fn, tp = conf_matrix.ravel()




# Criar a visualização da matriz de confusão
fig, ax = plt.subplots(figsize=(8, 6))
conf_matrix_display = ConfusionMatrixDisplay(conf_matrix, display_labels=['Não', 'Sim'])

conf_matrix_display.plot(ax=ax,cmap='Blues', values_format='d', include_values=True)
plt.text(0.5, 0.1, f'FP: {fp}\nFN: {fn}\nVP: {tp}\nVN: {tn}', ha='center', va='center', fontsize=12, bbox=dict(facecolor='white', alpha=0.5))

# Adicionar legendas personalizadas
plt.title('Matriz de Confusão')
plt.xlabel('Ataques Preditos')
plt.ylabel('Ataques Reais')

# Salvar a matriz de confusão como imagem
plt.savefig('confusion_matrix.png')
plt.show()


# Salvar o arquivo com as novas colunas
data.to_csv('WMA_predicted.txt', sep='\t', index=False)

print("Arquivo Gerado com sucesso.")
