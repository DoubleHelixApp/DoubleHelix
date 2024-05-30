import typing

from wgse.data.chromosome_name_type import ChromosomeNameType


# Deprecated
class SequenceOrderer:
    def __init__(
        self,
        sequences=typing.List[str],
        target: ChromosomeNameType = ChromosomeNameType.Number,
    ) -> None:
        self.target = target
        # Map a canonic name with its index in the original sequences.
        self.sequence_map: dict[str, int] = {
            SequenceOrderer.canonicalize(x[1]): x[0] for x in enumerate(sequences)
        }
        self.ordered_sequences = self._get_ordered()

    def __iter__(self):
        """Generate an ordered list of sequences

        Yields:
            Tuple[int, str]: Tuple containing the index in the
                original sequence its converted name.

        """
        for sequence in self.ordered_sequences:
            yield self.sequence_map[sequence], SequenceOrderer.convert(
                sequence, self.target
            )

    def _get_ordered(self):
        autosome = self._get_autosome()
        sexual = self._get_sexual()
        mitochondrial = self._get_mitochondrial()
        others = self._get_others(autosome, sexual, mitochondrial)
        merged = [*autosome, *sexual, *mitochondrial, *others]
        return merged

    def _get_autosome(self):
        autosome = [x for x in self.sequence_map if x.isnumeric()]
        autosome.sort(key=lambda x: int(x))
        return autosome

    def _get_mitochondrial(self):
        return [x for x in self.sequence_map if x == "m"]

    def _get_sexual(self):
        sexual = []
        if "x" in self.sequence_map:
            sexual.append("x")
        if "y" in self.sequence_map:
            sexual.append("y")
        return sexual

    def _get_others(self, autosome, sexual, mitochondrial):
        others = []
        for sequence in self.sequence_map.keys():
            is_autosome = sequence in autosome
            is_sexual = sequence in sexual
            is_mitochondrial = sequence in mitochondrial
            if not is_autosome and not is_sexual and not is_mitochondrial:
                others.append(sequence)
        others.sort()
        return others

    def canonicalize(sequence_name: str) -> str:
        return SequenceOrderer.convert(sequence_name, ChromosomeNameType.Number)

    def convert(input: str, target: ChromosomeNameType):
        normalized = input.lower()
        if normalized.startswith("chr"):
            normalized = normalized.replace("chr", "", 1)
        if normalized.startswith("mt"):
            normalized = normalized.replace("mt", "m", 1)
        if target == ChromosomeNameType.Chr:
            if normalized.isnumeric() or normalized == "m":
                return "chr" + normalized
            return normalized
        elif target == ChromosomeNameType.Number:
            return normalized
        elif target == ChromosomeNameType.GenBank:
            raise NotImplementedError(
                "Converting to Accession is not supported at the moment."
            )
        raise ValueError(f"Converting to unrecognized target format: {target.name}")
