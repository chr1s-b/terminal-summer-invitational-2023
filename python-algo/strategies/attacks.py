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
        SpawnPoint2 = [7, 6] #low-left
        SpawnPoint3 = [21, 7] #high-right
        SpawnPoint4 = [17, 3] #low-right
        global sent_destroyers
        sent_destroyers = False
        self.mid_attack_next_turn = False
        return

    def attack(self, game_state, strat_phase):
        # TODO: Replace this
        middleStillOpen = 5
        numMP = math.floor(game_state.get_resource(MP))
        if game_state.turn_number == 0:
            game_state.attempt_spawn(SCOUT, [14, 0], 1)
            game_state.attempt_spawn(SCOUT, [6, 7], 3)

        if strat_phase < middleStillOpen:
            depRight, depLeft = self.spawn_intercept(game_state)
            if depLeft[0] != 0:
                if numMP - depLeft[0] * 2 >= 2:
                    game_state.attempt_spawn(INTERCEPTOR, depLeft[1], depLeft[0])
                else:
                    game_state.attempt_spawn(INTERCEPTOR, depLeft[1], 1)
            if depRight[0] != 0:
                game_state.attempt_spawn(INTERCEPTOR, depRight[1], depRight[0])
            self.early_scouts(game_state)

        if strat_phase > middleStillOpen:
            global sent_destroyers
            if self.mid_attack_next_turn:  # now it's "next turn"
                self.do_mid_attack(game_state)
                self.mid_attack_next_turn = False
            else:
                gauntletSpawn, damageGauntlet = self.send_boosted_destroyers(game_state)
                game_state_copy = game_state
                damageMid = self.simul_remove_mid(game_state_copy)

                if game_state.turn_number > 15 and damageMid < damageGauntlet and numMP >= 12:
                    game_state.attempt_remove([9,8])
                    self.mid_attack_next_turn = True
                else:
                    # send scout + demo combo round after sending destroyers, then revert
                    # above heuristic can be optimized to check if sending destroyers was successful, rather than sending right after
                    if not sent_destroyers:
                        if numMP >= 12:
                            game_state.attempt_spawn(DEMOLISHER, gauntletSpawn, 7)    
                            sent_destroyers = True
                    else:
                        self.scout_demo_combo(game_state)
                        sent_destroyers = False

    def do_mid_attack(self, game_state):
        game_state.attempt_spawn(DEMOLISHER, SpawnPoint2, 1)
        self.early_scouts(game_state)
        game_state.attempt_spawn(DEMOLISHER, SpawnPoint2, 7)
        return

    def least_damage_path(self, game_state, location_options):
        damages = []
        for location in location_options:
            damage = self.damage_during_path(game_state, location)
            damages.append(damage)
        minDamage = min(damages)
        return [location_options[damages.index(minDamage)], minDamage]

    def least_damage_path_enemy(self, game_state, location_options):
        damages = []
        for location in location_options:
            damage = self.damage_during_path(game_state, location, player=1)
            damages.append(damage)
        minDamage = min(damages)
        return [location_options[damages.index(minDamage)], minDamage]

    def early_scouts(self, game_state):
        friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
        best_location, minDamage = self.least_damage_path(game_state, deploy_locations)
        numScouts = int(game_state.get_resource(MP))
        totalScoutHealth = numScouts * 20
        if totalScoutHealth > minDamage:
            game_state.attempt_spawn(SCOUT, best_location, numScouts)

    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        right_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        for location in locations:
            if location in right_edges:
                if not game_state.contains_stationary_unit(location) and not game_state.contains_stationary_unit([location[0] - 1, location[1]]) and not game_state.contains_stationary_unit([location[0], location[1] + 1]):
                    filtered.append(location)
            else:
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
        if numPosEnemyAttackers >= 8:
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

            total_health = numPosEnemyAttackers * (20 + max_shielding)
            if minDamage_left < total_health:
                # Gamble and send half to conserve mobile points
                numDeploy = math.floor(total_health - minDamage_left / 6 / 4)
                interceptors[0] = [numDeploy, SpawnPoint3]
            if minDamage_right < total_health:
                numDeploy = math.floor(total_health - minDamage_right / 6 / 4) 
                interceptors[1] = [numDeploy, SpawnPoint2]
        return interceptors

    def send_boosted_destroyers(self, game_state):
        spawnLoc = self.where_spawn_dest(game_state)
        listicle = self.least_damage_path(game_state, [spawnLoc])
        return listicle

    def where_spawn_dest(self, game_state):
        spawn_locs = [SpawnPoint1, [3, 11], [4, 11]]
        for location in spawn_locs:
            if len(game_state.get_attackers(location, 0)) > 0:
                return SpawnPoint2
        return SpawnPoint1

    def simul_remove_mid(self, game_state_copy):
        game_state_copy.game_map.remove_unit([9, 8])
        _, minDamage = self.least_damage_path(game_state_copy, [SpawnPoint2])
        return minDamage

    def scout_demo_combo(self, game_state):
        game_state.attempt_spawn(DEMOLISHER, SpawnPoint3, 1)
        spawnLoc = self.where_spawn_dest(game_state)
        game_state.attempt_spawn(SCOUT, spawnLoc, 1)

    def damage_during_path(self, game_state, start_location, player=0):
        path = game_state.find_path_to_edge(start_location)
        damage = 0
        for path_location in path:
            # Get number of enemy turrets that can attack each location and multiply by turret damage
            for unit in game_state.get_attackers(path_location, player):
                if unit.attackRange > 3.5: #seeing if upgraded or not
                    damage += 20
                else:
                    damage += 8
        return damage
