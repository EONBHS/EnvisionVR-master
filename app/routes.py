from flask import Flask,render_template,redirect,request,jsonify,abort,session
from flask_cors import CORS
from app import app, db, models
from app.models import user, games
from werkzeug.utils import secure_filename

# GOOGLE AUTH
from google_auth_oauthlib import flow
from google.oauth2 import id_token
import google.auth.transport.requests

import pathlib
import os
import zipfile
import requests
import cachecontrol

cors = CORS(app)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "81031882791-gsi00o9hkktjep6ughav7vka774fv7bc.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secrets.json")
app.config['UPLOAD_FOLDER'] = 'app/static/temp' 



flow = flow.Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
    )

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if 'google_id' not in session:
            return abort(401)
        else:
            return function()
    return wrapper

# Login required
@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorization_url)

# google Callback
@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    if not session ["state"] == request.args["state"]:
        abort(500)
    
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session['google_id'] = id_info['sub']
    session['name'] = id_info['name']
    session['email'] = id_info['email']
    session['picture'] = id_info['picture']

    # add user to database
    new_user = user(google_ID=session['google_id'], name=session['name'], email=session['email'], Profilepicture=session['picture'])
    db.session.add(new_user)
    db.session.commit()

    

    return redirect('/')


@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')


@app.route('/', methods=["GET", "POST"])
def home():

    # Query filename,dirname,dirpath from EnvisionVR.DB
    GameID = games.query.all()
    print(GameID)
    return render_template ('index.html', GameID=GameID)

@app.route('/browse', methods=["GET", "POST"])
def browse():
    items = user.query.all()
    print(items)
    return render_template ('browse.html', items=items)

# a route that will display popular.html
@app.route('/popular', methods=["GET", "POST"])
def popular():
    items = user.query.all()
    print(items)
    return render_template ('popular.html', items=items)

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    items = user.query.all()
    print(items)
    return render_template ('dashboard.html', items=items)


    
@app.route("/zip", methods=["GET", "POST"])
def read_zip_file():
    file = request.files['file']
    if file.filename.endswith('.zip'):
        # get filename
        filename = secure_filename(file.filename)
        # save file
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # create directory with the name of the zip file
        dirname = os.path.splitext(filename)[0]
        dirpath = os.path.join('app/static/temp', dirname)
        os.mkdir(dirpath)
        # Save filename to EnvisionVR.DB
        
        new_game = games(filename=filename, dirname=dirname, dirpath=dirpath)
        db.session.add(new_game)
        db.session.commit()

        # extract contents of the zip file to the new directory
        with zipfile.ZipFile(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r') as zip_ref:
            zip_ref.extractall(dirpath)
        return redirect("/")
    else:
        return jsonify({'error': 'file must be a zip file'}), 400