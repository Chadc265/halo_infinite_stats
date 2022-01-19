class ZoneStats:
    def __init__(self, zones_data:dict):
        self.zones_secured = zones_data.get('secured', 0)
        self.zones_captured = zones_data.get('captured', 0)
        self.occupation_time = zones_data.get('occupation', {}).get('duration', {}).get('seconds', 0)
        zone_kills = zones_data.get('kills', {})
        self.defensive_kills = zone_kills.get('defensive', 0)
        self.offensive_kills = zone_kills.get('offensive', 0)

class FlagStats:
    def __init__(self, flags_data:dict):
        self.flag_grabs = flags_data.get('grabs', 0)
        self.flag_steals = flags_data.get('grabs', 0)
        self.flag_secures = flags_data.get('grabs', 0)
        self.flag_returns = flags_data.get('grabs', 0)
        self.flag_possession = flags_data.get('possession', {}).get('duration', {}).get('seconds', 0)

        capture_data = flags_data.get('captures', {})
        self.flag_captures = capture_data.get('total', 0)
        self.flag_assists = capture_data.get('assists', 0)

        flag_kills = flags_data.get('kills', {})
        self.flag_carrier_kills = flag_kills.get('carriers', 0)
        self.flag_returner_kills = flag_kills.get('returners', 0)
        self.kills_as_flag_carrier = flag_kills.get('as', {}).get('carrier', 0)
        self.kills_as_flag_returner = flag_kills.get('as', {}).get('returner', 0)

class OddballStats:
    def __init__(self, oddballs_stats:dict):
        self.ball_grabs = oddballs_stats.get('grabs', 0)
        self.ball_controls = oddballs_stats.get('controls', 0)

        possession_data = oddballs_stats.get('possession', {})
        self.ball_hold_ticks, \
        self.longest_ball_time, \
        self.total_ball_time = self._parse_possession_data(possession_data)

        self.ball_carriers_killed = oddballs_stats.get('kills', {}).get('carriers', 0)
        self.kills_as_ball_carrier = oddballs_stats.get('kills', {}).get('as', {}).get('carrier', 0)

    @staticmethod
    def _parse_possession_data(possession_data:dict):
        ticks = possession_data.get('ticks', 0)
        durations = possession_data.get('durations', {})
        longest_hold = durations.get('longest', {}).get('seconds', 0)
        total_hold_time = durations.get('total', {}).get('seconds', 0)
        return ticks, longest_hold, total_hold_time