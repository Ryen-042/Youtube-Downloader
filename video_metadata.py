"""
This module provides functions for dealing with the metadata of `YouTube` objects.
"""
from __future__ import annotations
from rich.console import Console
from rich.table import Table
from rich import box

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pytube import YouTube


# Available functions in this module:
# ['grouper_sort',  'get_vid_metadata',  'print_streams']


console = Console()


def grouper_sort(stream_list: list[list], group_by=1, sort_by=3) -> dict[str, list[list]]:
    """
    Description:
        Takes a list of augmented stream lists and returns a dictionary after grouping the streams from the same category together.
    ---
    Parameters:
        `stream_list` (`list[list]`)
            A list of augmented stream lists.
            
            An `augmented_stream_list` is a list in the next format: `[[Stream, vid_id, str_filesize, filesize], ...]`.
        
        `group_by` (`int`)
            The grouping strategy to use. Defaults to group by `mime_type`.
        
        `sort_by` (`int`)
            The sorting strategy to use. Defaults to sort by `filesize`.
    ---
    Returns:
        (`dict[str, list[list]]`) => A dict containing (`mime_type`) keys and (`list of augmented stream lists`) as values.
    """
    
    # [<Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d401e" progressive="False" type="video">,
    #     'vid_id', '  1.24 GB', 1242.29]
    # [<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2" progressive="False" type="audioudio', 'mp4', None, False, '141.25 MB', 1">,
    #     'vid_id', '374.89 MB', 374.89 ]
    groups: dict[str, list[list]] = {}
    
    # Group by `mime_type`, i.e., ['video/mp4', 'audio/mp4', ...]
    for vid_stream in stream_list:
        match group_by:
            case 1: groups[vid_stream[0].mime_type] = groups.get(vid_stream[0].mime_type, []) + [vid_stream]
            # Add any other criteria here
    
    # Sort by filesize
    for k in groups:
        groups[k] = sorted(groups[k], key = lambda x: x[sort_by])
    
    return groups



def get_vid_metadata(vid_obj: YouTube, mp4_only = False) -> dict[str, list[list]]:
    """
    Description:
        Takes a `YouTube` objects and returns a dictionary after grouping its streams from the same category together.
    ---
    Parameters:
        `vid_obj` (`YouTube`).
        
        `mp4_only` (`bool`):
            To skip any streams that are not `.mp4`.
    ---
    Returns:
        A dict containing (`mime_type`) keys and (list of augmented stream lists) as values. Ex:
            {"video/mp4": [[stream_obj, vid_obj.video_id, str_file_size, file_size], ...],
             "audio/mp4": ...}
    """
    
    # The content in this list eventually will be moved into a dict after using grouper_sort().
    vid_augmented_streams_list = []
    
    for stream in vid_obj.streams:
        # Don't store info about any streams that are not `.mp4` (used in download_many_videos()).
        if mp4_only and stream.subtype != "mp4":
            continue
        
        # Sometimes, one or more streams for are corrupted, their sizes are unknown and raises an error when accessed, and
        # cannot be downloaded (but some other data are accessable).
        try:
            file_size = round(stream.filesize/1024/1024, 2) # Size in MBs
        except:
            file_size = 0.001 # If the stream is corrupted, store its file_size as 0.001 MB
        str_file_size = ""
        
        # if   file_size == 0.001:
            # continue
        
        if file_size > 1023:
            str_file_size = f"{round(file_size/1024, 2):7.2f} GB"
        else:   str_file_size = f"{file_size:7.2f} MB"
        
        vid_augmented_streams_list.append([stream, vid_obj.video_id, str_file_size, file_size])
    
    # Formatting to a vid_augmented_streams_dict.
    return grouper_sort(vid_augmented_streams_list)


# Prints and counts categories and streams
def print_streams(vid_augmented_streams_dict: dict[str, list[list]]) -> list[int]:
    """
    Description:
        Takes a `YouTube` objects and returns a dictionary after grouping.
    ---
    Parameters:
        `vid_augmented_streams_dict` (`dict[str, list[list]]`)
            dict containing (`mime_type`) keys and (list of augmented stream lists) as values.
    ---
    Returns:
        (`list[int]`) => A list containing the number of streams in each category.
    """
    
    streams_in_each_category = []
    bg_color = f" on #00005f"
    table = Table(  style         = "bold blue1"+bg_color,
                    row_styles    = ["bold medium_purple3"+bg_color, "bold dark_violet"+bg_color],
                    header_style  = "bold deep_pink1"+bg_color,
                    show_lines=True, box = box.DOUBLE)
    
    table.add_column("Category", justify="center", no_wrap=True, vertical="middle")
    table.add_column("Quality",  justify='left')
    table.add_column("Size",     justify="right")
    table.add_column("Progressive", justify="left")
    
    for i, k in enumerate(vid_augmented_streams_dict, 1):
        streams_in_each_category.append(len(vid_augmented_streams_dict[k]))
        
        qualities   = []
        sizes       = []
        prog_states = []
        
        for j, vid in enumerate(vid_augmented_streams_dict[k], 1):
            if vid[0].resolution:     # resolution
                if vid[0].is_progressive: # is_progressive
                    prog_states.append("Progressive")
                else:
                    prog_states.append("")
                qualities.append(f"{j}) {vid[0].resolution}")
            else:   # no resolution data, i.e. an audio stream
                qualities.append(f"{j}) {vid[0].abr}")
            sizes.append(f"{vid[2]}")
        table.add_row(f"({i}) {k}", "\n".join(qualities), "\n".join(sizes), "\n".join(prog_states))
    console.print(table)
    console.print("")
    return streams_in_each_category
