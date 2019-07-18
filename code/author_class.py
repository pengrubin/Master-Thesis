# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 10:50:06 2018

@author: Bokkin Wang
"""

import os
import json
import re
import csv
import sys 
sys.path.append("D:/bigdatahw/dissertation/pre_defence/code") 
import time
import difflib
import pickle as pkl
import numpy as np
from copy import deepcopy
from LDA_for_label import read_pkl
from itertools import islice   #导入迭代器


class author(object):
    
    def __init__(self,one_line):
        self.authors = [author.split('@')[0].replace(', ',',').replace('  ',' ').replace('. ','.').title().replace('-','') for author in one_line[10].split('::')]  #创建一个作者名录
        self.title = one_line[0].lower().strip().replace('  ',' ')
        self.publisher = one_line[1].lower()
        self.publish_date = one_line[3].strip().replace('  ',' ')
        self.cited_num = one_line[4]
        self.time_cited = one_line[5]
        self.abstract = one_line[6]
        self.keyword = ','.join([item.strip().lower().replace('  ',' ') for item in one_line[7].split(',')])
        self.keyword_plus = ','.join([item.strip().lower().replace('  ',' ') for item in one_line[8].split(',')])
        self.anthor_address = one_line[9]
        self.author_university = one_line[10]
        self.author_id = one_line[11]
        self.author_dict = {}
            
    def time_transform(self):
        def months_match(var):
            return {'JAN': '1','JANUARY':'1','FEB': '2','FEBRUARY':'2','MAR': '3','MARCH':'3',
                    'APR':'4','APRIL':'4','MAY':'5','JUN':'6','JUNE':'6','JUL':'7','JULY':'7',
                    'AUG':'8','AUGUST':'8','SEP':'9','SEPT':'9','SEPTEMBER':'9',
                    'OCT':'10','OCTOBER':'10','NOV':'11','NOVEMBER':'11','DEC':'12','DECEMBER':'12'}.get(var,'error')  
        re_pattern1 = re.compile(r"[A-Za-z]{3,9}\s+?\d{1,2}\s+?\d{4}")
        re_pattern2 = re.compile(r"[A-Za-z]{3,9}\s+?\d{4}")
        re_pattern3 = re.compile(r"\d{4}/\d{1,2}/\d{1,2}")
        re_pattern4 = re.compile(r"[A-Za-z]{3}-[A-Za-z]{3}\s+?\d{4}")
        re_pattern5 = re.compile(r"\d{4}")
        re_pattern6 = re.compile(r"[A-Za-z]{3}-\d{2}")
        re_pattern7 = re.compile(r"[A-Za-z]{3,9}\s*\d{1,2}\s*\d{4}")
        re_pattern8 = re.compile(r"\d{1,2}-[A-Za-z]{3}")
        re_pattern9 = re.compile(r"\d{4}-[A-Za-z]{3,9}")
        re_pattern10 = re.compile(r"\d{2}\s+?\d{4}")
        self.publish_date = self.publish_date.replace('.',' ')
        if re_pattern1.fullmatch(self.publish_date):
            date_time = self.publish_date.split()
            date = date_time[2]+'-' + months_match(date_time[0].upper())
        if re_pattern2.fullmatch(self.publish_date):
            date_time = self.publish_date.split()
            date = date_time[1]+'-' + months_match(date_time[0].upper())
        if re_pattern3.fullmatch(self.publish_date):
            date = self.publish_date.split('/')[0]+'-'+self.publish_date.split('/')[1]  
        if re_pattern4.fullmatch(self.publish_date):
            date_time = [item.split('-')[0] for item in self.publish_date.split()]
            date = date_time[1]+'-'+ months_match(date_time[0].upper())
        if re_pattern5.fullmatch(self.publish_date) and len(self.publish_date) == 4:
            date_time = self.publish_date
            date = self.publish_date + '-6'    
        if re_pattern6.fullmatch(self.publish_date):
            if int(self.publish_date.split('-')[1]) > 80:
                year = '19'+self.publish_date.split('-')[1]
            else:
                year = '20'+self.publish_date.split('-')[1]
            date = year + '-'+months_match(self.publish_date.split('-')[0].upper()) 
        if re_pattern7.fullmatch(self.publish_date):
            date = self.publish_date.split()[2]+'-'+months_match(self.publish_date.split()[0])  
        if re_pattern8.fullmatch(self.publish_date):
            if int(self.publish_date.split('-')[0]) > 80:
                year = '19'+self.publish_date.split('-')[0]
            else:
                if len(self.publish_date.split('-')[0]) == 1:
                    year = '200'+self.publish_date.split('-')[0]
                    date = year + '-'+months_match(self.publish_date.split('-')[1].upper())                     
                else:    
                    year = '20'+self.publish_date.split('-')[0]
                    date = year + '-'+months_match(self.publish_date.split('-')[1].upper())  
        if re_pattern9.fullmatch(self.publish_date):
            date = self.publish_date.split('-')[0]+'-'+months_match(self.publish_date.split('-')[1].upper())
        if re_pattern10.fullmatch(self.publish_date):
            date = self.publish_date.split()[1]+'-'+self.publish_date.split()[0].replace('0','')        
        if self.publish_date == '':
            date = '1905-6'
        try:
            return date 
        except:
            print(self.publish_date)
        
    def string_process(self,string):
        string = string.strip()
        string = string.replace(', ',',')
        string = string.replace('  ',' ')
        string = string.replace('   ',' ')
        return string
    
    def top_matching_degree(self,item_name):
        top_author = ''
        top_degree = 0 
        for author in self.authors:
            degree = difflib.SequenceMatcher(None, item_name, author).quick_ratio()
            if degree > top_degree:
                top_author = author
                top_degree = degree
        if top_degree > 0.57:
            return top_author
        else:
            top_author = ''
            return top_author
    
    def add_time_title(self):                 #存储题目
        try:
            for author in self.author_dict.keys():
                title = self.string_process(self.title)
                self.author_dict[author]['dynamic_data']['time_title'].append(title)
        except:
            print('time_title wrong')
    
    def add_publish_date(self):              #存储日期
        try:
            for author in self.authors:
                date = self.string_process(self.time_transform())
                self.author_dict[author]['dynamic_data']['time_publish_date'].append(date)
                self.author_dict[author]['state_data']['publish_date_stat'][date] = 1       
        except:
            print(self.publish_date)
            print('publish_date wrong')
    
    def add_publisher(self):                #存储杂志
        try:
            for author in self.authors:
                journal = self.string_process(self.publisher)
                self.author_dict[author]['dynamic_data']['time_publisher'].append(journal)
                self.author_dict[author]['state_data']['publisher_stat'][journal] = 1       
        except:
            print('publisher wrong')
            
    def add_cited_num(self):                #储存引用文献
        try:
            if self.cited_num == '':
                for author in self.authors:
                    self.author_dict[author]['dynamic_data']['time_cited_num'].append('0')
                    self.author_dict[author]['state_data']['cited_num_sum'] = 0  
            else:
                for author in self.authors:
                    cited_num = self.string_process(self.cited_num)
                    self.author_dict[author]['dynamic_data']['time_cited_num'].append(cited_num)
                    self.author_dict[author]['state_data']['cited_num_sum'] = int(cited_num)       
        except:
            print(self.cited_num)
            print('cited_num wrong')
    
    def add_time_cited(self):               #储存被引用文献
        try:
            if self.time_cited == '':
                for author in self.authors:
                    self.author_dict[author]['dynamic_data']['time_time_cited'].append('0')
                    self.author_dict[author]['state_data']['time_cited_sum'] = 0        
            else:
                for author in self.authors:
                    time_cited = self.string_process(self.time_cited).replace(',','')
                    self.author_dict[author]['dynamic_data']['time_time_cited'].append(time_cited)
                    self.author_dict[author]['state_data']['time_cited_sum'] = int(time_cited)       
        except:
            print(self.time_cited)
            print('time_cited wrong')
            
    def add_abstract(self):
        try:
            for author in self.authors:
                abstract = self.string_process(self.abstract)
                if abstract == 'no abstract':
                    self.author_dict[author]['dynamic_data']['time_abstract'].append(abstract)
                    self.author_dict[author]['state_data']['abstract_sum'] = ''
                else:
                    self.author_dict[author]['dynamic_data']['time_abstract'].append(abstract)
                    self.author_dict[author]['state_data']['abstract_sum'] = abstract       
        except:
            print('abstract wrong')
            
    def add_keyword(self):
        try:
            for author in self.authors:
                keyword = self.string_process(self.keyword)
                self.author_dict[author]['dynamic_data']['time_keyword'].append(keyword)
                for item in keyword.split(','):
                    self.author_dict[author]['state_data']['keyword_stat'][item] = 1       
        except:
            print('keyword wrong')
    
    def add_keyword_plus(self):
        try:
            for author in self.authors:
                keyword_plus = self.string_process(self.keyword_plus)
                self.author_dict[author]['dynamic_data']['time_keyword_plus'].append(keyword_plus)
                for item in keyword_plus.split(','):
                    self.author_dict[author]['state_data']['keyword_plus_stat'][item] = 1       
        except:
            print('keyword_plus wrong')
#            exit()       
    
    def add_coauthor(self):
        try:
            for author in self.authors:
                coauthor_list = deepcopy(self.authors)
                coauthor_list.remove(author)
                self.author_dict[author]['dynamic_data']['time_coauthor'].append('+'.join(coauthor_list))  
                for coauthor in self.authors:
                    self.author_dict[author]['state_data']['coauthor_stat'][coauthor] = 1                         
        except:
            print('coauthor wrong')
#            sys.exit(0)      
            
    def add_university(self):
#        try:
        for author_univer in self.author_university.split('::'):
            author = author_univer.split('@')[0].replace(', ',',').replace('  ',' ').replace('. ','.').title().replace('-','')
            universitys = author_univer.split('@')[1:]
            universitys = [self.string_process(item) for item in universitys]
            universitys = list(set(universitys))
            self.author_dict[author]['dynamic_data']['time_university'].append('+'.join(universitys))
            for university in universitys:
                self.author_dict[author]['state_data']['university_stat'][university] = 1                         
#        except:
#            print('coauthor wrong')
#            sys.exit(0)          

    def add_address(self):
        try:
            for author_addre in self.anthor_address.split('::'):
                author = author_addre.split('@')[0].replace(', ',',').replace('  ',' ').replace('. ','.').title().replace('-','')
                addresses = author_addre.split('@')[1:]
                addresses = [self.string_process(item) for item in addresses]
                addresses = list(set(addresses))
                self.author_dict[author]['dynamic_data']['time_address'].append('+'.join(addresses))
                for address in addresses:
                    self.author_dict[author]['state_data']['address_stat'][address] = 1                         
        except:
            print('coauthor wrong')
#            sys.exit(0)        
      
    def add_id(self):
        re_ResearcherID = re.compile(r"[A-Z]-\d{4}-\d{4}",re.DOTALL)
        re_ORCID = re.compile(r"http:.*/\d{4}-\d{4}-\d{4}-\d{4}",re.DOTALL)
        string = self.author_id
        if string == 'not exist':
            pass
        else:
            ident_list = [thing.replace(' ','') for thing in string.split('::')]
            identifiction_list = []
            for i,value in enumerate(ident_list):
                if ',' in value:
                    identifiction_list.append(value)
                else:
                    ident = ident_list[i-1].split('@')[:1]
                    ident.append(value)
                    ident_join= '@'.join(ident)
                    identifiction_list.append(ident_join)
            identifiction_list = [self.string_process(item) for item in identifiction_list]
            for item in identifiction_list:
                item_name = item.split('@')[0].replace(', ',',').replace('  ',' ').replace('. ','.').title().replace('-','')
                author = self.top_matching_degree(item_name)
                if author != '':
                    try:
                        ResearcherID = re_ResearcherID.findall(item)[0]
                        self.author_dict[author]['state_data']['id_stat']['researcher_id'].append(ResearcherID)
                        self.author_dict[author]['state_data']['id_stat']['researcher_id'] = list(set(self.author_dict[author]['state_data']['id_stat']['researcher_id']))
                    except:
                        pass
                    try:
                        ORCID = re_ORCID.findall(item)[0]
                        self.author_dict[author]['state_data']['id_stat']['orcid'].append(ORCID)
                        self.author_dict[author]['state_data']['id_stat']['orcid'] = list(set(self.author_dict[author]['state_data']['id_stat']['orcid']))
                    except:
                        pass
                else:
                    pass

    def add_author_attribute(self):
        #增加数据
        self.add_time_title()
        self.add_publish_date()
        self.add_publisher()
        self.add_cited_num()
        self.add_time_cited()
        self.add_abstract()
        self.add_keyword()
        self.add_keyword_plus()
        self.add_coauthor()
        self.add_university()
        self.add_address()
        self.add_id()
#        print(self.title+'    success')
                
    def init_author_dict(self):
        for author in self.authors:
            this_attribute = {'state_data':{},'dynamic_data':{}}
            this_attribute['state_data'] = {'publisher_stat':{},'publish_date_stat':{},'cited_num_sum':{},
                                            'time_cited_sum':{},'abstract_sum':{},'keyword_stat':{},
                                            'keyword_plus_stat':{},'coauthor_stat':{},'university_stat':{},
                                            'address_stat':{},'id_stat':{'researcher_id':[],'orcid':[]}}
            this_attribute['dynamic_data'] = {'time_publisher':[],'time_publish_date':[],'time_cited_num':[],
                                               'time_time_cited':[],'time_abstract':[],'time_keyword':[],
                                               'time_keyword_plus':[],'time_coauthor':[],'time_university':[],
                                               'time_address':[],'time_title':[]}
            self.author_dict[author] = this_attribute
        self.add_author_attribute()
        return self.author_dict
    

        
#########################################################
#########################################################
#########################################################
    
def csv_to_nod(path_csv,path_nod,path_pkl):
    csvnames = os.listdir(path_csv)
#    paper_all = []
    author_dict = {}
    authors_list = []
    for csvname in csvnames:
        paper_title = []                                  #转化为小写，并去除空格
        filepath = path_csv+'/'+csvname   
        with open(filepath,mode='r',encoding='ISO-8859-1',newline='') as csv_file:
            csv_reader_lines = csv.reader(csv_file)       #逐行读取csv文件
            next(islice(csv_reader_lines,1), None)   
            for one_line in csv_reader_lines: 
                one_authors = author(one_line)                         
                if one_authors.time_transform()>='1990-00':     #加入文档去重
                    if one_line[0].lower() not in paper_title:                                                            
                        paper_title.append(' '.join(one_line[0].lower().split()))
                        authors_dict_nod = one_authors.init_author_dict()
                        for key,value in authors_dict_nod.items():
                            if key == '':
                                key = value['dynamic_data']['time_title'][0]+'_anonymous'
                            if key in authors_list:
                                author_dict[key] = mix_dict(value,author_dict[key])
                                author_dict[key] = change_time_rank(author_dict[key])        #时间序列矫正
                            else:
                                authors_list.append(key)
                                author_dict[key] = value 
                else:
                    continue
#        paper_all.extend(paper_title)
    author_dict = nod_unique_deep(author_dict) 
    ##序化模型
    author_dict_pkl = open(path_pkl, 'wb')
    pkl.dump(author_dict, author_dict_pkl)
    author_dict_pkl.close()
    ##nod模型
    for key,value in author_dict.items(): 
        one_author = [key,json.dumps(value)]
        with open(path_nod+'/author_nod.csv', "a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(one_author)
            f.close()
#    return paper_all

def mix_dict(value,author_dictkeys):
    author_dictkey = deepcopy(author_dictkeys)
    #动态数据添加
    for item in author_dictkey['dynamic_data'].keys():
        author_dictkey['dynamic_data'][item].extend(value['dynamic_data'][item]) 
    #静态数据添加
    #静态摘要添加
    author_dictkey['state_data']['abstract_sum'] = author_dictkey['state_data']['abstract_sum']+value['state_data']['abstract_sum']
    #静态地址统计
    for thing in value['state_data']['address_stat'].keys():
        if thing in author_dictkey['state_data']['address_stat'].keys():
            author_dictkey['state_data']['address_stat'][thing] += value['state_data']['address_stat'][thing]
        else:
            author_dictkey['state_data']['address_stat'][thing] = value['state_data']['address_stat'][thing]            
    #静态引用数量统计
    author_dictkey['state_data']['cited_num_sum'] += value['state_data']['cited_num_sum']
    #静态合作者统计
    for thing in value['state_data']['coauthor_stat'].keys():
        if thing in author_dictkey['state_data']['coauthor_stat'].keys():
            author_dictkey['state_data']['coauthor_stat'][thing] += value['state_data']['coauthor_stat'][thing]
        else:
            author_dictkey['state_data']['coauthor_stat'][thing] = value['state_data']['coauthor_stat'][thing]
    #静态id统计
    author_dictkey['state_data']['id_stat']['orcid'].extend(value['state_data']['id_stat']['orcid'])
    author_dictkey['state_data']['id_stat']['orcid'] = list(set(author_dictkey['state_data']['id_stat']['orcid']))
    author_dictkey['state_data']['id_stat']['researcher_id'].extend(value['state_data']['id_stat']['researcher_id'])
    author_dictkey['state_data']['id_stat']['researcher_id'] = list(set(author_dictkey['state_data']['id_stat']['researcher_id']))    
    #静态附加关键词统计
    for thing in value['state_data']['keyword_plus_stat'].keys():
        if thing in author_dictkey['state_data']['keyword_plus_stat'].keys():
            author_dictkey['state_data']['keyword_plus_stat'][thing] += value['state_data']['keyword_plus_stat'][thing]
        else:
            author_dictkey['state_data']['keyword_plus_stat'][thing] = value['state_data']['keyword_plus_stat'][thing]    
    #静态关键词统计
    for thing in value['state_data']['keyword_stat'].keys():
        if thing in author_dictkey['state_data']['keyword_stat'].keys():
            author_dictkey['state_data']['keyword_stat'][thing] += value['state_data']['keyword_stat'][thing]
        else:
            author_dictkey['state_data']['keyword_stat'][thing] = value['state_data']['keyword_stat'][thing]    
    #静态发表日期统计
    for thing in value['state_data']['publish_date_stat'].keys():
        if thing in author_dictkey['state_data']['publish_date_stat'].keys():
            author_dictkey['state_data']['publish_date_stat'][thing] += value['state_data']['publish_date_stat'][thing]
        else:
            author_dictkey['state_data']['publish_date_stat'][thing] = value['state_data']['publish_date_stat'][thing]        
    #静态发表杂志统计
    for thing in value['state_data']['publisher_stat'].keys():
        if thing in author_dictkey['state_data']['publisher_stat'].keys():
            author_dictkey['state_data']['publisher_stat'][thing] += value['state_data']['publisher_stat'][thing]
        else:
            author_dictkey['state_data']['publisher_stat'][thing] = value['state_data']['publisher_stat'][thing]            
   #静态被引次数统计
    author_dictkey['state_data']['time_cited_sum'] += value['state_data']['time_cited_sum']    
   #静态大学统计
    for thing in value['state_data']['university_stat'].keys():
        if thing in author_dictkey['state_data']['university_stat'].keys():
            author_dictkey['state_data']['university_stat'][thing] += value['state_data']['university_stat'][thing]
        else:
            author_dictkey['state_data']['university_stat'][thing] = value['state_data']['university_stat'][thing]               
    return author_dictkey
    
def change_time_rank(value):
    try:
        time_list = value['dynamic_data']['time_publish_date']
        time_list = np.array([int(time.mktime(time.strptime(item, "%Y-%m"))) for item in time_list])
        time_index = np.argsort(time_list)
        for key_of_dynamic in value['dynamic_data'].keys():
            value['dynamic_data'][key_of_dynamic] = np.array(value['dynamic_data'][key_of_dynamic])[time_index].tolist()
    except:
        pass
        print(time_index)
        print(value['dynamic_data'][key_of_dynamic])
    return value    
    
def nod_unique_deep(author_dict):
    #第一步合并相同识别号的，利用识别号遍历，利用含识别号且首字母相同的之中遍历
    author_list = list(author_dict.keys())
    author_list_copy = deepcopy(author_list)
    for author in author_list_copy:
        if author_dict[author]['state_data']['id_stat']['researcher_id'] == []:
            author_list.remove(author)
    while len(author_list) > 1:
        author1 = author_list[0]
        mix_list = [author1]
        for author2 in author_list[1:]:
            if author_dict[author1]['state_data']['id_stat']['researcher_id'] == author_dict[author2]['state_data']['id_stat']['researcher_id']:
                mix_list.append(author2)
        for item in mix_list:
            author_list.remove(item)
        while len(mix_list) > 1:
            author1 = mix_list[0]
            author2 = mix_list[1]
            new_turple ,need_change_author ,short_name = deep_mix(author1,author2,author_dict[author1],author_dict[author2])
            del author_dict[author1]
            del author_dict[author2]
            author_dict[new_turple[0]] = change_time_rank(new_turple[1])
            mix_list.remove(short_name)
            for change_author in need_change_author:
                author_dict[change_author] = change_coauthor(new_turple[0],short_name,author_dict[change_author])           
    #第二步orcid有交集的进行合并
    author_list = list(author_dict.keys())
    author_list_copy = deepcopy(author_list)
    for author in author_list_copy:
        if author_dict[author]['state_data']['id_stat']['orcid'] == []:
            author_list.remove(author)
    while len(author_list) > 1:
        author1 = author_list[0]
        mix_list = [author1]
        list_len = len(author_dict[author1]['state_data']['id_stat']['orcid'])
        large_list_len = len(author_dict[author1]['state_data']['id_stat']['orcid'])
        large_list = author1        
        for author2 in author_list[1:]:
            if list(set(author_dict[author1]['state_data']['id_stat']['orcid']).intersection(set(author_dict[author2]['state_data']['id_stat']['orcid']))) != [] :
                mix_list.append(author2)
                if len(author_dict[author2]['state_data']['id_stat']['orcid']) > large_list_len:
                    large_list = author2
                    large_list_len = len(author_dict[author2]['state_data']['id_stat']['orcid'])
        author1 = large_list
        while  large_list_len > list_len:
            list_len = len(author_dict[author1]['state_data']['id_stat']['orcid'])
            large_list_len = len(author_dict[author1]['state_data']['id_stat']['orcid'])
            large_list = author1        
            for author2 in author_list:
                if list(set(author_dict[author1]['state_data']['id_stat']['orcid']).intersection(set(author_dict[author2]['state_data']['id_stat']['orcid']))) != [] :
                    mix_list.append(author2)
                    if len(author_dict[author2]['state_data']['id_stat']['orcid']) > large_list_len:
                        large_list = author2
                        large_list_len = len(author_dict[author2]['state_data']['id_stat']['orcid']) 
            mix_list = list(set(mix_list))
            author1 = large_list           
        for item in mix_list:
            author_list.remove(item)
        while len(mix_list) > 1:
            author1 = mix_list[0]
            author2 = mix_list[1]
            new_turple ,need_change_author ,short_name = deep_mix(author1,author2,author_dict[author1],author_dict[author2])
            del author_dict[author1]
            del author_dict[author2]
            author_dict[new_turple[0]] = change_time_rank(new_turple[1])
            mix_list.remove(short_name)
            for change_author in need_change_author:
                author_dict[change_author] = change_coauthor(new_turple[0],short_name,author_dict[change_author])           
    #第三步姓名相似度高的进行合并，第一是姓名包含，第二个是衡量字符串的相似度。合作者相似交集，大学相似交集，地址相似交集
    #相似度较低，较差的进行人眼识别。
    author_list_dict = divide_by_first_letter(author_dict) #按首字母切分字典
    for key,value in author_list_dict.items():
        author_list = deepcopy(value)  
        while len(author_list)>1:
            print(len(author_list))
            author1 = author_list[0] 
            mix_list = find_sim_by_name(author1, author_list)
            if len(mix_list) == 0:
                author_list.remove(author1)
            else:
                mix_list_true = true_sim_by_info(author_dict, mix_list, author1) #根据信息确定真实相似

                if len(mix_list_true) != 0:  
                    min_list = list(set(mix_list).difference(set(mix_list_true)))
                    if len(min_list) != 0 :
                        mix_list_ture_copy = deepcopy(mix_list_true)
                        for author1s in mix_list_ture_copy:
                            mix_list_true.extend(true_sim_by_info(author_dict, min_list, author1s))
                        mix_list_true = list(set(mix_list_true))
                        min_list = list(set(min_list).difference(set(mix_list_true)))
                        
                    if len(min_list) != 0 and mix_list_true != mix_list_ture_copy:  #这里本来是while的，精髓被破坏
                        mix_list_ture_copy = deepcopy(mix_list_true)
                        for author1s in mix_list_ture_copy:
                            mix_list_true.extend(true_sim_by_info(author_dict, min_list, author1s))
                        mix_list_true = list(set(mix_list_true))
                    
                    mix_list_true, author_list = upgrade_mix_author(mix_list_true, author_list) #更新两个list，包括添加作者本身，以及剔除author_list中的mix
                    author_dict = mix_in_dict(mix_list_true,author_dict)                        #更新字典
                    print(len(author_list))

                else:
                    author_list.remove(author1)
                    print(len(author_list))            
                    
    return author_dict
                
#    print(author1+' , '+author2)
#    compRawStr = input('y or n   \n')     #键盘读入
#    if compRawStr == 'y':
#        deep_mix()
#    else:
#        pass    
    


def deep_mix(author1,author2,author_dictauthor1s,author_dictauthor2s):
    author_dictauthor1 = deepcopy(author_dictauthor1s)
    author_dictauthor2 = deepcopy(author_dictauthor2s)
    new_turple = []
    if len(author1) > len(author2) :
        new_turple.append(author1)
        short_name = author2
        need_change_author = list(author_dictauthor2['state_data']['coauthor_stat'].keys())
        need_change_author.remove(author2)
        author_dictauthor2['state_data']['coauthor_stat'][new_turple[0]] = author_dictauthor2['state_data']['coauthor_stat'].pop(short_name)
    else:
        new_turple.append(author2)
        short_name = author1        
        need_change_author = list(author_dictauthor1['state_data']['coauthor_stat'].keys())
        need_change_author.remove(author1)
        author_dictauthor1['state_data']['coauthor_stat'][new_turple[0]] = author_dictauthor1['state_data']['coauthor_stat'].pop(short_name)
    new_turple.append(mix_dict(author_dictauthor1,author_dictauthor2))        
    return new_turple ,need_change_author ,short_name

def change_coauthor(new_turple0,short_name,author_dictchange_author):
    #动态合作者
    author_dictchange_author['dynamic_data']['time_coauthor'] = [item.replace(short_name,new_turple0) for item in author_dictchange_author['dynamic_data']['time_coauthor']]
    #静态合作者
    if  new_turple0 in author_dictchange_author['state_data']['coauthor_stat']:
        author_dictchange_author['state_data']['coauthor_stat'][new_turple0] += author_dictchange_author['state_data']['coauthor_stat'].pop(short_name)
    else:
        author_dictchange_author['state_data']['coauthor_stat'][new_turple0] = author_dictchange_author['state_data']['coauthor_stat'].pop(short_name)
    return author_dictchange_author

def name_familiar(author1,author2):
    try:
        if ',' in author1:
            author1_name = author1.split(',')[0].lower()
            author1_letter = [item[0] for item in author1.split(',')][1].lower()
        elif '.' in author1:
            author1_name = author1.split('.')[0].lower()
            author1_letter = [item[0] for item in author1.split('.')][1].lower()
        else:
            author1_name = author1.split()[0].lower()
            author1_letter = [item[0] for item in author1.split()][1].lower()
      
        if ',' in author2:
            author2_name = author2.split(',')[0].lower()
            author2_letter = [item[0] for item in author2.split(',')][1].lower()
        elif '.' in author2:
            author2_name = author2.split('.')[0].lower()
            author2_letter = [item[0] for item in author2.split('.')][1].lower()                
        else:
            author2_name = author2.split()[0].lower()
            author2_letter = [item[0] for item in author2.split()][1].lower()
        if  difflib.SequenceMatcher(None, author1_name, author2_name).quick_ratio()> 0.9:
            if  author1_letter == author2_letter:
                degree = difflib.SequenceMatcher(None, author1, author2).quick_ratio()
            else:
                degree = 0
        else:
            degree = 0
    except:
        degree = difflib.SequenceMatcher(None, author1, author2).quick_ratio()-0.25
    return degree

def coauthor_familiar(author1,candidate,author_dictauthor1,author_dictcandidate):   
    #合作者相似
    try:
        author1_list = deepcopy(list(author_dictauthor1['state_data']['coauthor_stat'].keys()))
        candidate_list = deepcopy(list(author_dictcandidate['state_data']['coauthor_stat'].keys()))
        author1_list.remove(author1)
        candidate_list.remove(candidate)
        candidate_bool = 0
        for item in author1_list:
            for thing in candidate_list:
                if name_familiar(item,thing) >= 0.80 :
                    candidate_bool += 1
        candidate_bool = bool(candidate_bool)
    except:
        candidate_bool = False
    return candidate_bool

def university_familiar(author1,candidate,author_dictauthor1,author_dictcandidate):
    #大学相似注意unknown
    try:
        author1_list = deepcopy(list(author_dictauthor1['state_data']['university_stat'].keys()))
        candidate_list = deepcopy(list(author_dictcandidate['state_data']['university_stat'].keys()))
        if 'Unknow' in author1_list:
            author1_list.remove('Unknow')
        if 'Unknow' in candidate_list:
            candidate_list.remove('Unknow')
        university_bool = 0                        
        for item in author1_list:
            for thing in candidate_list:
                if difflib.SequenceMatcher(None, item.lower(), thing.lower()).quick_ratio() > 0.82:
                    university_bool += 1
        university_bool = bool(university_bool)                       
    except:
        university_bool = False  
    return university_bool

def address_familiar(author1,candidate,author_dictauthor1,author_dictcandidate):
    #地址相似注意unknown
    try:
        author1_list = deepcopy(list(author_dictauthor1['state_data']['address_stat'].keys()))
        candidate_list = deepcopy(list(author_dictcandidate['state_data']['address_stat'].keys()))
        if 'Unknow' in author1_list:
            author1_list.remove('Unknow')
        if 'Unknow' in candidate_list:    
            candidate_list.remove('Unknow')
        address_bool = 0                         
        for item in author1_list:
            for thing in candidate_list:
                if difflib.SequenceMatcher(None, item.lower(), thing.lower()).quick_ratio() > 0.85:
                    address_bool +=1
        address_bool = bool(address_bool)                       
    except:
        address_bool = False
    return address_bool

'''
对大学名称的统一，有利于研究大学之间的合作网络，待定
def unify_univesity() :
'''
def divide_by_first_letter(author_dict):
    author_list = list(author_dict.keys())
    author_list_dict = {}
    for author_name in author_list:
        if author_name[0] in author_list_dict.keys():
            author_list_dict[author_name[0]].append(author_name)
        else:
            author_list_dict[author_name[0]] = [author_name]
    return author_list_dict

def find_sim_by_name(author1, author_list):
    mix_list = []
    for author2 in author_list[1:]:
        if name_familiar(author1,author2) > 0.70 :
            mix_list.append(author2)
    return mix_list

def true_sim_by_info(author_dict, mix_list, author1):
    mix_list_true = []
    mix_list = find_sim_by_name(author1, mix_list)
    if mix_list:
        for candidate in mix_list:
            if candidate not in author_dict[author1]['state_data']['coauthor_stat'].keys():
                candidate_bool = coauthor_familiar(author1,candidate,author_dict[author1],author_dict[candidate])
                university_bool = university_familiar(author1,candidate,author_dict[author1],author_dict[candidate])
                address_bool = address_familiar(author1,candidate,author_dict[author1],author_dict[candidate])
                if candidate_bool or (university_bool and address_bool):
                     mix_list_true.append(candidate)
        return mix_list_true
    else:
        return []

def upgrade_mix_author(mix_list_true, author_list):
    author1 = author_list[0]
    mix_list_true.append(author1) 
#   print(author1)
#   print(mix_list_true)
    for item in mix_list_true:
        author_list.remove(item) 
    return mix_list_true, author_list

def mix_in_dict(mix_list_true,author_dict):
    while len(mix_list_true) > 1:
        author1 = mix_list_true[0]
        author2 = mix_list_true[1]
        new_turple ,need_change_author ,short_name = deep_mix(author1,author2,author_dict[author1],author_dict[author2])
        del author_dict[author1]
        del author_dict[author2]
        author_dict[new_turple[0]] = change_time_rank(new_turple[1])
        mix_list_true.remove(short_name)
        for change_author in need_change_author:
            author_dict[change_author] = change_coauthor(new_turple[0],short_name,author_dict[change_author])
    return author_dict

if __name__ == '__main__':  
    os.chdir("D:/bigdatahw/pan_paper/潘老师")
    path_csv = 'D:/bigdatahw/pan_paper/潘老师/original_data(corresponding to journal nod)'
    path_nod = 'D:/bigdatahw/pan_paper/潘老师/nod'
    path_pkl = 'D:/bigdatahw/pan_paper/潘老师/pkl/author_dict.pkl'
    author_dict = read_pkl(path_pkl)
#    csv_to_nod(path_csv,path_nod)
    csv_to_nod(path_csv,path_nod,path_pkl)

