# implementing 3-tier structure: Hall --> Room --> Clients; 
# 14-Jun-2013

import select, sys
from pychat_util import Hall, Player
from ECC import ECCipher
from Point import Point
from fancyDES import FancyDES
from ECCParameter_GUI import ECCParam
import pychat_util


class PychatServer:
    def __init__(self, host):
        """ Initialize the server paramater """

        # Intialize the new connection listening port
        self.READ_BUFFER = 4096
        self.listen_sock = pychat_util.create_socket((host, pychat_util.PORT))

        # Create ECC parameter input window
        # Wait until parameter is entered
        param = ECCParam()
        while not param.param_set : pass

        # Initialize the ECC curve, and generate the secret key
        #self.curve = ECCipher(-1, 188, 7919, Point(224, 503), 20)
        self.curve = ECCipher(param.a_val, param.b_val, param.p_val, Point(param.pt_x, param.pt_y), param.k_val)
        self.secret_key = self.curve.gen_fancy_des_secret_key()

        # Initialize the server's Hall and the connection list
        self.hall = Hall(self.curve.gen_fancy_des_partial_key(self.secret_key))
        self.connection_list = []
        self.connection_list.append(self.listen_sock)

    def start_listen(self):
        """ Start the control loop for listening and handling client requests """

        while True:

            # Wait for input from either the new connection socket or any of the connected players
            read_players, write_players, error_sockets = select.select(self.connection_list, [], [])

            # For every socket in a ready-to-read state,
            for player in read_players:

                # If it is the new connection socket, handle the new connection
                if player is self.listen_sock:
                    self.handle_new_player(player)

                # Else, it is a new message from one of the connected players
                else:
                    try:
                        msg = player.socket.recv(self.READ_BUFFER)
                    except:
                        msg = ""
                    self.handle_player_msg(player, msg)

            # Close error sockets
            for sock in error_sockets:
                sock.close()
                self.connection_list.remove(sock)

    def handle_new_player(self, player):
        """
        Handle the new connection received by registering it as a new player
        :param player: The new-connection socket
        """

        # Accept the new connection and create a wrapper Player object around it
        new_socket, add = player.accept()
        new_player = Player(new_socket)

        # Add the player to the listener list and send a welcome message to the new player
        self.connection_list.append(new_player)
        self.hall.welcome_new(new_player)

    def handle_player_msg(self, player, msg):
        """
        Handle the msg buffer that is received from one of the connected player
        :param player: The sender of the message
        :param msg: The message sent
        """

        if msg:
            # If the player hasn't sent it's key and username yet, the message contains the player's public key
            if player.shared_key is None:

                # Initialize the player-server shared key for this player
                player.shared_key = self.curve.gen_fancy_des_shared_key(self.secret_key, msg)

            # Else, decrypt and handle the message
            else:
                msg = FancyDES(key=player.shared_key).decrypt(message=msg, fromFile=False, mode="CBC")
                msg = msg.decode().rstrip('\0')
                self.hall.handle_msg(player, msg)

        else:
            self.hall.remove_player(player)
            player.socket.close()
            self.connection_list.remove(player)

if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) >= 2 else ''
    server = PychatServer(host)
    server.start_listen();
