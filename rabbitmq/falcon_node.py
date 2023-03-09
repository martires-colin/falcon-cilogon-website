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
        self.verified = "-1"


    def on_request(self, ch, method, props, body):
        daemon = Thread(
            target=self.execute_request, args=(props, body), daemon=True, 
            name="falcon_request"
        )
        daemon.start()


    def execute_request(self, props, body):
        request = json.loads(body.decode())

        if request["command"] == "verify":
            response = self.verify_connection(request["argument"])
        elif self.verified != "0":
            response = json.dumps({"error": "Node is unverified."})
        elif request["command"] == "list":
            response = self.list_files(request["argument"])
        elif request["command"] == "transfer":
            response = self.transfer_files(request["argument"], request["argument2"])

        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.basic_publish(
            exchange="", routing_key=props.reply_to, body=response,
            properties=pika.BasicProperties(correlation_id=props.correlation_id)
        )

        connection.close()
        
        if self.verified == "0":
            output = {
                "verify": " [x] Verified connection with Falcon server.",
                "list": f" [x] Listed contents of {request['argument']}.",
                "transfer": f" [x] Completed transfer to {request['argument']}."
            }
            print(output[request["command"]])
        

    def verify_connection(self, access_token):
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
            self.verified = "0"

        except:
            # TODO: handle failed verification
            print(" [x] Connection with Falcon server could not be verified.")
            self.verified = "0"

        return json.dumps({"verification_result": self.verified})
            

    def list_files(self, directory):
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

        response = {
            "DATA_TYPE": "file_list",
            "path": directory,
            "DATA": data_list
        }

        return json.dumps(response)


    def get_directory_size(self, start_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)

        return total_size


    def transfer_files(self, receiver_ip, files):
        print(f" [x] Initiating transfer to {receiver_ip}")

        files = json.loads(files)
        root = files["path"]
        all_files = []
        for file in files["DATA"]:
            file_path = os.path.join(root, file["name"])
            if file["type"] == "file":
                all_files.append(file_path)
            else:
                for dirpath, dirnames, filenames in os.walk(file_path):
                    for filename in filenames:
                        all_files.append(os.path.join(dirpath, filename))
            
        time.sleep(5) # TODO: start file transfer

        return json.dumps({"transfer_result": "0"}) # TODO: generate response


if __name__ == '__main__':
    try:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()


        ### Send connection message to server
        connection_message = {
            "ip": ip,
            "status": "online"
            # TODO: add all node details 
        }
        connection_message = json.dumps(connection_message)

        connection_queue = "connections"
        channel.basic_publish(
            exchange="", routing_key=connection_queue, body=connection_message
        )
        print(" [x] Connected to the Falcon server.")


        ### Consume and execute requests
        consumer = Consumer()
        channel.queue_declare(queue=ip)
        channel.basic_consume(
            queue=ip, auto_ack=True, on_message_callback=consumer.on_request
        )
        print(" [x] Waiting for messages from Falcon server...")
        channel.start_consuming()
        

    except KeyboardInterrupt:
        connection.close()
        print(" [x] Falcon node was interrupted.")
        sys.exit(0)