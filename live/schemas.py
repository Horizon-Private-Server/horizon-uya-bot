from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Pagination[T](BaseModel):
    count: int
    results: list[T]


class LeaderboardEntry(BaseModel):
    id: int
    username: str
    rank: int
    score: int


class StatOffering(BaseModel):
    domain: str
    stat: str
    label: str
    custom: bool


class DeadlockedStatsBase(BaseModel):
    rank: int
    wins: int
    losses: int
    kills: int
    deaths: int


class DeadlockedOverallStatsSchema(DeadlockedStatsBase):
    games_played: int
    disconnects: int
    squats: int


class DeadlockedDeathmatchStatsSchema(DeadlockedStatsBase):
    pass


class DeadlockedConquestStatsSchema(DeadlockedStatsBase):
    nodes_taken: int


class DeadlockedCTFStatsSchema(DeadlockedStatsBase):
    flags_captured: int


class DeadlockedGameModeWithTimeSchema(DeadlockedStatsBase):
    time: int


class DeadlockedVehicleStatsSchema(BaseModel):
    roadkills: int
    squats: int


class DeadlockedWeaponStatsSchema(BaseModel):
    wrench_kills: int
    wrench_deaths: int
    dual_viper_kills: int
    dual_viper_deaths: int
    magma_cannon_kills: int
    magma_cannon_deaths: int
    arbiter_kills: int
    arbiter_deaths: int
    fusion_rifle_kills: int
    fusion_rifle_deaths: int
    hunter_mine_launcher_kills: int
    hunter_mine_launcher_deaths: int
    b6_obliterator_kills: int
    b6_obliterator_deaths: int
    scorpion_flail_kills: int
    scorpion_flail_deaths: int
    holoshield_launcher_kills: int
    holoshield_launcher_deaths: int


class DeadlockedCustomGamemodeSchema(BaseModel):
    rank: int
    wins: int
    losses: int
    games_played: int
    time_played: int


class DeadlockedCustomCompetitiveGamemodeSchema(DeadlockedCustomGamemodeSchema):
    kills: int
    deaths: int


class DeadlockedHorizonStatsSchema(BaseModel):
    total_bolts: int
    current_bolts: int


class DeadlockedSNDStatsSchema(DeadlockedCustomCompetitiveGamemodeSchema):
    plants: int
    defuses: int
    ninja_defuses: int
    wins_attacking: int
    wins_defending: int


class DeadlockedPayloadStatsSchema(DeadlockedCustomCompetitiveGamemodeSchema):
    points: int
    kills_while_hot: int
    kills_on_hot: int


class DeadlockedSpleefStatsSchema(DeadlockedCustomGamemodeSchema):
    rounds_played: int
    points: int
    boxes_broken: int


class DeadlockedInfectedStatsSchema(DeadlockedCustomCompetitiveGamemodeSchema):
    infections: int
    times_infected: int
    wins_as_survivor: int
    wins_as_first_infected: int


class DeadlockedGungameStatsSchema(DeadlockedCustomCompetitiveGamemodeSchema):
    promotions: int
    demotions: int
    times_demoted: int


class DeadlockedInfiniteClimberStatsSchema(DeadlockedCustomGamemodeSchema):
    high_score: int


class DeadlockedSurvivalStatsSchema(BaseModel):
    rank: int
    games_played: int
    time_played: int
    kills: int
    deaths: int
    revives: int
    times_revived: int
    mystery_box_rolls: int
    demon_bells_activated: int
    times_activated_power: int
    tokens_used_on_gates: int

    wrench_kills: int
    dual_viper_kills: int
    magma_cannon_kills: int
    arbiter_kills: int
    fusion_rifle_kills: int
    hunter_mine_launcher_kills: int
    b6_obliterator_kills: int
    scorpion_flail_kills: int


class DeadlockedSurvivalMapStatsSchema(BaseModel):
    solo_high_score: int
    coop_high_score: int
    xp: int
    prestige: int


class DeadlockedTrainingStatsSchema(BaseModel):
    rank: int
    games_played: int
    time_played: int
    total_kills: int

    fusion_best_points: int
    fusion_best_time: int
    fusion_kills: int
    fusion_hits: int
    fusion_misses: int
    fusion_accuracy: int
    fusion_best_combo: int

    cycle_best_points: int
    cycle_best_combo: int
    cycle_kills: int
    cycle_deaths: int
    cycle_fusion_hits: int
    cycle_fusion_misses: int
    cycle_fusion_accuracy: int


class DeadlockedPlayerDetailsSchema(BaseModel):

    id: int
    username: str

    overall_stats: DeadlockedOverallStatsSchema
    deathmatch_stats: DeadlockedDeathmatchStatsSchema
    conquest_stats: DeadlockedConquestStatsSchema
    ctf_stats: DeadlockedCTFStatsSchema
    koth_stats: DeadlockedGameModeWithTimeSchema
    juggernaut_stats: DeadlockedGameModeWithTimeSchema
    weapon_stats: DeadlockedWeaponStatsSchema
    vehicle_stats: DeadlockedVehicleStatsSchema

    horizon_stats: DeadlockedHorizonStatsSchema
    snd_stats: DeadlockedSNDStatsSchema
    payload_stats: DeadlockedPayloadStatsSchema
    spleef_stats: DeadlockedSpleefStatsSchema
    infected_stats: DeadlockedInfectedStatsSchema
    gungame_stats: DeadlockedGungameStatsSchema
    infinite_climber_stats: DeadlockedInfiniteClimberStatsSchema
    survival_stats: DeadlockedSurvivalStatsSchema
    survival_orxon_stats: DeadlockedSurvivalMapStatsSchema
    survival_mountain_pass_stats: DeadlockedSurvivalMapStatsSchema
    survival_veldin_stats: DeadlockedSurvivalMapStatsSchema
    training_stats: DeadlockedTrainingStatsSchema



class UyaStatsBase(BaseModel):
    rank: int
    wins: int
    losses: int
    wl_ratio: int
    kills: int
    deaths: int
    suicides: int
    kd_ratio: int
    avg_kills: int
    avg_deaths: int
    avg_suicides: int
    games_played: int

class UyaSiegeStatsSchema(UyaStatsBase):
    base_dmg: int
    nodes: int
    avg_nodes: int
    avg_base_dmg: int

class UyaDeathmatchStatsSchema(UyaStatsBase):
    pass

class UyaOverallStatsSchema(UyaStatsBase):
    base_dmg: int
    nodes: int
    avg_nodes: int
    avg_base_dmg: int
    squats: int
    avg_squats: int
    sq_ratio: int
    total_times_squatted: int
    avg_squatted_on: int
    sd_ratio: int
    total_team_squats: int
    avg_team_squats: int

class UyaCTFStatsSchema(UyaStatsBase):
    base_dmg: int
    nodes: int
    flag_captures: int
    flag_saves: int
    avg_nodes: int
    avg_base_dmg: int
    avg_flag_captures: int
    avg_flag_saves: int

class UyaPlayerDetailsSchema(BaseModel):

    id: int
    username: str

    overall_stats: UyaOverallStatsSchema
    deathmatch_stats: UyaDeathmatchStatsSchema
    siege_stats: UyaSiegeStatsSchema
    ctf_stats: UyaCTFStatsSchema


class DeadlockedPlayerOnlineSchema(BaseModel):
    username: str

class UyaPlayerOnlineSchema(BaseModel):
    username: str

class DeadlockedGameOnlineSchema(BaseModel):
    name: str
    game_status: str
    time_started: str
    players: list[DeadlockedPlayerOnlineSchema]
    last_updated: str

class UyaGameOnlineSchema(BaseModel):
    id: int
    name: str
    game_status: str
    time_started: str
    map: str
    time_limit: int
    game_mode: str
    game_type: str
    players: list[UyaPlayerOnlineSchema]
    last_updated: str

class UyaGameHistoryEntry(BaseModel):
    id: int
    status: str
    game_map: str
    game_name: str
    game_mode: str
    game_submode: str
    time_limit: int
    n60_enabled: bool
    lava_gun_enabled: bool
    gravity_bomb_enabled: bool
    flux_rifle_enabled: bool
    mine_glove_enabled: bool
    morph_enabled: bool
    blitz_enabled: bool
    rocket_enabled: bool
    player_count: int

    game_create_time: datetime
    game_start_time: datetime
    game_end_time: datetime
    game_duration: float

class UYALivePlayerUpgrade(BaseModel):
    upgrade: str
    kills: int


class UYALivePlayerUpgrades(BaseModel):
    flux: UYALivePlayerUpgrade
    blitz: UYALivePlayerUpgrade
    grav: UYALivePlayerUpgrade


class UYALivePlayer(BaseModel):
    player_id: int
    account_id: int
    team: str
    username: str
    coord: tuple[float, float, float]
    cam_x: int
    weapon: Optional[str] = None
    upgrades: UYALivePlayerUpgrades
    flag: Optional[str] = None
    health: int
    total_kills: int
    total_deaths: int
    total_suicides: int
    total_flags: int

class UYALiveGameEvent(BaseModel):
    # Define the structure of any events that might appear in the game
    # Placeholder for now as the events array in the provided JSON is empty
    pass


class UYALiveGameSession(BaseModel):
    world_id: int
    world_latest_update: str
    players: list[UYALivePlayer]
    events: list[UYALiveGameEvent]
    map: str
    name: str
    game_mode: str


class UyaGameHistoryPlayerStatSchema(BaseModel):
    game_id: int
    player_id: int
    username: str

    win: bool
    kills: int
    deaths: int
    base_dmg: int
    flag_captures: int
    flag_saves: int
    suicides: int
    nodes: int
    n60_deaths: int
    n60_kills: int
    lava_gun_deaths: int
    lava_gun_kills: int
    gravity_bomb_deaths: int
    gravity_bomb_kills: int
    flux_rifle_deaths: int
    flux_rifle_kills: int
    mine_glove_deaths: int
    mine_glove_kills: int
    morph_deaths: int
    morph_kills: int
    blitz_deaths: int
    blitz_kills: int
    rocket_deaths: int
    rocket_kills: int
    wrench_deaths: int
    wrench_kills: int



class UyaGameHistoryDetailSchema(BaseModel):
    game: UyaGameHistoryEntry
    players: list[UyaGameHistoryPlayerStatSchema]
