# Integrantes do Grupo

Rafael Machado, Luan Simões e Rafael Coelho

# README

Este documento descreve o processo para obter e processar os dados de `tcpdump` utilizados no projeto. Além disso descreve o processo de implementação do IDS utilizando o algorítimo WMA

## 1. Obtenção dos Dados

Para obter o arquivo `results.txt`, foi necessário baixar todos os dados do link fornecido:

[MIT - Dataset Week 2](https://archive.ll.mit.edu/ideval/data/1999/training/week2/index.html)

## 2. Processamento dos Arquivos

### Passos no WSL (Windows Subsystem for Linux)

O processo foi realizado utilizando o WSL (Windows Subsystem for Linux), permitindo a execução de comandos do Linux em um ambiente Windows.

1. **Preparação dos Arquivos**

   Após baixar os arquivos, cada arquivo referente a um dia da semana foi processado individualmente. Utilizou-se o comando `tcpstat` para processar cada arquivo `.tcpdump` e gerar arquivos de texto para cada dia da semana. O comando utilizado foi:

   ```bash
   tcpstat -r inside.tcpdump -o "%S %p\n" 60 > dia-da-semana.txt
   ```

O comando acima foi repetido para cada dia da semana, alterando o nome do arquivo de saída (`segunda.txt`, `terca.txt`, etc.).

2. **Agregação dos Dados**

   Para consolidar todos os arquivos diários em um único arquivo `results.txt`, utilizou-se o comando `cat`:

   ```bash
   cat segunda.txt terca.txt quarta.txt quinta.txt sexta.txt > results.txt
   ```

   Esse comando combina os arquivos de texto diários em um único arquivo chamado results.txt.

3. **Ajuste de Timestamp**

Nota-se que durante a coleta de dados com o `tcpstat %S`, o timestamp foi configurado para um intervalo em segundos após a `UNIX epoch`, e configurado para a time zone Americana/New York.

## 3. Adição da legenda de ataques Reais

1. **Obter os dados de ataques que ocorreram**
   Primeiramente foi necessário acessar o Link que contem os dados de ataques detectados e transcreve-los para um formato adequado para um script ler.
   [MIT - Dataset Week 2 - Detections List File](https://archive.ll.mit.edu/ideval/docs/detections_1999.html)
   Foi utilizado do ChatGPT para fazer essa transcrição do registro de 43 ataques.

2. **Inserir Dados de Ataques**
   Para inserir os dados de ataques no sistema, foi necessário seguir os seguintes passos:

   1. _Adição do Cabeçalho das Colunas_:

   - O arquivo `results.txt` deve conter os dados com duas colunas: `timestamp` e `packets/s`.
   - O cabeçalho das colunas foi adicionado para garantir que os dados sejam corretamente identificados e processados.

   2. _Formatação dos Dados_:

   - Os dados de ataques foram formatados em uma lista contendo pares de data e hora. Cada par é convertido em um timestamp Unix ajustado para o timezone 'America/New_York'.
   - Esta lista é então utilizada para comparar com os timestamps presentes no arquivo `results.txt`.

   3. _Conversão de Timestamps_:

      - O código utiliza a função `to_unix_timestamp` para converter as datas e horas dos ataques em timestamps Unix.
      - Esses timestamps são então utilizados para verificar se o timestamp de cada entrada em `results.txt` está dentro de um intervalo de 60 segundos de algum dos timestamps de ataque.

   4. _Marcando os Ataques_:
      - Para cada linha do arquivo `results.txt`, o código verifica se o timestamp está dentro do intervalo de 60 segundos de qualquer ataque.
      - Se um ataque é identificado dentro do intervalo, a coluna `real-label` é marcada como 1; caso contrário, é marcada como 0.

## 4. Implementação do IDS WMA

Neste Etapa é feita a implementação do Sistema de Detecção de Intrusões (IDS) usando o algoritmo de Média Móvel Ponderada (WMA) para prever a quantidade de pacotes por segundo e identificar possíveis ataques.

1.  **Carregamento dos Dados**: O arquivo `results_with_labels.txt` é carregado, contendo as colunas `timestamp`, `packets/s`, e `real-label`. Esse arquivo já foi processado para incluir rótulos reais de ataque.

2.  **Função `calculate_wma`**: Esta função calcula a Média Móvel Ponderada (WMA) para uma série de dados usando uma janela deslizante. O cálculo é feito com base na fórmula:

\[
\text{WMA} = \frac{\sum*{i=1}^{n} (w_i \cdot v_i)}{\sum*{i=1}^{n} (w_i)}
\]

onde \( w_i \) são os pesos e \( v_i \) são os valores da série de dados.

3.  **Aplicação do WMA**: O WMA é aplicado à coluna `packets/s` com uma janela deslizante de 10 elementos. O valor previsto é arredondado para duas casas decimais para maior precisão.

    _Nota sobre a Janela Deslizante_: No início da série de dados, onde o número de elementos é menor que o tamanho da janela (10 elementos neste caso), o WMA ainda é calculado. Isso ocorre porque a função `rolling` do Pandas, quando configurada com `min_periods=1`, permite o cálculo da média móvel com o número disponível de elementos na janela. Portanto, mesmo com menos de 10 elementos, o WMA é calculado usando todos os elementos disponíveis e pesos proporcionais.

4.  **Definição dos Limiares (threshold)**: Os limiares de ataque são calculados com base nos valores previstos pelo WMA, utilizando duas abordagens distintas:

    - **Definição Percentual**:

      - **Limiar Superior**: 110% do valor previsto pelo WMA.

      Limiares de 10% proporcionam um equilíbrio razoável entre detectar ataques reais e evitar a classificação errônea de comportamentos normais como ataques.

    - **Definição por Desvio Padrão**:

      - **Limiar Superior**: Valor previsto pelo WMA mais o desvio padrão da janela deslizante multiplicado por um fator(4).

      A abordagem baseada em desvio padrão ajusta os limiares de acordo com a variabilidade dos dados, oferecendo maior flexibilidade para capturar variações na série temporal e adaptar-se a comportamentos anômalos. O fator utilizado na multiplicação do desvio padrão pode ser ajustado conforme a necessidade para melhorar a detecção de ataques e reduzir falsos positivos.

Essas duas abordagens fornecem diferentes formas de calibrar os limiares de detecção, permitindo a adaptação às características específicas dos dados e aos requisitos do sistema de monitoramento.

5.  **Previsão de ataque**: Se o valor real de `packets/s` estiver fora dos limiares definidos, o rótulo previsto é definido como 1 (indicando um possível ataque); caso contrário, o rótulo é definido como 0 (sem ataque).

6.  **Arquivo de Saída**: Os resultados são salvos em um arquivo chamado `WMA_predicted.txt`, que inclui as colunas originais e as novas colunas `predict_p/s` e `predict-label`.

## 5. Matriz de Confusão

A matriz de confusão é uma ferramenta fundamental para avaliar o desempenho do sistema de detecção de intrusões (IDS). Ela mostra a relação entre os valores reais e preditos, permitindo a análise dos erros do modelo e a avaliação de seu desempenho.
OBS: A geração ca matriz é feita ao fim do código do IDS.

1. **Geração da Matriz de Confusão**

Para gerar matriz de confusão, utilizamos as colunas `real-label` (rótulo real) e `predict-label` (rótulo predito) dos dados processados. A matriz é calculada utilizando a função `confusion_matrix` da biblioteca `sklearn`.

2. **Análise da Matriz de Confusão**
   A matriz de confusão é composta por quatro principais métricas:

- _Verdadeiro Negativo (TN)_: Número de eventos corretamente identificados como não ataque.
- _Falso Positivo (FP)_: Número de eventos incorretamente classificados como ataque quando não são.
- _Falso Negativo (FN)_: Número de eventos incorretamente identificados como não ataque quando são.
- _Verdadeiro Positivo (TP)_: Número de eventos corretamente identificados como ataque.

3. **Geração da Imagem**

A matriz de confusão é visualizada usando `matplotlib` e a classe `ConfusionMatrixDisplay` da biblioteca `sklearn`. A visualização inclui as métricas de TN, FP, FN e TP, permitindo uma análise detalhada do desempenho do IDS. Além disso a imagem é baixada e pode ser compartilhada.

## 6. Implementação das Métricas de Avaliação para o WMA

Para avaliar a eficácia das predições do tráfego de rede, duas métricas de erro foram implementadas: **Erro Quadrático Médio Normalizado (NMSE)** e **Erro Percentual Absoluto Médio (MAPE)**. Essas métricas são essenciais para medir a precisão das previsões e comparar o desempenho do modelo. No caso em questão ele valida a predição de valores ou seja, predict_p/s em comparação a packets/s.

### 5.1. Erro Quadrático Médio Normalizado (NMSE)

O NMSE é definido pela fórmula:

\[ \text{NMSE} = \frac{1}{r^2} \cdot \frac{1}{N} \sum\_{t=1}^{N} (X_t - \hat{X}\_t)^2 \]

Onde:

- \( r^2 \) é a variância da série temporal durante a duração da previsão.
- \( X_t \) é o valor observado da série temporal no tempo \( t \).
- \( \hat{X}\_t \) é o valor previsto no tempo \( t \).
- \( N \) é o número total de valores previstos.

O NMSE avalia a precisão da previsão comparando com um preditor trivial que usa a média da série temporal. Se o NMSE = 1, o desempenho do preditor é pior do que o do preditor trivial. Se NMSE = 0, o preditor é perfeito.

### 5.2. Erro Percentual Absoluto Médio (MAPE)

O MAPE é definido pela fórmula:

\[ \text{MAPE} = \frac{1}{N} \sum\_{t=1}^{N} \left| \frac{X_t - \hat{X}\_t}{X_t} \right| \times 100 \text{ (se } X_t > 0) \]

\[ \text{MAPE} = \frac{1}{N} \sum\_{t=1}^{N} \left| \frac{X_t - \hat{X}\_t}{\bar{X}} \right| \times 100 \text{ (caso contrário)} \]

Onde:

- \( X_t \) é o valor observado no tempo \( t \).
- \( \hat{X}\_t \) é o valor previsto no tempo \( t \).
- \( \bar{X} \) é a média da série temporal (usada se \( X_t = 0 \)).
- \( N \) é o número total de valores na série temporal.

O MAPE expressa o erro como uma porcentagem dos valores reais. Se o MAPE é zero, a previsão é perfeita.
