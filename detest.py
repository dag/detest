# encoding: utf-8
from __future__ import unicode_literals


if __name__ == '__main__':
    from _detest.environment import Environment
    Environment.main()


exports = dict(
    capturing = 'ExceptionCapture OutputCapture',
    config = 'Config',
    diffing = 'TreeDiffer JSONDiffer PrettyDiffer YAMLDiffer DataDiffer',
    environment = 'Environment',
    expecting = 'MustRaise',
    importing = 'BlockingImporter AssertionLoggingImporter',
    representing = 'AttributeRepr TreeRepr',
    running = 'Runner TerminalRunner',
    suite = 'ConfigSuite Suite fixture generator test',
)


defs = {}
for module, members in exports.iteritems():
    for member in members.split():
        defs[member] = ''.join(['_detest.', module, ':', member])


defs.update(
    paver = dict(
        auto = '_detest.paver:auto',
        test = '_detest.paver:test',
    )
)


import apipkg
apipkg.initpkg(__name__, defs)
