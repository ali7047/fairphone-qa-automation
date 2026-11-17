"""Unit tests for utils/sitemap.py (no browser, no network).

Why: the detection job checks only the pages this module picks. If it picked
login actions or robots.txt-blocked pages, the job would knock on doors it
shouldn't; if the sample changed on every re-run, a failure couldn't be re-checked.
"""

from utils.sitemap import (
    disallowed_paths,
    is_checkable,
    sample_pages,
    section_of,
    urls_from_sitemap,
)

HOST = "www.fairphone.com"
ROBOTS = """
User-agent: *
Disallow: /web/login
Disallow: /my
Disallow: /shop/buy-the-fairphone-gen-6-1889   # old product page

User-agent: SomeOtherBot
Disallow: /
"""


def url(path: str) -> str:
    return f"https://{HOST}{path}"


def test_reads_every_loc_once_in_order():
    xml = """<urlset>
      <url><loc>https://www.fairphone.com/</loc></url>
      <url><loc>
        https://www.fairphone.com/stories/a
      </loc></url>
      <url><loc>https://www.fairphone.com/</loc></url>
    </urlset>"""
    assert urls_from_sitemap(xml) == [url("/"), url("/stories/a")]


def test_robots_rules_for_all_crawlers_only():
    assert disallowed_paths(ROBOTS) == ["/web/login", "/my", "/shop/buy-the-fairphone-gen-6-1889"]


def test_section_ignores_the_language_prefix():
    assert section_of(url("/nl/stories/x")) == section_of(url("/stories/y")) == "stories"
    assert section_of(url("/")) == section_of(url("/nl")) == "home"
    assert section_of(url("/shop/fairphone-6-protective-case-1892")) == "shop"


def test_actions_blocked_paths_and_other_hosts_are_left_out():
    blocked = disallowed_paths(ROBOTS)
    assert is_checkable(url("/stories/a"), blocked, HOST)
    assert is_checkable(url("/nl/warranty"), blocked, HOST)
    assert not is_checkable(url("/auth0/social/complete"), blocked, HOST)  # login action
    assert not is_checkable(url("/nl/add/take_back/product"), blocked, HOST)  # "add" action
    assert not is_checkable(url("/shop/cart"), blocked, HOST)  # needs a session, tested by smoke
    assert not is_checkable(url("/my"), blocked, HOST)  # robots.txt
    assert not is_checkable(url("/shop/buy-the-fairphone-gen-6-1889"), blocked, HOST)  # robots.txt
    assert not is_checkable("https://support.fairphone.com/hc/en-us", blocked, HOST)  # another site


def _site() -> list[str]:
    stories = [url(f"/stories/story-{n}") for n in range(100)]
    shop = [url(f"/shop/product-{n}") for n in range(40)]
    small = [url("/warranty"), url("/contact"), url("/legal/terms")]
    return [url("/"), *stories, *shop, *small]


def test_sample_is_capped_and_always_contains_the_home_page():
    sample = sample_pages(_site(), size=30, seed="2026-W47")
    assert len(sample) == 30
    assert len(set(sample)) == 30
    assert url("/") in sample


def test_same_seed_gives_the_same_pages_so_a_rerun_checks_the_same_week():
    assert sample_pages(_site(), 30, "2026-W47") == sample_pages(_site(), 30, "2026-W47")


def test_another_week_checks_other_pages():
    assert set(sample_pages(_site(), 30, "2026-W47")) != set(sample_pages(_site(), 30, "2026-W48"))


def test_small_sections_are_not_crowded_out_by_big_ones():
    sample = sample_pages(_site(), size=10, seed="any")
    sections = {section_of(page) for page in sample}
    assert {"home", "warranty", "contact", "legal", "stories", "shop"} <= sections


def test_sample_never_exceeds_what_exists():
    assert len(sample_pages([url("/"), url("/a")], size=30, seed="x")) == 2
    assert sample_pages(_site(), size=0, seed="x") == []
