#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import pdfplumber
import pandas as pd
import shutil
import plotly.express as px
from pdfminer.high_level import extract_text
from tqdm import tqdm
import os
import glob
from datetime import datetime, timedelta
import urllib.request
from tqdm import tqdm
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Descarga lo que falta desde el ultimo informe a la fecha

# In[2]:


#Entre todos ls informes en la carpeta INFORME_DIARIO busca el mas reciente
todos_los_diarios=glob.glob(os.path.join(os.getcwd(), "INFORME_DIARIO","*.pdf"))
numeros_informes=[]
for file in todos_los_diarios:
    numero_informe=file.split("/")[-1].split("_")[-1].replace(".pdf","")
    numero_informe=int(numero_informe)
    numeros_informes.append(numero_informe)
ultimo_informe = max(numeros_informes)


# In[3]:


#Lee el ultimo informe y extrae dia, mes anio y "variable" desconocida
full_informe=glob.glob(os.path.join(os.getcwd(), "INFORME_DIARIO",f"*{ultimo_informe}.pdf"))
dia=full_informe[0].split("/")[-1].split("_")[2]
mes=full_informe[0].split("/")[-1].split("_")[1]
anio=full_informe[0].split("/")[-1].split("_")[0]
variable=int(full_informe[0].split("/")[-1].split("_")[-2])


# In[4]:


#generar lista de dias sobre los que buscar informes

def get_dates(anio,mes,dia):
    # Define the desired date format
    date_format = "%Y/%-m_%-d"
    # Initialize an empty list to store the dates
    dates = []
    # Get the current date
    end_date = datetime.today()
    # Format the input year, month, and day into a date string
    date = f"{dia.zfill(2)}_{mes.zfill(2)}_{anio}"
    # Convert the formatted date string into a datetime object
    start_date=datetime.strptime(date,"%d_%m_%Y")
    while start_date <= end_date:
        # Append the formatted date string to the list
        dates.append(start_date.strftime(date_format))
        # Increment the start_date by one day
        start_date += timedelta(days=1)
    return dates
# Call the get_dates function to populate the iterable_dates variable
iterable_dates = get_dates(anio,mes,dia)
iterable_dates


# In[5]:


# download PDF files from a given URL pattern for a range of dates, variables, and final values. The downloaded files are saved in "descargas"
# Specify the directory to save the downloaded files
directorio_descargas=os.path.join(os.getcwd(),"descargas")
# Iterate over the iterable_dates
for day in iterable_dates:
    # Iterate over the range of variables
    for k in range(variable,variable+5):
        # Iterate over the range of final values
        for final in range(ultimo_informe,ultimo_informe+(len(iterable_dates)*10)):
            try:
                # Create the URL for the PDF file
                url = f"https://iamcmediamanager.prod.ingecloud.com/mediafiles/iamc/{day}/0/11/{k}/{final}.pdf"
                # Generate a file name based on the URL
                file_name = url.split("https://iamcmediamanager.prod.ingecloud.com/mediafiles/iamc/")[-1].replace("/","_")
                # Download the file and save it in the specified directory
                urllib.request.urlretrieve(url, os.path.join(directorio_descargas, file_name))                            
                print(url)
            except:pass


# Busca palabras claves en los informes para identificar los informes diarios y resumenes semanales y backupea en pdfs_backup

# In[6]:


# Obtener el directorio actual
directorio_actual = os.getcwd()
#encontrar la carpeta INFORME_DIARIO
carpeta_inf_diarios = os.path.join(directorio_actual, "INFORME_DIARIO")
#encontrar la carpeta backup
carpeta_backup = os.path.join(directorio_actual, "pdfs_backup")

# Definir la cadenas a buscar (esta es una cadena que solo esta en los informes diarios)
cadenas = ["Rueda del","Ruedas del"]

#encontrar todos los archivos en la carpeta de descargas
archivos = os.listdir(directorio_descargas)

for archivo in tqdm(archivos):
    if archivo.endswith('.pdf'):
        with open(os.path.join(directorio_descargas, archivo), 'rb') as f:
            # Abre el archivo en modo de lectura binaria para poder procesar el contenido del PDF
            pdf_reader = extract_text(f)
            # Verifica si alguna de las cadenas está presente en el texto del PDF
            if any(re.search(rf"\b{re.escape(cadena)}\b", pdf_reader) for cadena in cadenas): 
                # Si alguna de las cadenas está presente en el texto del PDF, se copia el archivo a la carpeta INFORME_DIARIO
                origen = os.path.join(directorio_descargas, archivo)
                destino = os.path.join(carpeta_inf_diarios, archivo)
                shutil.copy(origen, destino)
            else:
                # Si ninguna de las cadenas está presente en el texto del PDF, se mueve el archivo a la carpeta de backup
                shutil.move(os.path.join(directorio_descargas, archivo),os.path.join(carpeta_backup,archivo))


# Extrae de los informes diarios nuevos la informacion de las obligaciones negociables en ley extranjera

# In[7]:


def convert_pdf_to_list(pdf_file_path):
    hoja = []
    # Abre el archivo PDF utilizando pdfplumber y lo asigna al objeto 'pdf'
    with pdfplumber.open(pdf_file_path) as pdf:        
        # Itera sobre cada página del PDF
        for page in pdf.pages:            
            # Extrae el texto de la página actual del PDF
            text = page.extract_text()            
            # Divide el texto en líneas utilizando el carácter de salto de línea ('\n')
            lines = text.split('\n')            
            # Agrega la lista de líneas al objeto 'hoja'
            hoja.append(lines)
    try:
        # Intenta acceder al contenido de la página 7 del PDF desde la línea después de 'Obligaciones Negociables Ley extranjera' hasta la línea anterior a 'Tipo de Cambio Peso-Dólar(*)'
        contenido_on = hoja[7][hoja[7].index('Obligaciones Negociables Ley extranjera') + 2:hoja[7].index('Tipo de Cambio Peso-Dólar(*)')]
        # Devuelve el contenido obtenido de la página 7
        return contenido_on
    except:
        try:
            # Si en la pagina 7 no encontró las líneas objetivo, intenta acceder al contenido de la página 8
            contenido_on = hoja[8][hoja[8].index('Obligaciones Negociables Ley extranjera') + 2:hoja[8].index('Tipo de Cambio Peso-Dólar(*)')]
            # Devuelve el contenido obtenido de la página 8
            return contenido_on
        except:
            # Si no se puede acceder al contenido de ninguna de las páginas, imprime la ruta del archivo PDF
            print(pdf_file_path)


# In[8]:


#levanta todos los archivos de la carpeta descargas y los convierte a una lista de listas en python, seleccionando solo la seccion de ONs 
ons=[]
for i in tqdm(glob.glob(os.path.join(directorio_descargas,"*.pdf"))):
    contenido_on=convert_pdf_to_list(i)
    ons.append(contenido_on)


# Convierte la información a un pandas df. AL FINAL LO GUARDA EN UN CSV!

# In[9]:


#Este código define una función llamada txt_a_df que toma dos argumentos: contenido_on y tickers. La función crea un DataFrame vacío con columnas predefinidas. 
#Luego, se realiza un bucle para procesar el contenido de contenido_on, que se espera que sea una lista de texto. Para cada fila en contenido_on, se realiza otro bucle para cada ticker en la lista tickers. 
#Si el ticker se encuentra en la fila actual, se realiza un conjunto de operaciones para extraer diferentes valores de la fila y asignarlos a variables específicas. 
#Estos valores se utilizan para construir una nueva fila de datos, que se agrega al DataFrame utilizando df.loc[len(df)] = new_row. Finalmente, se devuelve el DataFrame resultante. 
#Si se produce una excepción durante el procesamiento, se imprime un mensaje de error.

#Las variables definidas en una larga columna abajo iteran cada fila de la tabla de obligaciones negociables para extraer los valores de cada ticker en cada informe diario

def txt_a_df(contenido_on,tickers):
    df = pd.DataFrame(columns = ["TICKER","EMISOR","VENCIMIENTO","AMORTIZACION","CUPON_DE_RENTA","PROX_VENC","VR","COTIZACION","FECH_ULT_COT","RENTA_ANUAL","INT_CORRIDOS_C100vn","YIELD_ANUAL","VALOR_TECNICO_C100vn",
                               "PARIDAD_PERC","TIR_ANUAL","DM","PPV"])
    try:
        for row in contenido_on:

                for ticker in tickers:
                    if ticker in row:
                        b=row.split(ticker)
                        if len(b)==2:
                            TICKER=ticker
                            EMISOR=b[0]
                            VENCIMIENTO=b[1].split()[0]
                            if re.search(fr"{VENCIMIENTO}(.*?)(?:Sem\.|Trim\.)", b[1]):
                                    try:AMORTIZACION = re.search(fr"{VENCIMIENTO}(.*?)(?:Sem\.|Trim\.)", b[1]).group(1).strip()
                                    except:pass
                            c=b[1].split(AMORTIZACION)[1]
                            d=c.split()
                            e = []
                            i = 0
                            while i < len(d):
                                if d[i] == 'Tasa' and i < len(d) - 1:
                                    e.append(d[i] + ' ' + d[i+1])
                                    i += 1
                                else:
                                    e.append(d[i])
                                i += 1

                            CUPON_DE_RENTA=e[0]
                            PROX_VENC=e[1]
                            VR=e[3]
                            COTIZACION=e[4]
                            FECH_ULT_COT=e[5]
                            RENTA_ANUAL=e[6]
                            INT_CORRIDOS_C100vn=e[7]
                            YIELD_ANUAL=e[8]
                            VALOR_TECNICO_C100vn=e[9]
                            PARIDAD_PERC=e[10]
                            TIR_ANUAL=e[11]
                            DM=e[12]
                            PPV=e[13]
                            new_row=[TICKER,EMISOR,VENCIMIENTO,AMORTIZACION,CUPON_DE_RENTA,PROX_VENC,VR,COTIZACION,FECH_ULT_COT,RENTA_ANUAL,INT_CORRIDOS_C100vn,YIELD_ANUAL,VALOR_TECNICO_C100vn,PARIDAD_PERC,TIR_ANUAL,DM,PPV]
                            df.loc[len(df)]=new_row
    except:
        print("'NoneType' object is not iterable")

    return df


# In[10]:


#Consigue el csv mas reciente, en la proxima celda lo junta con los nuevos informes diarios
files = glob.glob(os.path.join(os.getcwd(), "cotizaciones_historicas_al_*.csv"))
csv_dates=[]
for file in files:
    file=file.replace(os.path.join(os.getcwd(), "cotizaciones_historicas_al_"),"").replace(".csv","")
    csv_dates.append(file)
date_objects = [datetime.strptime(date, '%d-%m-%Y') for date in csv_dates]

# Get the most recent date
most_recent_date = max(date_objects)
date_without_hour_string = most_recent_date.strftime('%d-%m-%Y')

#Lee el csv mas reciente y lo convierte en un pandas df
previous_csv=pd.read_csv(f"cotizaciones_historicas_al_{date_without_hour_string}.csv")


# In[11]:


#Junta el csv que encontro arriba con la informacion que consiguio de los nuevos pdf de informes diarios

from datetime import date
master_df = pd.DataFrame(columns = ["TICKER","EMISOR","VENCIMIENTO","AMORTIZACION","CUPON_DE_RENTA","PROX_VENC","VR","COTIZACION","FECH_ULT_COT","RENTA_ANUAL","INT_CORRIDOS_C100vn","YIELD_ANUAL","VALOR_TECNICO_C100vn",
                                "PARIDAD_PERC","TIR_ANUAL","DM","PPV"])
tickers=["PTSTO","RCC9O","YPCUO","CAC2O","CP17O","YCA6O","TLC5O","YMCHO","MTCGO","TLC1O","MGC9O","PNDCO","GNCXO","RCCJO","IRCFO","YMCIO","YMCJO"]

for contenido_on in ons:
    df=txt_a_df(contenido_on,tickers)
    master_df=pd.concat([master_df,df])

master_df=pd.concat([previous_csv,master_df]).drop_duplicates()

today=date.today().strftime("%d-%m-%Y")
csv_name=f"cotizaciones_historicas_al_{today}.csv"
master_df = master_df[master_df.columns.drop(list(master_df.filter(regex='Unnamed')))]
master_df.to_csv(csv_name)


# In[12]:


#VACIA LA CARPETA DESCARGAS

# Get a list of all files in the folder
files = os.listdir(directorio_descargas)

# Iterate over the files and delete them one by one
for file in files:
    file_path = os.path.join(directorio_descargas, file)
    if os.path.isfile(file_path):
        os.remove(file_path)


# Plotea las TIRs de todos los tickers

# In[13]:


master_df=pd.read_csv(csv_name)

# Custom mapping for Spanish month names
month_mapping = {
    'Ene': 'Jan',
    'Feb': 'Feb',
    'Mar': 'Mar',
    'Abr': 'Apr',
    'May': 'May',
    'Jun': 'Jun',
    'Jul': 'Jul',
    'Ago': 'Aug',
    'Sep': 'Sep',
    'Oct': 'Oct',
    'Nov': 'Nov',
    'Dic': 'Dec'
}
# Reemplaza los nombres de los meses en español en la columna 'FECH_ULT_COT' por los equivalentes en inglés utilizando el mapeo
master_df["FECH_ULT_COT"]=master_df["FECH_ULT_COT"].replace(month_mapping, regex=True)

# Convierte la columna 'FECH_ULT_COT' al formato de fecha y hora de pandas ('datetime') utilizando el formato especificado
master_df['FECH_ULT_COT'] = pd.to_datetime(master_df['FECH_ULT_COT'], format='%d-%b-%y')
# Elimina el último carácter de cada valor en la columna 'TIR_ANUAL' para eliminar el símbolo de porcentaje
master_df['TIR_ANUAL'] = master_df['TIR_ANUAL'].str[:-1]
# Convierte los valores en la columna 'TIR_ANUAL' a números de punto flotante (float), y asigna None a los valores vacíos o nulos
master_df['TIR_ANUAL'] = master_df['TIR_ANUAL'].apply(lambda x: float(x) if (x and x!="**") else None)
# Crea un gráfico de dispersión utilizando los datos del DataFrame 'master_df', utilizando la columna 'FECH_ULT_COT' como eje x, la columna 'TIR_ANUAL' como eje y, y la columna 'TICKER' para asignar colores a los puntos en el gráfico
fig = px.scatter(master_df, x='FECH_ULT_COT', y="TIR_ANUAL",color="TICKER")
# Show the plot
#fig.show()


# Plotea, para cada ticker comprado, los graficos de ratios

# In[14]:


#Escribir en forma de lista todos los tickers comprados
comprado=["YCA6O"]


# In[15]:


cocientes=pd.DataFrame(columns=["FECH_ULT_COT"])
#agarra el df de antes (el master que tiene toda la info de los tickers historicos y hace una pivot donde pone los tickers en las columnas, las fechas en las filas y los valores de tir en los valores)
tirs=pd.pivot_table(master_df, values="TIR_ANUAL", index="FECH_ULT_COT", columns="TICKER", aggfunc='mean', fill_value=None).reset_index()
"""
#Para cada ticker
for ticker in tickers:
    #Y parada ticker comprado
    for compra in comprado:
        #crea un df vacio que solo tiene la columna FECH_ULT_COT
        cocientes=pd.DataFrame(columns=["FECH_ULT_COT"])
        #Y la llena con las fechas de las que tenemos informacion de tirs
        cocientes["FECH_ULT_COT"]=tirs["FECH_ULT_COT"]
        #Crea una columna llamada ticker/ticker_comprado que contiene ese cociente
        cocientes[f"{ticker}/{compra}"]=tirs[ticker]/tirs[compra]
        # Calcula el promedio del cociente
        cocientes['Mean']= (cocientes[f"{ticker}/{compra}"]).mean()
        # Calcula la media + 2 desvios estándar
        cocientes['Mean-2DE']= cocientes['Mean']- (2 * cocientes[f"{ticker}/{compra}"].std())
        # Calcula la media - 2 desvios estándar
        cocientes['Mean+2DE']= cocientes['Mean'] + (2 * cocientes[f"{ticker}/{compra}"].std())
        #Si el cociente de hoy es mas grande que el promedio historico + 2 DE, entonces imprime el gráfico clave con una alerta
        if cocientes[f"{ticker}/{compra}"].iloc[-1]>cocientes['Mean+2DE'].iloc[-1]:
            alert="###### OPORTUNIDAD DE COMPRA ###### OPORTUNIDAD DE COMPRA ###### OPORTUNIDAD DE COMPRA ######"
            # Create the scatter plot using Plotly Express
            fig = px.scatter(cocientes, x='FECH_ULT_COT', y=['Mean-2DE','Mean+2DE',f"{ticker}/{compra}"],title=f"{ticker}/{compra}    {alert}")
            # Show the plot
            fig.show()
            
        else: alert=""
"""        

all_figures = []
titles=[]
for ticker in tickers:
        #crea un df vacio que solo tiene la columna FECH_ULT_COT
        cocientes=pd.DataFrame(columns=["FECH_ULT_COT"])
        #Y la llena con las fechas de las que tenemos informacion de tirs
        cocientes["FECH_ULT_COT"]=tirs["FECH_ULT_COT"]
        #Crea una columna llamada ticker/ticker_comprado que contiene ese cociente
        cocientes[f"TIR"]=tirs[ticker]
        # Calcula el promedio del cociente
        cocientes['Mean']= cocientes["TIR"].mean()
        # Calcula la media + 2 desvios estándar
        cocientes['Mean-2DE']= cocientes['Mean']- (2 * cocientes["TIR"].std())
        # Calcula la media - 2 desvios estándar
        cocientes['Mean+2DE']= cocientes['Mean'] + (2 * cocientes["TIR"].std())
        df["FECH_ULT_COT"]=pd.to_datetime(df['FECH_ULT_COT'])
        alert="###### OPORTUNIDAD DE COMPRA ###### OPORTUNIDAD DE COMPRA ###### OPORTUNIDAD DE COMPRA ######"
        fig = px.scatter(cocientes, x='FECH_ULT_COT', y=['Mean-2DE','Mean+2DE',"TIR"],title=f"{ticker}    {alert}")
        all_figures.append(fig)
        titles.append(f"TIR de {ticker}")
        #Si el cociente de hoy es mas grande que el promedio historico + 2 DE, entonces imprime una alerta en el titulo del gráfico
        if cocientes["TIR"].iloc[-1]>cocientes['Mean+2DE'].iloc[-1] and today in df['FECH_ULT_COT'].dt.date.values:
            fig.show()

# Crea un subploteo con una sola columna para poner los gráficos uno debajo del otro
fig_subplots = make_subplots(rows=len(all_figures), cols=1)
# Agrega cada figura al subploteo
for i, fig in enumerate(all_figures):
    for trace in fig['data']:
        fig_subplots.add_trace(trace, row=i + 1, col=1)
# Actualiza los títulos de los ejes y para que se muestren correctamente en el subploteo
for i, title in enumerate(titles):
    fig_subplots.update_yaxes(title_text=title, row=i + 1, col=1)
# Actualiza el layout del subploteo para que los gráficos no se superpongan
fig_subplots.update_layout(height=500 * len(all_figures), title_text="TIRs por TICKER")
# Guarda los gráficos en un archivo .html
fig_subplots.write_html("plots.html")