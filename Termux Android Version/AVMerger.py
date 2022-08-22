from global_imports import *

def avmerger(directory, filename, subtitles=''):
	input_video  = directory + "/" + filename + ' (Video).mp4'
	input_audio  = directory + "/" + filename + ' (Audio).mp4'
	merged_video = directory + "/" + filename + ' (Merged).mp4'
	ffmpeg_log   = f"{directory}/ffmpeglogs.txt"
	fixed_part1  = f"ffmpeg -loglevel error -hide_banner -nostats -i \"{input_video}\" -i \"{input_audio}\""
	fixed_part2  = f"\"{merged_video}\" 2> \"{directory}/ffmpeglogs.txt\""
	if subtitles:
		input_subtitles = directory + "/" + filename
		
		if subtitles == '12':
			os.system(f"{fixed_part1} -i \"{input_subtitles}\".en.vtt -i \"{input_subtitles}\".ar.vtt -map 0:v -map 1:a -map 2:s -map 3:s -c:v copy -c:a copy -c:s:0 mov_text -c:s:1 mov_text -metadata:s:s:0 language=eng -metadata:s:s:1 language=ara {fixed_part2}")
			if os.stat(ffmpeg_log).st_size == 0:
				os.remove(input_subtitles + ".en.vtt")
				os.remove(input_subtitles + ".ar.vtt")
			else:
				with open(ffmpeg_log) as ffmpeg_logs:
					console.print(f"[warning2]{ffmpeg_logs.read()}[/]")
				return False
		elif subtitles == '1':
			os.system(f"{fixed_part1} -i \"{input_subtitles}\".en.vtt -map 0:v -map 1:a -map 2:s -c:v copy -c:a copy -c:s mov_text -metadata:s:s:0 language=eng {fixed_part2}")
			if os.stat(ffmpeg_log).st_size == 0:
				os.remove(input_subtitles + ".en.vtt")
			else:
				with open(f"\"{directory}\"/ffmpeglogs.txt") as ffmpeg_logs:
					console.print(f"[warning2]{ffmpeg_logs.read()}[/]")
				return False
		else:
			os.system(f"{fixed_part1} -i \"{input_subtitles}\".ar.vtt -map 0:v -map 1:a -map 2:s -c:v copy -c:a copy -c:s mov_text -metadata:s:s:0 language=ara {fixed_part2}")
			if os.stat(ffmpeg_log).st_size == 0:
				os.remove(input_subtitles + ".ar.vtt")
			else:
				with open(f"\"{directory}\"/ffmpeglogs.txt") as ffmpeg_logs:
					console.print(f"[warning2]{ffmpeg_logs.read()}[/]")
				return False
	else:
		os.system(f"{fixed_part1} -c copy {fixed_part2}")
	
	if os.path.isfile(merged_video):
		if os.stat(ffmpeg_log).st_size == 0:
			os.remove(input_video)
			os.remove(input_audio)
			return True
		else:
			with open(f"\"{directory}\"/ffmpeglogs.txt") as ffmpeg_logs:
				console.print(f"[warning2]{ffmpeg_logs.read()}[/]")
	return False