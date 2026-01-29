from peewee import *
from datetime import datetime
from typing import List, Dict

# Database connection
db = PostgresqlDatabase(
    'waterpolo_analytics',
    user='your_username',
    password='your_password',
    host='localhost',
    port=5432
)

class BaseModel(Model):
    """Base model with common fields and database connection"""
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    class Meta:
        database = db
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)


class Team(BaseModel):
    """Represents a water polo team"""
    name = CharField(unique=True)
    coach_name = CharField(null=True)
    division = CharField(null=True)
    season = CharField(null=True)
    
    class Meta:
        indexes = (
            (('name', 'season'), True),  # Unique constraint
        )


class Player(BaseModel):
    """Represents a water polo player"""
    team = ForeignKeyField(Team, backref='players', on_delete='CASCADE')
    first_name = CharField()
    last_name = CharField()
    jersey_number = IntegerField()
    position = CharField()  # e.g., 'Center', 'Wing', 'Driver', 'Goalie', 'Flat'
    is_active = BooleanField(default=True)
    
    class Meta:
        indexes = (
            (('team', 'jersey_number'), True),  # Unique per team
        )


class Match(BaseModel):
    """Represents a water polo match"""
    home_team = ForeignKeyField(Team, backref='home_matches')
    away_team = ForeignKeyField(Team, backref='away_matches')
    match_date = DateTimeField()
    location = CharField(null=True)
    home_score = IntegerField()
    away_score = IntegerField()
    quarter_scores = JSONField(null=True)  # Store quarter-by-quarter scores
    match_type = CharField()  # 'Regular', 'Playoff', 'Tournament', 'Scrimmage'
    notes = TextField(null=True)


class PlayerMatchStats(BaseModel):
    """Statistics for a player in a specific match"""
    player = ForeignKeyField(Player, backref='match_stats')
    match = ForeignKeyField(Match, backref='player_stats', on_delete='CASCADE')
    
    # Offensive stats
    shots_attempted = IntegerField(default=0)
    goals = IntegerField(default=0)
    assists = IntegerField(default=0)
    turnovers = IntegerField(default=0)
    
    # Defensive stats
    steals = IntegerField(default=0)
    blocks = IntegerField(default=0)
    rebounds = IntegerField(default=0)
    
    # Fouls
    fouls_committed = IntegerField(default=0)
    fouls_drawn = IntegerField(default=0)
    exclusions = IntegerField(default=0)  # Kicked out of game
    
    # Special situations
    power_play_goals = IntegerField(default=0)
    power_play_attempts = IntegerField(default=0)
    penalty_shots_made = IntegerField(default=0)
    penalty_shots_attempted = IntegerField(default=0)
    
    # Goalie-specific stats (null for non-goalies)
    saves = IntegerField(null=True)
    goals_allowed = IntegerField(null=True)
    
    # Time
    minutes_played = DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        indexes = (
            (('player', 'match'), True),  # One stat entry per player per match
        )
    
    @property
    def shot_percentage(self):
        if self.shots_attempted == 0:
            return 0
        return (self.goals / self.shots_attempted) * 100
    
    @property
    def save_percentage(self):
        if self.saves is None or self.goals_allowed is None:
            return None
        total_shots = self.saves + self.goals_allowed
        if total_shots == 0:
            return 0
        return (self.saves / total_shots) * 100


class Play(BaseModel):
    """Represents a strategic play or tactic"""
    name = CharField()
    description = TextField(null=True)
    play_type = CharField()  # 'Offensive', 'Defensive', 'Special Teams'
    formation = CharField(null=True)  # e.g., '3-3', '4-2', 'Press'
    team = ForeignKeyField(Team, backref='plays', null=True)  # null if generic play
    diagram_url = CharField(null=True)  # Optional link to play diagram
    
    class Meta:
        indexes = (
            (('name', 'team'), False),
        )


class MatchPlay(BaseModel):
    """Tracks which plays were used in a match and their effectiveness"""
    match = ForeignKeyField(Match, backref='plays_used', on_delete='CASCADE')
    play = ForeignKeyField(Play, backref='match_usage')
    team = ForeignKeyField(Team, backref='match_plays')  # Which team executed it
    quarter = IntegerField()  # Which quarter (1-4, or 5+ for overtime)
    times_used = IntegerField(default=1)
    successful_executions = IntegerField(default=0)  # How many times it resulted in goal/stop
    notes = TextField(null=True)


class Action(BaseModel):
    """Detailed log of every action during a match (for advanced analysis)"""
    match = ForeignKeyField(Match, backref='actions', on_delete='CASCADE')
    player = ForeignKeyField(Player, backref='actions', null=True)
    team = ForeignKeyField(Team, backref='actions')
    
    action_type = CharField()  # 'Shot', 'Goal', 'Pass', 'Steal', 'Block', 'Foul', etc.
    timestamp = TimeField()  # Time in match (e.g., 'Q2 3:45')
    quarter = IntegerField()
    
    # Context
    location_x = DecimalField(max_digits=5, decimal_places=2, null=True)  # Position on pool
    location_y = DecimalField(max_digits=5, decimal_places=2, null=True)
    result = CharField(null=True)  # 'Success', 'Fail', 'Blocked', etc.
    
    # Related entities
    assist_player = ForeignKeyField(Player, backref='assists_given', null=True)
    related_play = ForeignKeyField(Play, backref='actions', null=True)
    
    # Additional context
    is_power_play = BooleanField(default=False)
    is_counter_attack = BooleanField(default=False)
    notes = TextField(null=True)


class OpponentProfile(BaseModel):
    """Profile of opponent teams for strategic analysis"""
    team = ForeignKeyField(Team, backref='opponent_profiles', unique=True)
    
    # Tendencies
    avg_goals_per_game = DecimalField(max_digits=5, decimal_places=2, null=True)
    avg_goals_allowed = DecimalField(max_digits=5, decimal_places=2, null=True)
    common_formations = JSONField(null=True)  # List of common formations
    common_plays = JSONField(null=True)  # List of play IDs they frequently use
    
    # Strengths and weaknesses
    strengths = TextField(null=True)
    weaknesses = TextField(null=True)
    key_players = JSONField(null=True)  # List of player IDs
    
    # Analysis metadata
    matches_analyzed = IntegerField(default=0)
    last_analysis_date = DateTimeField(null=True)


# Helper functions for common queries
class QueryHelpers:
    """Helper class for common database queries"""
    
    @staticmethod
    def get_player_season_averages(player: Player, season: str = None):
        """Calculate season averages for a player"""
        query = (PlayerMatchStats
                .select()
                .join(Match)
                .where(PlayerMatchStats.player == player))
        
        if season:
            query = query.where(Match.match_date.year == season)
        
        stats = list(query)
        if not stats:
            return None
        
        total_games = len(stats)
        return {
            'games_played': total_games,
            'avg_goals': sum(s.goals for s in stats) / total_games,
            'avg_shots': sum(s.shots_attempted for s in stats) / total_games,
            'avg_assists': sum(s.assists for s in stats) / total_games,
            'avg_steals': sum(s.steals for s in stats) / total_games,
            'avg_blocks': sum(s.blocks for s in stats) / total_games,
            'shot_percentage': (sum(s.goals for s in stats) / 
                              sum(s.shots_attempted for s in stats) * 100 
                              if sum(s.shots_attempted for s in stats) > 0 else 0),
        }
    
    @staticmethod
    def rank_players_by_stat(team: Team, stat: str, min_games: int = 3):
        """Rank players by a specific statistic"""
        players = (Player
                  .select(Player, fn.AVG(getattr(PlayerMatchStats, stat)).alias('avg_stat'),
                         fn.COUNT(PlayerMatchStats.id).alias('games'))
                  .join(PlayerMatchStats)
                  .where(Player.team == team)
                  .group_by(Player)
                  .having(fn.COUNT(PlayerMatchStats.id) >= min_games)
                  .order_by(SQL('avg_stat').desc()))
        
        return list(players)
    
    @staticmethod
    def get_team_vs_opponent_history(team: Team, opponent: Team):
        """Get historical matchup data between two teams"""
        matches = (Match
                  .select()
                  .where(
                      ((Match.home_team == team) & (Match.away_team == opponent)) |
                      ((Match.home_team == opponent) & (Match.away_team == team))
                  )
                  .order_by(Match.match_date.desc()))
        
        return list(matches)
    
    @staticmethod
    def get_play_effectiveness(play: Play, team: Team = None):
        """Calculate effectiveness of a play"""
        query = MatchPlay.select().where(MatchPlay.play == play)
        if team:
            query = query.where(MatchPlay.team == team)
        
        usages = list(query)
        if not usages:
            return None
        
        total_uses = sum(u.times_used for u in usages)
        total_success = sum(u.successful_executions for u in usages)
        
        return {
            'total_uses': total_uses,
            'success_rate': (total_success / total_uses * 100) if total_uses > 0 else 0,
            'matches_used': len(usages)
        }


# Database initialization
def initialize_database():
    """Create all tables in the database"""
    db.connect()
    db.create_tables([
        Team, Player, Match, PlayerMatchStats, Play, 
        MatchPlay, Action, OpponentProfile
    ])
    print("Database tables created successfully!")


def close_database():
    """Close database connection"""
    if not db.is_closed():
        db.close()


# Example usage
if __name__ == '__main__':
    # Initialize database
    initialize_database()
    
    # Example: Create a team
    team = Team.create(
        name="Neptune Warriors",
        coach_name="Coach Smith",
        division="Division 1",
        season="2024-25"
    )
    
    # Example: Add a player
    player = Player.create(
        team=team,
        first_name="John",
        last_name="Doe",
        jersey_number=7,
        position="Center"
    )
    
    print(f"Created team: {team.name}")
    print(f"Created player: {player.first_name} {player.last_name}")
    
    # Example: Get player averages
    averages = QueryHelpers.get_player_season_averages(player)
    if averages:
        print(f"Season averages: {averages}")
    
    close_database()