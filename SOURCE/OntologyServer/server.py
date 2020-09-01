from flask import Flask, render_template, request,jsonify
from rdflib import Graph
from rdflib.namespace import DCTERMS,Namespace
from bot import AdobeAPI
from OpenSSL import SSL
import json

app = Flask(__name__)
BOT = AdobeAPI()
 

def search_intent_ask_how(operator, list_entity, context):
	res = BOT.search_how(operator,list_entity,context)
	return res

def search_intent_ask_what(list_entity, context):
    res = BOT.search_what(list_entity,context)
    #print(res)
    return res

def search_steps_process(process):
    res = BOT.search_step(process)
    return res

@app.route("/ask_what", methods=["POST"])
def ask_what():
    data = request.get_json()
    res = search_intent_ask_what(data['entity'], data['context']) # entity là thuộc tính của json 
    return jsonify(resp = res)


@app.route("/ask_how", methods=["POST"])
def ask_how():
	data = request.get_json()
	res = search_intent_ask_how(data['operator'], data['entity'], data['context']) # opeator là phương thức, entity là list thuộc tính
	return jsonify(resp = res)

@app.route("/ask_step", methods=["POST"])
def ask_steps():
    data = request.get_json()
    res = search_steps_process(data['process'])
    return jsonify(resp = res)

if __name__ == "__main__":
    #app.run( host='172.29.64.182', port=274, debug = True, ssl_context="adhoc")
	app.run(debug = True)

