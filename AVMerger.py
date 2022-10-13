"""
AVMerger means `Audio/Video Merger`.

This module provides a function for merging two streams (video + audio) and subtitle files.
"""

from global_imports import *

def avmerger(save_directory_path: str, unified_filename: str, subtitles='') -> int:
    """
    Description:
        Merge streams along with subtitle files.
    ---
    Parameters:
        `save_directory_path` (`str`)
            The path to the directory containing all the files.
        
        `unified_filename`  (`str`)
            The common name of all the files the files that will be merged together.
        
        `subtitles` (`str`)
            A string containing a number corresponding to a subtitle file downloaded in a specific language.
    ---
    Returns:
        (`int`) => The status code value representing the success or failure of the merge operation.
    """

    input_video  = os.path.join(save_directory_path, unified_filename + ' (Video).mp4')
    input_audio  = os.path.join(save_directory_path, unified_filename + ' (Audio).mp4')
    merged_video = os.path.join(save_directory_path, unified_filename + ' (Merged).mp4')
    ffmpeg_log   = os.path.join(save_directory_path, "ffmpeg-logs.txt")
    fixed_part1  = f"ffmpeg -loglevel error -hide_banner -nostats -i \"{input_video}\" -i \"{input_audio}\""
    fixed_part2  = f"\"{merged_video}\" 2> \"{os.path.join(save_directory_path, 'ffmpeg-logs.txt')}\""

    if subtitles:
        input_subtitles = os.path.join(save_directory_path, unified_filename)
        
        if subtitles == '12':
            os.system(f"{fixed_part1} -i \"{input_subtitles}\".en.vtt -i \"{input_subtitles}\".ar.vtt -map 0:v -map 1:a -map 2:s -map 3:s -c:v copy -c:a copy -c:s:0 mov_text -c:s:1 mov_text -metadata:s:s:0 language=eng -metadata:s:s:1 language=ara {fixed_part2}")
            if os.stat(ffmpeg_log).st_size == 0:
                os.remove(input_subtitles + ".en.vtt")
                os.remove(input_subtitles + ".ar.vtt")
        
        elif subtitles == '1':
            os.system(f"{fixed_part1} -i \"{input_subtitles}\".en.vtt -map 0:v -map 1:a -map 2:s -c:v copy -c:a copy -c:s mov_text -metadata:s:s:0 language=eng {fixed_part2}")
            if os.stat(ffmpeg_log).st_size == 0:
                os.remove(input_subtitles + ".en.vtt")
        
        else:
            os.system(f"{fixed_part1} -i \"{input_subtitles}\".ar.vtt -map 0:v -map 1:a -map 2:s -c:v copy -c:a copy -c:s mov_text -metadata:s:s:0 language=ara {fixed_part2}")
            if os.stat(ffmpeg_log).st_size == 0:
                os.remove(input_subtitles + ".ar.vtt")
    else:
        os.system(f"{fixed_part1} -c copy {fixed_part2}")
    
    merged_file = os.path.isfile(merged_video)
    if merged_file:
        if os.stat(ffmpeg_log).st_size == 0:
            os.remove(input_video)
            os.remove(input_audio)
            return 1 # Merged successfully
        else:
            console.print("[warning1]Something went wrong. The video is merged but the next error occurred:\n")
    else:
        console.print("[warning1]Warning! The merge operation has failed. The next error has occurred:\n[/]")
    
    # Copy the error logs from "ffmpeg-logs.txt" and append it to "ffmpeg-logs-history.txt"
    with open(ffmpeg_log, 'r', encoding='utf-8') as f1, open(os.path.join(save_directory_path, "ffmpeg-logs-history.txt"), 'w', encoding='utf-8') as f2:
        f2.write(f1.read() + "\n")
        console.print(f"[warning2]{f1.read()}[/]")
    
    if merged_file:
        return 0  # Merged but error occurred
    else:
        return -1 # Not merged


if __name__ == "__main__":
    save_directory_path = input("Enter the the video path: ")
    unified_filename  = input("\nEnter the filename: ")
    
    avmerger(save_directory_path, unified_filename)


## Useful Links
# -loglevel warning -hide_banner -stats To show progress
    # Source: https://superuser.com/questions/326629/how-can-i-make-ffmpeg-be-quieter-less-verbose
# Merge subtitles:
    # https://gist.github.com/berndverst/8e1b8321926426ded9555c15a2c0c837
    # https://stackoverflow.com/questions/8672809/use-ffmpeg-to-add-text-subtitles
    # https://superuser.com/questions/549179/using-ffmpeg-to-add-subtitles-to-a-m4v-video-file
