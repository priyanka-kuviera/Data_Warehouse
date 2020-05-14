"""Script that deletes the cluster when done using it."""
from create_redshift_cluster import config, redshift
from create_IAM_Role import config,iam
from time import sleep


def delete_cluster():
    """Delete the cluster when done using it."""
    try:
        redshift.delete_cluster(
            ClusterIdentifier=config.get(
                'DWH', 'DWH_CLUSTER_IDENTIFIER'), SkipFinalClusterSnapshot=True)
        print('Deletion of cluster has been initiated!')
    except Exception as e:
        print(e)
        
def delete_IAM_Role():
    try:
        iam.detach_role_policy(RoleName=config.get('DWH','DWH_IAM_ROLE_NAME'),
                                       PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess")
        iam.delete_role(RoleName=config.get('DWH','DWH_IAM_ROLE_NAME')) 
        print('IAM Role has been deleted')
    except Exception as e:
        print(e)

if __name__ == "__main__":
    delete_cluster()
    sleep(120)
    delete_IAM_Role()