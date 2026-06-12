# Changelog for `typing_extensions` for checking which types were added when
# https://github.com/python/typing_extensions/blob/main/CHANGELOG.md

# Note that we do not need to explicitly check for python version here,
# because `typing_extensions` will do it for us and either import from `typing`
# or use the back-ported version of the type.

# Once web3 supports >= the noted python version, the type may be directly
# imported from `typing`. Python 3.10 still needs the `typing_extensions`
# backport for these names.

import sys
from typing import TypeAlias

if sys.version_info >= (3, 11):
    from typing import (
        NotRequired,  # py311
        Self,  # py311
        Unpack,  # py311
    )
else:
    # Python 3.10 compatibility path.
    from typing_extensions import (
        NotRequired,
        Self,
        Unpack,
    )
