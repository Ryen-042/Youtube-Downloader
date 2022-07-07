import Links_and_Objects as lo, Video_Metadata as vmd, Utility as ut
from rich.console import Console
from rich.theme import Theme
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))



custom_theme = Theme({
    "normal1"       :   "bold blue1 on grey23",
    "normal2"       :   "bold dark_violet",

    "warning1"      :   "bold plum4 on grey23",
    "warning2"      :   "bold red",
    
    "exists"        :   "bold chartreuse3 on gray23"
})

console = Console(theme=custom_theme)



def download_one_video():
    # Generate a video object from the user input link
    vid_obj = lo.get_vid_obj()


    # Getting the metadata of the video
    vid_streams_dict = vmd.get_vid_metadata(vid_obj)

    console.print(f"[normal1]Video Title: [normal2]{vid_obj.title}[/][/]")
    vid_duration = round(vid_obj.length/60, 2)
    console.print(f"[normal1]Duration   : [normal2]{int(vid_duration)}:{int(vid_duration % 1 * 60)} mins[/][/]\n")

    # remove stupid colons and unsupported characters for a filename
    valid_filename    = ut.format_name(vid_obj.title, "[#<>:\"\'/\\|.?*,%]")
    formated_filename = ut.format_name(vid_obj.title, "[<>:\"/\\|?*]", " -")
    
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



def download_many_videos(from_playlist=True):
    # Generate video objects from the (playlist input link/filepath containing video links)
    if from_playlist:
        vid_objs = lo.get_vid_objs_from_playlist()
    else:
        vid_objs = lo.get_vid_objs_from_file()

    console.print(f"[normal1]Below are the [normal2]{'playlist videos' if from_playlist else 'videos'}[/] {'you selected for download' if from_playlist else 'from the provided links'}:[/]")
    console.print(f"[normal1]{'='*56 if from_playlist else '='*45}[/]")
    # Getting the metadata of the video objects
    selected_streams_for_download = []
    for obj_num, vid_obj in enumerate(vid_objs):
        vid_streams_dict = vmd.get_vid_metadata(vid_obj)

        console.print(f"[normal1]Video number: [normal2]{obj_num+1}[/][/]", end="")
        vid_duration = round(vid_obj.length/60, 2)
        console.print(f"[normal1]  |  Duration: [normal2]{int(vid_duration)}[/]:[normal2]{int(vid_duration % 1 * 60)} min[/][/]")
        console.print(f"[normal1]Video title:  [normal2]{vid_obj.title}[/][/]\n")

        # remove stupid colons and unsupported characters for a filename
        valid_filename    = ut.format_name(vid_obj.title, "[#<>:\"\'/\\|.?*,%]")
        formated_filename = ut.format_name(vid_obj.title, "[<>:\"/\\|?*]", " -")

        # Check if the video is already downloaded before doing anything
        if os.path.isfile(formated_filename + " (Merged).mp4"):
            console.print("[exists]This [normal2]video[/] is already downloaded[/]\n")
            console.print(f"[normal1]{'='*42}[/]")
            console.print("")
            continue

        # printing the available streams
        console.print("[normal1]Available streams are:[/]")
        console.print(f"[normal1]{'='*22}[/]")
        # [number_of_categories, [number of streams in each category]]
        categories_lengths = vmd.print_streams(vid_streams_dict)


        # Option_1: Download video & audio streams then merge them with ffmpeg
        merge_option = False
        if "video/mp4" in vid_streams_dict and "audio/mp4" in vid_streams_dict:
            console.print("[normal1]Download [normal2]video[/] & [normal2]audio[/] streams and merge them with ffmpeg?[/]")
            console.print("[normal1]Avaliable options: ([normal2]1[/]:YES  |  [normal2]-1[/]:break  |  [normal2]else[/]:no): [/]", end="")
            merge_option = ut.yes_no_choice(blank_true=True)
        
        selected_streams = []
        if merge_option == -1:
                break
        else:
            selected_streams = ut.select_streams(merge_option,  categories_lengths)
        
        if(selected_streams[0]): # if not empty            
            streams_categories = list(vid_streams_dict.keys())
            
            # Get the selected category and resolution option
            selected_stream = vid_streams_dict[streams_categories[int(selected_streams[0])-1]][int(selected_streams[1])-1]

            if not merge_option:
                if selected_stream[2] == 'video':
                    selected_streams_for_download.append(ut.format_selected_stream_into_dict(formated_filename, valid_filename, selected_stream))
                else:
                    selected_streams_for_download.append(ut.format_selected_stream_into_dict(formated_filename, valid_filename, selected_audio_stream=selected_stream))
                console.print(f"[normal1]The next [normal2]{selected_stream[2]}[/] stream has been added to the download list: [normal2]{selected_stream[1]}[/], [normal2]{selected_stream[-4] if selected_stream[2] == 'video' else selected_stream[0].abr}[/], [normal2]{selected_stream[-2].strip()}[/]...[/]\n")

            else:
                # Audio stream
                selected_audio_stream = vid_streams_dict[streams_categories[int(selected_streams[2])-1]][int(selected_streams[3])-1]
                selected_streams_for_download.append(ut.format_selected_stream_into_dict(formated_filename, valid_filename, selected_stream, selected_audio_stream, merge_option=True))
                console.print("[normal1]The next [normal2]video[/] & [normal2]audio[/] streams have been added to the download list:[/]")
                console.print(f"[normal1][normal2]{selected_stream[1]}[/], [normal2]{selected_stream[-4]}[/], [normal2]{selected_stream[-2].strip()}[/][/]")
                console.print(f"[normal1][normal2]{selected_audio_stream[1]}[/], [normal2]{selected_audio_stream[0].abr}[/], [normal2]{selected_audio_stream[-2].strip()}[/][/]\n")
            console.print(f"[normal1]{'='*42}[/]")
            ##### console.rule(style=)
            console.print("")

    console.print(f"[normal1][normal2]{len(selected_streams_for_download)}[/] stream{'s have' if len(selected_streams_for_download) > 1 else ' has'} been added to the download list. The streams are:[/]")
    console.print(f"[normal1]{'=' * (len( str( len(selected_streams_for_download) ) ) + 63)}[/]")
    for stream in selected_streams_for_download:
        if stream.get('video'):
            console.print(f"[normal1]Title: [normal2]{stream['video'][0][0].title}[/][/]")
            console.print(f"[normal1]Info : [normal2]{stream['video'][0][1]}[/], [normal2]{stream['video'][0][-4]}[/], [normal2]{stream['video'][0][-2].strip()}[/]", end="  +  " if stream.get('audio') else "\n")
        
        if stream.get('audio'):
            if not stream.get('video'):
                console.print(f"[normal1]Title: [normal2]{stream['audio'][0][0].title}[/]\nInfo: [/]", end="")
            console.print(f"[normal1][normal2]{stream['audio'][0][1]}[/], [normal2]{stream['audio'][0][0].abr}[/], [normal2]{stream['audio'][0][-2].strip()}[/][/]")
        console.print("")

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
    while(True):
        continue_option = download_one_video()
        # continue_option = download_many_videos()
        # continue_option = download_many_videos(False)
        if(not continue_option):
            console.print("[normal1]Exiting...[/]")
            os.startfile(os.path.dirname(os.path.abspath(__file__)))
            break
