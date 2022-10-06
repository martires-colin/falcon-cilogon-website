import json
import zmq
import datetime

from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from pymongo import MongoClient
from flask import Flask, redirect, render_template, session, url_for, request, jsonify

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

context = zmq.Context()
print("Connecting to Falcon server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
# socket = context.socket(zmq.SUB)
# socket.connect("tcp://localhost:5555")

# MongoDB Cloud implementation
# cluster = MongoClient(f'mongodb+srv://{env.get("MONGODB_USERNAME")}:{env.get("MONGODB_PASSWORD")}@cluster0.74uzvj4.mongodb.net/?retryWrites=true&w=majority')
# # cluster = MongoClient("mongodb+srv://cmartires:46Against19!@cluster0.74uzvj4.mongodb.net/?retryWrites=true&w=majority")
# db = cluster["Falcon"]
# collection = db["transfer_data"]

db_client = MongoClient('localhost', 27017)
# , username='{env.get("MONGODB_USERNAME")}', password='{env.get("MONGODB_PASSWORD")}
db = db_client.falcon_db
l_transfer_data = db.l_transfer_data


app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)


@app.route("/")
def home():
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
        page="Dashboard"
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


@app.route("/account")
def account():
    return render_template(
            "home.html",
            session=session.get("user"),
            pretty=json.dumps(session.get("user"), indent=4),
            page="Account"
        )


@app.route("/history")
def history():
    print('balls')
    cursor = l_transfer_data.find().sort("epochTime", -1)
    list_cur = list(cursor)
    return render_template(
            "home.html",
            session=session.get("user"),
            pretty=json.dumps(session.get("user"), indent=4),
            page="History",
            transferData=list_cur
        )


@app.route('/updateSrc', methods=['POST'])
def updateSrc():

    srcIP = request.form["srcIP"]
    srcPath = request.form["srcPath"]

    if srcIP and srcPath:

        topic = "ls_src"
        IP_addr = f'IP Address: {srcIP}'
        file_path = f'Path: {srcPath}'

        print("Sending request ...")
        socket.send_string("%s\n%s\n%s" % (topic, IP_addr, file_path))

        srcFiles = socket.recv_json()
        # print("Received reply %s" % message)
        # srcFiles = getFiles(srcCollection, srcPath)
    else:
        srcFiles = []

    return jsonify({'files': srcFiles["DATA"]})


@app.route('/updateDest', methods=['POST'])
def updateDest():

    destIP = request.form["destIP"]
    destPath = request.form["destPath"]

    if destIP and destPath:
        topic = "ls_dest"
        IP_addr = f'IP Address: {destIP}'
        file_path = f'Path: {destPath}'

        print("Sending request ...")
        socket.send_string("%s\n%s\n%s" % (topic, IP_addr, file_path))

        destFiles = socket.recv_json()
        # print("Received reply %s" % message)
        # srcFiles = getFiles(srcCollection, srcPath)
    else:
        destFiles = []

    return jsonify({'files': destFiles["DATA"]})


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
        "transferStatus": "false [temp val]"
        }

    # cloud MongoDB
    # collection.insert_one(post)
    l_transfer_data.insert_one(post)

    return file_data
    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=env.get("PORT", 3000))
