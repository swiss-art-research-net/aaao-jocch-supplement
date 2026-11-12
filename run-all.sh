#!/usr/bin/env bash
# Regenerates every report in this supplement from the files in it.
# Needs Python 3.9+ with the packages in requirements.txt (pip install -r requirements.txt).
set -euo pipefail
cd "$(dirname "$0")"
AAAO=../ontology/crmaaa-1.5.4.2.rdf
CRM=../external/CIDOC_CRM_v7.1.3.rdf

echo "6.1 use-case check, projection to CIDOC CRM, perspective query"
(cd 5-use-cases && python3 ../6.1-compatibility/check_and_project.py $AAAO $CRM \
   isabella.ttl totem.ttl brandenburg.ttl > ../6.1-compatibility/report.txt)

echo "6.2 representational cost at equal information"
(cd 6.2-equal-information && python3 equal_information.py > equal-information-report.txt)

echo "6.3 competency questions"
(cd 5-use-cases && python3 ../6.3-competency-questions/competency_questions.py $AAAO $CRM \
   isabella.ttl totem.ttl brandenburg.ttl > ../6.3-competency-questions/cq-report.txt)

echo "done"
