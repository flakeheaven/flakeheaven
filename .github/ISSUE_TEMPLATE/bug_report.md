---
name: Bug report
about: Create a report to help us improve
title: 'BUG:'
labels: bug, triage
assignees: ''

---

**Checklist**
<!--
After checking this list, maybe a new bug issue is not the best location for this.

Feedback is always appreciated!
Maybe its better suited as a docs improvement?
or just a discussion on discord...
-->

* [ ] Same issue occurs when reproducing the MWE below: new virtualenv, clean folder, minimal additional libs, etc.
* [ ] Same issue occurs when running without cache (eg by setting the env var `FLAKEHEAVEN_CACHE_TIMEOUT=0`)

**Bug Description**
<!--A clear and concise description of what the bug is.-->

**Expected behavior**
<!--
A clear and concise description of what you expected to happen.

If it applies, reference to what happens in plain flake8 usually help.
-->

**Bug Repro**

1. OS, arch
2. `python --version`
3. `pyproject.toml` (and / or all other config files that apply, eg `.pylintrc`, stc)
4. `pip freeze`
5.  `flakeheaven plugins`
6. Contents of any additional files (eg sample `.py` file(s) to be linted)
7. Any additional env vars setup
8. [If available] contents of `flakeheaven config -vvv`

Steps to reproduce the behavior:
<!-- cli and env setup.-->
1. run `flakeheaven ...`
2. ...


**Additional context**
<!--Add any other context about the problem here, if it applies. Otherwise, you can just delete this section.-->
