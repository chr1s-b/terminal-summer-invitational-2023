import gamelib
import math

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
        SpawnPoint1 = [2, 11] #high-left
        SpawnPoint2 = [8, 5] #low-left
        SpawnPoint3 = [21, 7] #high-right
        SpawnPoint4 = [17, 3] #low-right
        return

    def attack(self, game_state, strat_phase):
        # TODO: Replace this
        middleStillOpen = 1

        if game_state.turn_number == 1:
            game_state.attempt_spawn(SCOUT, [14, 0], 1)
            game_state.attempt_spawn(SCOUT, [6, 7], 3)
        
        if strat_phase < middleStillOpen:
            interceptors = self.spawn_intercept(game_state)
            depRight = interceptors[0]
            depLeft = interceptors[1]
            if depLeft[0] != 0 :
                game_state.attempt_spawn(INTERCEPTOR, depLeft[1], depLeft[0])
            if depRight[0] != 0 :
                game_state.attempt_spawn(INTERCEPTOR, depRight[1], depRight[0])
            self.early_scouts(game_state)
        if strat_phase > middleStillOpen:
            # need way to determine which attack will be most effective, if can spawn reasonable #, if nothing on right, comparing lowest damage
            self.send_boosted_destroyers(game_state)
            #self.scout_demo_combo(game_state)
            #game_state_copy = game_state
            #self.simul_remove_mid(game_state_copy)
         
   
    def least_damage_path(self, game_state, location_options):
        damages = []
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy turrets that can attack each location and multiply by turret damage
                for unit in game_state.get_attackers(path_location, 0):
                    if unit.attackRange > 3.5: # seeing if upgraded or not
                        damage += 20
                    else:
                        damage += 8
            damages.append(damage)

        minDamage = min(damages)
        return [location_options[damages.index(minDamage)], minDamage]

    def least_damage_path_enemy(self, game_state, location_options):
        damages = []
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy turrets that can attack each location and multiply by turret damage
                for unit in game_state.get_attackers(path_location, 1):
                    if unit.attackRange > 3.5: #seeing if upgraded or not
                        damage += 20
                    else:
                        damage += 8
            damages.append(damage)

        minDamage = min(damages)
        return [location_options[damages.index(minDamage)], minDamage]

    def early_scouts(self, game_state):
        friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
        listicle = self.least_damage_path(game_state, deploy_locations)
        best_location = listicle[0]
        minDamage = listicle[1]
        numScouts = int(game_state.get_resource(MP))
        totalScoutHealth = numScouts * 20
        if totalScoutHealth > minDamage:
            game_state.attempt_spawn(SCOUT, best_location, numScouts)

    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
           if not game_state.contains_stationary_unit(location):
              filtered.append(location)
        return filtered
    
    def calculate_shielding_map(self, game_state, player_index):
        grid = [[0 for _ in range(0, game_state.game_map.ARENA_SIZE)] for _ in range(0, game_state.game_map.ARENA_SIZE)]
        for location in game_state.game_map:
            if len(game_state.game_map[location]) != 0 and game_state.game_map[location][0].unit_type == SUPPORT and game_state.game_map[location][0].player_index == player_index:
                support_unit = game_state.game_map[location][0]
                # Get y position relative to enemy
                shield_bonus =  support_unit.shieldBonusPerY * (support_unit.y if player_index == 0 else (27 - support_unit.y)) 
                shield_strength = support_unit.shieldPerUnit + shield_bonus
                shield_range = support_unit.shieldRange
                for shield_location in game_state.game_map.get_locations_in_range(location, shield_range):
                    grid[shield_location[0]][shield_location[1]] += shield_strength

        return grid

    def spawn_intercept(self, game_state):
        # TODO: Change this
        middleIsOpen = True
        enemy_shielding_map = self.calculate_shielding_map(game_state, player_index=1)

        #note: doesn't incldue effects of supports yet (just assuming they're boosted by div by 6, could make 9 if know no supports)
        interceptors = [[0, [0,0]], [0, [0,0]]] #[leftside (num to spawn, where to spawn), rightside (num to spawn, where to spawn)]
        numPosEnemyAttackers = game_state.get_resource(MP, player_index=1)
        if numPosEnemyAttackers > 8:
            enemy_edges_right = game_state.game_map.get_edge_locations(game_state.game_map.TOP_RIGHT)
            enemy_edges_left = game_state.game_map.get_edge_locations(game_state.game_map.TOP_LEFT)
            deploy_locations_right = self.filter_blocked_locations(enemy_edges_right, game_state)
            deploy_locations_left = self.filter_blocked_locations(enemy_edges_left, game_state)
            enemy_path_right = self.least_damage_path_enemy(game_state, deploy_locations_right)
            enemy_path_left = self.least_damage_path_enemy(game_state, deploy_locations_left)
            best_location_right = enemy_path_right[0]
            minDamage_right = enemy_path_right[1]
            best_location_left = enemy_path_left[0]
            minDamage_left = enemy_path_left[1]

            enemy_path_locations = game_state.find_path_to_edge(enemy_path_left[0]) +  game_state.find_path_to_edge(enemy_path_right[0])

            max_shielding = max([enemy_shielding_map[enemy_path_location[0]][enemy_path_location[1]] for enemy_path_location in enemy_path_locations])

            total_health = numPosEnemyAttackers * 20 + max_shielding
            if minDamage_left < total_health:
                numDeploy = math.ceil(total_health - minDamage_left / 6)
                interceptors[0] = [numDeploy, SpawnPoint3]
            if minDamage_right < total_health:
                numDeploy = math.ceil(total_health - minDamage_right / 6)
                interceptors[1] = [numDeploy, SpawnPoint2]
        return interceptors

    def send_boosted_destroyers(self, game_state):
        spawnLoc = self.where_spawn_dest(game_state)
        if self.get_resource(MP, 0) >= 12:
           game_state.attempt_spawn(DEMOLISHER, spawnLoc, 7)

    def where_spawn_dest(self, game_state):
        spawn_locs = [SpawnPoint1, [3, 11], [4, 11], [5, 11]]
        numAttackers = 0
        for location in spawn_locs:
            numAttackers += len(self.get_attackers(location, 0))
        if numAttackers != 0:
            return SpawnPoint2
        else:
            return SpawnPoint1

 #   def simul_remove_mid(self, game_state):
 #       pass
        # gets passed the game state copy, changes it to simul removing a mid piece and attacking
   # if self.contains_stationary_unit([x,y]):
            #            self.game_map[x,y][0].pending_removal = True

#    def scout_demo_combo(self, game_state):
 #       pass

   
