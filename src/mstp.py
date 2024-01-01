"""
MSTP (Min-Send Transfer Protocol) module.
"""
from typing import Dict, List


class MSTPHeaders:
    """
    MSTP headers.
    :author: James Chan
    """

    def __init__(self):
        # Mapping from key to values
        self._dict: Dict[str, str] = {}

    def add(self, key: str, value: str) -> None:
        """
        Adds a header entry.
        :param key: The key of the header entry.
        :param value: The value of the header entry.
        """
        self._dict[key] = value

    def get(self, key: str) -> str | None:
        """
        Retrieves a header value.
        :param key: The key associated with the value to retrieve.
        :return: The value associated with the key; None if the key does not exist.
        """
        return self._dict.get(key)


class MSTPMessage:
    """
    MSTP message.
    :author: James Chan
    """

    # Three types of MSTP messages
    TYPE_REQ = 0
    TYPE_RES = 1
    TYPE_ACK = 2

    TYPE_STRING_MAP = {
        "REQ": 0,
        "RES": 1,
        "ACK": 2
    }

    @staticmethod
    def parse(message: str) -> "MSTPMessage":
        """
        Parses a MSTP message.
        :param message The original message to parse.
        :return: A parsed MSTP message.
        """
        lines = message.split('\n')
        for i in range(len(lines)):
            lines[i] = lines[i].strip()

        # First line
        first_line_sp = lines[0].split(' ')
        type_str = first_line_sp[0]
        action = first_line_sp[1]
        type_int = MSTPMessage.TYPE_STRING_MAP[type_str]

        # Headers
        headers = MSTPHeaders()
        line_index = 1
        while line_index < len(lines) and lines[line_index] != "":
            line = lines[line_index]
            leftmost_equal_index = line.find('=')
            key = line[:leftmost_equal_index]
            value = line[leftmost_equal_index + 1:]
            headers.add(key, value)

            line_index += 1

        # Data
        data_lines: List[str] = []
        line_index += 1
        while line_index < len(lines):
            data_lines.append(lines[line_index])
            line_index += 1
        data = '\n'.join(data_lines)

        return MSTPMessage(type_int, action, headers, data)

    def __init__(self, _type: int, action: str, headers: MSTPHeaders, data: str):
        # The type
        self.type: int = _type

        # The action
        self.action: str = action

        # The headers
        self.headers: MSTPHeaders = headers

        # Data
        self.data: str = data
