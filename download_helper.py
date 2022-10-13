"""
This module provides functions for selecting, formatting, and downloading streams.
"""
# Postponed evaluation of annotations, for more info: https://docs.python.org/3/whatsnew/3.7.html#pep-563-postponed-evaluation-of-annotations
from __future__ import annotations
from traceback import print_exc
from re import sub
from global_imports import *
from avmerger import avmerger
from http.client import IncompleteRead # HTTP Exception Type

# TYPE_CHECKING: A special constant that is assumed to be True by 3rd party static type checkers. It is False at runtime. Usage:
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pytube import YouTube
    from pytube.streams import Stream

# Available functions in this module:
# ['format_name',    'yes_no_choice',     'check_stream_existence',
#  'merge_streams',  'optional_download', 'download_subtitles',
#  'select_streams', 'format_selected_vid_streams_into_dict', 'download_streams']


# valid_filename:    [<>\"/\\?*:|#\'.,%]
# formated_filename: [<>\"/\\?*:|]
def format_name(name: str, pytube_format=False) -> str:
    """
    Description:
        Takes an unformatted name and format it to be used as filename.
    ---
    Parameters:
        `name` (`str`)
            An unformatted name.
        
        `pytube_format` (`bool`)
            There are valid filename characters that pytube omits when it downloads anything.
            
            To format names like what pytube does, these characters will be removed.
    
    ---
    Returns:
        (`str`) => A formated name valid to be used as a filename.
    """
    
    new_name    = sub('[<>\"/\\?*]', "", name)
    new_name    = new_name.replace("\\", "")
    
    # pytube_format is only set for `valid_filename`.
    if not pytube_format:
        new_name    = sub('[:]', ".", new_name)
        new_name    = sub('[|]', "-", new_name)
        
        # removeing multiple spaces
        new_name    = sub(' +', ' ', new_name)
    
    else:
        # Some of these characters are valid filename characters that pytube omit.
        new_name    = sub('[:|#\'.,%]', "", new_name)
    
    return new_name

#!
def yes_no_choice(blank_true=False, third_option=False) -> int:
    """
    Description:
        Asks the user for some input and returns it.
    ---
    Parameters:
        `blank_true`   (`bool`)
            Whether to treat a blank input as a `"yes"` (`1`) or a `"no"` (`0`).
        
        `third_option` (`bool`)
            Whether to acknowledge a third value of input, `"skip"` (`2`).
    ---
    Returns:
        (`int`) => returns 0, 1, or 2 depending on the user input.
    """
    
    choice = input().strip().lower()
    console.print("")
    
    # blank_true >> Returns `True` if the user didn't enter anything
    if choice in ["1", "yes", "y"] or not choice and blank_true:
        return 1
    
    if third_option and choice in ["2", "skip"]:
        return 2
    
    return 0


def check_stream_existence(stream_obj: Stream, formated_filename: str, valid_filename: str) -> None:
    """
    Description:
        Checks if the given stream is already downloaded, and if not, downloads it.
    ---
    Parameters:
        `stream_obj` (`Stream`).
        
        `formated_filename` (`str`)
            To name the downloaded stream.
        
        `valid_filename` (`str`)
            The name that `pytube` will use for the downloaded stream.
    ---
    Returns: `None`.
    """
    valid_filename    += f".{stream_obj.subtype}" # '.mp4'
    # Notice that we will change the file extension to `.mp4` if it was anything else.
    formated_filename += f" ({stream_obj.type.capitalize()}).mp4"
    
    check1 = os.path.isfile(valid_filename)
    check2 = os.path.isfile(formated_filename)
    
    stream_size = 0
    if check1:
        stream_size = os.path.getsize(valid_filename)
    elif check2:
        stream_size = os.path.getsize(formated_filename)
    
    
    # If both checks is false, then no files are downloaded
    if not check1 and not check2:
        stream_obj.download(max_retries=10)
        os.rename(valid_filename, formated_filename)
    
    # If check1 and the downloaded filesize is 0, then the file is created locally but no data is downloaded
    elif check1 and stream_size==0:
        console.print(f"[exists][normal2]{stream_obj.type.capitalize()}[/] stream exists but [normal2]empty[/].[/]\n")
        # `skip_existing=False` overrides the downloaded file if it exists
        stream_obj.download(skip_existing=False, max_retries=10)
        os.rename(valid_filename, formated_filename)
    
    # Same as above but the file is not renamed yet
    elif check2 and stream_size==0:
        console.print(f"[exists][normal2]{stream_obj.type.capitalize()}[/] stream exists but [normal2]empty[/].[/]\n")
        os.remove(formated_filename) # delete the empty merged file
        stream_obj.download(skip_existing=False, max_retries=10)
        os.rename(valid_filename, formated_filename)
    
    elif check1 and not check2:
        console.print(f"[exists][normal2]{stream_obj.type.capitalize()}[/] stream already downloaded but [normal2]its name is not formatted[/].[/]\n")
        os.rename(valid_filename, formated_filename)
    else:
        console.print(f"[exists][normal2]{stream_obj.type.capitalize()}[/] stream already downloaded[/]\n")



def merge_streams(formated_filename: str, vid_id: str, no_subtitles: bool=False) -> None:
    """
    Description:
        Merges a video and an audio streams along with subtitles if there are any.
    ---
    Parameters:
        `formated_filename` (`str`)
            To name the merged file.
        
        `vid_id` (`bool`)
            A video identifier to download subtitles.
        
        `no_subtitles` (`bool`)
            Specify whether to skip downloading subtitles or not.
    ---
    Returns: `None`.
    """
    
    console.print("[normal1]Starting merging...[/]")
    subtitles = ""
    if not no_subtitles:
        subtitles = download_subtitles(vid_id, formated_filename)
    
    try:
        merge_status = avmerger(os.getcwd(), formated_filename, subtitles)
    #     if not merge_status:
    #         raise ValueError
    # except ValueError:
    #     console.print("[warning1]Value Error! [warning2]False[/] was returned from the merging function. Check if both streams have been downloaded correctly.[/]\n")
    except:
        console.print("[warning1]An unexpected error occurred while merging streams for the current video.[/]")
        print_exc()
        console.print("")
    else:
        console.print("[normal1]File merged successfully.[/]\n")


def optional_downloads(formated_filename: str, option_name: str, vid_obj: YouTube) -> None:
    """
    Description:
        Download one of the provided optional downloads.
    ---
    Parameters:
        `formated_filename` (`str`)
            To name the optional download file.
        
        `option_name` (`str`)
            The name of the optional download.
        
        `vid_obj` (`YouTube`).
    
    ---
    Returns: `None`.
    """
    file_exists = os.path.isfile(formated_filename + f" ({option_name}).txt")
    if not file_exists or file_exists and os.path.getsize(os.path.join(os.getcwd(), f"{formated_filename} ({option_name}).txt")) == 0:
        try:
            if option_name == "Description":
                description = vid_obj.description
                if len(description):
                    with open(formated_filename + f" ({option_name}).txt", "w", encoding="utf-8") as option_file:
                        option_file.write(vid_obj.description)
            # Add new options here.
        except:
            console.print(f"[warning1]Sorry, couldn't download the [warning2]video {option_name}[/]![/]")
        # console.print("")
    else:
        console.print(f"[exists][normal2]Video {option_name.lower()}[/] already downloaded[/]\n")



def download_subtitles(vid_id: str, formated_filename: str) -> str:
    """
    Description:
        Download video subtitles (`Eng` and `Ara`).
    ---
    Parameters:
        `vid_id` (`bool`)
            A video identifier to download subtitles.
        
        `formated_filename` (`str`)
            To name the subtitle files.
    ---
    Returns:
        (`string`) => The concatenation of one or two numbers corresponding to a subtitle downloaded in a specific language.
        
        `"1"`: English.
        `"2"`: Arabic.
        `"12"`: Arabic & English.
    """
    
    if not os.path.isfile(formated_filename + ".en.vtt") and not os.path.isfile(formated_filename + ".ar.vtt"):
        console.print("[normal1]Downloading [normal2]subtitles[/]...[/]")
        # https://write.corbpie.com/downloading-youtube-videos-and-playlists-with-yt-dlp/
        
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
        console.print("[exists][normal2]Subtitles[/] already downloaded.[/]")
    
    subtitles = ""
    if os.path.isfile(formated_filename + ".en.vtt"):
        subtitles += "1"
    if os.path.isfile(formated_filename + ".ar.vtt"):
        subtitles += "2"
    return subtitles


def select_streams(merge_option: int, categories_lengths: list[int], skip_not_stop = True, res_only = False) -> list[int]:
    """
    Description:
        Asks the user to select from the available categories and resolutions.
    ---
    Parameters:
        `merge_option` (`int`)
            A value of `1` or `2`.
        
        `categories_lengths` (`list[int]`)
            The number of streams in each category.
        
        `skip_not_stop` (`bool`)
            Whether to display `skip` or `stop`.
        
        `res_only` (`bool`)
            Whether to accept two inputs or the normal amount. Will break the script if `merge_option` is `1`.
    ---
    Returns:
        (`list(int)`) => A list containing the selected category/ies and resolution/s.
    """
    
    if merge_option == 1 and res_only:
        console.print("[warning1]WARNING! `[warning2][i]res_only = True[/][/]` and [warning2][i]`merge_option = 1[/][/]` detected.[/]")
        console.print("[normal1]`[normal2]res_only[/]` will be set to [normal2]Null[/].[/]\n")
        res_only = False
    
    valid_choices = False
    if merge_option == 2 and not res_only:
        message = f"[normal1]Select a [normal2]category[/] and a [normal2]resolution[/] option for both the video & audio streams ([normal2]4[/] numbers) separated by [normal2]spaces[/] or [normal2]leave empty[/] to {'skip' if skip_not_stop else 'stop'}: [/]"
    elif res_only:
        message = f"[normal1]Select a [normal2]resolution[/] option for both the video & audio streams ([normal2]2[/] numbers) separated by a [normal2]space[/] or [normal2]leave empty[/] to {'skip' if skip_not_stop else 'stop'}: [/]"
    else:
        message = f"[normal1]Select a [normal2]category[/] and a [normal2]resolution[/] option separated by a [normal2]space[/] or [normal2]leave empty[/] to {'skip' if skip_not_stop else 'stop'}: [/]"
    
    # TODO - `res_only=True` can cause problems if merge_option is `1`
    while not valid_choices:
        console.print(message, end='')
        choices = input().strip().split(" ")
        console.print("")
        
        # If choices is empty (i.e., [""]) return [0]
        if len(choices) == 1 and not choices[0]:
            return [0]
        
        if not res_only and len(choices) > (4 if merge_option==2 else 2) or res_only and len(choices) > 2:
            console.print(f"[warning1]Invalid input. Requested [warning2]{2 if res_only else 4 if merge_option==2 else 2}[/] numbers, but got [warning2]{len(choices)}[/] inputs. Your input: [warning2]{choices}[/][/]\n")
            continue
        
        elif not res_only and len(choices) != (4 if merge_option==2 else 2) or res_only and len(choices) != 2:
            console.print(f"[warning1][warning2]Not enough data[/]. Requested [warning2]{2 if res_only else 4 if merge_option==2 else 2}[/] numbers, but got [warning2]{len(choices)}[/] input{'s' if len(choices) > 1 else ''}. Your input: [warning2]{choices}[/][/]\n")
            continue
        
        if res_only and merge_option == 2:
            choices = ["1", choices[0], "2", choices[1]]
        
        try:
            if int(choices[0]) <= len(categories_lengths):
                if merge_option == 2 and int(choices[2]) <= len(categories_lengths) or merge_option == 1:
                    for j, i in enumerate(range(1, len(choices), 2)):
                        if not res_only and int(choices[i]) <= categories_lengths[int(choices[i-1])-1]:
                            continue
                        if int(choices[i]) > categories_lengths[j]:
                            console.print(int(choices[i]), categories_lengths[j])
                            console.print(f"[warning1][warning2]Error Encountered[/]. Make sure the [warning2]selected stream number{'s[/] are' if merge_option == 2 else '[/] is'} correct. Your input: [warning2]{choices}[/][/]\n")
                            break
                    else:
                        valid_choices = True
                elif merge_option == 2 and int(choices[2]) > len(categories_lengths):
                    console.print(f"[warning1][warning2]Error Encountered[/]. Make sure the [warning2]second selected category number[/] is correct. Your input: [warning2]{choices}[/][/]\n")
            else:
                console.print(f"[warning1][warning2]Error Encountered[/]. Make sure the [warning2]{'first' if merge_option == 2 else ''} selected category number[/] is correct. Your input: [warning2]{choices}[/][/]\n")
        except:
            console.print(f"[warning1]Invalid input. You have entered something wrong. Your input: [warning2]{choices}[/][/]\n")
    return [int(choice) if choice !="-" else "-" for choice in choices]



def format_selected_vid_streams_into_dict(formated_filename: str, valid_filename: str, first_selected_stream: list = None,
                                            second_selected_stream: list = None) -> dict[str, list]:
    """
    Description:
        Format the selected video streams into a formated dict.
    ---
    Parameters:
        `formated_filename` (`str`).
        
        `valid_filename` (`str`).
        
        `first_selected_stream` (`list[Stream, str, str, float]`)
            An augmented stream list for one (the first) stream.
        
        `second_selected_stream` (`list[Stream, str, str, float]`)
            An augmented stream list for the second stream. Only used if `merge_option == 2`.
            
            An `augmented stream list` is a list in the next format: `[Stream, vid_id, str_filesize, filesize]`
    
    ---
    Returns:
        (`dict`) => A dict containing (`type`) keys and (`list[augmented_stream_lists, formated_filename, valid_filename]`) as values.
    """
    
    if second_selected_stream:
        stream_dict = {
            first_selected_stream[0].type: [first_selected_stream, formated_filename, valid_filename],
            second_selected_stream[0].type: [second_selected_stream, formated_filename, valid_filename]
        }
    
    else:
        stream_dict = {
            first_selected_stream[0].type: [second_selected_stream, formated_filename, valid_filename]
        }
    return stream_dict



def download_streams(selected_streams_for_download: list[dict[str, list]], no_subtitles: bool = False) -> None:
    """
    Description:
        Download all the chosen streams.
    ---
    Parameters:
        `selected_streams_for_download` (`list[dict[str, list]]`)
            A dict containing (`type`) keys and a (`list[augmented_stream_list, formated_filename, valid_filename]`) as values.
            
            An `augmented_stream_list` is a list in the next format: `[[Stream, vid_id, str_filesize, filesize], ...]`.
            
        `no_subtitles` (`bool`)
            Specify whether to skip downloading subtitles or not.
    
    ---
    Returns:
        (`list[dict[str, list]]`) => A list similar to `selected_streams_for_download` containing all the failed to download streams.
    """
    failed_merges = []
    failed_downloads = []
    for stream_counter, stream_dict in enumerate(selected_streams_for_download):
        try:
            if 'video' in stream_dict:
                console.print(f"[normal1]► [normal2]{stream_dict['video'][0][0].title}[/][/]")
                console.print("-" * (2 + len(stream_dict['video'][0][0].title)))
                
                console.print(f"[normal1]➜ Downloading [normal2]{stream_dict['video'][0][0].mime_type}[/], [normal2]{stream_dict['video'][0][0].resolution}[/], [normal2]{stream_dict['video'][0][2].strip()}[/]...[/]")
                check_stream_existence(stream_dict['video'][0][0], stream_dict['video'][1], stream_dict['video'][2])
            
            if 'audio' in stream_dict:
                console.print(f"[normal1]➜ Downloading [normal2]{stream_dict['audio'][0][0].mime_type}[/], [normal2]{stream_dict['audio'][0][0].abr}[/], [normal2]{stream_dict['audio'][0][2].strip()}[/]...[/]")
                check_stream_existence(stream_dict['audio'][0][0], stream_dict['audio'][1], stream_dict['audio'][2])
        except IncompleteRead:
            # TODO: Check if the stream is partially downloaded
            print_exc()
            failed_downloads.append(stream_counter)
            console.print("")
            console.print(f"[normal1]{'='*20}[/]")
            console.print("")
            continue
        
        if 'video' in stream_dict and 'audio' in stream_dict:
            if merge_streams(stream_dict['video'][1], stream_dict['video'][0][1], no_subtitles) == -1:
                failed_merges.append(stream_dict['video'][1])
        console.print(f"[normal1]{'='*20}[/]")
        console.print("")
    if len(failed_merges):
        console.print(f"[warning1]The following files have not been merged:\n")
        console.print('\n'.join(failed_merges))
        console.print("")
    return [selected_streams_for_download[i] for i in failed_downloads]
