from pytube import YouTube
import AVMerger
import os
import re

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def grouper_sort(vlist, group_by=1, sort_by=-1):
    groups = {}

    # Group by `mime_type`
    for vid_stream in vlist: 
        groups[vid_stream[group_by]] = groups.get(vid_stream[group_by], []) + [vid_stream]
    
    # Sort by filesize
    for k in groups.keys():
        groups[k] = sorted(groups[k], key = lambda x: x[sort_by])
    
    return groups

def on_complete(stream, file_path):
    print(f"File downloaded successfully in the next path: {file_path}\n")

def on_progress(stream, chunk, bytes_remaining):
    print(100 - round(bytes_remaining/stream.filesize * 100, 2), f"{round(bytes_remaining/1000/1000, 2)} : {round(stream.filesize/1000/1000, 2)} MB", sep="%, ")

def youtube_video_download():
    # Getting a link from the user
    print("Enter a Link to a YouTube Video:", end=" ")
    link_valid = False
    
    while(not link_valid):
        link = input()
        try: # check for invalid links
            vid_obj = YouTube(link, on_complete_callback=on_complete, on_progress_callback=on_progress)
            link_valid = True
        except:
            print(f"\n({link}) is not a valid link for a YouTube video.\n\nTry again:", end=" ")

    print("\nA list of all available streams is being fetched...\n")
    vid_streams_dict = [] # initially a list but becomes a dict after using grouper_sort()

    # Getting video data
    for stream in vid_obj.streams:
        try: # sometimes one or more streams for some reason are corrupted and you can't view their size or download them (but other data is accessable)
            file_size = round(stream.filesize/1000/1000, 2)
        except:
            file_size = 0.01 # if the stream is corrupted, save its file_size as 0.01 MB
        str_file_size = ""

        if file_size > 1000:
                str_file_size = f"{round(file_size/1000, 2):6} GB"
        else:   str_file_size = f"{file_size:6} MB"

        vid_streams_dict.append([stream, stream.mime_type, stream.type, stream.subtype, stream.resolution, "Progressive" if stream.is_progressive else False, str_file_size, file_size])

    # Formatting and printing out found streams
    vid_streams_dict = grouper_sort(vid_streams_dict)

    print(f"Video Title: {vid_obj.title}")
    vid_duration = round(vid_obj.length/60, 2)
    print(f"Duration: {int(vid_duration)}:{int(vid_duration % 1 * 60)} min\n")

    print("Available streams are:")
    print("="*22)

    for i, k in enumerate(vid_streams_dict, 1):
        print(f"({i}) [{k}]:")
        for j, vid in enumerate(vid_streams_dict[k], 1):
            if vid[-4]:
                if vid[-3]:
                    print(f"   {j:2}) {vid[-4]:5}  >>  {vid[-2]:9}  >>  {vid[-3]}") # resolution, str_file_size & is_progressive
                else:
                    print(f"   {j:2}) {vid[-4]:5}  >>  {vid[-2]:9}") # resolution, str_file_size
            else:   # no resolution data, i.e. an audio stream
                print(f"   {j:2}) Audio  >>  {vid[-2]}")
        print("\n")
    
    # Option_1: Download video & audio streams then merge them with ffmpeg
    merge_option = False
    if "audio/mp4" in vid_streams_dict or "audio/webm" in vid_streams_dict:
        merge_option = True if input(f"Do you want to download a video & an audio streams then merge them with ffmpeg? (1:yes, else:No): ").lower() in ["1", "yes", "y"] else False
    
    vid_options = []
    if merge_option:
        vid_options = input('Choose a category and a resolution option for both the video & audio streams (4 numbers) separated by spaces or leave empty to stop: ').split(" ")
    else:
        vid_options = input('Choose a category and a resolution option separated by a space or leave empty to stop: ').split(" ")
    print("")

    #TODO1: Add the ability to download subtitles if available and rename it with the same filename
    
    #TODO2: Next line causes `IndexError: list index out of range` if not entered correctly. (The commented lines are possible solution)
    # if vid_options[0] >= len(streams_categories) or vid_options[2] >= len(vid_streams_dict[streams_categories[int(vid_options[0])]]):
        # try again!
    if(vid_options[0]): # if not empty
        streams_categories = list(vid_streams_dict.keys())
        selected_stream = vid_streams_dict[streams_categories[int(vid_options[0])-1]][int(vid_options[1])-1]
        print(f"Downloading {selected_stream[1]}, {selected_stream[-4]}, {selected_stream[-2]}...")

        # remove stupid colons and unsupported characters for a filename
        valid_filename    = re.sub("[^A-Za-z0-9_.\-\\ !\(\)\[\]\u0600-\u065F\u066A-\u06EF\u06FA-\u06FF]", "", vid_obj.title)
        formated_filename = re.sub("[^A-Za-z0-9_.\-\\ !\(\)\[\]\u0600-\u065F\u066A-\u06EF\u06FA-\u06FF]", " -", vid_obj.title)

        if not merge_option:
            selected_stream[0].download()
            os.rename(valid_filename + ".mp4", formated_filename + ".mp4")

        else:
            if not os.path.isfile(valid_filename + ' (Video).mp4'):
                selected_stream[0].download()
                os.rename(valid_filename + ".mp4", formated_filename + " (Video).mp4")
            else:
                print("Video stream already downloaded\n")
            
            print(f"Downloading {selected_stream[1]}, {selected_stream[-4]}, {selected_stream[-2]}...")
            if not os.path.isfile(valid_filename + " (Audio).mp4"):
                selected_stream = vid_streams_dict[streams_categories[int(vid_options[2])-1]][int(vid_options[3])-1]
                # selected_stream[0].download(filename=vid_obj.title+' (Audio).mp4') >> Causes a weird bug where the file is downloaded but empty (and some times not downloaded at all).
                selected_stream[0].download()
                os.rename(valid_filename + ".mp4", formated_filename + " (Audio).mp4")
            else:
                print("Audio stream already downloaded\n")

            print("Starting merging...\n")
            try:
                AVMerger.avmerger(  directory = os.path.dirname(os.path.abspath(__file__)), 
                                    filename  = valid_filename)
            except:
                print("Something went wrong! Check if both the video and audio streams have been downloaded.")
            else:
                print(f"File merged successfully\n")

    continue_option = True if input("Do you want to download another video? (1:Yes, else:No): ").lower() in ["1", "yes", "y"] else False
    print("")

    return continue_option

while(True):
    continue_option = youtube_video_download()
    if(not continue_option):
        print("Exiting...")
        break
