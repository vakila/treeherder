from urllib import urlencode

from django.conf import settings

from treeherder.etl.common import fetch_json
from treeherder.model.derived import RefDataManager


def get_bz_source_url():
    hostname = settings.BZ_API_URL
    params = {
        'keywords': 'intermittent-failure',
        'chfieldfrom': '-1y',
        'include_fields': ('id,summary,status,resolution,'
                           'op_sys,cf_crash_signature, '
                           'keywords, last_change_time')
    }
    endpoint = 'rest/bug'

    source_url = '{0}/{1}?{2}'.format(
        hostname, endpoint, urlencode(params)
    )
    return source_url


class BzApiBugProcess():

    def run(self):
        bug_list = []

        offset = 0
        limit = 500

        while True:
            # fetch the bugzilla service until we have an empty result
            paginated_url = "{0}&offset={1}&limit={2}".format(
                get_bz_source_url(),
                offset,
                limit
            )
            bugs_chunk = fetch_json(paginated_url).get('bugs', [])
            bug_list += bugs_chunk
            if len(bugs_chunk) < limit:
                break
            offset += limit

        if bug_list:
            for bug in bug_list:
                # drop the timezone indicator to avoid issues with mysql
                bug["last_change_time"] = bug["last_change_time"][0:19]

            with RefDataManager() as rdm:
                rdm.update_bugscache(bug_list)
