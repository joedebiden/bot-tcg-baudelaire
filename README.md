# Discord Bot Documentation : TCG - Elo manager

## Introduction 

This Discord bot manages a competition between players using an Elo rating system. It allows you to:

- Create a player account.

- Initiate matches between players.

- Update player Elo scores after a match.

- View the player leaderboard.

## Installation

### Prerequisites

1. Python version 3.12+
2. A configured database instance (SQLite3 in this project)
3. A discord bot token (created via the [Discord Developper Portal]([text](https://discord.com/developers/applications)))

### Installation steps

1. Clone this repo:
```
git clone https://github.com/joedebiden/bot-tcg-baudelaire.git`
cd bot-tcg-baudelaire
```
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Configure your .env file:
- Create a `.env` file:
- Add your Discord token: 
```
BOT_TOKEN='Your_discord_token_here'
```

4. Run the bot in the src folder: 
```
python main.py
```

## Usage

### Available commands

1. **Starting the adventure**
    - Command: `.start`
    - Description: Adds the current user to the competition with an initial Elo score of 1200.

2. **Player Information**
    - Command: `.info <name>`
    - Description: Displays a player's information (name and Elo score).

3. **Declare a Match**
    - Command: `.match <opponent_name>`
    - Description: Declares a match between the user and an opponent.

4. **Accept a Match**
    - Command: `.accepter <match_id>`
    - Description: Accepts a pending match.

5. **Decline a Match**
    - Command: `.refuser <match_id>`
    - Description: Declines a pending match.

6. **Register a Winner**
    - Command: `.win <match_id> <winner_name>`
    - Description: Records the winner of a match and updates the Elo scores.

7. **Show the Leaderboard**
    - Command: `.leaderboard`
    - Description: Displays the current leaderboard sorted by Elo scores.

## Database

### Main tables

1. **Joueurs**
- `id`: Unique identifier for player
- `nom`: Player's name
- `elo`: Player's elo score

2. **Matches**
- `id`: Unique match identifier
- `joueur1`: Name of player 1 (the one who request the match)
- `joueur2`: Name of player 2 
- `etat`: Match status (pending, ongoing, completed, cancelled)
- `gagnant`: Winner's name (if the match is completed)

## Future improvements

1. Tournament management.

2. Automatic notifications for important updates.

3. Adding a website or interactive dashboard to visualize the leaderboard.

## Contribution 

1. Clone the project:
```
git clone https://github.com/joedebiden/bot-tcg-baudelaire.git
```

2. Create a branch for your changes:
```
git checkout -b my-feature
```

3. Submit a pull request after making your changes.


### Thank you for contributing to this project!
