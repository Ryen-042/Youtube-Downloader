# Youtube-Downloader
YouTube video, audio, and playlist downloader with pytube.
## Why did I write this script?
Because of Google. I was using FDM to download videos from Youtube until Google came and caused the FDM team to drop this feature for unknown reasons (a real mystery indeed). There are similar apps and even online websites that can download from youtube. You only have to be content with what they decided to give (or show) you until Google comes again to do its usual business with them.

Another reason is my need for a fast and easy-to-use keyboard method to download videos from youtube and select all the parameters I want.
## Features:
- Download video streams.
- Download audio streams.
- Download a video stream and an audio stream, then merge them with ffmpeg.
- Download a playlist or a subset of a playlist.
- Download individual videos from links in a text file.
- Using the merge option will automatically download English and Arabic subtitles (manually created or auto-generated if the former does not exist).
- Download the video description.
- Terminal arguments support skipping the input steps.
- Runs in Android (Termux).
## Prerequisites:
- Install ffmpeg. (You can see how to [here](https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/))
- `pip install pytube`
- ~~`pip install youtube_dl'~~
- `pip install yt-dlp`
- `pip install rich`
- `pip install playsound` to enable notification sounds.
## Usage:
You can either run this script normally by entering inputs as asked or simply use terminal arguments to skip the input steps. Ex:
- Step by step: `python "main.py"`.
- With terminal args: `python "main.py" [script_mode] [youtube_link] [start_video_number] [end_video_number]`.
  
You can use `python "main.py" help` to get more information about the expected terminal arguments.
## For Android Users:
You can use this script by downloading Termux. It is available in Play Store and F-Droid, but I highly recommend that you download the [F-Droid](https://f-droid.org/en/packages/com.termux/) version, as the Play Store version causes some problems.  

After Downloading Termux, execute these commands:
- `termux-setup-storage` to get storage permissions.
- `apt update && apt full-upgrade`
- `pkg install ffmpeg`
- `pkg install python`
- `pip install --upgrade pip`
- `pip install pytube`
- `pip install rich`
- `pip install yt-dlp`
## Bonus Section:
- If you are using a terminal that supports aliases, you can run this script with less typing, for example: 
   * `alias ppp=python "E:\...\main.py" $*`
   * `$*` is used to support arguments.
- Termux supports aliases, but it requires you to add a `\` before any space or bracket, for example:
   * `alias ccc=cd\ "/storage/emulated/0/\[My\ Scripts\]\ \[Python\ 3\]/Programming"`.
   * The destination without backslashes directs to `/storage/emulated/0/[My Scripts] [Python 3]/Programming`.
- The used progress bar is provided by pytube in the `cli.py` file. To modify it, you need first to find its location, which you can achieve in two ways:
   * Use some editor like `VS Code` that supports the `Go to the Definition` feature.
   * Use `pip show <package_name>` to get information about the installed package, including its location.  
   
   After finding the package location, locate the `cli.py` file. Inside, edit the `display_progress_bar` function by modifying the `text` variable:
     * `text = f"{mbytes_remaining:>7}:{round(filesize/1000/1000, 2)} MB | {progress_bar} | {percent}%\t\t\r"`
