from datetime import datetime

import pause
from dateutil import tz


def is_over_core_rate(github):
    if 'remaining=0' in str(github.get_rate_limit()):
        return True
    return False

def is_over_search_rate(github):
    if 'remaining=0' in str(github.get_rate_limit().search):
        return True
    return False


def sleep_until_core_rate_reset(github):
    print(github.get_rate_limit())
    dateutc = github.get_rate_limit().core.reset
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')
    utc = dateutc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    t = datetime.now()
    t = t.astimezone(to_zone)
    seconds = min((central - t).seconds, 3600)+180
    print('sleeping for ' + str(seconds) + ' seconds starting at' + str(t))
    pause.seconds(seconds)

def sleep_until_search_rate_reset(github):
    print(github.get_rate_limit().search)
    dateutc = github.get_rate_limit().search.reset
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')
    utc = dateutc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    t = datetime.now()
    t = t.astimezone(to_zone)
    seconds = min((central - t).seconds, 600)+180
    print('sleeping for ' + str(seconds) + ' seconds starting at' + str(t))
    pause.seconds(seconds)

def get_github_token():
    return "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" #generate a token from github and add here
