# TrustLab Host

This is the host library of the TrustLab aTLAS and thus a submodule of the TrustLab
(https://gitlab.hrz.tu-chemnitz.de/vsr/phd/siegert/trustlab)


## Assumptions
Here are some assumptions which are assumed by the code.

### Connectors
- The connectors are assumed to be placed in ``connectors`` directory.
- Every connector has its own file, which is named like the class but all lower case and seperated with ``_`` where camel case inserted capital chars.
- A new connector class should be inserted in the choices of the connectors argument in supervisor's argparse.


