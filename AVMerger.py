import os

def avmerger(directory, filename):
	input_video  = directory + "\\" + filename + ' (Video).mp4'
	input_audio  = directory + "\\" + filename + ' (Audio).mp4'
	merged_video = directory + "\\" + filename + ' (Merged).mp4'

	os.system(f"ffmpeg -loglevel error -hide_banner -nostats -i \"{input_video}\" -i \"{input_audio}\" -c copy \"{merged_video}\"")


if __name__ == "__main__":
	directory    = input("Enter the the video path: ")
	filename  	 = input("\nEnter the filename: ")

	input_video  = directory + "\\" + filename + ' (Video).mp4'
	input_audio  = directory + "\\" + filename + ' (Audio).mp4'
	merged_video = directory + "\\" + filename + ' (Merged).mp4'

	os.system(f"ffmpeg -loglevel error -hide_banner -nostats -i \"{input_video}\" -i \"{input_audio}\" -c copy \"{merged_video}\"")
