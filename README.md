# Full documentation of ATEM protocol

Uses yaml to provide a standard way of describing the BMD Atem protocol.

The yaml files are generated into a set of python files that form an interface, providing developer friendly access to the API.

## Generating the interface

I'm using python 3.12, but I think anything above 3.6 should work.

Create a virtual envrionment with
`python -m venv env`. Then, in this environment install the latest version of PyYaml with `/env/bin/python -m pip install pyyaml` or similar.

To generate the interface run `python main.py`. The folder labelled `interface` will fill up with a bunch of python files. You can import these by using somethingl ike this: `import interface.common import ATEMEnumOrFunction`.

Editing any of the yaml files in the `protocol` folder requires generating the interface again to see the results.