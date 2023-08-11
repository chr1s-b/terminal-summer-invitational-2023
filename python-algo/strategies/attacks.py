import gamelib


class Attacks:
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
        global SpawnPoint1, SpawnPoint2, SpawnPoint3, SpawnPoint4
        # change these, will be one higher spawn point and one lower spawn point / side
        SpawnPoint1 = [0, 13]
        SpawnPoint2 = [0, 13]
        SpawnPoint3 = [0, 13]
        SpawnPoint4 = [0, 13]
        return

    def attack(self, game_state):
        pass
        #if game_state.turn_number == 1:
            #hardcode where to send some scouts
         #if game_state.turn_number < someNum:
                # send early scouts
         #if strat_phase (or whatever we name it) > x, x representing support phase num:
                # boosted demolisher, combo, remove_mid --> need way to determine which will be most effective
                # for simul: game_state_copy = gamelib.GameState(self.config, turn_state)
         #if strat_phase < y, y representing middle still open:
            # intercept stuff

    #game_state.get_resource(MP) >= game_state.type_cost(INTERCEPTOR)[MP]
    #game_state.attempt_spawn(INTERCEPTOR, deploy_location)
    #game_state.attempt_spawn(DEMOLISHER, [24, 10], 1000)
    def least_damage_path(self, game_state):
        pass
        #damages = []
        # Get the damage estimate each path will take
       # for location in location_options:
        #    path = game_state.find_path_to_edge(location)
          #  damage = 0
         #   for path_location in path:
                # Get number of enemy turrets that can attack each location and multiply by turret damage
       #         damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(TURRET, game_state.config).damage_i
       #     damages.append(damage)
        
        # Now just return the location that takes the least damage
      #  return location_options[damages.index(min(damages))]

    def num_spawn_intercept(self, game_state):
        pass
    
    def early_scouts(self, game_state):
        pass
    #friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
    #deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
#def filter_blocked_locations(self, locations, game_state):
 #       filtered = []
 #       for location in locations:
  #          if not game_state.contains_stationary_unit(location):
   #             filtered.append(location)
  #      return filtered
    
    def where_spawn_intercept(self, game_state):
        pass

    def send_boosted_destroyers(self, game_state):
        pass

    def simul_remove_mid(self, game_state):
        pass
        # gets passed the game state copy, changes it to simul removing a mid piece and attacking

    def scout_demo_combo(self, game_state):
        pass

   
