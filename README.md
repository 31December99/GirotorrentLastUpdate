# GirotorrentLastUpdate

# GiroTorrent.org platform Telegram Notifier

The program is functional but still in an early stage, undergoing constant modifications.

This Python script queries the homepage of girotorrent.org to receive the names of the latest uploaded torrents. For each file, it sends the .torrent file to the user via Telegram
It performs the following tasks:

- Bot log in
- Query "Ultimo Torrent" Table.
- Extracts a series of title directly from the table.
- Compare the table with the bot database and create a list only with new titles.
- Download the file .torrent.
- Send each file to the user via Telegram.

## Usage

1. Just run the bot

## Dependencies

- requiremensts.txt

## Installation

1. Clone this repository.
2. Install the required dependencies using PIP.
3. Configure .env file

## Configuration

Make sure to configure the necessary API keys and authentication credentials in a separate configuration file (.env).

## Contribution

Contributions are welcome! Feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License

# .env file Example:

- user=user
- passw=passw
- download_folder =/home/<user>/GirotorrentLastUpdate/download/
- interval=10
- notify=username telegram user
- api_id=telegram api_id
- api_key=telegram api_key
- bot_token=bot token 


# user
Your forum username 

# passw
your forum password

# DOWNLOAD Folder
your path for file .torrent

# INTERVAL
Query interval

# NOTIFY
your username telegram profile

# API_ID 
Telegram api_id

# API_KEY
Telegram api_key

