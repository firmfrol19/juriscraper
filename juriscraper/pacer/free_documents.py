"""
The design here is intended to be used by Celery tasks, so the goal is to
make something that can be run in parallel by a huge number of tasks.

There are a few opportunities to split this up. The general process is as
below:

 + Log into the jurisdiction.
 + Query the free documents report (split this by date range).
 + Download each of the results in the report in its own task.

The only item above that can't be made parallel is logging in, but that's fine
because logging in is a one step thing.
"""
import certifi
import re

import requests
from dateutil.rrule import rrule, DAILY

from juriscraper.lib.log_tools import make_default_logger

logger = make_default_logger()


def make_written_report_url(court_id):
    if 'court_id' == 'ohnd':
        return 'https://ecf.ohnd.uscourts.gov/cgi-bin/OHND_WrtOpRpt.pl'
    else:
        return 'https://ecf.%s.uscourts.gov/cgi-bin/WrtOpRpt.pl' % court_id


def get_written_report_token(url, session):
    """Get the token that's part of the post form.

    This appears to be a kind of CSRF token. In the HTML of every page, there's
    a random token that's added to the form, like so:

        <form enctype="multipart/form-data" method="POST" action="../cgi-bin/WrtOpRpt.pl?196235599000508-L_1_0-1">

    This function simply loads the written report page, extracts the token and
    returns it.
    """
    r = session.get(url)
    m = re.search('../cgi-bin/WrtOpRpt.pl\?(.+)\"', r.text)
    if m is not None:
        return m.group(1)


def query_free_documents_report(court, start, end, cookie):
    s = requests.session()
    s.cookies.set(**cookie)
    written_report_url = make_written_report_url(court)
    csrf_token = get_written_report_token(written_report_url, s)
    dates = [d.strftime('%m/%d/%Y') for d in rrule(DAILY, interval=1,
                                                   dtstart=start, until=end)]
    responses = []
    for d in dates:
        # Iterate one day at a time. Any more and PACER chokes.
        logger.info("Querying written opinions report for '%s' between %s and "
                    "%s" % (court, d, d))
        responses.append(s.post(
            written_report_url + '?' + csrf_token,
            headers={'User-Agent': 'Juriscraper'},
            verify=certifi.where(),
            timeout=300,
            files={
                'filed_from': ('', d),
                'filed_to': ('', d),
                'ShowFull': ('', '1'),
                'Key1': ('', 'cs_sort_case_numb'),
                'all_case_ids': ('', '0'),
            }
        ))
    return responses

