from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from pymongo import MongoClient
import json
import re

#Conecta ao mongo
cliente = MongoClient('172.17.0.2', 27017)

#Cria database
db = cliente['pls']

#Adiciona Collection
pls = db.pls

# Mapeia a URL que contém os links das PLs de 2018
url = "https://www.al.sp.gov.br/alesp/projetos/?tipo=1&ano=2018"

# Requisicao da página
with uReq(url) as pagina:
    conteudo = pagina.read()

# Transforma a página em objetos manipuláveis
pagina_html = soup(conteudo, "html.parser")

# Filtra os links
lista_links = pagina_html.findAll("ul", {"class": "listaNP_itens"})

# Armazena os links em uma lista
lista_urls = []

for item in lista_links[0].find_all('a'):
    lista_urls.append("https://www.al.sp.gov.br{}".format(item['href']))

# Coleta as 50 primeiras pls
lista_dic = []

for item in range(50):
    with uReq(lista_urls[item]) as pagina:
        conteudo = pagina.read()

    html = soup(conteudo, "html.parser")

    div = html.findAll("div", {"class": "ativo", "id": "referencias"})

    tabela = div[0].table.tbody.find_all('td')

    pl = {}
    pl['um_legistativo'] = tabela[3].text.strip()
    pl['ementa'] = tabela[5].text.strip()
    pl['data'] = tabela[7].text.strip()
    pl['regime'] = tabela[9].text.strip()
    pl['autores'] = tabela[11].text.strip()
    pl['apoiadores'] = tabela[13].text.strip()
    pl['indexadores'] = tabela[15].text.strip().split(',')
    pl['etapa_atual'] = tabela[17].text.strip()

    lista_dic.append(pl)


pls.insert_many(lista_dic)

# Serializa o json em formato de string
json_data = json.dumps(lista_dic)

# Cria arquivo json
output = open("output.json", "w+")

# Escreve os dados no arquivo
output.write(json_data)

output.close()
