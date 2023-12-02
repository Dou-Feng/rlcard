import unittest
import numpy as np

from rlcard.games.limitholdem.game import LimitHoldemGame as Game
from rlcard.games.limitholdem.player import LimitHoldemPlayer as Player
from rlcard.games.limitholdem.utils import Action_Enum

class TestLimitHoldemMethods(unittest.TestCase):

    def test_get_num_players(self):
        game = Game()
        num_players = game.get_num_players()
        self.assertEqual(num_players, 2)

    def test_get_num_actions(self):
        game = Game()
        num_actions = game.get_num_actions()
        self.assertEqual(num_actions, 5)

    def test_init_game(self):
        game = Game()
        state, player_id = game.init_game()
        test_id = game.get_player_id()
        self.assertEqual(test_id, player_id)
        self.assertIn(Action_Enum.to_enum('call'), state['legal_actions'])
        self.assertIn(Action_Enum.to_enum('raise'), state['legal_actions'])
        self.assertIn(Action_Enum.to_enum('fold'), state['legal_actions'])

    def test_step(self):
        game = Game()

        # test raise
        game.init_game()
        init_raised = game.round.have_raised
        init_point = game.game_pointer
        game.step(('raise', 10))
        step_raised = game.round.have_raised
        self.assertEqual(init_raised+1, step_raised)
        next_point = (init_point + 1) % 2
        self.assertEqual(game.game_pointer, next_point)
        self.assertEqual(game.players[init_point].in_chips, 12)
        self.assertEqual(game.players[next_point].in_chips, 2)
        self.assertEqual(game.players[init_point].rest_chips, 28)
        self.assertEqual(game.players[next_point].rest_chips, 38)
        self.assertEqual(game.max_player_raise_amount(), 28)
        game.step(('call', 0))
        self.assertEqual(game.players[next_point].in_chips, 12)
        self.assertEqual(game.players[next_point].rest_chips, 28)

        # test call
        game.init_game()
        init_not_raise_num = game.round.not_raise_num
        game.step('call')
        step_not_raise_num = game.round.not_raise_num
        self.assertEqual(init_not_raise_num+1, step_not_raise_num)

        # test fold
        game.init_game()
        game.step('fold')
        self.assertTrue(game.round.player_folded)

        # test check
        game.init_game()
        game.step('call')
        game.step('check')
        self.assertEqual(game.round_counter, 1)

        # test play 4 rounds
        game.init_game()
        for i in range(19):
            if (i+1) % 5 == 0:
                game.step('call')
            else:
                game.step(('raise', 1))
            self.assertEqual(game.is_over(), False)
        game.step('call')
        self.assertEqual(game.is_over(), True)

        # Test illegal actions
        game.init_game()
        with self.assertRaises(Exception):
            game.step('check')

        # Test the upper limit of raise
        game.init_game()
        for _ in range(4):
            game.step(('raise', 1))

        legal_actions = game.get_legal_actions()
        self.assertNotIn('raise', legal_actions)

    def test_step_back(self):
        game = Game(allow_step_back=True)
        game.init_game()
        self.assertEqual(game.step_back(), False)
        index = 0
        previous = None
        while not game.is_over():
            index += 1
            legal_actions = game.get_legal_actions()
            if index == 2:
                result = game.step_back()
                now = game.get_player_id()
                if result:
                    self.assertEqual(previous, now)
                else:
                    self.assertEqual(len(game.history), 0)
                break
            previous = game.get_player_id()
            action = np.random.choice(list(legal_actions)) if len(legal_actions) else (0, 0)
            action = (action, min(np.random.randint(1, 10) , game.max_player_raise_amount()))
            game.step(action)

    def test_payoffs(self):
        game = Game()
        np.random.seed(0)
        for _ in range(5):
            game.init_game()
            while not game.is_over():
                legal_actions = game.get_legal_actions()
                action = np.random.choice(list(legal_actions)) if len(legal_actions) else 0
                amount = min(np.random.randint(1, 10) , game.max_player_raise_amount())
                action = (action, amount)
                game.step(action)
            payoffs = game.get_payoffs()
            total = 0
            for payoff in payoffs:
                total += payoff
            self.assertEqual(total, 0)

    def test_get_player_id(self):
        player = Player(3, np.random.RandomState())
        self.assertEqual(player.get_player_id(), 3)


if __name__ == '__main__':
    unittest.main()
