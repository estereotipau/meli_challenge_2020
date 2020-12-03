import gzip
import json
import pandas as pd
from simple_cluster_EG import data_for_segments

def jl_to_list(fname):
    output = []
    with gzip.open(fname, 'rb') as f:
        for line in f:
            output.append(json.loads(line))
    return output

rows_train = jl_to_list('train_dataset.jl.gz')
rows_test = jl_to_list('test_dataset.jl.gz')
df_train = data_for_segments(rows_train)
df_train['segment'] = 'train'
df_test = data_for_segments(rows_test)
df_test['segment'] = 'test'
df = pd.concat([df_train.drop(columns=['segment']), df_test.drop(columns=['segment'])], ignore_index = True)
segment = pd.concat([df_train['segment'], df_test['segment']], ignore_index = True)

df.to_csv('meli_data_v2.csv', index=False, sep=';')
segment.to_csv('meli_segment_v2.csv', index=False, sep=';', header=True)