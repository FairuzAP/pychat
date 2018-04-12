# implementing 3-tier structure: Hall --> Room --> Clients; 
# 14-Jun-2013

import select, sys
from pychat_util import Hall, Player
from ECC import ECCipher
from Point import Point
from fancyDES import FancyDES
import pychat_util


class PychatServer:
    def __init__(self, host):
        self.READ_BUFFER = 4096
        self.listen_sock = pychat_util.create_socket((host, pychat_util.PORT))

        self.curve = ECCipher(-1, 188, 7919, Point(224, 503), 20)
        self.secret_key = self.curve.gen_fancy_des_secret_key()

        self.hall = Hall(self.curve.gen_fancy_des_partial_key(self.secret_key))
        self.connection_list = []
        self.connection_list.append(self.listen_sock)

    def start_listen(self):
        while True:
            read_players, write_players, error_sockets = select.select(self.connection_list, [], [])
            for player in read_players:
                if player is self.listen_sock:  # new connection, player is a socket
                    self.handle_new_player(player)

                else:  # new message
                    msg = player.socket.recv(self.READ_BUFFER)
                    self.handle_player_msg(player, msg)

            for sock in error_sockets:  # close error sockets
                sock.close()
                self.connection_list.remove(sock)

    def handle_new_player(self, player):
        new_socket, add = player.accept()
        new_player = Player(new_socket)
        self.connection_list.append(new_player)
        self.hall.welcome_new(new_player)

    def handle_player_msg(self, player, msg):
        if player.shared_key is None: # If the player hasn't sent it's key and username yet,
            partial_key = msg[:msg.decode(errors='replace').rfind("name:")]
            player.shared_key = self.curve.gen_fancy_des_shared_key(self.secret_key, partial_key)
            player.cipher = FancyDES(key=player.shared_key)
            msg = msg[msg.decode(errors='replace').rfind("name:"):]
        else:
            msg = player.cipher.decrypt(message=msg, fromFile=False, mode="CBC")

        if msg:
            # Decrypt the msg buffer here first, including the first username buffer
            msg = msg.decode().lower()
            self.hall.handle_msg(player, msg)
        else:
            player.socket.close()
            self.connection_list.remove(player)


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) >= 2 else ''
    server = PychatServer(host)
    server.start_listen();
