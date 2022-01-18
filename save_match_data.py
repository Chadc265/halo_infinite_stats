import argparse
import sys
import pandas as pd
from data import get_api_token, get_offset_array, \
    get_match_id_list, get_specified_matches, \
    matches_to_dict_list, get_output_directory, \
    get_known_teammates, get_single_player_matches


CONFIG_PATH = "C:/Repo/python_config.ini"

def parse_args(args):
    parser = argparse.ArgumentParser(description="Save pvp match statistics from Halo API. 25 matches will be \
    returned if less are requested.")
    parser.add_argument("gamertag",
                        type=str,
                        help="Required and case sensative")
    parser.add_argument("number_matches",
                        type=int,
                        default=-1,
                        help="Number of matchmade pvp matches to pull starting with most recent. defaults to '-1' \
                        which will pull all available matchmade pvp matches")
    parser.add_argument("filename",
                        type=str,
                        help="Output filename to store csv data. Directory is chosen by your python_config.ini")
    parser.add_argument('--solo',
                        action='store_true',
                        help="Exclude matches that contain players in your 'known_players.txt' file. Intended use is \
                        tracking matches where you queued without a fireteam. If used, '--gamertag_only' flag will be \
                        ignored. Will be result in less than 'number_matches' results due to exclusions")
    parser.add_argument('--gamertag_only',
                        action='store_true',
                        help="Only store stats from 'gamertag' player and not everyone in the lobby")

    return parser.parse_args(args)


def fetch_full_match_data(gamer_tag, number_matches=-1, solo=False):
    known_teammates = get_known_teammates(CONFIG_PATH) if solo else []
    print(known_teammates)
    token = get_api_token(CONFIG_PATH)
    offset_array = get_offset_array(token, gamer_tag, number_matches=number_matches)
    match_ids = get_match_id_list(offset_array, token, gamer_tag)
    matches = get_specified_matches(match_ids, token, ignore_match_gamertags=known_teammates)
    return matches_to_dict_list(matches)

def fetch_player_only_data(gamer_tag, number_matches=-1):
    token = get_api_token(CONFIG_PATH)
    offset_array = get_offset_array(token, gamer_tag, number_matches=number_matches)
    matches = get_single_player_matches(offset_array, token, gamer_tag)
    return matches_to_dict_list(matches)

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    if args.gamertag_only:
        data = fetch_player_only_data(args.gamertag, args.number_matches)
    else:
        data = fetch_full_match_data(args.gamertag, args.number_matches, args.solo)
    df = pd.DataFrame(data)
    df.drop(['player_match_id'], axis=1, inplace=True)
    df.to_csv(get_output_directory(CONFIG_PATH) + args.filename, index=False)