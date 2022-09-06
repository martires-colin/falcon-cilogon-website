import json
import zmq
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
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
    print(token)
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


@app.route("/userInfo")
def userInfo():
    return render_template(
            "home.html",
            session=session.get("user"),
            pretty=json.dumps(session.get("user"), indent=4),
            page="UserInfo"
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


@app.route('/transferFiles', methods=['POST'])
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

    return file_data


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=env.get("PORT", 3000))