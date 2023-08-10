import gamelib


class Defenses:
    def __init__(self, config):
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
        self.scored_on_locations = []

        self.phase = 0
        return

    def advance_phase(self, game_state):
        """Upgrade defences in the mid-game."""
        # TODO count what phase the build gets to

        # phase 0 corresponds to opening complete
        # phase 1 adds a turret on left
        game_state.attempt_spawn(TURRET, [1, 12])

        # phase 2 upgrades left turret, adds walls
        game_state.attempt_upgrade([1, 12])
        wall_positions = [[2, 12], [4, 12], [5, 12], [22, 12]]
        game_state.attempt_spawn(WALL, wall_positions)

        # phase 3 adds a turret on the right, upgrades turret
        game_state.attempt_spawn(TURRET, [25, 11])
        game_state.attempt_upgrade([25, 11])

        # phase 4 adds a turret on mid right, upgrade turret
        game_state.attempt_spawn(TURRET, [20, 10])
        game_state.attempt_upgrade([20, 10])

        # NOTE this is incorrect until TODO is complete
        return self.phase
