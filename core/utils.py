import os
import time
import tempfile
import subprocess

from core.config import OUTPUTS_DIR, FFMPEG_PATH, FFPROBE_PATH


def timestamp_file(prefix, ext):
    """Return a timestamped path inside OUTPUTS_DIR."""
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S_") + str(int(time.time() * 1000) % 1000)
    return os.path.join(OUTPUTS_DIR, f"{prefix}_{ts}.{ext}")


def to_wav(audio_path, sr=16000, channels=1):
    """
    Convert any audio file to a temp WAV at the given sample rate / channels.
    Returns (wav_path, is_tmp). Caller deletes wav_path if is_tmp is True.
    """
    ext = os.path.splitext(audio_path)[1].lower()
    if ext == ".wav":
        return audio_path, False

    from pydub import AudioSegment
    AudioSegment.converter = FFMPEG_PATH
    AudioSegment.ffprobe   = FFPROBE_PATH

    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_frame_rate(sr).set_channels(channels)

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    audio.export(tmp.name, format="wav")
    return tmp.name, True


def transcode_h264(video_path):
    """
    Re-encode any video to H.264 / yuv420p so OpenCV/ffmpeg can decode it
    everywhere (Colab can't decode AV1, which many phone/screen recordings use).
    Returns a new mp4 path.
    """
    out = timestamp_file("norm", "mp4")
    subprocess.run(
        [FFMPEG_PATH, "-y", "-i", video_path,
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
         "-c:a", "aac", out],
        check=True, capture_output=True, text=True,
    )
    return out


def audio_duration(audio_path):
    """Duration in seconds, or None on failure."""
    try:
        from pydub import AudioSegment
        AudioSegment.converter = FFMPEG_PATH
        AudioSegment.ffprobe   = FFPROBE_PATH
        return len(AudioSegment.from_file(audio_path)) / 1000.0
    except Exception:
        return None
