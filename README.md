## Estructura de la Aplicación

1. **Scrapper**:
    - Recopila los datos de la pagina [Waze](https://www.waze.com/es-419/live-map/) para luego extraer las alertas publicadas en Santiago de Chile.
    - Separa la ciudad en 4 áreas distintas para poder recopilar la mayor cantidad de alertas posible.

2. **Data Storage**:
    - Almacena los datos extraidos del scrapper para ser consumidos por el siguiente modulo.

3. **Filtrado y Homogenizacion**:
    - Con los datos del Data Storage se realiza un proceso de limpieza de datos, el cual elimina los datos erroneos, incompletos o repetidos.
    - Agrupa los datos recopilados segun caracecteristicas similares.

4. **Processing**:
    - Se procesan los datos del modulo anterior para realizar consultas y transformaciones complejas de datos para posterior análisis


## Tecnologías Utilizadas

- **Docker**: Conteneriza todos los servicios y simplificar la implementación.
- **Selenium**: Automatizacion de pruebas en aplicaciones web por medio de varios navegadores.
- **BeautifulSoup**: Recupera el HTML dejado por Selenium y extrae los datos. Herramienta principal para el scrapping.
- **Mysql**: Sistema de Gestión de base de datos que utiliza lenguaje SQL (Structured Query Language) que nos permite almacenar la información del scraper.
- **Apache Pig**: Framework de código abierto que permite procesar grandes conjuntos de datos complejos, en nuestro caso nos permite agrupar y analizar el comportamiento de las alertas de la plataforma Waze. 

## Instrucciones de Instalación

1. **Levantar servicios (contenedores) y esperar unos segundos**
    docker-compose up --build

2. **Ejecutar codigo scraper.py (en otra terminal)**
    docker-compose run --rm waze-scraper

3. **Abrir otra terminal para entrar en contenedor Pig para filtrado y carga de archivo csv**
    docker exec -it pig bash
    hdfs dfs -mkdir -p /user/hadoop
    hdfs dfs -put /data/alerts.csv /user/hadoop/alerts.csv

4. **Ejecutar Filtrado.pig en Pig**
    pig -x mapreduce /data/filtrado.pig

5. **Ver Resultados**
    hdfs dfs -cat /user/hadoop/alertas_filtradas/part-*