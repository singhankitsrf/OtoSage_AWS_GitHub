from __future__ import annotations
import argparse, time
import boto3


def latest_approved(sm, group):
    r = sm.list_model_packages(
        ModelPackageGroupName=group,
        ModelApprovalStatus="Approved",
        SortBy="CreationTime",
        SortOrder="Descending",
        MaxResults=1,
    )
    items = r.get("ModelPackageSummaryList", [])
    if not items:
        raise RuntimeError(f"No Approved model package in {group}.")
    return items[0]["ModelPackageArn"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-package-group", required=True)
    ap.add_argument("--endpoint-name", required=True)
    ap.add_argument("--output-s3", required=True)
    ap.add_argument("--success-topic-arn", required=True)
    ap.add_argument("--failure-topic-arn", required=True)
    ap.add_argument("--role-arn", required=True)
    ap.add_argument("--instance-type", default="ml.m5.xlarge")
    ap.add_argument("--region", default=None)
    a = ap.parse_args()
    sm = boto3.Session(region_name=a.region).client("sagemaker")
    package = latest_approved(sm, a.model_package_group)
    stamp = time.strftime("%Y%m%d%H%M%S")
    model_name = f"{a.endpoint_name}-model-{stamp}"
    config_name = f"{a.endpoint_name}-config-{stamp}"
    sm.create_model(
        ModelName=model_name,
        PrimaryContainer={"ModelPackageName": package},
        ExecutionRoleArn=a.role_arn,
    )
    sm.create_endpoint_config(
        EndpointConfigName=config_name,
        ProductionVariants=[
            {
                "VariantName": "AllTraffic",
                "ModelName": model_name,
                "InitialInstanceCount": 1,
                "InstanceType": a.instance_type,
                "InitialVariantWeight": 1.0,
            }
        ],
        AsyncInferenceConfig={
            "OutputConfig": {
                "S3OutputPath": a.output_s3,
                "NotificationConfig": {
                    "SuccessTopic": a.success_topic_arn,
                    "ErrorTopic": a.failure_topic_arn,
                },
            },
            "ClientConfig": {"MaxConcurrentInvocationsPerInstance": 2},
        },
    )
    try:
        sm.describe_endpoint(EndpointName=a.endpoint_name)
        sm.update_endpoint(EndpointName=a.endpoint_name, EndpointConfigName=config_name)
        print("Updating endpoint:", a.endpoint_name)
    except sm.exceptions.ClientError:
        sm.create_endpoint(EndpointName=a.endpoint_name, EndpointConfigName=config_name)
        print("Creating endpoint:", a.endpoint_name)
    print("Model package:", package)


if __name__ == "__main__":
    main()
