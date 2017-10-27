import numpy as np
from gym import spaces
from pysc2.lib import actions, features

# noinspection PyUnresolvedReferences
import sc2gym.envs
from sc2gym.envs import SC2GameEnv

__author__ = 'Islam Elnabarawy'

_MAP_NAME = 'MoveToBeacon'

_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_PLAYER_RELATIVE_SCALE = features.SCREEN_FEATURES.player_relative.scale

_NO_OP = actions.FUNCTIONS.no_op.id

_SELECT_ARMY = actions.FUNCTIONS.select_army.id
_SELECT_ALL = [0]

_MOVE_SCREEN = actions.FUNCTIONS.Move_screen.id
_NOT_QUEUED = [0]


class MoveToBeaconEnv(SC2GameEnv):
    def __init__(self, visualize=False):
        super().__init__(map_name=_MAP_NAME, visualize=visualize)
        self._action_space = None
        self._observation_space = None

    def _reset(self):
        super()._reset()
        obs, reward, done, info = super()._step([_SELECT_ARMY, _SELECT_ALL])
        obs = self._extract_observation(obs)
        return obs

    def _step(self, action):
        action = self._translate_action(action)
        obs, reward, done, info = super()._step(action)
        if obs is None:
            return None, 0, True, {}
        obs = self._extract_observation(obs)
        return obs, reward, done, info

    @property
    def observation_space(self):
        if self._observation_space is None:
            screen_shape = self.observation_spec["screen"][1:] + (1, )
            self._observation_space = spaces.Box(low=0, high=_PLAYER_RELATIVE_SCALE, shape=screen_shape)
        return self._observation_space

    @property
    def action_space(self):
        if self._action_space is None:
            screen_shape = self.observation_spec["screen"][1:]
            self._action_space = spaces.Discrete(screen_shape[0]*screen_shape[1])
        return self._action_space

    @staticmethod
    def _extract_observation(obs):
        obs = obs.observation["screen"][_PLAYER_RELATIVE]
        obs = obs.reshape(obs.shape + (1, ))
        return obs

    def _translate_action(self, action):
        if action == 0:
            return [_NO_OP]
        screen_shape = self.observation_spec["screen"][1:]
        target = list(np.unravel_index(action, screen_shape)[::-1])
        return [_MOVE_SCREEN, _NOT_QUEUED, target]
