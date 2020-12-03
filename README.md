# meli_challenge_2020
 
El notebook "meli_challenge_v9.7" contiene los pasos para construir el archivo de predicciones "submission_n25.csv" que fue el que obtuvo el último y mejor puntaje en el concurso (subido el 30/11/2020).

En las primeras 9 celdas carga la información generada en otros notebooks y prepara la estimación: (1) se importan bibliotecas; (2) se definen funciones, (3) se carga información de ítems extraída del archivo "item_data.jl"; (4) se cargan vectores de dimensión del train dataset con (a) ids de los ítems comprados, (b) ids de los dominios de los ítems comprados y (c) mercado - Méximo o Brasil - de los ítems comprados; (5) se cargan los predictores, que son estrategias para acertar los ítems a ser comprados - en total hay 56 predictores disponibles tanto para el train dataset como para el test dataset, generados con cuadernillos auxiliares (*); (6) se divide el train dataset en train (50%) y test (50%); (7) se cargan vectores de dominio y mercado para el train dataset (train y test); (8) se cargan predictores de ítems más vendidos restringido por mercado; (9) se cargan los clusters a los que pertenece cada sesión del train dataset para restringir la estimación por cluster - los clusters fueron determinados por Kmeans tomando como features candidad de búsquedas, cantidad de visitas, cantidad de dominios visitados, cantidad de categorías visitadas, cantidad de productos visitados y tiempo total en segundos de cada sesión; (10) no se aplica en esta versión.

La celda 11 corresponde a la calibración de cada predictor según su efectividad en el tramo "train" del train dataset (muestra aleatoria del 50% de las sesiones). Se evalúa la performance de cada predictor de forma separada, restringiendo por cluster. La celda 12 hace lo mismo pero sin restringir. No es utilizada para las predicciones finales.

La celda 13 inicializa las versiones. Como en esta versión yo ya había elegido los predictores que mejor funcionaban, utilicé el código de la celda 14.

La celda 15 es la más importante de todo el proceso. El loop exterior - while - prueba con los predictores de a uno, eligiéndolos del "grupoA". Luego mantiene en la primera posición al predictor que mejor performance tuvo (pasándolo al "grupoB") y sigue con los restante. Cuando en toda una ronda la performance total no mejoró respecto de la anterior, el loop se interrumpe.

Este proceso se aplica al tramo test del train dataset (50% de la muestra seleccionada de forma aleatoria, celda 6).

El segundo loop itera por cada una de las versiones, combinando los elementos del "grupoA" con los del "grupoB". El tercer loop itera por cada una de las sesiones que integran la muestra.

Para elaborar un ranking de los ítems se establece una referencia (cref) que corresponde con el cluster al que pertenece la sesión que se está intentando predecir. Esto se realiza para cada predictor "f". Luego la función "get_y_hat" devuelve los 10 ítems que obtuvieron mejor ranking, sumando la performance de sus apariciones. Es decir, si un mismo ítems aparece en dos estrategias (por ejemplo "último ítem visitado" e "ítem más visitado") el ranking que obtiene corresponde a la suma de ambas.

Si se obtiene menos de 10 ítems, la lista se completa con lo más vendido del dominio según el mercado (función "gen_sales").

El resto del código de la celda se aplica para evaluar la predicción, contrastando con los ítems efectivamente adquiridos, que para este dataset están disponibles.

A través de este procedimiento se selecciona el mejor modelo, que consiste en incorporar el grupo de predictores que en conjunto mejor funcionan. En el mejor resultado fueron: 'dim_miv', 'dim_tbc', 'dim_liv', 'dim_sss', 'dim_vc', 'dim_ocat_16', 'dim_tbp', 'dim_bc', ordenados por mejor performance individual. Aquí va una breve descripción de cada uno: 'dim_miv', ítems más visitados; 'dim_tbc', top de ventas por categoría más visitada; 'dim_liv', últimos ítems visitados; 'dim_sss', palabras clave de ítems más vendidos por búsqueda, si una búsqueda incluye ciertas keywords existe un conjunto de ítems que es más probable que sea adquirido; 'dim_vc', vistas-compra con sesgo por endogeneidad exatraído; 'dim_ocat_16', ítems más vendidos en la categoría más visitada y en un rasgo de 0.5 desvíos estándar de la mediana de precio de las visitas; 'dim_tbp', top de ventas por producto más visitado; 'dim_bc', búsquedas-compra con sesgo por endogeneidad extraído.

Esa selección de predictores se utiliza en la anteúltima celda para generar la predicción final sobre el test dataset. Adicionalmente, cuando se tienen cargados los resultados de otros modelos, se ejecuta una versión optimizada de la predicción que consiste en elegir el modelo que mejor funcionó para cluster. Aunque en términos teóricos esto puede conducir a overfitting, al aplicarlo verifiqué una mejora de algunos puntos en el resultado de la predicción arrojado por el sitio del challenge.

(*) Algunos de los notebooks que acompaño en el repositorio muestran cómo fueron generados cada uno de estos 56 predictores. Por ejemplo, "meli_challenge_make_busquedas_compras" muestra cómo se crearon los predictores de búsquedas-compra sin sesgo tanto para el train como para el test dataset.

Ezequiel Guerra
FCE - UBA
Diciembre 2020









