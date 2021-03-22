#!/bin/bash
for i in $(seq ${1} ${2});
do
sv_name=lbsvc-$i
echo $sv_name
lb=`cat "lb.yaml" | sed "s/{{sv_name}}/$sv_name/g"`
echo "$lb" | kubectl --kubeconfig ${3} apply -f - || echo "Command failed"
done
