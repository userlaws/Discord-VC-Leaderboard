### `README.md`

# Discord VC Leaderboard [Proof](https://i.ibb.co/T2xC7Zv/Screenshot-2024-09-16-150215.png)

[![Discord Bot](https://img.shields.io/badge/Discord-Bot-blue?style=flat-square)](https://discord.com/)

This is a Discord bot that tracks users' activity in voice channels, including total time spent, muted time, and deafened time. The bot posts and updates a leaderboard on a Discord channel using webhooks.

## Features

- Tracks total time spent in voice channels.
- Tracks time spent while muted or deafened.
- Updates the leaderboard dynamically every 6 seconds.
- Posts and updates the leaderboard using a Discord webhook.

## Getting Started

### Prerequisites

- Python 3.8+
- `discord.py` library
- A Discord bot token
- A Discord server with appropriate permissions for the bot

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/userlaws/Discord-VC-Leaderboard.git
   cd Discord-VC-Leaderboard


2. **Install dependencies:**
- **You dont really need to have the .txt file you can just pip install discord etc.**
   - The ``-r`` option is used when you have a file (commonly named requirements.txt) that lists multiple dependencies required for your project. This approach is useful when you need to install several packages at once or when you want to share the list of dependencies with others.
     
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your bot:**

   - Open `main.py` and replace:
     - `'your_bot_token_here'` with your actual bot token.
     - `'your_webhook_url_here'` with the webhook URL for the channel you want to post the leaderboard.

4. **Run the bot:**
   ```bash
   python main.py
   ```

### Usage

1. **Invite your bot to a server:**  
   Go to the Discord Developer Portal, generate an OAuth2 URL with the required permissions, and invite the bot to your server.

2. **Ensure proper permissions:**  
   The bot requires permissions to read member statuses, manage messages, and access voice states.

3. **Monitor and use the leaderboard:**  
   The bot will automatically post and update the leaderboard to the specified channel using the webhook.

### Configuration

- **Webhook URL:** You need to set up a Discord webhook in the channel where you want the leaderboard to be posted.
- **Bot Token:** Obtain your bot token from the Discord Developer Portal and replace it in the script.

### `requirements.txt`

```plaintext
discord.py
requests
```

## Contributing

Feel free to fork this repository and submit pull requests. Please ensure all code adheres to Python best practices and is well-documented.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
