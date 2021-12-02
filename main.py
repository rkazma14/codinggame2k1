import sys
import random
from operator import attrgetter

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
        self.my_stations.sort(key=attrgetter('objective_score'), reverse=True)

    def get_station_objective_by_id(self, station_id):
        return (station_objective for station_objective in self.station_objectives if station_objective.id == station_id)

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

    def should_colonize_planet(self, planet, station):
        return self.is_planet_not_already_lost(planet) and self.can_use_station_techs_on_planet(planet, station)

    def get_best_planet(self, station):
        return self.get_first_valid_planet(station)

    def get_best_station_from_tech(self, tech_level):
        for station in self.my_stations:
            station_objective = self.get_station_objective_by_id(station.id)
            for i in range(len(station.tech)):
                if (station.tech[i] + 1 == tech_level) and (station.tech[i] < station_objective.tech_objectives[i]):
                    return station, i
        return None, None

    def get_energy_core_command_line(self):
        return 'ENERGY_CORE'

    def get_tech_research_command_line(self, tech_level):
        station_id = None
        station, tech_id = self.get_best_station_from_tech(tech_level)
        if station is None or tech_id is None:
            station_id = random.randint(0,3)
            tech_id = random.randint(0,3)
        else:
            station_id = station.id
        if (self.my_stations[station_id].tech[tech_id] > 0):
            if (self.my_stations[station_id].tech[tech_id] + 1 == tech_level):
                return "TECH_RESEARCH {0} {1}".format(self.my_stations[station_id].id, tech_id)
        else:
            return "NEW_TECH {0} {1} {2}{3}".format(self.my_stations[station_id].id, tech_id, 'TECH_RESEARCH_', tech_level)
        return None

    def get_alien_artifact_command_line(self):
        return None

    def get_best_bonus(self):
        for bonus in self.my_bonuses:
            if bonus not in ["POINTS_1", "POINTS_2", "POINTS_3"]:
                return bonus
        return None

    def get_bonus_command_line(self):
        bonus = self.get_best_bonus()
        if bonus == "ENERGY_CORE":
            return self.get_energy_core_command_line()
        elif bonus == "TECH_RESEARCH_2":
            return self.get_tech_research_command_line(2)
        elif bonus == "TECH_RESEARCH_3":
            return self.get_tech_research_command_line(3)
        elif bonus == "TECH_RESEARCH_4":
            return self.get_tech_research_command_line(4)
        elif bonus == "ALIEN_ARTIFACT":
            return self.get_alien_artifact_command_line()
        return None

    bonus_ranking = {"POINTS_3": 0,\
                     "ENERGY_CORE": 1,\
                     "POINTS_2": 2,
                     "TECH_RESEARCH_2": 3,\
                     "ALIEN_ARTIFACT": 4,\
                     "POINTS_1": 5,\
                     "TECH_RESEARCH_3": 6,\
                     "TECH_RESEARCH_4": 7}

    def get_best_preferred_bonus(self, planet):
        if self.bonus_ranking[planet.bonuses[0]] > self.bonus_ranking[planet.bonuses[1]]:
            return 1
        else:
            return 0


    def get_action(self):
        # main actions: COLONIZE | RESUPPLY
        # bonus actions: ENERGY_CORE | ALIEN_ARTIFACT | TECH_RESEARCH | NEW_TECH

        bonus_command_line = self.get_bonus_command_line()
        if bonus_command_line is not None:
            return bonus_command_line
        else:
            combos = []
            for station in self.my_stations:
                if station.available:
                    for planet in self.planets:
                        combos.append(Combo(station, planet))
            combos.sort(key=attrgetter('score', 'planet.colonization_score', 'planet_tasks_sum'), reverse=True)

            for combo in combos:
                print(combo.score, file=sys.stderr, flush=True)
                if self.should_colonize_planet(combo.planet, combo.station):
                    bonus = self.get_best_preferred_bonus(combo.planet)
                    return "COLONIZE {0} {1} {2}".format(combo.station.id, combo.planet.id, bonus)
            return 'RESUPPLY'

class StationObjective:
    def __init__(self, id, mine, objective_score, tech_objectives):
        self.id = id
        self.mine = mine
        self.objective_score = objective_score
        self.tech_objectives = tech_objectives

class Station:
    def __init__(self, id, mine, available, tech, objective_score):
        self.id = id
        self.mine = mine
        self.available = available
        self.tech = tech
        self.objective_score = objective_score

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

class Combo:
    def __init__(self, station, planet):
        self.id = id
        self.station = station
        self.planet = planet
        self.score = 0
        self.set_score()
        self.planet_tasks_sum = 16 - self.planet.tasks_remaining()

    def set_score(self):
        self.score = 0
        for i in range(4):
            self.score += min(self.planet.tasks[i], self.station.tech[i])

game = Game()

for i in range(8):
    # objective_score: receive these points if tech level objectives are met
    station_id, mine, objective_score, obj_0, obj_1, obj_2, obj_3 = [int(j) for j in input().split()]
    station_objective = StationObjective(station_id, mine, objective_score, [obj_0, obj_1, obj_2, obj_3])
    game.station_objectives[id] = station_objective

# game loop
while True:
    sector_index = int(input())
    game.sector_index = sector_index

    game.my_stations = []
    game.opp_stations = []
    for i in range(8):
        station_id, mine, available, tech_0, tech_1, tech_2, tech_3 = [int(j) for j in input().split()]
        station = Station(station_id, mine, available, [tech_0, tech_1, tech_2, tech_3], game.get_station_objective_by_id(station_id).objective_score)
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
