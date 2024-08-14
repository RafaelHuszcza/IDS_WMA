from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import pandas as pd
# Carregar os dados com as previsões
data = pd.read_csv('WMA_predicted.txt', sep='\t')

# Calcular as métricas de classificação
accuracy = accuracy_score(data['real-label'], data['predict-label'])
precision = precision_score(data['real-label'], data['predict-label'])
recall = recall_score(data['real-label'], data['predict-label'])
f1 = f1_score(data['real-label'], data['predict-label'])


# Imprimir as métricas
print("Acurácia:", accuracy)
print("Precisão:", precision)
print("Recall:", recall)
print("F1-Score:", f1)
