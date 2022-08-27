from rich.console import Console
from rich.table import Table

# For type hinting only
from pytube import YouTube


# Available functions in this module:
# ['grouper_sort',  'get_vid_metadata',  'print_streams']


console = Console()


def grouper_sort(stream_list: list[list], group_by=1, sort_by=3) -> dict[str, list[list]]:
    """
    ### Description:
        Takes a list of augmented stream lists and returns a dictionary after grouping
        the streams from the same category together.

    ### Parameters:
        - `stream_list` -> `list[list[Stream, str, str, float]]`:
            A list of augmented stream lists.
            
            An `augmented_stream_list` is a list in the next format: `[Stream, vid_id, str_filesize, filesize]`.
        - `group_by`    -> `int`:
            The grouping strategy to use. Defaults to group by `mime_type`.
        - `sort_by`     -> `int`:
            The sorting strategy to use. Defaults to sort by `filesize`.

    ### Returns:
        A dict containing (`mime_type`) keys and (list of augmented stream lists) as values.
    """

    # [<Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d401e" progressive="False" type="video">,
    #     'vid_id', '  1.24 GB', 1242.29]
    # [<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2" progressive="False" type="audioudio', 'mp4', None, False, '141.25 MB', 1">,
    #     'vid_id', '374.89 MB', 374.89 ]
    groups = {}

    # Group by `mime_type`, i.e., ['video/mp4', 'audio/mp4', ...]
    for vid_stream in stream_list:
        match group_by:
            case 1: groups[vid_stream[0].mime_type] = groups.get(vid_stream[0].mime_type, []) + [vid_stream]
    
    # Sort by filesize
    for k in groups.keys():
        groups[k] = sorted(groups[k], key = lambda x: x[sort_by])
    
    return groups



def get_vid_metadata(vid_obj: YouTube, skip_mime_types_not_mp4 = False) -> dict[str, list[list]]:
    """
    ### Description:
        Takes a `YouTube` objects and returns a dictionary after grouping
        its streams from the same category together.

    ### Parameters:
        - `vid_obj`                 -> `YouTube`.
        - `skip_mime_types_not_mp4` -> `bool`:
            To skip any streams that are not `.mp4`.

    ### Returns:
        A dict containing (`mime_type`) keys and (list of augmented stream lists) as values. Ex:
            
            {"video/mp4": [[stream_obj, vid_obj.video_id, str_file_size, file_size], ...],
             "audio/mp4": ...}
    """
    # Augmented stream list: [<Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d401e" progressive="False" type="video">, 'vid_id', '  1.24 GB', 1242.29]

    # The content is initially stored in a list but eventually is turned into a dict after using grouper_sort()
    vid_augmented_streams_list = []
    
    for stream in vid_obj.streams:
        # Don't store info about any streams that are not `.mp4` (used in download_many_videos())
        if skip_mime_types_not_mp4 and stream.mime_type not in ["video/mp4", "audio/mp4"]:
            continue
        
        # Sometimes, one or more streams for are corrupted, their sizes are unknown and raises an error when accessed, and 
        # cannot be downloaded (but some other data are accessable).
        try:
            file_size = round(stream.filesize/1000/1000, 2)
        except:
            file_size = 0.001 # if the stream is corrupted, store its file_size as 0.001 MB
        str_file_size = ""

        if   file_size == 0.001:
            continue
        elif file_size > 1000:
                str_file_size = f"{round(file_size/1000, 2):6} GB"
        else:   str_file_size = f"{file_size:6} MB"

        # vid_augmented_streams_list.append([   stream, stream.mime_type, stream.type, vid_obj.video_id,
                                    # stream.resolution, stream.is_progressive, str_file_size, file_size])
        vid_augmented_streams_list.append([stream, vid_obj.video_id, str_file_size, file_size])

    # Formatting to a vid_augmented_streams_dict.
    return grouper_sort(vid_augmented_streams_list)



# Prints and counts categories and streams
def print_streams(vid_augmented_streams_dict: dict[str, list[list]]) -> list:
    """
    ### Description:
        Takes a `YouTube` objects and returns a dictionary after grouping

    ### Parameters:
        - `vid_augmented_streams_dict` -> `dict[str, list[list]]`:
            dict containing (`mime_type`) keys and (list of augmented stream lists) as values.

    ### Returns:
        A list in the next format: [number_of_categories, [number of streams in each category]]
    """

    streams_in_each_category = []

    table = Table(  style         = "bold blue1", 
                    row_styles    = ["bold blue1", "bold dark_violet"],
                    header_style  = "bold deep_pink1",
                    show_lines=True)
    
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
    return [len(vid_augmented_streams_dict)] + streams_in_each_category
