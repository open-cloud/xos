SLICE=princeton_planetstack
HOST=node54.princeton.vicci.org
#SLICE=service_vini
#HOST=bilby.cs.princeton.edu
rsync -avz --exclude "__history" --exclude "*~" -e ssh . $SLICE@$HOST:/opt/planetstack/core/xoslib/

