import os
import string 
import sys
import pandas as pd
from pandas import DataFrame
import numpy as np
import random
from munkres import Munkres, print_matrix, DISALLOWED
from lapsolver import solve_dense
from collections import Counter
from tqdm import tqdm
import difflib
import re
import time

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

def get_unit(str):
    unit = re.findall(r'\D+',str)
    return unit[0]

def read_pair(pair: list):
    struc = pd.read_csv(data_dir+pair[0],names=['from_id','to_id','edge_bin','edge_type','node_type'])
    exp = pd.read_csv(data_dir+pair[1],names=['from_id','to_id','edge_bin','edge_type','node_type'])
    label = []
    order = exp['from_id'].unique()
    order_new = order.copy()
    random.shuffle(order_new)
    label = dict(zip(order,order_new))
    exp_new = exp.copy()
    exp_new['from_id'] = exp_new['from_id'].map(lambda x: label[x])
    exp_new['to_id'] = exp_new['to_id'].map(lambda x: label[x])

    return exp, exp_new, struc, label

def score(pre:list, label:dict):
    count = 0
    for pair in pre:
        if pair[1] in label.keys():
            if label[pair[1]] == pair[0]:
                count += 1
    return round(count/len(pre),4)

def get_matrix (exp:DataFrame, exp_new:DataFrame, struc:DataFrame):
    exp_new = exp_new.sort_values(by=['from_id'], ascending=[1])
    source = exp_new['from_id'].unique()
    target = struc['from_id'].unique()
    # print (len(source), len(target)) # n*m rectangular matrix
    matrix = []
    for v1 in tqdm(source):
        line = []
        for v2 in target:
            source_tmp = exp_new[exp_new['from_id'] == v1]
            target_tmp = struc[struc['from_id'] == v2]
            if len(source_tmp) > len(source_tmp):
                line.append(DISALLOWED)
            else:
                t1 = len(list((Counter(source_tmp['edge_bin']) & Counter(target_tmp['edge_bin'])).elements()))
                t2 = len(list((Counter(source_tmp['edge_type']) & Counter(target_tmp['edge_type'])).elements()))
                t3 = 5 - int(difflib.SequenceMatcher(None, get_unit(source_tmp['node_type'].values[0]), 
                        get_unit(target_tmp['node_type'].values[0])).quick_ratio() * 5)
                cost = 2 * len(source_tmp) - t1 - t2 + t3
                line.append(cost)
        matrix.append(line)
    for i in range(len(target)-len(source)):
        line = [0 for k in range(len(target))]
        matrix.append(line)
    return matrix, source, target

def assign (matrix:list, source, target):
    m = Munkres()
    indexes = m.compute(matrix)
    total = 0
    pre = []
    for row, column in indexes:
        value = matrix[row][column]
        total += value
        print(f'({row}, {column}) -> {value}')
        if row < len(source):
            pre.append([source[row], target[column]])
    print(f'total cost: {total}')
    return pre

def assign2 (matrix:list, source, target):
    for i in matrix:
        for j in i:
            if j == DISALLOWED:
                j = np.nan
    costs = np.array(matrix)
    rids, cids = solve_dense(costs)
    pre = []
    for r,c in zip(rids, cids):
        if r < len(source):
            pre.append([source[r],target[c]])
    return pre


def main():
    get_pairs()
    result = ''
    for i in tqdm(file_pair):
        result += i[0]+','+i[1]+','
        exp, exp_new, struc, label = read_pair(i)
        matrix, source, target = get_matrix(exp, exp_new, struc)
        pre = assign2 (matrix, source, target)
        result += str(score(pre,label))+'\n'
    file = open('./result.txt','w')
    file.write(result)
    file.close()
if __name__ == '__main__':
    main()