#!/usr/bin/python

# Functionality to compare the installed openstack-tripleo-heat-templates
# version with the available diff versions and patch the appropriate diff.
# Since different openstack-tripleo-heat-templates can require different
# diff patches to be applied, this functionality takes care of hiding
# those details while applying the right patch. Currently all versions
# upto version openstack-tripleo-heat-templates-5.3.8-1 are handled.
# Later versions are not supported at this time.
#
# Usage: ./apply_patch.py
#

import rpm
import sys
import subprocess
from rpmUtils.miscutils import stringToVersion

VERSION_1_CHECK = "openstack-tripleo-heat-templates-5.3.0-4.el7ost.noarch"
VERSION_2_CHECK = "openstack-tripleo-heat-templates-5.3.8-1.el7ost.noarch"
PRE_VERSION_1_DIFF = "diff_OSPD10_5.2.0-15"
PRE_VERSION_2_DIFF = "diff_OSPD10_5.3.0-4"
POST_VERSION_2_DIFF = "diff_OSPD10_5.3.3-1"

if len(sys.argv) != 1:
    print "Usage: %s" % sys.argv[0]
    sys.exit(1)

def version_compare((e1, v1, r1), (e2, v2, r2)):
    return rpm.labelCompare((e1, v1, r1), (e2, v2, r2))

version = subprocess.check_output(['rpm', '-qa', 'openstack-tripleo-heat-templates'])

(e1, v1, r1) = stringToVersion(version)
(e2, v2, r2) = stringToVersion(VERSION_1_CHECK)
(e3, v3, r3) = stringToVersion(VERSION_2_CHECK)

args = "patch -p0 -N -d /usr/share"

# Compare versions
version_1_rc = version_compare((e1, v1, r1), (e2, v2, r2))
version_2_rc = version_compare((e1, v1, r1), (e3, v3, r3))
if version_1_rc < 0:
    args = args + " < " + PRE_VERSION_1_DIFF

elif version_1_rc >= 0 and version_2_rc < 0:
    args = args + " < " + PRE_VERSION_2_DIFF

elif version_2_rc == 0:
    args = args + " < " + POST_VERSION_2_DIFF

elif version_2_rc > 0:
    print "Not supported for %s" % version
    sys.exit(1)

# Apply appropriate diff
print "Applying: %s" % args
subprocess.call(args, shell=True)