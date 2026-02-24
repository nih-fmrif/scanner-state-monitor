
from flask import Flask, jsonify, request

app = Flask(__name__)



# Use dictionary to represent scanner info and state with a set of key-value pairs
scanner_state_info = { 'scanner AE Title': 'fmrif3tc', 'state': 'decommissioned' }



# Default for ReST GET method
@app.route('/scanner_state')

def get_info_and_state():

   return jsonify(scanner_state_info)



# Use POST to add a new entry to JSON published to ReST API.  See
# comment below for update_ / PUT / PATCH.
@app.route('/scanner_state', methods=['POST'])

def add_info_and_state():

   scanner_state_info.update(request.get_json())
   # return '', 204
   return jsonify(scanner_state_info)



# Use PUT and PATCH to update an entry in JSON published to ReST API.
# This still uses the same 'update' method for dictionaries, but with
# the methods separarted right now, it can leave open the possibility
# to use another iterator in the future, if needed.
@app.route('/scanner_state', methods=['PUT', 'PATCH'])

def update_info_and_state():

   scanner_state_info.update(request.get_json())
   # return '', 204
   return jsonify(scanner_state_info)

