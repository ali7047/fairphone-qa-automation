"""Detection job: shared setup.

The pages to check are picked once per run from the shop's sitemap (see
utils/sitemap.py) and turned into one test per page, so the report shows each
page as its own result.

Options (defined in tests/conftest.py; command line > environment variable > default):
    --max-pages N    / MAX_PAGES    at most N pages (default and cap: 30)
    --pages URLs     / PAGES        check these addresses instead of a sample (comma separated),
                                    e.g. a page a content editor just published
    --sample-seed S  / SAMPLE_SEED  which sample; default: the current ISO week (same pages all week)

Running with 2 workers (-n 2): pytest-xdist requires every worker to collect the
same tests. The main process therefore picks the pages once and hands the list to
each worker, so a sitemap change between two downloads can never split them.
"""

from __future__ import annotations

import datetime as dt
import os
import urllib.request
from urllib.parse import urljoin, urlparse

import pytest

from config.settings import load_settings
from utils.sitemap import disallowed_paths, is_checkable, sample_pages, urls_from_sitemap

MAX_PAGES_CAP = 30  # agreed upper limit: a light, polite check of a live shop
USER_AGENT = "Mozilla/5.0 (compatible; FairphoneQA-detection/1.0)"


def _option(config: pytest.Config, name: str, env_var: str, default: str = "") -> str:
    """Command-line option (defined in tests/conftest.py) > environment variable > default."""
    value = config.getoption(name)
    return str(value) if value not in (None, "") else os.getenv(env_var, default)


def _fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def _iso_week() -> str:
    year, week, _ = dt.date.today().isocalendar()
    return f"{year}-W{week:02d}"


def pick_pages(config: pytest.Config) -> tuple[list[str], dict]:
    """The pages to check this run, and how they were chosen (shown in the report)."""
    settings = load_settings(
        region_code=config.getoption("--region"),
        language_code=config.getoption("--language"),
        base_url=config.getoption("--base-url"),
    )
    size = min(int(_option(config, "--max-pages", "MAX_PAGES", str(MAX_PAGES_CAP))), MAX_PAGES_CAP)
    chosen = [p.strip() for p in _option(config, "--pages", "PAGES").split(",") if p.strip()]
    if chosen:
        pages = [urljoin(settings.base_url + "/", page) for page in chosen][:size]
        return pages, {"source": "given addresses", "count": len(pages), "cap": size}

    host = urlparse(settings.base_url).netloc
    seed = _option(config, "--sample-seed", "SAMPLE_SEED") or _iso_week()
    urls = urls_from_sitemap(_fetch(settings.base_url + "/sitemap.xml"))
    blocked = disallowed_paths(_fetch(settings.base_url + "/robots.txt"))
    checkable = [u for u in urls if is_checkable(u, blocked, host)]
    pages = sample_pages(checkable, size, seed)
    return pages, {
        "source": f"{settings.base_url}/sitemap.xml",
        "pages_in_sitemap": len(urls),
        "checkable_after_robots_txt_and_filters": len(checkable),
        "sample_seed": seed,
        "count": len(pages),
        "cap": size,
    }


def _sample(config: pytest.Config) -> dict:
    """This run's sample: picked once, then reused.

    - Single process: picked on first use and kept on the config.
    - With workers (pytest-xdist): the main process picks it and hands it to every
      worker (pytest_configure_node below), so all workers check exactly the same pages.
    """
    if hasattr(config, "workerinput") and "detection_sample" in config.workerinput:
        return config.workerinput["detection_sample"]
    if not hasattr(config, "_detection_sample"):
        selected = "detection" in (config.getoption("markexpr") or "")
        pages, sampling = pick_pages(config) if selected else ([], {"source": "not selected"})
        config._detection_sample = {"pages": pages, "sampling": sampling}
    return config._detection_sample


@pytest.hookimpl(optionalhook=True)
def pytest_configure_node(node) -> None:
    """pytest-xdist: give each worker the sample the main process picked."""
    node.workerinput["detection_sample"] = _sample(node.config)


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Turn the picked pages into one test per page."""
    if "detection_page" not in metafunc.fixturenames:
        return
    pages = _sample(metafunc.config)["pages"]
    metafunc.parametrize("detection_page", pages, ids=[urlparse(p).path or "/" for p in pages])


@pytest.fixture(scope="session")
def detection_sampling(pytestconfig: pytest.Config) -> dict:
    return _sample(pytestconfig)["sampling"]
