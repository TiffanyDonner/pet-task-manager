import os
from flask import Flask, render_template, redirect, request, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt
from os import path
if path.exists("env.py"): 
    import env

app = Flask(__name__)


app.config["MONGO_DBNAME"] = 'paw_purfect_planner'
app.config['MONGO_URI'] = os.environ['MONGO_URI']
app.secret_key = 'somesecretkey'

mongo = PyMongo(app)

@app.route('/')
def home():
    """Render home.html and return buttons to either register or login"""
    
    return render_template("home.html")

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


@app.route('/register', methods=['POST', 'GET'])
def register():
    """Register user into database."""
    if request.method == 'POST':
        existing_user = mongo.db.users.find_one({'username' : request.form['username']})
        password = request.form['password']
        username = request.form['username']
        
        if password == '' or username == '':
            error = 'Please enter a username and password'
            return render_template('register.html')
                                    
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            
            mongo.db.users.insert_one({
                'username' : request.form['username'],
                'pet_name' : request.form['pet_name'],
                'first_name' : request.form['first_name'],
                'last_name' : request.form['last_name'],
                'email' : request.form['email'],
                'password' : hashpass, 
            })
            session['username'] = request.form['username']
            return redirect(url_for('home'))
        else:
            flash('This username already exists!')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Match form data with user database data and if match log in"""

    if request.method == 'POST':
        username = request.form['username']
        login_user = mongo.db.users.find_one({'username': username})

        if login_user:
            if bcrypt.checkpw(request.form['password'].encode('utf-8'),
                            login_user['password']):
                session['username'] = request.form.to_dict()['username']
                user_id = login_user['username']
                return redirect(url_for('user', user_id = user_id ))
            else:
                flash('Invalid username/password combination!')
                return render_template('register.html')
        else:
            flash('Invalid username/password combination!')
        
    return render_template('login.html')


@app.route('/user/<user_id>', methods=['GET', 'POST'])
def user(user_id):
    """Display all data in the user collection in the database."""
    
    if request.method == 'GET':
        if 'username' in session:
            the_user = mongo.db.users.find_one({'username': user_id })
            return render_template('profile_page.html', user=the_user)
        else:
            return render_template("login.html")
    elif request.method == 'POST':
        mongo.db.users.update_one( {"username": user_id })
        return redirect(url_for('user', user_id=user_id))


@app.route('/end_session')
def end_session():
    """End session."""
    
    session.clear()
    return render_template("home.html")
    

@app.errorhandler(404)
def error_page(e):
    """Handle 404 by rendering error-page.html."""
    
    return render_template('error-page.html'), 404

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)