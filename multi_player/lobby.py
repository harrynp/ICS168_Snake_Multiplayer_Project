__author__ = 'Harry'

game_lobby = []

def update(room_state, game_lobby):
    while True:
        for client in lobby:
            client.push(room_state)