# coding=utf-8
from Aurora.Mysql import Aurora
import time

"""
AWS Regions
('N. Virginia', 'us-east-1'),
('Ohio', 'us-east-2'),
('N. California', 'us-west-1'),
('Oregon', 'us-west-2'),
('Cape Town', 'af-south-1'),
('Hong Kong', 'ap-east-1'),
('Mumbai', 'ap-south-1'),
('Osaka', 'ap-northeast-3'),
('Seoul', 'ap-northeast-2'),
('Singapore', 'ap-southeast-1'),
('Sydney', 'ap-southeast-2'),
('Tokyo', 'ap-northeast-1'),
('Central', 'ca-central-1'),
('Frankfurt', 'eu-central-1'),
('Ireland', 'eu-west-1'),
('London', 'eu-west-2'),
('Milan', 'eu-south-1'),
('Paris', 'eu-west-3'),
('Stockholm', 'eu-north-1'),
('Bahrain', 'me-south-1'),
('São Paulo', 'sa-east-1'),
"""

"""
scaling target instance_id: instance_class dict
"""
scaling_dict = {}
scaling_dict["read-replica-1"] = "db.r5.16xlarge"


if __name__ == "__main__":
    aurora = Aurora(
        aws_region='us-east-1',
        cluster_id='aurora-common-auroracluster',
    )

    cluster_res = aurora.get_cluster_info()
    
    cluster_members = cluster_res["DBClusters"][0]["DBClusterMembers"]
    for cluster_member in cluster_members:
        response = aurora.get_describe_db_instances(cluster_member["DBInstanceIdentifier"])
        instance_id = response["DBInstances"][0]["DBInstanceIdentifier"]
        cluster_role = "Reader"
        if cluster_member["IsClusterWriter"]:
            cluster_role = "Writer"
            # DB Parameter group
            db_parameter_group = response["DBInstances"][0]["DBParameterGroups"][0]["DBParameterGroupName"]
        print_row = "{0}: [{1}] ".format(cluster_role, instance_id)
        print_row += "DBInstanceStatus [{0}] ".format(response["DBInstances"][0]["DBInstanceStatus"])
        print_row += "DBInstanceClass [{0}".format(response["DBInstances"][0]["DBInstanceClass"])
        if scaling_dict.get(instance_id):
            print_row += " -> {0}]".format(scaling_dict.get(instance_id))
            scaling_param = Aurora.get_max_connections(scaling_dict.get(instance_id))
        else:
            print_row += "]"

        print(print_row)
    print("____________________")

    # 변경 내용 중 Writer 가 포함된 경우 Parameter 중 max_connections, max_user_connections Class 에 맞춰서 수정.
    if db_parameter_group:
        print("DB Parameter change >>> {0}".format(scaling_param))
        aurora.set_db_connections(
            db_param_id=db_parameter_group,
            max_conn=scaling_param[0],
            max_user_conn=scaling_param[1],
        )
        # 변경 후 Cluster 상태 확인.
        aurora.get_cluster_available_check()
    
    # Reader scaling-up
    # failover_target_id
    failover_target_id = None
    for cluster_member in cluster_members:
        instance_id = cluster_member["DBInstanceIdentifier"]
        
        if cluster_member["IsClusterWriter"] == False:
            if scaling_dict.get(instance_id):
                print("____________________")
                target_class = scaling_dict.get(instance_id)
                info_comm = "{0} Scaling: ".format(instance_id)
                info_comm += "[{0}]".format(target_class)
                print(info_comm)
                aurora.set_modify_db_instance(instance_id, target_class)
                # Failover target id
                if not failover_target_id:
                    failover_target_id = instance_id
    
    aurora.get_cluster_available_check()

    if failover_target_id:
        print("Failover Begin: [{0}]".format(time.strftime('%c', time.localtime(time.time()))))
        aurora.set_failover_db_cluster(failover_target_id)
        aurora.get_cluster_available_check()
        print("Failover Completed!: [{0}]".format(time.strftime('%c', time.localtime(time.time()))))
