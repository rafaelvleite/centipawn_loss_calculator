import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO, StringIO
from zipfile import ZipFile

import chess.pgn
import requests

CONCURRENCY = 100
LAST_WEEK = 1455  # 26/09/2022
# FIRST_WEEK = 1450
FIRST_WEEK = 1140  # 12/09/2016
# get weeks in https://theweekinchess.com/twic


def make_request(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    }
    # response = requests.get('https://theweekinchess.com/zips/twic1455g.zip', headers=headers)
    response_ = requests.get(url, headers=headers)
    return response_


def get_week_pgn(week_number):
    response = make_request(f"https://theweekinchess.com/zips/twic{week_number}g.zip")
    pgn_zip = ZipFile(BytesIO(response.content))
    pgn_file = pgn_zip.namelist()[0]
    pgn_text = pgn_zip.open(pgn_file).read().decode("latin1")
    return pgn_text


def parse_week_pgn(pgn_text):
    pgn_text_split = re.split(r"\n\n", pgn_text)
    games_pgn = []
    for index, _ in enumerate(pgn_text_split):
        try:
            if index % 2 != 0:
                continue
            game_info = pgn_text_split[index]
            game_moves = pgn_text_split[index + 1]
            games_pgn.append("\n\n".join([game_info, game_moves]))
        except:
            continue

    all_games = []
    games_with_erro = []
    for pgn in games_pgn:
        pgn_io = StringIO(pgn)
        pgn_read = chess.pgn.read_game(pgn_io, Visitor=MyGameBuilder)
        if pgn_read.errors:
            games_with_erro.append(pgn)
            continue
        game_info = dict(pgn_read.headers.items())
        game_info["pgn"] = pgn
        all_games.append(game_info)
    return all_games, games_with_erro


def get_week_games_info(week_number):
    week_pgn_text = get_week_pgn(week_number)
    all_games, games_with_erro = parse_week_pgn(week_pgn_text)
    {item.update({"week": week_number}) for item in all_games}
    {item.update({"week": week_number}) for item in games_with_erro}
    return all_games, games_with_erro


class MyGameBuilder(chess.pgn.GameBuilder):
    def handle_error(self, error: Exception) -> None:
        return True


if __name__ == "__main__":

    all_games = []
    all_games_fail = []
    size = LAST_WEEK - FIRST_WEEK + 1
    count = 0
    print(f"\rPercentage: {100*count/size:.2f}%", flush=True, end="")
    with ThreadPoolExecutor(max_workers=min(CONCURRENCY, size)) as executor:
        future_map = {
            executor.submit(get_week_games_info, week_number): week_number
            for week_number in range(FIRST_WEEK, LAST_WEEK + 1)
        }
        for future in as_completed(future_map):
            week_games, fail_games = future.result()
            all_games.extend(week_games)
            all_games_fail.extend(fail_games)
            count += 1
            print(f"\rPercentage: {100*count/size:.2f}%", flush=True, end="")

    with open(f"{FIRST_WEEK}_{LAST_WEEK}_png.json", "w") as outfile:
        json.dump(all_games, outfile, indent=2, ensure_ascii=False)

    with open(f"{FIRST_WEEK}_{LAST_WEEK}_fail.json", "w") as outfile:
        json.dump(all_games_fail, outfile, indent=2, ensure_ascii=False)
