"""
    atlas.code_operations
    ~~~~
    Commands that run on servers to deploy code.
"""
import logging
import os
import shutil
import subprocess

from git import Repo, Git

from atlas import utilities
from atlas.config import (ENVIRONMENT, CODE_ROOT, LOCAL_CODE_ROOT)
from atlas.config_servers import (SERVERDEFS)

# Setup a sub-logger. See tasks.py for longer comment.
log = logging.getLogger('atlas.code_operations')


def repository_clone(item):
    """
    Clone code to the local server.

    :param item:
    :return:
    """
    log.info('Code | Clone | Item - %s', item)
    code_dir = utilities.code_path(item)
    # Clone repo
    if os.path.exists(code_dir):
        raise Exception('Destinaton directory already exists')
    os.makedirs(code_dir)
    clone = Repo.clone_from(item['git_url'], code_dir)
    log.info('Code | Clone | Result - %s', clone)


def repository_checkout(item):
    """
    Checkout a code to the local server.

    :param item:
    :return:
    """
    log.info('Code | Checkout | Item - %s', item)
    # Fetch repo
    repo = Repo(utilities.code_path(item))
    repo.remote().fetch()
    # Checkout commit
    g = Git(utilities.code_path(item))
    g.checkout(item['commit_hash'])


def repository_remove(item):
    """
    Remove code from the local server.

    :param item:
    :return:
    """
    log.info('Code | Remove | Item - %s', item)
    shutil.rmtree(utilities.code_path(item))


def update_symlink_current(item):
    """
    Determine the path for a code item
    """
    code_folder_current = '{0}/{1}/{2}/{2}-current'.format(
        LOCAL_CODE_ROOT,
        utilities.code_type_directory_name(item['meta']['code_type']),
        item['meta']['name'])
    # Remove symlink if it exists
    if os.path.exists(code_folder_current):
        os.unlink(code_folder_current)
    os.symlink(utilities.code_path(item), code_folder_current)
    log.debug('Code deploy | Symlink | %s', code_folder_current)


def sync_code():
    """Copy the code to all of the relevant nodes.
    """
    log.info('Code | Sync')
    hosts = SERVERDEFS[ENVIRONMENT]['webservers'] + SERVERDEFS[ENVIRONMENT]['operations_server']
    utilities.sync(LOCAL_CODE_ROOT, hosts, CODE_ROOT)
