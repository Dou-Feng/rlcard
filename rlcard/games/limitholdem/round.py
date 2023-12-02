# -*- coding: utf-8 -*-
"""Limit texas holdem round class implementation"""
from collections import OrderedDict
from rlcard.games.limitholdem.utils import Action_Enum
from rlcard.games.limitholdem.player import PlayerStatus
import numpy as np
class LimitHoldemRound:
    """Round can call other Classes' functions to keep the game running"""

    def __init__(self, raise_amount, allowed_raise_num, num_players, np_random):
        """
        Initialize the round class

        Args:
            raise_amount (int): the raise amount for each raise
            allowed_raise_num (int): The number of allowed raise num
            num_players (int): The number of players
        """
        self.np_random = np_random
        self.game_pointer = None
        self.raise_amount = raise_amount
        self.allowed_raise_num = allowed_raise_num

        self.players = None
        self.num_players = num_players

        # Count the number of raise
        self.have_raised = 0

        # Count the number without raise
        # If every player agree to not raise, the round is over
        self.not_raise_num = 0

        # Raised amount for each player
        self.raised = [0 for _ in range(self.num_players)]
        self.player_folded = None
        self.folded_num = 0

    def start_new_round(self, players, game_pointer, raised=None):
        """
        Start a new bidding round

        Args:
            game_pointer (int): The game_pointer that indicates the next player
            raised (list): Initialize the chips for each player

        Note: For the first round of the game, we need to setup the big/small blind
        """
        self.game_pointer = game_pointer
        self.have_raised = 0
        self.not_raise_num = 0
        self.folded_num = 0
        self.players = players
        if raised:
            self.raised = raised
        else:
            self.raised = [self.players[i].in_chips for i in range(self.num_players)]

    def proceed_round(self, players, action_pack):
        """
        Call other classes functions to keep one round running

        Args:
            players (list): The list of players that play the game
            action (str): An legal action taken by the player

        Returns:
            (int): The game_pointer that indicates the next player
        """
        if not isinstance(action_pack, tuple):
            if isinstance(action_pack, str):
                action_pack = Action_Enum.to_enum(action_pack)
            elif isinstance(action_pack, int) or isinstance(action_pack, np.int64):
                action_pack = Action_Enum(action_pack)
            if action_pack == Action_Enum.Raise:
                raise Exception("Raise action lacks amount field")
            action, amount = action_pack, 0
        else:
            action, amount = action_pack
            if isinstance(action, str): 
                action = Action_Enum.to_enum(action)
            elif isinstance(action, int) or isinstance(action, np.int64):
                action = Action_Enum(action)
        cur_player = players[self.game_pointer]

        print("Player {}, action {}, amount {}\nCurrent Status: ".format(self.game_pointer, action.name, amount), end='')
    
        for i in range(self.num_players):
            print("{}: ({}, {}) ".format(i, players[i].in_chips, self.player_rest_chips(players, i)), end='')
        print("")

        # all in can't take any action
        assert(cur_player.status != PlayerStatus.FOLDED)
        if cur_player.status == PlayerStatus.ALLIN:
            if max(self.raised) != cur_player.in_chips:
                self.not_raise_num += 1
        else: # cur_player.status == ALIVE
            if action not in self.get_legal_actions(players):
                raise Exception('{} is not legal action. Legal actions: {}'.format(action, self.get_legal_actions(players)))

            if action == Action_Enum.Call:
                diff = max(self.raised) - self.raised[self.game_pointer]
                self.raised[self.game_pointer] = max(self.raised)
                cur_player.raise_in(diff)
                self.not_raise_num += 1

            elif action == Action_Enum.Raise:
                assert(amount > 0)
                diff = max(self.raised) - self.raised[self.game_pointer] + amount
                self.raised[self.game_pointer] = max(self.raised) + amount
                cur_player.raise_in(diff)
                self.have_raised += 1
                self.not_raise_num = 1

            elif action == Action_Enum.Fold:
                self.player_folded = True
                cur_player.status = PlayerStatus.FOLDED
                self.folded_num += 1

            elif action == Action_Enum.Check:
                self.not_raise_num += 1

            elif action == Action_Enum.All_in:
                org_raise_amount = max(self.raised)
                cur_raise_amount = cur_player.in_chips + cur_player.rest_chips
                if org_raise_amount < cur_raise_amount: # equal raise
                    self.have_raised += 1
                    self.not_raise_num = 1
                else: # equal call
                    self.not_raise_num += 1
                self.raised[self.game_pointer] = cur_raise_amount
                cur_player.raise_in(cur_player.rest_chips)
                cur_player.status = PlayerStatus.ALLIN
            
            else:
                raise Exception('LimitHoldem::round: Invalid operation.')

        self.game_pointer = (self.game_pointer + 1) % self.num_players

        # Skip the folded players
        round_around = self.game_pointer
        while players[self.game_pointer].status == PlayerStatus.FOLDED:
            self.game_pointer = (self.game_pointer + 1) % self.num_players
            if self.game_pointer == round_around: break

        return self.game_pointer

    def get_legal_actions(self, players):
        """
        Obtain the legal actions for the current player

        Returns:
           (OrderedDict):  A list of legal actions
        """
        full_action_packs = {k:0 for k in Action_Enum}

        # If the the number of raises already reaches the maximum number raises, we can not raise any more
        if self.have_raised >= self.allowed_raise_num or self.max_player_raise_amount(players) <= 0:
            full_action_packs.pop(Action_Enum.Raise)

        # If the current chips are less than that of the highest one in the round, we can not check
        if self.raised[self.game_pointer] < max(self.raised):
            full_action_packs.pop(Action_Enum.Check)

        # If the current player has put in the chips that are more than others, we can not call
        if self.raised[self.game_pointer] == max(self.raised) \
            or players[self.game_pointer].rest_chips + players[self.game_pointer].in_chips < max(self.raised):
            full_action_packs.pop(Action_Enum.Call)

        # we can always all in
        if players[self.game_pointer].rest_chips == 0:
            if Action_Enum.Raise in full_action_packs:
                full_action_packs.pop(Action_Enum.Raise)
            full_action_packs.pop(Action_Enum.All_in)
        
        # Raise amount upper bound
        if Action_Enum.Raise in full_action_packs:
            # TODO: improve this feature. I don't think the RL may figure out what this magic integer means.
            full_action_packs[Action_Enum.Raise] = players[self.game_pointer].rest_chips
        
        if players[self.game_pointer].status == PlayerStatus.ALLIN:
            full_action_packs.clear()
        return OrderedDict(full_action_packs)

    def is_over(self):
        """
        Check whether the round is over

        Returns:
            (boolean): True if the current round is over
        """
        if self.not_raise_num >= self.num_players - self.folded_num:
            return True
        return False

    def round_max_raise_amount(self) -> int:
        return max(self.raised)
    
    def player_rest_chips(self, players, id = None):
        if id == None:
            id = self.game_pointer
        return players[id].rest_chips
    
    def max_player_raise_amount(self, players, id = None) -> int:
        if id == None:
            id = self.game_pointer
        return self.player_rest_chips(players, id) - (self.round_max_raise_amount() - players[id].in_chips)