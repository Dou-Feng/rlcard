import json
import os
import numpy as np
from collections import OrderedDict

import rlcard
from rlcard.envs import Env
from rlcard.games.limitholdem import Game
from rlcard.games.limitholdem.utils import Action_Enum

DEFAULT_GAME_CONFIG = {
        'game_num_players': 2,
        }

CARD_NUM = 52
ROUND_NUM = 4
class LimitholdemEnv(Env):
    ''' Limitholdem Environment
    '''

    def __init__(self, config):
        ''' Initialize the Limitholdem environment
        '''
        self.name = 'limit-holdem'
        self.default_game_config = DEFAULT_GAME_CONFIG
        self.game = Game()
        super().__init__(config)
        self.state_shape = [[72] for _ in range(self.num_players)]
        self.action_shape = [None for _ in range(self.num_players)]

        with open(os.path.join(rlcard.__path__[0], 'games/limitholdem/card2index.json'), 'r') as file:
            self.card2index = json.load(file)

    def _get_legal_actions(self):
        ''' Get all leagal actions

        Returns:
            encoded_action_list (list): return encoded legal action list (from str to int)
        '''
        return self.game.get_legal_actions()

    def _extract_state(self, state):
        ''' Extract the state representation from state dictionary for agent

        Note: Currently the use the hand cards and the public cards. TODO: encode the states

        Args:
            state (dict): Original state from the game

        Returns:
            observation (list): combine the player's score and dealer's observable score for observation
        '''
        extracted_state = {}

        extracted_state['legal_actions'] = OrderedDict({a.value:amount for a, amount in state['legal_actions'].items()})

        public_cards = state['public_cards']
        hand = state['hand']
        raise_nums = state['raise_nums']
        cards = public_cards + hand
        idx = [self.card2index[card] for card in cards]
        
        # we should add more space here for the generic in case the number of players increase.
        obs = np.zeros(CARD_NUM + ROUND_NUM * (self.num_players+1))
        obs[idx] = 1
        for i, num in enumerate(raise_nums):
            obs[52 + i * (self.num_players+1) + num] = 1
        extracted_state['obs'] = obs
        extracted_state['raise_amount'] = state['raise_amount']
        extracted_state['raw_obs'] = state
        extracted_state['raw_legal_actions'] = [a for a in state['legal_actions']]
        extracted_state['action_record'] = self.action_recorder
        extracted_state['avail_raise_amount'] = [self.game.max_player_raise_amount(i) for i in range(self.num_players)]
        return extracted_state

    def get_payoffs(self):
        ''' Get the payoff of a game

        Returns:
           payoffs (list): list of payoffs
        '''
        return self.game.get_payoffs()

    def _decode_action(self, action_pack, race=True):
        ''' Decode the action for applying to the game

        Args:
            action pack ([str, int]): action id, and amount

        Returns:
            action ((str, int)): action for the game, and amount
        '''
        if not isinstance(action_pack, tuple):
            action_id = action_pack
            amount = 0
        else:
            action_id, amount = action_pack
        legal_actions = self.game.get_legal_actions()
        if  not Action_Enum(action_id) in legal_actions:
            if Action_Enum.Check in legal_actions:
                return Action_Enum.Check
            else:
                return Action_Enum.All_in if race else Action_Enum.Fold
        
        # only raise operation needs this field
        amount = max(amount, 1)
        amount = min(amount, self.game.max_player_raise_amount())

        return Action_Enum(action_id), amount

    def get_perfect_information(self):
        ''' Get the perfect information of the current state

        Returns:
            (dict): A dictionary of all the perfect information of the current state
        '''
        state = {}
        state['chips'] = [self.game.players[i].in_chips for i in range(self.num_players)]
        state['public_card'] = [c.get_index() for c in self.game.public_cards] if self.game.public_cards else None
        state['hand_cards'] = [[c.get_index() for c in self.game.players[i].hand] for i in range(self.num_players)]
        state['current_player'] = self.game.game_pointer
        state['legal_actions'] = self.game.get_legal_actions()
        return state
