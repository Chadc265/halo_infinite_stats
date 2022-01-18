import datetime
from .player import PlayerMatchStats

class PlaylistData:
    def __init__(self, data:dict):
        self.name = data.get('name', None)
        self.queue = data.get('properties', {}).get('queue', None)
        self.input = data.get('properties', {}).get('input', None)
        self.ranked = data.get('properties', {}).get('ranked', None)
        self.id = data.get('asset', {}).get('id', None)
        self.version = data.get('asset', {}).get('version', None)

class MatchListResult:
    def __init__(self, json_response):
        self.matches = json_response['data']
        self.count = json_response['count']
        self.gamer_tag = json_response['additional']['gamertag']
        self.offset = json_response['paging']['offset']


class Match:
    def __init__(self, data:dict, gamer_tag:str=None):
        self.id = data.get('id', None)
        details = data.get('details', {})
        self.mode = details.get('category', {}).get('name', None)
        self.map = details.get('map', {}).get('name', None)
        self.date_time = datetime.datetime.fromisoformat(data.get('played_at', '1970-01-01T00:00:00.000Z')[:-1])
        self.duration_seconds = data.get('duration', {}).get('seconds', 0)

        self.playlist = PlaylistData(details.get('playlist', {}))

        self.players = self._parse_players(data, gamer_tag=gamer_tag)

    def _parse_players(self, data, gamer_tag=None):
        player_data = data.get('player', data.get('players', None))
        player_list = []
        if player_data is not None:
            if isinstance(player_data, list):
                for player in player_data:
                    player_obj = PlayerMatchStats(player, self.id)
                    player_list.append(player_obj)
            else:
                player_list.append(PlayerMatchStats(player_data, self.id, gamer_tag=gamer_tag))
        return player_list

    def get_info_dict(self):
        """
        Returns dict with basic information on the match
        Includes "match_id", "mode", "map", "queue", "input", "ranked", "date_time", "match_duration"
        """
        low_dict = {
            'match_id': self.id,
            'mode': self.mode,
            'map': self.map,
            'queue': self.playlist.queue,
            'input': self.playlist.input,
            'ranked': self.playlist.ranked,
            'date_time': self.date_time,
            'match_duration': self.duration_seconds,
        }
        return {**low_dict}

    def to_dict(self):
        """
        Returns list of dictionaries with info_dict and a single player in each
        """
        info_dict = self.get_info_dict()
        ret = []
        for p in self.players:
            ret.append({**info_dict, **p.to_dict()})
        return ret


