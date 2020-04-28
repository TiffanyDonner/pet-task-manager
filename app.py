import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from os import path
if path.exists("env.py"): 
    import env

app = Flask(__name__)


app.config["MONGO_DBNAME"] = 'paw_purfect_planner'
app.config['MONGO_URI'] = os.environ['MONGO_URI']

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
    events =  mongo.db.events
    events.insert_one(request.form.to_dict())
    return redirect(url_for('get_events'))


@app.route('/edit_event/<event_id>')
def edit_event(event_id):
    the_event =  mongo.db.events.find_one({"_id": ObjectId(event_id)})
    all_categories =  mongo.db.categories.find()
    return render_template('editevent.html', event=the_event,
                           categories=all_categories)


@app.route('/update_event/<event_id>', methods=["POST"])
def update_event(event_id):
    events = mongo.db.events
    events.update( {'_id': ObjectId(event_id)},
    {
        'event_name':request.form.get('event_name'),
        'category_name':request.form.get('category_name'),
        'event_description': request.form.get('event_description'),
        'due_date': request.form.get('due_date'),
        'is_urgent':request.form.get('is_urgent')
    })
    return redirect(url_for('get_events'))


@app.route('/delete_event/<event_id>')
def delete_event(event_id):
    mongo.db.events.remove({'_id': ObjectId(event_id)})
    return redirect(url_for('get_events'))


@app.route('/get_categories')
def get_categories():
    return render_template('categories.html',
                           categories=mongo.db.categories.find())


@app.route('/delete_category/<category_id>')
def delete_category(category_id):
    mongo.db.categories.remove({'_id': ObjectId(category_id)})
    return redirect(url_for('get_categories'))


@app.route('/edit_category/<category_id>')
def edit_category(category_id):
    return render_template('editcategory.html',
    category=mongo.db.categories.find_one({'_id': ObjectId(category_id)}))


@app.route('/update_category/<category_id>', methods=['POST'])
def update_category(category_id):
    mongo.db.categories.update(
        {'_id': ObjectId(category_id)},
        {'category_name': request.form.get('category_name')})
    return redirect(url_for('get_categories'))


@app.route('/insert_category', methods=['POST'])
def insert_category():
    category_doc = {'category_name': request.form.get('category_name')}
    mongo.db.categories.insert_one(category_doc)
    return redirect(url_for('get_categories'))


@app.route('/add_category')
def add_category():
    return render_template('addcategory.html')


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)