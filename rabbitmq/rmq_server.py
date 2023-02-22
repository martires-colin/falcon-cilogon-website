# RabbitMQ communication for Falcon server

# added rabbitmq. fo server.py can find the config file ~Colin
# from rabbitmq.config_rabbitmq import configurations
# from uuid import uuid4
# import json
# import pika

# class RabbitMQServer:
#     def __init__(self):
#         credentials = pika.PlainCredentials(
#             username=configurations["user"], 
#             password=configurations["password"], 
#             erase_on_connect=True
#         )
#         parameters = pika.ConnectionParameters(
#             host=configurations["host"], 
#             port=configurations["port"], 
#             virtual_host=configurations["vhost"], 
#             credentials=credentials
#         )

#         self.connection = pika.BlockingConnection(parameters)
#         self.channel = self.connection.channel()

#         self.callback_queue = None
#         self.corr_id = None
#         self.response = None

#     def on_response(self, ch, method, props, body):
#         if self.corr_id == props.correlation_id:
#             self.response = body.decode()


# def send_access_token(client_id, payload):
#     server = RabbitMQServer()
#     server.channel.queue_declare(queue=client_id)
    
#     server.channel.basic_publish(
#         exchange="",
#         routing_key=client_id,
#         body=json.dumps(payload)
#     )
    
#     server.connection.close()
#     print(f" [x] Sent access token to {client_id}")


# def send_request(client_id, command, argument):
#     server = RabbitMQServer()
#     result = server.channel.queue_declare(queue="", exclusive=True)
#     server.callback_queue = result.method.queue
#     server.channel.basic_consume(
#         queue=server.callback_queue, 
#         on_message_callback=server.on_response,
#         auto_ack=True
#     )

#     server.response = None
#     server.corr_id = str(uuid4())
#     message = {"command": command, "argument": argument}
#     message = json.dumps(message)

#     server.channel.basic_publish(
#         exchange="", routing_key=client_id, body=message,
#         properties=pika.BasicProperties(
#             reply_to=server.callback_queue, correlation_id=server.corr_id
#         )
#     )
#     print(f" [x] {client_id}: Sent request: {command} {argument}")

#     server.connection.process_data_events(time_limit=None)

#     server.connection.close()
#     print(f" [x] {client_id}: Received response: {server.response}")

#     return server.response





# RabbitMQ communication for Falcon server


from rabbitmq.config_rabbitmq import configurations
import uuid
import json
import pika


credentials = pika.PlainCredentials(
    username=configurations["user"], password=configurations["password"], 
    erase_on_connect=True
)
parameters = pika.ConnectionParameters(
    host=configurations["host"], port=configurations["port"], 
    virtual_host=configurations["vhost"], credentials=credentials
)


class RequestConnection:
    def __init__(self):
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        callback_queue = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = callback_queue.method.queue
        self.channel.basic_consume(
            queue=self.callback_queue, on_message_callback=self.on_response, 
            auto_ack=True
        )

        self.corr_id =str(uuid.uuid4())
        self.properties=pika.BasicProperties(
            reply_to=self.callback_queue, correlation_id=self.corr_id
        )
        self.response = None
    

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body.decode())


def make_request(node_ip, command, argument, argument2=None):
    request = RequestConnection()
    
    message = {"command": command, "argument": argument}
    if argument2 != None:
        message["argument2"] = argument2
    message = json.dumps(message)

    request.channel.queue_declare(queue=node_ip)
    request.channel.basic_publish(
        exchange="", routing_key=node_ip, body=message,
        properties=request.properties
    )
    print(f" [x] {node_ip}: Sent request: {command} {argument}.")

    request.connection.process_data_events(time_limit=None)
    print(f" [x] {node_ip}: Received response: {request.response}.")

    request.connection.close()

    return request.response


def manage_connections():
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    connection_queue = "connections"
    channel.queue_declare(queue=connection_queue)
    channel.basic_consume(
        queue=connection_queue, on_message_callback=log_connection, 
        auto_ack=True
    )
    channel.start_consuming()


def log_connection(ch, method, props, body):
    connection_message = json.loads(body.decode())

    # If node exists, make updates to db object, else, make new db object

    if connection_message["status"] == "online":
        # TODO: log connection
        # add IP address that node sends on startup to db
        print(f" [x] Node at {connection_message['ip']} is now online.")

    elif connection_message["status"] == "verified":
        # TODO: log connection
        print(f" [x] Node at {connection_message['ip']} is ready for commands.")