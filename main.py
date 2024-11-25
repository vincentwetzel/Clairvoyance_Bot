import os
from typing import Dict, List

import cassiopeia as cass


def main():
    cass.set_riot_api_key(init_token())

    GAMES_TO_ANALYZE_COUNT = 2

    print_average_vision_score("rada3", GAMES_TO_ANALYZE_COUNT)


def print_average_vision_score(summoner_name: str, games_count: int) -> int:
    account = cass.get_account(name=summoner_name, tagline="NA1", region="NA")
    summoner: cass.Summoner = account.summoner
    match_history: cass.MatchHistory = cass.MatchHistory(puuid=summoner.puuid, continent=summoner.continent,
                                                         queue=cass.Queue.ranked_solo_fives)

    # Init variables
    match: cass.Match
    matches_with_role: List[cass.Match] = list()
    most_recent_role: cass.Role

    # Figure out most recent role
    found = False
    for match in match_history:
        for participant in match.participants:
            if participant.summoner.id == summoner.id:
                found = True
                most_recent_role = participant.role
                break
        if not found:
            raise Exception("Role not found. Exiting...")
        break

    # Analyze the recent matches with this role
    for match in match_history:
        print(f"Analyzing match: {match.id}")
        if match.is_remake:
            print(f"Skipping because the match was a remake...")
            continue
        for participant in match.participants:
            if participant.summoner.id == summoner.id:
                print(f"Summoner played role: {participant.role}")
                print(f"Summoner played champion: {participant.champion.name}")
                if participant.role == most_recent_role:
                    print(f"Adding Match {match.id} to matches_with_role List...")
                    matches_with_role.append(match)
                else:
                    print(f"Summoner played a different role in match {match.id}")
                break
        if (len(matches_with_role) > games_count):
            break

    total_vision_score = 0
    total_minutes_played = 0
    for match in matches_with_role:
        print(
            f"DATE: {match.start.date()}, CHAMPION: {match.participants[summoner].champion.name}, MATCH ID: {match.id}")
        participant: cass.core.match.Participant
        for participant in match.participants:
            if (participant.summoner.id == summoner.id and participant.stats.vision_score > 0):
                print("Vision score: " + str(participant.stats.vision_score))
                total_vision_score += participant.stats.vision_score
                total_minutes_played += match.duration.seconds / 60

    print(f"\nAverage vision score across {games_count} games as {most_recent_role.name} was: {total_vision_score / len(matches_with_role):.2f}")
    print(f"Average vision score per minute across {games_count} games was: {total_vision_score / total_minutes_played:.2f}")


def init_token() -> str:
    if os.path.isfile("settings.ini"):
        with open("settings.ini", 'r') as f:
            settings_lines = f.readlines()
            for line in settings_lines:
                if "riot_api_token=" in line:
                    return line.split("=")[1]


if __name__ == "__main__":
    main()
