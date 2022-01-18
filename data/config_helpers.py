import configparser

def get_api_token(config_path: str) -> str:
    config = configparser.ConfigParser()
    config.read(config_path)
    return config['halo']['dev_token']

def get_known_teammates(config_path:str) -> list[str]:
    config = configparser.ConfigParser()
    config.read(config_path)
    fn = config['halo']['known_teammate_file_path']
    return parse_known_teammate_file(fn)

def get_output_directory(config_path:str) -> str:
    config = configparser.ConfigParser()
    config.read(config_path)
    return config['halo']['out_directory']

def parse_known_teammate_file(fn:str) -> list[str]:
    ret = []
    with open(fn) as f:
        lines = f.read().splitlines()
        for line in lines:
            ret.append(line)
    return ret