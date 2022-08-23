from rich.console import Console
from rich.table import Table



# Available functions in this module:
# ['grouper_sort',  'get_vid_metadata',  'print_streams']


console = Console()


def grouper_sort(stream_list: list, group_by=1, sort_by=-1) -> dict:
    # [<Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d401e" progressive="False" type="video">, 
    #     'video/mp4', 'video', 'vid_id', '360p', False, '  1.24 GB', 1242.29]

    # [<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2" progressive="False" type="audioudio', 'mp4', None, False, '141.25 MB', 1">,
    #     'audio/mp4', 'audio', 'vid_id', None, False, '374.89 MB', 374.89]
    groups = {}

    # Group by `mime_type`, i.e., 'video/mp4', Or 'audio/mp4', or ...
    for vid_stream in stream_list: 
        groups[vid_stream[group_by]] = groups.get(vid_stream[group_by], []) + [vid_stream]
    
    # Sort by filesize
    for k in groups.keys():
        groups[k] = sorted(groups[k], key = lambda x: x[sort_by])
    
    return groups



def get_vid_metadata(vid_obj, playlist_skip_mime_types = False) -> dict:
    # The content is initially stored in a list but eventually is turned into a dict after using grouper_sort()
    vid_streams_list = []
    
    for stream in vid_obj.streams:
        if playlist_skip_mime_types and stream.mime_type not in ["video/mp4", "audio/mp4"]:
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

        vid_streams_list.append([   stream, stream.mime_type, stream.type, vid_obj.video_id,
                                    stream.resolution, stream.is_progressive, str_file_size, file_size])

    # Formatting
    vid_streams_dict = grouper_sort(vid_streams_list)

    return vid_streams_dict



# Prints and counts categories and streams
def print_streams(vid_streams_dict: dict) -> list:
    streams_in_each_category = []

    table = Table(  style         = "bold blue1", 
                    row_styles    = ["bold blue1", "bold dark_violet"],
                    header_style  = "bold deep_pink1",
                    show_lines=True)
    
    table.add_column("Category", justify="center", no_wrap=True, vertical="middle")
    table.add_column("Quality",  justify='left')
    table.add_column("Size",     justify="right")
    table.add_column("Progressive", justify="left")

    for i, k in enumerate(vid_streams_dict, 1):
        streams_in_each_category.append(len(vid_streams_dict[k]))
        
        qualities   = []
        sizes       = []
        prog_states = []
        
        for j, vid in enumerate(vid_streams_dict[k], 1):
            if vid[-4]:     # resolution
                if vid[-3]: # is_progressive
                    prog_states.append("Progressive")
                else:
                    prog_states.append("")
                qualities.append(f"{j}) {vid[-4]}")
            else:   # no resolution data, i.e. an audio stream
                qualities.append(f"{j}) {vid[0].abr}")
            sizes.append(f"{vid[-2]}")
        table.add_row(f"({i}) {k}", "\n".join(qualities), "\n".join(sizes), "\n".join(prog_states))
    console.print(table)
    console.print("")
    return [len(vid_streams_dict)] + streams_in_each_category
