from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pi')
def pi():
    return 'Raspberry Pie!'

# dynamic route
@app.route('/<name>')
def print_name(name):
    return 'Hi, {}'.format(name)



if __name__ == '__main__':

 app.run(debug=True, host='0.0.0.0', port=80)