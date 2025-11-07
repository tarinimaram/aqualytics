class Player:
    def __init__(self, name, number) -> None:
        self.name = name
        self.number = number
        self.game_stats = [] # list of PlayerGameStat

    def fillGameStats():
        pass
    
    def getAvgStats():
        pass

class PlayerGameStat:
    def __init__(self, name, number, shots, goals, blocks, rebounds, assists, steals, turnovers, hustles, exclusions, tipped_passes) -> None:
        self.name = name
        self.number = number
        #some identifier for game (opponent, location, date, arbitrary id)
        self.shots = shots
        self.goals = goals
        self.blocks = blocks
        self.rebounds = rebounds
        self.assists = assists
        self.steals = steals
        self.turnovers = turnovers
        self.hustles = hustles
        self.exclusions = exclusions
        self.tipped_passes = tipped_passes



