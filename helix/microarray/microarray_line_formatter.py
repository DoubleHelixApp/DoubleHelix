from helix.data.microarray_converter import (
    MicroarrayConverterExtensions,
    MicroarrayConverterTarget,
)

TARGET_FORMATTER_MAP: dict[
    MicroarrayConverterTarget, tuple[callable, MicroarrayConverterExtensions]
] = dict()


def target(
    target: MicroarrayConverterTarget, extension=MicroarrayConverterExtensions.TXT
):
    """Simple decorator that binds a microarray target with a function.

    Args:
        target (MicroarrayConverterTarget): Target to bind to the function
        it's decorating.
    """

    def inner_decorator(func):
        TARGET_FORMATTER_MAP[target] = (func, extension)
        return func

    return inner_decorator


class MicroarrayLineFormatter:
    @target(MicroarrayConverterTarget.FTDNA_v1, MicroarrayConverterExtensions.CSV)
    @target(MicroarrayConverterTarget.MyHeritage_v2, MicroarrayConverterExtensions.CSV)
    def to_quote_comma_separated(id, chromosome, position, result):
        return f'"{id}","{chromosome}","{position}","{result}"\n'

    @target(MicroarrayConverterTarget.FTDNA_v3, MicroarrayConverterExtensions.CSV)
    def to_comma_separated(id, chromosome, position, result):
        return f"{id},{chromosome},{position},{result}\n"

    @target(MicroarrayConverterTarget.LivingDNA_v1)
    @target(MicroarrayConverterTarget.LivingDNA_v2)
    @target(MicroarrayConverterTarget.TwentyThreeAndMe_SNPs_API)
    @target(MicroarrayConverterTarget.TwentyThreeAndMe_v3)
    @target(MicroarrayConverterTarget.TwentyThreeAndMe_v35)
    @target(MicroarrayConverterTarget.TwentyThreeAndMe_v4)
    @target(MicroarrayConverterTarget.TwentyThreeAndMe_v5)
    def to_tab_separated(id, chromosome, position, result):
        return f"{id}\t{chromosome}\t{position}\t{result}\n"

    @target(MicroarrayConverterTarget.Ancestry_v1)
    @target(MicroarrayConverterTarget.Ancestry_v2)
    def handle_ancestry(id, chromosome, position, result):
        map_results = {"--": "00", "CT": "TC", "GT": "TG"}
        if result in map_results:
            result = map_results[result]
        return f"{id}\t{chromosome}\t{position}\t{result[0]}\t{result[1]}\n"

    @target(MicroarrayConverterTarget.MyHeritage_v1, MicroarrayConverterExtensions.CSV)
    def handle_my_heritage_v1(id, chromosome, position, result):
        map_results = {"CT": "TC", "GT": "TG"}
        if result in map_results:
            result = map_results[result]
        return MicroarrayLineFormatter.to_quote_comma_separated(
            id, chromosome, position, result
        )

    @target(MicroarrayConverterTarget.FTDNA_v2, MicroarrayConverterExtensions.CSV)
    def handle_ftdna_v2(id, chromosome, position, result):
        output = ""
        if id == "rs5939319":
            output += "RSID,CHROMOSOME,POSITION,RESULT\n"
        return output + MicroarrayLineFormatter.to_quote_comma_separated(
            id, chromosome, position, result
        )
