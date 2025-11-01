from __future__ import annotations

from typing import List, NotRequired, Optional, Required, TypedDict


class ProviderResponse(TypedDict):
    """Standardized response from a provider."""

    data: Entry
    status_code: int


class DefinitionExampleEntry(TypedDict):
    """A single dictionary entry with a definition and optional example."""

    definition: Required[str]
    example: NotRequired[str | None]


class ParsedWordData(TypedDict):
    """Dictionary structure that the module must return in the end."""

    word: Required[str]
    phonetic: NotRequired[str]
    audio: NotRequired[str]
    definition_by_part_of_speech: Required[dict[str, list[DefinitionExampleEntry]]]


class Definition(TypedDict):
    """Definition field type structure. Needed for Meaning."""

    definition: str
    example: str
    synonyms: List[str]
    antonyms: List[str]


class Meaning(TypedDict):
    """Meaning field type structure. Needed for Entry."""

    partOfSpeech: str
    definitions: List[Definition]


class Phonetic(TypedDict):
    """Phonetic field type structure. Needed for Entry."""

    text: str
    audio: Optional[str]


class Entry(TypedDict):
    """
    Entry field type structure.

    Entry is the top-level response list returned by the dictionaryapi.dev.
    (i.e., response[0] for the word).
    """

    word: str
    phonetic: str
    phonetics: List[Phonetic]
    origin: str
    meanings: List[Meaning]
