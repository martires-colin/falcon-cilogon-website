# RabbitMQ communication for Falcon node

from config_rabbitmq import configurations
from threading import Thread
import json
import time
import pika
import sys
import jwt
import os

credentials = pika.PlainCredentials(
    username=configurations["user"], 
    password=configurations["password"], 
    erase_on_connect=True
)
parameters = pika.ConnectionParameters(
    host=configurations["host"], 
    port=configurations["port"], 
    virtual_host=configurations["vhost"], 
    credentials=credentials
)

id = "1234" # TODO: choose node id
connection_message = {"id": id} # TODO: add all node details
connection_message = json.dumps(connection_message)


def authenticate_node(channel):
    channel.basic_consume(
        queue=id, on_message_callback=authentication_callback
    )
    print(" [x] Waiting for authentication")
    channel.start_consuming()


def authentication_callback(ch, method, properties, body):
    ch.basic_ack(delivery_tag=method.delivery_tag)

    message = json.loads(body.decode())
    id_token_jwt = jwt.decode(
        message["id_token_jwt"], 
        options={"verify_signature": False}
    )

    # TODO: authenticate node

    ch.stop_consuming()
    print(f" [x] Authentication complete for {id_token_jwt['idp_name']}")


def update_connection(channel):
    connection_queue = "connections"
    channel.basic_publish(
        exchange="", 
        routing_key=connection_queue, 
        body=connection_message
    )
    print(" [x] Sent connection update to server")


def manage_requests():
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue=id)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=id, 
        on_message_callback=request_callback
    )

    print(" [x] Awaiting messages from Falcon user server")
    channel.start_consuming()


def request_callback(ch, method, props, body):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    daemon = Thread(
        target=execute_request, 
        args=(props, body), 
        daemon=True, name="falcon_request"
    )
    daemon.start()


def execute_request(props, body):
    message = json.loads(body.decode())

    if message["command"] == "list":
        directory_list = os.listdir(message["argument"])
        response = ",".join(directory_list)

    elif message["command"] == "transfer":
        print(f" [x] Initiating transfer of {message['argument']}")
        time.sleep(5) # TODO: start file transfer
        response = "0" # TODO: generate response

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.basic_publish(
        exchange="", routing_key=props.reply_to, 
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=response
    )
        
    connection.close()
    if message["command"] == "list":
        print(f" [x] Listed contents of {message['argument']}")
    elif message["command"] == "transfer":
        print(f" [x] Completed transfer of {message['argument']}")


if __name__ == '__main__':
    try:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        authenticate_node(channel)

        daemon = Thread(
            target=manage_requests, daemon=True, name="falcon_request_manager"
        )
        daemon.start()

        while True:
            update_connection(channel)
            time.sleep(30)
        
    except KeyboardInterrupt:
        print(" [x] Falcon node was interrupted")
        try:
            connection.close()
            sys.exit(0)

        except SystemExit:
            connection.close()
            os._exit(0)