file_data = {
  "DATA": [
    {
      "DATA_TYPE": "file",
      "group": "G-818990",
      "last_modified": "2022-07-22 20:20:08+00:00",
      "link_group": None,
      "link_last_modified": None,
      "link_size": None,
      "link_target": None,
      "link_user": None,
      "name": ".bash_history",
      "permissions": "0600",
      "size": 150,
      "type": "file",
      "user": "tg882963"
    },
    {
      "DATA_TYPE": "file",
      "group": "G-818990",
      "last_modified": "2022-07-14 01:43:12+00:00",
      "link_group": None,
      "link_last_modified": None,
      "link_size": None,
      "link_target": None,
      "link_user": None,
      "name": ".bashrc",
      "permissions": "0700",
      "size": 4030,
      "type": "file",
      "user": "tg882963"
    },
    {
      "DATA_TYPE": "file",
      "group": "G-818990",
      "last_modified": "2022-07-14 01:43:12+00:00",
      "link_group": None,
      "link_last_modified": None,
      "link_size": None,
      "link_target": None,
      "link_user": None,
      "name": ".cshrc",
      "permissions": "0700",
      "size": 2636,
      "type": "file",
      "user": "tg882963"
    },
    {
      "DATA_TYPE": "file",
      "group": "G-818990",
      "last_modified": "2022-07-14 01:43:12+00:00",
      "link_group": None,
      "link_last_modified": None,
      "link_size": None,
      "link_target": None,
      "link_user": None,
      "name": ".login",
      "permissions": "0700",
      "size": 381,
      "type": "file",
      "user": "tg882963"
    },
    {
      "DATA_TYPE": "file",
      "group": "G-818990",
      "last_modified": "2022-07-14 01:43:12+00:00",
      "link_group": None,
      "link_last_modified": None,
      "link_size": None,
      "link_target": None,
      "link_user": None,
      "name": ".profile",
      "permissions": "0700",
      "size": 717,
      "type": "file",
      "user": "tg882963"
    },
    {
      "DATA_TYPE": "file",
      "group": "G-818990",
      "last_modified": "2022-07-22 20:10:18+00:00",
      "link_group": None,
      "link_last_modified": None,
      "link_size": None,
      "link_target": None,
      "link_user": None,
      "name": ".ssh",
      "permissions": "0700",
      "size": 4096,
      "type": "dir",
      "user": "tg882963"
    },
    {
      "DATA_TYPE": "file",
      "group": "G-818990",
      "last_modified": "2022-07-22 20:31:02+00:00",
      "link_group": None,
      "link_last_modified": None,
      "link_size": None,
      "link_target": None,
      "link_user": None,
      "name": "test_stampede.txt",
      "permissions": "0600",
      "size": 0,
      "type": "file",
      "user": "tg882963"
    }
  ],
  "DATA_TYPE": "file_list",
  "absolute_path": None,
  "endpoint": "ceea5ca0-89a9-11e7-a97f-22000a92523b",
  "length": 7,
  "path": "/~/",
  "rename_supported": True,
  "symlink_supported": False,
  "total": 7
}

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

    # channel.queue_declare(queue='connections')
    channel.queue_declare(queue='access_token')
    channel.queue_declare(queue='reply')


    def callback(ch, method, properties, body):
        print(" [x] Received %r" % json.loads(body))

        print(ch)
        print(method)
        print(properties)


        payload = {
            "msg": "YOOO"
        }

        ch.basic_publish(
            exchange='',
            routing_key='reply',
            body=json.dumps(file_data)
        )


    # channel.basic_consume(queue='connections', on_message_callback=callback, auto_ack=True)
    channel.basic_consume(queue='access_token', on_message_callback=callback, auto_ack=True)


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