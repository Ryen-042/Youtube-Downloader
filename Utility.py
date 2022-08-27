from global_imports import *
from AVMerger import avmerger
from traceback import format_exc
from re import sub

from typing import Union, Literal
# For type hinting only
from pytube import YouTube
from pytube.streams import Stream

# Available functions in this module:
# ['format_name',    'yes_no_choice',     'check_stream_existence',
#  'merge_streams',  'optional_download', 'download_subtitles',
#  'select_streams', 'format_selected_stream_into_dict', 'download_streams']


# valid_filename:    [<>\"/\\?*:|#\'.,%]
# formated_filename: [<>\"/\\?*:|]
def format_name(name: str, pytube_format=False) -> str:
    """
    ### Description:
        Takes an unformatted name and format it to be used as filename.

    ### Parameters:
        - `name`          -> `str`:
            An unformatted name.
        - `pytube_format` -> `bool`:
            There are valid filename characters that pytube omits when it downloads anything.
            To format names like what pytube does, these characters will be removed.

    ### Returns:
        A formated name valid to be used as a filename.
    """
    new_name    = sub('[<>\"/\\?*]', "", name)
    new_name    = new_name.replace("\\", "")
    
    if not pytube_format: # pytube_format is only set for `valid_filename`.
        new_name    = sub('[:]', ".", new_name)
        new_name    = sub('[|]', "-", new_name)
        new_name    = sub(' +', ' ', new_name) # remove multiple spaces
    else:
        # Some of these characters are valid filename characters but pytube omit when it downloads anything.
        new_name    = sub('[:|#\'.,%]', "", new_name)
    
    return new_name



def yes_no_choice(blank_true=False, third_option=False) -> int:
    """
    ### Description:
        Asks the user for some input and returns it.

    ### Parameters:
        - `blank_true`   -> `bool`:
            Whether to treat a blank input as a `yes` (`1`) or a `no` (`0`).
        - `third_option` -> `bool`:
            Whether to acknowledge a third value of input, `skip` (`2`).

    ### Returns:
        returns 0, 1, or 2 depending on the user input.
    """

    choice = input().lower()
    console.print("")
    
    # blank_true >> return True if the user didn't enter anything
    if choice in ["1", "yes", "y"] or not choice and blank_true:
        return 1
    if third_option and choice in ["2", "skip"]:
        return 2
    return 0



def check_stream_existence(stream_obj: Stream, formated_filename: str, valid_filename: str) -> None:
    """
    ### Description:
        Checks if the given stream is already downloaded, and if not, downloads it.

    ### Parameters:
        - `stream_obj`        -> `Stream`.
        - `formated_filename` -> `str`:
            To name the downloaded stream.
        - `valid_filename`    -> `str`:
            The name that `pytube` will use for the downloaded stream.

    ### Returns: None.
    """
    check1 = os.path.isfile(valid_filename + '.mp4')
    check2 = os.path.isfile(formated_filename + (" (Video).mp4" if stream_obj.type == "video" else " (Audio).mp4"))
    
    if not check1 and not check2:
        stream_obj.download()
        os.rename(valid_filename + ".mp4", formated_filename + (" (Video).mp4" if stream_obj.type == "video" else " (Audio).mp4"))
    elif check1:
        os.rename(valid_filename + ".mp4", formated_filename + (" (Video).mp4" if stream_obj.type == "video" else " (Audio).mp4"))
    else:
        console.print(f"[exists][normal2]{'Video' if stream_obj.type == 'video' else 'Audio'}[/] stream already downloaded[/]\n")



def merge_streams(formated_filename: str, vid_id: str) -> None:
    """
    ### Description:
        Merges a video and an audio streams along with subtitles if there are any.

    ### Parameters:
        - `formated_filename` -> `str`:
            To name the merged file.
        - `vid_id`            -> `bool`:
            A video identifier to download subtitles.

    ### Returns: `None`.
    """

    console.print("[normal1]Starting merging...[/]")
    subtitles = download_subtitles(vid_id, formated_filename)
    try:
        merge_status = avmerger(os.getcwd(), formated_filename, subtitles)
        if not merge_status:
            raise ValueError
    except ValueError:
        console.print("[warning1]Value Error! [warning2]False[/] was returned from the merging function. Check if both streams have been downloaded correctly.[/]\n")
    except:
        console.print("[warning1]Something went wrong! Check if both the [warning2]video[/] and [warning2]audio[/] streams have been downloaded correctly.[/]")
        console.print(f"[warning2]{format_exc()}[/]\n")
    else:
        console.print(f"[normal1]File merged successfully.[/]\n")



def optional_download(formated_filename: str, option_name: str, vid_obj: YouTube) -> None:
    """
    ### Description:
        Download one of the provided optional downloads.

    ### Parameters:
        - `formated_filename` -> `str`:
            To name the optional download file.
        - `option_name`       -> `str`:
            The name of the optional download.
        - `vid_obj`           -> `YouTube`.

    ### Returns: `None`.
    """

    if not os.path.isfile(formated_filename + f" ({option_name}).txt"):
        try:
            with open(formated_filename + f" ({option_name}).txt", "w", encoding="utf-8") as option_file:
                if option_file == "Description":
                    option_file.write(vid_obj.description)
                # Add new options here.
        except:
            console.print(f"[warning1]Sorry, couldn't download the [warning2]video {option_name}[/]![/]")
            console.print(f"[warning2]{format_exc()}[/]\n")
        else:
            console.print("")
    else:
        console.print(f"[exists][normal2]Video {option_name.lower()}[/] already downloaded[/]\n")



def download_subtitles(vid_id: str, formated_filename: str) -> Literal['12', '2', '1', '']:
    """
    ### Description:
        Download video subtitles (`Eng` and `Ara`).

    ### Parameters:
        - `vid_id`            -> `bool`:
            A video identifier to download subtitles.
        - `formated_filename` -> `str`:
            To name the subtitles files.

    ### Returns:
        A string containing a number corresponding to a subtitles downloaded in a specific language.
    """

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


def select_streams(merge_option: int, categories_lengths: tuple[int, list[int]], skip_not_stop = True, res_only = False) -> list[int]:
    """
    ### Description:
        Ask the user to select from the available categories and resolutions.

    ### Parameters:
        - `merge_option`       -> `int`:
            A value of `1` or `0`.
        - `categories_lengths` -> `list[int, list[int]]`:
            A list in the next form: [number_of_categories, [number of streams in each category]].
        - `skip_not_stop`      -> `bool`:
            Whether to display `skip` or `stop`.
        - `res_only`           -> `bool`:
            Whether to accept two inputs or the normal amount. Will break the script if merge_option is `False`.

    ### Returns:
        A list containing the selected category/ies and resolution/s.
    """

    valid_choices = False
    if merge_option and not res_only:
        message = f"[normal1]Select a [normal2]category[/] and a [normal2]resolution[/] option for both the video & audio streams ([normal2]4[/] numbers) separated by [normal2]spaces[/] or [normal2]leave empty[/] to {'skip' if skip_not_stop else 'stop'}: [/]"
    elif res_only:
        message = f"[normal1]Select a [normal2]resolution[/] option for both the video & audio streams ([normal2]2[/] numbers) separated by a [normal2]space[/] or [normal2]leave empty[/] to {'skip' if skip_not_stop else 'stop'}: [/]"
    else:
        message = f"[normal1]Select a [normal2]category[/] and a [normal2]resolution[/] option separated by a [normal2]space[/] or [normal2]leave empty[/] to {'skip' if skip_not_stop else 'stop'}: [/]"
    
    # TODO - res_only will not work if merge_option is `False`
    while not valid_choices:
        console.print(message, end='')
        choices = input().split(" ")
        console.print("")

        # If choices is empty (i.e., [""]) return [0]
        if len(choices) == 1 and not choices[0]:
                return [0]

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
    return [int(choice) for choice in choices]



def format_selected_vid_streams_into_dict(   formated_filename: str,
                                        valid_filename: str, 
                                        selected_video_stream: list = None,
                                        selected_audio_stream: list = None,
                                        merge_option = False
                                    ) -> dict[str, tuple[list, str, str]]:
    """
    ### Description:
        Format the selected video streams into a formated dict.

    ### Parameters:
        - `formated_filename`     -> `str`.
        - `valid_filename`        -> `str`.
        - `selected_video_stream` -> `list[Stream, str, str, float]`:
            An augmented stream list for a video stream [Stream, vid_id, str_filesize, filesize].
        - `selected_audio_stream` -> `list[Stream, str, str, float]`:
            An augmented stream list for an audio stream [Stream, vid_id, str_filesize, filesize].
        - `merge_option`          -> `int`:
            A value of `1` or `0`.

    ### Returns:
        A dict containing (`type`) keys and (`list[augmented_stream_lists, formated_filename, valid_filename]`) as values.
    """
    
    if merge_option:
        stream_dict = {
            "video": [selected_video_stream, formated_filename, valid_filename],
            "audio": [selected_audio_stream, formated_filename, valid_filename]
        }
    
    else:
        if not stream_dict:
            vid_selected_streams = {
                "audio": [selected_audio_stream, formated_filename, valid_filename]
            }
        
        else:
            stream_dict = {
                "video": [selected_video_stream, formated_filename, valid_filename],
            }
    
    return stream_dict



def download_streams(selected_streams_for_download: list[dict[str, tuple[list, str, str]]]) -> None:
    """
    ### Description:
        Download all the chosen streams.

    ### Parameters:
        - `selected_streams_for_download` -> `str`:
            A dict containing (`type`) keys and a (`list[augmented_stream_list, formated_filename, valid_filename]`) as values.

            An `augmented_stream_list` is a list in the next format: `[Stream, vid_id, str_filesize, filesize]`.

    ### Returns:
        A dict containing (`type`) keys and (list[augmented_stream_lists, formated_filename, valid_filename]) as values.
    """

    for stream_dict in selected_streams_for_download:
        if 'video' in stream_dict:
            console.print(f"[normal1]Downloading [normal2]{stream_dict['video'][0][0].title}[/][/]")
            console.print(f"[normal1][normal2]{stream_dict['video'][0][0].mime_type}[/], [normal2]{stream_dict['video'][0][0].resolution}[/], [normal2]{stream_dict['video'][0][2].strip()}[/]...[/]")
            check_stream_existence(stream_dict['video'][0][0], stream_dict['video'][1], stream_dict['video'][2])
        
        if 'audio' in stream_dict:
            console.print(f"[normal1]Downloading [normal2]{stream_dict['audio'][0][0].mime_type}[/], [normal2]{stream_dict['audio'][0][0].abr}[/], [normal2]{stream_dict['audio'][0][2].strip()}[/]...[/]")
            check_stream_existence(stream_dict['audio'][0][0], stream_dict['audio'][1], stream_dict['audio'][2])
        
        if 'video' in stream_dict and 'audio' in stream_dict:
            merge_streams(stream_dict['video'][1], stream_dict['video'][0][1])
        console.print(f"[normal1]{'='*20}[/]")
        console.print("")
