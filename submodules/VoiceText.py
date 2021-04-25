from datetime import datetime, timedelta
from voicetext import VoiceText, VoiceTextException

class vt_func:
    def to_wave(text, speaker, emotion, emotionlevel, speed, pitch, volume, guildid, apikey):
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{guildid}.wav"
        vt = VoiceText(apikey).speaker(speaker)
        vt.emotion(emotion, int(emotionlevel))
        vt.speed(int(speed))
        vt.pitch(int(pitch))
        vt.volume(int(volume))

        with open(f"./{filename}", 'wb') as f:
            f.write(vt.to_wave(text))

        return f"./{filename}"