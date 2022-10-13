"""
This module provides functions for dealing with pytube `YouTube` objects.
"""
from __future__ import annotations
from pytube import YouTube, Playlist, request
# from pytube.cli import on_progress as pytube_on_progress
from shutil import get_terminal_size
from traceback import print_exc # also format_exc
from global_imports import *

# TYPE_CHECKING: A special constant that is assumed to be True by 3rd party static type checkers. It is False at runtime. Usage:
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Union
    from pytube.streams import Stream

## Available functions in this module:
# ['on_complete',  'on_progress',   'vid_link_checker',
#  'get_vid_obj',  'get_start_end', 'get_vid_objs_from_file',
#  'add_links_to_file', 'get_vid_objs_from_playlist']


#~ https://github.com/pytube/pytube/issues/1035
# To change the value here to something smaller to decrease chunk sizes, thus increasing the number of times that the progress callback occurs:
request.default_range_size = int(9437184/9*5) # 5MB chunk size

#~ To change the look of the built-in progress bar in pytube, modify the `display_progress_bar` function by adding these lines in the `cli.py` file:
# mbytes_remaining = round( ( filesize - (filesize - bytes_received) ) /1024/1024, 2)
# text = f"{mbytes_remaining:>7}:{round(filesize/1024/1024, 2)} MB | {progress_bar} | {percent}%\r"



def on_complete(stream: Stream, file_path: str) -> None:
    """
    Description:
        Called at the end of the execution of the `Stream.download()` method.
    ---
    Parameters:
        `stream` (`Stream`).
        
        `file_path` (`str`)
            The path to the downloaded stream.
    ---
    Returns: `None`.
    """
    
    # Print only the path to the downloaded file, not including the file's name as it is changed after downloading.
    path_to_file = '\\'.join((file_path.split('\\')[:-1]))
    console.print(f"[normal1]File downloaded successfully in the next path: [normal2]{path_to_file:113}[/][/]\n")



def on_progress(stream: Stream, chunk: bytes, bytes_remaining: int) -> None:
    """
    Description:
        Called after downloading a new chunk of data to print out a progress bar.
    ---
    Parameters:
        `stream` (`Stream`).
        
        `chunk` (`bytes`).
        
        `bytes_remaining` (`int`).
    
    ---
    Returns: `None`.
    """
    char_empty   = "░" # ▄ ░ ▒ ▓
    char_fill    = "█"
    scale        = 0.55
    columns      = get_terminal_size().columns
    max_width    = int(columns * scale)
    filled       = int(round(max_width * (stream.filesize - bytes_remaining)/stream.filesize))
    remaining    = max_width - filled
    progress_bar = char_fill * filled + char_empty * remaining
    percent      = round((stream.filesize - bytes_remaining) / stream.filesize * 100, 2)
    text         = f"[normal1]\[[normal2]{format((stream.filesize - bytes_remaining)/1024/1024, '.2f') + '[/] / [normal2]' + format(stream.filesize/1024/1024, '.2f')+'[/]] MB':36} | [exists]{progress_bar}[/] | [normal2]{format(bytes_remaining/1024/1024, '.2f')+'[/] MB — [normal2]'+format(percent, '.2f')+'[/] %':37}[/]"
    console.print(text, end="")
    # console.print(f"[normal1][nprmal2]{round(100 - bytes_remaining/stream.filesize * 100, 2):< 7.2f}[/] % | [normal2]{round((stream.filesize - bytes_remaining)/1024/1024, 2)}[/]:[normal2]{round(stream.filesize/1024/1024, 2)}[/] MB[/]", end="")
    
    # To erase and return the curson to the beginning of the current line.
    # https://stackoverflow.com/questions/5290994/remove-and-replace-printed-items
    
    # Usage of 'r' leaves the previously printed characters if they are not overridden.
    # Also, 'r' does not work with console.print().
    
    # print('\033[2K\033[1G', end="") # Doesn't work with CMD
    
    # In theory, visually speaking, the previously line is equivalent to:
    print("\r", end="")
    # print(" " * 100, end="\r") # (100) is some arbitrary number.



def vid_link_checker(link: str) -> Union[YouTube, bool]:
    """
    Description:
        Checks if the provided link is valid and returns a `YouTube` object if so, otherwise returns `False`.
    ---
    Parameters:
        `link` (`str`)
            A link to a youtube video.
    ---
    Returns:
        (`YouTube` | `bool`) => A `YouTube` object if the provided `link` is valid, otherwise `False`.
    """
    
    try:
        return YouTube(link, on_complete_callback=on_complete, on_progress_callback=on_progress) # pytube_on_progress
    except:
        return False



def get_vid_obj(video_link = "") -> YouTube:
    """
    Description:
        If no argument is provided, asks the user for a youtube link, checks if it is valid then returns a `YouTube` object if so,
        otherwise asks the user again for a new link.
    ---
    Parameters:
        `video_link` (`str`)
            A link to a youtube video.
    ---
    Returns: A `Youtube` object.
    """
    
    if not video_link:
        console.print("[normal1]Enter a [normal2]link[/] to a YouTube video:[/]", end=" ")
        video_link = input().strip()
    video_obj = vid_link_checker(video_link)
    while not video_obj:
        console.print(f"\n[warning1]([warning2]{video_link}[/]) is not a valid link for a YouTube video.[/]")
        console.print("[normal1]Try again:[/]", end=" ")
        video_link = input().strip()
        video_obj  = vid_link_checker(video_link)
    
    console.print("")
    return video_obj



def get_start_end(limit: int, from_video: int=0, to_video: int=0) -> list[int]:
    """
    Description:
        Takes two optional numbers representing from where to start and end downloading videos from a playlist.
        
        If no numbers are given or if they are not valid numbers, it asks the user again.
    
    ---
    Parameters:
        `limit` (`int`)
            The count of the videos in the playlist.
        
        `from_video` (`int`)
            The start video number to start downloading from.
        
        `to_video` (`int`)
            The number of the last video to download.
    ---
    Returns:
        A list containing two numbers representing the first and last video numbers.
    """

    if not (from_video and to_video):
        console.print("[normal1]Enter the [normal2]start[/] and [normal2]end[/] of the videos you want to download separated by a [normal2]space[/] or [normal2]leave empty[/] to select all: [/]", end="")
        start_end = input().strip().split(" ")
    else:
        start_end = [from_video, to_video]
        if from_video == -1 and to_video == -1:
            return [1, limit]
    
    while True:
        # The user left the input blank, meaning they want to download all the videos in the playlist.
        if len(start_end) == 1 and not start_end[0]:
            return [1, limit]
        
        elif len(start_end) == 2:
            try:
                if int(start_end[0]) > limit or int(start_end[1]) > limit:
                    console.print(f"\n[warning1]The [warning2]start[/] and [warning2]end[/] cannot be greater than the [warning2]limit[/] ([warning2]{limit}[/]). Your input: [warning2]{start_end}[/]\nTry again: [/]", end="")
                
                # elif start_end[0] == 0:
                    # return [1, int(start_end[1])]
                
                # If end number is -1, then return the start and limit
                elif int(start_end[1]) == -1:
                    return [int(start_end[0]), limit]
                
                elif int(start_end[0]) > int(start_end[1]):
                    console.print(f"\n[warning1]The [warning2]start[/] cannot be greater than the [warning2]end[/]. Your input: [warning2]{start_end}[/]\nTry again: [/]", end="")
                
                else:
                    return [int(start_end[0]), int(start_end[1])]
            except:
                console.print(f"\n[warning1]Invalid input: [warning2]{start_end}[/]\nTry again: [/]", end="")
        else:
            console.print(f"\n[warning1]Invalid input. Requested [warning2]two numbers[/] but got [warning2]{len(start_end)}[/] inputs: [warning2]{start_end}[/]\nTry again: [/]", end="")
        
        start_end = input().strip().split(" ")



def get_vid_objs_from_file(path="individual-video-links.txt") -> list[YouTube]:
    """
    Description:
        Get video links from a file and return a `YouTube` object for each valid link.
    ---
    Parameters:
        `path` (`str`)
            The path to the file containing the video links.
    ---
    Returns: A list of `YouTube` objects.
    """
    
    path_to_links_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    if not os.path.exists(path_to_links_file):
        # Create an empty file and return an empty list (i.e., no links):
        with open(path, "w", encoding='utf-8'):
            return []
    
    with open(path_to_links_file, "r", encoding='utf-8') as links:
        vid_objs = []
        for link_num, link in enumerate(links):
            vid_objs.append(vid_link_checker(link))
            if not vid_objs[-1]:
                console.print(f"\n[warning1][warning2]Error[/] encountered with video nubmer [warning2]{link_num+1}[/]: [warning2]{link}[/][/]")
                console.print("[warning1]This is not a valid [warning2]link[/] for a YouTube video.[/]")
                vid_objs.pop()
    return vid_objs



def add_links_to_file(video_links: list[str]=None, path="individual-video-links.txt") -> None:
    """
    Description:
        Get video links from user and add them to a file.
    ---
    Parameters:
        `path` (`str`)
            The path to the file containing where the video links will be stored.
    ---
    Returns: `None`.
    """
    
    path_to_links_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    
    with open(path_to_links_file, "w", encoding='utf-8') as links_file:
        links_file.write("\n".join(video_links))


def get_vid_objs_from_playlist(playlist_link: str, from_video: int=0, to_video: int=0) -> list[YouTube]:
    """
    Description:
        Takes a link for a playlist and returns a list of `YouTube` video objects in the specified range between `from_video` and `to_video`.
    ---
    Parameters:
        `playlist_link` (`str`)
            A link for a youtube playlist.
            
        `from_video` (`int`)
            The start video number to start downloading from.
            
        `to_video`   (`int`)
            The number of the last video to download.
    ---
    Returns: A list of `YouTube` objects.
    """
    
    if not playlist_link:
        console.print("[normal1]Enter a [normal2]link[/] to a YouTube playlist: [/]", end="")
        playlist_link = input().strip()
    
    # Check if the playlist link is valid
    while(True):
        try:
            playlist_obj = Playlist(playlist_link)
            len(playlist_obj) # this line triggers the `KeyError: 'list'` exception if the link is invalid
            break
        except KeyError:
            console.print(f"\n[warning1]([warning2]{playlist_link}[/]) is not a valid [warning2]link[/] for a YouTube playlist.\nTry again:[/]", end=" ")
        # except URLError:
            # console.print("[warning2]Internect Connection Error![/]")
            # console.print(f"[warning2]{print_exc()}[/]\n")
        except:
            console.print("[warning1]Something went wrong. It could have been a network connection error.")
            print_exc()
            console.print("")
            console.print("[warning1]Try again! Enter a link to a YouTube playlist:[/]", end=" ")
        playlist_link = input().strip()
    console.print("")
    
    # Choose the start and end of videos to download
    console.print(f"[normal1]Playlist: [normal2]{playlist_obj.title}[/][/]")
    console.print(f"[normal1]There are [normal2]{len(playlist_obj)}[/] videos in this playlist.[/]\n")
    start_end = get_start_end(len(playlist_obj), from_video, to_video)
    
    # Adding start_count[0] (i.e. first video number) to the output list
    vid_objs = [start_end[0]]
    
    # Adding the playlist's name to the output list
    vid_objs.append(playlist_obj.title)
    
    # Get the playlist's video objects
    for link_num, link in enumerate(playlist_obj[start_end[0]-1 : start_end[1]]):
        vid_objs.append(vid_link_checker(link))
        if not vid_objs[-1]:
            console.print(f"\n[warning1][warning2]Error[/] encountered with video number [warning2]{start_end[0] + link_num}[/]: [warning2]{link}[/][/]")
            console.print("[warning1]This is not a valid [warning2]link[/] for a YouTube video.[/]")
            vid_objs.pop()
    
    console.print("")
    return vid_objs
