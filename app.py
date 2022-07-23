# Import dependencies
from cProfile import run
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func 

from flask import Flask, jsonify

# Set up the database
engine = create_engine('sqlite:///hawaii.sqlite')

# Reflect the database into our classes
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save our references to each table 
Station = Base.classes.station
Measurement = Base.classes.measurement


# Create a session link from python to our database
session = Session(engine)

# Set up Flask
app = Flask(__name__)

# Creating the welcome route
@app.route('/')
def welcome():
    return (
        """
        Welcome to the Climate Analysis API! 
        Available Routes: 
        api/v1.0/precipitation 
        api/v1.0/stations 
        api/v1.0/tobs 
        api/v1.0/temp/start/end 
        """)

# Creating route for the precipitation analysis
@app.route('/api/v1.0/precipitation')
def precipitation():
# Insert function that will calculate the date one year ago 
# from the most recent date in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    # Write a query that finds the date and precipitation for the previous year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    precip = {date: prcp for date, prcp in precipitation}    
        # Return a 'jsonified' file
    return jsonify(precip)

# Creating route for the stations data
@app.route('/api/v1.0/stations')
def stations():
# Insert function to find all stations in the database
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

# Creating route for the monthly temperature route
@app.route('/api/v1.0/tobs')
def temp_monthly():
# Creating a function to record monthly temperatures
# Finding the date, one year ago from 
# the most recent date in the database    
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query the primary station (station with most data)
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()    
    # Unravel results into one dimensional array, converted to a list     
    temps = list(np.ravel(results))
    # Return 'temps' jsonified 
    return jsonify(temps = temps)

# Creating the Statistics route
@app.route('/api/v1.0/temp/<start>')
@app.route('/api/v1.0/temp/<start>/<end>')
# Create a stats function, with the parameters 'start' and 'end'
def stats(start = None, end = None):
    # Query for the min, avg, and max temps from the database
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    # Add an if-not statement to determine the start and end parameters 
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps = temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps = temps)


