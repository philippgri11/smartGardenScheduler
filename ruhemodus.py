import json
from datetime import datetime, timedelta

from controlGPIO import disableAllChannels
from database import updateStatus

with open("/home/pi/smartGardenScheduler/environment.json") as f:
    d = json.load(f)
    timeToWaitRuhemodus = d["timeToWaitRuhemodus"]

def ruhemodusON(scheduler):
    disableAllChannels()
    if scheduler.get_job(job_id ='ruhemodusON') is not None:
        scheduler.remove_job(job_id ='ruhemodusON')
    scheduler.add_job(updateStatus, 'date', run_date=datetime.now()+ timedelta(hours=timeToWaitRuhemodus), args=[False],
                      id='ruhemodusON', max_instances=1, jobstore='default')
    updateStatus(True)

def ruhemodusOFF(scheduler):
    scheduler.remove_job(job_id='ruhemodusON')
    updateStatus(False)

def setRuhemodus(status, scheduler):
    print(status)
    if status:
        ruhemodusON(scheduler)
    else:
        ruhemodusOFF(scheduler)