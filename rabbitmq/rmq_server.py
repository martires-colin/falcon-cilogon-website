# RabbitMQ communication for Falcon server

# added rabbitmq. fo server.py can find the config file ~Colin
from rabbitmq.config_rabbitmq import configurations
from uuid import uuid4
import json
import pika

class RabbitMQServer:
    def __init__(self):
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

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        self.callback_queue = None
        self.corr_id = None
        self.response = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body.decode()


def send_access_token(client_id, payload):
    server = RabbitMQServer()
    server.channel.queue_declare(queue=client_id)
    
    server.channel.basic_publish(
        exchange="",
        routing_key=client_id,
        body=json.dumps(payload)
    )
    
    server.connection.close()
    print(f" [x] Sent access token to {client_id}")


def send_request(client_id, command, argument):
    server = RabbitMQServer()
    result = server.channel.queue_declare(queue="", exclusive=True)
    server.callback_queue = result.method.queue
    server.channel.basic_consume(
        queue=server.callback_queue, 
        on_message_callback=server.on_response,
        auto_ack=True
    )

    server.response = None
    server.corr_id = str(uuid4())
    message = {"command": command, "argument": argument}
    message = json.dumps(message)

    server.channel.basic_publish(
        exchange="", routing_key=client_id, body=message,
        properties=pika.BasicProperties(
            reply_to=server.callback_queue, correlation_id=server.corr_id
        )
    )
    print(f" [x] {client_id}: Sent request: {command} {argument}")

    server.connection.process_data_events(time_limit=None)

    server.connection.close()
    print(f" [x] {client_id}: Received response: {server.response}")

    return server.response