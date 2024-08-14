import pandas as pd
from datetime import datetime
import pytz
import re

# Função para converter data e hora em timestamp Unix ajustado para o timezone América/New_York
def to_unix_timestamp(date_str, time_str):
    datetime_str = f"{date_str} {time_str}"
    dt = datetime.strptime(datetime_str, "%m/%d/%Y %H:%M:%S")

    # Definir o timezone 'America/New_York'
    ny_tz = pytz.timezone('America/New_York')
    
    # Localizar o datetime no timezone especificado
    dt = ny_tz.localize(dt)
    
    # Converter diretamente para timestamp Unix considerando o timezone local
    return int(dt.timestamp())

# Função para verificar se o timestamp de ataque está dentro do intervalo de 60 segundos do timestamp na coluna
def is_attack_in_interval(timestamp, attack_timestamps):
    return any(timestamp <= attack_timestamp <= timestamp + 59 for attack_timestamp in attack_timestamps)

# Lista de ataques
attack_data = [
    ("03/08/1999", "08:01:01"), ("03/08/1999", "08:50:15"), ("03/08/1999", "09:39:16"),
    ("03/08/1999", "12:09:18"), ("03/08/1999", "15:57:15"), ("03/08/1999", "17:27:13"),
    ("03/08/1999", "19:09:17"), ("03/09/1999", "08:44:17"), ("03/09/1999", "09:43:51"),
    ("03/09/1999", "10:06:43"), ("03/09/1999", "10:54:19"), ("03/09/1999", "11:49:13"),
    ("03/09/1999", "14:25:16"), ("03/09/1999", "13:05:10"), ("03/09/1999", "16:11:15"),
    ("03/09/1999", "18:06:17"), ("03/10/1999", "12:02:13"), ("03/10/1999", "13:44:18"),
    ("03/10/1999", "15:25:18"), ("03/10/1999", "20:17:10"), ("03/10/1999", "23:23:00"),
    ("03/10/1999", "23:56:14"), ("03/11/1999", "08:04:17"), ("03/11/1999", "09:33:17"),
    ("03/11/1999", "10:50:11"), ("03/11/1999", "11:04:16"), ("03/11/1999", "12:57:13"),
    ("03/11/1999", "14:25:17"), ("03/11/1999", "15:47:15"), ("03/11/1999", "16:36:10"),
    ("03/11/1999", "19:16:18"), ("03/12/1999", "08:07:17"), ("03/12/1999", "08:10:40"),
    ("03/12/1999", "08:16:46"), ("03/12/1999", "09:18:15"), ("03/12/1999", "11:20:15"),
    ("03/12/1999", "12:40:12"), ("03/12/1999", "13:12:17"), ("03/12/1999", "14:06:17"),
    ("03/12/1999", "14:24:18"), ("03/12/1999", "15:24:16"), ("03/12/1999", "17:13:10"),
    ("03/12/1999", "17:43:18")
]

# Converter ataques para timestamps
attack_timestamps = [to_unix_timestamp(date, time) for date, time in attack_data]

# Função para extrair o timestamp numérico da coluna
def extract_numeric_timestamp(value):
    # Usar regex para extrair a parte numérica
    match = re.match(r'(\d+)', value)
    return int(match.group(1)) if match else None

# Carregar o arquivo results.txt
data = pd.read_csv('results.txt', sep='\t', header=None, names=['timestamp', 'packets/s'])

# Adicionar a coluna 'real-label' com valores iniciais de 0
data['real-label'] = data['timestamp'].apply(lambda x: 1 if is_attack_in_interval(extract_numeric_timestamp(x), attack_timestamps) else 0)

# Salvar o resultado em um novo arquivo
data.to_csv('results_with_labels.txt', sep='\t', index=False)

print("Arquivo Gerado com sucesso.")
