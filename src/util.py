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


def url_for(endpoint: str, **kwargs) -> str:
    """
    Helper function to generate URLs similar to Flask's url_for.
    This is a simplified version for use in Jinja2 templates.
    
    Args:
        endpoint: Route name in format 'blueprint.function_name'
        **kwargs: Additional query parameters
    
    Returns:
        URL path string
    """
    from urllib.parse import urlencode
    
    # Map of endpoint names to URL paths
    endpoint_map = {
        'public.index': '/',
        'auth.login': '/auth/login',
        'auth.logout': '/auth/logout',
        'auth.register': '/auth/register',
        'auth.account': '/auth/account',
        'auth.forgot_password': '/auth/forgot_password',
        'auth.reset_password': '/auth/reset_password',
        'auth.activate': '/auth/activate',
        'auth.resend_activation_email': '/auth/resend_activation_email',
        'auth.upload': '/auth/upload',
        'auth.newmonth': '/auth/newmonth',
        'auth.groups': '/auth/groups',
        'auth.timecards': '/auth/timecards',
        'auth.user_add': '/auth/user_add',
        'auth.addToGroup': '/auth/addToGroup',
        'auth.timecardForGroup': '/auth/timecardForGroup',
        'auth.show_groups': '/auth/show_groups',
        'auth.show_timecards': '/auth/show_timecards',
        'auth.show_userGroups': '/auth/show_userGroups',
        'auth.groupTimecards': '/auth/groupTimecards',
        'auth.user_list': '/auth/user_list',
        'auth.mesicni_vypis_vyber': '/auth/mesicni_vypis_vyber',
        'auth.mesicni_vypis_vyber_hodiny': '/auth/mesicni_vypis_vyber_hodiny',
        'auth.pristupy_all': '/auth/pristupy_all',
        'auth.pristupy': '/auth/pristupy',
        'auth.skupiny': '/auth/skupiny',
        'auth.vypisy': '/auth/vypisy',
        'static': '/static',
    }
    
    # Get base URL from map
    url = endpoint_map.get(endpoint, '/' + endpoint.replace('.', '/'))
    
    # Add query parameters if provided (properly URL-encoded)
    if kwargs:
        params = urlencode(kwargs)
        url = f"{url}?{params}"
    
    return url


def get_flashed_messages(request=None, with_categories=False):
    """
    Get flash messages from session.
    This is a helper for Jinja2 templates.
    """
    # This will be called from templates with request context
    # For now, return empty list - actual implementation will be in template context processor
    return []


