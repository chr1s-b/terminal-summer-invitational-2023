import gamelib
import math
import copy


class Attacks:
    def __init__(self, config, defenses):
        self.config = config
        self.defenses = defenses
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
        self.mid_attack_next_turn = False
        self.left_attack_next_turn = False
        return

    def attack(self, game_state, strat_phase):
        middleStillOpen = 5

        numMP = math.floor(game_state.get_resource(MP))
        enemy_shielding_map = self.calculate_shielding_map(game_state, player_index=1)
        our_shielding_map = self.calculate_shielding_map(game_state, player_index=0)
        numMP_enemy = math.floor(game_state.get_resource(MP, player_index=1))
        if strat_phase < middleStillOpen:
            # Prioritize planned attacks from the previous turn
            if self.mid_attack_next_turn:
                self.do_mid_attack(game_state)
            elif self.left_attack_next_turn:
                self.do_left_attack(game_state)

            # Spawn demolishers 
            if game_state.turn_number > 0 and (numMP_enemy <= 8 or numMP > 10):
                self.spawn_early_demolishers(game_state, our_shielding_map)
            else:
                self.spawn_early_demolishers(game_state, our_shielding_map, 1)

            # Spawn interceptors
            depRight, depLeft = self.spawn_intercept(game_state, enemy_shielding_map)
            if depLeft[0] != 0:
                if numMP - depLeft[0] * 2 >= 4 and numMP_enemy >= 12:
                    game_state.attempt_spawn(INTERCEPTOR, depLeft[1], depLeft[0])
                else:
                    game_state.attempt_spawn(INTERCEPTOR, depLeft[1], 1)
            if depRight[0] != 0:
                if numMP_enemy >= 12:
                    game_state.attempt_spawn(INTERCEPTOR, depRight[1], depRight[0])
                else:
                    game_state.attempt_spawn(INTERCEPTOR, depRight[1], 1)

            if game_state.turn_number > 0:
                self.early_scouts(game_state)

        if strat_phase >= middleStillOpen:
            if len(game_state.game_map[[23,14]]) != 0 and len(game_state.game_map[[22,14]]) != 0:
                if numMP >= 18:
                    game_state.attempt_spawn(DEMOLISHER, SpawnPoint3, 7)
                
            global sent_destroyers
            if self.mid_attack_next_turn:  # now it's "next turn"
                self.do_mid_attack(game_state)
            elif self.left_attack_next_turn:
                self.do_left_attack(game_state)
            else:
                gauntletSpawn, damageGauntlet = self.send_boosted_destroyers(game_state)
                game_state_copy = copy.deepcopy(game_state)
                game_state_copy_left = copy.deepcopy(game_state)
                damageMid = self.simul_remove_mid(game_state_copy)
                damageLeft = self.simul_remove_left(game_state_copy_left)
                if damageMid < damageGauntlet - 10 and damageMid < damageLeft + 20 and numMP >= 12:
                    self.defenses.make_hole(game_state, [[9, 8]])
                    self.mid_attack_next_turn = True
                elif damageLeft < damageGauntlet and damageGauntlet >= 100 and len(game_state.get_attackers([2, 14], 0)) <= 1 and numMP >= 12:
                    self.defenses.make_hole(game_state, [[2, 12], [2, 13]])
                    self.left_attack_next_turn = True
                else:
                    if self.right_side_open(game_state) and numMP >= 7:  
                        self.scout_demo_combo(game_state)
                    else:
                        if numMP >= 15:
                            game_state.attempt_spawn(DEMOLISHER, gauntletSpawn, 7)

    def do_mid_attack(self, game_state):
        game_state.attempt_spawn(DEMOLISHER, SpawnPoint2, 2)
        self.early_scouts(game_state)
        game_state.attempt_spawn(DEMOLISHER, SpawnPoint2, 7)
        self.mid_attack_next_turn = False
        return

    def do_left_attack(self, game_state):
        game_state.attempt_spawn(DEMOLISHER, [3,10], 2)
        game_state.attempt_spawn(SCOUT, [14,0], 5)
        game_state.attempt_spawn(SCOUT, [16, 2], 20)
        self.left_attack_next_turn = False
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
        bottom_left_locations = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT)
        bottom_right_locations = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        friendly_edges = bottom_left_locations + bottom_right_locations
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
        best_location, minDamage = self.least_damage_path(game_state, deploy_locations)
        numScouts = int(game_state.get_resource(MP))
        totalScoutHealth = numScouts * 20
        if totalScoutHealth > minDamage:
            if numScouts <= 5:
                game_state.attempt_spawn(SCOUT, best_location, numScouts)
            else:
                if best_location in bottom_left_locations:
                    suicide_location = (16, 2)
                else:
                    suicide_location = (best_location[0] + 1, best_location[1] + 1)
                game_state.attempt_spawn(SCOUT, suicide_location, 5)
                game_state.attempt_spawn(SCOUT, best_location, max(numScouts - 5, 0))

    def right_side_open(self, game_state):
        if len(game_state.get_attackers([23, 13], 0)) >= 1:
            return False
        else:
            return True

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
                shield_bonus = support_unit.shieldBonusPerY * (support_unit.y if player_index == 0 else (27 - support_unit.y)) 
                shield_strength = support_unit.shieldPerUnit + shield_bonus
                shield_range = support_unit.shieldRange
                for shield_location in game_state.game_map.get_locations_in_range(location, shield_range):
                    grid[shield_location[0]][shield_location[1]] += shield_strength

        return grid        

    def spawn_intercept(self, game_state, enemy_shielding_map):
        numMP_enemy = math.floor(game_state.get_resource(MP, player_index=1))
        # note: doesn't incldue effects of supports yet (just assuming they're boosted by div by 6, could make 9 if know no supports)
        interceptors = [[0, [0, 0]], [0, [0, 0]]] #[leftside (num to spawn, where to spawn), rightside (num to spawn, where to spawn)]
        numPosEnemyAttackers = game_state.get_resource(MP, player_index=1)
        if numPosEnemyAttackers >= 5:
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

            left_path = game_state.find_path_to_edge(enemy_path_left[0]) or []
            right_path = game_state.find_path_to_edge(enemy_path_right[0]) or []
            enemy_path_locations = left_path + right_path

            max_shielding = max([enemy_shielding_map[enemy_path_location[0]][enemy_path_location[1]] for enemy_path_location in enemy_path_locations])

            total_health = numPosEnemyAttackers * (20 + max_shielding)
            if numMP_enemy >= 15:
                if minDamage_left < total_health:
                    # Gamble and send half to conserve mobile points
                    numDeploy = min(2, math.floor((total_health - minDamage_left) / 6 / 4))
                    interceptors[0] = [numDeploy, SpawnPoint3]
                if minDamage_right < total_health:
                    numDeploy = min(2, math.floor((total_health - minDamage_right) / 6 / 4))
                    interceptors[1] = [numDeploy, SpawnPoint2]
            else:
                if minDamage_left <= minDamage_right and minDamage_left < total_health:
                    # Gamble and send half to conserve mobile points
                    numDeploy = min(2, math.floor((total_health - minDamage_left) / 6 / 4))
                    interceptors[0] = [numDeploy, SpawnPoint3]
                if minDamage_right < minDamage_left and minDamage_right < total_health:
                    numDeploy = min(2, math.floor((total_health - minDamage_right) / 6 / 4))
                    interceptors[1] = [numDeploy, SpawnPoint2]
        return interceptors

    def calculate_demolisher_damage(self, game_state, spawn_location, spawn_count, our_shielding_map):
        # This is an estimate since it doesn't simulate the destruction of buildings
        base_demolisher_health = 5 + our_shielding_map[spawn_location[0]][spawn_location[1]]
        demolisher_damage = 8
        demolisher_path = game_state.find_path_to_edge(spawn_location)
        if not demolisher_path:
            return 0
        inflicted_damage = 0
        num_demolishers = spawn_count
        curr_demolisher_health = base_demolisher_health
        for location in demolisher_path:
            enemy_health_in_range = 0
            for demolisher_attack_location in game_state.game_map.get_locations_in_range(location, 4.5):
                if len(game_state.game_map[demolisher_attack_location]) > 0 and game_state.game_map[demolisher_attack_location][0].player_index == 1:
                    enemy_health_in_range += game_state.game_map[demolisher_attack_location][0].health

            inflicted_damage += min(enemy_health_in_range, num_demolishers * demolisher_damage) 

            damage = 0
            for unit in game_state.get_attackers(location, 0):
                if unit.attackRange > 3.5: #seeing if upgraded or not
                    damage += 20
                else:
                    damage += 8

            curr_demolisher_health -= damage
            if curr_demolisher_health <= 0:
                num_demolishers -= 1
                curr_demolisher_health = base_demolisher_health

            if num_demolishers == 0:
                break

        return inflicted_damage

    def spawn_early_demolishers(self, game_state, our_shielding_map, max_amount = 100):
        bottom_left_locations = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT)
        bottom_right_locations = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        deploy_locations = self.filter_blocked_locations(bottom_left_locations + bottom_right_locations, game_state)
        spawn_number = min(game_state.number_affordable(DEMOLISHER), max_amount)
        max_damage = 0
        best_location = SpawnPoint3
        for location in deploy_locations:
            potential_damage = self.calculate_demolisher_damage(game_state, location, spawn_number, our_shielding_map)
            if potential_damage > max_damage:
                max_damage = potential_damage
                best_location = location
        if max_damage > 48:
            game_state.attempt_spawn(DEMOLISHER, best_location, spawn_number)

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

    def simul_remove_left(self, game_state_copy):
        game_state_copy.game_map.remove_unit([2, 12])
        game_state_copy.game_map.remove_unit([2, 13])
        game_state_copy.game_map.add_unit(WALL,[20, 8])
        game_state_copy.game_map.add_unit(WALL,[19, 8])
        if len(game_state_copy.game_map[[21,8]]) == 0:
            game_state_copy.game_map.add_unit(WALL,[21, 8])
        _, minDamage = self.least_damage_path(game_state_copy, [[14, 0]])
        return minDamage

    def scout_demo_combo(self, game_state):
        game_state.attempt_spawn(DEMOLISHER, SpawnPoint3, 2)
        spawnLoc = self.where_spawn_dest(game_state)
        game_state.attempt_spawn(SCOUT, spawnLoc, 10)

    def damage_during_path(self, game_state, start_location, player=0):
        path = game_state.find_path_to_edge(start_location)
        if not path:
            return 0

        damage = 0
        for path_location in path:
            # Get number of enemy turrets that can attack each location and multiply by turret damage
            for unit in game_state.get_attackers(path_location, player):
                if unit.attackRange > 3.5:  # seeing if upgraded or not
                    damage += 20
                else:
                    damage += 8
        return damage

    def build_funnels(self, game_state):
        if self.left_attack_next_turn:
            temporary_funnel = [[23, 12], [24, 12], [14, 2], [15, 3], [16, 4]]
            for temporary_funnel_location in temporary_funnel:
                game_state.attempt_spawn(WALL, temporary_funnel_location)
                game_state.attempt_remove(temporary_funnel_location)  
