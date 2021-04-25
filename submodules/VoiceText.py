from datetime import datetime, timedelta
from voicetext import VoiceText, VoiceTextException

class vt_func:
    VT_APIKEY = "3io9bd31euk2cekx"

    def to_wave(text, speaker, emotion, speed, pitch, volume, guildid):
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{guildid}.wav"
        vt = VoiceText(vt_func.VT_APIKEY).speaker(speaker)
        if speed:
            vt.speed(int(speed))
        if emotion:
            vt.emotion(emotion)
        if pitch:
            vt.pitch(int(pitch))
        if volume:
            vt.volume(int(volume))
    
        with open(f"./{filename}", 'wb') as f:
            f.write(vt.to_wave(text))

        return f"./{filename}"