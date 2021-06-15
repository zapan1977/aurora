# coding=utf-8
import boto3
import time

class Aurora:
    def __init__(self, **kwargs):
        """
        Default valuabale define.
        aws_region reguired. (Defalut: Seoul)
        cluster_id (Default: )
        """
        if kwargs.get('aws_region'):
            self.aws_region = kwargs['aws_region']
        else:
            self.aws_region = "ap-northeast-2"

        self.client = boto3.client(
            'rds',
            region_name=self.aws_region
        )
        self.cluster_id = kwargs.get('cluster_id')

    def get_cluster_info(self, c_id=None):
        if c_id:
            response = self.client.describe_db_clusters(
                DBClusterIdentifier=c_id
            )
        elif self.cluster_id:
            response = self.client.describe_db_clusters(
                DBClusterIdentifier=self.cluster_id
            )
        else:
            response = self.client.describe_db_clusters()
        return response

    def get_describe_db_instances(self, id):
        return self.client.describe_db_instances( DBInstanceIdentifier=id )
    
    def get_cluster_available_check(self):
        cluster_res = self.get_cluster_info()
        cluster_members = cluster_res["DBClusters"][0]["DBClusterMembers"]
        time.sleep(60)
        status_check = 0
        while status_check < 100:
            is_available = True
            for cluster_member in cluster_members:
                instance_id = cluster_member["DBInstanceIdentifier"]
                instance_res = self.get_describe_db_instances(instance_id)
                db_ins_status = instance_res["DBInstances"][0]["DBInstanceStatus"]
                cluster_role = "Reader"
                if cluster_member["IsClusterWriter"]:
                    cluster_role = "Writer"
                print_row = "[{0}] [{1}]".format(cluster_role, instance_id)
                print_row += " ({0})".format(db_ins_status)
                print_row += " ({0})".format(instance_res["DBInstances"][0]["DBInstanceClass"])
                print_row += " [{0}]".format(time.strftime('%c', time.localtime(time.time())))
                print(print_row)
                if db_ins_status != "available":
                    is_available = False
            if is_available:
                break
            time.sleep(30)
            status_check = status_check + 1
        return True
    
    def set_db_connections(self, **kwargs):
        db_param_id = kwargs.get("db_param_id")
        max_conn = kwargs.get("max_conn")
        max_user_conn = kwargs.get("max_user_conn")
        self.client.modify_db_parameter_group(
            DBParameterGroupName=db_param_id,
            Parameters=[
                {
                    'ParameterName': 'max_connections',
                    'ParameterValue': '{0}'.format(max_conn),
                    'ApplyMethod': 'immediate'
                },
                {
                    'ParameterName': 'max_user_connections',
                    'ParameterValue': '{0}'.format(max_user_conn),
                    'ApplyMethod': 'immediate'
                }
            ]
        )

    def set_modify_db_instance(self, id, cls):
        res = self.client.modify_db_instance(
            DBInstanceIdentifier=id,
            DBInstanceClass=cls,
            ApplyImmediately=True
        )
        print_row = "Class [{0}] ".format(res["DBInstance"]["DBInstanceClass"])
        print_row += "to [{0}] ".format(cls)
        print_row += " Status [{0}]".format(res["DBInstance"]["DBInstanceStatus"])

        print("Modify: {0}".format(print_row))
        print("Begin: [{0}]".format(time.strftime('%c', time.localtime(time.time()))))

    def set_failover_db_cluster(self, target_id):
        self.client.failover_db_cluster(
            DBClusterIdentifier=self.cluster_id,
            TargetDBInstanceIdentifier=target_id
        )
        time.sleep(30)
        status_check = 0
        while status_check < 100:
            is_break = False
            res = self.get_cluster_info()
            rows = res["DBClusters"][0]["DBClusterMembers"]
            for row in rows:
                if row["IsClusterWriter"] and row["DBInstanceIdentifier"] == target_id:
                    is_break = True
                    break

            if is_break:
                break
            status_check = status_check + 1
            time.sleep(30)
        

    @staticmethod
    def get_max_connections(db_cls):
        class_param = {
            "db.r5.large": (2000, 1950),
            "db.r5.xlarge": (3000, 2950),
            "db.r5.2xlarge": (4000, 3950),
            "db.r5.4xlarge": (5000, 4950),
            "db.r5.8xlarge": (6000, 5950),
            "db.r5.12xlarge": (7000, 6950),
            "db.r5.16xlarge": (7000, 6950),
            "db.r5.24xlarge": (10000, 9950),
            "db.r6g.large": (2000, 1950),
            "db.r6g.xlarge": (3000, 2950),
            "db.r6g.2xlarge": (4000, 3950),
            "db.r6g.4xlarge": (5000, 4950),
            "db.r6g.8xlarge": (6000, 5950),
            "db.r6g.12xlarge": (7000, 6950),
            "db.r6g.16xlarge": (7000, 6950),
            "db.r6g.24xlarge": (10000, 9950),
            "db.t3.small": (45, 40),
            "db.t3.medium": (90, 85)
        }
        return class_param.get(db_cls)


class RestoreAurora(Aurora):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if kwargs.get('restore_class'):
            self.restore_class = kwargs['restore_class']
        else:
            self.restore_class = "db.t3.medium"

        self.restore_info = {
            'Owner': 'soohyun',
            'aws_region': self.aws_region,
            'restore_port': 3306,
            'restore_DBClusterParameter': kwargs.get('soohyun_cluster_param'),
            'restore_DBParameter': kwargs.get('soohyun_instance_param'),
            'restore_class': self.restore_class
        }

    def get_automated_snapshots(self):
        response = self.client.describe_db_cluster_snapshots(
            DBClusterIdentifier=self.cluster_id,
            SnapshotType='automated'
        )
        return response

    def set_restore_form_last_snapshots(self):
        """
        Aurora 에서 마지막으로 자동 백업된 스냅샷에서 복구에 필요한 정보를 restore_info dict 에 추가.
        """
        response = self.get_automated_snapshots()
        self.restore_info['snapshot_id'] = response['DBClusterSnapshots'][-1]['DBClusterSnapshotIdentifier']
        self.restore_info['snapshot_create_time'] = response['DBClusterSnapshots'][-1]['SnapshotCreateTime']
        self.restore_info['az_list'] = response['DBClusterSnapshots'][-1]['AvailabilityZones']
        self.restore_info['rds_engine'] = response['DBClusterSnapshots'][-1]['Engine']
        if self.restore_info['rds_engine'] == 'aurora':
            self.restore_info['rds_engine_ver'] = '5.6.mysql_aurora.1.23.2'
        elif self.restore_info['rds_engine'] == 'aurora-mysql':
            self.restore_info['rds_engine_ver'] = '5.7.mysql_aurora.2.09.2'
        else:
            self.restore_info['rds_engine_ver'] = response['DBClusterSnapshots'][-1]['EngineVersion']
        
        self.restore_info['kms_key_id'] = response['DBClusterSnapshots'][-1]['KmsKeyId']
        """
        Source Aurora Cluster 에서 복구에 필요한 정보 restore_info dict 에 추가.
        """
        response = self.get_cluster_info()
        self.restore_info['db_subnet']  = response['DBClusters'][0]['DBSubnetGroup']
        vpc_sg_ids = []
        for row in response['DBClusters'][0]['VpcSecurityGroups']:
            vpc_sg_ids.append(row['VpcSecurityGroupId'])
        self.restore_info['vpc_sg_ids'] = vpc_sg_ids
        self.restore_info['backup_widow'] = response['DBClusters'][0]['PreferredBackupWindow']
        self.restore_info['maintenance_widow'] = response['DBClusters'][0]['PreferredMaintenanceWindow']
        sendbird_region = self.restore_info['aws_region']
        tags_list = response['DBClusters'][0]['TagList']
        for tags in tags_list:
            if tags['Key'] == "sendbird_region":
                sendbird_region = tags['Value']
            elif tags['Key'] == "product":
                product = tags['Value']
        restore_tags = [
            {
                'Key': 'product',
                'Value': self.restore_info['Owner']
            },
            {
                'Key': 'managed_by',
                'Value': 'manually'
            },
            {
                'Key': 'sendbird_region',
                'Value': '{0}-{1}'.format(sendbird_region, self.restore_info['Owner'])
            },
            {
                'Key': 'env',
                'Value': 'dev'
            },
            {
                'Key': 'Owner',
                'Value': "{0}.park".format(self.restore_info['Owner'])
            }
        ]
        self.restore_info['restore_tags'] = restore_tags
        self.restore_info['restore_cluster_id'] = "{0}-{1}-dev-01".format(
            self.restore_info['Owner'],
            sendbird_region
        )

    def set_restore_db_cluster_from_snapshot(self):
        response = self.client.restore_db_cluster_from_snapshot(
            AvailabilityZones=self.restore_info['az_list'],
            DBClusterIdentifier=self.restore_info['restore_cluster_id'],
            SnapshotIdentifier=self.restore_info['snapshot_id'],
            Engine=self.restore_info['rds_engine'],
            EngineVersion=self.restore_info['rds_engine_ver'],
            Port=self.restore_info['restore_port'],
            DBSubnetGroupName=self.restore_info['db_subnet'],
            VpcSecurityGroupIds=self.restore_info['vpc_sg_ids'],
            Tags=self.restore_info['restore_tags'],
            KmsKeyId=self.restore_info['kms_key_id'],
            EnableIAMDatabaseAuthentication=True,
            DBClusterParameterGroupName=self.restore_info['restore_DBClusterParameter'],
            DeletionProtection=False
        )
        return response

    def set_restore_db_instance_from_snapshot(self):
        response = self.client.create_db_instance(
            DBClusterIdentifier=self.restore_info['restore_cluster_id'],
            DBInstanceIdentifier=self.restore_info['restore_cluster_id'],
            DBInstanceClass=self.restore_info['restore_class'],
            Engine=self.restore_info['rds_engine'],
            PreferredMaintenanceWindow=self.restore_info['maintenance_widow'],
            DBParameterGroupName=self.restore_info['restore_DBParameter'],
            MultiAZ=False,
            EngineVersion=self.restore_info['rds_engine_ver'],
            AutoMinorVersionUpgrade=False,
            PubliclyAccessible=False,
            Tags=self.restore_info['restore_tags'],
            EnablePerformanceInsights=False
        )
        return response

    def get_restore_db_cluster_status(self):
        response = self.get_cluster_info(self.restore_info['restore_cluster_id'])
        return response
