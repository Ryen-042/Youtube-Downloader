# Youtube-Downloader
YouTube video, audio, and playlist downloader with pytube.
## Why I made this script?
Because of Google. I was using FDM to download videos from Youtube until Google came and caused the FDM team to drop this feature for unknown reasons (a real mystery indeed). Other similar apps and even online websites are there that can download youtube videos, you just have to be content with what they decided to give (or show) you until Google comes again to do its business with them.

Another reason is my need for a fast, easy to use with keyboard method to download videos from youtube and select all the parameters I want.
## Features:
- Download video streams.
- Download audio streams.
- Download a video stream and an audio stream then merge them with ffmpeg.
- Download a playlist or a subset of a playlist.
- Download individual videos from links in a text file.
- Using the merge option will automaticall download English and Arabic subtitles (auto-generated and manually created).
- Download video description.
- Terminal arguments support to skip the input steps.
## Usage:
You can either run the script normally in a step-by-step manner and enter what is asked from you, or simply use terminal arguments and skip the input steps. Ex:
- Step by step: `python "main.py"`
- With terminal args: `python "main.py" [script_mode] [youtube_link] [start_video_number] [end_video_number]`
## Prerequisites:
- Install ffmpeg. (You can see how to [here](https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/))
- `pip install pytube`
- ~~`pip install youtube_dl'~~
- `pip install yt-dlp`
- `pip install rich`
