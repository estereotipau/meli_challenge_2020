import gzip
import json
import numpy as np
import pandas as pd
from tqdm.notebook import tqdm
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from collections import Counter

#Funciones.
def jl_to_list(fname):
    output = []
    with gzip.open(fname, 'rb') as f:
        for line in f:
            output.append(json.loads(line))
    return output
    
def load_item_data(all_itms = False):
    ITEM_DATA = pd.read_csv('item_data.csv', sep=';')
    ITEM_DATA.loc[ITEM_DATA['product_id'] == 0, 'product_id'] = -1
    ITEM_DATA['domain_code'], domain_uniques = pd.factorize(ITEM_DATA['domain_id'], sort=True)
    ITEM_DATA['category_code'], category_uniques = pd.factorize(ITEM_DATA['category_id'], sort=True)
    fields = ['item_id', 'domain_id', 'domain_code', 'product_id', 'category_id', 'category_code', 'price', 'price_cluster', 'condition', 'mexico']
    m = {}
    for column in tqdm(fields):
         m[column] = list(ITEM_DATA[column])
    metadata = {}
    for i, j in tqdm(enumerate(m['item_id'])):
        metadata[j] = {}
        for column in fields: 
            metadata[j].update({column: m[column][i]})
    if all_itms:
        all_items = list(metadata)
    else:
        all_items = []
    return metadata, all_items

def views(row):
    return ([ev['event_info'] for ev in row['user_history'] if ev['event_type']=='view'])
	
def searchs(row):
    return ([ev['event_info'] for ev in row['user_history'] if ev['event_type']=='search'])

def dominios_visitados(visits):
    domains = Counter()
    for item in visits:
        domain = metadata[item]['domain_code']
        domains[domain] += 1
    return domains

def productos_visitados(visits):
    productos = Counter()
    for item in visits:
        producto = metadata[item]['product_id']
        if producto:
            productos[producto] += 1
    return productos

def categorias_visitadas(visits):
    categorias = Counter()
    for item in visits:
        categoria = metadata[item]['category_code']
        if categoria:
            categorias[categoria] += 1
    return categorias

def get_session_time(history):
    last_event=len(history)-1
    t0=datetime.strptime(history[0]['event_timestamp'].replace('T',' ')[:-5],'%Y-%m-%d %H:%M:%S.%f')
    t1=datetime.strptime(history[last_event]['event_timestamp'].replace('T',' ')[:-5],'%Y-%m-%d %H:%M:%S.%f')
    T=t1-t0
    return T.days*24*60*60+T.seconds+T.microseconds/1000000
    
def precio_mediano(visits):
    precios = []
    for item in visits:
    	if metadata[item]['price']:
    	    precios.append(float(metadata[item]['price']))
    if len(precios) != 0:
    	return np.median(np.array(precios))
    else:
    	return 0
    	
def precio_desvio(visits):
    precios = []
    for item in visits:
    	if metadata[item]['price']:
    	    precios.append(float(metadata[item]['price']))
    if len(precios) != 0:
    	return np.std(np.array(precios))
    else:
    	return 0

def mercado(visits):
	mexico = []
	for item in visits:
		mexico.append(int(metadata[item]['mexico']))
	if np.mean(np.array(mexico)) > 0.5:
		return 1
	else:
		return 0

def data_for_clusters(rows_data):
    cluster_data = []
    for row in tqdm(rows_data):
        temp = {'d_visitados': len(dominios_visitados(views(row))),
                'p_visitados': len(productos_visitados(views(row))),
                'c_visitadas': len(categorias_visitadas(views(row))),
                's_time': get_session_time(row['user_history']),
                's_len': len(row['user_history']),
                'v_len': len(views(row)),
                'p_views': len(views(row)) / len(row['user_history']),
                'median_p': precio_mediano(views(row)),
                'sd_p': precio_desvio(views(row)),
                'mercado': mercado(views(row))}
        cluster_data.append(temp)
    return pd.DataFrame(cluster_data)
    
def data_for_segments(rows_data):
    cluster_data = []
    for row in tqdm(rows_data):
        temp = {'v_len': len(views(row)),
				's_len': len(searchs(row))}
        cluster_data.append(temp)
    return pd.DataFrame(cluster_data)

def data_for_features(rows_data):
    cluster_data = []
    for row in tqdm(rows_data):
        temp = {'domain_code': list(dominios_visitados(views(row))),
                'product_id': list(productos_visitados(views(row))),
                'category_code': list(categorias_visitadas(views(row))),
                'median_p': precio_mediano(views(row)),
                'sd_p': precio_desvio(views(row)),
                'mercado': mercado(views(row))}
        cluster_data.append(temp)
    return pd.DataFrame(cluster_data)
	
def dominio_mas_visitado(rows_data):
    cluster_data = []
    for row in tqdm(rows_data):
        dominios = list(dominios_visitados(views(row)))
        if len(dominios) > 0:
            temp = {'vdomain': list(dominios_visitados(views(row)))[0]}
        else:
            temp = {'vdomain': -1}
        cluster_data.append(temp)
    return pd.DataFrame(cluster_data)

def clustering_process(df, k):    
    #Normalizacion.
    df_norm = StandardScaler().fit_transform(df)
    
    #Estructura para resultados.
    cs=np.empty(shape=[len(df_norm),1])
    
    #Algoritmo.
    kmeans=KMeans(n_clusters=k)
    kmeans.fit(df_norm)
    cs[:,0]=kmeans.fit_predict(df_norm)
    
    #Concat.
    df_cs=pd.DataFrame(cs,columns=['cluster'])
    df_final=pd.concat([df,df_cs],axis=1)
    
    if k <= 100:
        print(df_cs['cluster'].value_counts())
    
    return df_cs, kmeans

def clustering_predict(df, kmeans, k=10):    
    #Normalizacion.
    df_norm = StandardScaler().fit_transform(df)
    
    #Estructura para resultados.
    cs=np.empty(shape=[len(df_norm),1])
    
    #Algoritmo.
    cs[:,0]=kmeans.fit_predict(df_norm)
    
    #Concat.
    df_cs=pd.DataFrame(cs,columns=['cluster'])
    df_final=pd.concat([df,df_cs],axis=1)
    
    if k <= 100:
        print(df_final['cluster'].value_counts())
    
    return df_final
    
def meli_clusters(k):
    df = pd.read_csv('meli_data.csv', sep=';')
    df_c, kmeans = clustering_process(df, k)
    return df_c, kmeans

#Datos.
metadata, _ = load_item_data()