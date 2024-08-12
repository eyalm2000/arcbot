import discord
from discord.ext import tasks, commands
import requests
from bs4 import BeautifulSoup
import zipfile
from datetime import datetime
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Discord bot token and channel IDs
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
NEWS_CHANNEL_ID = int(os.getenv("NEWS_CHANNEL_ID"))
EARLY_NEWS_CHANNEL_ID = int(os.getenv("EARLY_NEWS_CHANNEL_ID"))
WIN_CHAT_CHANNEL_ID = int(os.getenv("WIN_CHAT_CHANNEL_ID"))
EARLY_CHAT_CHANNEL_ID = int(os.getenv("EARLY_CHAT_CHANNEL_ID"))
WINDOWS_NEWS_ROLE_ID = int(os.getenv("WINDOWS_NEWS_ROLE_ID"))
LOGGING_CHANNEL_ID = int(os.getenv("LOGGING_CHANNEL_ID"))

# Earlybirds hash
EARLYBIRDS_HASH = os.getenv("EARLYBIRDS_HASH")

# Emojis
ARC_EMOJI = os.getenv("ARC_EMOJI")
ARC_RC_EMOJI = os.getenv("ARC_RC_EMOJI")
TIME_EMOJI = os.getenv("TIME_EMOJI")

# URLs
STABLE_APPINSTALLER_URL = "https://releases.arc.net/windows/prod/Arc.appinstaller"
EARLYBIRDS_APPINSTALLER_URL = f"https://releases.arc.net/windows/rc/{EARLYBIRDS_HASH}/Arc.appinstaller"
RELEASE_NOTES_URL = "https://resources.arc.net/hc/en-us/articles/22513842649623-Arc-for-Windows-2023-2024-Release-Notes"

# Global variables to store last recorded versions and files
last_stable_version = None
last_earlybirds_version = None
last_earlybirds_files = None

# User-Agent for requests
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
HEADERS = {'User-Agent': USER_AGENT}

# Initialize the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Function to extract version from appinstaller
def extract_version(appinstaller_content):
    soup = BeautifulSoup(appinstaller_content, "xml")
    version = soup.find("AppInstaller")["Version"]
    return version

# Function to extract changelog from release notes
def extract_changelog(release_notes_content, version):
    soup = BeautifulSoup(release_notes_content, "html.parser")
    changelog_section = soup.find("h2", string=lambda text: version in text)
    if changelog_section:
        changelog = []
        for sibling in changelog_section.next_siblings:
            if sibling.name == "h2":
                break
            if sibling.name == "ul":
                for item in sibling.find_all("li"):
                    changelog.append(f"- {item.text.strip()}")
            elif sibling.name == "p":
                changelog.append(sibling.text.strip())
        return "\n".join(changelog)
    return None

# Function to extract files from MSIX
def extract_msix_files(msix_path):
    try:
        with zipfile.ZipFile(msix_path, 'r') as zip_ref:
            return zip_ref.namelist()
    except zipfile.BadZipFile:
        log_error(f"Invalid MSIX file: {msix_path}")
        return None
    except Exception as e:
        log_error(f"Error extracting MSIX files: {type(e).__name__}: {e}")
        return None

# Function to compare file lists
def compare_file_lists(old_list, new_list):
    added = list(set(new_list) - set(old_list))
    removed = list(set(old_list) - set(new_list))
    changed = []

    # Check for changes in content (excluding binary files)
    for file in set(old_list) & set(new_list):
        try:
            with zipfile.ZipFile('old_version.msix', 'r') as old_zip, \
                 zipfile.ZipFile('new_version.msix', 'r') as new_zip:

                # Check if the file is likely binary
                if file.endswith(('.exe', '.dll', '.png', '.jpg', '.jpeg', '.gif')):
                    continue  # Skip binary files

                old_content = old_zip.read(file).decode('utf-8')
                new_content = new_zip.read(file).decode('utf-8')
                if old_content != new_content:
                    changed.append(file)
        except Exception as e:
            log_error(f"Error comparing file content: {type(e).__name__}: {e}")

    return added, removed, changed

# Function to log messages
def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    asyncio.run_coroutine_threadsafe(send_log_to_discord(message), bot.loop)

# Function to log errors
def log_error(error_message):
    log_message(f"Error: {error_message}")

# Function to send logs to Discord
async def send_log_to_discord(message):
    channel = bot.get_channel(LOGGING_CHANNEL_ID)
    await channel.send(message)

# Function to format changelog for Discord message
def format_changelog(changelog):
    if changelog:
        return f"> {changelog}"
    else:
        return "\n- Waiting for release notes. It could take a few minutes. \n"

# Function to split a message into chunks
def split_message(message, max_length=2000):
    chunks = []
    current_chunk = ""
    for line in message.splitlines():
        if len(current_chunk) + len(line) + 1 > max_length:
            chunks.append(current_chunk)
            current_chunk = ""
        current_chunk += line + "\n"
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

# Task to check for stable Arc updates
@tasks.loop(minutes=5)
async def check_stable_arc_updates():
    global last_stable_version
    try:
        response = requests.get(STABLE_APPINSTALLER_URL, headers=HEADERS)
        response.raise_for_status()
        new_version = extract_version(response.content)

        if new_version != last_stable_version:
            # New stable version detected
            log_message(f"New stable Arc version detected: {new_version}")
            last_stable_version = new_version
            channel = bot.get_channel(WIN_CHAT_CHANNEL_ID)
            await channel.send("A new version of Arc is available. Check it out!")

            # Send changelog to news channel
            await send_stable_changelog(new_version)

    except requests.exceptions.RequestException as e:
        log_error(f"Error checking stable Arc updates: {type(e).__name__}: {e}")

# Function to send stable changelog to news channel
async def send_stable_changelog(version):
    try:
        response = requests.get(RELEASE_NOTES_URL, headers=HEADERS)
        response.raise_for_status()
        changelog = extract_changelog(response.content, version)

        # Create initial message
        channel = bot.get_channel(NEWS_CHANNEL_ID)
        message_content = (f"# {ARC_EMOJI} Arc for Windows Update - {version}\n"
                           f"## {TIME_EMOJI} {datetime.now().strftime('%B %d, %Y')}\n\n"
                           f"{format_changelog(changelog)}\n\n"
                           f"[**Release Notes**]({RELEASE_NOTES_URL}) - "
                           f"[**Download Arc for Windows**]"
                           f"(https://releases.arc.net/windows/prod/{version}/Arc.x64.msix)")

        for chunk in split_message(message_content):
            message = await channel.send(chunk)

        # Check for changelog updates every minute
        @tasks.loop(minutes=1)
        async def check_changelog_updates():
            nonlocal changelog
            try:
                response = requests.get(RELEASE_NOTES_URL, headers=HEADERS)
                response.raise_for_status()
                new_changelog = extract_changelog(response.content, version)

                if new_changelog and new_changelog != changelog:
                    changelog = new_changelog
                    updated_message_content = (f"# {ARC_EMOJI} Arc for Windows Update - {version}\n"
                                               f"## {TIME_EMOJI} {datetime.now().strftime('%B %d, %Y')}\n\n"
                                               f"> {changelog}\n\n"
                                               f"[**Release Notes**]({RELEASE_NOTES_URL}) - "
                                               f"[**Download Arc for Windows**]"
                                               f"(https://releases.arc.net/windows/prod/{version}/Arc.x64.msix)\n\n"
                                               f"<@&{WINDOWS_NEWS_ROLE_ID}>")  # Ping the role after changelog is updated

                    # Edit or send new messages depending on changelog length
                    chunks = split_message(updated_message_content)
                    if len(chunks) == 1:
                        await message.edit(content=chunks[0])
                    else:
                        # Delete the old message and send new chunks
                        await message.delete()
                        for chunk in chunks:
                            await channel.send(chunk)

                    check_changelog_updates.cancel()  # Stop checking once changelog is updated
            except requests.exceptions.RequestException as e:
                log_error(f"Error checking changelog updates: {type(e).__name__}: {e}")

        check_changelog_updates.start()

    except requests.exceptions.RequestException as e:
        log_error(f"Error sending stable changelog: {type(e).__name__}: {e}")

# Task to check for Earlybirds Arc updates
@tasks.loop(minutes=2)
async def check_earlybirds_arc_updates():
    global last_earlybirds_version, last_earlybirds_files
    try:
        response = requests.get(EARLYBIRDS_APPINSTALLER_URL, headers=HEADERS)
        response.raise_for_status()
        new_version = extract_version(response.content)

        if new_version != last_earlybirds_version:
            # New Earlybirds version detected
            log_message(f"New Earlybirds Arc version detected: {new_version}")
            last_earlybirds_version = new_version
            channel = bot.get_channel(EARLY_CHAT_CHANNEL_ID)
            await channel.send("There is a new version of Arc Early Birds! Go and download it!")

            # Download and analyze MSIX
            msix_url = f"https://releases.arc.net/windows/rc/{EARLYBIRDS_HASH}/{new_version}/Arc.x64.msix"
            msix_response = requests.get(msix_url, headers=HEADERS)
            msix_response.raise_for_status()

            with open("new_version.msix", "wb") as f:
                f.write(msix_response.content)

            new_files = extract_msix_files("new_version.msix")

            if new_files:
                if last_earlybirds_files:
                    # Download the old MSIX file for comparison
                    if os.path.exists("old_version.msix"):
                        os.remove("old_version.msix")
                    old_msix_url = f"https://releases.arc.net/windows/rc/{EARLYBIRDS_HASH}/{last_earlybirds_version}/Arc.x64.msix"
                    old_msix_response = requests.get(old_msix_url, headers=HEADERS)
                    old_msix_response.raise_for_status()
                    with open("old_version.msix", "wb") as f:
                        f.write(old_msix_response.content)

                    added, removed, changed = compare_file_lists(last_earlybirds_files, new_files)

                    msix_changes = ""
                    if added:
                        msix_changes += "**Added Files/Directories:**\n"
                        msix_changes += "\n".join([f"- `{file}`" for file in added]) + "\n\n"
                    if removed:
                        msix_changes += "**Removed Files/Directories:**\n"
                        msix_changes += "\n".join([f"- `{file}`" for file in removed]) + "\n\n"
                    if changed:
                        msix_changes += "**Changed Files/Directories:**\n"
                        msix_changes += "\n".join([f"- `{file}`" for file in changed]) + "\n\n"

                    if not msix_changes:
                        msix_changes = "No significant file changes detected.\n"

                else:
                    msix_changes = "First Earlybirds version detected, no comparison available.\n"

                last_earlybirds_files = new_files

                # Send update message to news channel
                channel = bot.get_channel(EARLY_NEWS_CHANNEL_ID)
                message_content = (f"# {ARC_RC_EMOJI} Arc Early Birds Update - {new_version}\n"
                                   f"## {TIME_EMOJI} {datetime.now().strftime('%B %d, %Y')}\n\n"
                                   f"> Arc does not provide official changelogs for Early Birds versions.\n\n"
                                   f"**Changes in this version:**\n"
                                   f"> Processing the new version, please wait.\n\n"
                                   f"**Additional Information:**\n"
                                   f"> {msix_changes}\n"
                                   f"[**Download Arc Early Birds**]({msix_url})")

                for chunk in split_message(message_content):
                    await channel.send(chunk)

            # Clean up downloaded MSIX files
            if os.path.exists("new_version.msix"):
                os.remove("new_version.msix")
            if os.path.exists("old_version.msix"):
                os.remove("old_version.msix")

    except requests.exceptions.RequestException as e:
        log_error(f"Error checking Earlybirds Arc updates: {type(e).__name__}: {e}")

# Start the tasks when the bot is ready
@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    check_stable_arc_updates.start()
    check_earlybirds_arc_updates.start()

# Run the bot
bot.run(DISCORD_TOKEN)