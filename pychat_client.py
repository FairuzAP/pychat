import socket, sys, os
from threading import Thread
from ECC import ECCipher
from Point import Point
from fancyDES import FancyDES
from serverInput_GUI import ServerInput
from ECCParameter_GUI import ECCParam
from pychat_GUI import ChatGUI
import pychat_util


class PychatClient:
    def __init__(self):
        """
        Initialize the client paramater
        :param host: IP addres and port of the server
        """

        # Ask for server address
        # Wait until address is entered
        server = ServerInput()
        while not server.server_set: pass

        # Intialize connection to the chat server
        self.READ_BUFFER = 4096
        self.server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_connection.connect((server.address, pychat_util.PORT))
        print("Connected to server\n")

        # Create ECC parameter input window
        # Wait until parameter is entered
        param = ECCParam()
        while not param.param_set: pass

        # Initialize the ECC curve, and generate the secret key
        #self.curve = ECCipher(-1, 188, 7919, Point(224, 503), 20)
        self.curve = ECCipher(param.a_val, param.b_val, param.p_val, Point(param.pt_x, param.pt_y), param.k_val)
        self.secret_key = self.curve.gen_fancy_des_secret_key()
        self.shared_key = None
        self.msg = ""
        self.msg_prefix = ''

        # Create and show chat window
        self.gui = ChatGUI(self)

    def listen_to_server(self):
        """ Start the control loop for listening and handling server responses """
        while True:
            msg = self.server_connection.recv(self.READ_BUFFER)
            if not msg:
                while not self.add_entry("Server down!"):
                    pass
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
            while not self.add_entry("Welcome to pychat.\nPlease tell us your name:\n"):
                print("wait")

        else:
            # Decrypt all responses first
            msg = FancyDES(key=self.shared_key).decrypt(message=msg, fromFile=False, mode="CBC")
            decoded = msg.decode().rstrip('\0')

            # Abort the client if the server close the connection
            if decoded == pychat_util.QUIT_STRING:
                while not self.add_entry("Bye\n"):
                    pass
                self.server_connection.close()
                os._exit(2)

            self.msg_prefix = ''

            # Print all the message received from the server
            while not self.add_entry(decoded):
                pass

    # Send message to server, called by pychat_GUI class
    def send_message(self, msg):
        msg = self.msg_prefix + msg

        assert self.shared_key is not None

        # Encrypt the msg buffer, including the first username buffer
        msg_bytes = FancyDES(key=self.shared_key).encrypt(message=msg.encode(), fromFile=False, mode="CBC")

        # Send the encrypted message to the server
        self.server_connection.sendall(msg_bytes)

    # Add message from server to variable; only add if there is no other message waiting to be put to queue
    def add_entry(self, input):
        if self.msg != "":
            return False
        else:
            self.msg = input
            return True

    # Add message to queue for GUI
    def add_to_queue(self, thread_queue=None):
        while True:
            while self.msg == "":
                pass
            thread_queue.put(self.msg)
            self.msg = ""

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python client.py [hostname]", file=sys.stderr)
        sys.exit(1)

    else:
        client = PychatClient()
        Thread(target=client.listen_to_server).start()
        client.gui.start_GUI()
        #client.listen_to_stdin()
