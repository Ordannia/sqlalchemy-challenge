# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import and_

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


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
        f"/api.v1.0/tobs<br/>"
        f"/api.v1.0/<start><br/>"
        f"/api.v1.0/<start>/<end>"
    )

#--------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------#
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Convert the query results from your precipitation analysis 
    # (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key 
    # and prcp as the value.

    # Find the most recent date in the data set.
    latest_date = session.query(func.max(Measurement.date)).scalar()
    latest_date

    # Calculate the date range for the last 12 months
    latest_date_obj = dt.datetime.strptime(latest_date, '%Y-%m-%d').date()
    one_year_ago = latest_date_obj - dt.timedelta(days=365)
    one_year_ago = one_year_ago.strftime('%Y-%m-%d')

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(
        and_(Measurement.date >= one_year_ago, Measurement.date <= latest_date)
    ).all()

    # Save the query results as a Pandas DataFrame. Explicitly set the column names
    data = [(result.date, result.prcp) for result in results]
    precipitation_data = pd.DataFrame(data, columns=['date', 'precipitation'])

    # Convert the DataFrame to a dictionary for JSON serialization
    precipitation_dict = precipitation_data.to_dict(orient='records')

    # Close the session
    session.close() 

    # Return the JSON representation of your dictionary.
    return jsonify(precipitation_dict)

#--------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------#
@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query
    stations = session.query(Station.station, Station.name).all()

    stations_df = pd.DataFrame(stations, columns=['station', 'name'])

    stations_dict = stations_df.to_dict(orient='records')

    # Close the session
    session.close()

    # Return a JSON list of stations from the dataset.
    return jsonify(stations_dict)

#--------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------#
@app.route("/api.v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperature observations of the most-active station for the previous year 
    # of data.

    # Find the most recent date in the data set.
    latest_date = session.query(func.max(Measurement.date)).scalar()
    latest_date

    # Calculate the date range for the last 12 months
    latest_date_obj = dt.datetime.strptime(latest_date, '%Y-%m-%d').date()
    one_year_ago = latest_date_obj - dt.timedelta(days=365)
    one_year_ago = one_year_ago.strftime('%Y-%m-%d')

    results = session.query(Measurement.date, Measurement.tobs) \
        .filter(and_(Measurement.date >= one_year_ago, \
                     Measurement.date <= latest_date, \
                     Measurement.station == 'USC00519281')).all()

    results_df = pd.DataFrame(results, columns=['date', 'tobs'])

    results_dict = results_df.to_dict(orient='records')

    # Close the session
    session.close()

    # Return a JSON list of temperature observations for the previous year.
    return jsonify(results_dict)

#--------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------#
@app.route("/api.v1.0/<start>")
def start_date_temps(start):

    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a JSON list of the minimum temperature, the average temperature, and the 
    # maximum temperature for a specified start.
    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal 
    # to the start date. 
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    
    # Close the session
    session.close()

    temp_data = []
    for result in results:
        min_temp, avg_temp, max_temp = result
        temp_data.append({
            'Min Temperature': min_temp,
            'Average Temperature': avg_temp,
            'Max Temperature': max_temp
        })

    return jsonify(temp_data)
#--------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------#
@app.route("/api.v1.0/<start>/<end>")
def start_end_range(start, end):

    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a JSON list of the minimum temperature, the average temperature, and the 
    # maximum temperature for a specified start-end range.

    # For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the 
    # dates from the start date to the end date, inclusive.
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(and_ (Measurement.date >= start_date, \
                     Measurement.date <= end_date)).all()
    
    # Close the session
    session.close()

    temp_data = []
    for result in results:
        min_temp, avg_temp, max_temp = result
        temp_data.append({
            'Min Temperature': min_temp,
            'Average Temperature': avg_temp,
            'Max Temperature': max_temp
        })

    return(jsonify(temp_data))

#--------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------#
if __name__ == '__main__':
    app.run(debug=True)