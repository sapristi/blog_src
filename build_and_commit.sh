#!/bin/bash


cd input/achem

for f in $(ls | grep  .org$)
do
    emacs $f --load ~/.emacs.d/init.el --batch -f org-md-export-to-markdown
    echo "exported " + $f + " as markdown" 
done
cd ../..

python2 poole.py --build
echo "built website"

git add -u
git commit -m "website source"
if [ -n $1 -a $1 = "push" ]
then 
    git push
fi

cd ..
cp -r ./blog_src/output/* ./sapristi.github.io/

cd sapristi.github.io

git add -u
git add *.html
git add achem/*.html
git commit -m "website"

if [ -n $1 -a $1 = "push" ]
then 
    git push
fi
