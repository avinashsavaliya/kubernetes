
#!/bin/bash
for i in $(seq ${1} ${2});
do
cluster=${3}-c$i
echo $cluster
template=`cat "tkc.yaml" | sed "s/{{MYNS}}/${3}/g" | sed "s/{{MYNAME}}/$cluster/g" | sed "s/{{VERSION}}/${4}/g"`
echo "$template" | kubectl apply -f - || echo "Command failed"
done
