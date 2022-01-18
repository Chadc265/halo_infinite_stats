from data import get_api_token, get_offset_array, \
    get_match_id_list, get_specified_matches, \
    matches_to_dict_list
import pandas as pd

CONFIG_PATH = "C:/Repo/python_config.ini"

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    tag = 'CRZY CLwN13'
    token = get_api_token(CONFIG_PATH)
    offset_array = get_offset_array(token, tag, number_matches=50)
    # test = get_my_stats(offset_array, token, tag)
    # test.to_csv('C:/repo/new halo stats test.csv')
    match_ids = get_match_id_list(offset_array, token, tag)
    # match_ids = get_match_id_list([700, 725, 750], token, tag)
    known_teammates=['Shrubanator',
                     'C1umsyNinjaMan',
                     'CharlozD',
                     'I Clown On You',
                     'doomlama',
                     'pledgePLOPPER',
                     'RarmijoTres',
                     'Mister Jinxy'
]
    csr_matches = get_specified_matches(match_ids, token, ignore_match_gamertags=None)
    csr_data = matches_to_dict_list(csr_matches)
    csr_df = pd.DataFrame(csr_data)
    csr_df.drop(['player_match_id'], axis=1, inplace=True)
    csr_df.to_csv('C:/repo/match_csr_stats_01-18-2022.csv', index=False)