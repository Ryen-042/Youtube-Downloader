from pytube import YouTube, Playlist 
from rich.console import Console
from rich.theme import Theme



## Available functions in this module:
# ['on_complete',  'on_progress',   'vid_link_checker',
#  'get_vid_obj',  'get_start_end', 'get_vid_objs_from_file',
#  'get_vid_objs_from_playlist']



custom_theme = Theme({
    "normal1"       :   "bold blue1 on grey23",
    "normal2"       :   "bold dark_violet",
    "warning1"      :   "bold plum4 on grey23",
    "warning2"      :   "bold red"
})

console = Console(theme=custom_theme)



def on_complete(stream, file_path):
    # Print only the path to the downloaded file, not including the file's name as it is changed after downloading.
    path_to_file = '\\'.join((file_path.split('\\')[:-1]))
    console.print(f"[normal1]File downloaded successfully in the next path: [normal2]{path_to_file}[/][/]\n")



def on_progress(stream, chunk, bytes_remaining):
    console.print(f"{round(100 - bytes_remaining/stream.filesize * 100, 2)}% | {round((stream.filesize - bytes_remaining)/1000/1000, 2)} : {round(stream.filesize/1000/1000, 2)} MB", end="")
    
    # To erase and return the curson to the beginning of the current line.
    # https://stackoverflow.com/questions/5290994/remove-and-replace-printed-items

    # Usage of 'r' leaves the previously printed characters if they are not overridden.
    # Also, 'r' does not work with console.print().
    
    print('\033[2K\033[1G', end="")
    
    # In theory, visually speaking, the previously line is equivalent to:
    # print("\r", end="")
    # print(" " * 100, end="") # (100) is some arbitrary number.
    # print("\r", end="")



def vid_link_checker(link):
    try:
        return YouTube(link, on_complete_callback=on_complete, on_progress_callback=on_progress)
    except:
        return False



def get_vid_obj():
    console.print("[normal1]Enter a [normal2]link[/] to a YouTube video:[/]", end=" ")
    link_valid = False

    while(not link_valid):
        link = input()
        link_valid = vid_link_checker(link)
        if not link_valid:
            console.print(f"\n[warning1]([warning2]{link}[/]) is not a valid link for a YouTube video.[/]")
            console.print("[normal1]Try again:[/]", end=" ")
    
    console.print("")
    return link_valid



def get_start_end(limit):
    console.print("[normal1]Enter the [normal2]start[/] and [normal2]end[/] of the videos you want to download separated by a [normal2]space[/] or [normal2]leave empty[/] to select all: [/]", end="")
    while True:
        start_end = input().split(" ")
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
                
                return [int(start_end[0]), int(start_end[1])]

            except:
                console.print(f"\n[warning1]Invalid input: [warning2]{start_end}[/]\nTry again: [/]", end="")
                continue
        
        console.print(f"\n[warning1]Invalid input: [warning2]{start_end}[/]\nTry again: [/]", end="")



def get_vid_objs_from_file(path="individual-video-links.txt"):
    with open(path, 'r') as links:
        vid_objs = []
        for link_num, link in enumerate(links):
            vid_objs.append(vid_link_checker(link))
            if not vid_objs[-1]:
                console.print(f"\n[warning1][warning2]Error[/] encountered with video nubmer [warning2]{link_num+1}[/]: [warning2]{link}[/][/]")
                console.print("[warning1]This is not a valid [warning2]link[/] for a YouTube video.[/]")
                vid_objs.pop()
    return vid_objs



def get_vid_objs_from_playlist():
    console.print("[normal1]Enter a [normal2]link[/] to a YouTube playlist: [/]", end="")
    link_valid = False

    # Check if the playlist link is valid
    while(not link_valid):
        playlist_link = input()
        try:
            playlist_obj = Playlist(playlist_link)
            len(playlist_obj) # this line triggers the `KeyError: 'list'` exception if the link is invalid
            link_valid = True
        except:
            console.print(f"\n[warning1]([warning2]{playlist_link}[/]) is not a valid [warning2]link[/] for a YouTube playlist.\nTry again: [/]", end="")
    console.print("")

    # Choose the start and end of videos to download
    console.print(f"[normal1]There are [normal2]{len(playlist_obj)}[/] videos in the playlist.[/]")
    start_end = get_start_end(len(playlist_obj))
    
    if start_end == -1:
        start_end = [1, len(playlist_obj)]

    # Get the playlist's video objects
    vid_objs = []
    for link_num, link in enumerate(playlist_obj[int(start_end[0])-1 : int(start_end[1])]):
        vid_objs.append(vid_link_checker(link))
        if not vid_objs[-1]:
            console.print(f"\n[warning1][warning2]Error[/] encountered with video nubmer [warning2]{start_end[0] + link_num}[/]: [warning2]{link}[/][/]")
            console.print("[warning1]This is not a valid [warning2]link[/] for a YouTube video.[/]")
            vid_objs.pop()
    
    console.print("")
    return vid_objs
