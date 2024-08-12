
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
  - **Windows [Stable](#stable-appinstaller):** `https://releases.arc.net/windows/prod/Arc.appinstaller`
  - **Windows [Earlybirds](#earlybirds-appinstaller):** `https://releases.arc.net/windows/rc/[EARLYBIRDS_HASH]/Arc.appinstaller`
- **Actions:**
  - **Detect new version:**
    1. Download the `appinstaller` file using `requests`
    2. Extract version number using `beautifulsoup4`
    3. Compare new version to last recorded version
  - **Process stable version information:**
    1. Download [Release Notes page](https://resources.arc.net/hc/en-us/articles/22513842649623-Arc-for-Windows-2023-2024-Release-Notes)
    2. Extract relevant changelog from [HTML](/html-example.html)
    3. Split changelog into smaller parts if necessary, preserving existing paragraph breaks
  - **Process Earlybirds version information:**
    1. Download MSIX file: `https://releases.arc.net/windows/rc/[EARLYBIRDS_HASH]/[VERSION]/Arc.x64.msix`
    2. Extract file and directory list from MSIX
    3. Compare new file list to previous Earlybirds version
    4. Create a message describing added/removed files and directories

### 3. Sending Messages

- **New stable version detected:**
  - Send to `WIN_CHAT_CHANNEL_ID`
  - Content: "A new version of Arc is available. Check it out!"

- **Stable version update:**
  - Channels: `NEWS_CHANNEL_ID`
  - Ping: `WINDOWS_NEWS_ROLE_ID` 
  - [Content](#stable-version-message-example) for `NEWS_CHANNEL_ID`:
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
      "/n - Waiting for release notes. It could take a few minutes. /n"
  

- **Earlybirds version update:**
  - Channels: `EARLY_NEWS_CHANNEL_ID`, `EARLY_CHAT_CHANNEL_ID`
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

<br>
<br>
<br>


------------------------------------------------------------

<br>

### Stable .appinstaller
```
<?xml version="1.0" encoding="utf-8"?>
<AppInstaller Uri="https://releases.arc.net/windows/prod/Arc.appinstaller" Version="1.14.0.41781" xmlns="http://schemas.microsoft.com/appx/appinstaller/2018">
    <MainPackage Name="TheBrowserCompany.Arc" Version="1.14.0.41781" Publisher="E=hello@thebrowser.company, CN=THE BROWSER COMPANY OF NEW YORK INC., O=THE BROWSER COMPANY OF NEW YORK INC., STREET=295 LAFAYETTE STREET, L=New York, S=New York, C=US, OID.1.3.6.1.4.1.311.60.2.1.2=Delaware, OID.1.3.6.1.4.1.311.60.2.1.3=US, SERIALNUMBER=7571542, OID.2.5.4.15=Private Organization" Uri="https://releases.arc.net/windows/prod/1.14.0.41781/Arc.x64.msix" ProcessorArchitecture="x64" />
    <Dependencies>
        <Package Name="Microsoft.VCLibs.140.00.UWPDesktop" Publisher="CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US" ProcessorArchitecture="x64" Uri="https://releases.arc.net/windows/dependencies/x64/Microsoft.VCLibs.x64.14.00.Desktop.14.0.33728.0.appx" Version="14.0.33728.0" />
    </Dependencies>
</AppInstaller>
```

### Earlybirds .appinstaller
```
<?xml version="1.0" encoding="utf-8"?>
<AppInstaller Uri="https://releases.arc.net/windows/rc/8EE7CF18-AF4C-48AF-94B0-4B9300876DA5/Arc.appinstaller" Version="1.15.0.52516" xmlns="http://schemas.microsoft.com/appx/appinstaller/2018">
    <MainPackage Name="TheBrowserCompany.Arc" Version="1.15.0.52516" Publisher="E=hello@thebrowser.company, CN=THE BROWSER COMPANY OF NEW YORK INC., O=THE BROWSER COMPANY OF NEW YORK INC., STREET=295 LAFAYETTE STREET, L=New York, S=New York, C=US, OID.1.3.6.1.4.1.311.60.2.1.2=Delaware, OID.1.3.6.1.4.1.311.60.2.1.3=US, SERIALNUMBER=7571542, OID.2.5.4.15=Private Organization" Uri="https://releases.arc.net/windows/rc/8EE7CF18-AF4C-48AF-94B0-4B9300876DA5/1.15.0.52516/Arc.x64.msix" ProcessorArchitecture="x64" />
    <Dependencies>
        <Package Name="Microsoft.VCLibs.140.00.UWPDesktop" Publisher="CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US" ProcessorArchitecture="x64" Uri="https://releases.arc.net/windows/dependencies/x64/Microsoft.VCLibs.x64.14.00.Desktop.14.0.33728.0.appx" Version="14.0.33728.0" />
    </Dependencies>
</AppInstaller>
```

### Stable Version Message Example
```
# <:arc:1159648372324569198> Arc for Windows Update - 1.13.0 (40526)
## <:time:1022128056917299302>  August 1, 2024

> - Arc is now available on Windows 10 version 19H1 and newer! Check the minimum requirements to run Arc on Windows 10. Download the latest from arc.net/download.
> - Fixed Issue(s):
>   - Focus would always shift to the first Space after reordering Spaces.
>   - The Mini Player (Picture-in-Picture) would not fully close when returning to the tab playing the original video.
>   - If you've experienced issues with Arc Sync, Arc Max or submitting reports via "Contact the Team" please sign out (Arc Menu > Sign Out) and sign back in to Arc. This will resolve the issue.  Some Members reported that they were force signed out of Arc due to this issue. Arc will now display a banner in Settings (Control+Comma) urging Members experiencing this issue to sign out and back in to resolve.  Please make sure to save your Recovery Phrase before signing out to prevent issues reenabling Arc Sync.

[Download Arc for Windows](https://releases.arc.net/windows/prod/1.13.0.40526/Arc.x64.msix) - [Release Notes](<https://resources.arc.net/hc/en-us/articles/22513842649623-Arc-for-Windows-2023-2024-Release-Notes>)

<@&1199550383849226291>

```

lol why did u read this bullshit


+rss podcast
+arc.net/release-notes
