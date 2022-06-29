# Available functions in this module:
# ['grouper_sort',  'get_vid_metadata',  'print_streams']

def grouper_sort(vlist, group_by=1, sort_by=-1):
    # [<Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d401e" progressive="False" type="video">, 
    #     'video/mp4', 'video', 'mp4', '360p', False, '  1.24 GB', 1242.29]

    # [<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2" progressive="False" type="audioudio', 'mp4', None, False, '141.25 MB', 1">,
    #     'audio/mp4', 'audio', 'mp4', None, False, '374.89 MB', 374.89]
    groups = {}

    # Group by `mime_type`, i.e., 'video/mp4', Or 'audio/mp4', or ...
    for vid_stream in vlist: 
        groups[vid_stream[group_by]] = groups.get(vid_stream[group_by], []) + [vid_stream]
    
    # Sort by filesize
    for k in groups.keys():
        groups[k] = sorted(groups[k], key = lambda x: x[sort_by])
    
    return groups



def get_vid_metadata(vid_obj):
    # Initially a list but becomes a dict after using grouper_sort()
    vid_streams_dict = []
    
    for stream in vid_obj.streams:
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

        vid_streams_dict.append([stream, stream.mime_type, stream.type, stream.subtype, stream.resolution, "Progressive" if stream.is_progressive else False, str_file_size, file_size])

    # Formatting
    vid_streams_dict = grouper_sort(vid_streams_dict)

    return vid_streams_dict


# Prints and counts categories and streams
def print_streams(vid_streams_dict):
    streams_in_each_category = []
    for i, k in enumerate(vid_streams_dict, 1):
        streams_in_each_category.append(len(vid_streams_dict[k]))
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
    
    return [len(vid_streams_dict)] + streams_in_each_category
