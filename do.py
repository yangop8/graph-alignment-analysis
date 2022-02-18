import os 
import sys
import pandas as pd
import numpy as np

file_pair = []
data_dir = './data/'

def has_pair(file: str, files: list):
    if file.endswith('struc'):
        target = file[:file.find('struc')] + 'exp'
        return (target if target in files else None)
    elif file.endswith('exp'):
        target = file[:file.find('exp')] + 'struc'
        return (target if target in files else None)
    else:
        return None

def get_pairs():
    all_files = os.listdir(data_dir)

    for file in all_files:
        if file.endswith('struc') and has_pair(file,all_files) != None:
            file_pair.append([file,has_pair(file,all_files)])
        else:
            continue

def read_pair(pair: list):
    struc = pd.read_csv(data_dir+pair[0],names=['from_id','to_id','edge_bin','edge_type','node_type'])
    exp = pd.read_csv(data_dir+pair[1],names=['from_id','to_id','edge_bin','edge_type','node_type'])
    print (struc)
    print (exp)
        

def main():
    get_pairs()
    read_pair(file_pair[0])
    

if __name__ == '__main__':
    main()