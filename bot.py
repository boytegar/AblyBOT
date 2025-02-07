import base64
import json
import os
import random
import sys
import time
from urllib.parse import parse_qs, unquote
from datetime import datetime, timedelta
from ably import Ably

def print_(word):
    now = datetime.now().isoformat(" ").split(".")[0]
    print(f"[{now}] | {word}")


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')
    
def load_query():
    try:
        with open('ably_query.txt', 'r') as f:
            queries = [line.strip() for line in f.readlines()]
        return queries
    except FileNotFoundError:
        print("File query name .txt not found.")
        return [  ]
    except Exception as e:
        print("Failed get Query :", str(e))
        return [  ]

def parse_query(query: str):
    parsed_query = parse_qs(query)
    parsed_query = {k: v[0] for k, v in parsed_query.items()}
    user_data = json.loads(unquote(parsed_query['user']))
    parsed_query['user'] = user_data
    return parsed_query

def get(id):
        tokens = json.loads(open("tokens.json").read())
        if str(id) not in tokens.keys():
            return None
        return tokens[str(id)]

def save(id, token):
        tokens = json.loads(open("tokens.json").read())
        tokens[str(id)] = token
        open("tokens.json", "w").write(json.dumps(tokens, indent=4))

def load_config():
     data = json.loads(open("config.json").read())
     return data

def print_delay(delay):
    print()
    while delay > 0:
        now = datetime.now().isoformat(" ").split(".")[0]
        hours, remainder = divmod(delay, 3600)
        minutes, seconds = divmod(remainder, 60)
        sys.stdout.write(f"\r[{now}] | Waiting Time: {round(hours)} hours, {round(minutes)} minutes, and {round(seconds)} seconds")
        sys.stdout.flush()
        time.sleep(1)
        delay -= 1
    print_("Waiting Done, Starting....\n")

def main():
    while True:
        start_time = time.time()
        delay = 9 * 3600
        clear_terminal()
        queries = load_query()
        sum = len(queries)
        ably = Ably()
        config = load_config()
        for index, query in enumerate(queries, start=1):
            user = ably.get(query)
            name = user.get('name')
            daily_points = user.get('daily_points', 0)
            points = user.get('points', 0)
            retrodrop_received = user.get('retrodrop_received', True)
            sequential_reward_day = user.get('sequential_reward_day', 0)
            print_(f"[SxG] ======= Account {index}/{sum} | {name} ======= [SxG]")
            print_(f"Points: {points} | Checkin : {sequential_reward_day} Days")
            if not retrodrop_received:
                 ably.generate_retro(query)
            if daily_points == 0:
                 ably.checkin(query)
            if config.get('auto_spin'):
                 print_("Open Spin")
                 ably.wheel_data(query)
            if config.get('auto_task'):
                 print_("Open Task Daily")
                 ably.list_task_daily(query)

                 print_("Open Task Earn")
                 ably.list_task_partner(query)
            
            if config.get('auto_convert'):
                if points > 10000:
                    ably.exchange(query=query, amount=points)
                else:
                     print_("Not enough points to exchange")

            
        end_time = time.time()
        total = delay - (end_time-start_time)
        if total > 0:
            print_delay(total)

if __name__ == "__main__":
     main()