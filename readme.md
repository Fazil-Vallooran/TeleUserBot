# TeleUserBot

A Telegram userbot built with [Telethon](https://github.com/LonamiWebs/Telethon) that automatically adds watermarks to images, appends channel/bot usernames to messages, and handles MP3/document messages with custom formatting.

## Features

- Adds a semi-transparent watermark (channel/bot username) to outgoing images.
- Appends a username footer to outgoing text messages in channels or bot chats.
- Edits outgoing MP3/document messages to include the filename and username.
- Prevents message processing loops.

## Requirements

- Python 3.8+
- [Telethon](https://github.com/LonamiWebs/Telethon)
- [Pillow (PIL)](https://python-pillow.org/)

## Setup

1. **Clone the repository** and install dependencies:
    ```sh
    pip install telethon pillow
    ```

2. **Configure your Telegram API credentials**  
   Edit [`config.py`](config.py) with your `API_ID`, `API_HASH`, `PHONE`, and `TWO_STEP_PASS`.

3. **Add the font file**  
   Ensure `Franklin Gothic Heavy Regular.ttf` is present in the project root for watermarking.

4. **Run the bot**:
    ```sh
    python main.py
    ```

## File Structure

- [`main.py`](main.py): Main bot logic.
- [`config.py`](config.py): Configuration for API credentials.
- `Franklin Gothic Heavy Regular.ttf`: Font used for watermarking.
- `Telethon_UserBot.session`: Session file (auto-generated).
- `temp_media/`: Temporary media storage (if used).

## Notes

- Your credentials in `config.py` are sensitive. Do **not** share this file.
- The bot edits only your own outgoing messages.
- Watermarked images are sent as new messages and the originals are deleted.
