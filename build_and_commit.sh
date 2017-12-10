#/bin/bash




cd gen/input/achem

for f in $(ls | grep  .org$)
do
    emacs $f --load ~/.emacs --batch -f org-md-export-to-markdown
    echo "exported " + $f + " as markdown" 
done
cd ../..

poole.py --build
echo "built website"

cd ..
cp -r gen/output/* .



git add -u
git add *.html
git add achem/*.html
git commit -m "website"

if [ -n $1 -a $1 = "push" ]
then 
    git push
fi
