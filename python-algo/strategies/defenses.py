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
        opening_phase = 0

        # turn 1
        turret_positions = [[3, 12], [6, 12], [25, 12], [18, 9]]
        wall_positions = [[3, 13], [6, 13], [25, 13], [17, 9], [18, 10]]
        upgrade_turret_positions = [[3, 12], [6, 12], [25, 12]]
        phase_1 = [(TURRET, t_pos) for t_pos in turret_positions]
        + [(WALL, w_pos) for w_pos in wall_positions]
        + [(UPGRADE, u_pos) for u_pos in upgrade_turret_positions]
        if not self.build_phase(game_state, phase_1):
            return
        opening_phase = 1

        if (game_state.turn_number == 0):
            return

        # expected turn 2
        phase_2 = [(UPGRADE, [18, 9])]
        if not self.build_phase(phase_2):
            return
        opening_phase = 2

        # expected turn 2/3
        # ? do the walls get spawned in list-order priority?
        wall_positions = [[7, 12], [7, 11], [7, 10], [8, 9], [26, 13], [27, 13], [0, 13], [1, 13], [2, 13], [4, 13], [5, 13]]
        phase_3 = [(WALL, w_pos) for w_pos in wall_positions]
        if not self.build_phase(game_state, phase_3):
            return
        opening_phase = 3

        # expected turn 4
        phase_4 = [(TURRET, [21, 11]), (WALL, [21, 12]), (WALL, [22, 12])]
        if not self.build_phase(phase_4):
            return
        opening_phase = 4

        # expected turn 5
        wall_positions = [[20, 11], [19, 10], [22, 14]] + [[x, 8] for x in range(9, 17)]
        phase_5 = [(UPGRADE, [21, 11])] + [(WALL, w_pos) for w_pos in wall_positions]
        if not self.build_phase(phase_5):
            return
        opening_phase = 5

        return opening_phase

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
