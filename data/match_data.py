from .api_calls import get_match_list_json, get_single_match_json, \
    get_pvp_matches_played
from classes import MatchListResult, Match
from tqdm import tqdm
import numpy as np
import pandas as pd
import json
import os
from typing import List

__all__ = [
    "get_match_id_list",
    "get_offset_array",
    "get_single_player_matches",
    "get_specified_matches",
    "matches_to_dict_list",
    "get_match_id_list_auto"
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

def get_match_id_list_auto(offset_list, api_token, gamertag, json_dir) -> List[str]:
    stored_files = os.listdir(json_dir)
    ret = []
    ready_to_bail = False
    for o in tqdm(offset_list, desc='match ids', unit='batch'):
        match_list = get_match_list_json(gamertag, offset=int(o), token=api_token)
        match_list_obj = MatchListResult(match_list)
        for match in match_list_obj.matches:
            match_id = match.get('id', None)
            if not match_id in ret:
                if not any([match_id in f for f in stored_files]):
                    ret.append(match_id)
                else:
                    ready_to_bail = True
        if ready_to_bail:
            return ret
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
        ignore_match_gamertags=[],
        save_json_dir:str=None) -> list[Match]:

    match_list = []
    for mid in tqdm(match_id_list, desc='match list', unit='match'):
        match_result = get_single_match_json(mid, api_token)

        if save_json_dir is not None:
            with open(save_json_dir + mid + '.json', 'w') as f:
                json.dump(match_result, f)

        match_obj = Match(match_result['data'])
        if len(ignore_match_gamertags) > 0:
            match_names = [x.gamer_tag for x in match_obj.players]
            if any([x in match_names for x in ignore_match_gamertags]):
                continue
        match_list.append(match_obj)
    return match_list

def matches_to_dict_list(match_list: list[Match], include_mode:bool=False) -> list[dict]:
    dict_list = []
    for m in match_list:
        dict_list.extend(m.to_dict(include_mode))
    return dict_list

def preprocess_dataframe(df: pd.DataFrame, known_teammates:List[str]) -> pd.DataFrame:
    df['date_time'] = pd.to_datetime(df['date_time'])
    df = df.sort_values(by='date_time')
    df['date'] = df['date_time'].dt.date
    df['damage_ratio'] = df['damage_dealt'] / df['damage_taken']
    df['csr_change'] = df['after_csr'] - df['before_csr']
    df['csr_diff_from_team_mmr'] = df['before_csr'] - df['team_mmr']
    df['known_teammate'] = df['gamer_tag'].isin(known_teammates)


    gb = df.groupby('match_id')
    df['solo'] = gb['known_teammate'].transform('any')
    df['full_lobby'] = gb['outcome'].transform(lambda x: 'left' not in x.tolist())
    df['lobby_csr_mean'] = gb['before_csr'].transform('mean')
    df['csr_lobby_rank'] = gb['before_csr'].rank('dense', ascending=False)
    df['kda_lobby_rank'] = gb['kda'].rank('dense', ascending=False)
    df['damage_ratio_lobby_rank'] = gb['damage_ratio'].rank('dense', ascending=False)
    df['csr_diff_from_lobby_mean'] = df['before_csr'] - df['lobby_csr_mean']


    team_grouped = df.groupby(['match_id', 'team'])
    df['damage_ratio_team_rank'] = team_grouped['damage_ratio'].rank('dense', ascending=False)
    df['kda_team_rank'] = team_grouped['kda'].rank('dense', ascending=False)
    df['score_team_rank'] = team_grouped['score'].rank('dense', ascending=False)
    df['csr_team_rank'] = team_grouped['before_csr'].rank('dense', ascending=False)
    df['csr_diff_from_team_mean'] = df['before_csr'] - team_grouped['before_csr'].transform('mean')

    temp = pd.get_dummies(df['outcome'])
    df['win'] = temp['win']
    df['loss'] = temp['loss']
    return df