# Import necessary libraries and packages
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import numpy as np
import datetime as dt



# Create an engine to connect to the SQLite database file named "hawaii.sqlite"
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():
    '''
    This is the initial page that will give the routes the user can go to
    '''
    return (
        "<h1>Welcome to my climate app</h1><br/>"
        "<h2>This is the solution for #2 on the sqlalchemy-challenge</h2><br/>"
        "<br/>"
        "<h3>Available routes</h3><br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/start_date (Enter a date between '2010-01-01' and '2017-08-23' in this format)<br/>"
        "/api/v1.0/start_date/end_date (Enter start and end dates between '2010-01-01' and '2017-08-23' in this format)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    '''
    Return a list of all daily precipitation totals for the last year
    '''
    session = Session(engine)

    # Calculate the last date in the dataset
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d").date()

    # Calculate the date one year ago from the last date
    one_year_ago = last_date - dt.timedelta(days=365)

    # Query precipitation data for the last year
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    session.close()

    # Create a dictionary of date and precipitation values
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    '''
    Return a list of stations available to review
    '''
    session = Session(engine)

    # Query all station names
    results = session.query(Station.name).all()

    session.close()

    # Convert the list of tuples into a normal list
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    '''
    Return the temperatures and dates for the last year for the station with the most observations
    '''
    session = Session(engine)


    # Find the station with the most observations
    top_station = session.query(Measurement.station)\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc())\
        .first()[0]

    # Calculate the last date and one year ago
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d").date()
    one_year_ago = last_date - dt.timedelta(days=365)

    # Query temperature observations for the last year for the top station
    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == top_station)\
        .filter(Measurement.date >= one_year_ago)\
        .all()

    session.close()

    # Create a list of dictionaries containing date and temperature
    tobs_data = [{"date": date, "temperature": tobs} for date, tobs in results]
    return jsonify(tobs_data)


@app.route("/api/v1.0/<start>")
def temperature_range_start(start):
    '''
    Calculate the minimum, average, and maximum temperatures for dates greater than or equal to the start date
    '''
    session = Session(engine)

    # Query the minimum, average, and maximum temperatures
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .all()

    session.close()

    # Extract the temperature values from the query results
    min_temp, avg_temp, max_temp = results[0]

    # Create a dictionary with the temperature values
    temperature_data = {
        "start_date": start,
        "end_date": None,
        "min_temperature": min_temp,
        "avg_temperature": avg_temp,
        "max_temperature": max_temp
    }

    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>/<end>")
def temperature_range_start_end(start, end):
    '''
    Calculate the minimum, average, and maximum temperatures for dates between the start and end date (inclusive)
    '''
    session = Session(engine)

    # Query the minimum, average, and maximum temperatures
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date <= end)\
        .all()

    session.close()

    # Extract the temperature values from the query results
    min_temp, avg_temp, max_temp = results[0]

    # Create a dictionary with the temperature values
    temperature_data = {
        "start_date": start,
        "end_date": end,
        "min_temperature": min_temp,
        "avg_temperature": avg_temp,
        "max_temperature": max_temp
    }

    return jsonify(temperature_data)



if __name__ == '__main__':
    app.run()








 




