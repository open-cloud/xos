# cleanup phase
for f in samples/*.yaml; do
   echo --------------------------------------------------
   echo destroy $f
   python ./destroy.py scott@onlab.us $f
done

for f in samples/*.yaml; do
   echo --------------------------------------------------
   echo run $f
   python ./run.py scott@onlab.us $f
   echo destroy $f
   python ./destroy.py scott@onlab.us $f
done
