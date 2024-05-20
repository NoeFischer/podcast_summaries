from pydub import AudioSegment

audio_folder = "../data/audio/"
file_name = "the_gradient_240502"

podcast = AudioSegment.from_file(f"{audio_folder}{file_name}.mp3", "mp3")

# Split the podcast into 10-minute segments
podcast_length = len(podcast)
segment_length = 10 * 60 * 1000

for i in range(0, podcast_length, segment_length):
    segment = podcast[i : i + segment_length]
    segment.export(
        f"../data/audio/audio_segments/{file_name}/segment_{i // segment_length}.mp3",
        format="mp3",
    )
