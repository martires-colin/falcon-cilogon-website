
# RabbitMQ communication for Falcon node


from config_rabbitmq import configurations
from threading import Thread
import requests
import json
import time
import pika
import sys
import jwt
import os


credentials = pika.PlainCredentials(
    username=configurations["user"], password=configurations["password"], 
    erase_on_connect=True
)
parameters = pika.ConnectionParameters(
    host=configurations["host"], port=configurations["port"], 
    virtual_host=configurations["vhost"], credentials=credentials
)

ip = requests.get('https://checkip.amazonaws.com').text.strip()


class Consumer:
    def __init__(self):
        self.status = "online"


    def on_request(self, ch, method, props, body):
        daemon = Thread(
            target=self.execute_request, args=(props, body), daemon=True, 
            name="falcon_request"
        )
        daemon.start()


    def execute_request(self, props, body):
        request = json.loads(body.decode())

        if request["command"] == "verify":
            response = self.verify(request["argument"])
        elif self.status != "verified":
            response = json.dumps({"success": False})

        elif request["command"] == "list":
            response = self.list_directory(request["argument"])
        elif request["command"] == "send":
            response = self.send(request["argument"], request["argument2"])
        elif request["command"] == "receive":
            response = self.receive(request["argument"], request["argument2"])

        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.basic_publish(
            exchange="", routing_key=props.reply_to, body=response,
            properties=pika.BasicProperties(correlation_id=props.correlation_id)
        )

        connection.close()
        
        if self.status == "verified":
            output_messages = {
                "verify": " [x] Verified connection with Falcon server.",
                "list": f" [x] Listed contents of {request['argument']}.",
                "send": f" [x] Finished sending files to {request['argument']}.",
                "receive" : f" [x] Finished receiving files from {request['argument']}."
            }
            print(output_messages[request["command"]])
        

    def verify(self, access_token):
        try:
            token = json.loads(access_token)["id_token_jwt"]
            unvalidated = jwt.decode(token, options={"verify_signature": False})
            well_known_url = unvalidated["iss"] + "/.well-known/openid-configuration"
            aud = unvalidated["aud"]

            jwks_url = json.loads(requests.get(well_known_url).text.strip())["jwks_uri"]
            jwks_client = jwt.PyJWKClient(jwks_url)
            header = jwt.get_unverified_header(token)
            key = jwks_client.get_signing_key(header["kid"]).key

            decoded = jwt.decode(token, key, audience=aud, algorithms=[header["alg"]])
            self.status = "verified"
            verification_result = True

        except:
            # TODO: handle failed verification
            self.status = "verified" # TODO: delete after testing
            verification_result = True # TODO: set to False after testing
            print(" [x] ERROR - Connection with Falcon web server could not be verified.")

        return json.dumps({"success": verification_result})
            

    def list_directory(self, directory):
        data_list = []

        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            is_dir = os.path.isdir(file_path)

            file_data = {
                "DATA_TYPE": "file",
                "name": file,
                "type": "dir" if is_dir else "file",
                "user": ip,
                "last_modified": time.ctime(os.path.getmtime(file_path)),
                "size": self.get_directory_size(file_path) if is_dir \
                    else os.path.getsize(file_path)
            }
            data_list.append(file_data)

        files = {
            "DATA_TYPE": "file_list",
            "path": directory,
            "DATA": data_list
        }

        return json.dumps({"success": True, "files": files})


    def get_directory_size(self, start_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)

        return total_size


    def send(self, receiver_ip, files):
        print(f" [x] Starting file transfer to {receiver_ip}")

        file_list = files.split(",")

        config_sender = {
            "receiver": {
                "host": receiver_ip,
                "port": 50021
            },
            "data_dir": "/falcon/source",
            "method": "gradient", # options: [gradient, bayes, random, brute, probe, cg, lbfgs]
            "bayes": {
                "initial_run": 3,
                "num_of_exp": -1 #-1 for infinite
            },
            "random": {
                "num_of_exp": 10
            },
            "emulab_test": False, # True for per process I/O limit emulation
            "centralized": False, # True for centralized optimization
            "file_transfer": True,
            "B": 10, # severity of the packet loss punishment
            "K": 1.02, # cost of increasing concurrency
            "loglevel": "info",
            "probing_sec": 5, # probing interval in seconds
            "multiplier": 1, # multiplier for each files, only for testing purpose
            "mp_opt": False, # Always False for python version
            "fixed_probing": {
                "bsize": 10,
                "thread": 5
            },
            "max_cc": 20,
        }

        with open("config_sender.py", "w") as file:
            file.write("configurations = ")
            file.write(json.dumps(config_sender))
            
        time.sleep(5) # TODO: call Falcon sender

        return json.dumps({"success": True})


    def get_file_list(self, files):
        files = json.loads(files)
        root = files["path"]
        file_list = []

        for file in files["DATA"]:
            file_path = os.path.join(root, file["name"])
            if file["type"] == "file":
                file_list.append(file_path)
            else:
                for dirpath, dirnames, filenames in os.walk(file_path):
                    for filename in filenames:
                        file_list.append(os.path.join(dirpath, filename))

        return file_path
    

    def receive(self, sender_ip, files):
        print(f" [x] Receiving files from {sender_ip}")

        file_list = files.split(",")

        config_receiver = {
            "receiver": {
                "host": ip,
                "port": 50021
            },
            "data_dir": "/home/ptrue/Falcon-Test-Folder1",
            "max_cc": 20,
            "file_transfer": True,
            "loglevel": "info",
        }

        with open("config_receiver.py", "w") as file:
            file.write("configurations = ")
            file.write(json.dumps(config_receiver))
            
        time.sleep(5) # TODO: call Falcon receiver

        return json.dumps({"success": True})


if __name__ == "__main__":
    try:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        online_message = json.dumps({"ip": ip, "status": "online"})
        connection_queue = "connections"
        channel.basic_publish(
            exchange="", routing_key=connection_queue, body=online_message
        )
        print(" [x] Connected to the Falcon web server.")

        consumer = Consumer()
        channel.queue_declare(queue=ip)
        channel.basic_consume(
            queue=ip, auto_ack=True, on_message_callback=consumer.on_request
        )
        print(" [x] Waiting for messages from Falcon web server...")
        channel.start_consuming()
        
    except KeyboardInterrupt:
        offline_message = json.dumps({"ip": ip, "status": "offline"})
        channel.basic_publish(
            exchange="", routing_key=connection_queue, body=offline_message
        )

        connection.close()
        print(" [x] Falcon node was interrupted.")
        sys.exit(0)