import boto3
import os
import cam

import time
from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

key= os.getenv('API_KEY_ID')
access_key= os.getenv('API_SECRET_KEY')
connection_string= os.getenv('CONNECTION_STRING')

s3 = boto3.client('s3', aws_access_key_id= key, aws_secret_access_key= access_key)
bucket_name='dheerajtest1'
client= MongoClient(connection_string)




def score_update(user_id):
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix= user_id)

    db= client['test']
    col= db['candidatedetails']
    user= ObjectId(user_id)

    # videos=[]
    score_dic= {
        "role_related":[],
        "creative_related":[],
        "situation_related":[] 
    }
    for obj in response['Contents']:
        vid= os.path.split(obj['Key'])[1]
        print(vid)
        if vid != '':
            word= vid.split('-')[0]
            vidpath= f'video_store/{vid}'
            s3.download_file(bucket_name, obj['Key'], vidpath)
            tup= list(cam.run(vidpath))
            if word=='creative':
                score_dic['creative_related'].append(tup)
            elif word=='role':
                score_dic['role_related'].append(tup)
            elif word=='situation':
                score_dic['situation_related'].append(tup)
            

    print(score_dic)        
    print('Inserting in role-related...')

    ins= col.update_one(
          {"user":user},
          {"$set":{"role_related.proc":score_dic['role_related']}}
          ).acknowledged
    
    print(ins)

    print('Inserting in creative-related...')

    ins= col.update_one(
          {"user":user},
          {"$set":{"creative_related.proc":score_dic['creative_related']}}
          ).acknowledged
    
    print(ins)

    print('Inserting in situation-related...')

    ins= col.update_one(
          {"user":user},
          {"$set":{"situation_related.proc":score_dic['situation_related']}}
          ).acknowledged
    
    print(ins)

    print('Done...')