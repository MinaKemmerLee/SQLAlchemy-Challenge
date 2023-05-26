# Import the dependencies
from flask import Flask, jsonify
from sqlalchemy import func
import datetime as dt
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///SurfsUp/Resources/hawaii.sqlite")

# Reflect the existing database into a new model
Base = automap_base()

#reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create the session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    # List all routes 
    return(
        f"Welcome to the Hawaii Climate API Homepage!<br/>"
        f"The Available Routes are listed below: <br/>"
        f"Precipitation Levels from the past year: /api/v1.0/precipitation <br/>"
        f"Info. on All Stations: /api/v1.0/stations <br/>"
        f"Specific info. on this year's Most Active Station: /api/v1.0/tobs <br/>"
        f"Temperature Summary start date-most recent date: /api/v1.0/<start> <br/>"
        f"Temperature Summary start date-end date: /api/v1.0/<start>/<end> <br/>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session= Session(engine)

    the_most_recent_date= dt.date(2017,8,23)

    one_year_prior =dt.date(the_most_recent_date.year -1, the_most_recent_date.month, the_most_recent_date.day)

    data= [measurement.date, measurement.prcp]
    year1results = session.query(*data).filter(measurement.date >= one_year_prior).all()

    # Close session
    session.close()

    # Create a list with the Prcp Data
    prcp_data= []
    for date, rain in year1results:
        prcp_dict= {}
        prcp_dict["Date"]= date
        prcp_dict["Prcp"]= rain
        prcp_data.append(prcp_dict)
    
    # jsonify response
    return (jsonify(prcp_data))


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session= Session(engine)

    # Query all needed info
    data= [station.station]
    allstations = session.query(*data).all()

    # Close session
    session.close()

    # Create a Station list
    station_list = [result[0] for result in allstations]

    # jsonify response
    return (jsonify(station_list))

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all needed info
    most_active_station = session.query(measurement.station).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).\
        first()

    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d').date()
    year_prior_to_last_date = dt.date(last_date.year - 1, last_date.month, last_date.day)

    tobs_data = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station[0]).\
        filter(measurement.date >= year_prior_to_last_date).all()

    # Close session
    session.close()

    # Create a list with the TOBS
    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {"Date": date, "TOBS": tobs}
        tobs_list.append(tobs_dict)

    # jsonify response
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def temperature_summary_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all needed info
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()

    # Close session
    session.close()

    # Create a dictionary with the temperature summary
    temperature_summary_1 = {
        "Start Date": start,
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    # jsonify response
    return (jsonify(temperature_summary_1))

@app.route("/api/v1.0/<start>/<end>")
def temperature_summary_range(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all needed info
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()

    # Close session
    session.close()

    # Create a dictionary with the temperature summary
    temperature_summary_2 = {
        "Start Date": start,
        "End Date": end,
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    # jsonify response
    return (jsonify(temperature_summary_2))

# Run app
if __name__ == "__main__":
    app.run(debug=True)