#Author-Kushagra Shukla
from flask import Flask, request, jsonify , render_template
import os
import pickle
import json
import numpy as np

__locations = None
__data_columns = None
__model = None

def get_estimated_price(location,sqft,bhk,bath):
    try:
        loc_index = __data_columns.index(location.lower())
    except:
        loc_index = -1

    x = np.zeros(len(__data_columns))
    x[0] = sqft
    x[1] = bath
    x[2] = bhk
    if loc_index>=0:
        x[loc_index] = 1

    return round(__model.predict([x])[0],2)

def load_saved_artifacts():
    print("loading saved artifacts...start")
    global  __data_columns #will be used as a list
    global __locations #will be used as a list

    json_path=os.path.join(app.root_path,'home.json')
    with open(json_path, "r") as f:
        __data_columns = json.load(f)['data_columns']
        __locations = __data_columns[3:]  # first 3 columns are sqft, bath, bhk so we ignore them and take only the locations

    global __model
    pickle_path=os.path.join(app.root_path,'home.pickle')
    if __model is None:
        with open(pickle_path, 'rb') as f:
            __model = pickle.load(f)
    print("loading saved artifacts...done")

app = Flask(__name__)
@app.route('/')
def home():
   return render_template('app.html')


@app.route('/get_location_names', methods=['GET']) #Routine to get location names
def get_location_names():
    load_saved_artifacts()
    response = jsonify({
        'locations': __locations
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/predict_home_price', methods=['GET', 'POST'])
def predict_home_price():
    total_sqft = float(request.form['total_sqft'])
    location = request.form['location']
    bhk = int(request.form['bhk'])
    bath = int(request.form['bath'])

    response = jsonify({
        'estimated_price': get_estimated_price(location,total_sqft,bhk,bath)
    })
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

if __name__ == "__main__":
    print("Starting Python Flask For Home Price Prediction...")
    app.run()
