from model.player_state import PlayerState

class GameState:
    def __init__(self, player:PlayerState):
        self.player = player

        self.players = {} # player id -> PlayerState

        self.state = 'staging'
