import os

def avmerger(directory, filename, subtitles=''):
	input_video  = directory + "\\" + filename + ' (Video).mp4'
	input_audio  = directory + "\\" + filename + ' (Audio).mp4'
	merged_video = directory + "\\" + filename + ' (Merged).mp4'
	
	if subtitles:
		input_subtitles = directory + "\\" + filename
		if subtitles == '12':
			os.system(f"ffmpeg -loglevel error -hide_banner -nostats -i \"{input_video}\" -i \"{input_audio}\" -i \"{input_subtitles}\".en.vtt -i \"{input_subtitles}\".ar.vtt -map 0:v -map 1:a -map 2:s -map 3:s -c:v copy -c:a copy -c:s:0 mov_text -c:s:1 mov_text -metadata:s:s:0 language=eng -metadata:s:s:1 language=ara \"{merged_video}\"")
			os.remove(input_subtitles + ".en.vtt")
			os.remove(input_subtitles + ".ar.vtt")
		elif subtitles == '1':
			os.system(f"ffmpeg -loglevel error -hide_banner -nostats -i \"{input_video}\" -i \"{input_audio}\" -i \"{input_subtitles}\".en.vtt -map 0:v -map 1:a -map 2:s -c:v copy -c:a copy -c:s mov_text -metadata:s:s:0 language=eng \"{merged_video}\"")
			os.remove(input_subtitles + ".en.vtt")
		else:
			os.system(f"ffmpeg -loglevel error -hide_banner -nostats -i \"{input_video}\" -i \"{input_audio}\" -i \"{input_subtitles}\".ar.vtt -map 0:v -map 1:a -map 2:s -c:v copy -c:a copy -c:s mov_text -metadata:s:s:0 language=ara \"{merged_video}\"")
			os.remove(input_subtitles + ".ar.vtt")
	else:
		os.system(f"ffmpeg -loglevel error -hide_banner -nostats -i \"{input_video}\" -i \"{input_audio}\" -c copy \"{merged_video}\"")
	
	os.remove(input_video)
	os.remove(input_audio)


if __name__ == "__main__":
	directory    = input("Enter the the video path: ")
	filename  	 = input("\nEnter the filename: ")

	input_video  = directory + "\\" + filename + ' (Video).mp4'
	input_audio  = directory + "\\" + filename + ' (Audio).mp4'
	merged_video = directory + "\\" + filename + ' (Merged).mp4'
	input_subtitles = directory + "\\" + filename
	os.system(f"ffmpeg -loglevel error -hide_banner -nostats -i \"{input_video}\" -i \"{input_audio}\" -i \"{input_subtitles}\".en.vtt -i \"{input_subtitles}\".ar.vtt -map 0:v -map 1:a -map 2:s -map 3:s -c:v copy -c:a copy -c:s:0 mov_text -c:s:1 mov_text -metadata:s:s:0 language=eng -metadata:s:s:1 language=ara \"{merged_video}\"")


## Useful Linls
# -loglevel warning -hide_banner -stats To show progress
	# Source: https://superuser.com/questions/326629/how-can-i-make-ffmpeg-be-quieter-less-verbose
# Merge subtitles:
	# https://gist.github.com/berndverst/8e1b8321926426ded9555c15a2c0c837
	# https://stackoverflow.com/questions/8672809/use-ffmpeg-to-add-text-subtitles
	# https://superuser.com/questions/549179/using-ffmpeg-to-add-subtitles-to-a-m4v-video-file
