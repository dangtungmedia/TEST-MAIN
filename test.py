import edge_tts
import asyncio

async def list_voices():
    voices_manager = await edge_tts.VoicesManager.create()
    voices = voices_manager.voices
    for voice in voices:
        print(f"Name: {voice['Name']}, Gender: {voice['Gender']}, Locale: {voice['Locale']}")
    return voices

voices = asyncio.run(list_voices())

import edge_tts
import asyncio

async def text_to_speech(text, voice, output_file):
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(output_file)

# Giả sử bạn muốn sử dụng giọng 'kn-IN-SapnaNeural'
selected_voice = next(voice for voice in voices if voice['Name'] == "Microsoft Server Speech Text to Speech Voice (kn-IN, SapnaNeural)")

text = "Hello, how are you?"
output_file = "output_kn.mp3"

asyncio.run(text_to_speech(text, selected_voice['ShortName'], output_file))
