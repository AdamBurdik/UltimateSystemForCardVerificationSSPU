import argparse
import subprocess
import sys

from sqlalchemy.engine.url import make_url


def invoke_process(proc_name, proc_args, **subprocess_args):
    return subprocess.call([proc_name] + proc_args, **subprocess_args)


def parse_sqlalchemy_url(input_url):
    """
    Parses the input as a valid SQLAlchemy URL, or otherwise raises an
    exception that argparse will recognize as a type validation error.
    """
    try:
        url = make_url(input_url)
        _ = url.get_dialect()  # may throw if the URI refers to a mystery dialect
        return url
    except Exception as e:
        raise argparse.ArgumentTypeError(str(e))


def yes_no(message):
    "Provides an interactive yes/no prompt and returns whether the user answered 'yes'."
    response = input("{} [y/n] ".format(message))
    while response.lower() not in ['y', 'n']:
        response = input("Please enter 'y' or 'n'. ")
    return response == 'y'
