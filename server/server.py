from flask import Flask, render_template, request, jsonify
import os
import logging
import datastore
import aqistore

# DotMap is a dot-access dictionary subclass
# https://pypi.org/project/dotmap/
# https://github.com/drgrib/dotmap
from dotmap import DotMap

# logging configuration
# debug, info, warning, error, critical
logging.basicConfig(filename='./instance/aqi.log', filemode='w',
                    level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.info('Started')
logging.info('running server.py')

# Example ajax code from
# https://github.com/caseydunham/ajax-flask-demo

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'aqi.sqlite'),
    LOGGER=os.path.join(app.instance_path, 'aqi.log'),
)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
    logging.info('server - created instance folder.')
except OSError:
    pass

# default sensor_id for PurpleAir sensor Forest Park
sensor_id = 104402


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/pi')
def pi():
    return 'Raspberry Pie!'


@app.route('/sensor')
def sensor_index():
    return render_template('sensor.html')


@app.route('/aqi')
def aqi_index():
    return render_template('aqi.html')


@app.route('/api/aqi', methods=['POST'])
def aqi_post():
    out = aqi_proc()
    r = out.toDict()
    return jsonify(result=r, status=200)


def aqi_proc():
    error = None
    aqi = 0
    aqiColor = 0
    try:
        aqi, aqiColor = aqistore.purpleAir()
    except Exception as e:
        error = e
        logging.warning(e)
    out = DotMap()
    out.aqi = aqi
    out.aqiColor = aqiColor
    out.error = error
    logging.info('aqi_proc - data from purpleAir.', out.toDict())
    logging.info(out)
    return out


@app.route('/api/sensor_post', methods=['POST'])
def sensor_post():
    json = request.get_json()
    msg = DotMap(json)
    out = sensor_proc(msg)
    r = out.toDict()
    return jsonify(result=r, status=200)


def sensor_proc(msg):
    sensor_id = msg.sensor_id
    logging.info('server - updating db sensor_id: ' + str(sensor_id))
    error = None

    if not sensor_id:
        error = 'Sensor_id is required.'
        logging.warning(error)

    if error is None:
        error = datastore.set_sensor_id(sensor_id)
    out = DotMap()
    out.sensor_id = sensor_id
    out.error = error
    return out


@app.route('/api/say_name', methods=['POST'])
def say_name_post():
    json = request.get_json()
    msg = DotMap(json)
    out = say_name_proc(msg)
    r = out.toDict()
    return jsonify(result=r, status=200)

# process say_name message


def say_name_proc(msg):
    datastore.get_db()
    first_name = msg.first_name
    last_name = msg.last_name
    day_week = msg.day_week

    out = DotMap()
    out.first_name = first_name
    out.last_name = last_name
    out.day_week = day_week
    datastore.close_db()
    return out


@app.route('/init')
def init():
    datastore.init_db()
    return 'Database initialized'

# dynamic route


@app.route('/<name>')
def print_name(name):
    return 'Hi, {}'.format(name)


if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=5000)
