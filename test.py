import edge_tts
import asyncio

async def list_voices():
    voices_manager = await edge_tts.VoicesManager.create()
    voices = voices_manager.voices
    return voices

voices = asyncio.run(list_voices())
async def text_to_speech(text, voice, output_file):
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(output_file)

# Giả sử bạn muốn sử dụng giọng 'kn-IN-SapnaNeural'
selected_voice = next(voice for voice in voices if voice['ShortName'] == "ko-KR-HyunsuNeural")

text = "한국은 다른 나라가 못해낸 걸 해냈어! 미국 여성 버스기사들이 버스를 타러 한국에 왔다가 충격을 받은 진짜 이유"
output_file = "output_kn.mp3"
asyncio.run(text_to_speech(text, selected_voice['ShortName'], output_file))
