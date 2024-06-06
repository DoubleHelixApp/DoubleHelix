from math import ceil, floor, log, log10
from typing import OrderedDict


class UnitPrefix:
    def convert_bytes(input: int, decimal=2):
        if input < 1 and input > 0:
            raise ValueError("Can't convert a fractional number of bytes")
        elif input < 0:
            raise ValueError("Can't convert a negative number of bytes")
        converted = None
        si_prefixes = OrderedDict(
            [
                ("B", (0, 10, 0)),
                ("kB", (10, 20, 10)),
                ("MB", (20, 30, 20)),
                ("GB", (30, 40, 30)),
                ("TB", (40, None, 40)),
            ]
        )
        if input == 0:
            return "0B"

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

    def convert(input: int, decimal=2):
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
        # i.e., -3.9 should become -4;
        #        3.9 should become 4
        if input_log < 0:
            input_log = int(floor(input_log))
        else:
            input_log = int(ceil(input_log))

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
