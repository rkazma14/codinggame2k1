import sys
import random
from operator import attrgetter

feature_only_2_remaining = False

#weights = [('finish_it', 16), ('planet_bonus_score', 8) , ('score', 4), ('planet.colonization_score', 2) , ('planet_tasks_sum', 1)]
weights = [('finish_it', 16), ('planet_bonus_score', 8) , ('score', 4), ('planet_tasks_sum', 1)]

bonus_ranking_by_points = {
    "POINTS_3": 16,
    "POINTS_2": 15, 
    "POINTS_1": 14,
    "TECH_RESEARCH_2": 9,
    "TECH_RESEARCH_3": 8,
    "TECH_RESEARCH_4": 7,
    "ENERGY_CORE": 4,
    "ALIEN_ARTIFACT": 0
}

bonus_ranking_by_tech = {
    "TECH_RESEARCH_2": 16,
    "TECH_RESEARCH_3": 15,
    "TECH_RESEARCH_4": 14,
    "POINTS_3": 4,
    "POINTS_2": 4, 
    "ENERGY_CORE": 4,
    "POINTS_1": 4,
    "ALIEN_ARTIFACT": 4
}

number_of_objectives_reached_before_we_target_point = 1

class Game:
    def __init__(self):
        self.sector_index = 0
        self.station_objectives = {}
        self.my_stations = []
        self.opp_stations = []
        self.planets = []
        self.my_bonuses = []
        self.opp_bonuses = []
        self.my_colonization_score = 0
        self.opp_colonization_score = 0
        self.reset()

    def reset(self):
        self.current_station_index = -1
        self.my_stations.sort(key=attrgetter('remaining_upgrades'))

    def tech_first(objectives_reached):
        return (objectives_reached < number_of_objectives_reached_before_we_target_point)

    def get_objectives_reached(self):
        count = 0
        for station in self.my_stations:
            reached = True
            for i in range(len(station.tech)):
                if (station.tech[i] < self.get_station_objective_by_id(station.id).tech_objectives[i]):
                    reached = False
            if reached:
                count += 1
        return count

    def get_station_objective_by_id(self, station_id):
        return self.station_objectives[str(station_id)]

    def get_next_active(self):
        if (self.current_station_index+1 < len(self.my_stations)):
            for i in range(self.current_station_index+1, len(self.my_stations)):
                if self.my_stations[i].available:
                    self.current_station_index = i
                    return self.my_stations[i]
        return None

    def get_next_station(self):
        return self.get_next_active()

    def get_first_valid_planet(self, station):
        for planet in self.planets:
            if self.should_colonize_planet(planet, station):
                return planet
        return None

    def is_planet_not_already_lost(self, planet):
        total_tasks = planet.my_contribution + planet.opp_contribution + planet.tasks_remaining()
        if total_tasks / 2 >= planet.opp_contribution:
            return True
        else:
            return False

    def can_use_station_techs_on_planet(self, planet, station):
        for i in range(len(planet.tasks)):
                if planet.tasks[i] > 0 and station.tech[i] > 0:
                    return True
        return False

    def should_colonize_planet(self, planet, station, go_for_it):
        colonize = self.is_planet_not_already_lost(planet) and self.can_use_station_techs_on_planet(planet, station)
        if colonize and feature_only_2_remaining:
            if len(self.planets) == 2 and (planet.my_contribution + planet.opp_contribution) == 0:
                colonize = False
        if not colonize and go_for_it:
            if planet.my_contribution == 0:
                colonize = True
        return colonize

    def get_best_planet(self, station):
        return self.get_first_valid_planet(station)

    def get_best_tech_from_station(self, tech_level, station):
        print("Station:", station, file=sys.stderr, flush=True)
        station_objective = self.get_station_objective_by_id(station.id)
        for i in range(len(station.tech)):
            print("i:", i, "tech_level:", tech_level, "current_tech_level:", station.tech[i], "station_tech_objective:", station_objective.tech_objectives[i], file=sys.stderr, flush=True)
            target_level = station.tech[i] + 1
            print("bool1:", (target_level == tech_level), "bool2:", (station.tech[i] < station_objective.tech_objectives[i]), file=sys.stderr, flush=True)
            if (target_level == tech_level) and (station.tech[i] < station_objective.tech_objectives[i]):
                print("made it", file=sys.stderr, flush=True)
                return station, i
        return None, None

    def get_best_station_from_tech(self, tech_level):
        #if Game.tech_first(self.get_objectives_reached()):
        if False:
            station = self.my_stations[0]
            return self.get_best_tech_from_station(tech_level, station)
        else:
            for station in self.my_stations:
                best_station, i = self.get_best_tech_from_station(tech_level, station)
                if best_station is not None:
                    return best_station, i
        return None, None

    def get_energy_core_command_line(self):
        if ("ENERGY_CORE" in self.my_bonuses):
            return 'ENERGY_CORE'
        return None

    def get_tech_research_command_line(self, bonus, tech_level):
        station_id = None
        station, tech_id = self.get_best_station_from_tech(tech_level)
        if station is None or tech_id is None:
            tech_level = 1
            station, tech_id = self.get_best_station_from_tech(tech_level)
        if station is not None:
            if (station.tech[tech_id] > 0):
                return "TECH_RESEARCH {0} {1}".format(station.id, tech_id)
            else:
                return "NEW_TECH {0} {1} {2}".format(station.id, tech_id, bonus)
        return None

    def get_alien_artifact_command_line(self):
        if ("ALIEN_ARTIFACT" in self.my_bonuses):
            tech_id_1 = random.randint(0,3)
            tech_id_2 = random.randint(0,3)
            while (tech_id_2 == tech_id_1):
                tech_id_2 = random.randint(0,3)
            return "ALIEN_ARTIFACT {0} {1}".format(tech_id_1, tech_id_2)
        return None

    def get_best_bonus(self):
        for bonus in self.my_bonuses:
            if bonus not in ["POINTS_1", "POINTS_2", "POINTS_3", "ENERGY_CORE"]:
                return bonus
        return None

    def get_bonus_command_line(self, objectives_reached):
        print("get_bonus_command_line, obj:", objectives_reached, "len bonuses:", len(self.my_bonuses), file=sys.stderr, flush=True)
        if (Game.tech_first(objectives_reached) and len(self.my_bonuses) > 0):
            # If TECH bonus: apply based on objective to TECH_RESEARCH
            # If not TECH bonus: apply based on objective to NEW_TECH
            for bonus in self.my_bonuses:
                if "TECH_RESEARCH" in bonus:
                    command = self.get_tech_research_command_line(bonus, int(bonus[-1]))
                else:
                    command = self.get_tech_research_command_line(bonus, 1)
                if command is not None:
                    return command
        else:
            bonus = self.get_best_bonus()
            if bonus == "TECH_RESEARCH_2":
                return self.get_tech_research_command_line(bonus, 2)
            elif bonus == "TECH_RESEARCH_3":
                return self.get_tech_research_command_line(bonus, 3)
            elif bonus == "TECH_RESEARCH_4":
                return self.get_tech_research_command_line(bonus, 4)
            elif bonus == "ALIEN_ARTIFACT":
                return self.get_tech_research_command_line(bonus, 1)
        return None

    def get_best_preferred_bonus(self, planet, objectives_reached):
        if (not Game.tech_first(objectives_reached)):
            if bonus_ranking_by_points[planet.bonuses[0]] > bonus_ranking_by_points[planet.bonuses[1]]:
                return 0
            else:
                return 1
        else:
            if bonus_ranking_by_tech[planet.bonuses[0]] > bonus_ranking_by_tech[planet.bonuses[1]]:
                return 0
            else:
                return 1


    def get_action(self):
        # main actions: COLONIZE | RESUPPLY
        # bonus actions: ENERGY_CORE | ALIEN_ARTIFACT | TECH_RESEARCH | NEW_TECH

        bonus_command_line = self.get_bonus_command_line(self.get_objectives_reached())
        if bonus_command_line is not None:
            return bonus_command_line
        else:
            combos = []
            for station in self.my_stations:
                if station.available:
                    for planet in self.planets:
                        combos.append(Combo(station, planet, self.get_objectives_reached()))
            combos.sort(key=attrgetter('finish_it', 'planet_bonus_score', 'score', 'planet.colonization_score', 'planet_tasks_sum'), reverse=True)

            for combo in combos:
                if self.should_colonize_planet(combo.planet, combo.station, go_for_it=False):
                    bonus = self.get_best_preferred_bonus(combo.planet, self.get_objectives_reached())
                    return "COLONIZE {0} {1} {2}".format(combo.station.id, combo.planet.id, bonus)

            #for combo in combos:
            #    if self.should_colonize_planet(combo.planet, combo.station, go_for_it=True):
            #        bonus = self.get_best_preferred_bonus(combo.planet, self.get_objectives_reached())
            #        return "COLONIZE {0} {1} {2}".format(combo.station.id, combo.planet.id, bonus)

            energy_core_command_line = self.get_energy_core_command_line()
            if energy_core_command_line is not None:
                return energy_core_command_line
            return 'RESUPPLY'

class StationObjective:
    def __init__(self, id, mine, objective_score, tech_objectives):
        self.id = id
        self.mine = mine
        self.objective_score = objective_score
        self.tech_objectives = tech_objectives

class Station:
    def __init__(self, id, mine, available, tech, objective_score, tech_objectives):
        self.id = id
        self.mine = mine
        self.available = available
        self.tech = tech
        self.tech_objectives = tech_objectives
        self.objective_score = objective_score
        self.remaining_upgrades = 0
        self.set_remaining_upgrades()

    def set_remaining_upgrades(self):
        for i in range(len(self.tech)):
            self.remaining_upgrades += (self.tech_objectives[i] - self.tech[i])

class Planet:
    def __init__(self, planet_id, tasks, my_contribution, opp_contribution, colonization_score, bonuses):
        self.id = planet_id
        self.tasks = tasks
        self.my_contribution = my_contribution
        self.opp_contribution = opp_contribution
        self.colonization_score = colonization_score
        self.bonuses = bonuses
    
    def tasks_remaining(self):
        return self.tasks[0] + self.tasks[1] + self.tasks[2] + self.tasks[3]

    def bonus_score(self, objectives_reached):
        if (not Game.tech_first(objectives_reached)):
            if bonus_ranking_by_points[self.bonuses[0]] > bonus_ranking_by_points[self.bonuses[1]]:
                return bonus_ranking_by_points[self.bonuses[0]]
            else:
                return bonus_ranking_by_points[self.bonuses[1]]
        else:
            if bonus_ranking_by_tech[self.bonuses[0]] > bonus_ranking_by_tech[self.bonuses[1]]:
                return bonus_ranking_by_tech[self.bonuses[0]]
            else:
                return bonus_ranking_by_tech[self.bonuses[1]]

class Combo:
    def __init__(self, station, planet, objectives_reached):
        self.id = id
        self.station = station
        self.planet = planet
        self.score = 0
        self.set_score()
        self.planet_tasks_sum = 16 - self.planet.tasks_remaining()
        self.planet_bonus_score = self.planet.bonus_score(objectives_reached)
        self.finish_it = 0
        self.set_finish_it()
        self.weighted_score = 0
        self.set_weighted_score()

    def set_score(self):
        self.score = 0
        for i in range(4):
            self.score += min(self.planet.tasks[i], self.station.tech[i])
    
    def set_finish_it(self):
        self.finish_it = 0
        can_finish = True
        for i in range(4):
            if (self.planet.tasks[i] > self.station.tech[i]):
                can_finish = False
        if can_finish and self.planet.opp_contribution == 0:
            self.finish_it = 16
            
    def set_weighted_score(self):
        score = 0
        for attribute, weight in weights:
            score += self.__getattribute__(attribute) * weight
        self.weighted_score = score


game = Game()

for i in range(8):
    # objective_score: receive these points if tech level objectives are met
    station_id, mine, objective_score, obj_0, obj_1, obj_2, obj_3 = [int(j) for j in input().split()]
    station_objective = StationObjective(station_id, mine, objective_score, [obj_0, obj_1, obj_2, obj_3])
    game.station_objectives[str(station_id)] = station_objective

# game loop
while True:
    sector_index = int(input())
    game.sector_index = sector_index

    game.my_stations = []
    game.opp_stations = []
    for i in range(8):
        station_id, mine, available, tech_0, tech_1, tech_2, tech_3 = [int(j) for j in input().split()]
        station_objective = game.get_station_objective_by_id(station_id)
        station = Station(station_id, mine, available, [tech_0, tech_1, tech_2, tech_3],
            station_objective.objective_score, station_objective.tech_objectives)
        if mine:
            game.my_stations.append(station)
        else:
            game.opp_stations.append(station)
    
    game.planets = []
    planet_count = int(input())
    for i in range(planet_count):
        inputs = input().split()
        planet_id = int(inputs[0])
        tasks_0 = int(inputs[1])
        tasks_1 = int(inputs[2])
        tasks_2 = int(inputs[3])
        tasks_3 = int(inputs[4])
        my_contribution = int(inputs[5])  # the amount of tasks you have already completed
        opp_contribution = int(inputs[6])
        colonization_score = int(inputs[7])  # points awarded to the colonizer having completed the most tasks
        bonus_0 = inputs[8]
        bonus_1 = inputs[9]
        planet = Planet(planet_id, [tasks_0, tasks_1, tasks_2, tasks_3], my_contribution, opp_contribution, colonization_score, [bonus_0, bonus_1])
        game.planets.append(planet)

    bonus_count = int(input())  # bonuses in both you and your opponent's inventories
    game.my_bonuses = []
    game.opp_bonuses = []
    for i in range(bonus_count):
        inputs = input().split()
        mine = int(inputs[0])
        bonus = inputs[1]
        if mine:
            game.my_bonuses.append(bonus)
        else:
            game.opp_bonuses.append(bonus)
    game.my_colonization_score = int(input())  # points from planet colonization, does not include bonus points
    game.opp_colonization_score = int(input())

    game.reset()

    action = game.get_action()
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)
    print(action)
