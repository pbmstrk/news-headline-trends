import itertools
import logging
import time
from datetime import datetime

import click

from .nytarchive import NYTArchive

logging.basicConfig(
    format="%(asctime)s: %(levelname)s: %(message)s", level=logging.INFO
)


@click.command()
@click.argument("start_year", type=click.INT)
@click.argument("end_year", type=click.INT)
@click.option("--force-load", is_flag=True, default=False)
def run(start_year: int, end_year: int, force_load: bool) -> None:
    """
    Loads data from the New York Times archive API using the NYTArchive class for a
    given range of years. Saves the data to local parquet files.

    Args:
        start_year: The starting year of the range of data to load.
        end_year: The ending year of the range of data to load.
        force_load: Whether to force data to be loaded from the API even if a
            local parquet file exists. Defaults to False.
    """
    nyt = NYTArchive()

    CURRENT_MONTH = datetime.now().month 
    CURRENT_YEAR = datetime.now().year

    years = list(range(start_year, end_year + 1))
    months = list(range(1, 13))

    for year, month in itertools.product(years, months):
        if year == CURRENT_YEAR and month >= CURRENT_MONTH:
            break
        data = nyt.load_data(year, month, force_load=force_load)
        if data.source == "api":
            time.sleep(12)


if __name__ == "__main__":
    run() # pylint: disable=no-value-for-parameter
