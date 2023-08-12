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

        phases = []

        # phase 1
        turret_positions = [[3, 12], [6, 12], [25, 12], [18, 9]]
        wall_positions = [[3, 13], [6, 13], [25, 13], [17, 9], [18, 10]]
        upgrade_turret_positions = [[3, 12], [6, 12], [25, 12]]
        turrets = [(TURRET, t_pos) for t_pos in turret_positions]
        walls = [(WALL, w_pos) for w_pos in wall_positions]
        upgrades = [(UPGRADE, u_pos) for u_pos in upgrade_turret_positions]
        phases.append(turrets + walls + upgrades)

        # phase 2
        phases.append([(UPGRADE, [18, 9])])

        # phase 3
        wall_positions = [[26, 13], [27, 13], [7, 12], [7, 11], [7, 10], [8, 9], [0, 13], [1, 13], [2, 13], [4, 13], [5, 13]]
        phases.append([(WALL, w_pos) for w_pos in wall_positions])

        # phase 4
        phases.append([(TURRET, [21, 11]), (WALL, [21, 12]), (WALL, [22, 12])])

        # phase 5
        wall_positions = [[20, 11], [19, 10]] + [[x, 8] for x in range(16, 8, -1)]
        phases.append([(UPGRADE, [21, 11])] + [(WALL, w_pos) for w_pos in wall_positions])

        # phase 6
        wall_positions = [[21, 13], [22, 13], [25, 13], [26, 12],
                          [24, 11], [23, 10], [22, 9], [21, 8]]
        phases.append([(UPGRADE, u_pos) for u_pos in [[25, 13], [26, 13], [27, 13]]] + [(WALL, w_pos) for w_pos in wall_positions])

        completed = self.build_phases(game_state, phases)
        return completed

    def build_midgame_defenses(self, game_state):
        """Upgrade and maintain defences in the mid-game."""
        # currently quits when it fails to complete a phase

        phases = []

        # phase 0 corresponds to opening complete
        # phase 1 adds a turret on left and builds upgraded supports
        support_positions_phase_1 = [[4, 11], [5, 11], [6, 11]]
        phases.append([(TURRET, [1, 12])] + [(SUPPORT, s_pos) for s_pos in support_positions_phase_1] + [(UPGRADE, s_pos) for s_pos in support_positions_phase_1])

        # phase 2 upgrades left turret, adds walls
        wall_positions = [[2, 12], [4, 12], [5, 12], [22, 12]]
        phases.append([(UPGRADE, [1, 12])] + [(WALL, pos) for pos in wall_positions])

        # phase 3 adds a turret on the right, upgrades turret
        phases.append([(TURRET, [25, 11]), (UPGRADE, [25, 11])])

        # phase 4 adds a turret on mid right, upgrade turret
        phases.append([(TURRET, [20, 10]), (UPGRADE, [20, 10])])

        completed = self.build_phases(game_state, phases)
        return completed

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

    def build_phases(self, game_state, phases):
        """Build multiple phases and return how many are complete."""
        for i, phase in enumerate(phases):
            isComplete = self.build_phase(game_state, phase)
            if not isComplete:
                return i
        return len(phases)
