# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 21:46:12 2019

@author: Bokkin Wang
"""
import os
import json
from math import log, sqrt
import re
import csv
import sys 
sys.path.append("D:/bigdatahw/dissertation/pre_defence/code")
import difflib
import numpy as np
from copy import deepcopy
from scipy import sparse
import pandas as pd
from itertools import islice   #导入迭代器
from collections import Counter
import networkx as nx
import pickle as pkl
from LDA_for_journal import convert_doc_to_wordlist
from LDA_for_journal import *
from gensim import corpora
from scipy.sparse import bsr_matrix, dok_matrix
from gensim.models import word2vec
import warnings
warnings.filterwarnings("ignore")

#分配标签划分网络
def distribute_label(journals_dict,paper_dict,path_read_paper_dict_pkl,path_subnet_cluster_pkl):
    subnet_cluster = {}
    pop_list = []
    for paper_title in paper_dict.keys():
        try:
            paper_dict[paper_title]['community'] = journals_dict[paper_dict[paper_title]['ego_attribute']['publisher']]['community']  
            for label in paper_dict[paper_title]['community']:
                if 'subnet_'+label in subnet_cluster.keys():
                    subnet_cluster['subnet_'+label][paper_title] =  paper_dict[paper_title]   
                else:
                    subnet_cluster['subnet_'+label] = {}
                    subnet_cluster['subnet_'+label][paper_title] =  paper_dict[paper_title]                
        except:
            pop_list.append(paper_title)
            print(paper_title)
            pass
    for pop_one in pop_list:
        paper_dict.pop(pop_one)
    write_pkl(path_read_paper_dict_pkl,paper_dict)
    write_pkl(path_subnet_cluster_pkl,subnet_cluster)
    return subnet_cluster

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
    
#筛选文章，输入文章字典增加连边
def statistics_paper_dict(paper_dict):
    paper_name = list(paper_dict.keys())
    paper = [''.join(rm_char(item).split())for item in paper_name]#将论文的名称去掉空格
    cite_all = []                                                 #所有的引用
    cite_paper = []
    cited_paper = []
    all_paper = []
    for one_paper in paper_dict.keys():
        cite_all.extend(list(paper_dict[one_paper]['cite_paper'].keys()))
        for one_cited_paper in list(paper_dict[one_paper]['cite_paper'].keys()):
            if ''.join(rm_char(one_cited_paper).split()) in paper:
                cited_paper.append(one_cited_paper)
                cite_paper.append(one_paper)
    cite_all = list(set(cite_all))            #总引用
    cite_paper = list(set(cite_paper))        #引用者
    cited_paper = list(set(cited_paper))      #被引用者   
    all_paper.extend(cite_paper)              #网络中不孤立的点
    all_paper.extend(cited_paper)
    all_paper = list(set(all_paper))
    return[cite_paper,cited_paper,all_paper,cite_all] #引用者,被引用者,网咯中不孤立的点,总引用


if  __name__ == '__main__':  
    path_read_journals_dict_pkl = 'D:/bigdatahw/dissertation/pre_defence/pkl/journal_dict.pkl'
    path_read_paper_dict_pkl = 'D:/bigdatahw/dissertation/pre_defence/pkl/paper_dict.pkl'
    path_subnet_cluster_pkl = 'D:/bigdatahw/dissertation/pre_defence/pkl/subnet_cluster.pkl'
    journals_dict = read_pkl(path_read_journals_dict_pkl)
    paper_dict = read_pkl(path_read_paper_dict_pkl)
    distribute_label(journals_dict,paper_dict,path_read_paper_dict_pkl,path_subnet_cluster_pkl)
    statistics_result = statistics_paper_dict(paper_dict)
