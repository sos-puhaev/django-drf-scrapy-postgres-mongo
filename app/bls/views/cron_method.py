from bls.views.admin.tpb import ListTpb
from bls.views.admin.eztv import ListEztv
from bls.views.admin.yts_torrent import YtsTorrent
from apscheduler.schedulers.background import BackgroundScheduler

def setting_timer_tpb():
    instance = ListTpb()
    cursor = instance.show_settings()
    return cursor[5]

def setting_timer_eztv():
    instance = ListEztv()
    cursor = instance.show_settings()
    return cursor[5]

def setting_timer_yts():
    instance = YtsTorrent()
    cursor = instance.show_settings()
    return cursor[5]

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(ListTpb().cron_tpb_start, 'interval', hours=int(setting_timer_tpb()))
    scheduler.add_job(ListEztv().cron_eztv_start, 'interval', hours=int(setting_timer_eztv()))
    scheduler.add_job(YtsTorrent().cron_yts_start, 'interval', hours=int(setting_timer_yts()))
    scheduler.start()

