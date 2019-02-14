
import json
import pandas as pd
import requests
from geojson import Point, Feature

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)
#app.config.from_object(__name__)
#app.config.from_envvar('APP_CONFIG_FILE', silent=True)

#MAPBOX_ACCESS_KEY = app.config['MAPBOX_ACCESS_KEY']

# Mapbox driving direction API call
ROUTE_URL = "https://api.mapbox.com/directions/v5/mapbox/driving/{0}.json?access_token={1}&overview=full&geometries=geojson"
ALLOWED_EXTENSIONS = set(['csv','xlsx','xlx'])
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

MAPBOX_ACCESS_KEY='pk.eyJ1Ijoic2FyYW5nb2YiLCJhIjoiY2pya3FzMTVsMDBtdTQzcGw5N2xkbXR6aCJ9.PuHyaN2w1BkaO5SCVoHPJQ'
#APP_CONFIG_FILE=settings.py

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_point_location_detail(title, latitude, longitude, index, pt_index, input_type):
    point = Point([longitude, latitude])
    if input_type=='CFS':
        properties = {
            "title": title,
            "icon": {
                'marker-color': '#f4df42',
                'marker-size': 'large',
                'marker-symbol':'campsite' 
            },
            #'icon': "campsite",
            #'marker-color': '#f4df42',
            #'marker-symbol': index,
            #'pt_index': 'cfs'+str(pt_index)
        }
    else:
        properties = {
            "title": title,
            "icon": {
                'marker-color': '#8834bb',
                'marker-size': 'large',
                'marker-symbol':'campsite' 
            },
            #'marker-color': '#3bb2d0',
            #'marker-symbol': index,
            #'pt_index': 'cs'+str(pt_index)
        }
    feature = Feature(geometry = point, properties = properties)
    return feature

def create_locations_details(data_pts,input_type):
    _locations = []
    for loc_index, location in data_pts.iterrows():
        new_location = create_point_location_detail(
            location['name'],
            location['lat'],
            location['long'],
            location['name'],#len(_locations) + 1,
            data_pts[data_pts.columns[0]],
            input_type
        )
        _locations.append(new_location)
    return _locations



@app.route('/', methods=['GET', 'POST'])
def mapbox_js():
    if request.method=='POST':
        print("POST request")
        file_SC = pd.read_excel(request.files.get("file_SC"))
        file_CFS = pd.read_excel(request.files.get("file_CFS"))
        av_lat = (file_CFS['lat'].mean() + file_SC['lat'].mean())/2.
        av_long = (file_CFS['long'].mean() + file_SC['long'].mean())/2.
        all_locations = create_locations_details(file_SC,'SC') + create_locations_details(file_CFS,'CFS') 
        print(all_locations)
    else:
        all_locations = []
        av_lat = 44.047993
        av_long = -88.551689

    return render_template('mapbox_js.html', 
                            ACCESS_KEY=MAPBOX_ACCESS_KEY,
                            all_locations=all_locations,
                            av_lat = av_lat,
                            av_long = av_long
                            )

app.run(host='0.0.0.0', port=4500)