# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 15:13:28 2019

@author: Bokkin Wang
"""
import sys
sys.path.append("D:/bigdatahw/dissertation/pre_defence/code")
import math  
import numpy as np 
import networkx as nx
import matplotlib.pyplot as plt
from scipy.sparse import bsr_matrix 
from network_bulit import trans_tuple, read_pkl, trans_tuple_without_ego, combine_tuple

def all_np(arr):
    arr = np.array(arr)
    key = np.unique(arr)
    result = {}
    for k in key:
        mask = (arr == k)
        arr_new = arr[mask]
        v = arr_new.size
        result[k] = v
    return result 

def paper_population(label_data_labels,df_prob):
    population = {}
    paper_name = df_prob.columns.values.tolist()
    for i in list(set(label_data_labels)):
        population[str(i)] = []
    for index, group in enumerate(label_data_labels):
        population[str(group)].append(paper_name[index])
    return population

def random_lab(num,kind):
    mex = np.random.rand(num, kind)
    index = np.argmax(mex, axis=1)
    mex = np.zeros((num, kind), np.float32)
    for i in list(range(num)):
        mex[i][index[i]] = 1.0
    return mex
 
# label propagation  
def labelPropagation(df_prob, num_classes=10, max_iter = 2, tol = 20):
    # initialize  
    affinity_matrix = df_prob.values
    
    num_samples = affinity_matrix.shape[0]                                   #样本数量

    label_function = random_lab(num_samples,num_classes)              #随机
            
    # start to propagation  
    iter = 0
    pre_label_function = np.zeros((num_samples, num_classes), np.float32)  #生成原始矩阵
    
    changed = np.abs(pre_label_function - label_function).sum()            #记录标签改变，记录收敛
    while iter < max_iter and changed > tol:  
        if iter % 1 == 0:  
            print ("---> Iteration %d/%d, changed: %f" % (iter, max_iter, changed))  
        pre_label_function = label_function  
        iter += 1  
          
        # propagation  
        label_function = np.dot(affinity_matrix, label_function)    #更新标签矩阵
          
        # check converge  
        changed = np.abs(pre_label_function - label_function).sum()  #计算改变
      
    # get terminate label of unlabeled data  
    label_data_labels = np.zeros(num_samples)  
    for i in range(num_samples):  
        label_data_labels[i] = np.argmax(label_function[i])  #返回标签
      
    return label_data_labels  

# main function  
if __name__ == "__main__":  
    path_df_prob = 'D:/bigdatahw/dissertation/pre_defence/pkl/df_paper_prob_subnet_0.pkl'
    df_prob = read_pkl(path_df_prob)
    label_data_labels = labelPropagation(df_prob)
    label_data_labels = label_data_labels.tolist()
    
    ##载入数据
    path_pkl = 'D:/bigdatahw/dissertation/pre_defence/nod/paper_new.pkl'
    paper_dict = read_pkl(path_pkl)
    
    G = nx.DiGraph()
    G.add_nodes_from(list(paper_group.keys()))
    
    #搭建边
    paper_group_edge = combine_tuple(paper_group, journal_group1)
    G.add_edges_from(paper_group_edge)
     
 
    nx.draw(G,node_color = label_data_labels,edge_color = 'r',node_size =20)
     
    plt.axis('off')
    plt.savefig("color_nodes.png")
    plt.show()
    

    
    

    