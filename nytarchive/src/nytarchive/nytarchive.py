"""
The nytarchive module provides a class for interacting with the New York Times archive 
API and caching data to parquet files. 

The NYTArchive class takes an optional API key to authenticate with the API, 
which can be provided as a parameter or read from the `nyt_api_key` environment 
variable.
"""
import logging
import os
from collections import namedtuple
from typing import Optional, List, Dict, Any

import pyarrow as pa
import pyarrow.parquet as pq
import requests

NYTArchiveData = namedtuple("NYTArchiveData", ["data", "source"])

logger = logging.getLogger(__name__)


class NYTArchive:
    """
    A class to interact with the New York Times archive API and cache data to parquet
    files.

    Args:
        api_key (str, optional): The API key to authenticate with the New York Times
            archive API. If not provided, the class will attempt to read the key from
            the 'nyt_api_key' environment variable. Defaults to None.
    """

    def __init__(self, api_key: Optional[str] = None):
        self._sess = requests.Session()
        if api_key is None:
            api_key = os.getenv("nyt_api_key")
            if api_key is None:
                raise ValueError(
                    """API key is required for API interaction. Please set
                nyt_api_key environment variable."""
                )
        self._sess.params = {"api-key": api_key}
        self._base_url = "https://api.nytimes.com/svc/archive/v1/"

    def load_data(
        self, year: int, month: int, data_path: str = ".data/", force_load: bool = False
    ) -> NYTArchiveData:
        """
        Load data for a given year and month from the New York Times archive API, or
        from a local parquet file if available.

        Args:
            year: The year to load data for.
            month: The month to load data for.
            data_path: The directory to save and load parquet files from.
                Defaults to "data/".
            force_load: Whether to force data to be loaded from the API even if a
                local parquet file exists. Defaults to False.

        Returns:
            NYTArchiveData: An object containing the loaded data and its source.
        """
        file_name = data_path + f"{year}-{month}.parquet"
        if os.path.exists(file_name) and not force_load:
            logger.info("%s exists. loading from file", file_name)
            table = pq.read_table(file_name)
            return NYTArchiveData(data=table.to_pylist(), source=file_name)
        logger.info("Requesting data for %s/%s", year, month)
        resp = self._sess.get(f"{self._base_url}/{year}/{month}.json", timeout=10)
        article_list = resp.json()["response"]["docs"]
        self.write_to_parquet(article_list, file_name)
        return NYTArchiveData(data=article_list, source="api")

    @staticmethod
    def write_to_parquet(data: List[Dict[str, Any]], file_name: str) -> None:
        """
        Write data to a parquet file.

        Args:
            data: A list of dictionaries containing data to be written.
            file_name: The name of the file to write to.
        """
        table = pa.Table.from_pylist(data)
        pq.write_table(table, file_name)
