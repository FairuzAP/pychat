import socket, sys, os
from threading import Thread
from ECC import ECCipher
from Point import Point
from fancyDES import FancyDES
import pychat_util


class PychatClient:
    def __init__(self, host):
        self.READ_BUFFER = 4096

        self.server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_connection.connect((sys.argv[1], pychat_util.PORT))

        print("Connected to server\n")
        self.curve = ECCipher(-1, 188, 7919, Point(224, 503), 20)
        self.secret_key = self.curve.gen_fancy_des_secret_key()
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
        # If the server hasn't send it's partial key yet
        if self.shared_key is None:
            msg_bytes = bytes(self.curve.gen_fancy_des_partial_key(self.secret_key))
            self.server_connection.sendall(msg_bytes)

            self.shared_key = self.curve.gen_fancy_des_shared_key(self.secret_key, msg)

            self.msg_prefix = 'name: '  # identifier for name
            sys.stdout.write("Welcome to pychat.\nPlease tell us your name:\n")

        else:
            # Decrypt the non-PartialKey response
            msg = FancyDES(key=self.shared_key).decrypt(message=msg, fromFile=False, mode="CBC")
            decoded = msg.decode().rstrip('\0')

            if decoded == pychat_util.QUIT_STRING:
                sys.stdout.write('Bye\n')
                self.server_connection.close()
                os._exit(2)

            self.msg_prefix = ''
            sys.stdout.write(decoded)

        print('>', end=' ', flush=True)

    def listen_to_stdin(self):
        while True:
            msg = sys.stdin.readline()
            msg = self.msg_prefix + msg

            # Encrypt the msg buffer here first, except the first username buffer
            msg_bytes = FancyDES(key=self.shared_key).encrypt(message=msg.encode(), fromFile=False, mode="CBC")

            self.server_connection.sendall(msg_bytes)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python client.py [hostname]", file=sys.stderr)
        sys.exit(1)

    else:
        client = PychatClient(sys.argv[1])
        Thread(target=client.listen_to_server).start()
        client.listen_to_stdin()
