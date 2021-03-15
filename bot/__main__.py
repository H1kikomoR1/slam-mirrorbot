import shutil, psutil
import signal
import pickle
from pyrogram import idle
from bot import app
from os import execl, kill, path, remove
from sys import executable
import time
from telegram import ParseMode
from telegram.ext import CommandHandler, run_async
from bot import dispatcher, updater, botStartTime
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, shell, eval, anime, stickers, search, delete, speedtest, usage


@run_async
def stats(update, context):
    currentTime = get_readable_time((time.time() - botStartTime))
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    stats = f'<b>Bot Uptime:</b> {currentTime}\n' \
            f'<b>Total disk space:</b> {total}\n' \
            f'<b>Used:</b> {used}  ' \
            f'<b>Free:</b> {free}\n\n' \
            f'📊Data Usage📊\n<b>Upload:</b> {sent}\n' \
            f'<b>Down:</b> {recv}\n\n' \
            f'<b>CPU:</b> {cpuUsage}%\n' \
            f'<b>RAM:</b> {memory}%\n' \
            f'<b>Disk:</b> {disk}%'
    sendMessage(stats, context.bot, update)


@run_async
def start(update, context):
    start_string = f'''
Hi, I'm Neko, a multipurpose bot for [#USERNEKOPOI](https://t.me/November2k)
Type /{BotCommands.HelpCommand} to get a list of available commands
'''
    update.effective_message.reply_photo("https://telegra.ph/file/4388e0e0cedcae0d6a96f.jpg", start_string, parse_mode=ParseMode.MARKDOWN)


@run_async
def restart(update, context):
    restart_message = sendMessage("Restarting, Please wait!", context.bot, update)
    # Save restart message object in order to reply to it after restarting
    fs_utils.clean_all()
    with open('restart.pickle', 'wb') as status:
        pickle.dump(restart_message, status)
    execl(executable, executable, "-m", "bot")


@run_async
def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


@run_async
def log(update, context):
    sendLogFile(context.bot, update)


@run_async
def bot_help(update, context):
    help_string = f'''
/{BotCommands.HelpCommand}: Untuk mendapatkan pesan ini 

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Mulai mirror tautan ke Google Drive 

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Mulai mirror dan jika file yang diunduh adalah arsip apa pun, ekstrak ke drive Google 

/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Mulai mirror dan unggah versi unduhan yang diarsipkan (.tar) 

/{BotCommands.CloneCommand}: Copy file/folder ke google drive

/{BotCommands.WatchCommand} [youtube-dl supported link]: Mirror melalui youtube-dl. tekan /{BotCommands.WatchCommand} untuk bantuan.

/{BotCommands.TarWatchCommand} [youtube-dl supported link]: Mirror melalui youtube-dl dan tar sebelum upload

/{BotCommands.CancelMirror}: Balas pesan yang digunakan untuk mengunduh dan unduhan itu akan dibatalkan 

/{BotCommands.StatusCommand}: Melihat status dari semua unduhan 

/{BotCommands.ListCommand} [search term]: Mencari list dri Google drive, jika ditemukan akan dibalas dengan tautan 

/{BotCommands.StatsCommand}: ampilkan Statistik mesin tempat bot dihosting 

/{BotCommands.AuthorizeCommand}: Otorisasi obrolan atau pengguna untuk menggunakan bot (Hanya dapat dieksekusi oleh #USERNEKOPOI) 

/{BotCommands.LogCommand}: Dapatkan file log dari bot. Berguna untuk mendapatkan laporan kerusakan bot atau crash

/{BotCommands.SpeedCommand}: Periksa Kecepatan Internet

/{BotCommands.UsageCommand}: Untuk melihat Heroku Dyno Stats ( hanya #USERNEKOPOI yang bisa menggunakan ini ) 

/tshelp: Dapatkan bantuan untuk modul pencarian torrent. 

/weebhelp: Dapatkan bantuan untuk modul anime, manga, dan karakter. 

/stickerhelp: Dapatkan bantuan untuk modul stiker. 
'''
    sendMessage(help_string, context.bot, update)


def main():
    fs_utils.start_cleanup()
    # Check if the bot is restarting
    if path.exists('restart.pickle'):
        with open('restart.pickle', 'rb') as status:
            restart_message = pickle.load(status)
        restart_message.edit_text("Restarted Successfully!")
        remove('restart.pickle')

    start_handler = CommandHandler(BotCommands.StartCommand, start,
                                   filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling()
    LOGGER.info("Bot Started!")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)

app.start()
main()
idle()
