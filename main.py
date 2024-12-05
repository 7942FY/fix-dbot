import os
import discord
import yt_dlp as youtube_dl
from discord.ext import commands

from serverii import server_on


# ตั้งค่าบอท
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ตัวแปรสำหรับระบบ Loop เพลง
loop_song = False
current_song_url = None

# ตรวจสอบว่า Bot ออนไลน์แล้ว
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

# คำสั่งสำหรับแนะนำตัว
@bot.command()
async def infoper(ctx):
    await ctx.send("สวัสดีน้าาา เราชื่อว่า เปอร์(Per) เราเป็นบอทที่ถูกสร้างขึ้น เราเป็นคนน่ารักขี้เหงาเราอยากให้พวกเธออยู่กับเราบ่อยๆนะ <3")

@bot.command()
async def order(ctx):
    await ctx.send(" !infoper !join !leave !play !loop !style !รักนะ ")

@bot.command()
async def style(ctx):
    await ctx.send("เราเป็นคนชิลๆ เราชอบนอนเป็นชีวิตจิตใจเราชอบของน่ารักที่สุดในโลกเลย")

@bot.command()
async def รักนะ(ctx):
    await ctx.send("เค้าเขินน้าาาา ")

# คำสั่งสำหรับเข้าช่องเสียง
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        try:
            await channel.connect()
            await ctx.send("เค้าเข้ามาแล้วน้าาา")
        except discord.errors.ClientException as e:
            await ctx.send(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
    else:
        await ctx.send("คุณต้องอยู่ในช่องเสียงก่อน")


# คำสั่งสำหรับออกจากช่องเสียง
@bot.command()
async def leave(ctx):
    global loop_song
    if ctx.voice_client:
        loop_song = False  # ปิดโหมด loop หากบอทออกจากห้อง
        await ctx.voice_client.disconnect()
        await ctx.send("ทิ้งเค้าแล้วหรอ T^T")
    else:
        await ctx.send("เค้าไม่ได้อยู่ในห้องแล้ว")

# คำสั่งสำหรับเล่นเพลงจากลิงก์
@bot.command()
async def play(ctx, url: str):
    global current_song_url
    if not ctx.voice_client:
        await ctx.send("คุณต้องอยู่ในห้องก่อนแล้วใช้คำสั่ง !join ")
        return

    current_song_url = url  # เก็บ URL เพลงปัจจุบันไว้สำหรับระบบ loop

    # ตั้งค่าการดาวน์โหลดเสียง
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['url']

        # เล่นเพลง
        ctx.voice_client.stop()
        ctx.voice_client.play(discord.FFmpegPCMAudio(url2), after=lambda e: check_loop(ctx))
        await ctx.send(f"Now playing: {info['title']}")
    except Exception as e:
        await ctx.send(f"เกิดข้อผิดพลาด: {e}")

# ฟังก์ชันสำหรับตรวจสอบว่าเปิดโหมด Loop อยู่หรือไม่
def check_loop(ctx):
    global loop_song, current_song_url
    if loop_song and current_song_url:
        ctx.voice_client.stop()  # หยุดการเล่นเพลงปัจจุบัน
        ctx.bot.loop.create_task(play(ctx, current_song_url))  # เล่นเพลงเดิมซ้ำ

# คำสั่งเปิด/ปิดโหมด Loop
@bot.command()
async def loop(ctx):
    global loop_song
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        await ctx.send("ไม่มีเพลงกำลังเล่นอยู่ เค้าเปิด Loop ไม่ได้นะ T^T")
        return

    loop_song = not loop_song  # สลับสถานะเปิด/ปิด
    if loop_song:
        await ctx.send("🔁 เปิดโหมด Loop เพลง!")
    else:
        await ctx.send("⏹️ ปิดโหมด Loop เพลงแล้ว!")

# รันบอท
server_on()
bot.run(os.getenv('TOKEN'))
