import pandas as pd
import argparse
import os
import sys
from classes import Match
from data import get_api_token, get_offset_array, \
    get_match_id_list, get_specified_matches, \
    matches_to_dict_list, get_output_directory, \
    get_match_id_list_auto

CONFIG_PATH = "C:/Repo/python_config.ini"

def fetch_full_match_data(gamer_tag, number_matches=-1, json_dir:str=None, skip_existing:bool=False) -> list[Match]:
    token = get_api_token(CONFIG_PATH)
    offset_array = get_offset_array(token, gamer_tag, number_matches=number_matches)
    match_ids = get_match_id_list(offset_array, token, gamer_tag)
    if skip_existing:
        match_ids = remove_stored_matches_from_list(match_ids, json_dir)
    matches = get_specified_matches(match_ids, token, ignore_match_gamertags=[], save_json_dir=json_dir)
    return matches

def fetch_data_auto_skip(gamer_tag, json_dir:str):
    token = get_api_token(CONFIG_PATH)
    offset_array = get_offset_array(token, gamer_tag)
    match_ids = get_match_id_list_auto(offset_array, token, gamer_tag, json_dir)
    matches = get_specified_matches(match_ids, token, save_json_dir=json_dir)
    return matches

def remove_stored_matches_from_list(match_ids:list[str], json_dir:str):
    stored_files = os.listdir(json_dir)
    trimmed_list = []
    for m in match_ids:
        if not any([m in f for f in stored_files]):
            trimmed_list.append(m)
    return trimmed_list

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
    parser.add_argument("--skip_existing",
                        action='store_true',
                        help="If json exists in json directory, do not save that game again")

    return parser.parse_args(arg)

def write_to_files(matches_by_date:dict, base_out_path):
    for k,v in matches_by_date.items():
        fn = make_filename(base_out_path, k)
        if os.path.exists(fn):
            df_existing = pd.read_csv(fn)
            df = pd.DataFrame(matches_to_dict_list(v))
            df.drop(['player_match_id'], axis=1, inplace=True)
            new_df = pd.concat([df_existing, df])
            new_df.to_csv(fn, index=False)
        else:
            df = pd.DataFrame(matches_to_dict_list(v))
            df.drop(['player_match_id'], axis=1, inplace=True)
            df.to_csv(fn, index=False)


def make_filename(path, date_string):
    return path + date_string + ".csv"

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    output_dir = get_output_directory(CONFIG_PATH)
    json_directory = output_dir + "JSON/"
    # if args.save_jsons:
    #     json_directory = output_dir + "JSON/"
    # match_list = fetch_full_match_data(args.gamertag,
    #                                    args.number_matches,
    #                                    json_dir=json_directory,
    #                                    skip_existing=args.skip_existing)
    match_list = fetch_data_auto_skip(args.gamertag, json_directory)
    daily_matches = split_matches_by_date(match_list)

    write_to_files(daily_matches, output_dir + "New/")
