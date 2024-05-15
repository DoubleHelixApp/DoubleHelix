from enum import Enum, IntFlag, auto


class AlignmentMapFlag(IntFlag):
    """Flags contained in a SAM row.
    Reference: https://samtools.github.io/hts-specs/SAMv1.pdf, Page 7.
    """

    MULTIPLE_SEGMENTS = 0x1
    ALIGNED = 0x2
    UNMAPPED = 0x4
    NEXT_SEGMENT_UNMAPPED = 0x8
    SEQ_REVERSE_COMPLEMENTED = 0x10
    NEXT_SEQ_REVERSE_COMPLEMENTED = 0x20
    FIRST_SEGMENT = 0x40
    LAST_SEGMENT = 0x80
    SECONDARY_ALIGNMENT = 0x100
    NOT_PASSING = 0x200
    DUPLICATE = 0x400
    SUPPLEMENTARY_ALIGNMENT = 0x800


class AlignmentMapOptionalFieldType(Enum):
    UNKNOWN = auto()
    PRINTABLE = "A"
    SIGNED_INT = "i"
    SINGLE_FLOAT = "f"
    PRINTABLE_WITH_SPACES = "Z"
    HEX_ARRAY = "H"
    NUMERIC_ARRAY = "B"


class AlignmentMapOptionalFieldArrayType(Enum):
    UNKNOWN = auto()
    INT_8 = "c"
    UINT_8 = "C"
    INT_16 = "s"
    UINT_16 = "S"
    INT_32 = "i"
    UINT_32 = "I"
    FLOAT = "f"


class AlignmentMapOptionalField:
    def __init__(self, field: str) -> None:
        tag, type, value = field.split(":", 2)

        self.tag = tag
        self.type = self._type_to_enum(type)
        self.value = self._get_value(value)

    def _type_to_enum(self, type: str):
        if type in [x.value for x in AlignmentMapOptionalFieldType]:
            return AlignmentMapOptionalFieldType(type)
        return AlignmentMapOptionalFieldType.UNKNOWN

    def _get_value(self, value):
        if self.type == AlignmentMapOptionalFieldType.SIGNED_INT:
            return int(value)
        elif self.type == AlignmentMapOptionalFieldType.SINGLE_FLOAT:
            return float(value)
        elif self.type == AlignmentMapOptionalFieldType.HEX_ARRAY:
            return bytes.fromhex(value)
        elif self.type == AlignmentMapOptionalFieldType.NUMERIC_ARRAY:
            return self._process_array(value)
        return value

    def _process_array(self, value):
        array_type = AlignmentMapOptionalFieldArrayType.UNKNOWN
        if value[0] in [x.value for x in AlignmentMapOptionalFieldArrayType]:
            array_type = AlignmentMapOptionalFieldArrayType(value[0])
        if array_type == AlignmentMapOptionalFieldArrayType.UNKNOWN:
            return value
        values = value.split(",")
        if len(values) == 1:
            return []
        values = values[1::]
        if array_type == AlignmentMapOptionalFieldArrayType.FLOAT:
            return [float(x) for x in values]
        return [int(x) for x in values]

    def __str__(self) -> str:
        return f"{self.tag}: {self.value}"

    def __repr__(self) -> str:
        return self.__str__()


class AlignmentMapRow:
    def __init__(self, row: str) -> None:
        self.__row: str = row
        self.__values: list[str] = None
        self.__query_template_name: str = None
        self.__values = None
        self.__flag: AlignmentMapFlag = None
        self.__reference_sequence_name: str = None
        self.__position: int = None
        self.__mapping_quality: int = None
        self.__cigar: str = None
        self.__mate_sequence_name: str = None
        self.__mate_position: int = None
        self.__template_length: int = None
        self.__sequence: str = None
        self.__quality: list[int] = None
        self.__optional: list[AlignmentMapOptionalField] = None

    @property
    def values(self):
        if self.__values is None:
            self.__values = self.__row.split()
        return self.__values

    @property
    def query_template_name(self):
        if self.__query_template_name is None:
            self.__query_template_name = self.values[0]
        return self.__query_template_name

    @property
    def flag(self):
        if self.__flag is None:
            self.__flag = AlignmentMapFlag(int(self.values[1]))
        return self.__flag

    @property
    def reference_sequence_name(self):
        if self.__reference_sequence_name is None:
            self.__reference_sequence_name = self.values[2]
        return self.__reference_sequence_name

    @property
    def position(self):
        if self.__position is None:
            self.__position = int(self.values[3])
        return self.__position

    @property
    def mapping_quality(self):
        if self.__mapping_quality is None:
            self.__mapping_quality = int(self.values[4])
        return self.__mapping_quality

    @property
    def cigar(self):
        if self.__cigar is None:
            self.__cigar = self.values[5]
        return self.__cigar

    @property
    def mate_sequence_name(self):
        if self.__mate_sequence_name is None:
            self.__mate_sequence_name = self.values[6]
        return self.__mate_sequence_name

    @property
    def mate_position(self):
        if self.__mate_position is None:
            self.__mate_position = int(self.values[7])
        return self.__mate_position

    @property
    def template_length(self):
        if self.__template_length is None:
            self.__template_length = int(self.values[8])
        return self.__template_length

    @property
    def sequence(self):
        if self.__sequence is None:
            self.__sequence = self.values[9]
        return self.__sequence

    @property
    def quality(self):
        if self.__quality is None:
            self.__quality = [ord(x) - 33 for x in self.values[10]]
        return self.__quality

    @property
    def optional(self):
        if self.__optional is None:
            if len(self.values) <= 10:
                return []
            self.__optional = [AlignmentMapOptionalField(x) for x in self.values[11::]]
        return self.__optional

    def __str__(self) -> str:
        return (
            f"{self.reference_sequence_name}:{self.position}; Q: {self.mapping_quality}"
        )

    def __repr__(self) -> str:
        return self.__str__()
