import requests
import base64
import json
import pandas

from datetime import datetime

class Utils:

    def getDate(self):
        now = datetime.now() # current date and time
        date_time = now.strftime("%Y%m%d_%H%M%S")
        return date_time

    #convierte  un JSON a DataFrame de Pandas
    def propertiesToDataFrame(self, properties)    :
        lista=[]
        lista.append(properties)
        return self.arrayToDataFrame(lista)

    #convierte un array en DataFrame de Panda
    def arrayToDataFrame(self, listProperties)    :
        df_tot = pandas.DataFrame()
        df_tot = df_tot.reset_index()
        df = pandas.DataFrame.from_dict(listProperties)
        df_tot = pandas.concat([df_tot,df])
        return df_tot

    #guarda el dataframe en un fichero CSV para poder ser tratable.
    def dataFrame_to_CSV(self, df, path, filename):
        df.to_csv(path+filename+".csv", sep=';')


class Tinsa:
    #Recupera todas las tasaciones del municipio
    def getTasacionesPorZona(self, codigo_municipio):
        url = "https://app.tinsa.es/es_ES/seo/tasaciones/"
        params = { 'codigo_municipio' : codigo_municipio , 'barrio': None }

        response = requests.post(url = url, data = params)
        message = response.text
        #tratamiento pq los datos vienen en hexadecimal
        base64_message = message
        base64_bytes = base64_message.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode('ascii')
        listProperties = json.loads(message)
        return listProperties

    # Recupera una tasación concreta
    def getTasacion(self, id):
        url = "https://app.tinsa.es/es_ES/seo/tasacion/"
        params = { 'id' : id , 'barrio': None }
        result = requests.post(url = url, data = params)
        property = json.loads(result.text)
        return property

    #Recupera los datos web de la última tasación realizada en el municipio
    def getUltimaTasacion(self, municipio):
        url = "https://www.tinsa.es/tasacion/"+municipio+"/"
        result = requests.post(url = url)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(result.text, 'html.parser')
        list_divs = soup.findAll('div', attrs={'id':'main'})

        for element_div in list_divs :
            list_p = element_div.findAll('p');
            for element_p in list_p:
                if len(element_p.get_text())>5:
                    texto_tasacion= element_p.get_text()

        return texto_tasacion





#indique aquí todos los municipios que debe descargar el programa.
municipios = [{'codigo_municipio': '1036' , 'municipio' : 'Malaga'},]


utils = Utils()
tinsa = Tinsa()

folder ="batch/data/" #destino de los ficheros donde se almacenará la información conseguida.

# Recorremos todos los municipios donde queremos realizar la obtención de datos.
for municipio in municipios:
    codigo_municipio = municipio['codigo_municipio']
    municipio = municipio['municipio']


    properties = tinsa.getTasacionesPorZona(codigo_municipio)
    df_properties = utils.arrayToDataFrame(properties)
    utils.dataFrame_to_CSV(df_properties,folder, utils.getDate()+"_"+codigo_municipio )

    #recupera los datos de la
    ultimaTasacion = tinsa.getUltimaTasacion(municipio)
    df_ultimatasacion = utils.propertiesToDataFrame(ultimaTasacion)
    utils.dataFrame_to_CSV(df_ultimatasacion,folder, "ultima_tasacion_"+ utils.getDate()+"_"+codigo_municipio )

    #para cada tasación en la zona, intentamos recuperar toda la información posible
    for property in properties:
        id =  property['data']['id']
        tasacion = tinsa.getTasacion(id)
        lista_tasacion =[]
        lista_tasacion.append(tasacion)
        df_tasacion = utils.propertiesToDataFrame(lista_tasacion)
        utils.dataFrame_to_CSV(df_tasacion,folder, codigo_municipio+"_"+id )
