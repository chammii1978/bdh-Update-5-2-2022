import shutil, psutil
import signal
import os
import asyncio
import time
import subprocess

from pyrogram import idle
from sys import executable
from telegram import ParseMode, InlineKeyboardMarkup
from telegram.ext import CommandHandler

from wserver import start_server_async
from bot import bot, app, dispatcher, updater, botStartTime, IGNORE_PENDING_REQUESTS, IS_VPS, PORT, alive, web, nox, OWNER_ID, AUTHORIZED_CHATS, LOGGER
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import sendMessage, sendMarkup, editMessage, sendLogFile
from .helper.ext_utils.telegraph_helper import telegraph
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper import button_build
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, shell, eval, delete, speedtest, count, leech_settings, search


def stats(update, context):
    currentTime = get_readable_time(time.time() - botStartTime)
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    disk = psutil.disk_usage('/').percent
    p_core = psutil.cpu_count(logical=False)
    t_core = psutil.cpu_count(logical=True)
    swap = psutil.swap_memory()
    swap_p = swap.percent
    swap_t = get_readable_file_size(swap.total)
    swap_u = get_readable_file_size(swap.used)
    memory = psutil.virtual_memory()
    mem_p = memory.percent
    mem_t = get_readable_file_size(memory.total)
    mem_a = get_readable_file_size(memory.available)
    mem_u = get_readable_file_size(memory.used)
    stats = f'<b>⏲️ আপটাইম:  {currentTime}</b>\n' \
            f'<b>📀 টোটাল ডিস্কস্পেস:  {total}</b>\n' \
            f'<b>🌡️ব্যবহৃত স্পেস:  {used}</b>\n' \
            f'<b>🔥 ফ্রী স্পেস :  {free}</b>\n\n' \
            f'📊 টোটাল ব্যবহৃত ব্যান্ডউইথ 📊\n<b>📤 আপলোড:  {sent}</b>\n' \
            f'<b>📥 ডাউনলোড:  {recv}</b>\n\n' \
            f'<b>🖥️ সিপিউ লোড:  {cpuUsage}</b>%\n' \
            f'<b>💾 র‍্যাম:  {mem_p}%</b>\n' \
            f'<b>💿 ডিস্ক:  {disk}%</b>\n' \
            f'<b>🔸ফিজিক্যাল কোর:</b> {p_core} টি\n'\
            f'<b>🔸মোট কোর:</b> {t_core} টি\n\n'\
            f'<b>⚠ Total SWAP:</b> {swap_t} \n<b>🌡️ব্যবহৃত SWAP:</b> {swap_p}%\n'\
            f'<b>💾 টোটাল মেমোরি:</b> {mem_t}\n'\
            f'<b>🔥 ফ্রী মেমোরি:</b> {mem_a}\n'\
            f'<b>🌡️ ব্যবহৃত মেমোরি:</b> {mem_u}\n'\
            f'<b>✍️ অনুবাদকঃ "এলেক্স স্টুয়ার্ট ©️" \n🙏 সম্পাদনায়ঃ "🇧🇩বাংলাদেশ হোর্ডিং🇧🇩" \n@BangladeshHoarding</b>'
    sendMessage(stats, context.bot, update)

def start(update, context):
    buttons = button_build.ButtonMaker()
    buttons.buildbutton("Admin", "https://t.me/BDH_PM_bot")
    buttons.buildbutton("Channel", "https://t.me/bangladeshhoarding")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        start_string = f'''
এই বট সকল ডিরেক্ট লিঙ্ক/ টরেন্ট গুগল ড্রাইভে আপলোড করে থাকে!
সকল কমান্ড দেখতে /{BotCommands.HelpCommand} কমান্ড ব্যবহার করুন
'''
        sendMarkup(start_string, context.bot, update, reply_markup)
    else:
        sendMarkup('Not Authorized user', context.bot, update, reply_markup)

def restart(update, context):
    restart_message = sendMessage("♻️ রি-বুট করা হচ্ছে, অপেক্ষা করুন 🙏 ", context.bot, update)
    fs_utils.clean_all()
    alive.kill()
    process = psutil.Process(web.pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()
    nox.kill()
    subprocess.run(["python3", "update.py"])
    # Save restart message object in order to reply to it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    os.execl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update)


help_string_telegraph = f'''<br>
<b>এখানে বট এর সকল কমান্ড ও তাদের ব্যবহারের নিয়ম দেওয়া আছে, ভালোভাবে দেখে নিন... অথবা গ্রুপের মেম্বারগন যেভাবে ব্যবহার করছে তা অনুসরন করুন</b>
<br><br>
<b>/{BotCommands.HelpCommand}</b>: To get this message
<br><br>
<b>/{BotCommands.MirrorCommand}</b> [download_url][magnet_link]: Start mirroring the link to Google Drive.
<br><br>
<b>/{BotCommands.ZipMirrorCommand}</b> [download_url][magnet_link]: Start mirroring and upload the archived (.zip) version of the download
<br><br>
<b>/{BotCommands.UnzipMirrorCommand}</b> [download_url][magnet_link]: Start mirroring and if downloaded file is any archive, extracts it to Google Drive
<br><br>
<b>/{BotCommands.QbMirrorCommand}</b> [magnet_link]: Start Mirroring using qBittorrent, Use <b>/{BotCommands.QbMirrorCommand} s</b> to select files before downloading
<br><br>
<b>/{BotCommands.QbZipMirrorCommand}</b> [magnet_link]: Start mirroring using qBittorrent and upload the archived (.zip) version of the download
<br><br>
<b>/{BotCommands.QbUnzipMirrorCommand}</b> [magnet_link]: Start mirroring using qBittorrent and if downloaded file is any archive, extracts it to Google Drive
<br><br>
<b>/{BotCommands.LeechCommand}</b> [download_url][magnet_link]: Start leeching to Telegram, Use <b>/{BotCommands.LeechCommand} s</b> to select files before leeching
<br><br>
<b>/{BotCommands.ZipLeechCommand}</b> [download_url][magnet_link]: Start leeching to Telegram and upload it as (.zip)
<br><br>
<b>/{BotCommands.UnzipLeechCommand}</b> [download_url][magnet_link]: Start leeching to Telegram and if downloaded file is any archive, extracts it to Telegram
<br><br>
<b>/{BotCommands.QbLeechCommand}</b> [magnet_link]: Start leeching to Telegram using qBittorrent, Use <b>/{BotCommands.QbLeechCommand} s</b> to select files before leeching
<br><br>
<b>/{BotCommands.QbZipLeechCommand}</b> [magnet_link]: Start leeching to Telegram using qBittorrent and upload it as (.zip)
<br><br>
<b>/{BotCommands.QbUnzipLeechCommand}</b> [magnet_link]: Start leeching to Telegram using qBittorrent and if downloaded file is any archive, extracts it to Telegram
<br><br>
<b>/{BotCommands.CloneCommand}</b> [drive_url]: Copy file/folder to Google Drive
<br><br>
<b>/{BotCommands.CountCommand}</b> [drive_url]: Count file/folder of Google Drive Links
<br><br>
<b>/{BotCommands.DeleteCommand}</b> [drive_url]: Delete file from Google Drive (Only Owner & Sudo)
<br><br>
<b>/{BotCommands.WatchCommand}</b> [youtube-dl supported link]: Mirror through youtube-dl. Click <b>/{BotCommands.WatchCommand}</b> for more help
<br><br>
<b>/{BotCommands.ZipWatchCommand}</b> [youtube-dl supported link]: Mirror through youtube-dl and zip before uploading
<br><br>
<b>/{BotCommands.LeechWatchCommand}</b> [youtube-dl supported link]: Leech through youtube-dl
<br><br>
<b>/{BotCommands.LeechZipWatchCommand}</b> [youtube-dl supported link]: Leech through youtube-dl and zip before uploading
<br><br>
<b>/{BotCommands.LeechSetCommand}</b>: Leech Settings
<br><br>
<b>/{BotCommands.SetThumbCommand}</b>: Reply photo to set it as Thumbnail
<br><br>
<b>/{BotCommands.CancelMirror}</b>: Reply to the message by which the download was initiated and that download will be cancelled
<br><br>
<b>/{BotCommands.CancelAllCommand}</b>: Cancel all running tasks
<br><br>
<b>/{BotCommands.ListCommand}</b> [query]: Search in Google Drive
<br><br>
<b>/{BotCommands.SearchCommand}</b> [site](optional) [query]: Search for torrents with API
<br>sites: <code>rarbg, 1337x, yts, etzv, tgx, torlock, piratebay, nyaasi, ettv</code><br><br>
<b>/{BotCommands.StatusCommand}</b>: Shows a status of all the downloads
<br><br>
<b>/{BotCommands.StatsCommand}</b>: Show Stats of the machine the bot is hosted on
'''

help = telegraph.create_page(
        title='Bangladesh Hoarding',
        content=help_string_telegraph,
    )["path"]

help_string = f'''
🥺🙏 বট ব্যবহারের পূর্বে বট কমান্ড ও তাদের ব্যবহার ও কার্যাবলী জেনে নিন.. 🙏🥺

/{BotCommands.MirrorCommand} [download_url][magnet_link]: ফাইল ড্রাইভে মিরর করার জন্য এই কমান্ড ব্যবহার করুন।

/{BotCommands.ZipMirrorCommand} [download_url][magnet_link]: এই কমান্ড দিয়ে ডিরেক্ট লিংক/ গুগল ড্রাইভ ফোল্ডার জিপ (.zip) করা যাবে।

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: এই কমান্ড দিয়ে ডিরেক্ট ফাইল/ গুগল ড্রাইভ এর জিপ করা ফোল্ডার আনজিপ করা যাবে।

/{BotCommands.QbMirrorCommand} [magnet_link]: কিউ-বিটটরেন্ট দিয়ে ফাইল ড্রাইভে মিরর করার জন্য এবং  ডাউনলোড এর পূর্বে ফাইল সিলেক্ট করতে <b>/{BotCommands.QbMirrorCommand} s</b> কমান্ড ব্যাবহার করুন  

/{BotCommands.QbZipMirrorCommand} [magnet_link]: কিউ-বিটটরেন্ট দিয়ে ডাউনলোডকৃত ফাইল (.zip) করার জন্য এই কমান্ড ব্যবহার করুন।

/{BotCommands.QbUnzipMirrorCommand} [magnet_link]: কিউ-বিটটরেন্ট দিয়ে ডাউনলোডকৃত জিপ ফাইল আনজিপ করার জন্য এই কমান্ড ব্যবহার করুন।

/{BotCommands.CloneCommand} [drive_url]: গুগল ড্রাইভ এর ফাইল/ ফোল্ডার কপি করতে এই কমান্ড ব্যাবহার করুন ।

🥺🙏 নিচের লিঙ্ক থেকে সকল বট কমান্ড ও তাদের ব্যবহার ও কার্যাবলী জেনে নিন.. 🙏🥺
'''

def bot_help(update, context):
    button = button_build.ButtonMaker()
    button.buildbutton("⁉️ বট কমান্ড ও ব্যবহারবিধি ⁉️", f"https://telegra.ph/{help}")
    reply_markup = InlineKeyboardMarkup(button.build_menu(1))
    sendMarkup(help_string, context.bot, update, reply_markup)

'''
botcmds = [
        (f'{BotCommands.MirrorCommand}', 'Start Mirroring'),
        (f'{BotCommands.ZipMirrorCommand}','Start mirroring and upload as .zip'),
        (f'{BotCommands.UnzipMirrorCommand}','Extract files'),
        (f'{BotCommands.QbMirrorCommand}','Start Mirroring using qBittorrent'),
        (f'{BotCommands.QbZipMirrorCommand}','Start mirroring and upload as .zip using qb'),
        (f'{BotCommands.QbUnzipMirrorCommand}','Extract files using qBitorrent'),
        (f'{BotCommands.CloneCommand}','Copy file/folder to Drive'),
        (f'{BotCommands.CountCommand}','Count file/folder of Drive link'),
        (f'{BotCommands.DeleteCommand}','Delete file from Drive'),
        (f'{BotCommands.WatchCommand}','Mirror Youtube-dl support link'),
        (f'{BotCommands.ZipWatchCommand}','Mirror Youtube playlist link as .zip'),
        (f'{BotCommands.CancelMirror}','Cancel a task'),
        (f'{BotCommands.CancelAllCommand}','Cancel all tasks'),
        (f'{BotCommands.ListCommand}','Searches files in Drive'),
        (f'{BotCommands.StatusCommand}','Get Mirror Status message'),
        (f'{BotCommands.StatsCommand}','Bot Usage Stats'),
        (f'{BotCommands.PingCommand}','Ping the Bot'),
        (f'{BotCommands.RestartCommand}','Restart the bot [owner/sudo only]'),
        (f'{BotCommands.LogCommand}','Get the Bot Log [owner/sudo only]'),
        (f'{BotCommands.HelpCommand}','Get Detailed Help')
    ]
'''

def main():
    fs_utils.start_cleanup()
    if IS_VPS:
        asyncio.new_event_loop().run_until_complete(start_server_async(PORT))
    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("✅ রি-বুট সম্পূর্ন হয়েছে , এখন ব্যবহার করতে পারেন!", chat_id, msg_id)
        os.remove(".restartmsg")
    elif OWNER_ID:
        try:
            text = "<b>🆙🆙 ছোট্ট একটা রি-বুট দিয়ে চলে আসলাম,,,😁😁!</b>"
            bot.sendMessage(chat_id=OWNER_ID, text=text, parse_mode=ParseMode.HTML)
            if AUTHORIZED_CHATS:
                for i in AUTHORIZED_CHATS:
                    bot.sendMessage(chat_id=i, text=text, parse_mode=ParseMode.HTML)
        except Exception as e:
            LOGGER.warning(e)
    # bot.set_my_commands(botcmds)
    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Bot Started!")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)

app.start()
main()
idle()
