from rlcard.utils.utils import print_card
from rlcard.games.limitholdem.utils import Action_Enum
from rlcard.games.limitholdem.player import PlayerStatus
class HumanAgent(object):
    ''' A human agent for Limit Holdem. It can be used to play against trained models
    '''

    def __init__(self, num_actions):
        ''' Initilize the human agent

        Args:
            num_actions (int): the size of the ouput action space
        '''
        self.use_raw = True
        self.num_actions = num_actions

    @staticmethod
    def step(state, rest_chips=1000):
        ''' Human agent will display the state and make decisions through interfaces

        Args:
            state (dict): A dictionary that represents the current state

        Returns:
            action (int): The action decided by human
        '''
        _print_state(state['raw_obs'], state['action_record'], state['raw_legal_actions'])
        if state['raw_obs']['status'] == PlayerStatus.ALLIN:
            print("Player {} is all in.".format(state['raw_obs']['player_id']))
            return Action_Enum.All_in, 0
        elif state['raw_obs']['status'] == PlayerStatus.FOLDED:
            print("Player is folded.")
            return Action_Enum.Fold, 0
        
        # Player.status == PlayerStatus.ALIVE
        action = int(input('>> You choose action (integer): '))
        while action < 0 or action >= len(state['legal_actions']):
            print('Action illegal...')
            action = int(input('>> Re-choose action (integer): '))
        action = state['raw_legal_actions'][action]
        print("User choose action: {}".format(action))
        amount = 0
        if action == Action_Enum.Raise:
            while True:
                try:
                    amount = int(input("Current action is {}. Please input amount:".format(action.name)))
                    if amount > rest_chips:
                        print("The raise amount is invalid.")
                    else: break
                except ValueError:
                    continue
        return action, amount

    def eval_step(self, state, rest_chips=1000):
        ''' Predict the action given the curent state for evaluation. The same to step here.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted (randomly chosen) by the random agent
        '''
        return self.step(state, rest_chips), {}

def _print_state(state, action_record, raw_legal_actions):
    ''' Print out the state

    Args:
        state (dict): A dictionary of the raw state
        action_record (list): A list of the each player's historical actions
    '''
    _action_list = []
    for i in range(1, len(action_record)+1):
        _action_list.insert(0, action_record[-i])
    for pair in _action_list:
        print('>> Player', pair[0], 'chooses', pair[1])

    print('\n=============== Community Card ===============')
    print_card(state['public_cards'])
    print('===============   Your Hand    ===============')
    print_card(state['hand'])
    print('===============     Chips      ===============')
    print('My In chips:   ', end='')
    for _ in range(state['my_chips']):
        print('+', end='')
    print('')
    print("My Rest chips:   {}".format(state['rest_chips']))
    print("All chips:")
    chip_sum = 0
    for i in range(len(state['all_chips'])):
        print("player {}:  ".format(i), end='')
        for _ in range(state['all_chips'][i][0]):
            print('+', end='')
        print(" (in: {}, rest: {})".format(state['all_chips'][i][0], state['all_chips'][i][1]))
        chip_sum += state['all_chips'][i][0]
    print("sum chips: {}".format(chip_sum))
    if len(raw_legal_actions):
        print('\n=========== Actions You Can Choose ===========')
        print(', '.join([str(index) + ': ' + action.name for index, action in enumerate(raw_legal_actions)]))
        print('')
