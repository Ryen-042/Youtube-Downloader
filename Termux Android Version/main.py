from global_imports import *
from sys import  argv
from glob import glob
import Links_and_Objects as lo, Video_Metadata as vmd, Utility as ut



def download_one_video(video_link):
    # Generate a video object from the user input link
    vid_obj = lo.get_vid_obj(video_link)

    # Getting the metadata of the video
    vid_streams_dict = vmd.get_vid_metadata(vid_obj)

    console.print(f"[normal1]Video Title: [normal2]{vid_obj.title}[/][/]")
    vid_duration = divmod(vid_obj.length, 60)
    console.print(f"[normal1]Duration   : [normal2]{vid_duration[0]:02}[/]:[normal2]{vid_duration[1]:02}[/] min{'s' if vid_duration[0] > 1 else ''}[/]\n")

    # remove stupid colons and unsupported characters for a filename
    valid_filename    = ut.format_name(vid_obj.title, "#\'.,%]")
    if vid_obj.title[0].isnumeric() or vid_obj.title.split(" ", maxsplit=1)[0].lower() == "part":
        formated_filename = ut.format_name(vid_obj.title.split(" ", maxsplit=1)[1])
    else:
        formated_filename = ut.format_name(vid_obj.title)
    
    # Check if the video is already downloaded before doing anything
    if os.path.isfile(formated_filename + " (Merged).mp4"):
        console.print("[exists]This [normal2]video[/] is already downloaded[/]")
        console.print("[normal1]Do you want to download another [normal2]video[/]? ([normal2]1[/]:yes, [normal2]else[/]:NO): [/]", end="")
        continue_option = ut.yes_no_choice()
        return continue_option

    console.print("[normal1] A list of all the [normal2]available streams[/] is being fetched...[/]\n")

    # printing the available streams
    console.print("[normal1]Available [normal2]streams[/] are:[/]")
    console.print(f"[normal1]{'='*22}[/]")
    # [number_of_categories, [number of streams in each category]]
    categories_lengths = vmd.print_streams(vid_streams_dict)
    

    # Option_1: Download video & audio streams then merge them with ffmpeg
    merge_option = False
    if "video/mp4" in vid_streams_dict and "audio/mp4" in vid_streams_dict:
        console.print("[normal1]Download [normal2]video[/] & [normal2]audio[/] streams and merge them with ffmpeg? ([normal2]1[/]:YES, [normal2]else[/]:no): [/]", end="")
        merge_option = ut.yes_no_choice(blank_true=True)
    
    selected_streams = []
    selected_streams = ut.select_streams(merge_option,  categories_lengths, False)

    if(selected_streams[0]): # if not empty
        streams_categories = list(vid_streams_dict.keys())
        selected_stream = vid_streams_dict[streams_categories[int(selected_streams[0])-1]][int(selected_streams[1])-1]

        console.print(f"[normal1]Downloading [normal2]{selected_stream[1]}[/], [normal2]{selected_stream[-4] if merge_option or selected_stream[2] == 'video' else selected_stream[0].abr}[/], [normal2]{selected_stream[-2].strip()}[/]...[/]\n")

        if not merge_option:
            selected_stream[0].download()
            os.rename(valid_filename + ".mp4", formated_filename + ".mp4")

        else:
            ut.check_stream_existence(selected_stream[0], formated_filename, valid_filename, 'video')

            # Audio stream
            selected_stream = vid_streams_dict[streams_categories[int(selected_streams[2])-1]][int(selected_streams[3])-1]
            console.print(f"[normal1]Downloading [normal2]{selected_stream[1]}[/], [normal2]{selected_stream[0].abr}[/], [normal2]{selected_stream[-2].strip()}[/]...[/]\n")
            ut.check_stream_existence(selected_stream[0], formated_filename, valid_filename, 'audio')


            # Merging the video & audio streams
            ut.merge_streams(formated_filename, selected_stream[-5])


    # Option_2: Download video description
    console.print("[normal1]Download [normal2]video description[/]? ([normal2]1[/]:yes, [normal2]else[/]:NO): [/]", end="")
    vid_description_option = ut.yes_no_choice()
    if vid_description_option:
        ut.optional_downloads(formated_filename, "Description", vid_obj)

    console.print("[normal1]Do you want to download [normal2]another video[/]? ([normal2]1[/]:yes, [normal2]else[/]:NO): [/]", end="")
    continue_option = ut.yes_no_choice()
    return continue_option



def download_many_videos(from_playlist=True, playlist_link="", from_video=0, to_video=0):
    # Generate video objects from the (playlist input link/filepath containing video links)
    start_video_number = 1
    if from_playlist:
        vid_objs = lo.get_vid_objs_from_playlist(playlist_link, from_video, to_video)
        start_video_number = vid_objs.pop(0)
        playlist_name = vid_objs.pop(0)
        formated_playlist_name = ut.format_name(playlist_name)
        os.makedirs(formated_playlist_name, exist_ok=True)
        os.chdir(formated_playlist_name)
    else:
        vid_objs = lo.get_vid_objs_from_file()

    console.print(f"[normal1]Below are the [normal2]{'playlist videos' if from_playlist else 'videos'}[/] {'you selected for download' if from_playlist else 'from the provided links'}:[/]")
    console.print(f"[normal1]{'='*56 if from_playlist else '='*45}[/]")
    # Getting the metadata of the video objects
    total_size      = 0
    total_duration  = 0
    selected_streams_for_download = []
    for obj_num, vid_obj in enumerate(vid_objs, start_video_number):
        console.print(f"[normal1]Video number: [normal2]{obj_num}[/][/]", end="")
        
        vid_duration = divmod(vid_obj.length, 60)
        total_duration += vid_obj.length
        
        console.print(f"[normal1]  |  Duration: [normal2]{vid_duration[0]:02}[/]:[normal2]{vid_duration[1]:02}[/] min{'s' if vid_duration[0] > 1 else ''}[/]")
        console.print(f"[normal1]Video title:  [normal2]{vid_obj.title}[/][/]\n")

        # remove stupid colons and unsupported characters for a filename
        valid_filename    = ut.format_name(vid_obj.title, "#\'.,%]")
        if vid_obj.title[0].isnumeric() or vid_obj.title.split(" ", maxsplit=1)[0].lower() == "part":
            formated_filename = ut.format_name(vid_obj.title.split(" ", maxsplit=1)[1])
        else:
            formated_filename = ut.format_name(str(obj_num) + ". " + vid_obj.title)


        # Check if the video is already downloaded before doing anything
        if os.path.isfile(formated_filename + " (Merged).mp4"):
            console.print("[exists]This [normal2]video[/] is already downloaded[/]\n")
            console.print(f"[normal1]{'='*42}[/]")
            console.print("")
            continue

        # printing the available streams
        console.print("[normal1]Available streams are:[/]")
        console.print(f"[normal1]{'='*22}[/]")

        # {"video/mp4": [[stream_obj, stream.mime_type, stream.type, vid_obj.video_id,
        #                stream.resolution, stream.is_progressive, str_file_size, file_size], ...],
        # "audio/mp4": ...}
        vid_streams_dict = vmd.get_vid_metadata(vid_obj, True)
        
        # [number_of_categories, [number of streams in each category]]
        categories_lengths = vmd.print_streams(vid_streams_dict)


        # Option_1: Download video & audio streams then merge them with ffmpeg
        # (Commented because I don't rarely download audio and video stream without merging when downloading a playlist)
        # merge_option = False
        # if "video/mp4" in vid_streams_dict and "audio/mp4" in vid_streams_dict:
        #     console.print("[normal1]Download [normal2]video[/] & [normal2]audio[/] streams and merge them with ffmpeg?[/]")
        #     console.print("[normal1]Available options: ([normal2]1[/]:YES  |  [normal2]-1[/]:break  |  [normal2]else[/]:no): [/]", end="")
        #     merge_option = ut.yes_no_choice(blank_true=True)
        
        # this is to skip the merge_option input process because it is unnecessary for me.
        merge_option = True

        selected_streams = []
        if merge_option == -1: # i.e., 'skip'
                break
        else:
            # Choices >> [Categories and resolutions]
            selected_streams = ut.select_streams(merge_option,  categories_lengths, res_only = True)
        
        if(selected_streams[0]): # if not empty
            # [video/mp4, audio/mp4, ...]
            streams_categories = list(vid_streams_dict.keys())
            
            # Get the selected category and resolution option
            selected_stream = vid_streams_dict[streams_categories[int(selected_streams[0])-1]][int(selected_streams[1])-1]

            if not merge_option:
                if selected_stream[2] == 'video':
                    selected_streams_for_download.append(ut.format_selected_stream_into_dict(formated_filename, valid_filename, selected_stream))
                else:
                    selected_streams_for_download.append(ut.format_selected_stream_into_dict(formated_filename, valid_filename, selected_audio_stream=selected_stream))
                total_size     += selected_stream[-1]
                console.print(f"[normal1]The next [normal2]{selected_stream[2]}[/] stream has been added to the download list: [normal2]{selected_stream[1]}[/], [normal2]{selected_stream[-4] if selected_stream[2] == 'video' else selected_stream[0].abr}[/], [normal2]{selected_stream[-2].strip()}[/]...[/]\n")

            else:
                # Audio stream
                selected_audio_stream = vid_streams_dict[streams_categories[int(selected_streams[2])-1]][int(selected_streams[3])-1]
                selected_streams_for_download.append(ut.format_selected_stream_into_dict(formated_filename, valid_filename, selected_stream, selected_audio_stream, merge_option=True))
                total_size += selected_stream[-1] + selected_audio_stream[-1]

                console.print("[normal1]The next [normal2]video[/] & [normal2]audio[/] streams have been added to the download list:[/]")
                console.print(f"[normal1][normal2]{selected_stream[1]}[/], [normal2]{selected_stream[-4]}[/], [normal2]{selected_stream[-2].strip()}[/][/]")
                console.print(f"[normal1][normal2]{selected_audio_stream[1]}[/], [normal2]{selected_audio_stream[0].abr}[/], [normal2]{selected_audio_stream[-2].strip()}[/][/]\n")
        console.print(f"[normal1]{'='*42}[/]")
        console.print("")

    if not len(selected_streams_for_download):
        console.print("[warning1]No [warning2]streams[/] were selected for download[/]\n")
    else:
        console.print(f"[normal1][normal2]{len(selected_streams_for_download)}[/] stream{'s have' if len(selected_streams_for_download) > 1 else ' has'} been added to the download list. The streams are:[/]")
        console.print(f"[normal1]{'=' * (len( str( len(selected_streams_for_download) ) ) + 62)}[/]")
        for stream in selected_streams_for_download:
            if stream.get('video'):
                console.print(f"[normal1]Title: [normal2]{stream['video'][0][0].title}[/][/]")
                console.print(f"[normal1]Info : [normal2]{stream['video'][0][1]}[/], [normal2]{stream['video'][0][-4]}[/], [normal2]{stream['video'][0][-2].strip()}[/]", end="  +  " if stream.get('audio') else "\n")
            
            if stream.get('audio'):
                if not stream.get('video'):
                    console.print(f"[normal1]Title: [normal2]{stream['audio'][0][0].title}[/]\nInfo: [/]", end="")
                console.print(f"[normal1][normal2]{stream['audio'][0][1]}[/], [normal2]{stream['audio'][0][0].abr}[/], [normal2]{stream['audio'][0][-2].strip()}[/][/]")
            console.print("")

        total_duration = divmod(total_duration, 60)
        console.print(f"[normal1]Total size:     [normal2]{round(total_size, 2)}[/] MB[/]")
        console.print(f"[normal1]Total Duration: [normal2]{total_duration[0]}[/]:[normal2]{total_duration[1]}[/] min{'s' if int(total_duration[0])>1 else ''}[/]")
        console.print("[normal1]Confirm? ([normal2]1[/]:YES, [normal2]else[/]:no): [/]", end="")
        if not ut.yes_no_choice(blank_true=True):
            console.print("[warning1]][warning2]Download[/] aborted...[/]\n")
            return
        
        ut.download_streams(selected_streams_for_download)
    if from_playlist:
        console.print("[normal1]Do you want to download [normal2]another playlist[/]? ([normal2]1[/]:yes, [normal2]else[/]:NO): [/]", end="")
        continue_option = ut.yes_no_choice()
        return continue_option
    console.print("[normal1]Download finished successfully! Enter anything to end the script: [/]", end="")
    input()



if __name__ == "__main__":
    terminal_argument_link = ""

    if len(argv) > 1:
        if argv[1] in ["help", "-h", "--help"]:
            console.print("""[normal1]python "[normal1]The_Refactored.py" \[[normal2]script_mode[/]] \[[normal2]target_link[/]] \[[normal2]from_video[/]] \[[normal2]to_video[/]]

[normal2]script_mode[/]: [normal2]1[/] -> DOWNLOAD ONE VIDEO  |  [normal2]-1[/] -> use links from a file  |  [normal2]else[/]: download a playlist[/]

[normal2]target_link[/]: A link for a [normal2]single video[/] when downloading [normal2]one video[/].
             A link for a [normal2]playlist[/] when downloading a [normal2]playlist[/].

[normal2]from_video[/] : The [normal2]video number[/] from where to start downloading when downloading a [normal2]playlist[/].

[normal2]to_video[/]   : The [normal2]video number[/] of the last video you want when downloading a [normal2]playlist[/].[/]""")
            
            choice = -999 # Skip and end the script.

        elif argv[1] in ["1", "yes", "y"]:
            choice = 1
        elif argv[1] in ["-1", "skip"]:
            choice = -1
        else:
            choice = False
        
        if len(argv) > 2:
            terminal_argument_link = argv[2]
    else:
        console.print("[normal1]Choose a mode: ([normal2]1[/]:ONE VIDEO  |  [normal2]-1[/]:links from file  |  [normal2]else[/]:playlist): [/]", end="")
        choice = ut.yes_no_choice(blank_true=True)
    
    if choice != -999:
        while True:
            if choice == 1:
                continue_option = download_one_video(video_link = terminal_argument_link)
            elif choice == -1:
                continue_option = download_many_videos(from_playlist = False)
            else:
                if len(argv) > 4:
                    continue_option = download_many_videos(playlist_link = terminal_argument_link, from_video=int(argv[3]), to_video=int(argv[4]))
                else:
                    continue_option = download_many_videos(playlist_link = terminal_argument_link)
            if(not continue_option):
                console.print("[normal1][normal2]Exiting[/]...[/]")
                break
            
            # Clear the previously entered video link and terminal arguments if another iteration is happening:
            terminal_argument_link = ""
            argv = [argv[0]]
