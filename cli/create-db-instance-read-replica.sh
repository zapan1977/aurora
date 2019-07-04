#--
# Dev Zone RDS: dev-identifier
# Prod Zone RDS: prod-identifier
#--

# RDS instance 확인.
aws rds describe-db-instances \
--db-instance-identifier dev-identifier

# RDS Read replica 생성.
aws rds create-db-instance-read-replica \
--db-instance-identifier identifier-dev-02 \
--source-db-instance-identifier identifier-dev-01 \
--db-instance-class db.t3.medium \
--availability-zone ap-northeast-2a \
--no-multi-az \
--no-publicly-accessible \
--tags Key=Name,Value=identifier-dev-02 Key=Owner,Value=soohyun Key=MadeBy,Value=AWSCLI Key=Workload-type,Value=develop \
--vpc-security-group-ids "sg-id" "sg-id" \
--no-copy-tags-to-snapshot \
--no-enable-performance-insights \
--no-deletion-protection
