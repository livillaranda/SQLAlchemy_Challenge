import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# start session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end_date><br/>"
    ) 
    
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Query results to a dictionary using date as the key and prcp as the value
    date_prcp = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    return jsonify(date_prcp)


@app.route("/api/v1.0/stations")
def stations():
    
    # Query all stations
    stations_info = session.query(Station.station, Station.name).all()

    session.close()

    return jsonify(stations_info)


@app.route("/api/v1.0/tobs")
def tobs():

    # Query the dates and temperature observations of the most active station for the last year of data
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    active = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    tempobs = session.query(Measurement.tobs).filter(Measurement.date >= year_ago).filter(Measurement.station == 'USC00519281').all()

    session.close()

    return (
        jsonify(
            (active[0]),
            (tempobs)
        )
    )


@app.route("/api/v1.0/<start>")
def start(start=None):
    
    # Query TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
    s_temp = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()

    s_list = []

    for date, min, max, avg in s_temp:
        s_list2 = {}
        s_list2["Date"] = date
        s_list2["TMIN"] = min
        s_list2["TMAX"] = max
        s_list2["TAVG"] = avg
        s_list.append(s_list2)

    session.close()

    return jsonify(s_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):

    # Query TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
    se_temp = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).group_by(Measurement.date).all()
    
    se_list = []

    for date, min, max, avg in se_temp:
        se_list2 = {}
        se_list2["Date"] = date
        se_list2["TMIN"] = min
        se_list2["TMAX"] = max
        se_list2["TAVG"] = avg
        se_list.append(se_list2)


    session.close()
    
    return jsonify(se_list)


# Run App
if __name__ == '__main__':
    app.run(debug=True)