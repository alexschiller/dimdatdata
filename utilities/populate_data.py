import os
import sys
import shutil

import json
import numpy as np
import pandas as pd


def rebuild_folder(dataset_dir):
    # delete and rebuild dataset directory
    if os.path.exists(dataset_dir):
        shutil.rmtree(dataset_dir)
    os.makedirs(dataset_dir)


def write_data(cols, dataset_dir, df, includes_any):
    if includes_any:
        df = df[np.bitwise_or.reduce([df[i['column']] == i['value'] for i in includes_any])]
    # header only needs to exist for multi column datasets
    write_header = len(cols) > 1
    subset = df.filter(cols, axis=1)
    subset.to_csv('{}data.csv'.format(dataset_dir), index=False, header=write_header)
    json_data = {key: list(subset[key]) for key in subset}
    with open('{}data.json'.format(dataset_dir), 'w') as fp:
        json.dump(json_data, fp)


def write_metadata(build, dataset_metadata, cols, dataset_dir):
    build['columns_metadata'] = [dataset_metadata[col] for col in cols]
    with open('{}metadata.json'.format(dataset_dir), 'w') as fp:
        json.dump(build, fp)

def populate_data(path=None):
    df = pd.read_csv('raw_data.csv')
    df.sort_values(df.columns[0])
    with open('builddata.json') as fp:
        builddata = json.load(fp)
    with open('metadata.json') as fp:
        dataset_metadata = json.load(fp)
    for build in builddata:
        if not path:
            dataset_dir = '{}/datasets/{}/'.format(os.path.dirname(os.path.dirname(os.getcwd())), build['route'])
        else:
            dataset_dir = '{}/datasets/{}/'.format(path, build['route'])
        rebuild_folder(dataset_dir)
        cols = build['columns']
        write_data(cols, dataset_dir, df, build['includes_any'])
        write_metadata(build, dataset_metadata, cols, dataset_dir)


if __name__ == '__main__':
    path = None
    if len(sys.argv) > 1:
        path = sys.argv[-1]
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    dirs = [x for x in os.listdir('raw_data') if x != '.DS_Store']
    for d in dirs:
        os.chdir('./raw_data/{}'.format(d))
        populate_data(path)
        os.chdir(os.path.abspath(os.path.join(os.getcwd(), '../..')))  # this is so bad, make me better
        print('successfully built: {}'.format(d))
