# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 17:09:01 2019

@author: Bokkin Wang
"""

import os
import json
import re
import nltk
import csv 
import difflib
import numpy as np
from copy import deepcopy
import pandas as pd
from collections import Counter
import pyLDAvis
import pyLDAvis.gensim
import pickle as pkl
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer       #词形变化
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet
from nltk.stem import PorterStemmer
from gensim.models import LdaModel
from gensim import corpora, models
import tempfile
from pprint import pprint



##缩略语补全
class RegexpReplacer(object):
    replacement_patterns = [
    (r'won\'t', 'will not'),
    (r'can\'t', 'cannot'),
    (r'i\'m', 'i am'),
    (r'ain\'t', 'is not'),
    (r'(\w+)\'ll', '\g<1> will'),
    (r'(\w+)n\'t', '\g<1> not'),
    (r'(\w+)\'ve', '\g<1> have'),
    (r'(\w+)\'s', '\g<1> is'),
    (r'(\w+)\'re', '\g<1> are'),
    (r'(\w+)\'d', '\g<1> would')
    ]
    def __init__(self, patterns=replacement_patterns):
        self.patterns = [(re.compile(regex), repl) for (regex, repl) in patterns]
    def replace(self, text):
        s = text
        for (pattern, repl) in self.patterns:
            (s, count) = re.subn(pattern, repl, s)
        return s

##重复字符删除
class RepeatReplacer(object):
    def __init__(self):
        self.repeat_regexp = re.compile(r'(\w*)(\w)\2(\w*)')
        self.repl = r'\1\2\3'
    def replace(self, word):
        if wordnet.synsets(word):
            return word
        repl_word = self.repeat_regexp.sub(self.repl, word)
        if repl_word != word:
            return self.replace(repl_word)
        else:
            return repl_word    

# 获取单词的词性
def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return None

##去除各种字符字符        
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

##去除数字、非英文字符、停用词、转换成小写、词形还原等文本整体处理函数
def rm_tokens(words):  # 去掉一些停用词和完全包含数字的字符串
    ##进行基础词汇定义
    words = words.encode("utf-8").decode("utf-8")
    words = re.sub("\d","",words)
    Reg = RegexpReplacer()                           #删除缩写
    words_seg = [re.sub(u'\W', "", Reg.replace(i)) for i in nltk.word_tokenize(words)] 
    space_len = words_seg.count(u"")
    for i in list(range(space_len)):
        words_seg.remove(u'')
    filtered = [w.lower() for w in words_seg if w.lower() not in stopwords.words('english')] 
    tagged_sent = pos_tag(filtered)     # 获取单词词性
    wnl = WordNetLemmatizer()
    lemmatized = []
    #Rep = RepeatReplacer()
    for tag in tagged_sent:
        wordnet_pos = get_wordnet_pos(tag[1]) or wordnet.NOUN
        if wordnet_pos not in ['v','a','r']:
            lemmatized.append(wnl.lemmatize(tag[0], pos=wordnet_pos)) # 词形还原
    #final = [Rep.replace(w) for w in stems]          #删除重复字符
    return " ".join(lemmatized)

#删除无含义的单个字符保留有含义的单个字符例如r,p,a
def remove_single(tmp_list):
#    flu_word = ['model','data','method','time','using','use','john','paper','one','used','problem','analysis','based','approach','study','result','also']
    flu_word = []
    retain_single_word = ['r','p','a'] 
    new_list = []
    for word in tmp_list:
        if len(word)>2 and word not in flu_word:
            new_list.append(word)  
        if word in retain_single_word:
            new_list.append(word)        
    return new_list

#将文档转化为单词列表
def convert_doc_to_wordlist(str_doc):
    sent_list = str_doc.split('\n')
    sent_list = map(rm_char, sent_list)  # 去掉一些字符，例如\u3000
    word_list = [rm_tokens(part) for part in sent_list]  # 分词
    word2list = [remove_single(a.split()) for a in word_list]
    return word2list[0]

#读取序化模型
def read_pkl(path_pkl):
    x = open(path_pkl, 'rb')
    journals_dict = pkl.load(x,encoding='iso-8859-1')
    x.close()
    return journals_dict

#写出序化模型
def write_pkl(path_pkl,abtract_complete):
    abtract_complete_file = open(path_pkl, 'wb')
    pkl.dump(abtract_complete, abtract_complete_file)
    abtract_complete_file.close()

##删除词频为1的词汇
def remove_flu_one(abtract_complete):
    abtract_complete_count = []
    for onelist in abtract_complete:
        abtract_complete_count.extend(onelist)
    word_count = (Counter(abtract_complete_count).most_common())
    word_count_top = word_count[0:24]                            #词频最高的10个单词
    for i in range(len(word_count)-1, -1, -1):
        if word_count[i][1] == 1:
            word_count_top.append(word_count[i])                #删除次品唯一的单词
    for word_list in abtract_complete:
        for minute_word in word_count_top:
            while minute_word[0] in word_list:
                word_list.remove(minute_word[0])
    return abtract_complete

##综合文本状况
def sum_paper_massage(year_list,journals_dict):
    abtract_complete = []
    ##读取文本状况
    for journal in journals_dict.keys(): 
        for year in year_list:
            abtract_complete.append(convert_doc_to_wordlist(journals_dict[journal][year]['abstract_sum']))
    return abtract_complete
    
if __name__ == '__main__':  
    os.chdir("D:/bigdatahw/dissertation/pre_defence/data")
    path_csv = 'D:/bigdatahw/dissertation/pre_defence/data'
    path_read_pkl = 'D:/bigdatahw/dissertation/pre_defence/pkl/journal.pkl'
    path_write_pkl = 'D:/bigdatahw/dissertation/pre_defence/pkl/abtract_complete.pkl'
    path_model_pkl = 'D:/bigdatahw/dissertation/pre_defence/model/lda.pkl'
    path_ldamodel = 'D:/bigdatahw/dissertation/pre_defence/model/lda.pkl'
    journals_dict = read_pkl(path_read_pkl)
    year_list = ['2018','2017','2016','2015','2014']
    abtract_complete = sum_paper_massage(year_list,journals_dict)
    ##写出文本分词的pkl        
    write_pkl(path_write_pkl,abtract_complete)
    ##读取文本分词
    abtract_complete = read_pkl(path_write_pkl)
    ##去除高频词
    abtract_complete = remove_flu_one(abtract_complete)
    
    #LDA model---------------------------------------------------    
    ##生成语料库
    TEMP_FOLDER = tempfile.gettempdir()
    print('Folder "{}" will be used to save temporary dictionary and corpus.'.format(TEMP_FOLDER))
    dictionary = corpora.Dictionary(abtract_complete)
    dictionary.save(os.path.join(TEMP_FOLDER, 'paper.dict'))  # store the dictionary, for future reference
    print(dictionary)
    print(dictionary.token2id)
    corpus = [dictionary.doc2bow(text) for text in abtract_complete]  
    
    #转tfidf向量
    tfidf = models.TfidfModel(corpus)
    corpusTfidf = tfidf[corpus]
          
    ##描述情况
    corpora.MmCorpus.serialize(os.path.join(TEMP_FOLDER, 'paper.mm'), corpus)            
    print('Number of unique tokens: %d' % len(dictionary))
    print('Number of documents: %d' % len(corpus))  

    #设定参数
    num_topics = 4
    chunksize = 1000
    passes = 40
    iterations = 600
    eval_every = None  # Don't evaluate model perplexity, takes too much time.
    temp = dictionary[0]  # This is only to "load" the dictionary.
    id2word = dictionary.id2token   

    #建立模型
    model = LdaModel(corpus=corpus, id2word=id2word, chunksize=chunksize, \
                       alpha='auto', eta='auto', \
                       iterations=iterations, num_topics=num_topics, \
                       passes=passes, eval_every=eval_every)
    
    #输出每个主题的关键词
    top_topics = model.top_topics(corpus)
    pprint(top_topics)    
    
    #序化模型
    lda_model_file = open(path_model_pkl, 'wb')
    pkl.dump(model, lda_model_file)
    lda_model_file.close() 
    model = read_pkl(path_ldamodel)
    
    #每一行包含了主题词和主题词的权重
    model.print_topic(0,10)
    model.print_topic(1,10)            
    
    #判断一个训练集文档属于哪个主题
    for index, score in sorted(model[corpus[0]], key=lambda tup: -1*tup[1]):
        print("Score: {}\t Topic: {}".format(score, model.print_topic(index, 10)))
    
    #给训练集输出其属于不同主题概率   
    for i in list(range(10)):
        for index, score in sorted(model[corpus[i]], key=lambda tup: -1*tup[1]):
            print(index, score)
    
    #LDA visualization---------------------------------------------------
        
    vis_wrapper = pyLDAvis.gensim.prepare(model,corpus,dictionary)
    pyLDAvis.display(vis_wrapper)
    pyLDAvis.save_html(vis_wrapper,"lda%dtopics.html"%num_topics)
    


    pyLDAvis.show(vis_wrapper)
    #pyLDAvis.enable_notebook()
    #pyLDAvis.prepare(mds='tsne', **movies_model_data    
        
    ##序化字典以及模型
    path_dictionary = 'D:/bigdatahw/dissertation/pre_defence/dictionary/dictionary.dict'
    path_ldamodel = 'D:/bigdatahw/dissertation/pre_defence/model/lda.pkl'
    dictionary.compactify()   #去掉序号之间的空隙
    dictionary.save(path_dictionary)  #永久化字典


