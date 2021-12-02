import sys

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

    def get_action(self):
        # main actions: COLONIZE | RESUPPLY
        # bonus actions: ENERGY_CORE | ALIEN_ARTIFACT | TECH_RESEARCH | NEW_TECH
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
