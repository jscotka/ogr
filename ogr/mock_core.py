from typing import Callable, Any, Union
import functools
import logging
from ogr.abstract import PullRequest, PRComment, PRStatus
import datetime


logger = logging.getLogger(__name__)


def readonly(*,
             return_value: Union[Any, None] = None,
             return_function: Union[Callable, None] = None,
             text: str = "") -> Any:
    """
    Decorator to log  function and ovewrite return value of object methods
    Ignore function name as first parameter and ignore every other parameters

    :param return_value: returned Any value if given, return_function has higher prio if set
    :param return_function: return function and give there parameters also
           original caller object return_function(self, *args, **kwargs)
    :param text: str string to put to logger output
    :return: Any type what is expected that function or return value returns
    """
    def decorator_readonly(func):
        @functools.wraps(func)
        def readonly_func(self, *args, **kwargs):
            if not self.read_only:
                return func(self, *args, **kwargs)
            else:
                if text:
                    logger.warning(text)
                logger.warning(f"{func.__name__} with args:{args} kwargs:{kwargs}")
                if return_function:
                    return return_function(self, *args, **kwargs)
                else:
                    return return_value
        return readonly_func
    return decorator_readonly


class GitProjectReadOnly:
    id = 1
    author = "Nobody"
    url = "None"

    @classmethod
    def pr_create(
        cls, original_object: object, title: str, body: str, target_branch: str, source_branch: str
    ) -> "PullRequest":
        kwargs = {"title": title,
                  "description": body,
                  "target_branch": target_branch,
                  "source_branch": source_branch,
                  "id": cls.id,
                  "status": PRStatus.open,
                  "url": cls.url,
                  "author": cls.author,
                  "created": datetime.datetime}

        output = PullRequest(**kwargs)
        return output

    @classmethod
    def pr_comment(
        cls,
        original_object: object,
        pr_id: int,
        body: str,
        commit: str = None,
        filename: str = None,
        row: int = None,
    ) -> "PRComment":
        pull_request = original_object.get_pr_info(pr_id)
        kwargs = {"comment": body, "author": cls.author}
        output = PRComment(**kwargs)
        kwargs["pr"] = pull_request
        kwargs["commit"] = commit
        kwargs["filename"] = filename
        kwargs["row"] = row
        return output

    @classmethod
    def pr_close(cls, original_object: object,  pr_id: int) -> "PullRequest":
        pull_request = original_object.get_pr_info(pr_id)
        pull_request.status = PRStatus.closed
        return pull_request

    @classmethod
    def pr_merge(cls, original_object: object,  pr_id: int) -> "PullRequest":
        pull_request = original_object.get_pr_info(pr_id)
        pull_request.status = PRStatus.merged
        return pull_request
