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

text = "한국은 다른 나라가 못해낸 걸 해냈어! 미국 여성 버스기사들이 버스를 타러 한국에 왔다가 충격을 받은 진짜 이유,제작비의 가장 큰 몫을 차지하는 것은 배우 출연료다. 업계 관계자들은 유명 톱 배우들은 이제 출연료 회당 10억원 소리를 하는 게 현실이 됐다고 실태를 전했다. 주연급 배우 회당 출연료 3억~4억원은 기본이 됐다는게 업계 관계자의 설명이다. 드라마 흥행에도 불구하고 높아진 제작비로 인한 수익을 내기 갈수록 힘들어지고 있다.최근 드라마 시장은 “아무리 싸게 찍어도 회당 10억원은 넘어야 한다”는 말이 나올 정도다. 그것도 회당 몇억원의 출연료를 줘야 하는 톱 배우 없이 만들었을 때 가능한 얘기다."
output_file = "voice.mp3"
asyncio.run(text_to_speech(text, selected_voice['ShortName'], output_file))
