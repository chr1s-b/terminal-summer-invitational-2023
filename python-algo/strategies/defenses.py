import gamelib
import math

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

        self.holes = []
        self.reserved_sp = 0
        self.phase = 0
        return

    def position_in_hole(self, position):
        for hole in self.holes:
            _, positions = hole
            if position in positions:
                return True
        return False

    def update_holes(self):
        updated_holes = []
        for hole in self.holes:
            hole[0] -= 1
            if hole[0] >= 0:  # not expired
                updated_holes.append(hole)
        self.holes = updated_holes

    def make_hole(self, game_state, locations, duration=1):
        """Make a hole in the defenses for {duration} turns."""
        self.holes.append([duration, locations])
        game_state.attempt_remove(locations)
        gamelib.debug_write(f'Attempting to remove at {locations}.')

    def reset_reserved_sp(self):
        self.reserved_sp = 0

    def reserve_sp(self, amount):
        self.reserved_sp += amount

    def five_turret(self, game_state, destroyed_supports):
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

        if game_state.turn_number != 0:
            # phase 2
            phases.append([(UPGRADE, [18, 9])])
    
            # phase 3 - build middle supports and walls
            initial_supports = [[12, 8], [13, 8]]
            wall_positions = [[26, 13], [27, 13], [7, 12], [7, 11], [7, 10], [8, 9], [0, 13], [1, 13], [2, 13], [4, 13], [5, 13]]
            phases.append([(WALL, w_pos) for w_pos in wall_positions] + ([support_and_upgrade for s_pos in initial_supports for support_and_upgrade in ((SUPPORT, s_pos), (UPGRADE, s_pos))] if len(destroyed_supports) == 0 else []))
    
            # phase 4
            phases.append([(TURRET, [21, 11]), (UPGRADE, [21, 11]),
                           (TURRET, [21, 12]), (UPGRADE, [21, 12]),
                           (TURRET, [22, 12]), (UPGRADE, [22, 12])])
    
            # phase 5
            wall_positions = [[20, 11], [19, 10]] + [[x, 8] for x in range(16, 8, -1)]
            phases.append([(UPGRADE, [21, 11])] + [(WALL, w_pos) for w_pos in wall_positions])
    
            # phase 6
            backup_supports = [[12, 7], [13, 7]]
            wall_positions = [[21, 13], [22, 13], [25, 13], [26, 12],
                              [24, 11], [23, 10], [22, 9], [21, 8]]
            wall_ugprades = [[25, 13], [26, 13], [27, 13], [0, 13], [1, 13], [2, 13]]
            phases.append([(UPGRADE, u_pos) for u_pos in wall_ugprades] + [(WALL, w_pos) for w_pos in wall_positions] + [support_and_upgrade for s_pos in backup_supports for support_and_upgrade in ((SUPPORT, s_pos), (UPGRADE, s_pos))])

        completed = self.build_phases(game_state, phases)
        return completed

    def build_midgame_defenses(self, game_state):
        """Upgrade and maintain defences in the mid-game."""
        # currently quits when it fails to complete a phase

        phases = []

        # phase 0 corresponds to opening complete
        # phase 1 adds a turret on left and builds upgraded supports
        phases.append([(TURRET, [1, 12]), (UPGRADE, [1, 12]),
                       (TURRET, [5, 12]), (UPGRADE, [5, 12])])

        # phase 2 upgrades left turret, adds walls
        wall_positions = [[2, 12], [4, 12], [22, 12]]
        phases.append([(WALL, pos) for pos in wall_positions])

        # phase 3 adds a turret on the right, upgrades turret
        phases.append([(TURRET, [25, 11]), (UPGRADE, [25, 11])])

        # phase 4 adds a turret on mid right, upgrade turret
        phases.append([(TURRET, [20, 10]), (UPGRADE, [20, 10])])

        # phase 5 reinforce right of gaunlet with upgraded walls and new turret
        wall_positions = [[26, 13], [27, 13], [25, 13], [26, 12]] #? not sure about order
        phases.append([(TURRET, [24, 12]), (UPGRADE, [24, 12]),
                       (TURRET, [25, 11]), (UPGRADE, [25, 11]),
                       (TURRET, [24, 10]), (UPGRADE, [24, 10])]
                       + [(UPGRADE, w_pos) for w_pos in wall_positions])

        # phase 6 add supports
        backwall_supports = [[i, 9] for i in range(16, 10, -1)]
        positions = [[20, 10], [23, 9], [19, 9]] + backwall_supports
        phase = []
        for pos in positions:
            phase += [(SUPPORT, pos), (UPGRADE, pos)]
        phases.append(phase)

        completed = self.build_phases(game_state, phases)
        return completed

    def build_phase(self, game_state, phase, force=False):
        hole_locations = [location for location in map(lambda x: x[1], self.holes)]
        gamelib.debug_write('Hole locations {}'.format(hole_locations))
        """Build phase and return whether complete."""
        complete = True
        for structure, location in phase:
            if self.position_in_hole(location) and not force:
                continue
            if game_state.get_resource(SP) - self.build_cost(game_state, structure, location) < self.reserved_sp:
                # never spend reserved sp
                continue
            if structure == UPGRADE:
                game_state.attempt_upgrade(location)
                unit = game_state.contains_stationary_unit(location)
                if not unit or not unit.upgrade:
                    gamelib.debug_write(f'Could not upgrade {unit} at {location}.')
                    complete = False
                else:
                    gamelib.debug_write(f'Upgraded {unit} at {location}.')
            else:
                if structure == WALL and location in hole_locations:
                    continue
                game_state.attempt_spawn(structure, location)
                unit = game_state.contains_stationary_unit(location)
                if not unit:
                    gamelib.debug_write(f'Could not spawn {unit} at {location}.')
                    complete = False
                else:
                    gamelib.debug_write(f'Spawned {unit} at {location}.')
        # gamelib.debug_write(f'build_phase returns complete={complete}')
        return complete

    def build_phases(self, game_state, phases, force=False):
        """Build multiple phases and return how many are complete."""
        for i, phase in enumerate(phases):
            isComplete = self.build_phase(game_state, phase, force)
            if not isComplete:
                return i
        return len(phases)

    def check_backwall_holes(self, game_state):
        """List holes in backwall."""
        backwall = [[7, 11], [7, 10], [8, 9]] + [[x, 8] for x in range(9, 17)]
        holes = []
        for pos in backwall:
            if not game_state.contains_stationary_unit(pos):
                holes.append(pos)
        return holes

    def is_completed_backwall(self, game_state):
        """Return if backwall is in a complete state."""
        holes = self.check_backwall_holes(game_state)
        return len(holes) <= 1

    def build_cost(self, game_state, structure, location):
        if structure == UPGRADE:
            # find if there is a unit at the position
            unit = game_state.contains_stationary_unit(location)
            if not unit:
                return 0
            return game_state.type_cost(unit.unit_type, upgrade=True)[SP]
        else:
            return game_state.type_cost(structure)[SP]

    def get_damaged_walls_locations(self, game_state):
        damaged_threshold = 0.75
        damaged_walls_locations = []
        for location in game_state.game_map:
            unit = game_state.contains_stationary_unit(location)
            if unit and unit.unit_type == WALL and (not unit.upgraded) and unit.player_index == 0 and unit.health/unit.max_health < damaged_threshold:
                damaged_walls_locations.append(location)

        return damaged_walls_locations
    
    def remove_damaged_walls(self, game_state):
        remaining_sp = game_state.get_resource(SP)
        # Use up half of remainign sp next turn to replace walls
        damaged_walls_locations = self.get_damaged_walls_locations(game_state)[0: math.ceil(remaining_sp / 2)]
        gamelib.debug_write('Repairing walls: {}'.format(damaged_walls_locations))
        for location in damaged_walls_locations:
            game_state.attempt_remove(location)

        return damaged_walls_locations
