import requests

__all__ = [
    "get_single_match_json",
    "get_match_list_json",
    "get_pvp_matches_played"
]

API_VERSION = "0.3.9"


def get_single_match_json(match_id:str, token:str):
    url = f'https://halo.api.stdlib.com/infinite@{API_VERSION}/stats/matches/retrieve/?id={match_id}'
    headers = {f'Authorization': 'Bearer ' + token}
    r = requests.get(url, headers=headers)
    return r.json()

def get_match_list_json(gamer_tag:str, token:str, count:int=25, offset:int=1):
    url = f'https://halo.api.stdlib.com/infinite@{API_VERSION}/stats/matches/list/?gamertag={gamer_tag}&limit.count={count}&limit.offset={offset}&mode=matchmade'
    headers = {f'Authorization': 'Bearer ' + token}
    r = requests.get(url, headers=headers)
    return r.json()

def get_pvp_matches_played(gamer_tag:str, token:str):
    url = f'https://halo.api.stdlib.com/infinite@{API_VERSION}/stats/service-record/multiplayer/?gamertag={gamer_tag}&filter=matchmade:pvp'
    headers = {f'Authorization': 'Bearer ' + token}

    r = requests.get(url, headers=headers)
    result = r.json()
    return result['data'].get('matches_played', None)
