# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 23:47:44 2019

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
from network_bulit import read_pkl
import pickle as pkl
from LDA_for_journal import convert_doc_to_wordlist
from LDA_for_journal import *
from gensim import corpora
from scipy.sparse import bsr_matrix
from gensim.models import word2vec
from network_bulit import trans_tuple, read_pkl, trans_tuple_without_ego, combine_tuple
import warnings
warnings.filterwarnings("ignore")

if __name__ == '__main__':  
    path_author_pkl = 'D:/bigdatahw/dissertation/pre_defence/nod/author_dict'
    author_dict = read_pkl(path_author_pkl)
    
