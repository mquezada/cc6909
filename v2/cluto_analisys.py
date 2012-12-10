import fileinput
import re

"""
command:


FILENAME=dvorak.dat

for i in {2..30..1}
do
    ./vcluster ~/git/cc6909/v2/data/$FILENAME -clmethod=direct -sim=cos -crfun=i2 -colmodel=idf $i | python ~/git/cc6909/v2/cluto_analisys.py
done

rm -rf /home/mquezada/git/cc6909/v2/data/$FILENAME.clustering.*

"""

get = False
read = False

isim = 0
esim = 0
csize = 0
k = 0
K = 0

for line in fileinput.input():
    if read and k > 0:
        row = line.split()
        csize += int(row[1])
        isim += float(row[2])
        esim += float(row[4])
        k -= 1

    if not read and get:
        read = True

    if not get and line.startswith('cid'):
        get = True

    if re.match('\d+-way clustering', line):
        k = int(re.findall('\d+', line)[0])
        K = k

print '\t'.join(map(str, [K, isim/K, esim/K, isim/esim]))