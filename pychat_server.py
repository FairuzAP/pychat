# implementing 3-tier structure: Hall --> Room --> Clients; 
# 14-Jun-2013

import select, sys
from pychat_util import Hall, Player
from ECC import ECCipher
from Point import Point
import pychat_util

READ_BUFFER = 4096

host = sys.argv[1] if len(sys.argv) >= 2 else ''
listen_sock = pychat_util.create_socket((host, pychat_util.PORT))

cipher = ECCipher(-1, 188, 7919, Point(224, 503), 20)
secret_key = cipher.gen_fancy_des_secret_key()

hall = Hall(cipher.gen_fancy_des_partial_key(secret_key))
connection_list = []
connection_list.append(listen_sock)

while True:
    # Player.fileno()
    read_players, write_players, error_sockets = select.select(connection_list, [], [])
    for player in read_players:
        if player is listen_sock: # new connection, player is a socket
            new_socket, add = player.accept()
            new_player = Player(new_socket)
            connection_list.append(new_player)
            hall.welcome_new(new_player)

        else: # new message
            msg = player.socket.recv(READ_BUFFER)

            # If the player hasn't sent it's key and username yet,
            if player.shared_key is None:
                partial_key = msg[:msg.decode(errors='replace').rfind("name:")]
                player.shared_key = cipher.gen_fancy_des_shared_key(secret_key, partial_key)
                msg = msg[msg.decode(errors='replace').rfind("name:"):]

            #TODO: Decrypt the msg buffer here first, including the first username buffer

            if msg:
                msg = msg.decode(errors='replace').lower()
                hall.handle_msg(player, msg)
            else:
                player.socket.close()
                connection_list.remove(player)

    for sock in error_sockets: # close error sockets
        sock.close()
        connection_list.remove(sock)
