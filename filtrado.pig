-- Cargar csv desde hdfs para el filtrado y homogenizacion
raw = LOAD '/user/hadoop/alerts.csv' USING PigStorage(',')
    AS (window_start:chararray, window_end:chararray, type:chararray, corner:chararray, count:int);

-- Eliminar primera fila (variables de la tabla)
datos = FILTER raw BY window_start != 'window_start';

-- Filtrado para evitar datos incorrectos
validos = FILTER datos BY
    (type IS NOT NULL AND TRIM(type) != '' AND
     corner IS NOT NULL AND TRIM(corner) != '' AND
     count > 0);

-- Normalizar para obtener las caracteristicas necesarias
normalizados = FOREACH validos GENERATE
    window_start AS timestamp,
    LOWER(TRIM(type)) AS tipo,
    LOWER(TRIM(corner)) AS zona,
    count;

-- Agrupar por tipo,zona,tiempo
agrupados = GROUP normalizados BY (tipo, zona, timestamp);

-- Generar descripcion de las alertas segun szona
resultado = FOREACH agrupados GENERATE
    group.tipo,
    group.zona,
    group.timestamp,
    COUNT(normalizados) AS total_incidentes,
    CONCAT('Incidente tipo ', group.tipo, ' en zona ', group.zona) AS descripcion;

-- Guardar resultados en hdfs
STORE resultado INTO '/user/hadoop/alertas_filtradas' USING PigStorage(',');

