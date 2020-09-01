import argparse
import logging

import pandas as pd
from rasa_core import utils
from rasa_core.agent import Agent
from rasa_core.policies.memoization import MemoizationPolicy
from owlready2 import *
import numpy as np
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

def f(x):
    s = x.value_counts()
    return np.nan if len(s) == 0 else s.index[0]

class AdobeAPI(object):
    def __init__(self):
        my_world = World()
        my_world.get_ontology("ChatbotTechnique.owl").load()
        self.graph = my_world.as_rdflib_graph()
        self.namespace = "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\
                            PREFIX owl: <http://www.w3.org/2002/07/owl#>\
                            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\
                            PREFIX ex: <http://fit.hcmus.edu.vn/ChatbotForTechniqueApp#>"
 

    #def what(self,obj):
    #    query = self.namespace + "SELECT DISTINCT ?Question ?Response ?Video ?Image \
    #    (count(?Object) as ?countObject) WHERE {"
    #    temp = "?Question rdf:type ex:What."
    #    for i in obj:
    #        temp += "?Question ex:hasObject ex:" + i +"."
            
    #    query += temp + "{?Question ex:hasVideo ?Video.}\
    #    UNION {?Question ex:Response ?Response.}UNION\
    #    {?Question ex:hasImage ?Image.} UNION {?Question ex:hasObject ?Object.}}\
    #     GROUP BY ?Question ?Response ?Video ?Image"
        
    #    return query

    def what(self, obj, context):
        query = self.namespace + "SELECT DISTINCT ?Question ?Response ?Video ?Image \
        (count(?Object) as ?countObject) WHERE {"
        temp = "?Question rdf:type ex:What."
        for i in obj:
            temp += "?Question ex:hasObject ex:" + i +"."
        for k in context:
            temp += "?Question ex:hasContext ex:" + k + "."
            
        query += temp + "{?Question ex:hasVideo ?Video.}\
        UNION {?Question ex:Response ?Response.}UNION\
        {?Question ex:hasImage ?Image.} UNION {?Question ex:hasObject ?Object.}}\
         GROUP BY ?Question ?Response ?Video ?Image"
        
        return query


    def how(self,operate,obj,context):
        query = self.namespace + "SELECT DISTINCT ?Question ?Response ?Video ?Process\
         ?Image ((count(?Object)+count(?Ope)) as ?countObject)  WHERE {"
        temp = "?Question rdf:type ex:How."
        for j in operate:
            temp += "?Question ex:hasOperation ex:" + j + "."
        for i in obj:
            temp += "?Question ex:hasObject ex:" + i + "."
        if context is not None:
            for k in context:
                temp += "?Question ex:hasContext ex:" + k + "."
            
        query += temp + "{?Question ex:hasVideo ?Video.}\
        UNION {?Question ex:Response ?Response.}\
        UNION {?Question ex:hasImage ?Image.} \
        UNION {?Question ex:hasProcess ?Process.} \
        UNION {?Question ex:hasObject ?Object.} \
        UNION {?Question ex:hasOperation ?Ope.}} \
        GROUP BY ?Question ?Response ?Video ?Image ?Process ?ProcessResponse"
        return query
    
    def getTalk(self, process):
        query = self.namespace + "SELECT DISTINCT ?Response ?Video ?Image ?Talk\
        ?TalkResponse ?TalkVideo ?TalkImage WHERE {"
        
        query += "{ex:" + process + " ex:hasVideo ?Video.} \
        UNION {ex:" + process + " ex:Response ?Response.} \
        UNION {ex:" + process + " ex:hasImage ?Image} \
        UNION {ex:" + process + " ex:hasStep ?Talk. \
        {?Talk ex:Response ?TalkResponse} \
        UNION {?Talk ex:hasImage ?TalkImage} \
        UNION {?Talk ex:hasVideo ?TalkVideo}}}"

        return query

    def findObject(self,entity, context):
        results = list(self.graph.query(self.what(entity,context)))
        #results = np.asarray(results)
        content = []
        #number_Object = []
        #respone = []
        #video = []
        #image = []
        #min_position = []
        #print(str(results[0]))
        QUES_Temp = []
        QUES = []
        RES = []
        VIDEO = []
        IMAGE = []
        COUNT = []
        for i in results:
            QUES_Temp.append(str(i[0]))
            RES.append(str(i[1]))
            VIDEO.append(str(i[2]))
            IMAGE.append(str(i[3]))
            COUNT.append(int(str(i[4])))
        #df = pd.DataFrame(results, columns = ['Question', 'Respone',  
        #                            'Video', 'Image', 
        #                            'Count'])
        #print(QUES[0])

        for item in QUES_Temp:
            kq = item.rfind('What')
            item = item.replace('_',' ')
            item = item.title()
            QUES.append(item[kq+5:])

        df = pd.DataFrame(dict(
            Question=QUES,
            Response=RES,
            Video=VIDEO,
            Image=IMAGE,
            Count=COUNT
        ))[['Question', 'Response', 'Video', 'Image', 'Count']]

        #print(df['Image'][0])
        #df.replace('None', np.nan)
        #print(df)
        df = df.replace(0, np.nan)
        df = df.replace('None', np.nan)
        df['Count'] = df['Count'].fillna(df.groupby('Question')['Count'].transform('mean'))
        

        df["Image"] = df.groupby("Question")["Image"].transform(f)
        df["Video"] = df.groupby("Question")["Video"].transform(f)
        #pd.concat([
        #    _df_[_df_.duplicated()],
        #    _df_.loc[_df_.drop_duplicates(keep=False).index]
        #])
        df = df.replace(np.nan, 'None')
        df.drop_duplicates(subset =["Question"], 
                     keep = "first", inplace = True)

        
        df.index = range(len(df)) # set lại cái index theo đúng thứ tự
        min_value = df['Count'].min()
        a = np.where(df['Count'] == min_value)[0]
        print(len(a))

        #print(min_value)
        #print(df)
        #print(_df_['Question'][2])
        #print(len(df.index))
        #print(_df_['Count'][0])
        #print(len(df.index))

        for i in range (0,len(df.index)):
            #print(df['Count'][i])
            if df['Count'][i] == min_value:
                if len(a) == 1:
                    temp = []
                    temp.append(df['Question'][i])
                    if df['Question'][i] != 'None':
                        content.append(("Type",temp))
                    if df['Video'][i] != 'None':
                        #print(df['Video'][i])
                        #print(type(df['Video'][i]))
                        content.append(("Video",df['Video'][i]))

                    if df['Response'][i] != 'None':
                        #print(df['Response'][i])
                        content.append(("Response", df['Response'][i]))

                    if df['Image'][i] != 'None':
                        content.append(("Image", df['Image'][i]))
                #else:
                #    content.append(("Type", df['Question'][i]))
        if len(a) != 1:
            _temp =[]
            for i in df['Question']:
                _temp.append(i)    
            content.append(("Type", _temp))
        #print(_df_['Image'][0])
        
        #for result in results:
            
        #    if str(result.Video) != 'None':
        #        video.append(str(result.Video))
        #    if str(result.Image) != 'None':
        #        image.append(str(result.Image))
        #    if str(result.Image) == 'None' and str(result.Response) != 'None':
        #        image.append('None')
        #    if str(result.Response) != 'None':    
        #        respone.append(str(result.Response))
        #    if int(str(result.countObject)) != 0:
        #        number_Object.append(int(str(result.countObject)))
        
        #print(len(number_Object))
        #a = np.array(number_Object) 
        #min_position = np.where(a == a.min())
        #print(min_position)
        #for i in min_position[0]:
        #    if video:
        #        content.append(("Video",video[i]))
        #    if image:
        #        content.append(("Image", image[i]))
        #    content.append(("Respone",respone[i]))

        #res = []
        #for item in content:
        #    if item != 'None':
        #        res.append(item)
        #print(content[1])
        #res = []
        #for item in content:
        #    if item != 'None':
        #        res.append(item)

        #return res
        return content

    def findProcess(self, operator, entity_list, context):
        results = list(self.graph.query(self.how(operator,entity_list,context)))
        content = []
        process = []
        if results:
            for result in results:
                if str(result.Process) != 'None':
                    #print(str(result.Process))
                    temp = str(result.Process)
                    _temp = temp.rfind('#')
                    if _temp != -1:
                        temp = temp.replace('_',' ')
                        process.append(temp[_temp+1:])

                if str(result.Video) != 'None':
                    content.append(("Video",str(result.Video)))
                if str(result.Response) != 'None':    
                    content.append(("Respone",str(result.Response)))
        
        if len(process) == 1:
            process[0] = process[0].replace(' ', '_')
            step_list = self.search_step(process[0])
            if step_list:
                return step_list
            else:
                return content
        else:
            if  process:
                content.append(("Process",process))
                res = []
                for item in content:
                    if item != 'None':
                        res.append(item)

                return res
            else:
             return process

    def findStepsOfProcess(self, process):
        results = list(self.graph.query(self.getTalk(process)))
        content = []
        list_step_image = []
        list_step_video = []
        list_step = []
        temps = []
        for result in results:
            if str(result.Response) != 'None':
                content.append(("Respone",str(result.Response)))

            if str(result.Video) != 'None':
                content.append(("Video", str(result.Video)))

            if str(result.Image) != 'None':
                content.append(("Image", str(result.Image)))

            temp_str = str(result.Talk)
            pos = temp_str.rfind('step')
            if pos != -1:
                step_number = temp_str[pos+4:]
                if str(result.TalkResponse) != 'None':
                    #temp = (int(step_number), str(result.TalkResponse))
                    temps.append([int(step_number),str(result.TalkResponse)])
                    #temps.append({'stt': int(step_number),'content' : str(result.TalkResponse)})

            if str(result.TalkImage) != 'None':
                list_step_image.append(str(result.TalkImage))
            if str(result.TalkVideo) != 'None':
                list_step_video.append(("TalkVideo",str(result.TalkVideo)))
            
               
        #steps = sorted(temps, key=lambda x: str(x[0]))
        #print (len(temps))
        #print(temps[0][0])
        if len(temps) != 0:
            for i in range (0,len(temps)):
                if list_step_image and not list_step_video: 
                    if i <= len(list_step_image) -1:
                        list_step.append({'stt': temps[i][0], 'TalkImage': list_step_image[i], 'content': temps[i][1]})
                    else:
                        list_step.append({'stt': temps[i][0],'content' : temps[i][1]})
                elif list_step_video and not list_step_image:
                    if i <= len(list_step_video) -1:
                        list_step.append({'stt': temps[i][0], 'TalkVideo': list_step_video[i], 'content': temps[i][1]})
                    else:
                        list_step.append({'stt': temps[i][0],'content' : temps[i][1]})
                elif list_step_video and list_step_image:
                    if i <= len(list_step_image) and i <= len(list_step_video):
                        list_step.append({'stt': temps[i][0], 'TalkImage': list_step_image[i], 'TalkVideo': list_step_video[i], 'content': temps[i][1]})
                    else:
                        list_step.append({'stt': temps[i][0],'content' : temps[i][1]})
                else:
                    list_step.append({'stt': temps[i][0],'content' : temps[i][1]})
        
        res = []
        if list_step:        
            content.append(("Step",list_step))
       
            for item in content:
                if item != 'None':
                    res.append(item)

        return res

    def search_what(self, info, context):
        return self.findObject(info,context)

    def search_how(self, operator, info,context):
        return self.findProcess(operator,info,context)

    def search_step(self, process):
        return self.findStepsOfProcess(process)

# neu list process <= 1 thi print luon ca step
#a = AdobeAPI()
#list_array =[]
#op = []
#context = []
#op.append("Install")
#op.append("Correct")
#op.append("Bend")
#j = 'Live_3D_Painting'
#list_array.append("Photoshop")#
#list_array.append("Color")
#list_array.appeund("Fuse")#
#context.append("Ubuntu")
#context.append("CS6")
#list_array.append("Black_and_White_Image")

#list_array.append("White")

#print(len(a.search(list_arrapay)))
#res = a.search_how(op,list_array,context)
#print(res)
