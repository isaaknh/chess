import requests
import time
from datetime import datetime

# User-specific settings
username = "isaaknh"  # Replace with your Chess.com username
contact_email = "youremail@example.com"  # Replace with your contact email
earliest_date = "2024-01-01"  # Set an earliest date in the format "YYYY-MM-DD" (or None to disable)
game_type = "rapid"  # Filter for rapid games (set to None to disable filtering)

# Set up headers to mimic a browser request and include a user-agent with contact info
headers = {
    'User-Agent': f'my-profile-tool/1.2 (username: {username}; contact: {contact_email})',
    'Accept-Encoding': 'gzip',
    'Accept': 'application/json, text/plain, */*'
}

# Function to fetch the list of archives (months/years with games)
def fetch_archives(username):
    url = f"https://api.chess.com/pub/player/{username}/games/archives"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            return response.json().get('archives', [])
        except requests.exceptions.JSONDecodeError:
            print("Error: Received non-JSON response")
            print(response.text)  # Debug: Print the raw response for further inspection
            return []
    else:
        print(f"Error: Failed to fetch archives. Status Code: {response.status_code}")
        print(response.text)  # Debug: Print the raw response for further inspection
        return []

# Function to fetch games from a list of archive URLs with optional filters
def fetch_filtered_games(archive_list, earliest_date=None, game_type=None):
    all_pgns = ""
    earliest_date_obj = datetime.strptime(earliest_date, "%Y-%m-%d") if earliest_date else None

    for archive_url in archive_list:
        # Delay between requests to avoid rate limiting
        time.sleep(1)
        
        response = requests.get(archive_url, headers=headers)
        print(f"Fetching games from {archive_url}, Status Code: {response.status_code}")
        
        if response.status_code == 200:
            games = response.json().get('games', [])
            
            for game in games:
                # Convert integer timestamp to datetime
                game_date = datetime.fromtimestamp(game['end_time']) if 'end_time' in game else None
               
                # Skip games that do not meet the date or game type criteria
                if earliest_date_obj and game_date and game_date < earliest_date_obj:
                    print(f"Skipping game from {game_date} because it's before {earliest_date}")
                    continue
                if game_type and game.get('time_class') != game_type:
                    continue

                # Add PGN to result
                all_pgns += game.get('pgn', '') + "\n\n"  # Add some space between games

        elif response.status_code == 429:
            print(f"Rate limit exceeded. Retrying after a delay.")
            time.sleep(60)  # Wait for 60 seconds before retrying
            response = requests.get(archive_url, headers=headers)
            if response.status_code == 200:
                games = response.json().get('games', [])
                for game in games:
                    game_date = datetime.fromtimestamp(game['end_time']) if 'end_time' in game else None
                    if earliest_date_obj and game_date and game_date < earliest_date_obj:
                        continue
                    if game_type and game.get('time_class') != game_type:
                        continue
                    all_pgns += game.get('pgn', '') + "\n\n"
            else:
                print(f"Failed to fetch games from {archive_url}")
        else:
            print(f"Failed to fetch games from {archive_url}")

    return all_pgns

# Main function to run the script
def main():
    print(f"Fetching game archives for user: {username}")
    archive_list = fetch_archives(username)
    if archive_list:
        print(f"Found {len(archive_list)} archives. Fetching games...")
        all_pgns = fetch_filtered_games(archive_list, earliest_date=earliest_date, game_type=game_type)
        
        # Write all PGNs to a single file
        filename = f"{username}_filtered_games.pgn"
        with open(filename, "w") as pgn_file:
            if all_pgns.strip():  # Ensure there is something to write
                pgn_file.write(all_pgns)
                print(f"Filtered games have been saved to {filename}")
            else:
                print("No games matched the specified criteria.")
    else:
        print("No archives found or unable to fetch archive list.")

if __name__ == "__main__":
    main()