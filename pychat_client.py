import socket, sys, os, signal
from threading import Thread
import pychat_util


def listen_to_server():
    global msg_prefix
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
                sys.stdout.write(msg.decode())
                if 'Please tell us your name' in msg.decode():
                    msg_prefix = 'name: '  # identifier for name
                else:
                    msg_prefix = ''
                print('>', end=' ', flush=True)


def listen_to_stdin():
    while True:
        msg = sys.stdin.readline()
        msg = msg_prefix + msg
        server_connection.sendall(msg.encode())


READ_BUFFER = 4096

if len(sys.argv) < 2:
    print("Usage: python client.py [hostname]", file = sys.stderr)
    sys.exit(1)
else:
    server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_connection.connect((sys.argv[1], pychat_util.PORT))

print("Connected to server\n")
msg_prefix = ''
socket_list = [sys.stdin, server_connection]

Thread(target=listen_to_server).start()
listen_to_stdin()

