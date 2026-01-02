from enum import Enum
class Player:
    def __init__(self, name, number) -> None:
        self.name = name
        self.number = number
        self.game_stats = [] # list of PlayerGameStat

    def fillGameStats():
        pass
    
    def getAvgStats():
        pass

# class PlayerGameStat:
#     def __init__(self, name, number, shots, goals, blocks, rebounds, assists, steals, turnovers, hustles, exclusions, tipped_passes) -> None:
#         self.name = name
#         self.number = number
#         #some identifier for game (opponent, location, date, arbitrary id)
#         self.shots = shots
#         self.goals = goals
#         self.blocks = blocks
#         self.rebounds = rebounds
#         self.assists = assists
#         self.steals = steals
#         self.turnovers = turnovers
#         self.hustles = hustles
#         self.exclusions = exclusions
#         self.tipped_passes = tipped_passes

class Game: 
    def __init__(self, id, date, home_team, visitor_team, actions, plays):
        self.home = home_team 
        self.visitor = visitor_team
        self.date = date
        self.id = id
        self.actions = actions
        self.plays = plays

class Play:
    def __init__(self, play_name, player_ids, timestamp, success):
        self.play_name = play_name
        self.players = player_ids
        self.timestamp = timestamp
        self.success = success # boolean T/F

class Team:
    def __init__(self, name, Players, Games):
        self.name = name
        self.players = Players
        self.games = Games

class Action: 
    def __init__(self, player_id, timestamp, action_name):
        self.player = player_id
        self.timestamp = timestamp
        self.action = action_name # list of ActionType

class ActionType(Enum):
    SHOT_MISS = 1
    SHOT_GOAL = 2
    BLOCK = 3
    REBOUND = 4
    ASSIST = 5
    STEAL = 6
    TURNOVER = 7
    HUSTLE = 8
    EXCLUSION = 9
    TIPPED_PASS = 10
