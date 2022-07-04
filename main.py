import Links_and_Objects as lo, Video_Metadata as vmd, Utility as ut
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def download_one_video():
    # Generate a video object from the user input link
    vid_obj = lo.get_vid_obj()


    # Getting the metadata of the video
    vid_streams_dict = vmd.get_vid_metadata(vid_obj)

    print(f"Video Title: {vid_obj.title}")
    vid_duration = round(vid_obj.length/60, 2)
    print(f"Duration: {int(vid_duration)}:{int(vid_duration % 1 * 60)} min\n")

    # remove stupid colons and unsupported characters for a filename
    valid_filename    = ut.format_name(vid_obj.title, "[#<>:\"\'/\\|.?*,%]")
    formated_filename = ut.format_name(vid_obj.title, "[<>:\"/\\|?*]", " -")
    
    # Check if the video is already downloaded before doing anything
    if os.path.isfile(formated_filename + " (Merged).mp4"):
        print("This video is already downloaded")
        continue_option = ut.yes_no_choice("Do you want to download another video? (1:yes, else:NO): ")
        return continue_option

    print("A list of all the available streams is being fetched...\n")

    # printing the available streams
    print("Available streams are:")
    print("="*22)
    # [number_of_categories, [number of streams in each category]]
    categories_lengths = vmd.print_streams(vid_streams_dict)
    

    # Option_1: Download video & audio streams then merge them with ffmpeg
    merge_option = False
    if "video/mp4" in vid_streams_dict and "audio/mp4" in vid_streams_dict:
        merge_option = ut.yes_no_choice("Download video & audio streams and merge them with ffmpeg? (1:YES, else:no): ", blank_true=True)
    
    selected_streams = []
    if merge_option:
        selected_streams = ut.select_streams(True,  categories_lengths, 'Select a category and a resolution option for both the video & audio streams (4 numbers) separated by spaces or leave empty to stop: ')
    else:
        selected_streams = ut.select_streams(False, categories_lengths, 'Select a category and a resolution option separated by a space or leave empty to stop: ')
    # print("")


    if(selected_streams[0]): # if not empty
        streams_categories = list(vid_streams_dict.keys())
        selected_stream = vid_streams_dict[streams_categories[int(selected_streams[0])-1]][int(selected_streams[1])-1]

        print(f"Downloading {selected_stream[1]}, {selected_stream[-4] if merge_option or selected_stream[2] == 'video' else selected_stream[0].abr}, {selected_stream[-2].strip()}...\n")
        if not merge_option:
            selected_stream[0].download()
            os.rename(valid_filename + ".mp4", formated_filename + ".mp4")

        else:
            ut.check_stream_existence(selected_stream[0], formated_filename, valid_filename, 'video')

            # Audio stream
            selected_stream = vid_streams_dict[streams_categories[int(selected_streams[2])-1]][int(selected_streams[3])-1]
            print(f"Downloading {selected_stream[1]}, {selected_stream[0].abr}, {selected_stream[-2].strip()}...\n")
            ut.check_stream_existence(selected_stream[0], formated_filename, valid_filename, 'audio')


            # Merging the video & audio streams
            ut.merge_streams(formated_filename, selected_stream[-5])


    # Option_2: Download video description
    vid_description_option = ut.yes_no_choice("Download video description? (1:yes, else:NO): ")
    if vid_description_option:
        ut.optional_downloads(formated_filename, "Description", vid_obj)

    continue_option = ut.yes_no_choice("Do you want to download another video? (1:yes, else:NO): ")
    return continue_option



def download_many_videos(from_playlist=True):
    # Generate video objects from the (playlist input link/filepath containing video links)
    if from_playlist:
        vid_objs = lo.get_vid_objs_from_playlist()
    else:
        vid_objs = lo.get_vid_objs_from_file()

    print("Next are the videos you selected to download:")
    print("=" * 45)
    # Getting the metadata of the video objects
    selected_streams_for_download = []
    for obj_num, vid_obj in enumerate(vid_objs):
        vid_streams_dict = vmd.get_vid_metadata(vid_obj)

        print(f"Video number: {obj_num+1}", end="  |  ")
        vid_duration = round(vid_obj.length/60, 2)
        print(f"Duration: {int(vid_duration)}:{int(vid_duration % 1 * 60)} min")
        print(f"Video title:  {vid_obj.title}\n")

        # remove stupid colons and unsupported characters for a filename
        valid_filename    = ut.format_name(vid_obj.title, "[#<>:\"\'/\\|.?*,%]")
        formated_filename = ut.format_name(vid_obj.title, "[<>:\"/\\|?*]", " -")

        # Check if the video is already downloaded before doing anything
        if os.path.isfile(formated_filename + " (Merged).mp4"):
            print("This video is already downloaded\n")
            print("="*42)
            print("")
            continue

        # printing the available streams
        print("Available streams are:")
        print("="*22)
        # [number_of_categories, [number of streams in each category]]
        categories_lengths = vmd.print_streams(vid_streams_dict)


        # Option_1: Download video & audio streams then merge them with ffmpeg
        merge_option = False
        if "video/mp4" in vid_streams_dict and "audio/mp4" in vid_streams_dict:
            merge_option = ut.yes_no_choice("Download video & audio streams and merge them with ffmpeg?\nAvaliable options: (1:YES  |  -1:skip the remaining videos  |  else:no): ", blank_true=True)
        
        selected_streams = []
        if merge_option == -1:
                break
        elif merge_option == True:
            selected_streams = ut.select_streams(True,  categories_lengths, "Select a category and a resolution option for both the video & audio streams (4 numbers) separated by spaces: ")
        else:
            selected_streams = ut.select_streams(False, categories_lengths, "Select a category and a resolution option separated by a space: ")

        if(selected_streams[0]): # if not empty            
            streams_categories = list(vid_streams_dict.keys())
            
            # Get the selected category and resolution option
            selected_stream = vid_streams_dict[streams_categories[int(selected_streams[0])-1]][int(selected_streams[1])-1]

            if not merge_option:
                if selected_stream[2] == 'video':
                    selected_streams_for_download.append(ut.format_selected_stream_into_dict(formated_filename, valid_filename, selected_stream))
                else:
                    selected_streams_for_download.append(ut.format_selected_stream_into_dict(formated_filename, valid_filename, selected_audio_stream=selected_stream))
                print(f"The next {selected_stream[2]} stream has been added to the download list: {selected_stream[1]}, {selected_stream[-4] if selected_stream[2] == 'video' else selected_stream[0].abr}, {selected_stream[-2].strip()}...\n")

            else:
                # Audio stream
                selected_audio_stream = vid_streams_dict[streams_categories[int(selected_streams[2])-1]][int(selected_streams[3])-1]
                selected_streams_for_download.append(ut.format_selected_stream_into_dict(formated_filename, valid_filename, selected_stream, selected_audio_stream, merge_option=True))
                print("The next video & audio streams has been added to the download list:")
                print(f"{selected_stream[1]}, {selected_stream[-4]}, {selected_stream[-2].strip()}")
                print(f"{selected_audio_stream[1]}, {selected_audio_stream[0].abr}, {selected_audio_stream[-2].strip()}\n")
            print("="*42)
            print("")
    print("="*42)

    print(f"{len(selected_streams_for_download)} stream(s) have been added to the download list. The streams are:")
    print("=" * (len( str( len(selected_streams_for_download) ) ) + 65) )
    for stream in selected_streams_for_download:
        if stream.get('video'):
            print(f"Title: {stream['video'][0][0].title}")
            print(f"Info:  {stream['video'][0][1]}, {stream['video'][0][-4]}, {stream['video'][0][-2].strip()}", end="  +  " if stream.get('audio') else "\n")
        
        if stream.get('audio'):
            if not stream.get('video'):
                print(f"Title: {stream['audio'][0][0].title}\nInfo: ", end=" ")
            print(f"{stream['audio'][0][1]}, {stream['audio'][0][0].abr}, {stream['audio'][0][-2].strip()}")
        print("")

    if not ut.yes_no_choice("Confirm? (1:YES, else:no): ", blank_true=True):
        print("Download aborted...\n")
        return
    
    ut.download_streams(selected_streams_for_download)

    continue_option = ut.yes_no_choice("Do you want to download another playlist? (1:yes, else:NO): ")
    return continue_option



if __name__ == "__main__":
    while(True):
        continue_option = download_one_video()
        # continue_option = download_many_videos()
        if(not continue_option):
            print("Exiting...")
            os.startfile(os.path.dirname(os.path.abspath(__file__)))
            break
