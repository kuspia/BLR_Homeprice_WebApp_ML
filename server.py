#Author-Kushagra Shukla
from flask import Flask, request, jsonify , render_template
import util
import pickle
import json
import numpy as np


locations = None
data_columns = None
model = None

def get_estimated_price(location,sqft,bhk,bath):
    try:
        loc_index = data_columns.index(location.lower())
    except:
        loc_index = -1

    x = np.zeros(len(data_columns))
    x[0] = sqft
    x[1] = bath
    x[2] = bhk
    if loc_index>=0:
        x[loc_index] = 1

    return round(model.predict([x])[0],2)

def load_saved_artifacts():
    print("loading saved artifacts...start")
    global data_columns #will be used as a list
    global locations #will be used as a list

    with open("home.json", "r") as f:
        data_columns = json.load(f)['data_columns']
        locations = data_columns[3:]  # first 3 columns are sqft, bath, bhk so we ignore them and take only the locations

    global model
    if model is None:
        with open('home.pickle', 'rb') as f:
            model = pickle.load(f)
    print("loading saved artifacts...done")

def get_location():
    return locations

def get_data_columns():
    return data_columns





app = Flask(__name__)
@app.route('/')
def home():
   return render_template('app.html')


@app.route('/get_location_names', methods=['GET']) #Routine to get location names
def get_location_names():
    response = jsonify({
        'locations': get_location()
    })
    print(locations)
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
    load_saved_artifacts()
    app.run(debug=True)
