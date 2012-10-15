#-*- coding: utf-8 -*-

import re
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk import bigrams, trigrams
import math


stopwords = nltk.corpus.stopwords.words('spanish')
tokenizer = RegexpTokenizer("[\w’]+", flags=re.UNICODE)


def freq(word, doc):
    return doc.count(word)


def word_count(doc):
    return len(doc)


def tf(word, doc):
    return (freq(word, doc) / float(word_count(doc)))


def num_docs_containing(word, list_of_docs):
    count = 0
    for document in list_of_docs:
        if freq(word, document) > 0:
            count += 1
    return 1 + count


def idf(word, list_of_docs):
    return math.log(len(list_of_docs) /
            float(num_docs_containing(word, list_of_docs)))


def tf_idf(word, doc, list_of_docs):
    return (tf(word, doc) * idf(word, list_of_docs))

#Compute the frequency for each term.
vocabulary = []
docs = {}
all_tips = []

s1 = """comentar empresa estadounidense spacex puso orbita domingo capsula dragon bordo cohete falcon 9 dirige estacion espacial internacional iss primera 12 misiones abastecimiento previstos contrato nasa lanzamiento realizado cabo canaveral florida sureste unidos 20h35 locales 00h35 gmt lunes cuenta atras registro problemas condiciones climaticas favorables trata segundo vuelo capsula tripulada dragon iss tras demostracion realizado mayo supuso primer amarre nave privada estacion espacial diez minutos despues lanzamiento dragon separo lanzador entro orbita minuto despues nave desplego dos antenas solares continuar viaje hacia iss previsto llegue miercoles dragon lleva bordo 455 km material nasa amarrara estacion ayuda brazo robotizado iss controlado dos seis astronautas encuentran plataforma espacial quedan hacer muchas cosas mientras guiamos acercamiento dragon hacia estacion espacial internacional lanzamiento sido perfecto exito celebro comunicado elon musk fundador propietario spacex material transporta capsula comida ropa herramientas esenciales tripulantes iss expedicion 33 compuesta dos estadounidenses japones tres rusos realicen experimentos cientificos regreso tierra 28 octubre dragon traera 333 kg material cientifico 229 kg material usado nasa espera spacex sociedades privadas puedan tomar relevo transbordadores espaciales registraron ultimo vuelo julio 2011 poder abastecer iss acuerdo contrato 1 600 millones dolares alcanzado nasa spacex debe realizar 12 vuelos estacion internacional cuatro anos trasladar total 20 toneladas material visto forma estan desarrollando acontecimientos pensamos podremos transportar unas 60 toneladas preciso sabado rueda prensa gwynne shotwell directora general spacex nasa tambien cerro contrato abastecimiento iss 1 900 millones dolares orbital sciences corporation efectuara primer vuelo pruebas proximos meses nueva base espacial costa virginia noreste agencia aeroespacial estadounidense selecciono recientemente spacex boeing sierra nevada desarrollar nave privada traslade personas hacia iss asi hacia destinos orbitales afp derechos reservados est prohibido tipo reproducci n autorizaci n"""
s2 = """ portada internacional paises hispanohablantes eduardo paes reelegido alcalde rio janeiro actual alcalde rio janeiro eduardo paes reelegido domingo cargo cuatro anos mas lograr 64 60 ciento votos comicios municipales celebrados hoy 100 ciento escrutinio finalizado editor ara 07 37 34 2012 10 08 agencia xinhua flash actual alcalde rio janeiro eduardo paes reelegido domingo cargo cuatro anos mas lograr 64 60 ciento votos comicios municipales celebrados hoy 100 ciento escrutinio finalizado paes candidato oficialista partido movimiento democratico brasileno pmdb supero segundo candidato mas votos marcelo freixo izquierdista partido socialista libertad psol obtuvo 28 15 ciento votos validos insuficientes forzar segunda vuelta candidato obtuvo tercer lugar resultados rodrigo maia opositor democratas dem hijo ex alcalde cesar maia recibio 2 93 ciento votos seguido diputado federal otavio leite partido social democracia brasilena psdb recibio 2 47 ciento segun cifras divulgadas tribunal superior electoral tse tras conocerse resultados eduardo paes prometio trabajar proximos anos tratar respeto ciudadano ademas elogiar politica seguridad impulsada gobernador regional sergio cabral devolvio paz muchas favelas tenia soberania asimismo quiso agradecer apoyo recibio presidenta brasilena dilma rousseff califico gran socia rio ex jefe luiz inacio lula da silva fundamental victoria urnas primeras elecciones hace cuatro anos paes 42 anos sera primer alcalde brasileno recibir ciudad juegos olimpicos ser rio janeiro sede olimpiadas 2016 ademas final mundial futbol 2014 copa confederaciones 2013 elecciones hoy 5 03 ciento poblacion carioca voto blanco 8 58 ciento nulo segunda mayor ciudad brasil tras sao paulo abstencion ascendio 20 45 ciento pesar voto obligatorio cifras mas altas grandes ciudades pais fi"""

documents = []

for tip in ([s1,s2]):
    tokens = tokenizer.tokenize(tip)

    bi_tokens = bigrams(tokens)
    tri_tokens = trigrams(tokens)
    tokens = [token.lower() for token in tokens if len(token) > 2]
    tokens = [token for token in tokens if token not in stopwords]

    bi_tokens = [' '.join(token).lower() for token in bi_tokens]
    bi_tokens = [token for token in bi_tokens if token not in stopwords]

    tri_tokens = [' '.join(token).lower() for token in tri_tokens]
    tri_tokens = [token for token in tri_tokens if token not in stopwords]

    final_tokens = []
    final_tokens.extend(tokens)
    final_tokens.extend(bi_tokens)
    final_tokens.extend(tri_tokens)
    docs[tip] = {'freq': {}, 'tf': {}, 'idf': {},
                        'tf-idf': {}, 'tokens': []}

    for token in final_tokens:
        #The frequency computed for each tip
        docs[tip]['freq'][token] = freq(token, final_tokens)
        #The term-frequency (Normalized Frequency)
        docs[tip]['tf'][token] = tf(token, final_tokens)
        docs[tip]['tokens'] = final_tokens

    vocabulary.append(final_tokens)

for doc in docs:
    for token in docs[doc]['tf']:
        #The Inverse-Document-Frequency
        docs[doc]['idf'][token] = idf(token, vocabulary)
        #The tf-idf
        docs[doc]['tf-idf'][token] = tf_idf(token, docs[doc]['tokens'], vocabulary)

#Now let's find out the most relevant words by tf-idf.
words = {}
for doc in docs:
    for token in docs[doc]['tf-idf']:
        if token not in words:
            words[token] = docs[doc]['tf-idf'][token]
        else:
            if docs[doc]['tf-idf'][token] > words[token]:
                words[token] = docs[doc]['tf-idf'][token]

    print doc
    for token in docs[doc]['tf-idf']:
        print token, docs[doc]['tf-idf'][token]

for item in sorted(words.items(), key=lambda x: x[1], reverse=True):
    print "%f <= %s" % (item[1], item[0])