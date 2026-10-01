"""
ENSIP-15 normalization tests sourced from the upstream ens-normalize.js repository.

Spec: https://docs.ens.domains/ensip/15

To verify that the local spec and test files are up to date with the latest
upstream versions, run:

    The scheduled compatibility workflow verifies these fixtures against upstream.
"""

import pytest
import json
import os

from ens import (
    InvalidName,
)
from ens._normalization import (
    normalize_name_ensip15,
)

NORMALIZATION_TESTS_PATH = os.path.join(
    os.path.dirname(__file__), "normalization_tests.json"
)
with open(NORMALIZATION_TESTS_PATH, encoding="utf-8") as f:
    normalization_tests = json.load(f)

POSITIVE_TEST_CASES = [test for test in normalization_tests if "error" not in test]
NEGATIVE_TEST_CASES = [test for test in normalization_tests if "error" in test]


def get_test_case_id(test_case):
    name = test_case["name"]
    return name if len(name) <= 100 else f"{name[:80]}...({len(name)} chars)"


# gut check that we have all the tests
if not len(POSITIVE_TEST_CASES) + len(NEGATIVE_TEST_CASES) == len(normalization_tests):
    raise AssertionError("Not all normalization tests are accounted for.")


@pytest.mark.parametrize(
    "positive_test_case",
    POSITIVE_TEST_CASES,
    ids=get_test_case_id,
)
def test_normalize_name_ensip15_positive_test_cases(positive_test_case):
    name = positive_test_case["name"]

    expected = positive_test_case.get("norm", positive_test_case.get("name"))
    assert normalize_name_ensip15(name).as_text == expected


@pytest.mark.parametrize(
    "negative_test_case",
    NEGATIVE_TEST_CASES,
    ids=get_test_case_id,
)
def test_normalize_name_ensip15_negative_test_cases(negative_test_case):
    name = negative_test_case["name"]

    with pytest.raises(InvalidName):
        normalize_name_ensip15(name)
