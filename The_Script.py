from pytube import YouTube, Caption
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
    print(round(100 - bytes_remaining/stream.filesize * 100, 2), f"{round((stream.filesize - bytes_remaining)/1000/1000, 2)} : {round(stream.filesize/1000/1000, 2)} MB", sep="%, ")

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
            file_size = 0.01 # if the stream is corrupted, store its file_size as 0.01 MB
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
            if vid[-4]:     # resolution
                if vid[-3]: # is_progressive
                    print(f"   {j:2}) {vid[-4]:5}  >>  {vid[-2]:9}  >>  {vid[-3]}") # resolution, str_file_size & is_progressive
                else:
                    print(f"   {j:2}) {vid[-4]:5}  >>  {vid[-2]:9}") # resolution, str_file_size
            else:   # no resolution data, i.e. an audio stream
                print(f"   {j:2}) Audio  >>  {vid[-2]:9}  >>  {vid[0].abr}")
        print("\n")
    
    # remove stupid colons and unsupported characters for a filename
        valid_filename    = re.sub("[<>:\"/\\|.?*,%]", "", vid_obj.title)
        formated_filename = re.sub("[<>:\"/\\|?*]", " -", vid_obj.title)

    # Option_1: Download video description
    vid_description_option = True if input(f"Download Video Description? (1:yes, else:No): ").lower() in ["1", "yes", "y"] else False
    if vid_description_option:
        try:
            with open(formated_filename + " (Description).txt", "w", encoding="utf-8") as vid_discription:
                vid_discription.write(vid_obj.description)
        except:
            print("Sorry, could't download the video description!\n")
        else:
            print("")
    
    # Option_2: Download video & audio streams then merge them with ffmpeg
    merge_option = False
    if "video/mp4" in vid_streams_dict and "audio/mp4" in vid_streams_dict:
        merge_option = True if input(f"Do you want to download a video & an audio streams then merge them with ffmpeg? (1:yes, else:No): ").lower() in ["1", "yes", "y"] else False
        print("")
    
    download_options = []
    if merge_option:
        download_options = input('Choose a category and a resolution option for both the video & audio streams (4 numbers) separated by spaces or leave empty to stop (mp4 streams only): ').split(" ")
    else:
        download_options = input('Choose a category and a resolution option separated by a space or leave empty to stop: ').split(" ")
    print("")

    # Option_3: Download subtitles
    # There is a very annoying bug in the Caption class, to solve this bug see:
    # https://stackoverflow.com/questions/68780808/xml-to-srt-conversion-not-working-after-installing-pytube
    vid_caption_option = True if input(f"Download Video Caption? (1:yes, else:No): ").lower() in ["1", "yes", "y"] else False
    if vid_caption_option:
        caption_filename = formated_filename + " (Merged).srt" if merge_option else formated_filename + ".srt"
        try:
            if vid_obj.captions.get("en"):
                vid_obj.captions["en"].download(title=caption_filename)
            elif vid_obj.captions.get("a.en"):
                vid_obj.captions["a.en"].download(title=caption_filename)
            else:
                raise AssertionError
        except AssertionError:
            print("Sorry, couldn't find any subtitle.")
        except KeyError:
            print("Unexpected error occurred while downloading video subtitles")
        else:
            print("")
        
        # Another way to download subtitles
        # xml_captions = vid_obj.captions["en"]
        # print(xml_captions.xml_caption_to_srt(xml_captions.xml_captions))
        
    if(download_options[0]): # if not empty
        streams_categories = list(vid_streams_dict.keys())
        selected_stream = vid_streams_dict[streams_categories[int(download_options[0])-1]][int(download_options[1])-1]

        print(f"Downloading {selected_stream[1]}, {selected_stream[-4]}, {selected_stream[-2]}...")
        if not merge_option:
            selected_stream[0].download()
            os.rename(valid_filename + ".mp4", formated_filename + ".mp4")

        else:
            if not os.path.isfile(formated_filename + ' (Video).mp4'):
                selected_stream[0].download()
                os.rename(valid_filename + ".mp4", formated_filename + " (Video).mp4")
            else:
                print("Video stream already downloaded\n")
            
            selected_stream = vid_streams_dict[streams_categories[int(download_options[2])-1]][int(download_options[3])-1]
            print(f"Downloading {selected_stream[1]}, {vid[0].abr}, {selected_stream[-2]}...")
            if not os.path.isfile(formated_filename + " (Audio).mp4"):
                # selected_stream[0].download(filename=vid_obj.title+' (Audio).mp4') >> Causes a weird bug where the file is downloaded but empty (and some times not downloaded at all).
                selected_stream[0].download()
                os.rename(valid_filename + ".mp4", formated_filename + " (Audio).mp4")
            else:
                print("Audio stream already downloaded\n")

            print("Starting merging...")
            if not os.path.isfile(formated_filename + " (Merged).mp4"):
                print("")
                try:
                    AVMerger.avmerger(  directory = os.path.dirname(os.path.abspath(__file__)), 
                                        filename  = formated_filename)
                except:
                    print("Something went wrong! Check if both the video and audio streams have been downloaded correctly.")
                else:
                    print(f"\nFile merged successfully.\n")
            else:
                print("Video is already merged\n")

    continue_option = True if input("Do you want to download another video? (1:Yes, else:No): ").lower() in ["1", "yes", "y"] else False
    print("")

    return continue_option

while(True):
    continue_option = youtube_video_download()
    if(not continue_option):
        print("Exiting...")
        break
