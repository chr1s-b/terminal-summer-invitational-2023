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
        self.strat_phase = 0

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

        self.utilities.track_destroyed_structures(game_state)
        gamelib.debug_write('Destroyed structures: {}'.format(self.utilities.destroyed_structures))
        self.starter_strategy(game_state)

        game_state.submit_turn()


    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def starter_strategy(self, game_state):
        destroyed_structures = self.utilities.destroyed_structures

        # only try to build the opening if the opening has not been completed yet
        phase_complete = self.defenses.five_turret(game_state)
        gamelib.debug_write(f'Opening phase complete: {phase_complete}')
        if phase_complete == 5:
            self.five_turret_complete = True

        if self.five_turret_complete:
            midgame_phase = self.defenses.build_midgame_defenses(game_state)

        self.attacks.attack(game_state, self.strat_phase)

        # repair walls with remaining credit
        game_state.attempt_spawn(WALL, destroyed_structures[WALL])
