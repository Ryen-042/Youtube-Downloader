from global_imports import *
import shutil

def avmerger(directory: str, filename: str, subtitles='') -> bool:
	"""
    ### Description:
        Merge stream files along with subtitles.

    ### Parameters:
        - `directory` -> `str`:
            The path of the directory containing all the files.
		- `filename` -> `str`:
			The name of all the files the files that will be merged together.
		- `subtitles` -> `str`:
			A string containing a number corresponding to a subtitles downloaded in a specific language.

    ### Returns:
        Whether the merge operation is successful or not.
    """

	input_video  = directory + "\\" + filename + ' (Video).mp4'
	input_audio  = directory + "\\" + filename + ' (Audio).mp4'
	merged_video = directory + "\\" + filename + ' (Merged).mp4'
	ffmpeg_log   = directory + "\\ffmpeg-logs.txt"
	ffmpeg_log_copy = directory + "\\" + filename + ", ffmpeg-logs.txt"
	fixed_part1  = f"ffmpeg -loglevel error -hide_banner -nostats -i \"{input_video}\" -i \"{input_audio}\""
	fixed_part2  = f"\"{merged_video}\" 2> \"{directory}\\ffmpeg-logs.txt\""
	if subtitles:
		input_subtitles = directory + "\\" + filename
		
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

	if os.path.isfile(merged_video):
		if os.stat(ffmpeg_log).st_size == 0:
			os.remove(input_video)
			os.remove(input_audio)
			return True
		else:
			shutil.copy(ffmpeg_log, ffmpeg_log_copy)
			with open(ffmpeg_log) as ffmpeg_logs:
				console.print(f"[warning2]{ffmpeg_logs.read()}[/]")
	return False
	# else:
	# 	console.print("[warning1][warning2]Error[/]: Merged file not found[/]")
	# 	return False


if __name__ == "__main__":
	directory = input("Enter the the video path: ")
	filename  = input("\nEnter the filename: ")
	avmerger(directory, filename, "12")


## Useful Links
# -loglevel warning -hide_banner -stats To show progress
	# Source: https://superuser.com/questions/326629/how-can-i-make-ffmpeg-be-quieter-less-verbose
# Merge subtitles:
	# https://gist.github.com/berndverst/8e1b8321926426ded9555c15a2c0c837
	# https://stackoverflow.com/questions/8672809/use-ffmpeg-to-add-text-subtitles
	# https://superuser.com/questions/549179/using-ffmpeg-to-add-subtitles-to-a-m4v-video-file
