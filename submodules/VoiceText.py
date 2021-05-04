from datetime import datetime, timedelta
import requests
from voicetext import VoiceText, VoiceTextException
import pyvcroid2

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

    def to_voiceroid_wave(self, text, guildid):
        url = f'http://127.0.0.1:8080/api/speechtext/' + text
        response = requests.get(url)
        saveFileName = "./" + datetime.now().strftime(f"%Y%m%d_%H%M%S_{guildid}") + ".wav"
        with open(saveFileName, 'wb') as saveFile:
            saveFile.write(response.content)

        return saveFileName

    async def new_to_voiceroid_wave(self, text, guildid, voicetype, filename):
        install_path = "C:\Program Files (x86)\AHS\VOICEROID2"
        with pyvcroid2.VcRoid2(install_path=install_path, install_path_x86=install_path) as vc:
            lang_list = vc.listLanguages()
            if "standard" in lang_list:
                vc.loadLanguage("standard")
            else:
                raise Exception("No language library")
            voice_list = vc.listVoices()
            if voicetype in voice_list:
                vc.loadVoice(voicetype)
            elif 0 < len(voice_list):
                vc.loadVoice(voice_list[0])
            else:
                raise Exception("No voice library")
            vc.param.volume = 1.0
            vc.param.speed = 1.0
            vc.param.pitch = 1.0
            vc.param.emphasis = 1.0
            vc.param.pauseMiddle = 80
            vc.param.pauseLong = 100
            vc.param.pauseSentence = 200
            vc.param.masterVolume = 1.0

            speech, tts_events = vc.textToSpeech(text)
            with open(filename, mode="wb") as f:
                f.write(speech)