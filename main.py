import sys
import random

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

    def get_first_active(self):
        for station in self.my_stations:
            if station.available:
                return station
        return None

    def get_first_non_colonized_planet(self, station):
        for planet in self.planets:
            fine = False
            for i in range(len(planet.tasks)):
                if planet.tasks[i] > 0 and station.tech[i] > 0:
                    fine = True
            if fine:
                return planet
        return self.planets[0]

    def get_best_station(self):
        return self.get_first_active()

    def get_best_planet(self, station):
        return self.get_first_non_colonized_planet(station)

    def get_energy_core_command_line(self):
        return 'ENERGY_CORE'

    def get_tech_research_command_line(self, tech_level):
        station_id = random.randint(0,3)
        tech_id = random.randint(0,3)
        if (self.my_stations[station_id].tech[tech_id] > 0):
            if (self.my_stations[station_id].tech[tech_id] < tech_level):
                return "TECH_RESEARCH {0} {1}".format(station_id, tech_id)
        else:
            return "NEW_TECH {0} {1} {2}{3}".format(station_id, tech_id, 'TECH_RESEARCH_', tech_level)
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

    def get_action(self):
        # main actions: COLONIZE | RESUPPLY
        # bonus actions: ENERGY_CORE | ALIEN_ARTIFACT | TECH_RESEARCH | NEW_TECH

        bonus_command_line = self.get_bonus_command_line()
        if bonus_command_line is not None:
            return bonus_command_line
        else:
            station = self.get_best_station()
            if station is not None:
                planet = self.get_best_planet(station)
                return "COLONIZE {0} {1} {2}".format(station.id, planet.id, 0)
            else:
                return 'RESUPPLY'

class StationObjective:
    def __init__(self, id, mine, objective_score, tech_objectives):
        self.id = id
        self.mine = mine
        self.objective_score = objective_score
        self.tech_objectives = tech_objectives

class Station:
    def __init__(self, id, mine, available, tech):
        self.id = id
        self.mine = mine
        self.available = available
        self.tech = tech

class Planet:
    def __init__(self, planet_id, tasks, my_contribution, opp_contribution, colonization_score, bonuses):
        self.id = planet_id
        self.tasks = tasks
        self.my_contribution = my_contribution
        self.opp_contribution = opp_contribution
        self.colonization_score = colonization_score
        self.bonuses = bonuses

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
        station = Station(station_id, mine, available, [tech_0, tech_1, tech_2, tech_3])
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

    action = game.get_action()
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)
    print(action)
