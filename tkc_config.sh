
#!/bin/bash
for i in $(seq ${1} ${2});
do
cluster=${3}${i}-c$i

echo $cluster
template=`cat "tkc.yaml" | sed "s/{{MYNS}}/${3}${i}/g" | sed "s/{{MYNAME}}/$cluster/g" | sed "s/{{VERSION}}/${4}/g"`
echo "$template" | kubectl apply -f - || echo "Command failed"
done

# ./tkc_config.sh 2 2 antrea-19-7-ns 1.19.7+vmware.1-tkg.1.fc82c41
