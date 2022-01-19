import pandas as pd
import argparse
import sys
from classes import Match
from data import get_api_token, get_offset_array, \
    get_match_id_list, get_specified_matches, \
    matches_to_dict_list, get_output_directory

CONFIG_PATH = "C:/Repo/python_config.ini"

def fetch_full_match_data(gamer_tag, number_matches=-1, json_dir:str=None) -> list[Match]:
    token = get_api_token(CONFIG_PATH)
    offset_array = get_offset_array(token, gamer_tag, number_matches=number_matches)
    match_ids = get_match_id_list(offset_array, token, gamer_tag)
    matches = get_specified_matches(match_ids, token, ignore_match_gamertags=[], save_json_dir=json_dir)
    return matches

def split_matches_by_type(matches:list[Match]):
    ranked = [m for m in matches if m.playlist.ranked]
    ctf = [m for m in ranked if m.mode.name == 'CTF']
    slayer = [m for m in ranked if m.mode.name == 'Slayer']
    zones = [m for m in ranked if m.mode.name == 'Strongholds']
    oddball = [m for m in ranked if m.mode.name == 'Oddball']
    return ctf, oddball, slayer, zones

def split_matches_by_date(matches:list[Match]):
    matches_by_date = {}
    for m in matches:
        d = m.date_time.date().strftime("%m-%d-%Y")
        if d in matches_by_date:
            matches_by_date[d].append(m)
        else:
            matches_by_date[d] = [m]
    return matches_by_date

def parse_args(arg):
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
    parser.add_argument("--save_jsons", action='store_true', help="store all raw json responses too")

    return parser.parse_args(arg)

def write_to_files(matches_by_date:dict, base_out_path):
    for k,v in matches_by_date.items():
        fn = make_filename(base_out_path, k)
        df = pd.DataFrame(matches_to_dict_list(v))
        df.drop(['player_match_id'], axis=1, inplace=True)
        df.to_csv(fn, index=False)


def make_filename(path, date_string):
    return path + date_string + ".csv"

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    output_dir = get_output_directory(CONFIG_PATH)
    json_directory = None
    if args.save_jsons:
        json_directory = output_dir + "JSON/"
    match_list = fetch_full_match_data(args.gamertag, args.number_matches, json_dir=json_directory)
    daily_matches = split_matches_by_date(match_list)

    write_to_files(daily_matches, output_dir + "All/")
