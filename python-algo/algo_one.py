import gamelib
import random
import math # noqa F401
import warnings # noqa F401
from sys import maxsize
import json
import strategies


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""


class AlgoStrategyOne(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0
        # This is a good place to do initial setup
        self.defenses = strategies.Defenses(config)
        self.attacks = strategies.Attacks(config)
        self.openings = strategies.Openings(config)
        self.utilities = strategies.Utilities(config)

        self.five_turret_complete = False

        self.scored_on_locations = []

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        self.utilities.track_enemy_spending(game_state)
        self.utilities.track_destroyed_walls(game_state)
        self.starter_strategy(game_state)

        game_state.submit_turn()


    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def starter_strategy(self, game_state):
        enemy_sp, enemy_mp = self.utilities.enemy_balance
        destroyed_walls = self.utilities.destroyed_walls

        # only try to build the opening if the opening has not been completed yet
        if not self.five_turret_complete:
            self.five_turret_complete = self.openings.five_turret(game_state)
            # TODO send mobile units
            return

        # maintain opening

        # middle/late game
        # TODO implement

        # defence
        # try to move to the next phase according to doc
        self.defenses.advance_phase(game_state)

        # not sure about the below
        priority_walls = destroyed_walls + []
        upgradeable_turrets = []
        new_turrets = []
        new_walls = []

        game_state.attempt_spawn(priority_walls)
        game_state.attempt_upgrade(upgradeable_turrets)
        game_state.attempt_spawn(new_turrets)
        game_state.attempt_upgrade(new_turrets)
        game_state.attempt_spawn(new_walls)
