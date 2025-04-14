import discord
from discord.ext import commands
import edge_tts
import asyncio
import os
import uuid
from collections import deque

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='.', intents=intents)

VOICE = "vi-VN-HoaiMyNeural"
tts_queue = deque()
is_playing = False
vc = None

target_channel_id = 1361424037825220781  # 👈 Thay bằng ID của channel bạn muốn bot đọc tin

@bot.event
async def on_ready():
    print(f'✅ Bot đã đăng nhập thành: {bot.user.name}')

@bot.event
async def on_message(message):
    global is_playing, vc

    if message.author.bot:
        return

    # Chỉ đọc tin nhắn từ kênh cụ thể
    if message.channel.id != target_channel_id:
        return

    if not message.author.voice or not message.author.voice.channel:
        await message.channel.send("❌ Bạn cần vào voice channel trước.")
        return

    voice_channel = message.author.voice.channel
    tts_queue.append(message.content)

    if not vc or not vc.is_connected():
        vc = await voice_channel.connect()

    if not is_playing:
        is_playing = True
        await play_next()

    await bot.process_commands(message)

async def play_next():
    global is_playing, vc

    if tts_queue:
        message = tts_queue.popleft()
        filename = f"tts_{uuid.uuid4()}.mp3"

        try:
            communicate = edge_tts.Communicate(text=message, voice=VOICE)
            await communicate.save(filename)
        except Exception as e:
            print(f"❌ TTS lỗi: {e}")
            is_playing = False
            return

        def after_playing(error):
            if error:
                print(f"🔴 Error: {error}")
            fut = asyncio.run_coroutine_threadsafe(play_next(), bot.loop)
            try:
                fut.result()
            except Exception as e:
                print(f"🔴 Future Error: {e}")

        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=filename), after=after_playing)

        while vc.is_playing():
            await asyncio.sleep(1)

        os.remove(filename)
    else:
        is_playing = False

        # ⏳ Chờ 3 phút, nếu không có gì mới thì ngắt kết nối
        await asyncio.sleep(180)  # 180 giây = 3 phút

        if not tts_queue and vc and vc.is_connected():
            await vc.disconnect()
            print("👋 Bot đã rời khỏi voice channel do không hoạt động.")
            vc = None




# Thay bằng token bot của bạn
bot.run("MTM1MTMzMDU1NjQ0ODYwODM3Ng.GUALcN.tk2R0IKsQ3J-YiwS_1RSKG7JhOaZNs-eUGcYbo")
