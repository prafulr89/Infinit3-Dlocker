from logging import error
from ntpath import join
import os
import pathlib

import requests
from flask import Flask, session, abort, redirect, request, render_template
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
#from werkzeug.exceptions import abort

app = Flask("Google Login application")
app.secret_key = "BaneChat"
file = open('key.key', 'rb')
key = file.read()
file.close()
fernet = Fernet(key)
ALLOWED_EXTS = {"txt", "jpeg", "jpg", "png"}
save_path = '/Uploads'

def check_file(file):
    return '.' in file and file.rsplit('.', 1)[1].lower() in ALLOWED_EXTS

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "267576824648-oqlk3v9gk8osj28lo3tpebjku0ci6flo.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401) #Authorization required
        else:
            return function()

    return wrapper

@app.route("/login", methods=["POST", "GET"])
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/protected_area")
    #return ("Hi")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/")
def index():
    return render_template('./chat_index.html')

@app.route("/protected_area")
@login_is_required
def protected_area():
    return render_template('./upload_index.html')

@app.route('/upload', methods=["POST", "GET"])
def upload_file():
    error = None
    if request.method == 'POST':
        if 'file' not in request.files:
            error = "File not selected"
            return render_template('/chat_index.html', error=error)

        f = request.files["file"]
        filename = f.filename
        new_filename = os.path.join("Uploads", filename)
        print ("f:", f)
        print("filename:", filename)
        data = f.read()
        encrypted = fernet.encrypt(data)
        with open(new_filename,'wb') as d:
            broad = d.write(encrypted)
            
        print("filename_again:", broad)
            #f_encry.save(os.path.join("Uploads", f_encry))

        if filename == "":
            error = "FIlename is empty"
            return render_template('./chat_index.html')
        if check_file(filename) == False:
            error = "This filename is not allowed"
            return render_template('./chat_index.html', error=error)
        
        #f.save(os.path.join("Uploads", f.filename))
        #f.write(os.path.join("Uploads", encrypted))
        return render_template('./list_index.html', upload_file=filename)

    return 'file uploaded succesfully'

@app.route('/view', methods=["POST", "GET"])
def view_file():
    path = os.path.expanduser(u'./Uploads')
    return render_template('./index.html', tree=make_tree(path)) 

#########file
def make_tree(path):
    tree = dict(name=os.path.basename(path), children=[])
    try: lst= os.listdir(path)
    except OSError:
        pass
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                tree['children'].append(dict(name=fn))
    return tree
############
if __name__ == "__main__":
    app.run(debug=True)

