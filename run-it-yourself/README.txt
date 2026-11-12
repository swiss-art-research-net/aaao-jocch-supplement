Run the Section 6.1 queries yourself
====================================

Nothing to install. You paste one data file and one query into an online
SPARQL playground and press Run.

Files in this folder
--------------------
data-isabella.ttl      Use case 1 (the painting Isabella)
data-totem.ttl         Use case 2 (the G'psgolox Totem Pole)
data-brandenburg.ttl   Use case 3 (the Brandenburg Gate)
    Each is the use-case file from the folder above, unchanged, followed by
    the subproperty hierarchy of AAAo (below the dashed line). The projection
    query needs that hierarchy to know that ZP5 is a subproperty of ZP1, and
    so on. The hierarchy is also given on its own in aaao-subproperties.ttl.

query-projection.rq    Listing 4 of the paper, with the four PREFIX lines added
query-perspective.rq   Listing 5 of the paper, with the four PREFIX lines added

expected-results.txt   What each query returned on 12 Nov 2026 (CRMaaa 1.5.4.2)

Steps
-----
1. Open a playground in your browser:
      https://rdfplayground.dcc.uchile.cl/        (University of Chile)
   or https://antvaset.pages.dev/sparql-playground
   The second one runs entirely in your browser.
2. Open data-isabella.ttl in a text editor, copy everything, and paste it
   into the RDF data box, replacing what is there. Choose Turtle as the
   format if asked.
3. Open query-projection.rq, copy everything, paste it into the SPARQL
   query box, and run it.
4. Compare the result with expected-results.txt: three statements, each
   saying the painting "is identified by" one of its three names.
5. Repeat steps 2 to 4 with data-totem.ttl (two statements) and
   data-brandenburg.ttl (three statements). That makes the eight statements
   reported in Section 6.1.
6. With data-totem.ttl still loaded, run query-perspective.rq. It should
   return two rows: Haisla people (for the Haisla people) and Olof Hanson
   (for the Canadian government).
