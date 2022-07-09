import json

import rpyc
import RPi.GPIO as GPIO
from rpyc.utils.server import ThreadedServer
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler

import database
from controlGPIO import outputServer, setupGPIO, outputWithoutInformBackend
from ruhemodus import setRuhemodus

with open("/home/pi/smartGardenScheduler/environment.json") as f:
    d = json.load(f)
    databaseName = d["databaseName"]
    databasePath = d["databasePath"]

class SchedulerService(rpyc.Service):
    def addJob(self, id, day_of_week, hour, minute, status, GPIO):
        print(id)
        print(day_of_week)
        print(hour)
        print(minute)
        print(GPIO)
        print(status)
        scheduler.add_job(outputServer, 'cron', hour=hour,
                      minute=minute, id=id, args=(GPIO, status),
                      max_instances=1, jobstore='default', day_of_week=day_of_week)

    def modifyJob(self, job_id, day_of_week, hour, minute):
        print(job_id)
        print(day_of_week)
        print(hour)
        print(minute)
        trigger = CronTrigger(hour=hour,minute=minute, day_of_week=day_of_week)
        scheduler.reschedule_job(job_id=job_id, trigger=trigger,jobstore='default')

    def pause_job(self, job_id, jobstore=None):
        return scheduler.pause_job(job_id, jobstore)

    def resume_job(self, job_id, jobstore=None):
        return scheduler.resume_job(job_id, jobstore)

    def remove_job(self, job_id, jobstore=None):
        scheduler.remove_job(job_id, jobstore)

    def get_job(self, job_id):
        return scheduler.get_job(job_id)

    def get_jobs(self, jobstore=None):
        return scheduler.get_jobs(jobstore)

    def output(self, channel, state):
        outputWithoutInformBackend(channel=channel, state=state)

    def setRuhemodusStatus(self, status):
        setRuhemodus(status, scheduler)

    def getStatusRuhemodus(self):
        print(database.getStatusRuhemodus())
        return database.getStatusRuhemodus()

jobstores = {'default': SQLAlchemyJobStore(url='sqlite:///' + databasePath)}
scheduler = BackgroundScheduler(jobstores=jobstores)

def printWorks():
    print('works')

if __name__ == '__main__':
    printWorks()
    scheduler.start()
    protocol_config={"allow_public_attrs": True, "allow_all_attrs": True, "allow_pickle": True}
    server = ThreadedServer(SchedulerService, port=12345, protocol_config=protocol_config)
    setupGPIO()
    try:
        server.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        scheduler.shutdown()
        GPIO.cleanup()