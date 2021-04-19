# TrustLab Host

This is the host library of the TrustLab aTLAS and thus a submodule of the TrustLab
(https://gitlab.hrz.tu-chemnitz.de/vsr/phd/siegert/trustlab)

## Setup

1. Ensure Setup of aTLAS. (https://gitlab.hrz.tu-chemnitz.de/vsr/phd/siegert/trustlab)

2. Clone submodule to host where required if not on same machine as aTLAS.

3. Setup pipenv in submodule root:
    ```bash
    pipenv install
    ```
   **OR** install all requirements in your virtual environment for this submodule with:
   ```bash
    pip install -r requirements.pip --exists-action w
    ```

## Run

1. Ensure Running of aTLAS. (https://gitlab.hrz.tu-chemnitz.de/vsr/phd/siegert/trustlab)

2. Start supervisor, e.g. with a maximum capacity of 10 agents:
    ```bash
    python3 supervisors.py 10
    ```
   For more specific preferences conduct the help of `supervisors.py`:
   ```bash
    python3 supervisors.py -h
    ```

## Assumptions
Here are some assumptions which are assumed by the code.

### Connectors
- The connectors are assumed to be placed in ``connectors`` directory.
- Every connector has its own file, which is named like the class but all lower case and seperated with ``_`` where camel case inserted capital chars.
- A new connector class should be inserted in the choices of the connectors argument in supervisor's argparse.

## Links To Know

* aTLAS Project page \
https://vsr.informatik.tu-chemnitz.de/projects/2020/atlas/

* Latest online prototype \
https://vsr.informatik.tu-chemnitz.de/projects/2020/atlas/demo/

* aTLAS main repository \
https://gitlab.hrz.tu-chemnitz.de/vsr/phd/siegert/trustlab
