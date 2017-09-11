import os
import re
import sys
import json
import logging
import argparse

from typing import List, Tuple

LOGGER = logging.getLogger(__name__)


def read_submissions(submissions_filename: str) -> List[Tuple[str, str]]:
    """Reads the submissions from the specified JSON file."""

    with open(submissions_filename, 'r') as submissions_file:
        return json.loads(submissions_file.read())


def preprocess_submission_body(submission_body: str) -> str:
    """Pre-processes the submission body by converting *[text]* to
    **[text]**. In Reddit's inline styling language, a single * means
    bold, but in Markdown it would mean italic."""

    return re.sub('\*(.*?)\*', r'**\1**', submission_body)


def generate_markdown_book(submissions: List[Tuple[str, str]]) -> str:
    """Generates a MarkDown e-book from the specified submissions."""

    markdown_content = ''

    for submission_title, submission_body in submissions:
        markdown_content += '# %s' % submission_title
        markdown_content += os.linesep
        markdown_content += os.linesep
        markdown_content += preprocess_submission_body(submission_body)
        markdown_content += os.linesep
        markdown_content += os.linesep

    return markdown_content


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate MarkDown a e-book from a list of submissions.')
    parser.add_argument('submissions_filename', type=str, required=True,
                        help='an integer for the accumulator')
    parser.add_argument('-o', type=str,
                        help='file to write to')

    args = parser.parse_args()

    submissions = read_submissions(args.submissions_filename)
    markdown = generate_markdown_book(submissions)

