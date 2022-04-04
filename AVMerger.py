import ffmpeg

def avmerger(directory, filename):
	input_video = ffmpeg.input(directory + "\\" + filename + ' (Video).mp4')
	input_audio = ffmpeg.input(directory + "\\" + filename + ' (Audio).mp4')
	
	ffmpeg.concat(input_video, input_audio, v=1, a=1).output(directory  + "\\" + filename + ' (Merged).mp4').run()

if __name__ == "__main__":
	directory = input("Enter the the video path: ")
	filename  = input("\nEnter the filename: ")
	
	input_video = ffmpeg.input(directory + "\\" + filename + '.mp4')
	input_audio = ffmpeg.input(directory + "\\" + filename + ' (Audio).mp4')

	ffmpeg.concat(input_video, input_audio, v=1, a=1).output(directory  + "\\" + filename + ' (Merged).mp4').run()
