from AVMerger import *
import re

# Available functions in this module:
# ['format_name',    'yes_no_choice',                    'check_stream_existence',
#  'merge_streams',  'optional_downloads',               'download_subtitles',
#  'select_streams', 'format_selected_stream_into_dict', 'download_streams']


# valid_filename:    [<>\"/\\?*:|#\'.,%]
# formated_filename: [<>\"/\\?*:|]
def format_name(filename, extra_pattern=""):
    new_name    = re.sub('[<>\"/\\?*]', "", filename)
    new_name    = new_name.replace("\\", "")
    
    if not extra_pattern: # extra_pattern is set only for valid_filename
        new_name    = re.sub('[:]', ".", new_name)
        new_name    = re.sub('[|]', "-", new_name)
        new_name    = re.sub(' +', ' ', new_name) # remove multiple spaces
    else:
        # Some of these characters are valid filename characters but pytube omit them from when downloading files.
        new_name    = re.sub('[:|#\'.,%]', "", new_name)
    
    return new_name



def yes_no_choice(blank_true=False):
    choice = input().lower()
    console.print("")
    
    # blank_true >> return True if the user didn't enter anything
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
        console.print(f"[exists][normal2]{'Video' if stream_type == 'video' else 'Audio'}[/] stream already downloaded[/]\n")



def merge_streams(formated_filename, vid_id):
    console.print("[normal1]Starting merging...[/]")
    subtitles = download_subtitles(vid_id, formated_filename)
    try:
        # os.path.dirname(os.path.abspath(__file__))+"\\Downloads"
        merge_status = avmerger(os.getcwd(), formated_filename, subtitles)
        if not merge_status:
            raise ValueError
    except ValueError:
        console.print("[warning1]Value Error! [warning2]False[/] was returned from the merging function. Check if both streams have been downloaded correctly.[/]\n")
    except:
        console.print("[warning1]Something went wrong! Check if both the [warning2]video[/] and [warning2]audio[/] streams have been downloaded correctly.[/]\n")
    else:
        console.print(f"[normal1]File merged successfully.[/]\n")



def optional_downloads(formated_filename, option_name, vid_obj):
    if not os.path.isfile(formated_filename + f" ({option_name}).txt"):
        try:
            with open(formated_filename + f" ({option_name}).txt", "w", encoding="utf-8") as option_file:
                if option_file == "Description":
                    option_file.write(vid_obj.description)
        except:
            console.print(f"[warning1]Sorry, couldn't download the [warning2]video {option_name}[/]![/]\n")
        else:
            console.print("")
    else:
        console.print(f"[exists][normal2]Video {option_name.lower()}[/] already downloaded[/]\n")



def download_subtitles(vid_id, formated_filename):
    if not os.path.isfile(formated_filename + ".en.vtt") and not os.path.isfile(formated_filename + ".ar.vtt"):
        console.print("[normal1]Downloading [normal2]subtitles[/]...[/]")
        
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

        # os.system(f"youtube-dl --write-sub --write-auto-sub --sub-lang ar,en --skip-download \"https://www.youtube.com/watch?v={vid_id}\" -o \"{formated_filename}\"")

        os.system(f"yt-dlp --write-sub --write-auto-sub --sub-lang ar,en --skip-download \"https://www.youtube.com/watch?v={vid_id}\" -o \"{formated_filename}\"")
    else:
        console.print("[exists][normal2]Subtitles[/] already downloaded.[/]\n")
    
    subtitles = ""
    if os.path.isfile(formated_filename + ".en.vtt"):
        subtitles += "1"
    if os.path.isfile(formated_filename + ".ar.vtt"):
        subtitles += "2"
    return subtitles


def select_streams(merge_option, categories_lengths, skip_not_stop = True, res_only = False):
    valid_choices = False
    if merge_option and not res_only:
        message = f"[normal1]Select a [normal2]category[/] and a [normal2]resolution[/] option for both the video & audio streams ([normal2]4[/] numbers) separated by [normal2]spaces[/] or [normal2]leave empty[/] to {'skip' if skip_not_stop else 'stop'}: [/]"
    elif res_only:
        message = f"[normal1]Select a [normal2]resolution[/] option for both the video & audio streams ([normal2]2[/] numbers) separated by a [normal2]space[/] or [normal2]leave empty[/] to {'skip' if skip_not_stop else 'stop'}: [/]"
    else:
        message = f"[normal1]Select a [normal2]category[/] and a [normal2]resolution[/] option separated by a [normal2]space[/] or [normal2]leave empty[/] to {'skip' if skip_not_stop else 'stop'}: [/]"

    while not valid_choices:
        console.print(message, end='')
        choices = input().split(" ")
        console.print("")

        # If choices is empty return ['']
        if len(choices) == 1 and not choices[0]:
                return choices

        if not res_only and len(choices) > (4 if merge_option else 2) or res_only and len(choices) > 2:
            console.print(f"[warning1]Invalid input. Requested [warning2]{2 if res_only else 4 if merge_option else 2}[/] numbers, but got [warning2]{len(choices)}[/] inputs. Your input: [warning2]{choices}[/][/]\n")
            continue
        elif not res_only and len(choices) != (4 if merge_option else 2) or res_only and len(choices) != 2:
            console.print(f"[warning1][warning2]Not enough data[/]. Requested [warning2]{2 if res_only else 4 if merge_option else 2}[/] numbers, but got [warning2]{len(choices)}[/] input{'s' if len(choices) > 1 else ''}. Your input: [warning2]{choices}[/][/]\n")
            continue
        
        if res_only:
            choices = [1, choices[0], 2, choices[1]]

        try:
            if int(choices[0]) <= categories_lengths[0]:
                if merge_option and int(choices[2]) <= categories_lengths[0] or not merge_option:
                    for i in range(1, len(choices), 2):
                        if int(choices[i]) > categories_lengths[int(choices[i-1])]:
                            console.print(int(choices[i]), categories_lengths[int(choices[i-1])])
                            console.print(f"[warning1][warning2]Error Encountered[/]. Make sure the [warning2]selected stream number{'s[/] are' if merge_option else '[/] is'} correct. Your input: [warning2]{choices}[/][/]\n")
                            break
                    else:
                        valid_choices = True
                elif merge_option and int(choices[2]) > categories_lengths[0]:
                    console.print(f"[warning1][warning2]Error Encountered[/]. Make sure the [warning2]second selected category number[/] is correct. Your input: [warning2]{choices}[/][/]\n")
            else:
                console.print(f"[warning1][warning2]Error Encountered[/]. Make sure the [warning2]{'first' if merge_option else ''} selected category number[/] is correct. Your input: [warning2]{choices}[/][/]\n")
        except:
            console.print(f"[warning1]Invalid input. You have entered something wrong. Your input: [warning2]{choices}[/][/]\n")
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
            console.print(f"[normal1]Downloading [normal2]{stream['video'][0][0].title}[/][/]")
            console.print(f"[normal1][normal2]{stream['video'][0][1]}[/], [normal2]{stream['video'][0][-4]}[/], [normal2]{stream['video'][0][-2].strip()}[/]...[/]")
            check_stream_existence(stream['video'][0][0], stream['video'][1], stream['video'][2], stream['video'][3])
        
        if 'audio' in stream:
            console.print(f"[normal1]Downloading [normal2]{stream['audio'][0][1]}[/], [normal2]{stream['audio'][0][0].abr}[/], [normal2]{stream['audio'][0][-2].strip()}[/]...[/]")
            check_stream_existence(stream['audio'][0][0], stream['audio'][1], stream['audio'][2], stream['audio'][3])
        
        if 'video' in stream and 'audio' in stream:
            merge_streams(stream['video'][1], stream['video'][0][-5])
        console.print(f"[normal1]{'='*20}[/]")
        console.print("")
