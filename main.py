from flask import Flask, request, jsonify
import json
from slouchy_main import * 
import numpy as np
from flask_cors import CORS
from collections import namedtuple
from flask_restful import Resource, Api
from PIL import Image
import io
import cv2
import base64 
import numpy as np
app = Flask(__name__)
CORS(app)
api = Api(app)

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

# @app.route('/photo', methods = ['POST'])
# def recieve_photo():
#   print request.args.get('photo')
#   response = {}
#   response['status'] = 1
#   return jsonify(response)
# Take in base64 string and return PIL image
def stringToImage(base64_string):
    imgdata = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(imgdata))

# convert PIL Image to an RGB image( technically a numpy array ) that's compatible with opencv
def toGRAY(image):
    return cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)

class Ner(Resource):
  def post(self):
    print "bikram"
    # print request.files['photo']
    photo = request.form['photo']
    image = stringToImage(photo.split(",")[1])
    image.show()
    y = toGRAY(image)
    # print str(y)
    response = {}
    maybe_image           = getMaybeImage(y)
    maybe_current_posture = determine_posture(maybe_image)

    if maybe_current_posture.success:
      distance_reference = str(maybe_current_posture.result.get('distance'))
      #config.config_file['MAIN']['distance_reference'] = distance_reference
      print("Reference value detected as:", maybe_current_posture.result)
      response['status'] = 1
      if request.form['distance_reference'] == 0:
        response['distance_reference'] = distance_reference
      else:
        maybe_slouching = detect_slouching(maybe_current_posture, distance_reference, thoracolumbar_tolerance, cervical_tolerance)
        slouching_results  = maybe_slouching.result
        response['slouching'] = slouching_results.get('body_slouching')
        response['head_tilt'] = slouching_results.get('head_tilting')
    else:
      print("Error:", maybe_current_posture.result)
      response['status'] = 0

    return jsonify(response)
api.add_resource(Ner,'/photo')

if __name__ == '__main__':
  app.run(debug = True)
