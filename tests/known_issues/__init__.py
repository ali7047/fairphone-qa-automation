"""Known issues: checks that fail today because the shop has a gap.

These tests are expected to be RED until the shop is fixed. They run in their
own, non-blocking job, so they are visible in the report without making the
smoke check (the PR gate) untrustworthy. When the shop fixes the issue, the test
turns green and moves into the smoke suite.
"""
