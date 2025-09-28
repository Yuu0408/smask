from typing import Dict, List

# Centralized options for contact sending (must mirror frontend dialog)
# TODO: Consider loading these from DB or config in the future.

ALLOWED_ADDRESSES: List[str] = [
    "Hà Nội",
]

FACILITIES_BY_ADDRESS: Dict[str, List[str]] = {
    "Hà Nội": [
        "Bệnh Viện Bạch Mai",
    ],
}


def get_allowed_addresses() -> List[str]:
    return list(ALLOWED_ADDRESSES)


def get_facilities_by_address() -> Dict[str, List[str]]:
    return {k: list(v) for k, v in FACILITIES_BY_ADDRESS.items()}
