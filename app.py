import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np 
from flask import Flask, jsonify
import datetime as dt
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

base = automap_base()

base.prepare(engine, reflect=True)
Measurement = base.classes.measurement
Station = base.classes.station
session=Session(engine)
app = Flask(__name__)


def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.

    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    print(start_date, end_date)
    if end_date:
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    else:
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).all()


@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    year_prior = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    last_12 = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_prior)

    all_precipitation = {date:prcp for date, prcp in last_12}

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    results2 = session.query(Station.station).all()

    session.close()

    all_stations = list(np.ravel(results2))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
    year_prior = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    recent = session.query(Measurement.tobs, Measurement.date).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= year_prior).order_by(Measurement.date).all()

    session.close()

    all_tobs = list(np.ravel(recent))

    return jsonify(all_tobs)

@app.route('/api/v1.0/<start>', defaults={'end':None})
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session=Session(engine)
  
    dates = calc_temps(start, end)
    
    session.close()

    all_dates = list(np.ravel(dates))
       
    return jsonify(all_dates)


if __name__ == '__main__':
    app.run()