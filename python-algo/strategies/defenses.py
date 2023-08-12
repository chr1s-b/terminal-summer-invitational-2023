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

    def five_turret(self, game_state):
        """Builds opening state with four turrets and five walls."""

        # turn 1
        turret_positions = [[3, 12], [6, 12], [25, 12], [18, 9]]
        wall_positions = [[3, 13], [6, 13], [25, 13], [17, 9], [18, 10]]
        upgrade_turret_positions = [[3, 12], [6, 12], [25, 12]]
        turrets = [(TURRET, t_pos) for t_pos in turret_positions]
        walls = [(WALL, w_pos) for w_pos in wall_positions]
        upgrades = [(UPGRADE, u_pos) for u_pos in upgrade_turret_positions]
        phase_1 = turrets + walls + upgrades
        if not self.build_phase(game_state, phase_1):
            return 0

        if (game_state.turn_number == 0):
            return 1

        # expected turn 2
        phase_2 = [(UPGRADE, [18, 9])]
        if not self.build_phase(game_state, phase_2):
            return 1

        # expected turn 2/3
        # ? do the walls get spawned in list-order priority?
        wall_positions = [[7, 12], [7, 11], [7, 10], [8, 9], [26, 13], [27, 13], [0, 13], [1, 13], [2, 13], [4, 13], [5, 13]]
        phase_3 = [(WALL, w_pos) for w_pos in wall_positions]
        if not self.build_phase(game_state, phase_3):
            return 2

        # expected turn 4
        phase_4 = [(TURRET, [21, 11]), (WALL, [21, 12]), (WALL, [22, 12])]
        if not self.build_phase(game_state, phase_4):
            return 3

        # expected turn 5
        wall_positions = [[20, 11], [19, 10], [22, 14]] + [[x, 8] for x in range(16, 8, -1)]
        phase_5 = [(UPGRADE, [21, 11])] + [(WALL, w_pos) for w_pos in wall_positions]
        if not self.build_phase(game_state, phase_5):
            return 4

        return 5

    def build_midgame_defenses(self, game_state):
        """Upgrade and maintain defences in the mid-game."""
        # currently quits when it fails to complete a phase

        # phase 0 corresponds to opening complete
        # phase 1 adds a turret on left
        if not self.build_phase(game_state, [(TURRET, [1, 12])]):
            return 0

        # phase 2 upgrades left turret, adds walls
        wall_positions = [[2, 12], [4, 12], [5, 12], [22, 12]]
        if not self.build_phase(game_state, [(UPGRADE, [1, 12])] + [(WALL, pos) for pos in wall_positions]):
            return 1

        # phase 3 adds a turret on the right, upgrades turret
        if not self.build_phase(game_state, [(TURRET, [25, 11]), (UPGRADE, [25, 11])]):
            return 2

        # phase 4 adds a turret on mid right, upgrade turret
        if not self.build_phase(game_state, [(TURRET, [20, 10]), (UPGRADE, [20, 10])]):
            return 3

        return 4

    def build_phase(self, game_state, phase):
        """Build phase and return whether complete."""
        complete = True
        for structure, location in phase:
            if structure == UPGRADE:
                game_state.attempt_upgrade(location)
                unit = game_state.contains_stationary_unit(location)
                if not unit or not unit.upgrade:
                    gamelib.debug_write(f'Could not upgrade {unit} at {location}.')
                    complete = False
            else:
                game_state.attempt_spawn(structure, location)
                unit = game_state.contains_stationary_unit(location)
                if not unit:
                    gamelib.debug_write(f'Could not spawn {unit} at {location}.')
                    complete = False
        gamelib.debug_write(f'build_phase returns complete={complete}')
        return complete
