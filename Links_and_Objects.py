from pytube import YouTube, Playlist 

# Available functions in this module:
# ['on_complete',            'on_progress',  'vid_link_checker',
#  'playlist_link_checker',  'get_vid_obj',  'get_vid_objs_from_file',
#  'get_vid_objs_from_playlist']


def on_complete(stream, file_path):
    # Print only the path to the downloaded file, not including the file's name as it is changed after downloading.
    path_to_file = '\\'.join((file_path.split('\\')[:-1]))
    print(f"File downloaded successfully in the next path: {path_to_file}\n")



def on_progress(stream, chunk, bytes_remaining):
    print(f"{round(100 - bytes_remaining/stream.filesize * 100, 2)}%, {round((stream.filesize - bytes_remaining)/1000/1000, 2)} : {round(stream.filesize/1000/1000, 2)} MB\r", end="")



def vid_link_checker(link):
    try:
        return YouTube(link, on_complete_callback=on_complete, on_progress_callback=on_progress)
    except:
        return False



def playlist_link_checker(link):
    try:
        return Playlist(link)
    except:
        return False



def get_vid_obj():
    print("Enter a link to a YouTube video:", end=" ")
    link_valid = False

    while(not link_valid):
        link = input()
        link_valid = vid_link_checker(link)
        if not link_valid:
            print(f"\n({link}) is not a valid link for a YouTube video.\n\nTry again:", end=" ")
    
    print("")
    return link_valid



def get_vid_objs_from_file(path):
    with open(path, 'r') as playlist:
        pass



def get_vid_objs_from_playlist():
    print("Enter a link to a YouTube playlist:", end=" ")
    link_valid = False

    # Check if the playlist link is valid
    while(not link_valid):
        playlist_link = input()
        try:
            playlist_obj = Playlist(playlist_link)
            len(playlist_obj)
            link_valid = True
        except:
            print(f"\n({playlist_link}) is not a valid link for a YouTube playlist.\n\nTry again:", end=" ")
    print("")

    # Get the playlist's video objects
    vid_objs = []
    for link_num, link in enumerate(playlist_obj):
        vid_objs.append(vid_link_checker(link))
        if not vid_objs[-1]:
            print(f"\nError encountered with video nubmer {link_num+1}: {link})\nThis is not a valid link for a YouTube video.\n")
            vid_objs.pop()
    

    # Choose the start and count of videos to download
    print(f"There are {len(vid_objs)} videos in the playlist.")
    while True:
            start_count = input("Enter the start and count of videos you want to download separated by a space or leave empty to select all: ").split(" ")
            if len(start_count) == 1 and not start_count[0]:
                print("")
                return vid_objs

            if len(start_count) == 2:
                try:
                    int(start_count[0]); int(start_count[1])
                    break
                except:
                    print(f"\nSomething went wrong. Your input: {start_count}.\nPlease enter the start and count again.\n")
    
    print("")
    return vid_objs[ int(start_count[0])-1 : int(start_count[1]) ]
