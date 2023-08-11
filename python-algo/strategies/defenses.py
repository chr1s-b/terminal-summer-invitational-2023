import gamelib


class Defenses:
    def __init__(self, config):
        self.config = config
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP, UPGRADE
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        UPGRADE = config["unitInformation"][7]["shorthand"]
        MP = 1
        SP = 0
        self.scored_on_locations = []

        self.phase = 0
        return

    def build_midgame_defenses(self, game_state):
        """Upgrade and maintain defences in the mid-game."""
        # currently quits when it fails to complete a phase

        # phase 0 corresponds to opening complete
        self.phase = 0

        # phase 1 adds a turret on left
        if not self.build_phase(game_state, [(TURRET, [1, 12])]):
            return
        self.phase = 1

        # phase 2 upgrades left turret, adds walls
        wall_positions = [[2, 12], [4, 12], [5, 12], [22, 12]]
        if not self.build_phase(game_state, [(UPGRADE, [1, 12])] + [(WALL, pos) for pos in wall_positions]):
            return
        self.phase = 2

        # phase 3 adds a turret on the right, upgrades turret
        if not self.build_phase(game_state, [(TURRET, [25, 11]), (UPGRADE, [25, 11])]):
            return
        self.phase = 3

        # phase 4 adds a turret on mid right, upgrade turret
        if not self.build_phase(game_state, [(TURRET, [20, 10]), (UPGRADE, [20, 10])]):
            return
        self.phase = 4

        return self.phase

    def build_phase(self, game_state, phase):
        """Build phase and return whether complete."""
        complete = True
        for structure, location in phase:
            if structure == UPGRADE:
                game_state.attempt_upgrade(location)
                if UPGRADE not in game_state.game_map[location]:
                    complete = False
            else:
                game_state.attempt_spawn(structure, location)
                if structure not in game_state.game_map[location]:
                    complete = False
        return complete
