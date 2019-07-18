# -*- coding: utf-8 -*-
"""
Created on Sat May  4 12:02:53 2019

@author: Bokkin Wang
"""

import os
import json
import re
import csv 
import pickle as pkl
import difflib
import numpy as np
from copy import deepcopy
import networkx as nx
import pandas as pd
from itertools import islice   #导入迭代器
import matplotlib.pyplot as plt
from scipy import sparse
from collections import Counter
from LDA_for_label import *
from gensim import corpora
from scipy.sparse import bsr_matrix, dok_matrix
from gensim.models import word2vec
import warnings
warnings.filterwarnings("ignore")


def read_pkl(path_pkl):
    x = open(path_pkl, 'rb')
    journals_dict = pkl.load(x,encoding='iso-8859-1')
    x.close()
    return journals_dict

#不包含自连，并且带权重
def combine_tuple(author_dict):
    edge_list = []
    author_all = []                                                       #所有的引用
    co_author = []
    for one_author, attribute in author_dict.items():
        author_all.append(one_author)
        if attribute['state_data']['coauthor_stat']:                      #有合作者
            co_author.append(one_author)    
            for coauthor, weight in attribute['state_data']['coauthor_stat'].items():
                if one_author != coauthor and ( coauthor, one_author, {'weight':weight}) not in edge_list and coauthor != '' :
                    edge_list.append((one_author, coauthor, {'weight':weight}))      #增加连接
    return edge_list

#去除无用字符
def rm_char(text):
    text = re.sub('\x01', '', text)                        #全角的空白符
    text = re.sub('\u3000', '', text) 
    text = re.sub('\n+', " ", text)
#    text = re.sub(' +', "E S", text)
    text = re.sub(r"[\)(↓%·▲ ……\s+】&【]", " ", text) 
    text = re.sub(r"[\d（）《》–>*!<`‘’:“”──"".￥%&*﹐,～-]", " ", text,flags=re.I)
    text = re.sub('\n+', " ", text)
    text = re.sub('[，、：@。_;」※\\\\☆=／|―「！"●#★\'■//◆－~？?；——]', " ", text)
    text = re.sub(' +', " ", text)
    text = re.sub('\[', " ", text)
    text = re.sub('\]', " ", text)
    return text
    
#做出一个对应字典，进入一个正常字典生成一个标号字典和一个标号字典名
def trans_name_to_num (author_dict):
    author_num_dict = {}
    author_num_name = {}
    author_name_num = {}
    i = 1
    for name, value in author_dict.items():
        author_num_dict[str(i)] = value 
        author_num_name[str(i)] = name
        author_name_num[name] = str(i)
        i= i+1
    return author_num_dict, author_num_name, author_name_num
    
def change_name_num(title,paper_title_num):
    num = paper_title_num[title]
    return num

def change_num_name(num,paper_num_title):
    title = paper_num_title[num]
    return title

#构建网络
def build_Di_network(certain_dict):
    #搭建点
    G = nx.DiGraph()
    G.add_nodes_from(list(certain_dict.keys()))
    #搭建边(非自连)
    paper_edge = combine_tuple(certain_dict)
    
    G.add_edges_from(paper_edge)
    #搭建边（自连）
    #paper_edge = combine_tuple(certain_dict)
    #G.add_edges_from(paper_edge)
    return G,paper_edge

def build_network(certain_dict):
    G = nx.Graph()
    G.add_nodes_from(list(certain_dict.keys()))
    #搭建边(非自连)
    paper_edge = combine_tuple(certain_dict)
    G.add_edges_from(paper_edge)
    #搭建边（自连）
    #paper_edge = combine_tuple(certain_dict)
    #G.add_edges_from(paper_edge)
    return G
   
#找最大连通组件
def find_max_network(G):
    largest_components = max(nx.connected_components(G),key=len)
    print(len(largest_components))
    drop_nodes = set(list(G.nodes())).difference(set(largest_components))
    G_max = deepcopy(G)
    G_max.remove_nodes_from(drop_nodes) 
    return G_max,largest_components

#精炼网络转化为数字id
#def refine_num(paper_refine, paper_title_num):
#    paper_refine_num = {}
#    for key,content in paper_refine.items():
#        paper_refine_num[paper_title_num[key]] = content
#    return paper_refine_num

#输出点及连接关系方便gephi作图,分别
def net_output_csv(G,author_name_num, path_authornet_csv):  
    start_spot = [edgetuple[0] for edgetuple in G.edges()]
    start_spot_id = [author_name_num[edgetuple[0]] for edgetuple in G.edges()]
    end_spot = [edgetuple[1] for edgetuple in G.edges()]
    end_spot_id = [author_name_num[edgetuple[1]] for edgetuple in G.edges()]
    weight = [G[edgetuple[0]][edgetuple[1]]['weight'] for edgetuple in G.edges()]
    pd.DataFrame({'start_spot':start_spot,'start_spot_id':start_spot_id,'end_spot':end_spot,'end_spot_id':end_spot_id,'weight':weight}).to_csv(path_authornet_csv) 

if __name__ == '__main__':  
    #筛选数据
    path_read_author_dict_pkl = 'D:/bigdatahw/pan_paper/潘老师/pkl/author_dict.pkl'
    path_authornet_csv = 'D:/bigdatahw/pan_paper/潘老师/csv/author_net.csv'
    author_dict = read_pkl(path_read_author_dict_pkl)
    author_num_dict, author_num_name, author_name_num = trans_name_to_num(author_dict)
    #创建作者无向网络
    G_author_name = build_network(author_dict) #构建精炼的author_network    
    #输出csv给gephi
    net_output_csv(G_author_name,author_name_num, path_authornet_csv)

    
    G_paper_fine, largest_of_G_paper_fine = find_max_network(G_author_name)
    largest_of_G_paper_fine_num = [change_name_num(title,author_name_num) for title in list(largest_of_G_paper_fine)]
    
    #绘图
    nx.draw(g,pos=nx.random_layout(g),node_color = 'b',edge_color = 'r',node_size =10,style='solid',node_shape='o',font_size=20)
    plt.savefig("paper_group.png", dpi=400, bbox_inches='tight')
    plt.show()

    #描述
    len(G_paper_title)
    G_paper_title.number_of_edges()
    nx.degree_histogram(G_paper_fine)

    #转矩阵    
    nx.adjacency_matrix(G_paper_title).todense()
    dense = nx.adjacency_matrix(G_paper_title).todense()
    sparse.coo_matrix(dense)
    
    ##储存中间结果
    path_pkl = 'D:/bigdatahw/dissertation/pre_defence/nod/paper_group1_metrix.pkl'
    paper_dict_file = open(path_pkl, 'wb')
    pkl.dump(dense, paper_dict_file)
    paper_dict_file.close()
