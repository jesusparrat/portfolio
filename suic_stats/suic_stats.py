# PROYECTO 1 - SUICIDIOS EN EL MUNDO
## Estudio sobre los suicidios en el mundo, filtrado por sexo intervalo de tiempos y países.

# Importamos las librerías necesarias para el programa:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
import os
import json
import os
import webbrowser


# se obtiene ruta absoluta del directorio actual ya que en script se ejecuta desde el directorio raíz
current_directory = os.path.dirname(os.path.abspath(__file__))

# se construye la ruta completa al archivo CSV que se encuentra en el directorio raíz
csv_file_path = os.path.join(current_directory, 'who_suicide_statistics.csv')

try:
    df = pd.read_csv(csv_file_path)

except FileNotFoundError:
    print(f"File not found: {csv_file_path}")
except Exception as e:
    print(f"An error occurred: {e}")


# nos quitamos datos nulos de varias columnas:
df = df.dropna()

# consultamos los valores de diversas columnas para un mejor filtrado:
df['year'].value_counts()

# filtraremos los datos en un intervalo de 20 años, del 90 al 2010, ambos inclusive:
df = df[(df["year"] >= 1990) & (df["year"] <= 2010)]
df


# miramos ahora los valores que tenemos por cada país para filtrar los países con poca muestra de datos:
with pd.option_context('display.max_rows', None):
    print(df['country'].value_counts())


df = df[~df['country'].isin(df['country'].value_counts()[df['country'].value_counts() < 100].index)]
df['country'].value_counts()
# esto imprime por pantalla todos los datos, no los 5 primeros y los 5 ultimos:
#with pd.option_context('display.max_rows', None):
#    print(df['country'].value_counts())


# ahora vamos a convertir los tipos de datos para tenerlo más preciso y mejorar el rendimiento:
df = df.copy()
df['year'] = df['year'].astype("int16")
df['suicides_no'] = df['suicides_no'].astype("int16")
df['population'] = df['population'].astype("int32")
df['country'] = df['country'].astype("string")
df['sex'] = df['sex'].astype("string")


# calculamos el número de suicidios por cada 100000 personas y agregamos la columna al final de la tabla. El número de suicidios por cada 100000 habitantes nos da una visión más acertada ya que estamos comparando el número bruto de suicidios con la gente de ese rango de edad y sexo por año:
data = {'suicides', 'population'}
def porcentaje_suic(row):
    return (row['suicides_no'] / row['population']) * 100000
df['suicides x100000'] = df.apply(porcentaje_suic, axis=1)

# ahora limpiamos los datos de los paises para que no haya errores:
df['country'] = df['country'].replace('\(USA\)','', regex = True)
df['country'] = df['country'].replace('\(Bolivarian Republic of\)','', regex = True)

# añadiremos una columna nueva para comprobar el continente del país. Para ello creamos una lista de países para cada continente:
europa = ['Ukraine', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands', 'Norway', 'Sweden', 'Spain', 'Romania', 'Russian Federation', 'Slovenia', 'Germany', 'France', 'Belgium', 'Czech Republic', 'Bulgaria', 'Estonia', 'United Kingdom', 'Finland', 'Austria', 'TFYR Macedonia', 'Poland', 'Albania', 'Slovakia', 'Portugal', 'Belarus','Denmark','Switzerland','Azerbaijan','Croatia', 'Serbia', 'Montenegro', 'Cyprus']
america = ['Guatemala','Trinidad and Tobago','Mexico','Puerto Rico','United States of America','Colombia','Costa Rica', 'Chile','Canada','Ecuador','Brazil','Argentina','Saint Lucia','Guyana','El Salvador','Belize','Suriname', 'Venezuela ', 'Paraguay', 'Cuba', 'Uruguay','Bahamas','Antigua and Barbuda','Saint Vincent and Grenadines','Barbados','Grenada','Panama', 'Virgin Islands ', 'Aruba', 'Martinique', 'Jamaica', 'Guadeloupe', 'French Guiana', 'Reunion']
africa = ['South Africa', 'Egypt', 'Seychelles']
asia = ['Hong Kong SAR','Israel','Japan','Kazakhstan','Kyrgyzstan','Republic of Korea','Republic of Moldova','Singapore','Turkmenistan','Armenia','Thailand','Uzbekistan','Kuwait', 'Brunei Darussalam', 'Mauritius', 'Georgia', 'Philippines', 'Bahrain', 'Qatar', 'Sri Lanka', 'Maldives']
oceania = ['New Zealand','Australia', 'Kiribati', 'Fiji']

# generamos una nueva columna llamada 'continent' con valores de la tabla, para no buscarnos muchos problemas:
df["continent"] = df["country"]
df['continent'] = df['continent'].replace(europa,'Europe', regex = True)
df['continent'] = df['continent'].replace(america,'America', regex = True)
df['continent'] = df['continent'].replace(africa,'Africa', regex = True)
df['continent'] = df['continent'].replace(asia,'Asia', regex = True)
df['continent'] = df['continent'].replace(oceania,'Oceania', regex = True)
df = df.reindex(columns=['country', 'continent','year', 'sex', 'age', 'suicides_no', 'population','suicides x100000'])

# comprobamos los continentes que tenemos para ver si lo hemos hecho bien:
df['continent'].value_counts()

# guardamos los datos en un fichero nuevo:
df_l = df.to_csv('datos_limpios.csv')

# agrupamos por país, genero y edad el número de suicidios a lo largo del intervalo:
total_suicides_by_sex_age = df.groupby(['country','sex', 'age'])['suicides_no'].sum()
total_suicides_by_sex_age

# ahora vamos a extraer los datos de España:
spain = df[df['country'] == 'Spain']
total_suicides_by_sex_age_spain = spain.groupby(['country','sex', 'age'])['suicides_no'].sum()
with pd.option_context('display.max_rows', None):
    print(total_suicides_by_sex_age_spain)

# extraemos los datos también para Europa:
europe = df[df['continent'] == 'Europe']
total_suicides_by_sex_age_europe = europe.groupby(['country','sex', 'age'])['suicides_no'].sum()
with pd.option_context('display.max_rows', None):
    print(total_suicides_by_sex_age_europe)

# observamos los datos de los suicidios por sexo, en total en España a lo largo de los años: 
total_suicides_by_sex_sp = spain.groupby(['country','sex'])['suicides_no'].sum()

# hacemos un gráfico para representarlo
sc_fem_to_sp = total_suicides_by_sex_sp[0]
sc_ma_to_sp = total_suicides_by_sex_sp[1]
plt.pie(
    # valores a representar
    [sc_fem_to_sp, sc_ma_to_sp],
    # etiquetas
    labels = ['Mujeres', 'Hombres'],
    # sombra
    shadow = True,
    # colores
    colors = ['g', 'y'],
    # ángulo de inicio
    startangle = 310,
    # mostramos el valor como un valor porcentual con un dígito decimal
    autopct = '%1.1f%%'
    )

# especificamos el título del gráfico
plt.title("Suicidios en España por sexos entre 1990-2010")

# mostramos el gráfico
plt.show()

# lo mismo para Europa:
total_suicides_by_sex_eu = europe.groupby(['sex'])['suicides_no'].sum()

sc_fem_to_eu = total_suicides_by_sex_eu[0]
sc_ma_to_eu = total_suicides_by_sex_eu[1]
plt.pie(
    # valores a representar
    [sc_fem_to_eu, sc_ma_to_eu],
    # etiquetas
    labels = ['Mujeres', 'Hombres'],
    # sombra
    shadow = True,
    # colores
    colors = ['g', 'y'],
    # ángulo de inicio
    startangle = 310,
    # mostramos el valor como un valor porcentual con un dígito decimal
    autopct = '%1.1f%%'
    )

# especificamos el título del gráfico
plt.title("Suicidios en Europa por sexos entre 1990-2010")

# mostramos el gráfico
plt.show()

# dividimos un poco más el dataframe de España y nos centramos en los suicidios por edad sin dependencia del sexo:
total_suicides_by_age_sp = spain.groupby(['country','age'])['suicides_no'].sum()

sc_15_24_to_sp = total_suicides_by_age_sp[0]
sc_25_34_to_sp = total_suicides_by_age_sp[1]
sc_35_54_to_sp = total_suicides_by_age_sp[2]
sc_5_14_to_sp = total_suicides_by_age_sp[3]
sc_55_74_to_sp = total_suicides_by_age_sp[4]
sc_75_to_sp = total_suicides_by_age_sp[5]
plt.pie(
    # valores a representar
    [sc_5_14_to_sp, sc_15_24_to_sp, sc_25_34_to_sp, sc_35_54_to_sp, sc_55_74_to_sp, sc_75_to_sp],
    # etiquetas
    labels = ['5-14 years', '15-24 years', '25-34 years', '35-54 years',  '55-74 years', '75+ years'],
    # sombra
    shadow = True,
    # colores
    colors = ['g', 'y', 'b', 'r', 'purple', 'orange'],
    # ángulo de inicio
    startangle = 0,
    # mostramos el valor como un valor porcentual con un dígito decimal
    autopct = '%1.1f%%'
    )

# especificamos el título del gráfico
plt.title("Suicidios en España por rango de edad entre 1990-2010")

# mostramos el gráfico
plt.show()

# hacemos lo mismo para los datos de Europa: 
total_suicides_by_age_eu = europe.groupby(['age'])['suicides_no'].sum()

sc_15_24_to_eu = total_suicides_by_age_eu[0]
sc_25_34_to_eu = total_suicides_by_age_eu[1]
sc_35_54_to_eu = total_suicides_by_age_eu[2]
sc_5_14_to_eu = total_suicides_by_age_eu[3]
sc_55_74_to_eu = total_suicides_by_age_eu[4]
sc_75_to_eu = total_suicides_by_age_eu[5]
plt.pie(
    # valores a representar
    [sc_5_14_to_eu, sc_15_24_to_eu, sc_25_34_to_eu, sc_35_54_to_eu, sc_55_74_to_eu, sc_75_to_eu],
    # etiquetas
    labels = ['5-14 years', '15-24 years', '25-34 years', '35-54 years',  '55-74 years', '75+ years'],
    # sombra
    shadow = True,
    # colores
    colors = ['g', 'y', 'b', 'r', 'purple', 'orange'],
    # ángulo de inicio
    startangle = 0,
    # mostramos el valor como un valor porcentual con un dígito decimal
    autopct = '%1.1f%%'
    )

# especificamos el título del gráfico
plt.title("Suicidios en Europa por rango de edad entre 1990-2010")

# mostramos el gráfico
plt.show()


# ahora vamos a hacer algo más ambicioso: vamos a hacer un mapa del mundo con los suicidios por 100000 habitantes de mujeres entre 15-24 años, por ejemplo:
df_suic_fem_15_24 = df.loc[(df["age"]=="15-24 years") & (df["sex"]=="male"), :]#.drop(["sex", "age", "suicides_no", "population"], axis=1)
df_suic_fem_15_24 = df_suic_fem_15_24.groupby(['country','continent'])['suicides x100000'].sum()
df_suic_fem_15_24 = pd.DataFrame(df_suic_fem_15_24).reset_index()
df_suic_fem_15_24 = df_suic_fem_15_24.sort_values(by=['suicides x100000'], ascending=False)
df_suic_fem_15_24

# se obtiene la ruta absoluta del directorio actual, ya que en script se ejecuta desde el directorio raíz
current_directory = os.path.dirname(os.path.abspath(__file__))

# se construye la ruta completa al archivo JSON
json_file_path = os.path.join(current_directory, 'world_countries.json')

try:
    with open(json_file_path, 'r') as f:
        world_geo = json.load(f)

    world_map = folium.Map(location=[0, 0], zoom_start=2, tiles='suicides x100000', attr='Suicidios por 100000 habitantes de 1990 a 2010 de mujeres entre 15-24 años')

    folium.Choropleth(
        geo_data=world_geo,
        data=df_suic_fem_15_24,
        columns=['country', "suicides x100000"],
        key_on='feature.properties.name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Suicidios por 100000 habitantes'
    ).add_to(world_map)

    folium.LayerControl().add_to(world_map)

    # mostramos el mapa guardándolo primero el mapa en un archivo HTML
    html_file_path = os.path.join(current_directory, 'world_map.html')
    world_map.save(html_file_path)

    # abrimos el archivo HTML en el navegador
    webbrowser.open(html_file_path)

except FileNotFoundError:
    print(f"File not found: {json_file_path}")
except Exception as e:
    print(f"An error occurred: {e}")



# ahora, algo más personalizable: vamos a hacer un mapa del mundo con los suicidios por 100000 habitantes con todas las combinaciones posibles de sexo y rango de edad:
num_intentos = 3

for intento in range(num_intentos):
    age_range = int(input("Introduce el rango de edad a filtrar:\n1. 5-14 years\n2. 15-24 years\n3. 25-34 years\n4. 35-54 years\n5. 55-74 years\n6. 75+ years\n"))

    if age_range == 1:
        age_range = "5-14 years"
    elif age_range == 2:
        age_range = "15-24 years"
    elif age_range == 3:
        age_range = "25-34 years"
    elif age_range == 4:
        age_range = "35-54 years"
    elif age_range == 5:
        age_range = "55-74 years"
    elif age_range == 6:
        age_range = "75+ years"
    else:
        print("Valor no válido. Intento {}/{}.".format(intento, num_intentos))
        if intento == num_intentos:
            print("Has agotado tus 3 intentos. Saliendo del programa.")
        continue
    break  # rompe el bucle si la entrada es válida


max_intentos = 3

for intento in range(1, max_intentos + 1):
    sex_fm = int(input("Introduce el sexo a filtrar:\n1. female\n2. male\n"))

    if sex_fm == 1:
        sex_fm = "female"
    elif sex_fm == 2:
        sex_fm = "male"
    else:
        print("Valor no válido. Intento {}/{}.".format(intento, max_intentos))
        if intento == max_intentos:
            print("Has agotado tus 3 intentos. Saliendo del programa.")
        continue
    break  # rompe el bucle si la entrada es válida

print(f"Seleccionado el rango de edad: {age_range}")
print(f"Seleccionado el sexo a filtrar: {sex_fm}")

df_pers = df.loc[(df["age"]==age_range) & (df["sex"]==sex_fm), :]#.drop(["sex", "age", "suicides_no", "population"], axis=1)
df_pers = df_pers.groupby(['country','continent'])['suicides x100000'].sum()
df_pers = pd.DataFrame(df_pers).reset_index()


# se obtiene la ruta absoluta del directorio actual, ya que en script se ejecuta desde el directorio raíz
current_directory = os.path.dirname(os.path.abspath(__file__))

# se construye la ruta completa al archivo JSON
json_file_path = os.path.join(current_directory, 'world_countries.json')

try:
    with open(json_file_path, 'r') as f:
        world_geo = json.load(f)

    world_map_2 = folium.Map(location=[0, 0], zoom_start=2, tiles='suicides x100000', attr='Suicidios por 100000 habitantes de 1990 a 2010 de {} entre {}'.format(sex_fm, age_range))

    folium.Choropleth(
        geo_data=world_geo,
        data=df_pers,
        columns=['country', "suicides x100000"],
        key_on='feature.properties.name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Suicidios por 100000 habitantes',
    ).add_to(world_map_2)

    folium.LayerControl().add_to(world_map_2)

    # mostramos el mapa guardándolo primero el mapa en un archivo HTML
    html_file_path_2 = os.path.join(current_directory, 'world_map_2.html')
    world_map_2.save(html_file_path_2)

    # abrimos el archivo HTML en el navegador
    webbrowser.open(html_file_path_2)

except FileNotFoundError:
    print(f"File not found: {json_file_path}")
except Exception as e:
    print(f"An error occurred: {e}")