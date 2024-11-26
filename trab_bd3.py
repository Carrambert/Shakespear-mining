# -*- coding: utf-8 -*-
"""Trab BD3

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1_GJYbsi9S0did3cjiWdmgV_hc5OxSp7g
"""

#Instalar as dependências

#Instalar Java 8
!apt-get install openjdk-8-jdk-headless -qq > /dev/null

#Realizar o download do Spark
!wget -q https://dlcdn.apache.org/spark/spark-3.4.3/spark-3.4.3-bin-hadoop3.tgz

#Descompartar o arquivo baixado
!tar xf spark-3.4.3-bin-hadoop3.tgz

#Instalando a findspark
!pip install -q findspark

! pip install nltk pandas
! python -m nltk.downloader wordnet omw-1.4

#Configurar as variáveis de ambiente

#Importando a biblioteca os
import os

#Definindo a variável de ambiente do Java
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"

#Definindo a variável de ambiente do Spark
os.environ["SPARK_HOME"] = "/content/spark-3.4.3-bin-hadoop3"

#Importando a findspark
import findspark

#Iniciando o findspark
findspark.init('spark-3.4.3-bin-hadoop3')

from pyspark.sql.functions import regexp_replace, col, lower, split, explode, count, translate, udf, monotonically_increasing_id
from pyspark.ml.feature import StopWordsRemover, Tokenizer
import string
import pandas as pd
from pyspark.sql.functions import pandas_udf, PandasUDFType
from pyspark.sql.types import ArrayType, StringType, IntegerType
from pyspark.sql import SparkSession
import time

# iniciar uma sessão local
from pyspark.sql import SparkSession
import time
sc = SparkSession.builder.master('local[*]').config('spark.ui.port', '4050').getOrCreate()

import nltk

nltk.download("punkt")

arquivo = "Shakespeare_alllines.txt"


with open(arquivo, 'r') as file:

    lines = file.readlines()


shows = ",".join(lines).replace('"', "").replace("'", "").replace('“', "").replace('”', "").replace("--", "").replace("SCENE", "").replace(".", "").replace("ACT II", "").replace("ACT III", "").replace("ACT IV", "").split("ACT I")
print(shows[1:10])
#data = sc.read.text(arquivo)

import string
nltk.download('stopwords')
from nltk.corpus import stopwords
play1 = nltk.word_tokenize(shows[1])

tokenized_plays = [nltk.word_tokenize(play) for play in shows]

stop_words = set(stopwords.words('english'))

def remove_punctuation_and_stopwords(tokens):
    return [word for word in tokens if word not in string.punctuation and word.lower() not in stop_words]


cleaned_plays = [remove_punctuation_and_stopwords(tokens) for tokens in tokenized_plays]
print(cleaned_plays[1])

from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
nltk.download('wordnet')
nltk.download('omw-1.4')


lemmatizer = WordNetLemmatizer()


def remove_punctuation_stopwords_and_lemmatize(tokens):
    return [lemmatizer.lemmatize(word) for word in tokens if word not in string.punctuation and word.lower() not in stop_words]


cleaned_plays = [remove_punctuation_stopwords_and_lemmatize(tokens) for tokens in tokenized_plays]

from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk import pos_tag
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('averaged_perceptron_tagger')


lemmatizer = WordNetLemmatizer()

def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN




def remove_punctuation_stopwords_and_classify(tokens, idx):

    filtered_tokens = [word for word in tokens if word not in string.punctuation and word.lower() not in stop_words]


    pos_tagged_tokens = pos_tag(filtered_tokens)


    classified_tokens = [(word, get_wordnet_pos(tag), idx) for word, tag in pos_tagged_tokens]

    return classified_tokens


classified_plays_with_index = [remove_punctuation_stopwords_and_classify(tokens, idx) for idx, tokens in enumerate(tokenized_plays)]

print(classified_plays_with_index[1])

#Adequando o data frame

juntando = [tupla for array in classified_plays_with_index for tupla in array]
tabela = sc.createDataFrame(pd.DataFrame(juntando, columns=['PALAVRA', 'TIPO', 'HISTORIA']))

#Mostrando a Tabela
tabela.show()

#Testando query
tabela.createOrReplaceTempView("tabela_temp")
resultado = sc.sql("SELECT * FROM tabela_temp WHERE historia = 1")
resultado.show()

#Exercício
#PERCENTUAL DA FREQUENCIA DA PALAVRA (PESO) POR PALAVRA E PELA HISTÓRIA
total_palavras = tabela.count()
resultado = sc.sql("SELECT palavra, historia,  COUNT(*) AS frequencia,(COUNT(*) * 100.0 / {}) AS percentual FROM tabela_temp GROUP BY palavra, historia Order By historia, frequencia Desc".format(total_palavras))
resultado.show()

#Mostrando pelo tipo de palavra, onde quase 60% é de substantivo.
resultado = sc.sql("SELECT TIPO,  COUNT(*) AS frequencia,(COUNT(*) * 100.0 / {}) AS percentual FROM tabela_temp GROUP BY TIPO Order By frequencia Desc".format(total_palavras))
resultado.show()

resultado = sc.sql("SELECT PALAVRA,  COUNT(*) QUANTIDADE FROM tabela_temp WHERE UPPER(TIPO) LIKE 'N' Group By PALAVRA ORDER BY COUNT(*) DESC" )
resultado.show()