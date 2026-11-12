"""Competency questions for the AAAo core (Section 6.4 of the AAAo paper).

Each competency question (CQ) is one generic SPARQL query. Because every
status class specializes ZP1 (subject), ZP2 (target) and ZP3 (relation), the
same query answers the question for names, owners and meanings alike. Each CQ
is run over the three use-case files (AAAo data, with the ontology loaded so
that subproperty paths can be followed) and, for comparison, over the CIDOC
CRM statements the same data implies: the projection of Section 6.2, with
documents attached to what they can refer to in CIDOC CRM alone (the object).

Usage: python3 competency_questions.py AAAO_RDF CRM_RDF isabella.ttl totem.ttl brandenburg.ttl > cq-report.txt
"""
import os
import sys
import rdflib
import pyoxigraph
from rdflib import URIRef, Literal, XSD

AAA = "https://takin.solutions/ontologies/crmaaa/"
CRM = "http://www.cidoc-crm.org/cidoc-crm/"

PREFIXES = f"""PREFIX aaao: <{AAA}>
PREFIX crm: <{CRM}>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""

# The generic institutional fact pattern, reused by every CQ.
PATTERN = """
  ?status ?sp ?entity ; ?tp ?value ; ?rp ?relation .
  ?sp rdfs:subPropertyOf* aaao:ZP1_has_intentional_subject .
  ?tp rdfs:subPropertyOf* aaao:ZP2_ascribes_intentional_target .
  ?rp rdfs:subPropertyOf* aaao:ZP3_ascribes_intentional_relation .
"""

CQ = {
 "CQ1": ("What [relation] did [entity] have at [date], and for which group?",
  PREFIXES + """SELECT ?relation ?value ?group WHERE {""" + PATTERN + """
  OPTIONAL { ?status aaao:ZP4_holds_for ?group }
  OPTIONAL { ?status crm:P4_has_time-span ?ts .
             OPTIONAL { ?ts crm:P82a_begin_of_the_begin ?b }
             OPTIONAL { ?ts crm:P82b_end_of_the_end ?e } }
  FILTER ((!BOUND(?b) || ?b <= ?date) && (!BOUND(?e) || ?e >= ?date))
}"""),
 "CQ2": ("For [entity], which statuses conflict: different values held for different groups over overlapping periods?",
  PREFIXES + """SELECT ?value1 ?group1 ?value2 ?group2 ?from ?to WHERE {
  ?s1 ?sp1 ?entity ; ?tp1 ?value1 ; ?rp1 ?relation ; aaao:ZP4_holds_for ?group1 .
  ?s2 ?sp2 ?entity ; ?tp2 ?value2 ; ?rp2 ?relation ; aaao:ZP4_holds_for ?group2 .
  ?sp1 rdfs:subPropertyOf* aaao:ZP1_has_intentional_subject .
  ?sp2 rdfs:subPropertyOf* aaao:ZP1_has_intentional_subject .
  ?tp1 rdfs:subPropertyOf* aaao:ZP2_ascribes_intentional_target .
  ?tp2 rdfs:subPropertyOf* aaao:ZP2_ascribes_intentional_target .
  ?rp1 rdfs:subPropertyOf* aaao:ZP3_ascribes_intentional_relation .
  ?rp2 rdfs:subPropertyOf* aaao:ZP3_ascribes_intentional_relation .
  FILTER (STR(?s1) < STR(?s2) && ?value1 != ?value2 && ?group1 != ?group2)
  ?s1 crm:P4_has_time-span ?t1 . ?s2 crm:P4_has_time-span ?t2 .
  OPTIONAL { ?t1 crm:P82a_begin_of_the_begin ?b1 } OPTIONAL { ?t1 crm:P82b_end_of_the_end ?e1 }
  OPTIONAL { ?t2 crm:P82a_begin_of_the_begin ?b2 } OPTIONAL { ?t2 crm:P82b_end_of_the_end ?e2 }
  FILTER ((!BOUND(?b1) || !BOUND(?e2) || ?b1 <= ?e2) && (!BOUND(?b2) || !BOUND(?e1) || ?b2 <= ?e1))
  BIND (IF(!BOUND(?b1), ?b2, IF(!BOUND(?b2), ?b1, IF(?b1 > ?b2, ?b1, ?b2))) AS ?from)
  BIND (IF(!BOUND(?e1), ?e2, IF(!BOUND(?e2), ?e1, IF(?e1 < ?e2, ?e1, ?e2))) AS ?to)
}"""),
 "CQ3": ("Which act brought [status] about or ended it, who performed it, and under which procedure?",
  PREFIXES + """SELECT ?value ?effect ?act ?actor ?procedure WHERE {""" + PATTERN + """
  { ?act aaao:ZP42_intentionally_initiated ?status . BIND("initiated" AS ?effect) }
  UNION
  { ?act aaao:ZP52_intentionally_terminated ?status . BIND("terminated" AS ?effect) }
  OPTIONAL { ?act crm:P14_carried_out_by ?actor }
  OPTIONAL { ?act aaao:ZP40_performed ?procedure }
}"""),
 "CQ4": ("Which statuses of [entity] have no known founding act (states attested without an attested event)?",
  PREFIXES + """SELECT ?relation ?value WHERE {""" + PATTERN + """
  FILTER NOT EXISTS { ?act aaao:ZP42_intentionally_initiated ?status }
}"""),
 "CQ5": ("Which documents attest [status]?",
  PREFIXES + """SELECT ?value ?group ?document WHERE {""" + PATTERN + """
  ?status crm:P67i_is_referred_to_by ?document .
  OPTIONAL { ?status aaao:ZP4_holds_for ?group }
}"""),
}

# Plain CIDOC CRM versions of the same questions, over the projected data.
CRM_PROPS = "crm:P1_is_identified_by crm:P51_has_former_or_current_owner crm:P129i_is_subject_of crm:P129_is_about"
CRM_CQ = {
 "CQ1": PREFIXES + f"""SELECT ?relation ?value WHERE {{
  VALUES ?relation {{ {CRM_PROPS} }}
  ?entity ?relation ?value .
}}""",
 "CQ5": PREFIXES + """SELECT ?document WHERE { ?entity crm:P67i_is_referred_to_by ?document }""",
}
# CQ2-CQ4 have no CIDOC CRM counterpart: a property instance has no group,
# no time-span and no founding act that a query could ask about.

CASES = [
  # file, entity, date for CQ1
  ("isabella.ttl", "https://example.org/aaao/isabella/painting", "2017-06-01T00:00:00"),
  ("totem.ttl", "https://example.org/aaao/totem/pole", "1950-01-01T00:00:00"),
  ("brandenburg.ttl", "https://example.org/aaao/brandenburg/vision", "1975-01-01T00:00:00"),
]

PROJECTION = PREFIXES + """CONSTRUCT { ?subject ?crmProperty ?target } WHERE {
  ?fact ?sp ?subject ; ?tp ?target ; ?rp ?crmProperty .
  ?sp rdfs:subPropertyOf* aaao:ZP1_has_intentional_subject .
  ?tp rdfs:subPropertyOf* aaao:ZP2_ascribes_intentional_target .
  ?rp rdfs:subPropertyOf* aaao:ZP3_ascribes_intentional_relation .
}"""
DOCS_TO_SUBJECT = PREFIXES + """CONSTRUCT { ?subject crm:P67i_is_referred_to_by ?doc } WHERE {
  ?fact ?sp ?subject ; crm:P67i_is_referred_to_by ?doc .
  ?sp rdfs:subPropertyOf* aaao:ZP1_has_intentional_subject .
}"""


def to_rdflib(t):
    if t is None:
        return None
    if isinstance(t, pyoxigraph.NamedNode):
        return URIRef(t.value)
    if isinstance(t, pyoxigraph.Literal):
        return Literal(t.value, datatype=URIRef(t.datatype.value) if t.datatype else None)
    return rdflib.BNode(t.value)


def short(g, v):
    if v is None:
        return "-"
    if isinstance(v, Literal):
        return str(v)[:10] if v.datatype == XSD.dateTime else str(v)
    lab = g.value(v, rdflib.RDFS.label) or g.value(v, URIRef(CRM + "P190_has_symbolic_content"))
    return str(lab) if lab else v.n3(g.namespace_manager)


def store_of(g):
    st = pyoxigraph.Store()
    st.load(g.serialize(format="nt").encode(), format=pyoxigraph.RdfFormat.N_TRIPLES)
    return st


def run(st, labels, q, entity, date):
    values = f'VALUES (?entity ?date) {{ (<{entity}> "{date}"^^xsd:dateTime) }}'
    k = q.index("WHERE {") + len("WHERE {")
    res = st.query(q[:k] + "\n  " + values + q[k:])
    out = []
    for sol in res:
        out.append([short(labels, to_rdflib(sol[v])) for v in res.variables])
    return sorted(out)  # fixed order, so re-runs match the report line for line


def main():
    aaao_rdf, crm_rdf, files = sys.argv[1], sys.argv[2], sys.argv[3:]
    onto = rdflib.Graph()
    onto.parse(aaao_rdf); onto.parse(crm_rdf)
    print("Competency questions over the use-case data (CRMaaa 1.5.4.2 + CIDOC CRM 7.1.3; engine: Oxigraph)\n")
    given = {os.path.basename(x): x for x in files}
    for name, ent, date in CASES:
        f = given.get(name, name)  # use the path given on the command line
        data = rdflib.Graph(); data.parse(f, format="turtle")
        work = data + onto
        work.namespace_manager = data.namespace_manager
        aaao_store = store_of(work)
        crm = rdflib.Graph()
        for r in aaao_store.query(PROJECTION):
            crm.add(tuple(to_rdflib(x) for x in r))
        for r in aaao_store.query(DOCS_TO_SUBJECT):
            crm.add(tuple(to_rdflib(x) for x in r))
        for prop in (rdflib.RDFS.label, URIRef(CRM + "P190_has_symbolic_content"), URIRef(CRM + "P65_shows_visual_item")):
            for t in data.triples((None, prop, None)): crm.add(t)
        crm_store = store_of(crm)
        entity = ent
        print(f"=== {name}  (entity: {short(data, URIRef(entity))}; date for CQ1: {date[:10]})")
        for k, (text, q) in CQ.items():
            print(f"  {k}: {text}")
            rows = run(aaao_store, data, q, entity, date)
            print(f"    AAAo ({len(rows)} rows)")
            for r in rows:
                print("      " + " | ".join(r))
            if k in CRM_CQ:
                rows = run(crm_store, data, CRM_CQ[k], entity, date)
                print(f"    CIDOC CRM alone ({len(rows)} rows)")
                for r in rows:
                    print("      " + " | ".join(r))
            else:
                print("    CIDOC CRM alone: not expressible (no group, time-span or founding act on a property instance)")
        print()


if __name__ == "__main__":
    main()
