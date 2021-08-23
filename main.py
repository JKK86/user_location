import json

import redis
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
r = redis.Redis()


@app.route("/")
def home():
    return render_template("maps.html")


@app.route("/add-marker", methods=["POST"])
def add_marker():
    req = request.form
    location = req["lname"]
    latitude = req["latitude"]
    longitude = req["longitude"]

    r.geoadd("points", longitude, latitude, location)
    r.set("last_loc_name", location)

    return redirect("/")


@app.route("/data")
def data():
    loc_name = r.get("last_loc_name")
    if loc_name is None:
        r.geoadd("points", "-104.985784", "39.728206", "parking")
        loc_name = "parking"

    all_loc = r.georadiusbymember(name="points", member=loc_name, radius=6371, unit="km", withcoord=True)
    print(all_loc)

    coordinates = dict()
    for loc in all_loc:
        name = loc[0].decode('UTF-8')
        longitude = loc[1][0]
        latitude = loc[1][1]
        coordinates[name] = {"lat": latitude, "lng": longitude}

    return json.dumps(coordinates)


@app.route("/last")
def last_location():
    return r.get("last_loc_name").decode('UTF-8')


if __name__ == '__main__':
    app.run()
