# pkgutil shenanigans to make python load wgse.third_party from site-packages
#
# tl;dr wgse.third_party contains some executables for windows and is installed
# from another pypi package (wgse-ng-3rd-party).
# When importing wgse.third_party from any files inside WGSE, python will expect
# to find wgse.third_party INSIDE this package and not in site-packages. Code 
# below will make this package a "Native Namespace Package" (PEP 420) and will 
# make it possible to have different packages contributing to the same namespace 
# (wgse). Only downside is the the IDE won't recognize wgse.third_party, which is
# not a big deal as it doesn't contain any python code.

from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)