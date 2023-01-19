import pika, sys, os, json

def main():

    credentials = pika.PlainCredentials(
        username='cmart',
        password='46Against19!'
    )
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='35.93.147.38',
        port=5672,
        virtual_host='demo',
        credentials=credentials
    ))

    channel = connection.channel()

    channel.queue_declare(queue='connections')

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % json.loads(body))

    channel.basic_consume(queue='connections', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)