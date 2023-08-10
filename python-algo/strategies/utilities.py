import gamelib


class Utilities:
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

        # Used to compare difference between the previous game state and the current one
        self.prev_game_map = None
        self.destroyed_structures = {WALL: [], SUPPORT: [], TURRET: []}
        return

    def track_destroyed_structures(self, game_state):
        """Tracks walls that have been destroyed in the recent turn."""
        if self.prev_game_map:
            for structure in [WALL, SUPPORT, TURRET]:
                for location in game_state.game_map:
                    if len(self.prev_game_map[location]) == 0 :
                        continue

                    prev_unit = self.prev_game_map[location][0]     

                    if prev_unit.player_index == 0 and len(game_state.game_map[location]) == 0 and prev_unit.unit_type == structure:
                        self.destroyed_structures[structure].append(location)

        self.prev_game_map = game_state.game_map
        return self.destroyed_structures

    def enemy_balance(self, game_state):
        """Get enemy balance of MP and SP."""
        return [game_state.get_resource(SP, player_index=1), game_state.get_resource(MP, player_index=1)]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x=None, valid_y=None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units

    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy turrets that can attack each location and multiply by turret damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(TURRET, game_state.config).damage_i
            damages.append(damage)

        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]
