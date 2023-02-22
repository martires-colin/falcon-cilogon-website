# Mock of Falcon server communication with Falcon node

# import rmq_server as rmq

# if __name__ == '__main__':
#     # Get Falcon node ID
#     node_id = "1234"

#     # Send access token to Falcon node
#     payload = {'access_token': 'NB2HI4DTHIXS6Y3JNRXWO33OFZXXEZZPN5QXK5DIGIXTOZT\
#         CHAYDMZJRGQZTGNZTG43DAMRZGFSWMMJWGRSTMMLFGRTDMMB7OR4XAZJ5MFRWGZLTONKG62\
#         3FNYTHI4Z5GE3DONJRGM4TGNJYGEZDMJTWMVZHG2LPNY6XMMROGATGY2LGMV2GS3LFHU4TA\
#         MBQGAYA', 'id_token_jwt': 'eyJ0eXAiOiJKV1QiLCJraWQiOiIyNDRCMjM1RjZCMjhF\
#         MzQxMDhEMTAxRUFDNzM2MkM0RSIsImFsZyI6IlJTMjU2In0.eyJlbWFpbCI6ImNtYXJ0aXJ\
#         lc0BuZXZhZGEudW5yLmVkdSIsImdpdmVuX25hbWUiOiJDb2xpbiIsImZhbWlseV9uYW1lIj\
#         oiTWFydGlyZXMiLCJuYW1lIjoiQ29saW4gTCBNYXJ0aXJlcyIsImNlcnRfc3ViamVjdF9kb\
#         iI6Ii9EQz1vcmcvREM9Y2lsb2dvbi9DPVVTL089VW5pdmVyc2l0eSBvZiBOZXZhZGEsIFJl\
#         bm8vQ049Q29saW4gTWFydGlyZXMgRTE1Mjc2IiwiaWRwIjoiaHR0cHM6Ly9pZHAyLnVuci5\
#         lZHUvaWRwL3NoaWJib2xldGgiLCJpZHBfbmFtZSI6IlVuaXZlcnNpdHkgb2YgTmV2YWRhLC\
#         BSZW5vIiwiZXBwbiI6ImNtYXJ0aXJlc0B1bnIuZWR1IiwiZXB0aWQiOiJodHRwczovL2lkc\
#         DIudW5yLmVkdS9pZHAvc2hpYmJvbGV0aCFodHRwczovL2NpbG9nb24ub3JnL3NoaWJib2xl\
#         dGghWmZaS1pVWFRhT2w2WmFmT3FXdmM0YWRVWnRnPSIsImFmZmlsaWF0aW9uIjoibWVtYmV\
#         yQHVuci5lZHU7ZmFjdWx0eUB1bnIuZWR1O2xpYnJhcnktd2Fsay1pbkB1bnIuZWR1O3N0YW\
#         ZmQHVuci5lZHU7ZW1wbG95ZWVAdW5yLmVkdTtzdHVkZW50QHVuci5lZHUiLCJhY3IiOiJ1c\
#         m46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6YWM6Y2xhc3NlczpQYXNzd29yZFByb3RlY3Rl\
#         ZFRyYW5zcG9ydCIsImlzcyI6Imh0dHBzOi8vY2lsb2dvbi5vcmciLCJzdWIiOiJodHRwOi8\
#         vY2lsb2dvbi5vcmcvc2VydmVyRS91c2Vycy8xNTI3NiIsImF1ZCI6ImNpbG9nb246L2NsaW\
#         VudF9pZC8xYTA1MTE0NWVjYjQzNzUwOGVkOGE4ODcxYmVkN2I3NyIsImp0aSI6Imh0dHBzO\
#         i8vY2lsb2dvbi5vcmcvb2F1dGgyL2lkVG9rZW4vM2M5Nzg3ZDk0ZmY2OWY2MWJjNTk0MmEx\
#         NjgzMzA5Zi8xNjc1MTM5MzU3NzM0Iiwibm9uY2UiOiJ1UW13QW5yQ1pEYlNXUnZ0IiwiYXV\
#         0aF90aW1lIjoxNjc1MTM3ODAyLCJleHAiOjE2NzUxNDAyNTcsImlhdCI6MTY3NTEzOTM1N3\
#         0.bRCxvj-sQXDYitUAacDyEZ2kJOVMmQEImlygzOeaStM_Tp7gKOmnKH46lb3n0iEPp0Y-H\
#         Ublpfk7aq9I4mCF1idoChcxmnp_TFh9_ivDIfEk0QQiEis1owBH-rJVq7OXIHGt2cNzUYaJ\
#         IFIXe2D-m-2nMJt29odV1UFmOPQht21fQe3J3coCcapItTuG8E5e50JiGCdYFwlMpIHl1nd\
#         J-yqV0mxnlqESn0DK0WgKlTIAsokOoWUlNgv6QDySGB8mmH-T4gKDlatylz2qNSQ-szW-La\
#         vJFgIAm2u55dKTG-e0yO2IXJ2SSjYhZDvXAiz6VtPTMmIBdq4-1IzWeg_GeA'
#     }
#     rmq.send_access_token(node_id, payload)

#     # Request file list from Falcon node
#     directory = "/home"
#     rmq.send_request(node_id, "list", directory)

#     # Request transfer from Falcon node
#     files = ",".join(["test1.txt", "test2.txt"])
#     rmq.send_request(node_id, "transfer", files)

# Mock of Falcon server communication with Falcon node


from threading import Thread
import rmq_server as rmq
import json
import sys
import os


if __name__ == '__main__':
    node_ip = "1234" # IP address of Falcon node


    ### Consume connection messages from Falcon nodes
    daemon = Thread(
        target=rmq.manage_connections, daemon=True, name=f"manage_falcon_connections"
    )
    daemon.start()


    ### Send access token to Falcon node
    access_token = {'access_token': 'NB2HI4DTHIXS6Y3JNRXWO33OFZXXEZZPN5QXK5DIGIXTOZT'+
        'CHAYDMZJRGQZTGNZTG43DAMRZGFSWMMJWGRSTMMLFGRTDMMB7OR4XAZJ5MFRWGZLTONKG62'+
        '3FNYTHI4Z5GE3DONJRGM4TGNJYGEZDMJTWMVZHG2LPNY6XMMROGATGY2LGMV2GS3LFHU4TA'+
        'MBQGAYA', 'id_token_jwt': 'eyJ0eXAiOiJKV1QiLCJraWQiOiIyNDRCMjM1RjZCMjhF'+
        'MzQxMDhEMTAxRUFDNzM2MkM0RSIsImFsZyI6IlJTMjU2In0.eyJlbWFpbCI6ImNtYXJ0aXJ'+
        'lc0BuZXZhZGEudW5yLmVkdSIsImdpdmVuX25hbWUiOiJDb2xpbiIsImZhbWlseV9uYW1lIj'+
        'oiTWFydGlyZXMiLCJuYW1lIjoiQ29saW4gTCBNYXJ0aXJlcyIsImNlcnRfc3ViamVjdF9kb'+
        'iI6Ii9EQz1vcmcvREM9Y2lsb2dvbi9DPVVTL089VW5pdmVyc2l0eSBvZiBOZXZhZGEsIFJl'+
        'bm8vQ049Q29saW4gTWFydGlyZXMgRTE1Mjc2IiwiaWRwIjoiaHR0cHM6Ly9pZHAyLnVuci5'+
        'lZHUvaWRwL3NoaWJib2xldGgiLCJpZHBfbmFtZSI6IlVuaXZlcnNpdHkgb2YgTmV2YWRhLC'+
        'BSZW5vIiwiZXBwbiI6ImNtYXJ0aXJlc0B1bnIuZWR1IiwiZXB0aWQiOiJodHRwczovL2lkc'+
        'DIudW5yLmVkdS9pZHAvc2hpYmJvbGV0aCFodHRwczovL2NpbG9nb24ub3JnL3NoaWJib2xl'+
        'dGghWmZaS1pVWFRhT2w2WmFmT3FXdmM0YWRVWnRnPSIsImFmZmlsaWF0aW9uIjoibWVtYmV'+
        'yQHVuci5lZHU7ZmFjdWx0eUB1bnIuZWR1O2xpYnJhcnktd2Fsay1pbkB1bnIuZWR1O3N0YW'+
        'ZmQHVuci5lZHU7ZW1wbG95ZWVAdW5yLmVkdTtzdHVkZW50QHVuci5lZHUiLCJhY3IiOiJ1c'+
        'm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6YWM6Y2xhc3NlczpQYXNzd29yZFByb3RlY3Rl'+
        'ZFRyYW5zcG9ydCIsImlzcyI6Imh0dHBzOi8vY2lsb2dvbi5vcmciLCJzdWIiOiJodHRwOi8'+
        'vY2lsb2dvbi5vcmcvc2VydmVyRS91c2Vycy8xNTI3NiIsImF1ZCI6ImNpbG9nb246L2NsaW'+
        'VudF9pZC8xYTA1MTE0NWVjYjQzNzUwOGVkOGE4ODcxYmVkN2I3NyIsImp0aSI6Imh0dHBzO'+
        'i8vY2lsb2dvbi5vcmcvb2F1dGgyL2lkVG9rZW4vM2M5Nzg3ZDk0ZmY2OWY2MWJjNTk0MmEx'+
        'NjgzMzA5Zi8xNjc1MTM5MzU3NzM0Iiwibm9uY2UiOiJ1UW13QW5yQ1pEYlNXUnZ0IiwiYXV'+
        '0aF90aW1lIjoxNjc1MTM3ODAyLCJleHAiOjE2NzUxNDAyNTcsImlhdCI6MTY3NTEzOTM1N3'+
        '0.bRCxvj-sQXDYitUAacDyEZ2kJOVMmQEImlygzOeaStM_Tp7gKOmnKH46lb3n0iEPp0Y-H'+
        'Ublpfk7aq9I4mCF1idoChcxmnp_TFh9_ivDIfEk0QQiEis1owBH-rJVq7OXIHGt2cNzUYaJ'+
        'IFIXe2D-m-2nMJt29odV1UFmOPQht21fQe3J3coCcapItTuG8E5e50JiGCdYFwlMpIHl1nd'+
        'J-yqV0mxnlqESn0DK0WgKlTIAsokOoWUlNgv6QDySGB8mmH-T4gKDlatylz2qNSQ-szW-La'+
        'vJFgIAm2u55dKTG-e0yO2IXJ2SSjYhZDvXAiz6VtPTMmIBdq4-1IzWeg_GeA'
    }
    access_token = json.dumps(access_token)

    rmq.make_request(node_ip, "verify", access_token)


    ### Request file list from Falcon node
    directory = "/home/ptrue/Falcon-Test-Folder1"

    daemon = Thread(
        target=rmq.make_request, args=(node_ip, "list", directory), 
        daemon=True, name=f"{node_ip}_list_request"
    )
    daemon.start()
    # response = rmq.send_request(node_ip, "list", directory) returns response


    ### Request transfer from Falcon node
    receiver_ip = "5678"
    files = [
        "/home/ptrue/Falcon-Test-Folder1", 
        "/home/ptrue/Falcon-Test-Folder2"
    ]
    file_list = ",".join(files)

    daemon = Thread(
        target=rmq.make_request, args=(node_ip, "transfer", receiver_ip, file_list), 
        daemon=True, name=f"{node_ip}_transfer_request"
    )
    daemon.start()
    # response = rmq.send_request(node_ip, "transfer", receiver_ip, files)


    ### Interrupt with 'Ctrl+C'
    while True:
        try:
            pass

        except KeyboardInterrupt:
            print(" [x] Falcon server was interrupted.")
            sys.exit(0)