import re
import json
import logging
import argparse

from typing import List

LOGGER = logging.getLogger(__name__)


def read_submissions(submissions_filename: str) -> List[dict]:
    """Reads the submissions from the specified JSON file."""

    with open(submissions_filename, 'r') as submissions_file:
        return json.loads(submissions_file.read())


def find_submission_body_start(submission_body: str) -> int:
    """Finds the start of a story's body by stripping everything before
    the last link in the first characters.

    Returns:
        The index at which the story's body starts.
    """

    # only match on first chars so we don't match any links at
    # the end of the submission
    offset = int(len(submission_body) / 2)
    matches = list(re.finditer(r'\[(?:.*)\]\((?:.*)\)', submission_body[:offset]))

    return matches[-1].end() if len(matches) != 0 else 0


def find_submission_body_end(submission_body: str) -> int:
    """Finds the end of the story's body by stripping edits and
    links at the bottom.

    Returns:
        the index at which the story's body ends.
    """

    markers = [
        '-Secrets',
        'EDIT:',
        'Edit:',
        'Continued in [part',
        'Concluded in [Part',
        '[Part'
    ]

    # only match the bottom half of the story so we don't
    # match things at the start of the story
    offset = int(len(submission_body) / 2)

    # find the end of the story, marked by one of the markers,
    # or none, and then we don't cut off anything at the end
    story_end_offset = None
    for end_marker in markers:
        try:
            story_end_offset = submission_body.index(end_marker, offset)
        except Exception as excp:
            continue

        break

    # no marker has been found, take the entire story
    if story_end_offset is None:
        story_end_offset = len(submission_body)

    return story_end_offset


def preprocess_submission_body(submission_body: str) -> str:
    """Pre-processes the story's body by finding the start and
    end."""

    story_start_offset = find_submission_body_start(submission_body)
    story_end_offset = find_submission_body_end(submission_body)

    return submission_body[story_start_offset:story_end_offset].strip(' \r\n')


def preprocess_submission(submission: dict) -> dict:
    """Pre-processes the the specified submission."""

    LOGGER.info('Pre-processing \'%s\'', submission['title'])

    return dict(
        url=submission['url'],
        title=submission['title'],
        body=preprocess_submission_body(submission['body'])
    )


def preprocess_submission_list(submissions: List[dict]) -> List[dict]:
    """Pre-processes a list of submissions."""

    preprocessed_submissions = [
        preprocess_submission(submission)
        for submission in submissions
    ]

    LOGGER.info('Pre-processed %d submissions', len(preprocessed_submissions))
    return preprocessed_submissions


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Pre-process submissions by cleaning body and title.')
    parser.add_argument('submissions_filename', type=str,
                        help='path to a file containing submissions')
    parser.add_argument('-o', '--output', type=str,
                        help='file to write to, if not specified, the exiting file is overwritten')

    args = parser.parse_args()

    output_filename = args.output or args.submissions_filename
    submissions = read_submissions(args.submissions_filename)
    preprocessed_submissions = preprocess_submission_list(submissions)

    with open(output_filename, 'w') as output_file:
        output_file.write(json.dumps(preprocessed_submissions, indent=4))
