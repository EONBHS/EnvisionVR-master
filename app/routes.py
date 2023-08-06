from flask import render_template,redirect,request,abort,session
from flask_cors import CORS
from app import app, db
from app.models import User, Games
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
    new_user = User(google_ID=session['google_id'], name=session['name'], email=session['email'], Profilepicture=session['picture'])
    db.session.add(new_user)
    db.session.commit()

    #Logged in session
    session['logged_in'] = True

    return redirect('/')


@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')


@app.route('/', methods=["GET", "POST"])
def home():

    # Query filename,dirname,dirpath from EnvisionVR.DB
    games = Games.query.all()   
    

    return render_template ('index.html', games=games)

@app.route('/browse', methods=["GET", "POST"])
def browse():
    ''' docstrin'''
    actions = Games.query.filter(Games.genre == "1").all()
    adventures = Games.query.filter(Games.genre == "2").all()
    rpgs = Games.query.filter(Games.genre == "3").all()
    strategys = Games.query.filter(Games.genre == "4").all()
    sports = Games.query.filter(Games.genre == "5").all()
    simulations = Games.query.filter(Games.genre == "6").all()
    puzzles = Games.query.filter(Games.genre == "7").all()
    idles = Games.query.filter(Games.genre == "8").all()
    horrors = Games.query.filter(Games.genre == "9").all()
    platformers = Games.query.filter(Games.genre == "10").all()
    others = Games.query.filter(Games.genre == "11").all()
    return render_template ('browse.html', actions=actions, adventures=adventures, rpgs=rpgs, strategys=strategys, sports=sports, simulations=simulations, puzzles=puzzles, idles=idles, horrors=horrors, platformers=platformers, others=others)

# a route that will display popular.html
@app.route('/popular', methods=["GET", "POST"])
def popular():
    items = User.query.all()
    print(items)
    return render_template ('popular.html', items=items)

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    items = User.query.all()
    print(items)
    return render_template ('dashboard.html', items=items)

@app.route('/addgame')
def upload():
   return render_template ('addgame.html')





@app.route('/zip', methods=["GET", "POST"])
def zip():
    if request.method == 'POST':
        name = request.form.get('Title')
        description = request.form.get('GameDescription')
        downloadable = bool(request.form.get('Downloadable'))
        
        genre = request.form.get('genre')
        splashscreen = request.files.get('splashscreen')
        image_1 = request.files.get('image1')
        image_2 = request.files.get('image2')
        file = request.files.get('zipfile')

        
        filename = secure_filename(file.filename)
        # save file
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # create directory with the name of the zip file
        dirname = os.path.splitext(filename)[0]
        dirpath = os.path.join('app/static/temp', dirname)
        os.mkdir(dirpath)
        # Save filename to EnvisionVR.DB 
        print(dirname)
        print(dirpath)
        
 
        splash = secure_filename(splashscreen.filename)
        splashscreen.save(os.path.join(dirpath, splash))

        image1 = secure_filename(image_1.filename)
        image_1.save(os.path.join(dirpath, image1))
       

        image2 = secure_filename(image_2.filename)
        image_2.save(os.path.join(dirpath, image2))
        
        new_game = Games(name=name, description=description, downloadable=downloadable,genre=genre,User_ID=session['google_id'],splashscreen=splash,image1=image1,image2=image2,filename=filename, dirname=dirname, dirpath=dirpath)
        db.session.add(new_game)
        db.session.commit()


        # extract contents of the zip file to the new directory
        with zipfile.ZipFile(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r') as zip_ref:
            zip_ref.extractall(dirpath)
        return redirect("/dashboard")
    

    #/game
@app.route('/<int:id>', methods=["GET", "POST"])
def game(id):
    game = Games.query.get(id)
    return render_template('game.html', game=game)