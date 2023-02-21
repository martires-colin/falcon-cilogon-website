import json
import pika
import datetime

from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from pymongo import MongoClient
from flask import Flask, redirect, render_template, session, url_for, request, jsonify
from flask_session import Session

#------------------CILogon OIDC---------------------------------------------------------------------------#
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata, ProviderMetadata
from flask_pyoidc.user_session import UserSession
#---------------------------------------------------------------------------------------------------------#

from rabbitmq import rmq_server as rmq

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Connect to local MongoDB database
db_client = MongoClient('localhost', 27017)
db = db_client.falcon_db
l_transfer_data = db.l_transfer_data

app = Flask(__name__)
app.config.update(
    SECRET_KEY=env.get("APP_SECRET_KEY"),
    OIDC_REDIRECT_URI=env.get("OIDC_REDIRECT_URI"),
    SESSION_TYPE="filesystem",
    SESSION_PERMANENT=False
)
sess = Session(app)

# Static Client/Provider Registration
client_metadata = ClientMetadata(
    client_id=env.get("CILOGON_CLIENT_ID"),
    client_secret=env.get("CILOGON_CLIENT_SECRET"),
    post_logout_redirect_uris=['https://localhost:3000/logout'])

provider_metadata = ProviderMetadata(
    issuer='https://cilogon.org',
    authorization_endpoint='https://cilogon.org/authorize',
    token_endpoint='https://cilogon.org/oauth2/token',
    introspection_endpoint='https://cilogon.org/oauth2/introspect',
    userinfo_endpoint='https://cilogon.org/oauth2/userinfo',
    #end_session_endpoint='https://idp.example.com/logout',
    jwks_uri='https://cilogon.org/oauth2/certs',
    registration_endpoint='https://cilogon.org/oauth2/register')

auth_params = {'scope': ['openid', 'profile', 'email', 'org.cilogon.userinfo']} # specify the scope to request

provider_config = ProviderConfiguration(
    provider_metadata=provider_metadata,
    client_metadata=client_metadata,
    auth_request_params=auth_params)

auth = OIDCAuthentication({
    'CILogon': provider_config,
    "Site1": provider_config,
    "Site2": provider_config
    }, app)


@app.route("/")
def home():
    return render_template(
        "home.html",
        session=session,
        page="Dashboard"
    )

@app.route("/dashboard")
def dashboard():
    return render_template(
        "home.html",
        session=session["userinfo"],
        page="Dashboard"
    )


# @app.route("/callback", methods=["GET", "POST"])
# def callback():
#     # token = oauth.auth0.authorize_access_token()
#     # session["user"] = token
#     return redirect("/")


@app.route("/login")
@auth.oidc_auth('CILogon')
def login():
    # user_session = UserSession(session)
    # print(user_session)
    session['user_info'] = {
        "full_name": session["userinfo"]["name"],
        "email": session["userinfo"]["email"],
        "idp_name": session["userinfo"]["idp_name"],
        "access_token": session["access_token"],
        "id_token_jwt": session["id_token_jwt"]
    }
    session['site1_info'] = {
        "full_name": None, 
        "email": None, 
        "idp_name": None, 
        "access_token": None, 
        "id_token_jwt": None 
    }
    session['site2_info'] = {
        "full_name": None,
        "email": None, 
        "idp_name": None, 
        "access_token": None,
        "id_token_jwt": None 
    }

    print(f'Logged in as {session["user_info"]["full_name"]}')
    print(session["user_info"])

    # payload = {
    #     "access_token": session["access_token"],
    #     "id_token_jwt": session["id_token_jwt"]    
    # }

    # node_id = "1234"
    # rmq.send_access_token(node_id, payload)

    return redirect(url_for("dashboard"))


@app.route("/loginSite1")
@auth.oidc_auth('Site1')
def loginSite1():
    # site1_session = UserSession(session)
    session['site1_info'] = {
        "full_name": session["userinfo"]["name"],
        "email": session["userinfo"]["email"],
        "idp_name": session["userinfo"]["idp_name"],
        "access_token": session["access_token"],
        "id_token_jwt": session["id_token_jwt"]
    }
    # print(f'Site 1: {session["userinfo"]["idp_name"]}')
    # print(f'Acceess Token: {session["access_token"]}')
    # print(session)
    return redirect(url_for("dashboard"))


@app.route("/loginSite2")
@auth.oidc_auth('Site2')
def loginSite2():
    # site1_session = UserSession(session)
    session['site2_info'] = {
        "full_name": session["userinfo"]["name"],
        "email": session["userinfo"]["email"],
        "idp_name": session["userinfo"]["idp_name"],
        "access_token": session["access_token"],
        "id_token_jwt": session["id_token_jwt"]
    }
    # print(f'Site 2: {session["userinfo"]["idp_name"]}')
    # print(f'Acceess Token: {session["access_token"]}')
    # print(session)
    return redirect(url_for("dashboard"))


@app.route("/logout")
@auth.oidc_logout
def logout():
    print(session)
    session.clear()
    return redirect(url_for("home"))


@app.route("/account")
def account():
    print(session["user_info"])
    print(session["site1_info"])
    print(session["site2_info"])
    return render_template(
            "home.html",
            name=session["user_info"]["full_name"],
            email=session["user_info"]["email"],
            affiliation=session["user_info"]["idp_name"],
            site1_name=session["site1_info"]["full_name"],
            site1_email=session["site1_info"]["email"],
            site1_affiliation=session["site1_info"]["idp_name"],
            site2_name=session["site2_info"]["full_name"],
            site2_email=session["site2_info"]["email"],
            site2_affiliation=session["site2_info"]["idp_name"],
            page="Account"
        )


@app.route("/history")
def history():
    cursor = l_transfer_data.find({"user_email": session["userinfo"]["email"]}).sort("epochTime", -1)
    list_cur = list(cursor)
    return render_template(
            "home.html",
            session=session["userinfo"],
            page="History",
            transferData=list_cur
        )


@app.route('/updateSrc', methods=['POST'])
def updateSrc():

    srcIP = request.form["srcIP"]
    srcPath = request.form["srcPath"]

    if srcIP and srcPath:
        
        print("Sending request ...")
        directory = "/home"
        node_id = "1234"
        srcFiles = rmq.send_request(node_id, "list", srcPath)


        # topic = "ls_src"
        # IP_addr = f'IP Address: {srcIP}'
        # file_path = f'Path: {srcPath}'

        # socket.send_string("%s\n%s\n%s" % (topic, IP_addr, file_path))

        # srcFiles = socket.recv_json()
        # print("Received reply %s" % message)
        # srcFiles = getFiles(srcCollection, srcPath)
    else:
        srcFiles = []

    # print(srcFiles)

    # return jsonify({'files': srcFiles["DATA"]})
    return jsonify({'files': srcFiles})


@app.route('/updateDest', methods=['POST'])
def updateDest():

    destIP = request.form["destIP"]
    destPath = request.form["destPath"]

    if destIP and destPath:
        # topic = "ls_dest"
        # IP_addr = f'IP Address: {destIP}'
        # file_path = f'Path: {destPath}'

        # print("Sending request ...")
        # socket.send_string("%s\n%s\n%s" % (topic, IP_addr, file_path))

        # destFiles = socket.recv_json()
        # print("Received reply %s" % message)
        # srcFiles = getFiles(srcCollection, srcPath)

        print("Sending request ...")
        directory = "/home"
        node_id = "1234"
        destFiles = rmq.send_request(node_id, "list", destPath)
    else:
        destFiles = []

    # return jsonify({'files': destFiles["DATA"]})
    return jsonify({'files': destFiles})


@app.route('/transferFiles', methods=['POST', 'GET'])
def transferFiles():

    srcIP = request.form["srcIP"]
    srcPath = request.form["srcPath"]
    destIP = request.form["destIP"]
    destPath = request.form["destPath"]
    selectedFiles = request.form.getlist("selectedFiles[]")

    topic = "transfer_files"
    src_IP_addr = f'Source IP Address: {srcIP}'
    src_path = f'Source File Path: {srcPath}'
    dest_IP_addr = f'Destination IP Address: {destIP}'
    dest_path = f'Destination File Path: {destPath}'

    print("Sending request ...")
    socket.send_string("%s\n%s\n%s\n%s\n%s" % (topic, src_IP_addr, src_path, dest_IP_addr, dest_path))

    transfer_status = socket.recv_string()
    print(transfer_status)
    file_data = jsonify({'data': selectedFiles})

    epochTime = datetime.datetime.now().timestamp()
    requestTime = datetime.datetime.now().strftime("%m/%d/%Y, %I:%M %p")

    post = {
        "user": session.get("user")["userinfo"]["name"],
        "user_email": session.get("user")["userinfo"]["email"],
        "affiliation": session.get("user")["userinfo"]["https://cilogon.org/idp_name"],
        "srcIP": srcIP,
        "srcPath": srcPath,
        "destIP": destIP,
        "destPath": destPath,
        "selectedFiles": selectedFiles,
        "epochTime":  epochTime,
        "requestTime": requestTime,
        "completionTime": "12345 [temp val]",
        "transferDuration": "12345 [temp val]",
        "transferStatus": "In Progress [temp val]"
        }

    # cloud MongoDB
    # collection.insert_one(post)
    l_transfer_data.insert_one(post)

    return file_data
    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=env.get("PORT", 3000))
