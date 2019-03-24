from flask import (Flask, render_template, request, redirect, jsonify, url_for,
                   flash)
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from sqlalchemy.orm.exc import NoResultFound

app = Flask(__name__)
engine = create_engine('postgres://catalog:catalog@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


CLIENT_ID = json.loads(
    open('/var/www/client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Andrei's Application"


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# species JSON
@app.route('/species.json')
def speciesJSON():
    species = session.query(Category).all()
    specieslist = []
    for i in species:
        s = i.serialize
        members = session.query(Item).filter_by(category_id=s['id']).all()
        s['members'] = []
        for j in members:
            m = j.serialize
            s['members'].append(m)
        specieslist.append(s)    
    return jsonify(Species=specieslist)


# Show all Species & recent members
@app.route('/')
@app.route('/species/')
def showSpecies():
    species = session.query(Category).order_by(asc(Category.name))
    members = session.query(Item).order_by(desc(Item.id)).limit(5)
    if 'username' not in login_session:
        return render_template('publicspecies.html',
                               species=species, members=members)
    else:
        return render_template('species.html',
                               species=species, members=members)


# show members that are part of a certain species
@app.route('/<string:species>/Members/')
def showMembers(species):
    cl = session.query(Category).order_by(asc(Category.name))
    s = session.query(Category).filter_by(name=species).one()
    members = session.query(Item).filter_by(
        category_id=s.id).all()
    if 'username' not in login_session:
        return render_template('publicmembers.html',
                               members=members, species=s, specieslist=cl)
    else:
        return render_template('members.html',
                               members=members, species=s, specieslist=cl)


# show member info
@app.route('/<string:species>/<string:member>/')
def showMember(species, member):
    s = session.query(Category).filter_by(name=species).all()
    m = session.query(Item).filter_by(name=member).one()
    if 'username' not in login_session:
        return render_template('publicmember.html', member=m, species=s)
    else:
        return render_template('member.html', member=m, species=s)


# Create a new  member
@app.route('/newmember/', methods=['GET', 'POST'])
def newMember():
    if 'username' not in login_session:
        return redirect('/login')
        
    if request.method == 'POST':
        s = session.query(Category).filter_by(name=request.form
                                              ['species']).one()
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=s.id, user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New Member %s  Successfully Created' % (newItem.name))
        return redirect(url_for('showSpecies'))
    else:
        species = session.query(Category).order_by(asc(Category.name))
        return render_template('newmember.html', species=species)


# Edit a member
@app.route('/<string:member>/edit', methods=['GET', 'POST'])
def editMember(member):
    if 'username' not in login_session:
        return redirect('/login')
    m = session.query(Item).filter_by(name=member).one()    
    if login_session['user_id'] != m.user_id:
        flash('You are not authorized to edit Member %s  .'
              'You can only edit members you created.' % (m.name))
        return redirect(url_for('showSpecies'))
    species = session.query(Category).order_by(asc(Category.name))
    if request.method == 'POST':
        if request.form['name']:
            m.name = request.form['name']
        if request.form['description']:
            m.description = request.form['description']
        if request.form['species']:
            s = session.query(Category).filter_by(name=request.form
                                                  ['species']).one()
            m.category_id = s.id
        session.add(m)
        session.commit()
        flash('Member %s  Successfully Edited' % (m.name))
        return redirect(url_for('showSpecies'))
    else:
        return render_template('editmember.html', member=m, species=species)


# Delete a member
@app.route('/<string:member>/delete', methods=['GET', 'POST'])
def deleteMember(member):
    if 'username' not in login_session:
        return redirect('/login')
    m = session.query(Item).filter_by(name=member).one()
    if login_session['user_id'] != m.user_id:
        flash('You are not authorized to delete Member %s  .'
              'You can only delete members you created.' % (m.name))
        return redirect(url_for('showSpecies'))
    if request.method == 'POST':
        session.delete(m)
        session.commit()
        flash('Member %s  Successfully Deleted' % (m.name))
        return redirect(url_for('showSpecies'))
    else:
        return render_template('deletemember.html', member=m)

# oauth connect with Google
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
                                 json.dumps("Token's client ID does not"
                                            "match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is '
                                            'already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 300px; height: 300px;border-radius: 150px;'
              -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '''
    flash("you are now logged in as %s" % login_session['username']) 
    print("done!") 
    return output

# User helper functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        userid = user.id
        return userid
    except NoResultFound:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('''Failed to revoke token for
                                            given user.''', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showSpecies'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showSpecies'))

if __name__ == '__main__':
    app.secret_key = 'dsf043rsmfsfsd'
    app.debug = False
    app.run()
