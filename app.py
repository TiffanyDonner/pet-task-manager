import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from os import path
if path.exists("env.py"): 
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = 'paw_purfect_planner'
app.config["MONGO_URI"] = os.getenv('MONGO_URI', 'mongodb://localhost')

mongo = PyMongo(app)

@app.route('/')
@app.route('/get_events')
def get_events():
    return render_template("events.html", 
                            events=mongo.db.events.find())

@app.route('/add_event')
def add_event():
    return render_template('addevent.html',
                           categories=mongo.db.categories.find())

@app.route('/insert_event', methods=['POST'])
def insert_event():
    events = mongo.db.events
    events.insert_one(request.form.to_dict())
    return redirect(url_for('get_events'))

@app.route('/edit_event/<event_id>')
def edit_event(event_id):
    the_event =  mongo.db.events.find_one({"_id": ObjectId(event_id)})
    all_categories =  mongo.db.categories.find()
    return render_template('editevent.html', event=the_event,
                           categories=all_categories)

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)