from enum import Enum


class PlayerStatus(Enum):
    ALIVE = 0
    FOLDED = 1
    ALLIN = 2


class LimitHoldemPlayer:

    def __init__(self, player_id, np_random):
        """
        Initialize a player.

        Args:
            player_id (int): The id of the player
        """
        self.np_random = np_random
        self.player_id = player_id
        self.hand = []
        self.status = PlayerStatus.ALIVE

        # The chips that this player has put in until now
        self.in_chips = 0
        # The rest of chips that this player possesses currently.
        self.rest_chips = 40

    def get_state(self, public_cards, all_chips, legal_actions):
        """
        Encode the state for the player

        Args:
            public_cards (list): A list of public cards that seen by all the players
            all_chips ((int ,int)): The chips that all players have put in, and all player rest.

        Returns:
            (dict): The state of the player
        """
        return {
            'player_id': self.player_id,
            'status': self.status,
            'hand': [c.get_index() for c in self.hand],
            'public_cards': [c.get_index() for c in public_cards],
            'all_chips': all_chips,
            'my_chips': self.in_chips,
            "rest_chips": self.rest_chips,
            'legal_actions': legal_actions
        }

    def raise_in(self, amount : int):
        self.in_chips += amount
        self.rest_chips -= amount
        assert(self.rest_chips >= 0)

    def get_player_id(self):
        return self.player_id
