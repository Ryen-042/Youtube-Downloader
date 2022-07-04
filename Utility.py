import AVMerger as avm
import os, re
import youtube_dl
# Available functions in this module:
# ['format_name',    'yes_no_choice',                    'check_stream_existence',
#  'merge_streams',  'optional_downloads',               'download_subtitles',
#  'select_streams', 'format_selected_stream_into_dict', 'download_streams']

def format_name(filename, pattern, replacement=""):
    new_named    = re.sub(pattern, replacement, filename)
    new_named    = new_named.replace("\\", "")
    return new_named



def yes_no_choice(message, blank_true=False):
    choice = input(message).lower()
    print("")

    if choice in ["1", "yes", "y"] or not choice and blank_true:
        return True
    if choice in ["-1", "skip"]:
        return -1
    return False



def check_stream_existence(stream_obj, formated_filename, valid_filename, stream_type):
    check1 = os.path.isfile(valid_filename + '.mp4')
    check2 = os.path.isfile(formated_filename + (" (Video).mp4" if stream_type == "video" else " (Audio).mp4"))
    if not check1 and not check2:
        stream_obj.download()
        os.rename(valid_filename + ".mp4", formated_filename + (" (Video).mp4" if stream_type == "video" else " (Audio).mp4"))
    elif check1:
        os.rename(valid_filename + ".mp4", formated_filename + (" (Video).mp4" if stream_type == "video" else " (Audio).mp4"))
    else:
        print(f"{'Video' if stream_type == 'video' else 'Audio'} stream already downloaded\n")



def merge_streams(formated_filename, vid_id):
    print("Starting merging...")
    subtitles = download_subtitles(vid_id, formated_filename)
    try:
        avm.avmerger(   os.path.dirname(os.path.abspath(__file__)),
                        formated_filename, subtitles)
    except:
        print("Something went wrong! Check if both the video and audio streams have been downloaded correctly.\n")
    else:
        print(f"File merged successfully.\n")



def optional_downloads(formated_filename, option_name, vid_obj):
    if not os.path.isfile(formated_filename + f" ({option_name}).txt"):
        try:
            with open(formated_filename + f" ({option_name}).txt", "w", encoding="utf-8") as option_file:
                if option_file == "Description":
                    option_file.write(vid_obj.description)
        except:
            print(f"Sorry, could't download the video {option_name}!\n")
        else:
            print("")
    else:
        print(f"Video {option_name.lower()} already downloaded\n")



def download_subtitles(vid_id, formated_filename):
    if not os.path.isfile(formated_filename + ".en.vtt") and not os.path.isfile(formated_filename + ".ar.vtt"):
        print("Downloading subtitles...")
        
        ## useful links: https://github.com/ytdl-org/youtube-dl#subtitle-options
        #                https://hassanlatif.net/how-to-download-youtube-videos-with-subtitles-using-youtube-dl-646.html
        ##Subtitle Options:
        #   --write-sub          Write subtitle file
        #   --write-auto-sub     Write automatic subtitle file (YouTube only)
        #   --all-subs           Download all the subtitles provided by the owner of the video
        #   --list-subs          List all available subtitles for the video
        #   --sub-format FORMAT  Subtitle format, accepts formats preference, for example: "srt" or "ass/srt/best"
        #   --sub-lang LANGS     Languages of the subtitles to download (optional) separated by commas, use IETF language tags like 'en,pt'
        ## Download specific subtitles:
        #   youtube-dl --write-sub --sub-lang ar,en --skip-download "download_link" -o "filename"
        ## Download specific subtitles provided by the owner of the video + the auto generated subtitles:
        #   youtube-dl --write-sub --write-auto-sub --sub-lang ar,en --skip-download "https://www.youtube.com/watch?v=MZS1F0Hp28A" -o "ff"

        os.system(f"youtube-dl --write-sub --write-auto-sub --sub-lang ar,en --skip-download \"https://www.youtube.com/watch?v={vid_id}\" -o \"{formated_filename}\"")
    else:
        print("Subtitles already downloaded.\n")
    
    subtitles = ""
    if os.path.isfile(formated_filename + ".en.vtt"):
        subtitles += "1"
    if os.path.isfile(formated_filename + ".ar.vtt"):
        subtitles += "2"
    return subtitles


def select_streams(merge_option, categories_lengths, message):
    valid_choices = False
    while not valid_choices:
        choices = input(message).split(" ")
        print("")

        # If choices is empty return ['']
        if len(choices) == 1 and not choices[0]:
                return choices

        if len(choices) > (4 if merge_option else 2):
            print(f"Error. Invalid input. Requested {4 if merge_option else 2} numbers, but got {len(choices)}. Your input: {choices}.\n")
            continue
        elif len(choices) != (4 if merge_option else 2):
            print(f"Error. Invalid input. Not enough data. Requested {4 if merge_option else 2} numbers, but got {len(choices)}. Your input: {choices}.\n")
            continue
        
        try:
            if int(choices[0]) <= categories_lengths[0]:
                if merge_option and int(choices[2]) <= categories_lengths[0] or not merge_option:
                    for i in range(1, len(choices), 2):
                        if int(choices[i]) > categories_lengths[int(choices[i-1])]:
                            print(int(choices[i]), categories_lengths[int(choices[i-1])])
                            print(f"Error Encountered. Make sure the selected stream number{'s are' if merge_option else ' is'} correct. Your input: {choices}.\n")
                            break
                    else:
                        valid_choices = True
                elif merge_option and int(choices[2]) > categories_lengths[0]:
                    print(f"Error Encountered. Make sure the second selected category number is correct. Your input: {choices}.\n")
            else:
                print(f"Error Encountered. Make sure the{' first' if merge_option else ''} selected category number is correct. Your input: {choices}.\n")
        except:
            print(f"Invalid input. You have entered something wrong. Your input: {choices}.\n")
    return choices



def format_selected_stream_into_dict(formated_filename, valid_filename, selected_video_stream=None, selected_audio_stream=None, merge_option=False):
    if merge_option:
        selected_streams = {
            "video": [selected_video_stream, formated_filename, valid_filename, "video"],
            "audio": [selected_audio_stream, formated_filename, valid_filename, 'audio']
        }
    
    else:
        if not selected_video_stream:
            selected_streams = {
                "audio": [selected_audio_stream, formated_filename, valid_filename, 'audio']
            }
        
        else:
            selected_streams = {
                "video": [selected_video_stream, formated_filename, valid_filename, "video"],
            }
    
    return selected_streams



def download_streams(selected_streams):
    for stream in selected_streams:
        if 'video' in stream:
            print(f"Downloading {stream['video'][0][0].title}")
            print(f"{stream['video'][0][1]}, {stream['video'][0][-4]}, {stream['video'][0][-2].strip()}...")
            check_stream_existence(stream['video'][0][0], stream['video'][1], stream['video'][2], stream['video'][3])
        
        if 'audio' in stream:
            print(f"Downloading {stream['audio'][0][1]}, {stream['audio'][0][0].abr}, {stream['audio'][0][-2].strip()}...")
            check_stream_existence(stream['audio'][0][0], stream['audio'][1], stream['audio'][2], stream['audio'][3])
        
        if 'video' in stream and 'audio' in stream:
            merge_streams(stream['video'][1], stream['video'][0][-5])
        print("="*20)
        print("")
