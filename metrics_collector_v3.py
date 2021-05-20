# Authors: savaliyaa

import os
import re
import xlwt
from xlwt import Workbook


def run_local_cmd(command):
    try:
        proc = os.popen(command).read().strip()
        return proc
    except Exception as e:
        print(e)


def get_sv_node_id():
    stdout = run_local_cmd("hostname")
    return stdout


def get_active_pods_name(ns):
    cmd = "kubectl get pods -n {ns} -o wide | grep -i {sv_node}".format(ns=ns,sv_node=current_sv_node)+" | awk '{print $1}'"
    pods = run_local_cmd(cmd).split("\n")
    print("Active PODS are : {}".format(pods))
    return pods


def retrieve_container_id(pod_name, ns):
    cmd = "kubectl get pod {} -n {}".format(pod_name,ns) + " -o jsonpath='{.status.containerStatuses[1].name}'"
    cname = run_local_cmd(cmd)
    if str(cname) == 'manager':
        id_cmd = "kubectl get pod {} -n {}".format(pod_name,ns) + " -o jsonpath='{.status.containerStatuses[1].containerID}'"
        cid = run_local_cmd(id_cmd).split("//")[-1]
        return cid, cname

    else:
        cmd = "kubectl get pod {} -n {}".format(pod_name, ns) + " -o jsonpath='{.status.containerStatuses[0].name}'"
        cname = run_local_cmd(cmd)
        if str(cname) == 'manager':
            id_cmd = "kubectl get pod {} -n {}".format(pod_name,ns) + " -o jsonpath='{.status.containerStatuses[0].containerID}'"
            cid = run_local_cmd(id_cmd).split("//")[-1]
            return cid, cname


def collect_container_metrics(id):

    cmd = "crictl stats {}".format(id)
    stdout = run_local_cmd(cmd)
    formatted_str = re.sub(' +', ' ', stdout)
    op_list = formatted_str.split()
    op_list.remove('%')
    print("collector metrics : {}".format(stdout))
    return op_list, stdout


def write_to_excel(metrics_list):

    wb = Workbook()
    # add_sheet is used to create sheet.
    sheet1 = wb.add_sheet('pod_metrics')
    row = 0
    columns = ['Namespace', 'Active_Pod', 'CPU(%)', 'Memory(MB)']
    for keys in range(0, 4):
        sheet1.write(row, keys, columns[keys])
    row += 1

    for metrics in metrics_list:
        col = 0
        for value in metrics.values():
            sheet1.write(row, col, value)
            col += 1
        row += 1

    wb.save('example.xls')


def main():
    metrics_list = []
    ns_list = ["vmware-system-tkg", "vmware-system-vmop", "vmware-system-capw", "vmware-system-nsop","vmware-system-netop"]
    print("Current SV Node hostname : {}".format(current_sv_node))
    if os.path.exists("resource_metrics.txt"):
        os.remove("resource_metrics.txt")

    for ns in ns_list:
        output = "\n==================================================   " + ns + \
                 "   ==================================================\n"

        active_pods = get_active_pods_name(ns)
        for pod in active_pods:
            metrics_dict = {}
            metrics_dict["Namespace"] = ns
            output += "\n Pod : " + pod + "   \n\n"
            metrics_dict["Active_Pod"] = pod
            cid, cname = retrieve_container_id(pod, ns)
            output += "container name  : " + cname + "     container id : " + cid
            metrics, metric_str = collect_container_metrics(cid)
            metrics_dict["CPU"] = metrics[6]
            metrics_dict["Memory"] = metrics[7][:-2]
            print("Metrics dict :{}".format(metrics_dict))
            metrics_list.append(metrics_dict)
            output += "\n" + metric_str + "\n"

        with open("resource_metrics.txt", 'a+', encoding='utf-8') as f:
            f.write(output + "\n\n")
    print("Metrics List :{}".format(metrics_list))
    write_to_excel(metrics_list)



if __name__ == "__main__":

    current_sv_node = get_sv_node_id()
    main()
    
 #Added logic for NCP pod
