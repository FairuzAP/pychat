import socket, sys, os
from threading import Thread
from ECC import ECCipher
from Point import Point
from fancyDES import FancyDES
import pychat_util


class PychatClient:
    def __init__(self, host):
        """
        Initialize the client paramater
        :param host: IP addres and port of the server
        """

        # Intialize connection to the chat server
        self.READ_BUFFER = 4096
        self.server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_connection.connect((host, pychat_util.PORT))
        print("Connected to server\n")

        # Initialize the ECC curve, and generate the secret key
        self.curve = ECCipher(-1, 188, 7919, Point(224, 503), 20)
        self.secret_key = self.curve.gen_fancy_des_secret_key()
        self.shared_key = None
        self.msg_prefix = ''

    def listen_to_server(self):
        """ Start the control loop for listening and handling server responses """
        while True:
            msg = self.server_connection.recv(self.READ_BUFFER)
            if not msg:
                print("Server down!")
                os._exit(2)
            else:
                self.handle_server_msg(msg)

    def handle_server_msg(self, msg):
        """
        Handle the msg buffer that is received from the chat server
        :param msg: The msg buffer received from the server
        """

        # If the server hasn't send it's partial key yet
        if self.shared_key is None:

            # Send the Diffie-Hellman public key to the server
            msg_bytes = bytes(self.curve.gen_fancy_des_partial_key(self.secret_key))
            self.server_connection.sendall(msg_bytes)

            # Calculate the shared key between this client and server
            self.shared_key = self.curve.gen_fancy_des_shared_key(self.secret_key, msg)

            self.msg_prefix = 'name: '  # identifier for name

            # Print the prompt to make user type his/her name
            sys.stdout.write("Welcome to pychat.\nPlease tell us your name:\n")

        else:
            # Decrypt all responses first
            msg = FancyDES(key=self.shared_key).decrypt(message=msg, fromFile=False, mode="CBC")
            decoded = msg.decode().rstrip('\0')

            # Abort the client if the server close the connection
            if decoded == pychat_util.QUIT_STRING:
                sys.stdout.write('Bye\n')
                self.server_connection.close()
                os._exit(2)

            self.msg_prefix = ''

            # Print all the message received from the server
            sys.stdout.write(decoded)

        # Flush the output bugger and append a prompt for user input
        print('>', end=' ', flush=True)

    def listen_to_stdin(self):
        """ Start the control loop for listening to stdin and and handling client requests """
        while True:
            # Read the next line of instruction form stdin
            msg = sys.stdin.readline()
            msg = self.msg_prefix + msg

            assert self.shared_key is not None

            # Encrypt the msg buffer, including the first username buffer
            msg_bytes = FancyDES(key=self.shared_key).encrypt(message=msg.encode(), fromFile=False, mode="CBC")

            # Send the encrypted message to the server
            self.server_connection.sendall(msg_bytes)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python client.py [hostname]", file=sys.stderr)
        sys.exit(1)

    else:
        client = PychatClient(sys.argv[1])
        Thread(target=client.listen_to_server).start()
        client.listen_to_stdin()
