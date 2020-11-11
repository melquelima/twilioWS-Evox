
from app import app,db
from flask import request,jsonify
# from app.models.uteis import mallowList
from app.models.Outros.uteis import fields_required
from flask_expects_json import expects_json
from twilio.rest import Client
# import pandas
# import xlrd
import json
import os

account_sid = 'ACd4a2461a72af4e16ad1fe73155c8db14'
auth_token = 'c52a84b8be8bd135b06516aeb8c611c7'
client = Client(account_sid, auth_token)

schema = {
  "type": "object",
  "properties": {
    "mensagem": { "type": "string","minLength": 10,"maxLength": 50},
    "destinatarios": { 
    "type": "array", 
    "minItems": 1,
    "items": {
        "type": "string",
        "minLength": 10,
        "maxLength": 15,
        "pattern": "^\+\d{2}"
    }
}
  },
  "required": ["mensagem","destinatarios"]
}
@app.route("/api/sendMessages",methods=["POST"])
@expects_json(schema)
# @fields_required({"numero":str,"mensagem":str},True)
def sendMessages():
    try:
        resp = {"status":"completo","relatorio":[]}
        values = request.get_json()
        for numb in values["destinatarios"]:
            send(values["mensagem"],numb)
            resp["relatorio"].append({numb:"OK"})
        return jsonify(resp)
    except:
        return "NOK",400

def send(message,to):
    message = client.messages.create(
                              body=message,
                              from_='+17864606607',
                              to=to
                          )
    a = 1

@app.route('/strict')
@expects_json()
def strict():
    return "This view will return 400 if mimetype is not 'application/json'"