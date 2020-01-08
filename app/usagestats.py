import os
import time
import git
import requests
import uuid
import threading
from config import basedir
from .models import User, Sample, Action
from .util import filesystem_usage

start_time = time.time()
usage_statistics_url_source = 'https://raw.githubusercontent.com/HolgerGraef/MSM-usage-statistics/master/url'
usage_statistics_sleep_time = 60.       # wait 1 minute after every update

# read site name from file if possible
if os.path.exists('usage_stats_site'):
    with open('usage_stats_site', 'r') as f:
        usage_statistics_site_name = f.readline().strip()
else:
    usage_statistics_site_name = 'unknown'


class UsageStatisticsThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.daemon = True  # kill the thread when the app is killed

        # run usage statistics thread (only run once, even in debug mode)
        if (not app.debug) or (os.environ.get("WERKZEUG_RUN_MAIN") == 'true'):
            self.start()

    def run(self):
        # determine site key or create one
        if os.path.exists('usage_stats_key'):
            with open('usage_stats_key', 'r') as f:
                key = f.readline().strip()
        else:
            key = str(uuid.uuid4())
            with open('usage_stats_key', 'w') as f:
                f.write(key)

        # obtain git revision and check if repo is clean
        if self.app.config['STANDALONE']:
            git_rev = 'standalone'
            git_clean = True
        else:
            repo = git.Repo(basedir)  # get Sample Manager git repo
            git_rev = str(repo.rev_parse('HEAD'))
            git_clean = str(not repo.is_dirty())

        dbsize, totuploadvol, availablevol = filesystem_usage(self.app)

        while True:
            with self.app.app_context():
                data = {'key': key,
                        'site': usage_statistics_site_name,
                        'users': User.query.count(),
                        'samples': Sample.query.filter_by(isdeleted=False).count(),
                        'actions': Action.query.join(Sample).filter(Sample.isdeleted == False).count(),
                        'starttime': start_time,
                        'uptime': time.time()-start_time,
                        'gitrev': git_rev,
                        'gitclean': git_clean,
                        'dbsize': dbsize,
                        'uploadvol': totuploadvol,
                        'availablevol': availablevol}

            # get usage statistics script url from GitHub
            try:
                response = requests.get(usage_statistics_url_source)
                if response.status_code == 200:
                    url = response.content.strip()
                    requests.post(url, json=data)
            except Exception as e:
                pass        # do not crash when there is e.g. a ConnectionError, simply keep trying

            time.sleep(usage_statistics_sleep_time)
