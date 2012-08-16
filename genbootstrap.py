#!/usr/bin/env python2

import virtualenv

f = open("bootstrap.py", "w")
bootstrap = virtualenv.create_bootstrap_script("print \"----- Preparing test environment -----\"")
f.write(bootstrap)
f.close()
