
from dataclasses import dataclass
from typing import Callable, List, TypeVar
from datetime import datetime, field
import os


T = TypeVar('T')  # Generic type variable, should be recognized as a filepath-like type


@dataclass
class FileCrawlQuery[T]:
    base_path: T
    filter_f: Callable[..., bool] = lambda _: True  # Default filter function that accepts all files 

@dataclass
class FileCrawlResult[T]:
    results: List[T]
    timestamp: datetime = field(default_factory=datetime.now)


class FileCrawler:

    """
    A utility class for crawling the filesystem starting from a specified base
    path and applying an optional filter function to select files.
    """

    @staticmethod
    def crawl(request: FileCrawlQuery[str]) -> FileCrawlResult[str]:

        """
        Crawl the filesystem starting from the base_path and apply an optional filter function. \n
        - Raises `FileNotFoundError` if the base_path does not exist. \n
        - Raises `ValueError` if the base_path is a file instead of a directory. \n
        """

        if not os.path.exists(request.base_path):
            raise FileNotFoundError(f"The base path {request.base_path} does not exist.")
        if os.path.isfile(request.base_path):
            raise ValueError(f"The base path {request.base_path} is a file, expected a directory.")

        result: List[str] = []

        for root, _, files in os.walk(request.base_path):
            for file in files:
                fp: str = os.path.join(root, file)
                if request.filter_f(fp):
                    result.append(fp)

        return FileCrawlResult(results=result)

