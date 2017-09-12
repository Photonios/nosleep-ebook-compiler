import re
import sys
import json
import logging
import argparse

import praw

from typing import List, Tuple


LOGGER = logging.getLogger(__name__)
CLIENT_ID = 'I8apOujHzdRVAg'
CLIENT_SECRET = 'xbljl1NwNZwWO-2UOFimntikbxQ'

reddit = praw.Reddit(user_agent='r/nosleep e-book compiler (by /u/photonios)',
                     client_id=CLIENT_ID, client_secret=CLIENT_SECRET)


def pull_submission(submission_url: str) -> dict:
    """Pulls the specified submission's contents from the
    specified URL.

    Arguments:
        submission_url:
            The URL of the submission to pull.

    Returns:
        A dictionary containing the submission's
        title and body.
    """

    submission = reddit.submission(url=submission_url)
    LOGGER.info('Pulled story \'%s\'', submission.title)

    return dict(
        url=submission_url.strip(' \r\n'),
        title=submission.title,
        body=submission.selftext,
    )


def pull_submission_list(submission_urls: List[str]) -> List[dict]:
    """Pulls the specified submissions's contents from the
    specified list of URL's.

    Arguments:
        submission_urls:
            URL's pointing to submissions to pull.

    Returns:
        A list of dictionaries containing the submission's
        title and body.
    """

    submissions = [
        pull_submission(submission_url)
        for submission_url in submission_urls
    ]

    LOGGER.info('Pulled %d submission URL\'s', len(submissions))
    return submissions


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


def read_submission_urls_file(submission_urls_filename: str) -> List[str]:
    """Reads submission URL's from the specified file.

    File must contain URL's to Reddit posts, one URL per line."""

    with open(submission_urls_filename, 'r') as submission_urls_file:
        submission_urls = submission_urls_file.readlines()

    LOGGER.info('Read %d submission URL\'s', len(submission_urls))
    return submission_urls


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Pull submissions into a JSON file.')
    parser.add_argument('submission_urls_filename', type=str,
                        help='path to a text file containing submission urls')
    parser.add_argument('-o', '--output', type=str,
                        help='file to write to')

    args = parser.parse_args()

    submission_urls = read_submission_urls_file(args.submission_urls_filename)
    submissions = pull_submission_list(submission_urls)

    submissions_json = json.dumps(submissions, indent=4)
    if args.output:
        with open(args.output, 'w') as output_file:
            output_file.write(submissions_json)

        LOGGER.info('Wrote submissions to \'%s\'', args.output)
