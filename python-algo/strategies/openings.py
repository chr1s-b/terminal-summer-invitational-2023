import gamelib


class Openings:
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
        return

    def five_turret(self, game_state):
        """Builds opening state with four turrets and five walls."""
        start_sp = game_state.get_resource(SP)

        # turn 1
        turret_positions = [[3, 12], [6, 12], [25, 12], [18, 9]]
        wall_positions = [[3, 13], [6, 13], [25, 13], [17, 9], [18, 10]]
        upgrade_turret_positions = [[3, 12], [6, 12], [25, 12]]
        game_state.attempt_spawn(TURRET, turret_positions)
        game_state.attempt_spawn(WALL, wall_positions)
        game_state.attempt_upgrade(upgrade_turret_positions)

        # expected turn 2
        upgrade_turret_positions += [[18, 9]]
        game_state.attempt_upgrade(upgrade_turret_positions)

        # expected turn 2/3
        # ? do the walls get spawned in list-order priority?
        wall_positions += [[7, 12], [7, 11], [7, 10], [8, 9], [26, 13], [27, 13]]
        game_state.attempt_spawn(WALL, wall_positions)

        # expected turn 4
        turret_positions += [[21, 11]]
        wall_positions += [[21, 12], [22, 12]]
        game_state.attempt_spawn(TURRET, turret_positions)
        game_state.attempt_spawn(wall_positions)

        # expected turn 5
        upgrade_turret_positions += [[21, 11]]
        wall_positions += [[20, 11], [19, 10]]
        wall_positions += [[x, 8] for x in range(9, 17)]
        game_state.attempt_upgrade(upgrade_turret_positions)
        game_state.attempt_spawn(WALL, wall_positions)

        return start_sp == game_state.get_resource(SP)
