from math import floor, log, log10
from typing import OrderedDict


class UnitPrefix:
    """Convert a quantity into a more readable form using unit prefixes.

    This class is expecially useful for very big or very small number, that
    are difficult to read or visualize.

    Examples:
        >>> UnitPrefix.convert_bytes(1024)
        '1kB'
        >>> UnitPrefix.convert(1000)
        '1k'
        >>> UnitPrefix.convert(0.01)
        '10m'
    """

    def convert_bytes(input: int, decimal=2) -> str:
        """Convert bytes using binary prefixes.

        Args:
            input (int): The number to convert.
            decimal (int, optional): Number of decimals to use. Defaults to 2.

        Raises:
            ValueError: The input number is a float
            ValueError: The input number is negative.

        Returns:
            str: Converted number.
        """
        if input is None:
            return None
        if isinstance(input, float):
            raise ValueError("Can't convert a fractional number of bytes")
        elif input < 0:
            raise ValueError("Can't convert a negative number of bytes")
        converted = None
        si_prefixes = OrderedDict(
            [
                (" B", (0, 10, 0)),
                (" kB", (10, 20, 10)),
                (" MB", (20, 30, 20)),
                (" GB", (30, 40, 30)),
                (" TB", (40, None, 40)),
            ]
        )
        if input == 0:
            return "0 B"

        input_log = log(input, 2)
        input_log = int(floor(input_log))

        converted = None
        for letter, interval in si_prefixes.items():
            min_interval = interval[0]
            max_interval = interval[1]
            in_interval = False
            if max_interval is None:
                in_interval = input_log >= min_interval
            elif min_interval is None:
                in_interval = input_log < max_interval
            else:
                in_interval = input_log >= min_interval and input_log < max_interval

            if in_interval:
                converted = f"{(input / 2**interval[2]):.{decimal}f}"
                # Not interested in any .0000 at the end
                converted = converted.rstrip("0").rstrip(".")
                # If converted == "0" will become ""
                if converted == "":
                    converted = "0"
                converted += letter
                break
        return converted

    def convert(input: int, decimal=2) -> str:
        """Convert a quantity using metric prefixes.

        Args:
            input (int): The number to convert.
            decimal (int, optional): Number of decimals to use. Defaults to 2.

        Returns:
            str: Converted number.
        """
        converted = None
        si_prefixes = OrderedDict(
            [
                ("p", (None, -9, -12)),
                ("n", (-9, -6, -9)),
                ("μ", (-6, -3, -6)),
                ("m", (-3, 0, -3)),
                ("", (0, 3, 0)),
                ("k", (3, 6, 3)),
                ("M", (6, 9, 6)),
                ("G", (9, 12, 9)),
                ("T", (12, 15, 12)),
                ("P", (15, None, 15)),
            ]
        )
        if input == 0:
            return "0"

        input_log = log10(input)
        input_log = int(floor(input_log))

        converted = None
        for letter, interval in si_prefixes.items():
            min_interval = interval[0]
            max_interval = interval[1]
            in_interval = False
            if max_interval is None:
                in_interval = input_log >= min_interval
            elif min_interval is None:
                in_interval = input_log < max_interval
            else:
                in_interval = input_log >= min_interval and input_log < max_interval

            if in_interval:
                converted = f"{(input / 10**interval[2]):.{decimal}f}"
                # Not interested in any .0000 at the end
                converted = converted.rstrip("0").rstrip(".")
                # If converted == "0" will become ""
                if converted == "":
                    converted = "0"
                converted += letter
                break
        return converted
