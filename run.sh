template=$(
    cat <<-END
---
title: FAST Time Table (\today{})
geometry: margin=2cm
header-includes:
    - \usepackage{setspace}
    - \doublespacing
    - \usepackage{lineno}
---

END
)

path="course_files/md"

cwd=$(pwd)

$(rm -rf $path/*.md $path/*.pdf)

python reader.py

cd $path

echo "$template" >timetable.md

cat *.md >> timetable.md

pandoc -s -o timetable.pdf timetable.md -V papersize:a4

setsid xdg-open timetable.pdf
