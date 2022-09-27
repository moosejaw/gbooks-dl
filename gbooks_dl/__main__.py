import os
import argparse


parser = argparse.ArgumentParser(
    prog="gbooks-dl",
    description=
    "A command-line program for downloading online book previews to your local computer."
)
parser.add_argument(
    'URL',
    nargs=1,
    help="A URL containing a preview-able book to be downloaded."
)
parser.add_argument(
    '-f', '--output-folder',
    nargs=1,
    default=os.getcwd(),
    help="The file folder in which the files containing the book previews should be saved."
)

if __name__ == '__main__':
    args = parser.parse_args()

    from gbooks_dl.pipeline import pipeline
    pipeline(args.url, args.dest)
