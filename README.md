# Supplementary material: Art and Architectural Argumentation Ontology

Data, queries and scripts for the article

> George Bruseker, Matthew Fielding, Denitsa Nenova, Rocio Jimenez-Diaz and Thomas Hänsli. *Art and Architectural Argumentation Ontology: A CIDOC CRM Compatible Ontology for Semantically Representing Historical Research Data.* ACM Journal on Computing and Cultural Heritage (JOCCH), submission JOCCH-26-0283. DOI to be added.

Archived version of this supplement: DOI to be added.

## What is here

The article describes the core of the ontology (version 0.9 as specified in CRMaaa 1.5.4). Everything here is run against **CRMaaa 1.5.4.2**, the corrected RDF serialization of 1.5.4, and **CIDOC CRM 7.1.3**. Each folder matches a section of the article.

| Folder | Article | Contents |
|---|---|---|
| `ontology/` | 4.1 | `crmaaa-1.5.4.2.rdf`, a copy of the release published at https://github.com/swiss-art-research-net/crmaaa and archived at https://doi.org/10.5281/zenodo.24163947 |
| `5-use-cases/` | 5 | The three use cases in Turtle: Isabella, the G'psgolox Totem Pole, the Brandenburg Gate |
| `6.1-compatibility/` | 6.1 | Checks the use-case data against the ontologies, projects it to plain CIDOC CRM and runs the perspective query |
| `6.2-equal-information/` | 6.2 | Encodes the same historical information in CIDOC CRM and in AAAo and counts triples, nodes and query patterns |
| `6.3-competency-questions/` | 6.3 | Runs the competency questions over the AAAo data and over its CIDOC CRM projection |
| `run-it-yourself/` | 6.1 | The 6.1 queries prepared for an online SPARQL playground, with nothing to install |
| `external/` | | CIDOC CRM 7.1.3 (RDFS), used by the scripts |

Each script folder holds the report the script produced.

## Running it

    pip install -r requirements.txt
    ./run-all.sh

`run-all.sh` regenerates every report in place; a version control diff, or a comparison with the archived copy, shows that the results are unchanged. To check the Section 6.1 results without installing anything, follow `run-it-yourself/README.txt`.

## Conventions

- The prefix `aaao:` stands for `https://takin.solutions/ontologies/crmaaa/`, the namespace of CRMaaa 1.5.4. Example data uses `https://example.org/aaao/`.
- CRMaaa 1.5.4.2 corrects the 1.5.4.1 serialization. It adds the inverse property declarations, the missing range of ZP19i, the subclass statement E13 Attribute Assignment ⊑ ZE13 Speech Act and the licence statement; fixes the superproperties of ZP26 and ZP62i; corrects garbled labels; and corrects four misspelled identifiers: `ZP27_ascribes_residence_place`, `ZP36i_is_referent_ascribed_by`, `ZP59i_is_obligation_relation_ascribed_by` and `ZP64i_is_property_right_subject_of`. The full list is in the release notes of 1.5.4.2.

## The ontology and its maintainers

CRMaaa was developed by Takin.solutions and SARI; its versions up to 1.5.4.2 are published at https://github.com/swiss-art-research-net/crmaaa. From version 2.0 the ontology, renamed AAAo (Art and Architectural Argumentation Ontology), is maintained by the Swiss Art Research Infrastructure (SARI), University of Zurich, in the namespace https://ontology.swissartresearch.net/aaao/, at https://github.com/swiss-art-research-net/aaao. Its development environment is OntoME, https://ontome.net/project/69.

## Licences

- Code (`*.py`, `*.sh`, `*.rq`): MIT, see `LICENSE-code.txt`.
- Data and reports (`*.ttl`, `*.txt`) and the ontology: CC BY-SA 4.0, see `LICENSE-data.txt`.
- `external/CIDOC_CRM_v7.1.3.rdf`: CC BY 4.0, FORTH-ICS and the CIDOC CRM SIG.

Copyright © 2026 Takin.solutions and Swiss Art Research Infrastructure (SARI), University of Zurich.
