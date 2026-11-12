"""Evidence for Sections 5 and 6.2 of the AAAo paper.

1. Load each use-case Turtle file and check it against the AAAo ontology
   (CRMaaa 1.5.4.2, the corrected RDF of 1.5.4) and CIDOC CRM 7.1.3: every class and
   property used is declared, and every triple respects the domain and range
   of its property under RDFS subclass reasoning.
2. Project the AAAo data back to plain CIDOC CRM with one SPARQL CONSTRUCT
   query, and check the projected triples against CIDOC CRM in the same way.
3. Run the perspective query on the Totem Pole data: who owned the pole on
   1 January 1950, and for whom.

Usage: python3 check_and_project.py AAAO_RDF CRM_RDF usecase1.ttl ... > report.txt
"""
import sys
import rdflib
from rdflib import RDF, RDFS, URIRef

AAA = "https://takin.solutions/ontologies/crmaaa/"
CRM = "http://www.cidoc-crm.org/cidoc-crm/"

PREFIXES = f"""PREFIX aaao: <{AAA}>
PREFIX crm: <{CRM}>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""

PROJECTION = PREFIXES + """
CONSTRUCT { ?subject ?crmProperty ?target }
WHERE {
  ?fact ?subjectProp ?subject ;
        ?targetProp ?target ;
        ?relationProp ?crmProperty .
  ?subjectProp  rdfs:subPropertyOf* aaao:ZP1_has_intentional_subject .
  ?targetProp   rdfs:subPropertyOf* aaao:ZP2_ascribes_intentional_target .
  ?relationProp rdfs:subPropertyOf* aaao:ZP3_ascribes_intentional_relation .
}
"""

PERSPECTIVE = PREFIXES + """
SELECT ?ownerLabel ?groupLabel
WHERE {
  ?status a aaao:ZE8_Ownership_Status ;
          aaao:ZP23_has_ownership_subject ?pole ;
          aaao:ZP24_ascribes_owner ?owner ;
          aaao:ZP4_holds_for ?group ;
          crm:P4_has_time-span ?ts .
  ?pole rdfs:label "G'psgolox Totem Pole" .
  ?owner rdfs:label ?ownerLabel .
  ?group rdfs:label ?groupLabel .
  OPTIONAL { ?ts crm:P82a_begin_of_the_begin ?begin }
  OPTIONAL { ?ts crm:P82b_end_of_the_end ?end }
  FILTER ((!BOUND(?begin) || ?begin <= "1950-01-01T00:00:00"^^xsd:dateTime) &&
          (!BOUND(?end)   || ?end   >= "1950-01-01T00:00:00"^^xsd:dateTime))
}
ORDER BY ?ownerLabel
"""


def ancestors(onto, cls):
    seen, todo = {cls}, [cls]
    while todo:
        c = todo.pop()
        for s in onto.objects(c, RDFS.subClassOf):
            if s not in seen:
                seen.add(s); todo.append(s)
    return seen


def check(data, onto, label):
    """Return a list of problems: undeclared terms and domain/range violations."""
    problems = []
    declared = set(onto.subjects())
    types = {}
    for s, o in data.subject_objects(RDF.type):
        types.setdefault(s, set()).update(ancestors(onto, o))
        if o not in declared:
            problems.append(f"undeclared class {o}")
    n = 0
    for s, p, o in data:
        if p == RDF.type or str(p).startswith(str(RDFS)):
            continue
        n += 1
        if p not in declared:
            problems.append(f"undeclared property {p}")
            continue
        for d in onto.objects(p, RDFS.domain):
            if d not in types.get(s, set()):
                problems.append(f"domain: {s} {p} (needs {d})")
        for r in onto.objects(p, RDFS.range):
            if isinstance(o, rdflib.Literal):
                continue
            if isinstance(o, URIRef) and o in declared and str(o).startswith(CRM) and str(r).endswith("E55_Type"):
                continue  # relation type given as the URI of a CRM property
            if r not in types.get(o, set()):
                problems.append(f"range: {s} {p} {o} (needs {r})")
    print(f"  {label}: {n} non-type triples checked, {len(problems)} problems")
    for pr in problems:
        print("   -", pr)
    return problems


def main():
    aaao_rdf, crm_rdf, files = sys.argv[1], sys.argv[2], sys.argv[3:]
    onto = rdflib.Graph()
    onto.parse(aaao_rdf)
    onto.parse(crm_rdf)
    print("Ontologies: CRMaaa 1.5.4.2 + CIDOC CRM 7.1.3")
    total_problems = 0
    for f in files:
        print(f"\n== {f}")
        data = rdflib.Graph(); data.parse(f, format="turtle")
        print(f"  {len(data)} triples")
        total_problems += len(check(data, onto, "AAAo data"))
        work = data + onto
        projected = rdflib.Graph()
        for t in work.query(PROJECTION):
            projected.add(t)
        print(f"  projection to CIDOC CRM: {len(projected)} distinct triples")
        for s, p, o in sorted(projected):
            print(f"    {s.n3(data.namespace_manager)} {p.n3(data.namespace_manager)} {o.n3(data.namespace_manager)}")
        # projected triples carry over the types of the original data
        proj_typed = projected + rdflib.Graph()
        for s, o in data.subject_objects(RDF.type):
            proj_typed.add((s, RDF.type, o))
        total_problems += len(check(proj_typed, onto, "projected CRM data"))
        if "totem" in f:
            print("  perspective query: owners of the pole on 1950-01-01, and for whom")
            for row in data.query(PERSPECTIVE):
                print(f"    {row.ownerLabel} (holds for {row.groupLabel})")
    print(f"\nTotal problems: {total_problems}")


if __name__ == "__main__":
    main()
