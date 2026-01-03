JOURNALS = {
    "aer": {
        "name": "American Economic Review",
        "issn": "0002-8282",
    },
    "econometrica": {
        "name": "Econometrica",
        "issn": "0012-9682",
    },
    "qje": {
        "name": "Quarterly Journal of Economics",
        "issn": "0033-5533",
    },
    "jpe": {
        "name": "Journal of Political Economy",
        "issn": "0022-3808",
    },
    "restud": {
        "name": "Review of Economic Studies",
        "issn": "0034-6527",
    },
}


def get_issn(journal_key: str) -> str:
    return JOURNALS[journal_key]["issn"]


def get_name(journal_key: str) -> str:
    return JOURNALS[journal_key]["name"]
