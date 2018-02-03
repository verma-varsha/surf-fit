from flask import Flask, request, jsonify
import json
from slouchy_main import * 
import numpy as np
from flask_cors import CORS
from collections import namedtuple
app = Flask(__name__)
CORS(app)

#THINGS TO BE RECIEVED VIA POST REQUEST
imageMatrix = np.loadtxt("matrix.txt")
imageMatrix = np.array(imageMatrix, dtype='uint8')
distance_reference = 248.965861114
thoracolumbar_tolerance = 0.05
cervical_tolerance = 0.35

Maybe = namedtuple('Maybe', ['success','result'])
#MaybeImage = (True, imageMatrix)

def getMaybeImage(grayimage):
  return Maybe(True, grayimage)

#@app.route('/', methods = ['POST'])
@app.route('/')
def hello_world():
  response = {}
  MaybeImage = getMaybeImage(imageMatrix)
  maybe_posture   = determine_posture(MaybeImage)
  maybe_slouching = detect_slouching(maybe_posture, distance_reference, thoracolumbar_tolerance, cervical_tolerance)

  if maybe_slouching.success:
        slouching_results  = maybe_slouching.result
        response['slouching'] = slouching_results.get('body_slouching')
        response['head_tilt'] = slouching_results.get('head_tilting')
        response['status'] = 1
  else:
    response['status'] = 0
  return jsonify(response)

#@app.route('/setup', methods = ['POST'])
#def distance_setup():
@app.route('/setup')
def setup():
  response = {}
  maybe_image           = getMaybeImage(imageMatrix)
  maybe_current_posture = determine_posture(maybe_image)

  if maybe_current_posture.success:
    distance_reference = str(maybe_current_posture.result.get('distance'))
    #config.config_file['MAIN']['distance_reference'] = distance_reference
    print("Reference value detected as:", maybe_current_posture.result)
    response['status'] = 1
    response['distance_reference'] = distance_reference
  else:
    print("Error:", maybe_current_posture.result)
    response['status'] = 0

  return jsonify(response)

if __name__ == '__main__':
  app.run(host="0.0.0.0",debug = True)
