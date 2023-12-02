import numpy as np


class MockAgent(object):

    def __init__(self, num_actions):
        ''' Initilize the random agent

        Args:
            num_actions (int): The size of the ouput action space
        '''
        self.use_raw = False
        self.num_actions = num_actions
        self.action_list = []
        self.index = 0

    def append_action(self, actions):
        if isinstance(actions, list):
            self.action_list.extend(actions)
        else: self.action_list.append(actions)

    @staticmethod
    def step(state, rest_chips=1000):
        return None

    def eval_step(self, state, rest_chips=1000):
        assert(self.index < len(self.action_list))
        action = self.action_list[self.index]
        self.index += 1
        return action, None
