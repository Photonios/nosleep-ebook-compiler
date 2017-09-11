import re
import sys
import json
import logging

import praw

from typing import List, Tuple


LOGGER = logging.getLogger(__name__)
CLIENT_ID = 'I8apOujHzdRVAg'
CLIENT_SECRET = 'xbljl1NwNZwWO-2UOFimntikbxQ'

reddit = praw.Reddit(user_agent='r/nosleep e-book compiler (by /u/photonios)',
                     client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

def extract_story(submission_body: str) -> str:
    """Extracts the actual story from the specified submission body.

    This involves stripping the links at the top of each submission
    so we're just left with the story itself. We simply find all the
    links and then get everything after the last one."""

    # only match on first 500 chars so we don't match any links at
    # the end of the submission
    matchable_body = submission_body[:500]
    regex_result = re.findall('\[(.*)\]\((.*)\)', matchable_body)

    # it could be that the story does not start with a link
    if len(regex_result) != 0:
        # +3 so we also cut of the blank lines after the link
        last_link = regex_result[-1][1]
        story_start_offset = matchable_body.index(last_link) + len(last_link) + 3
    else:
        story_start_offset = 0

    # find the end of the story, marked by one the markers
    story_end_offset = None
    for end_marker in ['-Secrets', 'EDIT:', 'Edit:']:
        try:
            story_end_offset = submission_body.index(end_marker) + len(end_marker)
        except Exception:
            continue

        break

    if story_end_offset is None:
        LOGGER.warning('Could not find end of story, assuming that\'s all')
        story_end_offset = len(submission_body)

    story = submission_body[story_start_offset:story_end_offset]
    return story


def discover_submissions(submission_url: str) -> List[Tuple[str, str]]:
    """Starts at the specified submission and finds the next submission
    linked in the specified submission.

    Arguments:
        submission_url:
            The URL to the submission to start discovering from.

    Returns:
        An array of tuples of submissions that were discovered.
    """

    submission = reddit.submission(url=submission_url)
    submission_title = submission.title
    submission_body = submission.selftext

    regex_result = (
        re.compile('(?:Next|Future)(?:.*)\((.*)\)', re.IGNORECASE)
        .search(submission_body)
    )

    story = [(submission_title, extract_story(submission_body))]
    LOGGER.info('Pulled story \'%s\'', submission_title)

    if regex_result:
        submission_url_next = regex_result.groups()[0]
        return story + discover_submissions(submission_url_next)

    return story


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    submissions = discover_submissions('https://www.reddit.com/r/nosleep/comments/1db7q8/case_file_1_the_lightning_man/')
    print(submissions)

    with open('submissions.json', 'w') as submissions_file:
        submissions_file.write(json.dumps(submissions))
