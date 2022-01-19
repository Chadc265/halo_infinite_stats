import datetime
from .game_mode import OddballStats, ZoneStats, FlagStats
ONYX_START = 1500

def get_onyx_sub_tier(csr):
    above_onyx = csr - ONYX_START
    onyx_csr = above_onyx - (above_onyx%50)
    return int((onyx_csr / 50) + 1)

class SummaryStats:
    def __init__(self, data:dict):
        self.kills = data.get('kills', 0)
        self.deaths = data.get('deaths', 0)
        self.assists = data.get('assists', 0)
        self.betrayals = data.get('betrayals', 0)
        self.suicides = data.get('suicides', 0)
        self.medals = data.get('medals', 0)

class DamageStats:
    def __init__(self, data:dict):
        self.damage_taken = data.get('taken', 0)
        self.damage_dealt = data.get('dealt', 0)

class ShotStats:
    def __init__(self, data:dict):
        self.shots_fired = data.get('fired', 0)
        self.shots_landed = data.get('landed', 0)
        self.shots_missed = data.get('missed', 0)
        self.accuracy = data.get('accuracy', 0)

class KillStats:
    def __init__(self, kill_breakdown_data:dict, assist_breakdown_data:dict={}):
        self.melee_kills = kill_breakdown_data.get('melee', 0)
        self.grenade_kills = kill_breakdown_data.get('grenades', 0)
        self.headshots = kill_breakdown_data.get('headshots', 0)
        self.power_weapon_kills = kill_breakdown_data.get('power_weapons', 0)
        self.emp_assists = assist_breakdown_data.get('emp', 0)
        self.callout_assists = assist_breakdown_data.get('callouts', 0)

class TeamMetricStats:
    def __init__(self, player_summary_stats, team:str):
        self.player_kills = [x.summary_stats for x in player_summary_stats if x.team == team]
        self.player_damage = [x.damage_stats for x in player_summary_stats if x.team == team]

    @property
    def total_kda(self):
        return sum([x.kills for x in self.player_kills]), \
               sum([x.deaths for x in self.player_kills]), \
               sum([x.assists for x in self.player_kills])

    @property
    def total_damage_dealt(self):
        return sum([x.damage_dealt for x in self.player_damage])


class PlayerMatchStats:
    def __init__(self, data:dict, match_id:str, gamer_tag=None):
        self.gamer_tag = data.get('gamertag', gamer_tag)
        self.match_id=match_id
        self.team = data.get('team', {}).get('name', 'null').lower()
        self.outcome = data['outcome']
        self.scoreboard_rank = data['rank']
        mode_data = data['stats'].get('mode', None)
        self.mode_stats = None
        if mode_data is not None:
            if 'oddballs' in mode_data:
                self.mode_stats = OddballStats(mode_data)
            elif 'zones' in mode_data:
                self.mode_stats = ZoneStats(mode_data)
            elif 'flags' in mode_data:
                self.mode_stats = FlagStats(mode_data)

        core_data = data['stats'].get('core', {})
        self.summary_stats = SummaryStats(core_data.get('summary', {}))
        self.damage_stats = DamageStats(core_data.get('damage', {}))
        self.shot_stats = ShotStats(core_data.get('shots', {}))

        breakdown_data = core_data.get('breakdowns', {})
        self.kill_stats = KillStats(breakdown_data.get('kills', {}), breakdown_data.get('assists', {}))

        self.kda = core_data.get('kda', 0.0)
        self.kdr = core_data.get('kdr', 0.0)
        self.score = core_data.get('score', 0.0)

        progression_data = data.get('progression', {})
        pre_match_prog, post_match_prog = self._parse_pre_post_progression(progression_data)
        self.before_csr, self.before_rank = self._parse_csr_tier(pre_match_prog)
        self.after_csr, self.after_rank = self._parse_csr_tier(post_match_prog)

        participation_data = data.get('participation', {})
        self.join_time, self.leave_time, self.match_completed = self._parse_participation_data(participation_data)

    @staticmethod
    def _parse_participation_data(participation_data):
        match_completed = participation_data.get('presence', {}).get('completion', None)
        join_time = participation_data.get('joined_at', None)
        leave_time = participation_data.get('left_at', None)
        if join_time is not None:
            join_time = datetime.datetime.fromisoformat(join_time[:-1])

        if leave_time is not None:
            leave_time = datetime.datetime.fromisoformat(leave_time[:-1])

        return join_time, leave_time, match_completed

    @staticmethod
    def _parse_pre_post_progression(progression_data):
        pre_match = {}
        post_match = {}
        if progression_data is not None:
            csr_data = progression_data.get('csr', {})
            pre_match = csr_data.get('pre_match', {})
            post_match = csr_data.get('post_match', {})

        return pre_match, post_match

    @staticmethod
    def _parse_csr_tier(progression_data):
        csr = progression_data.get('value', -1)
        tier = progression_data.get('tier', '')
        sub_tier = progression_data.get('sub_tier', -1)
        if tier != 'Onyx' and tier != '':
            rank = '{0} {1:d}'.format(tier, sub_tier + 1)
            return csr, rank
        elif tier == 'Onyx':
            rank = 'Onyx {0:d}'.format(get_onyx_sub_tier(csr))
            return csr, rank
        else:
            return csr, 'null'

    def to_dict(self, include_mode=False):
        low_dict = {
            'gamer_tag': self.gamer_tag,
            'player_match_id': self.match_id,
            'team': self.team,
            'outcome': self.outcome,
            'scoreboard_rank': self.scoreboard_rank,
            'kda': self.kda,
            'kdr': self.kdr,
            'score': self.score,
            'before_csr': self.before_csr,
            'before_rank': self.before_rank,
            'after_csr': self.after_csr,
            'after_rank': self.after_rank,
            'match_completed': self.match_completed
        }
        if include_mode:
            mode_dict = vars(self.mode_stats) if self.mode_stats is not None else {}
            return {**low_dict,
                    **vars(self.summary_stats),
                    **vars(self.damage_stats),
                    **vars(self.shot_stats),
                    **vars(self.kill_stats),
                    **mode_dict}
        else:
            return {**low_dict,
                    **vars(self.summary_stats),
                    **vars(self.damage_stats),
                    **vars(self.shot_stats),
                    **vars(self.kill_stats)}

class PlayerCSRData:
    def __init__(self, player_stats:PlayerMatchStats):
        self.before_csr = player_stats.before_csr
        self.after_csr = player_stats.after_csr
        self.match_completed = player_stats.match_completed
        self.team = player_stats.team

class TeamCSRData:
    def __init__(self, player_csrs:list, team:str):
        self.player_csrs = [x for x in player_csrs if x.team == team]

    @property
    def csrs_reported(self) -> int:
        return len([x for x in self.player_csrs if (x.before_csr >= 0 and x.after_csr >= 0)])

    @property
    def csrs_completed(self) -> int:
        return len([x for x in self.player_csrs if x.match_completed])

    @property
    def before_csr_stats(self):
        befores = [x.before_csr for x in self.player_csrs if x.before_csr >= 0]
        if len(befores) > 0:
            return sum(befores) / len(befores), min(befores), max(befores)
        else:
            return -1, -1, -1

    @property
    def after_csr_stats(self):
        afters = [x.after_csr for x in self.player_csrs if x.after_csr >= 0]
        if len(afters) > 0:
            return sum(afters) / len(afters), min(afters), max(afters)
        return -1, -1, -1