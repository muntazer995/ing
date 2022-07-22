# © SUPERIOR_BOTS
import io
from os import path
from typing import Callable
from asyncio.queues import QueueEmpty
import os
import random
import re
from random import choice
import aiofiles
import aiohttp
from Zaid.converter import convert
import ffmpeg
import requests
from Zaid.fonts import CHAT_TITLE
from PIL import Image, ImageDraw, ImageFont
from config import ASSISTANT_NAME, BOT_USERNAME, IMG_1, IMG_2, IMG_5, UPDATES_CHANNEL, GROUP_SUPPORT
from Zaid.filters import command, other_filters
from Zaid.queues import QUEUE, add_to_queue
from Zaid.main import call_py, Test as user
from Zaid.utils import bash
from Zaid.main import bot as Client
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped
from youtubesearchpython import VideosSearch
import yt_dlp
import yt_dlp

ZAID_IMGS = [
    "Process/ImageFont/LightGreen.png",
    "Process/ImageFont/Red.png",
    "Process/ImageFont/Black.png",
    "Process/ImageFont/Blue.png",
    "Process/ImageFont/Grey.png",
    "Process/ImageFont/Green.png",
    "Process/ImageFont/Lightblue.png",
    "Process/ImageFont/Lightred.png",
    "Process/ImageFont/Purple.png",
    "Process/ImageFont/foreground.png",
]

def ytsearch(query: str):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = data["thumbnails"][0]["url"]
        return [songname, url, duration, thumbnail]
    except Exception as e:
        print(e)
        return 0


async def ytdl(format: str, link: str):
    stdout, stderr = await bash(f'yt-dlp --geo-bypass -g -f "[height<=?720][width<=?1280]" {link}')
    if stdout:
        return 1, stdout
    return 0, stderr

chat_id = None
DISABLED_GROUPS = []
useer = "NaN"
ACTV_CALLS = []




def transcode(filename):
    ffmpeg.input(filename).output(
        "input.raw", 
        format="s16le", 
        acodec="pcm_s16le", 
        ac=2, 
        ar="48k"
    ).overwrite_output().run()
    os.remove(filename)

def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)

def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))



def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


async def generate_cover(thumbnail, title, userid, ctitle):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open(f"thumb{userid}.png", mode="wb")
                await f.write(await resp.read())
                await f.close()
    image1 = Image.open(f"thumb{userid}.png")
    images = choice(ZAID_IMGS)
    image2 = Image.open(images)
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save(f"temp{userid}.png")
    img = Image.open(f"temp{userid}.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Process/ImageFont/finalfont.ttf", 60)
    font2 = ImageFont.truetype("Process/ImageFont/finalfont.ttf", 70)     
    draw.text((20, 45), f"{title[:30]}...", fill= "white", stroke_width = 1, stroke_fill="white", font=font2)
    draw.text((120, 595), f"PlAYING ON: {ctitle[:20]}...", fill="white", stroke_width = 1, stroke_fill="white" ,font=font)
    img.save(f"final{userid}.png")
    os.remove(f"temp{userid}.png")
    os.remove(f"thumb{userid}.png") 
    final = f"final{userid}.png"
    return final



    
@Client.on_message(command(["تشغيل" ."شغل", "/play"]) & other_filters)
async def play(c: Client, m: Message):
    await m.delete()
    replied = m.reply_to_message
    chat_id = m.chat.id
    keyboard = InlineKeyboardMarkup(
                  [[
                      InlineKeyboardButton("⏹️", callback_data="cbstop"),
                      InlineKeyboardButton("⏸️", callback_data="cbpause"),
                      InlineKeyboardButton("⏭️", "skip"),
                      InlineKeyboardButton("🔼", callback_data="cbresume"),
                  ],[
                      InlineKeyboardButton(text="🥇 المطور ", url=f"https://t.me/{UPDATES_CHANNEL}"),
                  ],[
                      InlineKeyboardButton("مسح.", callback_data="close")],
                  ]
             )
    if m.sender_chat:
        return await m.reply_text("you're an __Anonymous__ Admin !\n\n» revert back to user account from admin rights.")
    try:
        aing = await c.get_me()
    except Exception as e:
        return await m.reply_text(f"error:\n\n{e}")
    a = await c.get_chat_member(chat_id, aing.id)
    if a.status != "administrator":
        await m.reply_text(
            f"❤️‍🔥 لاستخدام البوت, ارفعني كمشرف اولا **في مجموعتك** بعد ذالك اعطني الصلاحيات **التالية**:\n\n» 🤼 __حذف رسائل__\n» 🤼 __اضافة مستخدمين__\n» 🤼 __ادارة دردشة الفيديو__\n\nسيتم تحديث **البيانات تلقائيا**"
        )
        return
    if not a.can_manage_voice_chats:
        await m.reply_text(
            "شلون اشغل واني معندي صلاحية :" + "\n\n» ❤️‍🔥 __دردشة الفيديو__"
        )
        return
    if not a.can_delete_messages:
        await m.reply_text(
            "شلون اشغل واني معندي صلاحية:" + "\n\n» ❤️‍🔥 __حذف رسائل__"
        )
        return
    if not a.can_invite_users:
        await m.reply_text("شلون اشغل واني معندي صلاحية:" + "\n\n» ❤️‍🔥 __اضافة مستخدمين__")
        return
    try:
        ubot = (await user.get_me()).id
        b = await c.get_chat_member(chat_id, ubot)
        if b.status == "kicked":
            await m.reply_text(
                f"@{ASSISTANT_NAME} **حساب المساعد محظور من المجموعة** {m.chat.title}\n\n» **جرب الغاء حظر المساعد من الاعدادات واكتب .انضم.**"
            )
            return
    except UserNotParticipant:
        if m.chat.username:
            try:
                await user.join_chat(m.chat.username)
            except Exception as e:
                await m.reply_text(f"❤️‍🔥 **فشل حساب المساعد في الانضمام**\n\n**السبب**: `{e}`")
                return
        else:
            try:
                invitelink = await c.export_chat_invite_link(
                    m.chat.id
                )
                if invitelink.startswith("https://t.me/+"):
                    invitelink = invitelink.replace(
                        "https://t.me/+", "https://t.me/joinchat/"
                    )
                await user.join_chat(invitelink)
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                return await m.reply_text(
                    f"❤️‍🔥 **فشل حساب المساعد في الانضمام **\n\n**السبب**: `{e}`"
                )
    if replied:
        if replied.audio or replied.voice:
            suhu = await replied.reply("📥 **تحميل الصوت...**")
            dl = await replied.download()
            link = replied.link
            if replied.audio:
                if replied.audio.title:
                    songname = replied.audio.title[:70]
                else:
                    if replied.audio.file_name:
                        songname = replied.audio.file_name[:70]
                    else:
                        songname = "Audio"
            elif replied.voice:
                songname = "Voice Note"
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                await suhu.delete()
                await m.reply_photo(
                    photo=f"{IMG_1}",
                    caption=f"❤️‍🔥 → **أبشر يخوي حشغلها بعد هاذي »** `{pos}`\n\n❤️‍🔥 → **الاسم:** [{songname}]({link}) | `الاغنية`\n❤️‍🔥 → **الدردشة:** `{chat_id}`\n❤️‍🔥 → **طلب الحلو:** {m.from_user.mention()}",
                    reply_markup=keyboard,
                )
            else:
             try:
                await call_py.join_group_call(
                    chat_id,
                    AudioPiped(
                        dl,
                    ),
                    stream_type=StreamType().local_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                await suhu.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_photo(
                    photo=f"{IMG_2}",
                    caption=f"❤️‍🔥 → **الاسم:** [{songname}]({link})\n❤️‍🔥 → **الدردشة:** `{chat_id}`\n❤️‍🔥 → **طلب الحلو:** {requester}\n❤️‍🔥 → **نوع التشغيل:** `اغنية`",
                    reply_markup=keyboard,
                )
             except Exception as e:
                await suhu.delete()
                await m.reply_text(f"🚫 error:\n\n» {e}")
        
    else:
        if len(m.command) < 2:
         await m.reply_photo(
                     photo=f"{IMG_5}",
                    caption="❤️‍🩹**اكتب .شغل او تشغيل بالرد على ملف صوتي او اعطاء شي للبحث**"
                    ,
                      reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(" مسح", callback_data="cls")
                        ]
                    ]
                )
            )
        else:
            suhu = await m.reply_text(
        f"**❤️‍🔥 جَاެࢪي اެݪبَحثَ..."
    )
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            if search == 0:
                await suhu.edit("🤼 **لم يتم العثور على نتائج.**")
            else:
                songname = search[0]
                title = search[0]
                url = search[1]
                duration = search[2]
                thumbnail = search[3]
                userid = m.from_user.id
                gcname = m.chat.title
                ctitle = await CHAT_TITLE(gcname)
                image = await generate_cover(thumbnail, title, userid, ctitle)
                format = "bestaudio"
                abhi, ytlink = await ytdl(format, url)
                if abhi == 0:
                    await suhu.edit(f"💬 yt-dl issues detected\n\n» `{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                        await suhu.delete()
                        requester = (
                            f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        )
                        await m.reply_photo(
                            photo=image,
                            caption=f"👍🏻🔥 **أبشر عيني راح اشغلها بعد هاي »** `{pos}`\n\n❤️‍🔥→  **الاسم:** [{songname[:22]}]({url}) | `الاغنية`\n**❤️‍🔥 → المدة:** `{duration}`\n❤️‍🔥 → **طلب من الحب مالي:** {requester}",
                            reply_markup=keyboard,
                        )
                    else:
                        try:
                            await suhu.edit(
                            f"❤️‍🔥 يَتمَ اެݪتشغِيݪ اެلانِ"
                        )
                            await call_py.join_group_call(
                                chat_id,
                                AudioPiped(
                                    ytlink,
                                ),
                                stream_type=StreamType().local_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                            await suhu.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_photo(
                                photo=image,
                                caption=f"❤️‍🔥 **→ الاسم :** [{songname[:22]}]({url})\n**❤️‍🔥 → المدة:** `{duration}`\n❤️‍🔥 →** طلب من الگي:** {requester}",
                                reply_markup=keyboard,
                            )
                        except Exception as ep:
                            await suhu.delete()
                            await m.reply_text(f"💬 error: `{ep}`")
