"""
This is the main entry point for the entire script.
"""

from sys import  argv
from glob import glob
from global_imports import *
from playsound import playsound
import youtube_object_helper as yoh
import video_metadata as vmd
import download_helper as dh
import tui_helper as tui
from datetime import datetime as dt

def download_one_video(video_link: str) -> bool:
    """
    Description:
        Download only one video (two streams if `merge_option` is `True`, otherwise only one stream).
    ---
    Parameters:
        `video_link` (`str`)
            A link to a youtube video.
    ---
    Returns:
        (`bool`) => Whether to continue the script with the same mode or end it.
    """
    
    # Createing a video object from the user input link
    vid_obj = yoh.get_vid_obj(video_link)
    
    # Removing stupid colons and unsupported characters for a filename
    valid_filename    = dh.format_name(vid_obj.title, pytube_format=True)
    # if vid_obj.title[0].isnumeric() or vid_obj.title[1].isnumeric() or vid_obj.title.split(" ", maxsplit=1)[0].lower() == "part":
        # formated_filename = dh.format_name(vid_obj.title.split(" ", maxsplit=1)[1])
    # else:
    formated_filename = dh.format_name(vid_obj.title)
    
    # Checking if the video is already downloaded before doing anything
    if os.path.isfile(formated_filename + " (Merged).mp4"):
        console.print("[exists]This [normal2]video[/] is already downloaded[/]\n")
        continue_option_choice = tui.issue_yes_no_question("Download another video?")
        console.print("")
        return continue_option_choice != 0
    
    # Getting the metadata of the video
    vid_streams_dict = vmd.get_vid_metadata(vid_obj)
    
    console.print(f"[normal1]Video Title : [normal2]{vid_obj.title}[/][/]")
    vid_duration = divmod(vid_obj.length, 60)
    console.print(f"[normal1]Duration    : [normal2]{vid_duration[0]:02}[/]:[normal2]{vid_duration[1]:02}[/] min{'s' if vid_duration[0] > 1 else ''}[/]", end="  |  ")
    console.print(f"[normal1]Release Date: [normal2]{vid_obj.publish_date.strftime('%m/%d/%Y')}[/][/]\n")
    console.print("[normal1]A list of all the [normal2]available streams[/] is being fetched...[/]\n")
    
    # Printing the available streams
    console.print("[normal1]Available [normal2]streams[/] are:[/]")
    console.print(f"[normal1]{'='*22}[/]")
    
    # Returns the number of streams in each category
    categories_lengths = vmd.print_streams(vid_streams_dict)
    
    # Option_1: Downloading a video & an audio streams then mergeing them with ffmpeg
    # merge_option = 0
    # if "video/mp4" in vid_streams_dict and "audio/mp4" in vid_streams_dict:
    merge_option = tui.issue_yes_no_question("Download two separate streams then merge them?", 1, [1, 2], ["One stream", "Two streams"], [1, 2])
    console.print("")
    
    selected_streams_pointers = []
    # Choices >> [Categories and resolutions] >> Ex: [1, 5, 4, 1]
    selected_streams_pointers = dh.select_streams(merge_option,  categories_lengths, False)
    
    if selected_streams_pointers[0]: # If the only item != 0
        # ["video/mp4", "audio/mp4", ...]
        streams_categories = list(vid_streams_dict.keys())
        selected_stream = vid_streams_dict[streams_categories[selected_streams_pointers[0]-1]][selected_streams_pointers[1]-1]
        
        console.print(f"[normal1]Downloading [normal2]{selected_stream[0].mime_type}[/], [normal2]{selected_stream[0].resolution if selected_stream[0].type == 'video' else selected_stream[0].abr}[/], [normal2]{selected_stream[2].strip()}[/]...[/]")
        
        # Downloading one stream (the first in case of merge_option)
        dh.check_stream_existence(selected_stream[0], formated_filename, valid_filename)
        
        # Downloading two streams
        if merge_option:
            selected_stream = vid_streams_dict[streams_categories[selected_streams_pointers[2]-1]][selected_streams_pointers[3]-1]
            console.print(f"[normal1]Downloading [normal2]{selected_stream[0].mime_type}[/], [normal2]{selected_stream[0].abr if selected_stream[0].type == 'audio' else selected_stream[0].resolution}[/], [normal2]{selected_stream[2].strip()}[/]...[/]")
            dh.check_stream_existence(selected_stream[0], formated_filename, valid_filename)
            
            # Merging the video & audio streams
            dh.merge_streams(formated_filename, selected_stream[1])
            playsound(os.path.join(os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"), "SFX/Yay.mp3"))
    
    # Option_2: Downloading video description
    vid_description_option = tui.issue_yes_no_question("Download video description?")
    console.print("")
    if vid_description_option:
        dh.optional_downloads(formated_filename, "Description", vid_obj)
    
    continue_option_choice = tui.issue_yes_no_question("Download another video?")
    console.print("")
    return continue_option_choice != 0



def download_many_videos(from_playlist=True, playlist_link="", from_video=0, to_video=0) -> bool:
    """
    Description:
        Download many videos from a playlist or individual videos using links from a file.
    ---
    Parameters:
        `from_playlist` (`bool`)
            Whether to download from a playlist or individual videos using links from a file.
        
        `playlist_link` (`str`)
            A link to a playlist.
        
        `from_video`    (`int`)
            The start video number to start downloading from (playlist only).
        
        `to_video`      (`int`)
            The number of the last video to download (playlist only).
    ---
    Returns:
        (`bool`) => Whether to continue the script with the same mode or not.
    """
    
    # Creating video objects from the (playlist link/file containing individual video links)
    start_video_number = 1
    if from_playlist:
        vid_objs = yoh.get_vid_objs_from_playlist(playlist_link, from_video, to_video)
        start_video_number = vid_objs.pop(0)
        playlist_name = vid_objs.pop(0)       
        
        # To reset the current working directory in case of continuing the script.
        os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Downloads"))
        
        # Creating a new directory with the name of the playlist then `cd`ing to it
        formated_playlist_name = dh.format_name(playlist_name)
        os.makedirs(formated_playlist_name, exist_ok=True)
        os.chdir(formated_playlist_name)
    else:
        # Creating a new directory with name in the format "{current date}, {time}" then `cd`ing to it
        # Date/time formats: https://www.programiz.com/python-programming/datetime/strftime
        formated_download_directory_name = dt.now().strftime("%Y-%m-%d, %I-%M-%S %p")
        os.makedirs(formated_download_directory_name, exist_ok=True)
        os.chdir(formated_download_directory_name)
        vid_objs = yoh.get_vid_objs_from_file()
    
    console.print(f"[normal1]Below are the [normal2]{'playlist videos' if from_playlist else 'videos'}[/] {'you selected for download' if from_playlist else 'from the provided links'}:[/]")
    console.print(f"[normal1]{'='*56 if from_playlist else '='*45}[/]")
    
    # Getting the metadata of the video objects
    total_size      = 0
    total_duration  = 0
    selected_streams_for_download = []
    
    for obj_num, vid_obj in enumerate(vid_objs, start_video_number):
        # Removing stupid colons and unsupported characters for a filename
        valid_filename    = dh.format_name(vid_obj.title, pytube_format=True)
        if vid_obj.title[0].isnumeric() or vid_obj.title[1].isnumeric() or vid_obj.title.split(" ", maxsplit=1)[0].lower() == "part":
            formated_filename = dh.format_name(str(obj_num) + ". " + vid_obj.title.split(" ", maxsplit=1)[1])
        else:
            formated_filename = dh.format_name(str(obj_num) + ". " + vid_obj.title)
        
        # Checking if the video is already downloaded before doing anything
        if os.path.isfile(formated_filename + " (Merged).mp4"):
            console.print("[exists]This [normal2]video[/] is already downloaded[/]\n")
            console.print(f"[normal1]{'='*42}[/]")
            console.print("")
            continue
        
        total_duration += vid_obj.length
        mins, secs = divmod(vid_obj.length, 60)
        hours = 0
        if mins > 59:
            hours, mins = divmod(mins, 60)
        
        console.print(f"[normal1]Duration: [normal2]{format(hours, '02')+':' if hours else ''}[/][normal2]{mins:02}[/]:[normal2]{secs:02}[/][/]", end="  |  ")
        console.print(f"[normal1]Release Date: [normal2]{vid_obj.publish_date.strftime('%d-%m-%Y')}[/][/]")
        console.print(f"[normal1]Video #[exists]{obj_num}[/]: [normal2]{vid_obj.title}[/][/]\n")
        
        # Printing the available streams
        console.print("[normal1]Available streams are:[/]")
        console.print(f"[normal1]{'='*22}[/]")
        
        # {"video/mp4": [[stream_obj, vid_obj.video_id, str_file_size, file_size], ...],
        # "audio/mp4": ...}
        vid_streams_dict = vmd.get_vid_metadata(vid_obj)
        
        # Returns the number of streams in each category
        categories_lengths = vmd.print_streams(vid_streams_dict)
        
        # Option_1: Download video & audio streams then merge them with ffmpeg
        #/// (Commented because I never download only a video or an audio stream without the merge option when downloading from a playlist)
        # merge_option = 0
        # if "video/mp4" in vid_streams_dict and "audio/mp4" in vid_streams_dict:
            #/// if not from_playlist:
        merge_option = tui.issue_selection_question("Choose from the following options: ", ["Download only one stream", "Download and merge two separate streams", "Skip this one", "Skip all"], 1, [1, 2, 0, -1])
        console.print("")
            #/// This is to skip the merge_option input process (continuing from the above commented part).
            #/// merge_option = 1
        
        if merge_option == 0:  # i.e., 'skip this one'
            continue
        if merge_option == -1: # i.e., 'skip all'
            break
        
        selected_streams_pointers = []
        # Choices >> [Categories and resolutions] >> Ex: [1*, 5, 2*, 1] (* means fixed value if res_only == True)
        
        selected_streams_pointers = dh.select_streams(merge_option,  categories_lengths, res_only = False)
        
        if selected_streams_pointers[0]: # If the only item != 0
            # Downloading video description
            dh.optional_downloads(formated_filename, "Description", vid_obj)
            
            # ["video/mp4", "audio/mp4", ...]
            streams_categories = list(vid_streams_dict.keys())
            
            # Getting the selected category and resolution option (for the first in case of merge_option)
            first_selected_stream = vid_streams_dict[streams_categories[selected_streams_pointers[0]-1]][selected_streams_pointers[1]-1]
            
            # Adding streams to the selected streams list
            if merge_option == 1: # "Download only one stream"
                selected_streams_for_download.append(dh.format_selected_vid_streams_into_dict(formated_filename, valid_filename, first_selected_stream))
                total_size += first_selected_stream[3]
                console.print(f"[normal1]The next [normal2]{first_selected_stream[0].type}[/] stream has been added to the download list: [normal2]{first_selected_stream[0].mime_type}[/], [normal2]{first_selected_stream[0].resolution if first_selected_stream[0].type == 'video' else first_selected_stream[0].abr}[/], [normal2]{first_selected_stream[2].strip()}[/]...[/]\n")
            
            else: # "Download and merge two separate streams"
                second_selected_stream = vid_streams_dict[streams_categories[selected_streams_pointers[2]-1]][selected_streams_pointers[3]-1]
                selected_streams_for_download.append(dh.format_selected_vid_streams_into_dict(formated_filename, valid_filename, first_selected_stream, second_selected_stream))
                total_size += first_selected_stream[3] + second_selected_stream[3]
                
                console.print("[normal1]The next [normal2]video[/] & [normal2]audio[/] streams have been added to the download list:[/]")
                console.print(f"[normal1][normal2]{first_selected_stream[0].mime_type}[/], [normal2]{first_selected_stream[0].resolution if first_selected_stream[0].type == 'video' else first_selected_stream[0].abr}[/], [normal2]{first_selected_stream[2].strip()}[/][/]")
                console.print(f"[normal1][normal2]{second_selected_stream[0].mime_type}[/], [normal2]{second_selected_stream[0].abr if second_selected_stream[0].type == 'audio' else second_selected_stream[0].resolution}[/], [normal2]{second_selected_stream[2].strip()}[/][/]\n")
        console.print(f"[normal1]{'='*42}[/]")
        console.print("")
    
    # Downloading selected streams
    if not len(selected_streams_for_download):
        console.print("[warning1]No [warning2]streams[/] were selected for download![/]\n")
    else:
        console.print(f"[normal1][normal2]{len(selected_streams_for_download)}[/] stream{'s have' if len(selected_streams_for_download) > 1 else ' has'} been added to the download list. The streams are:[/]")
        console.print(f"[normal1]{'=' * (len( str( len(selected_streams_for_download) ) ) + 62)}[/]")
        for stream in selected_streams_for_download:
            if stream.get('video'):
                console.print(f"[normal1]Title: [normal2]{stream['video'][0][0].title}[/][/]")
                console.print(f"[normal1]Info : [normal2]{stream['video'][0][0].mime_type}[/], [normal2]{stream['video'][0][0].resolution}[/], [normal2]{stream['video'][0][2].strip()}[/]", end="  +  " if stream.get('audio') else "\n")
            
            if stream.get('audio'):
                if not stream.get('video'):
                    console.print(f"[normal1]Title: [normal2]{stream['audio'][0][0].title}[/]\nInfo: [/]", end="")
                console.print(f"[normal1][normal2]{stream['audio'][0][0].mime_type}[/], [normal2]{stream['audio'][0][0].abr}[/], [normal2]{stream['audio'][0][2].strip()}[/][/]")
            console.print("")
        
        mins, secs = divmod(total_duration, 60)
        hours = 0
        if mins > 59:
            hours, mins = divmod(mins, 60)
        
        console.print(f"[normal1]Total size:     [normal2]{format(total_size / 1024, '.2f')+'[/] GB' if total_size >= 1024 else format(total_size, '.2f')+'[/] MB'}[/]")
        console.print(f"[normal1]Total Duration: [normal2]{format(hours, '02')+':' if hours else ''}[/][normal2]{mins:02}[/]:[normal2]{secs:02}[/][/]\n") # min{'s' if int(total_duration[0])>1 else ''}
        if tui.issue_yes_no_question("Confirm download?", 1):
            console.print("")
            no_subtitles = tui.issue_yes_no_question("Download subtitles?", 1, [1, 0])
            while True:
                console.print("")
                selected_streams_for_download = dh.download_streams(selected_streams_for_download, no_subtitles)
                if len(selected_streams_for_download):
                    console.print(f"[warning1]The following streams were not/partially downloaded:\n")
                    console.print(f"[normal1]{'='*51}[/]")
                    console.print('\n'.join([fd.get('video', fd.get('audio'))[1] for fd in selected_streams_for_download]))
                    console.print("")
                    if not tui.issue_yes_no_question("Retry downloading failed videos?", 1):
                        console.print("")
                        break
                else:
                    break
            playsound(os.path.join(os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"), "SFX/Yay.mp3"))
        else:
            console.print("\n[warning1]][warning2]Download[/] cancelled...[/]\n")
    
    if from_playlist:
        continue_option_choice = tui.issue_yes_no_question("Download another playlist?")
        console.print("")
        return continue_option_choice != 0
    else:
        return False

if __name__ == "__main__":
    console.print("[exists]Initializing script...[/]")
    terminal_argument_link = ""
    
    if len(argv) > 1:
        if argv[1] in ["help", "-h", "--help"]:
            console.print("""
[normal1]python "[normal1]The_Refactored.py" \[[normal2]script_mode[/]] \[[normal2]target_link[/]] \[[normal2]from_video[/]] \[[normal2]to_video[/]]

[normal2]script_mode[/] : [normal2]1/blank[/] -> download one video
            : [normal2]2[/]       -> fetch links from a file
            : [normal2]else[/]    -> download a playlist[/]

[normal2]target_link[/] : A link for a [normal2]single video[/] when downloading [normal2]one video[/].
            : A link for a [normal2]playlist[/] when downloading a [normal2]playlist[/].

[normal2]from_video[/]  : The [normal2]video number[/] from where to start downloading when downloading a [normal2]playlist[/].

[normal2]to_video[/]    : The [normal2]video number[/] of the last video you want when downloading a [normal2]playlist[/].[/]""")
            
            choice = -999 # Skip and end the script.
        
        elif argv[1] == "-a":
            video_links = []
            if len(argv) > 2:
                video_links.extend((" ".join(argv[2:])).split(" "))
            else:
                console.print("[normal1]Enter the [normal2]links[/] to the [normal2]youtube videos[/] you want to download (enter a [normal2]blank line[/] to continue):[/]")
                while True:
                    link = input(f"> Link {len(video_links)+1:02}: ").strip()
                    if link == "":
                        break
                    video_links.extend(link.split(" "))
            yoh.add_links_to_file(video_links)
            choice = 2
        
        elif argv[1] == "1":
            choice = 1
        elif argv[1] == "2":
            choice = 2
        else:
            choice = False
        
        if len(argv) > 2:
            terminal_argument_link = argv[2]
    else:
        console.print("[normal1]Choose a mode: ([normal2]1[/]:ONE VIDEO  |  [normal2]2[/]:links from file  |  [normal2]else[/]:playlist): [/]", end="")
        choice = tui.issue_selection_question("Choose one mode:", ["One video", "Links from file", "Playlist"], 0, [1, 2, 3])
        console.print("")
    
    if choice != -999:
        while True:
            if choice == 1:
                continue_option = download_one_video(video_link = terminal_argument_link)
            elif choice == 2:
                continue_option = download_many_videos(from_playlist = False)
            else:
                if len(argv) > 4:
                    continue_option = download_many_videos(playlist_link = terminal_argument_link, from_video=int(argv[3]), to_video=int(argv[4]))
                else:
                    continue_option = download_many_videos(playlist_link = terminal_argument_link)
            if not continue_option:
                console.print("[normal1][normal2]Exiting[/]... Opening the [normal2]download location[/] and pointing to the [normal2]newest file[/] now...[/]")
                # os.startfile(os.getcwd())
                list_of_files = glob("*.mp4") # * means all. To target a specific file extension: `*.mp4`
                latest_file = max(list_of_files, key=os.path.getctime)
                os.system(f"explorer /select, \"{latest_file}\"")
                break
            
            # Clear the previously entered video link and terminal arguments if another iteration is happening:
            terminal_argument_link = ""
            argv = [argv[0]]
    # playsound(os.path.join(os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"), "SFX/goodbye-old-friend.mp3"))
