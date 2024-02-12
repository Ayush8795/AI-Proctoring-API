from flask import Flask,jsonify,request,redirect
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import scorer
load_dotenv()


app= Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

connection_string= os.getenv('CONNECTION_STRING')
client= MongoClient(connection_string)


db= client['test']
col= db['candidatedetails']


key= os.getenv('API_KEY_ID')
access_key= os.getenv('API_SECRET_KEY')
bucket_name='dheerajtest1'



@app.before_request
def before_request():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = app.make_default_options_response()
    
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization,access-control-allow-origin')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response




@app.route('/',methods=['GET'])
def welcome():
     return jsonify('working')


@app.route('/proctor/<user_id>/',methods=['GET'])
def proctor(user_id):
    print('Fetching videos and frames...')
    scorer.score_update(user_id)
    for vid in os.listdir('video_store'):
        vp= os.path.join('video_store',vid)
        os.remove(vp)
    
    return jsonify('proctoring_data_updated')


if __name__=='__main__':
    app.run(host='0.0.0.0',port=8000)