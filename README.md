# Youtube-Downloader
YouTube video/audio downloader with pytube.
## Why I made this script?
Because of Google. I was using FDM to download videos from Youtube until Google came and caused the FDM team to drop this feature for unknown reasons (a real mystery indeed). Other similar apps and even online websites are there that can download youtube videos, you just have to be content with what they decided to give (or show) you until Google comes again to do its business with them.
## Features:
Other than the intended purpose of downloading a Youtube video, you can:
- Download audio streams
- Download a video stream and an audio stream then merge them with ffmpeg
- Downloading videos with Arabic titles won't blow your machine (hopefully)
## Prerequisites:
- Install ffmpeg. (You can see how to [here](https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/))
- `pip install ffmpeg`
- `pip install pytube`
## Known Issues:
- Some streams cannot be downloaded for some reason. Any stream with a size of `0.01 MB` cannot be downloaded so don't choose them.
