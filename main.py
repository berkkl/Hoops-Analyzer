import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_game_links(team_url, num_games):
    response = requests.get(team_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    game_links = []

    for link in soup.find_all('a', href=True):
        if 'Basket-Mac' in link['href']:
            full_url = link['href']
            if full_url.startswith('//'):
                full_url = "https:" + full_url
            elif not full_url.startswith("http"):
                full_url = "https://arsiv.mackolik.com" + full_url

            game_links.append(full_url)
            if len(game_links) == num_games:
                break

    return game_links

def get_quarter_scores(game_url, team_name):
    response = requests.get(game_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    team_rows = soup.find_all('td', class_='team-name', text=lambda text: team_name in text)
    if not team_rows:
        print(f"Team rows not found for team: {team_name} in {game_url}")
        return {'1P': 0, '2P': 0, '3P': 0, '4P': 0}

    for team_row in team_rows:
        quarters = team_row.parent.find_all('td')[1:5]
        if quarters[0].text.strip().isdigit():
            break

    quarter_scores = {}
    for i, quarter in enumerate(quarters):
        period_name = f'{i+1}P'
        score_text = quarter.find('span', class_='cumilative-period-scores').previous_sibling
        score = int(''.join(filter(str.isdigit, score_text)))
        quarter_scores[period_name] = score
        #print(f"  {period_name}: {score}")

    return quarter_scores

def calculate_average_scores(teams_info):
    all_teams_scores = {}

    for team_name, team_details in teams_info.items():
        team_url, num_games = team_details
        game_links = get_game_links(team_url, num_games)
        team_scores = [get_quarter_scores(game, team_name) for game in game_links]

        avg_scores = pd.DataFrame(team_scores).mean().to_dict()
        all_teams_scores[team_name] = avg_scores

    return all_teams_scores

def main():
    teams_info = {}
    num_teams = int(input("Enter the number of teams: "))
    for _ in range(num_teams):
        team_name = input("Enter team name (as it appears on Mackolik): ")
        team_url = input(f"Enter Mackolik URL for {team_name}: ")
        num_games = int(input(f"Enter the number of recent games to analyze for {team_name}: "))
        teams_info[team_name] = (team_url, num_games)

    average_scores = calculate_average_scores(teams_info)
    for team, scores in average_scores.items():
        print(f"{team} average scores per quarter: {scores}")

if __name__ == "__main__":
    main()
