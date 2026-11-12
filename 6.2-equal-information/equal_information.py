"""Equal-information comparison of CIDOC CRM and AAAo (CRMaaa 1.5.4).

Encodes the same historical information in both ontologies, counts the
triples and new nodes each needs, and runs the 'which name on a date'
query against both, including a graph where the same title held in two
separate periods. Requires rdflib. Usage: python3 equal_information.py
The Turtle and SPARQL here are the listings printed in the paper
(Section "Representational Cost at Equal Information").
"""
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

PFX = """@prefix crm: <http://www.cidoc-crm.org/cidoc-crm/> .
@prefix aaao: <https://takin.solutions/ontologies/crmaaa/> .
@prefix ex:  <http://example.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""
# Shared by every encoding and excluded from the counts.
COMMON = """ex:painting a crm:E22_Human-Made_Object .
ex:title a crm:E41_Appellation ;
  crm:P190_has_symbolic_content "Young Woman with a Fan" .
ex:review2016 a crm:E31_Document .
ex:letter2019 a crm:E31_Document .
ex:decision a crm:E31_Document .
"""

def crm_state(i, a, b, d1, d2):
    """Two E13s: one standing for the beginning, one for the end.

    Each document that attests the state is evidence for both bounds (the
    name had begun by its date and had not yet ended), so it is attached to
    both events. Attaching it to one only would be an arbitrary choice and
    leaves documents that set neither bound without a place."""
    return f"""ex:aa{i}b a crm:E13_Attribute_Assignment ;
  crm:P140_assigned_attribute_to ex:painting ;
  crm:P141_assigned ex:title ;
  crm:P177_assigned_property_of_type crm:P1_is_identified_by ;
  crm:P2_has_type ex:name_begin ;
  crm:P4_has_time-span ex:ts{i}b .
ex:ts{i}b a crm:E52_Time-Span ;
  crm:P82b_end_of_the_end "{a}"^^xsd:date .
ex:aa{i}e a crm:E13_Attribute_Assignment ;
  crm:P140_assigned_attribute_to ex:painting ;
  crm:P141_assigned ex:title ;
  crm:P177_assigned_property_of_type crm:P1_is_identified_by ;
  crm:P2_has_type ex:name_end ;
  crm:P4_has_time-span ex:ts{i}e .
ex:ts{i}e a crm:E52_Time-Span ;
  crm:P82a_begin_of_the_begin "{b}"^^xsd:date .
ex:aa{i}b crm:P67i_is_referred_to_by {d1} , {d2} .
ex:aa{i}e crm:P67i_is_referred_to_by {d1} , {d2} .
"""

def aaao_state(i, a, b, d1, d2):
    """One ZE2 Appellative Status with the attested minimum extent (P81)."""
    return f"""ex:status{i} a aaao:ZE2_Appellative_Status ;
  aaao:ZP5_has_appellative_subject ex:painting ;
  aaao:ZP6_ascribes_appellation ex:title ;
  crm:P4_has_time-span ex:ts{i} .
ex:ts{i} a crm:E52_Time-Span ;
  crm:P81a_end_of_the_begin "{a}"^^xsd:date ;
  crm:P81b_begin_of_the_end "{b}"^^xsd:date .
ex:status{i} crm:P67i_is_referred_to_by {d1} , {d2} .
"""

CASES = {
    "A. state attested between two dates, two documents": (
        crm_state(1, "2016-01-01", "2019-12-31", "ex:review2016", "ex:letter2019"),
        aaao_state(1, "2016-01-01", "2019-12-31", "ex:review2016", "ex:letter2019")),
    "B. state attested from a date on, one document": (
        """ex:aa1b a crm:E13_Attribute_Assignment ;
  crm:P140_assigned_attribute_to ex:painting ; crm:P141_assigned ex:title ;
  crm:P177_assigned_property_of_type crm:P1_is_identified_by ;
  crm:P2_has_type ex:name_begin ; crm:P4_has_time-span ex:ts1b .
ex:ts1b a crm:E52_Time-Span ; crm:P82b_end_of_the_end "2016-01-01"^^xsd:date .
ex:aa1b crm:P67i_is_referred_to_by ex:review2016 .""",
        """ex:status1 a aaao:ZE2_Appellative_Status ;
  aaao:ZP5_has_appellative_subject ex:painting ; aaao:ZP6_ascribes_appellation ex:title ;
  crm:P4_has_time-span ex:ts1 .
ex:ts1 a crm:E52_Time-Span ; crm:P81a_end_of_the_begin "2016-01-01"^^xsd:date .
ex:status1 crm:P67i_is_referred_to_by ex:review2016 ."""),
    "C. naming act documented (AAAo also records the state it initiated)": (
        """ex:renaming a crm:E13_Attribute_Assignment ;
  crm:P140_assigned_attribute_to ex:painting ; crm:P141_assigned ex:title ;
  crm:P177_assigned_property_of_type crm:P1_is_identified_by ;
  crm:P4_has_time-span ex:tsr .
ex:tsr a crm:E52_Time-Span ; crm:P82a_begin_of_the_begin "2015-06-01"^^xsd:date ;
  crm:P82b_end_of_the_end "2015-06-30"^^xsd:date .
ex:renaming crm:P67i_is_referred_to_by ex:decision .""",
        """ex:renaming a aaao:ZE19_Naming ;
  crm:P140_assigned_attribute_to ex:painting ; crm:P141_assigned ex:title ;
  crm:P177_assigned_property_of_type crm:P1_is_identified_by ;
  crm:P4_has_time-span ex:tsr ;
  aaao:ZP42_intentionally_initiated ex:status1 .
ex:tsr a crm:E52_Time-Span ; crm:P82a_begin_of_the_begin "2015-06-01"^^xsd:date ;
  crm:P82b_end_of_the_end "2015-06-30"^^xsd:date .
ex:renaming crm:P67i_is_referred_to_by ex:decision .
ex:status1 a aaao:ZE2_Appellative_Status ;
  aaao:ZP5_has_appellative_subject ex:painting ; aaao:ZP6_ascribes_appellation ex:title ;
  crm:P4_has_time-span ex:ts1 .
ex:ts1 a crm:E52_Time-Span ; crm:P81a_end_of_the_begin "2015-06-30"^^xsd:date ."""),
}

Q_CRM = """PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX ex:  <http://example.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?name WHERE {
  ?b crm:P140_assigned_attribute_to ex:painting ;
     crm:P141_assigned ?name ;
     crm:P177_assigned_property_of_type crm:P1_is_identified_by ;
     crm:P2_has_type ex:name_begin ;
     crm:P4_has_time-span/crm:P82b_end_of_the_end ?from .
  ?e crm:P140_assigned_attribute_to ex:painting ;
     crm:P141_assigned ?name ;
     crm:P177_assigned_property_of_type crm:P1_is_identified_by ;
     crm:P2_has_type ex:name_end ;
     crm:P4_has_time-span/crm:P82a_begin_of_the_begin ?until .
  FILTER (?from <= "DATE"^^xsd:date && ?until >= "DATE"^^xsd:date)
}"""

Q_AAAO = """PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX aaao: <https://takin.solutions/ontologies/crmaaa/>
PREFIX ex:  <http://example.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?name WHERE {
  ?s aaao:ZP5_has_appellative_subject ex:painting ;
     aaao:ZP6_ascribes_appellation ?name ;
     crm:P4_has_time-span ?t .
  ?t crm:P81a_end_of_the_begin ?from ;
     crm:P81b_begin_of_the_end ?until .
  FILTER (?from <= "DATE"^^xsd:date && ?until >= "DATE"^^xsd:date)
}"""


def graph(body=""):
    g = Graph()
    g.parse(data=PFX + COMMON + body, format="turtle")
    return g


def patterns(q):
    """Triple patterns in the query, property paths expanded."""
    n = 0
    def walk(x):
        nonlocal n
        if getattr(x, "name", None) == "BGP":
            n += len(x.triples)
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, (list, tuple)):
            for v in x:
                walk(v)
    walk(prepareQuery(q.replace("DATE", "2000-01-01")).algebra)
    return n + q.count("/crm:")  # each two-step path is one extra pattern


def ask(g, q, date):
    return sorted(str(r.name).rsplit("/", 1)[-1] for r in g.query(q.replace("DATE", date)))


if __name__ == "__main__":
    base = graph()
    nb, base_nodes = len(base), set(base.subjects())
    print("1. Size at equal information (beyond object, appellation, documents)")
    for case, (crm, aaao) in CASES.items():
        out = []
        for body in (crm, aaao):
            g = graph(body)
            out.append((len(g) - nb, len(set(g.subjects()) - base_nodes)))
        print(f"  {case}\n    CIDOC CRM: {out[0][0]} triples, {out[0][1]} nodes"
              f" | AAAo: {out[1][0]} triples, {out[1][1]} nodes")

    print("\n   General case: dated state attested by k documents")
    for k in range(1, 6):
        docs = " , ".join(f"ex:doc{j}" for j in range(k))
        crm_k = crm_state(9, "2016-01-01", "2019-12-31", "ex:review2016", "ex:letter2019")
        crm_k = crm_k.replace("ex:review2016 , ex:letter2019", docs)
        aaao_k = aaao_state(9, "2016-01-01", "2019-12-31", "ex:review2016", "ex:letter2019")
        aaao_k = aaao_k.split("ex:status9 crm:P67i")[0] + f"ex:status9 crm:P67i_is_referred_to_by {docs} .\n"
        c, a = len(graph(crm_k)) - nb, len(graph(aaao_k)) - nb
        assert c == 16 + 2 * k and a == 7 + k, (k, c, a)
        print(f"    k={k}: CIDOC CRM {c} (16+2k) | AAAo {a} (7+k) | ratio {a / c:.2f}")

    print("\n2. Query 'names on a date'")
    print(f"  triple patterns: CIDOC CRM {patterns(Q_CRM)}, AAAo {patterns(Q_AAAO)}")
    one_crm, one_aaao = CASES["A. state attested between two dates, two documents"]
    print(f"  one period (2016-2019), date 2017-06-01: "
          f"CRM {ask(graph(one_crm), Q_CRM, '2017-06-01')}, "
          f"AAAo {ask(graph(one_aaao), Q_AAAO, '2017-06-01')}")
    two_crm = graph(one_crm + crm_state(2, "1950-01-01", "1960-12-31", "ex:review2016", "ex:letter2019"))
    two_aaao = graph(one_aaao + aaao_state(2, "1950-01-01", "1960-12-31", "ex:review2016", "ex:letter2019"))
    for d in ("1990-06-01", "2017-06-01"):
        print(f"  two periods (1950-1960, 2016-2019), date {d}: "
              f"CRM {ask(two_crm, Q_CRM, d)}, AAAo {ask(two_aaao, Q_AAAO, d)}")
