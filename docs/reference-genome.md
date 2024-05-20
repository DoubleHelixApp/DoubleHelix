# Reference genome

In some cases WGSE-NG needs to access the reference genome that was used to create an alignment-map file. Since this is information is not contained in an alignment-map file, WGSE-NG needs to deduct it somehow. This document explain how WGSE-NG solves this problem and what can go wrong.

## Introduction
 The biggest hint for identifying the reference genome is the header of an alignment-map file. The header contains a list of sequences contained in the reference used to do the alignment.

WGSE-NG solves the issue of identifying the reference by maintaining a list of meta-information about a number of reference genomes. In this way it can identify a reference if it's present in this list. The list can be modified and new references can be suggested by using this [GitHub issue template](https://github.com/WGSE-NG/WGSE-NG/issues/new?assignees=chaplin89&labels=reference&projects=&template=add-a-new-reference.md&title=%5BReference%5D+Please+add+a+new+reference) or by submitting a PR using the instruction below.

The process is not perfect and it can potentially give incorrect information (see the section below to understand how it works). In this case some actions may fail. Please feel free to open a [bug report](https://github.com/WGSE-NG/WGSE-NG/issues/new?assignees=&labels=&projects=&template=bug_report.md&title=) if that happens.

## How it works

The identification can works in two different ways, depending on the information available in the alignment-map file:
- Using MD5 of sequences
- Using lengths of sequences

MD5 indicates an MD5 string calculated in a reliable way (that account for case-differences inside the sequence) and is the preferred way and lengths are used only as a fallback when MD5s are not available. Unfortunately, despite MD5 of sequences being part of the [SAM specification standard]() they are not mandatory. Most alignment-map files won't have this field populated.

The lenghts indicate the length of the sequences expressed in base-pair. The lengths itself cannot identify reliably a single sequence as it's totally possible (and happening in practices) to have the same lengths for sequences having a completely different content. What's surely more reliable is to use the whole set of sequences to identify a reference. The set of the lengths contained in a reference happens to be pretty unique for each reference, and it's the current way used by WGSE-NG to identify a reference. It's still possible that two references have a perfectly identical set of lengths having a different content. In this case, if the alignment-map file was associated by WGSE-NG to a reference falling in this situation, WGSE-NG will present a choice to the user. Since it's impossible to reliably determine which reference was used without other information, the user have to choose which reference it's the correct one.

## Add a new reference

It's possible to onboard a new reference to WGSE-NG either by opening a GitHub issue with [this template](https://github.com/WGSE-NG/WGSE-NG/issues/new?assignees=chaplin89&labels=reference&projects=&template=add-a-new-reference.md&title=%5BReference%5D+Please+add+a+new+reference) or by using the following code:

```python
manager = RepositoryManager()
manager.genomes.append(
    manager.ingest(
        "https://source/reference.fa",
        "NIH", # Anything that matches an entry in sources.json
        "38",  # Only 38 or 19
    )
)
GenomeMetadataLoader().save(manager.genomes)
```

A GUI/CLI way will be added in the future.
