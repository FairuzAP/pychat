# implementing 3-tier structure: Hall --> Room --> Clients; 
# 14-Jun-2013

import socket, pdb

from fancyDES import FancyDES

MAX_CLIENTS = 30
PORT = 22222
QUIT_STRING = '<$quit$>'


def create_socket(address):
    """
    Helper method to create a socket to the given address
    :param address: The address to connect to or listen from
    :return: A non-blocking, listening socket bind to the given address
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(0)
    s.bind(address)
    s.listen(MAX_CLIENTS)
    print("Now listening at ", address)
    return s

class Hall:
    def __init__(self, partial_key):
        self.ptb = partial_key
        self.rooms = {} # {room_name: Room}
        self.room_player_map = {} # {playerName: roomName}

    def welcome_new(self, new_player):
        """ Send the server's public key to a new player """
        new_player.socket.sendall(self.ptb)

    def list_rooms(self, player):
        """ Send an encrypted room list to the player """
        if len(self.rooms) == 0:
            msg = 'Oops, no active rooms currently. Create your own!\n' \
                + 'Use [<join> room_name] to create a room.\n'
            player.encrypt_send(msg.encode())
        else:
            msg = 'Listing current rooms...\n'
            for room in self.rooms:
                msg += room + ": " + str(len(self.rooms[room].players)) + " player(s)\n"
            player.encrypt_send(msg.encode())
    
    def handle_msg(self, player, msg):
        """ Handle the message received from the given player """
        
        instructions = b'Instructions:\n'\
            + b'[<list>] to list all rooms\n'\
            + b'[<join> room_name] to join/create/switch to a room\n' \
            + b'[<manual>] to show instructions\n' \
            + b'[<quit>] to quit\n' \
            + b'Otherwise start typing and enjoy!' \
            + b'\n'

        print(player.name + " says: " + msg)

        # If contains the tag 'name:', register the player name
        if "name:" in msg.lower():
            name = msg.split()[1]
            player.name = name
            print("New connection from:", player.name)
            player.encrypt_send(instructions)

        # If contains the tag '<join>', change the player's room
        elif "<join>" in msg.lower():
            same_room = False
            if len(msg.split()) >= 2: # error check

                room_name = msg.split()[1]
                if player.name in self.room_player_map: # switching?
                    if self.room_player_map[player.name] == room_name:
                        player.encrypt_send(b'You are already in room: ' + room_name.encode())
                        same_room = True
                    else: # switch
                        old_room = self.room_player_map[player.name]
                        self.rooms[old_room].remove_player(player)

                if not same_room:
                    if not room_name in self.rooms: # new room:
                        new_room = Room(room_name)
                        self.rooms[room_name] = new_room
                    self.rooms[room_name].players.append(player)
                    self.rooms[room_name].welcome_new(player)
                    self.room_player_map[player.name] = room_name
            else:
                player.encrypt_send(instructions)

        # If contains the tag '<list>', send the active rooms list
        elif "<list>" in msg.lower():
            self.list_rooms(player)

        # If contains the tag '<manual>', send the instructions manual
        elif "<manual>" in msg.lower():
            player.encrypt_send(instructions)

        # If contains the tag '<quit>', terminate the connection
        elif "<quit>" in msg.lower():
            player.encrypt_send(QUIT_STRING.encode())
            self.remove_player(player)

        # Else, try to broadcast the message to the player's room
        else:
            # check if in a room or not first
            if player.name in self.room_player_map:
                self.rooms[self.room_player_map[player.name]].broadcast(player, msg.encode())
            else:
                msg = 'You are currently not in any room! \n' \
                    + 'Use [<list>] to see available rooms! \n' \
                    + 'Use [<join> room_name] to join a room! \n'
                player.encrypt_send(msg.encode())
    
    def remove_player(self, player):
        if player.name in self.room_player_map:
            self.rooms[self.room_player_map[player.name]].remove_player(player)
            del self.room_player_map[player.name]
        print("Player: " + player.name + " has left\n")

    
class Room:
    def __init__(self, name):
        self.players = [] # a list of sockets
        self.name = name

    def welcome_new(self, from_player):
        msg = self.name + " welcomes: " + from_player.name + '\n'
        for player in self.players:
            player.encrypt_send(msg.encode())
    
    def broadcast(self, from_player, msg):
        msg = from_player.name.encode() + b": " + msg
        for player in self.players:
            player.encrypt_send(msg)

    def remove_player(self, player):
        self.players.remove(player)
        leave_msg = player.name.encode() + b" has left the room\n"
        self.broadcast(player, leave_msg)


class Player:
    def __init__(self, socket, name = "new"):
        socket.setblocking(0)
        self.socket = socket
        self.name = name
        self.shared_key = None

    def fileno(self):
        return self.socket.fileno()

    def encrypt_send(self, msg):
        """ Encrypt all the message to a player using the shared key """
        encoded = FancyDES(key=self.shared_key).encrypt(message=msg, fromFile=False, mode="CBC")
        self.socket.sendall(encoded)
