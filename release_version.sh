git commit --all -m "Version bump" && git tag v`cat main.py | grep "VERSION =" | cut -d' ' -f3 | cut -d'"' -f2` && git push --tags
