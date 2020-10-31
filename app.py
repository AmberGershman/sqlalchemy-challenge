import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurements = Base.classes.measurement
stations = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


@app.route("/")
def index():
    """What do you want to see? Here are all the available routes"""
    return (
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> ( __ enter date in format YYYY-M-D)<br/>"
        f"/api/v1.0/<start>/<end>(__ enter dates in format YYYY-M-D, YYYY-M-D)<br/>")


@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)
    results = session.query(measurements.date, measurements.prcp).all()

    session.close()

    rainfall = []
    for date, prcp in results:
        measure_dict = {}
        measure_dict = {date: prcp}
        rainfall.append(measure_dict)

    return jsonify(rainfall)


@app.route("/api/v1.0/stations")
def sstations():

    session = Session(engine)
    all_stations = session.query(stations.station, stations.name).all()

    session.close()

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def temps():

    # one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #this is hardcoded! We want flexible code, dammit. 
    session = Session(engine)
    most_recent = session.query(measurements.date)\
        .order_by(measurements.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(most_recent, "%Y-%m-%d") - dt.timedelta(days=365)
    recent_temps = session.query(measurements.date, measurements.station, measurements.tobs)\
        .filter(measurements.date >= one_year_ago)\
        .group_by(measurements.station).all()
    #     .order_by(measurements.station).all()

    session.close()

    temps = []

    for date in recent_temps:
        temp = {}
        temp['date'] = date[0]
        temp['station'] = date[1]
        temp['temperture'] = date[2]
        temps.append(temp)
    return jsonify(temps)


@app.route("/api/v1.0/<start>")
def start_date(start):

    session = Session(engine)

    from_measures = session.query(func.min(measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs))\
        .filter(measurements.date >= start).all()
    
    session.close()
    
    overall_measures = []
    for min,max, avg in from_measures:
        temps={}
        temps['Minimum Temp: ']= min
        temps['Maximum Temp: ']= max
        temps['Average Temp: ']= avg
        overall_measures.append(temps)

    return jsonify(overall_measures)

@app.route("/api/v1.0/<start><end>")
def start_end(start,end):

    session = Session(engine)

    from_to_measures = session.query(func.min(measurements.tobs), func.avg(measurements.tobs), func.max(measurements.tobs))\
        .filter(measurements.date >= start).filter(measurements.date <= end).all()
    
    session.close()
    
    dated_measures = []
    for min,max, avg in from_to_measures:
        temps_1={}
        temps_1['Minimum Temp: ']= min
        temps_1['Maximum Temp: ']= max
        temps_1['Average Temp: ']= avg
        dated_measures.append(temps_1)

    return jsonify(dated_measures)


if __name__ == "__main__":
    app.run(debug=True)
