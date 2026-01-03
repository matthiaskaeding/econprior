from econprior.get_data.apis import crossref, openalex


def test_crossref_parse_article() -> None:
    item = {
        "DOI": "10.1257/aer.20180338",
        "title": ["Test Title"],
        "abstract": "This is the abstract.",
        "author": [
            {"given": "John", "family": "Doe"},
            {"given": "Jane", "family": "Smith"},
        ],
        "published": {"date-parts": [[2020, 1, 15]]},
        "container-title": ["American Economic Review"],
    }

    result = crossref.parse_article(item)

    assert result is not None
    assert result["doi"] == "10.1257/aer.20180338"
    assert result["title"] == "Test Title"
    assert result["abstract"] == "This is the abstract."
    assert result["authors"] == ["John Doe", "Jane Smith"]
    assert result["year"] == 2020
    assert result["journal"] == "American Economic Review"


def test_crossref_parse_article_missing_doi() -> None:
    item = {"title": ["No DOI Article"]}
    assert crossref.parse_article(item) is None


def test_openalex_reconstruct_abstract() -> None:
    inverted_index = {
        "This": [0],
        "is": [1],
        "a": [2],
        "test": [3],
        "abstract.": [4],
    }

    result = openalex.reconstruct_abstract(inverted_index)
    assert result == "This is a test abstract."


def test_openalex_reconstruct_abstract_none() -> None:
    assert openalex.reconstruct_abstract(None) is None


def test_openalex_parse_article() -> None:
    item = {
        "doi": "https://doi.org/10.1257/aer.20180338",
        "title": "Test Title",
        "abstract_inverted_index": {"Hello": [0], "world": [1]},
        "authorships": [
            {"author": {"display_name": "John Doe"}},
            {"author": {"display_name": "Jane Smith"}},
        ],
        "publication_year": 2020,
        "primary_location": {"source": {"display_name": "American Economic Review"}},
    }

    result = openalex.parse_article(item)

    assert result is not None
    assert result["doi"] == "10.1257/aer.20180338"
    assert result["title"] == "Test Title"
    assert result["abstract"] == "Hello world"
    assert result["authors"] == ["John Doe", "Jane Smith"]
    assert result["year"] == 2020
    assert result["journal"] == "American Economic Review"


def test_openalex_parse_article_missing_doi() -> None:
    item = {"title": "No DOI Article"}
    assert openalex.parse_article(item) is None
