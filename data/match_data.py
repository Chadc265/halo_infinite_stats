from .api_calls import get_match_list_json, get_single_match_json, \
    get_pvp_matches_played
from classes import MatchListResult, Match
from tqdm import tqdm
import numpy as np

__all__ = [
    "get_match_id_list",
    "get_offset_array",
    "get_single_player_matches",
    "get_specified_matches",
    "matches_to_dict_list"
]

def get_offset_array(api_token, gamertag, number_matches = -1):
    matches_played = number_matches
    if matches_played < 0:
        matches_played = get_pvp_matches_played(gamertag, api_token)
    matches_played = max(matches_played, 25)
    nice_round_max_matches = 25 * round(matches_played / 25)
    offset_list = np.arange(0,nice_round_max_matches, 25)
    return offset_list

def get_match_id_list(offset_list, api_token, gamertag) -> list[str]:
    ret = []
    for o in tqdm(offset_list, desc='match ids', unit='batch'):
        match_list = get_match_list_json(gamertag, offset=int(o), token=api_token)
        match_list_obj = MatchListResult(match_list)
        for match in match_list_obj.matches:
            match_id = match.get('id', None)
            if not match_id in ret:
                ret.append(match_id)
    return ret

def get_single_player_matches(offset_list, api_token, gamertag) -> list[Match]:
    match_list = []
    for o in tqdm(offset_list, desc='{} stats'.format(gamertag)):
        result = get_match_list_json(gamertag, offset=int(o), token=api_token)
        match_list_obj = MatchListResult(result)
        for match in match_list_obj.matches:
            match_obj = Match(match, match_list_obj.gamer_tag)
            if not any([match_obj.id == x.id for x in match_list]):
                match_list.append(match_obj)
    return match_list

def get_specified_matches(
        match_id_list,
        api_token,
        ignore_match_gamertags=None) -> list[Match]:

    match_list = []
    for mid in tqdm(match_id_list, desc='match list', unit='match'):
        match_result = get_single_match_json(mid, api_token)
        match_obj = Match(match_result['data'])
        if len(ignore_match_gamertags) > 0:
            match_names = [x.gamer_tag for x in match_obj.players]
            if any([x in match_names for x in ignore_match_gamertags]):
                continue
        match_list.append(match_obj)
    return match_list

def matches_to_dict_list(match_list: list[Match]) -> list[dict]:
    dict_list = []
    for m in match_list:
        dict_list.extend(m.to_dict())
    return dict_list