# Discord Bot for Arc Browser Updates

## Objective
To build a Discord bot in Python 3 that automatically updates the Arc community about new versions and changes in the browser, including analysis of Earlybirds versions.

## Stage 1: Core Requirements

### 1. Environment

- **Programming Language:** Python 3
- **Libraries:** 
  - `discord.py`: For Discord API interaction
  - `requests`: For downloading web pages and content
  - `beautifulsoup4`: For HTML parsing
  - `zipfile`: For working with MSIX files
  - `python-dotenv`: For loading variables from a `.env` file
- **.env file:**
  ```
  DISCORD_TOKEN="YOUR_DISCORD_BOT_TOKEN"
  NEWS_CHANNEL_ID=123456789012345678
  EARLY_NEWS_CHANNEL_ID=987654321098765432
  WIN_CHAT_CHANNEL_ID=135792468013579246
  EARLY_CHAT_CHANNEL_ID=246801357924680135
  WINDOWS_NEWS_ROLE_ID=111222333444555666
  EARLYBIRDS_HASH="8EE7CF18-AF4C-48AF-94B0-4B9300876DA5"
  ARC_EMOJI="<:arc:1159648372324569198>"
  ARC_RC_EMOJI="<:arcReleaseCandidate:1159647421316485162>"
  TIME_EMOJI="<:time:1022128056917299302>"
  LOGGING_CHANNEL_ID=111111111111111111
  ```

### 2. Version Checking

- **Frequency:**
  - **Stable versions:** Check every 5 minutes
  - **Earlybirds versions:** Check every 2 minutes during expected update hours (define in code)
- **Sources:**
  - **Windows Stable:** `https://releases.arc.net/windows/prod/Arc.appinstaller`
  - **Windows Earlybirds:** `https://releases.arc.net/windows/rc/[EARLYBIRDS_HASH]/Arc.appinstaller`
- **Actions:**
  - **Detect new version:**
    1. Download the `appinstaller` file using `requests`
    2. Extract version number using `beautifulsoup4`
    3. Compare new version to last recorded version
  - **Process stable version information:**
    1. Download Release Notes page
    2. Extract relevant changelog from HTML
    3. Split changelog into smaller parts if necessary, preserving existing paragraph breaks
  - **Process Earlybirds version information:**
    1. Download MSIX file
    2. Extract file and directory list from MSIX
    3. Compare new file list to previous Earlybirds version
    4. Create a message describing added/removed files and directories

### 3. Sending Messages

- **New version detected:**
  - Send to all news channels (`NEWS_CHANNEL_ID`, `EARLY_NEWS_CHANNEL_ID`)
  - Content: "A new version of Arc is available. Check it out!"

- **Stable version update:**
  - Channels: `NEWS_CHANNEL_ID`, `WIN_CHAT_CHANNEL_ID`
  - Ping: `WINDOWS_NEWS_ROLE_ID` (only for `NEWS_CHANNEL_ID`)
  - Content for `NEWS_CHANNEL_ID`:
    ```
    # <:arc:1159648372324569198> Arc for Windows Update - [VERSION]
    ## <:time:1022128056917299302> [DATE]

    > [CHANGELOG]

    [**Release Notes**](<https://resources.arc.net/hc/en-us/articles/22513842649623-Arc-for-Windows-2023-2024-Release-Notes>) - [**Download Arc for Windows**](<https://releases.arc.net/windows/prod/[VERSION]/Arc.x64.msix>)
    ```
    - Do not ping immediately
    - Check for changes in the changelog HTML file
    - If changes exist, edit the message
    - If no changes, check every 1 minute until changes are detected
    - If no valid changelog, replace [CHANGELOG] with:
      "Waiting for release notes. It could take a few minutes."
  - Content for `WIN_CHAT_CHANNEL_ID`:
    "There is a new version of Arc for Windows! Go and download it!"

- **Earlybirds version update:**
  - Channels: `EARLY_NEWS_CHANNEL_ID`, `EARLY_CHAT_CHANNEL_ID`
  - Ping: Include ping (if exists) when sending the message
  - Content for `EARLY_NEWS_CHANNEL_ID`:
    ```
    # <:arcReleaseCandidate:1159647421316485162> Arc Early Birds Update - [VERSION]
    ## <:time:1022128056917299302> [DATE]

    > Arc does not provide official changelogs for Early Birds versions.

    **Changes in this version:**
    > Processing the new version, please wait.

    **Additional Information:**
    > [MSIX_CHANGES]

    [**Download Arc Early Birds**](<https://releases.arc.net/windows/rc/[EARLYBIRDS_HASH]/[VERSION]/Arc.x64.msix>)
    ```
  - Content for `EARLY_CHAT_CHANNEL_ID`:
    "There is a new version of Arc Early Birds! Go and download it!"

### 4. Logging System

- Implement a logging system that:
  - Sends logs to the terminal
  - Sends logs to a dedicated Discord channel (use `LOGGING_CHANNEL_ID`)

## Stage 2: Additional Requirements (Optional)

### Weekly Summary

- Collect information:
  - Screenshot of visual changelog
  - Podcast transcription (using Google Cloud API)
  - Changelogs from all platforms (Windows only initially)
- Use a large language model to create a summary of key new features
- Send summary to news channel on Thursdays

### Historical Documentation

- Use `README.md` file on GitHub
- Convert repo to GitHub Pages
- Automatically update page with each significant change
- Page structure:
  - Update date
  - New versions for each platform
  - Links to full changelogs
  - Brief summary of main changes
  - Link to new podcast episode (if available)

### Additional Integrations

- Reddit (Broadmap):
  - Build Reddit bot to automatically share updates in a specific thread or send notifications when the topic changes
  - Integrate with Discord bot for unified script

## Important Notes

- **Message Splitting:** Ensure each Discord message doesn't exceed 2000 characters. Split long messages logically, preserving existing paragraphs.
- **Support for Additional Platforms:** Support for other platforms (macOS, iOS, Android) can be added later.
- **Variable and Function Names:** Choose clear and readable variable and function names in the code.
