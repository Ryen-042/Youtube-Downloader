from pytube import YouTube
import AVMerger
import os
import re

# Pseudocode:

# select_mode() 						# video or playlist
# open_video_link() 					# or open_playlist_link()
# get_all_the_data_of_the_video()		# or videos
# select_type_and_resolution()
# any_extra()							# like subtitles or download the description

# https://www.youtube.com/watch?v=RmJryKpLKrM

# https://www.youtube.com/watch?v=Iwfe5XPSRRA

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


def comments():
    ## grouper_sort(vid_streams_dict)
    # {'video/3gpp': [
    # [<Stream: itag="17" mime_type="video/3gpp" res="144p" fps="7fps" vcodec="mp4v.20.3" acodec="mp4a.40.2" progressive="True" type="video">, 'video/3gpp', 'video', '3gpp', '144p', '13.72 MB', 13.72],

    # 'video/mp4': [
    # [<Stream: itag="160" mime_type="video/mp4" res="144p" fps="30fps" vcodec="avc1.4d400c" progressive="False" type="video">, 'video/mp4', 'video', 'mp4', '144p', '17.21 MB', 17.21],
    # [<Stream: itag="133" mime_type="video/mp4" res="240p" fps="30fps" vcodec="avc1.4d400d" progressive="False" type="video">, 'video/mp4', 'video', 'mp4', '240p', '38.86 MB', 38.86],
    # [<Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d401e" progressive="False" type="video">, 'video/mp4', 'video', 'mp4', '360p', '80.87 MB', 80.87],
    # [<Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2" progressive="True" type="video">, 'video/mp4', 'video', 'mp4', '360p', '98.29 MB', 98.29],
    # [<Stream: itag="135" mime_type="video/mp4" res="480p" fps="30fps" vcodec="avc1.4d401f" progressive="False" type="video">, 'video/mp4', 'video', 'mp4', '480p', '152.52 MB', 152.52],
    # [<Stream: itag="136" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001f" progressive="False" type="video">, 'video/mp4', 'video', 'mp4', '720p', '292.66 MB', 292.66],
    # [<Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2" progressive="True" type="video">, 'video/mp4', 'video', 'mp4', '720p', '315.74 MB', 315.74],
    # [<Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028" progressive="False" type="video">, 'video/mp4', 'video', 'mp4', '1080p', '548.37 MB', 548.37],

    # 'video/webm': [
    # [<Stream: itag="278" mime_type="video/webm" res="144p" fps="30fps" vcodec="vp9" progressive="False" type="video">, 'video/webm', 'video', 'webm', '144p', '15.61 MB', 15.61],
    # [<Stream: itag="242" mime_type="video/webm" res="240p" fps="30fps" vcodec="vp9" progressive="False" type="video">, 'video/webm', 'video', 'webm', '240p', '31.63 MB', 31.63],
    # [<Stream: itag="243" mime_type="video/webm" res="360p" fps="30fps" vcodec="vp9" progressive="False" type="video">, 'video/webm', 'video', 'webm', '360p', '54.14 MB', 54.14],
    # [<Stream: itag="244" mime_type="video/webm" res="480p" fps="30fps" vcodec="vp9" progressive="False" type="video">, 'video/webm', 'video', 'webm', '480p', '94.05 MB', 94.05],
    # [<Stream: itag="247" mime_type="video/webm" res="720p" fps="30fps" vcodec="vp9" progressive="False" type="video">, 'video/webm', 'video', 'webm', '720p', '163.71 MB', 163.71],
    # [<Stream: itag="248" mime_type="video/webm" res="1080p" fps="30fps" vcodec="vp9" progressive="False" type="video">, 'video/webm', 'video', 'webm', '1080p', '288.09 MB', 288.09],
    # [<Stream: itag="271" mime_type="video/webm" res="1440p" fps="30fps" vcodec="vp9" progressive="False" type="video">, 'video/webm', 'video', 'webm', '1440p', '767.75 MB', 767.75],
    # [<Stream: itag="313" mime_type="video/webm" res="2160p" fps="30fps" vcodec="vp9" progressive="False" type="video">, 'video/webm', 'video', 'webm', '2160p', '1.61 GB', 1652.27],

    # 'audio/mp4': [
    # [<Stream: itag="139" mime_type="audio/mp4" abr="48kbps" acodec="mp4a.40.5" progressive="False" type="audio">, 'audio/mp4', 'audio', 'mp4', None, '8.78 MB', 8.78],
    # [<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2" progressive="False" type="audio">, 'audio/mp4', 'audio', 'mp4', None, '23.29 MB', 23.29],

    # 'audio/webm': [
    # [<Stream: itag="249" mime_type="audio/webm" abr="50kbps" acodec="opus" progressive="False" type="audio">, 'audio/webm', 'audio', 'webm', None, '8.83 MB', 8.83],
    # [<Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus" progressive="False" type="audio">, 'audio/webm', 'audio', 'webm', None, '11.0 MB', 11.0],
    # [<Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus" progressive="False" type="audio">, 'audio/webm', 'audio', 'webm', None, '21.65 MB', 21.65]]}
    pass
