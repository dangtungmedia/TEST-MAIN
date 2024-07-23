import subprocess

def merge_audio_video(video_path, audio_path, output_path):
    """
    Merges an audio file into a video file using FFmpeg.

    Parameters:
    video_path (str): The path to the input video file.
    audio_path (str): The path to the input audio file.
    output_path (str): The path to the output video file.
    """
    ffmpeg_command = [
        'ffmpeg',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-strict', 'experimental',
        '-shortest',
        '-y',
        output_path
    ]

    try:
        process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        print("FFmpeg stdout:\n", stdout.decode())
        print("FFmpeg stderr:\n", stderr.decode())

        if process.returncode != 0:
            raise Exception("FFmpeg command failed with return code {}".format(process.returncode))
        else:
            print(f"Successfully merged audio and video into {output_path}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
video_path = "media/234/PQKOBYZ98Q.mp4"
audio_path = "media/234/audio.wav"
output_path = "media/234/final_video.mp4"

merge_audio_video(video_path, audio_path, output_path)
