# -*- coding: utf-8 -*-
"""
Created on Fri Jan 11 14:50:03 2019

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
import pandas as pd
from itertools import islice   #导入迭代器

def read_pkl(path_pkl):
    x = open(path_pkl, 'rb')
    journals_dict = pkl.load(x,encoding='iso-8859-1')
    x.close()
    return journals_dict

def exist_or_not(paper_name, cite_all):   
    count = []
    for item in cite_all:
        if item in paper_name:
            count.append('1')
    print(len(count))

if __name__ == '__main__':  
    path_pkl = 'D:/bigdatahw/dissertation/pre_defence/nod/paper.pkl'
    paper_dict = read_pkl(path_pkl)
    paper_name = list(paper_dict.keys())
    paper = [''.join(item.split())for item in paper_name]#将论文的名称去掉空格
    cite_all = []
    for line in paper_name:
        cite_all.extend(list(paper_dict[line]['cite_paper'].keys()))
    cite_paper = []
    cited_paper = []
    all_paper = []
    for one_paper in paper_dict.keys():
        for one_cited_paper in list(paper_dict[one_paper]['cite_paper'].keys()):
            if ''.join(one_cited_paper.split()) in paper_name:
                cited_paper.append(one_cited_paper)
                cite_paper.append(one_paper)
    cite_paper = list(set(cite_paper))
    cited_paper = list(set(cited_paper))
    all_paper.extend(cite_paper)
    all_paper.extend(cited_paper)
    all_paper = list(set(all_paper))
    
    paper_dict_capy = deepcopy(paper_dict)
    for one_paper in paper_dict_capy.keys():
        if one_paper not in all_paper:
            paper_dict.pop(one_paper)
    
    path_csv = 'D:/bigdatahw/dissertation/pre_defence/data'
    path_nod = 'D:/bigdatahw/dissertation/pre_defence/nod'
    path_pkl = '/paper_new.pkl'
    paper_dict_file = open(path_nod+path_pkl, 'wb')
    pkl.dump(paper_dict, paper_dict_file)
    paper_dict_file.close()
    
    
    
                
                
                
                
                
                