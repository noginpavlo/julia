"""
Parser module for API responses fetching dictionary data.

Converts API JSON responses into structured word data, including:
- Word, phonetic, and audio URL
- Definitions grouped by part of speech, with optional examples

Provides:
- `Parser` (abstract base class)
- `DictApiParser` (concrete parser)
- `DefinitionExampleEntry` and `ParsedWordData` TypedDicts

APIs used:
1. dictionaryapi.dev
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import islice
from typing import NotRequired, Required, TypedDict

from requests import Response

from card_manager.services.validator import Definition, Entry, Meaning


class Parser(ABC):
    """Abstract base class for parsing API responses into ParsedWordData format."""

    @abstractmethod
    def __init__(self, response: Response, max_definitions: int) -> None: ...

    @abstractmethod
    def parse_word_data(self) -> ParsedWordData:
        """Orchestrates parsing methosds."""


class DictApiParser(Parser):
    """
    Parse dictionaryapi.dev responses into ParsedWordData format.

    Extracts word, phonetics , audio link, and definitions grouped by part of speech.
    Limits definitions per part of speech using `max_definitions` variable.
    """

    def __init__(self, response: Response, max_definitions: int) -> None:
        self._response = response
        self._max_definitions = max_definitions

    def parse_word_data(self) -> ParsedWordData:

        entry = self._response[0]
        parsed_data: ParsedWordData = {
            "word": entry.get("word"),
            "phonetic": entry.get("phonetic", ""),
            "audio": self._parse_audio(entry),
            "definition_by_part_of_speech": self._group_definitions_by_part_of_speech(entry),
        }

        return parsed_data

    def _group_definitions_by_part_of_speech(
        self, entry: Entry
    ) -> dict[str, list[DefinitionExampleEntry]]:

        result: dict[str, list[DefinitionExampleEntry]] = {}
        for meaning in self._extract_meanings(entry):
            part_of_speech = meaning.get("partOfSpeech", "part_of_speech_unknown")
            raw_definitions = meaning.get("definitions", [])

            transformed_definition_gen = (
                definition_entry
                for definition_entry in (
                    self._transform_definition(definition) for definition in raw_definitions
                )
                if definition_entry is not None
            )

            result[part_of_speech] = list(islice(transformed_definition_gen, self._max_definitions))

        return result

    def _extract_meanings(self, entry: Entry) -> list[Meaning]:
        """Returns meanings list from the entry."""
        return entry.get("meanings", [])

    def _transform_definition(self, definition: Definition) -> DefinitionExampleEntry | None:
        """Converts a raw definition dict into a DefinitionExampleEntry."""
        definition_text = definition.get("definition")
        if not definition_text:
            return None

        example_text = definition.get("example")
        if example_text and not example_text.strip():
            example_text = None

        definition_example_entry = DefinitionExampleEntry(
            definition=definition_text, example=example_text
        )
        return definition_example_entry

    def _parse_audio(self, entry: Entry) -> str:
        """Return the first available audio URL from phonetics, always as a string."""
        for phonetic in entry.get("phonetics", []):
            if isinstance(phonetic, dict):
                audio = phonetic.get("audio")
                if audio:
                    return audio
        return ""


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
