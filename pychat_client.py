import socket, sys, os
from threading import Thread
from ECC import ECCipher
from Point import Point
import pychat_util


class PychatClient:
    def __init__(self, host):
        self.READ_BUFFER = 4096

        self.server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_connection.connect((sys.argv[1], pychat_util.PORT))

        print("Connected to server\n")
        self.cipher = ECCipher(-1, 188, 7919, Point(224, 503), 20)
        self.secret_key = self.cipher.gen_fancy_des_secret_key()
        self.msg_prefix = ''
        self.shared_key = None

    def listen_to_server(self):
        while True:
            msg = self.server_connection.recv(self.READ_BUFFER)
            if not msg:
                print("Server down!")
                os._exit(2)
            else:
                self.handle_server_msg(msg)

    def handle_server_msg(self, msg):
        if msg == pychat_util.QUIT_STRING.encode():
            sys.stdout.write('Bye\n')
            self.server_connection.close()
            os._exit(2)

        else:
            # If the server hasn't send it's partial key yet
            if self.shared_key is None:
                self.msg_prefix = 'name: '  # identifier for name
                sys.stdout.write("Welcome to pychat.\nPlease tell us your name:\n")
                self.shared_key = self.cipher.gen_fancy_des_shared_key(self.secret_key, msg)

            else:
                # TODO: Decrypt the non-QUIT and PartialKey response here first

                decoded = msg.decode(encoding='UTF-8', errors='ignore')
                self.msg_prefix = ''
                sys.stdout.write(decoded)

            print('>', end=' ', flush=True)

    def listen_to_stdin(self):
        while True:
            msg = sys.stdin.readline()
            msg = self.msg_prefix + msg
            msg_bytes = msg.encode()

            # TODO: Encrypt the msg buffer here first, including the first username buffer

            # If this is the first message sent to server, prepend the partial key
            if self.msg_prefix == 'name: ':
                msg_bytes = bytes(self.cipher.gen_fancy_des_partial_key(self.secret_key)) + msg_bytes

            self.server_connection.sendall(msg_bytes)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python client.py [hostname]", file=sys.stderr)
        sys.exit(1)

    else:
        client = PychatClient(sys.argv[1])
        Thread(target=client.listen_to_server).start()
        client.listen_to_stdin()
