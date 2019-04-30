import github as github_origin
import logging
from ogr.mock_core import PersistentObjectStorage
from typing import Type

logger = logging.getLogger(__name__)

old__requestEncode = github_origin.MainClass.Requester._Requester__requestEncode


def new__requestEncode(self, cnx, verb, url, parameters, requestHeaders, input, encode):
    """
    replacement for  github_origin.MainClass.Requester._Requester__requestEncode method
    """
    internal_keys = [verb, url, parameters]
    if self.persistent_storage.is_write_mode:
        status, responseHeaders, output = old__requestEncode(
            self, cnx, verb, url, parameters, requestHeaders, input, encode
        )
        self.persistent_storage.store(
            keys=internal_keys, values=[status, responseHeaders, output]
        )
    else:
        logger.debug(f"Persistent github API: {internal_keys}")
        status, responseHeaders, output = self.persistent_storage.read(
            keys=internal_keys
        )
    return status, responseHeaders, output


def get_Github_class(
    storage_file: str, is_write_mode: bool
) -> Type[github_origin.MainClass.Github]:
    """
    returns improved Github class, what allows read and write communication to yaml file
    It replace method of Reguester class to use storage
    new class attribute:
         persistent_storage
    new class method:
        dump_yaml
    :param storage_file: string with
    :return: Github class
    """
    storage = PersistentObjectStorage(storage_file, is_write_mode=is_write_mode)
    github_origin.MainClass.Requester.persistent_storage = storage
    github_origin.MainClass.Requester._Requester__requestEncode = new__requestEncode
    github_origin.MainClass.Github.persistent_storage = storage
    github_origin.MainClass.Github.dump_yaml = storage.dump

    return github_origin.MainClass.Github