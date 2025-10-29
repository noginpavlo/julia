# =================================================================================================
# 🛠️ Parser section
# Low-level module that parses validated data:
#   - removes empty and excessive entries from Response.
#   - defines structure of the data returned to the caller
# =================================================================================================
from abc import ABC, abstractmethod
from typing import TypedDict, Required, NotRequired
from itertools import islice
from requests import Response

class DefinitionExampleEntry(TypedDict):
    """A single dictionary entry with a definition and optional example."""

    definition: Required[str]
    example: NotRequired[str | None]


class ParsedWordData(TypedDict):
    """Dictionary structure that the module must return in the end."""

    word: Required[str]
    phonetic: NotRequired[str | None]
    audio: NotRequired[str | None]
    definitions_by_pos: Required[dict[str, list[DefinitionExampleEntry]]]


class ApiParser(ABC):  # Parser/AbstractParser => this name is too similar to DictApiParser
    """Abstract base class for parsing API responses into ParsedWordData format.

    Methods:
        parse_word_data(): Returns ParsedWordData formatted data.
    """

    @abstractmethod
    def __init__(self, response: Response, max_definitions: int) -> None: ...

    @abstractmethod
    def parse_word_data(self) -> ParsedWordData:
        """Orchestrates parsing methosds to parse word datat from Response."""


class DictApiParser(ApiParser):  # => this name is too similar to ApiParesr
    """Parse dictionaryapi.dev responses into ParsedWordData format.

    Extracts word, phonetics , audio link, and definitions grouped by part of speech.
    Limits definitions per part of speech using `max_definitions`.

    Methods:
        parse_word_data(): Returns a ParsedWordData dictionary.
    """

    def __init__(self, response: Response, max_definitions: int) -> None:
        self._response = response
        self._max_definitions = max_definitions

    def _parse_audio(self) -> str | None:
        """Extracts phonetics and the first audio URL from Response."""

        entry = self._response[0]

        phonetics = entry.get("phonetics")
        if phonetics:
            audio = phonetics.get("audio")
            if isinstance(audio, str) and audio:
                return audio

        return None

    def _parse_definitions(self) -> dict[str, list[DefinitionExampleEntry]]:
        """
        Extracts definitions and examples grouped by part of speech, limited by `max_definitions`.
        """

        entry = self._response[0]

        meanings = entry.get("meanings")
        result: dict[str, list[DefinitionExampleEntry]] = {}

        for meaning in meanings:
            pos = meaning.get("partOfSpeech", "unknown_type")
            def_list = meaning.get("definitions")

            def_entry_gen = (
                DefinitionExampleEntry(
                    definition=d["definition"],
                    example=(
                        d.get("example") if d.get("example") and d.get("example").strip() else None
                    ),
                )
                for d in def_list
                if d.get("definition")
            )

            entries_list = list(islice(def_entry_gen, self._max_definitions))

            result[pos] = entries_list

        return result

    def parse_word_data(self) -> ParsedWordData:
        """Utilizes _parse_audio and _parse_definitions to return ParsedWordData dict.

        Extracts the word, phonetic transcription, audio link, and
        definitions grouped by part of speech.
        """

        entry = self._response[0]

        parsed_data: ParsedWordData = {
            "word": entry.get("word"),
            "phonetic": entry.get("phonetic", ""),
            "audio": self._parse_audio(),
            "definitions_by_pos": self._parse_definitions(),
        }

        return parsed_data


