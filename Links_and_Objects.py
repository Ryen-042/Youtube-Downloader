from pytube import YouTube, Playlist, request
from pytube.cli import on_progress as pytube_on_progress
from global_imports import *


## Available functions in this module:
# ['on_complete',  'on_progress',   'vid_link_checker',
#  'get_vid_obj',  'get_start_end', 'get_vid_objs_from_file',
#  'get_vid_objs_from_playlist']


#~ https://github.com/pytube/pytube/issues/1035
# To change the value here to something smaller to decrease chunk sizes, thus increasing the number of times that the progress callback occurs:
request.default_range_size = int(9437184/9*5) # 5MB chunk size

#~ To change the look of the built-in progress bar in pytube, modify the `display_progress_bar` function by adding these lines in the `cli.py` file:
# mbytes_remaining = round( ( filesize - (filesize - bytes_received) ) /1000/1000, 2)
# text = f"{mbytes_remaining:>7}:{round(filesize/1000/1000, 2)} MB | {progress_bar} | {percent}%\r"



def on_complete(stream, file_path):
    # Print only the path to the downloaded file, not including the file's name as it is changed after downloading.
    path_to_file = '\\'.join((file_path.split('\\')[:-1]))
    console.print(f"[normal1]File downloaded successfully in the next path: [normal2]{path_to_file}[/][/]\n")



def on_progress(stream, chunk, bytes_remaining):
    console.print(f"[normal1][nprmal2]{round(100 - bytes_remaining/stream.filesize * 100, 2)}[/]% | [normal2]{round((stream.filesize - bytes_remaining)/1000/1000, 2)}[/]:[normal2]{round(stream.filesize/1000/1000, 2)}[/] MB[/]", end="")
    
    # To erase and return the curson to the beginning of the current line.
    # https://stackoverflow.com/questions/5290994/remove-and-replace-printed-items

    # Usage of 'r' leaves the previously printed characters if they are not overridden.
    # Also, 'r' does not work with console.print().
    
    # print('\033[2K\033[1G', end="") # Doesn't work with CMD
    
    # In theory, visually speaking, the previously line is equivalent to:
    print("\r", end="")
    # print(" " * 100, end="\r") # (100) is some arbitrary number.



def vid_link_checker(link):
    try:
        return YouTube(link, on_complete_callback=on_complete, on_progress_callback=pytube_on_progress)
    except:
        return False



def get_vid_obj(video_link):
    if not video_link:
        console.print("[normal1]Enter a [normal2]link[/] to a YouTube video:[/]", end=" ")
        video_link = input()
    video_obj = vid_link_checker(video_link)
    while not video_obj:
        console.print(f"\n[warning1]([warning2]{video_link}[/]) is not a valid link for a YouTube video.[/]")
        console.print("[normal1]Try again:[/]", end=" ")
        video_link = input()
        video_obj  = vid_link_checker(video_link)
    
    console.print("")
    return video_obj



def get_start_end(limit, from_video, to_video):
    if not (from_video and to_video):
        console.print("[normal1]Enter the [normal2]start[/] and [normal2]end[/] of the videos you want to download separated by a [normal2]space[/] or [normal2]leave empty[/] to select all: [/]", end="")
        start_end = input().split(" ")
    else:
        start_end = [from_video, to_video]
    
    while True:
        # The user left the input blank, meaning they want to download all the videos in the playlist.
        if len(start_end) == 1 and not start_end[0]:
            return -1

        elif len(start_end) == 2:
            try:
                if int(start_end[0]) > limit or int(start_end[1]) > limit:
                    console.print(f"\n[warning1]The [warning2]start[/] and [warning2]end[/] cannot be greater than the [warning2]limit[/] ([warning2]{limit}[/]). You input: [warning2]{start_end}[/]\nTry again: [/]", end="")
                    continue
                if int(start_end[0]) > int(start_end[1]):
                    console.print(f"\n[warning1]The [warning2]start[/] cannot be greater than the [warning2]end[/]. You input: [warning2]{start_end}[/]\nTry again: [/]", end="")
                    continue
                
                if start_end[0] == "0":
                    return [1, int(start_end[1])]
                return [int(start_end[0]), int(start_end[1])]

            except:
                console.print(f"\n[warning1]Invalid input: [warning2]{start_end}[/]\nTry again: [/]", end="")
                continue
        
        console.print(f"\n[warning1]Invalid input. Requested [warning2]two numbers[/] but got [warning2]{len(start_end)}[/] inputs: [warning2]{start_end}[/]\nTry again: [/]", end="")
        start_end = input().split(" ")



def get_vid_objs_from_file(path="individual-video-links.txt"):
    if not os.path.exists(path):
        with open(path, "w"):
            return []
    with open(path, "r") as links:
        vid_objs = []
        for link_num, link in enumerate(links):
            vid_objs.append(vid_link_checker(link))
            if not vid_objs[-1]:
                console.print(f"\n[warning1][warning2]Error[/] encountered with video nubmer [warning2]{link_num+1}[/]: [warning2]{link}[/][/]")
                console.print("[warning1]This is not a valid [warning2]link[/] for a YouTube video.[/]")
                vid_objs.pop()
    return vid_objs



def get_vid_objs_from_playlist(playlist_link, from_video, to_video):
    if not playlist_link:
        console.print("[normal1]Enter a [normal2]link[/] to a YouTube playlist: [/]", end="")
        playlist_link = input()
    link_valid = False

    # Check if the playlist link is valid
    while(not link_valid):
        try:
            playlist_obj = Playlist(playlist_link)
            len(playlist_obj) # this line triggers the `KeyError: 'list'` exception if the link is invalid
            link_valid = True
        except:
            console.print(f"\n[warning1]([warning2]{playlist_link}[/]) is not a valid [warning2]link[/] for a YouTube playlist.\nTry again: [/]", end="")
            playlist_link = input()
    console.print("")

    # Choose the start and end of videos to download
    console.print(f"[normal1]Playlist: [normal2]{playlist_obj.title}[/][/]")
    console.print(f"[normal1]There are [normal2]{len(playlist_obj)}[/] videos in this playlist.[/]")
    start_end = get_start_end(len(playlist_obj), from_video, to_video)
    
    if start_end == -1:
        start_end = [1, len(playlist_obj)]

    # Adding start_count[0] (i.e. first video number) to the output list
    vid_objs = [start_end[0]]
    
    # Adding the playlist's name to the output list
    vid_objs.append(playlist_obj.title)

    # Get the playlist's video objects
    for link_num, link in enumerate(playlist_obj[int(start_end[0])-1 : int(start_end[1])]):
        vid_objs.append(vid_link_checker(link))
        if not vid_objs[-1]:
            console.print(f"\n[warning1][warning2]Error[/] encountered with video number [warning2]{start_end[0] + link_num}[/]: [warning2]{link}[/][/]")
            console.print("[warning1]This is not a valid [warning2]link[/] for a YouTube video.[/]")
            vid_objs.pop()
    
    console.print("")
    return vid_objs
