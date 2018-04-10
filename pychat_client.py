import socket, sys, os
from threading import Thread
from ECC import ECCipher
from Point import Point
import pychat_util


def listen_to_server():
    global msg_prefix, shared_key
    while True:
        try:
            msg = server_connection.recv(READ_BUFFER)
        except:
            os._exit(2)

        if not msg:
            print("Server down!")
            os._exit(2)

        else:
            if msg == pychat_util.QUIT_STRING.encode():
                sys.stdout.write('Bye\n')
                server_connection.close()
                os._exit(2)

            else:
                # If the server hasn't send it's partial key yet
                if shared_key is None:
                    msg_prefix = 'name: '  # identifier for name
                    sys.stdout.write("Welcome to pychat.\nPlease tell us your name:\n")
                    shared_key = cipher.gen_fancy_des_shared_key(secret_key, msg)

                else:
                    #TODO: Decrypt the non-QUIT and PartialKey response here first

                    decoded = msg.decode(encoding='UTF-8', errors='ignore')
                    msg_prefix = ''
                    sys.stdout.write(decoded)
                print('>', end=' ', flush=True)


def listen_to_stdin():
    while True:
        msg = sys.stdin.readline()
        msg = msg_prefix + msg
        msg_bytes = msg.encode()

        # TODO: Encrypt the msg buffer here first, including the first username buffer

        # If this is the first message sent, include the partial key
        if msg_prefix == 'name: ':
            msg_bytes = bytes(cipher.gen_fancy_des_partial_key(secret_key)) + msg_bytes

        server_connection.sendall(msg_bytes)


READ_BUFFER = 4096

if len(sys.argv) < 2:
    print("Usage: python client.py [hostname]", file = sys.stderr)
    sys.exit(1)
else:
    server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_connection.connect((sys.argv[1], pychat_util.PORT))

print("Connected to server\n")
cipher = ECCipher(-1, 188, 7919, Point(224, 503), 20)
secret_key = cipher.gen_fancy_des_secret_key()
msg_prefix = ''
shared_key = None

Thread(target=listen_to_server).start()
listen_to_stdin()

