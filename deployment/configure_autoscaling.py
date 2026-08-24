from __future__ import annotations
import argparse, boto3

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--endpoint-name",required=True); ap.add_argument("--variant-name",default="AllTraffic"); ap.add_argument("--min-capacity",type=int,default=0); ap.add_argument("--max-capacity",type=int,default=4); ap.add_argument("--target-backlog-per-instance",type=float,default=2.0); ap.add_argument("--region",default=None); a=ap.parse_args()
    app=boto3.Session(region_name=a.region).client("application-autoscaling"); rid=f"endpoint/{a.endpoint_name}/variant/{a.variant_name}"
    app.register_scalable_target(ServiceNamespace="sagemaker",ResourceId=rid,ScalableDimension="sagemaker:variant:DesiredInstanceCount",MinCapacity=a.min_capacity,MaxCapacity=a.max_capacity)
    app.put_scaling_policy(PolicyName=f"{a.endpoint_name}-backlog-target",ServiceNamespace="sagemaker",ResourceId=rid,ScalableDimension="sagemaker:variant:DesiredInstanceCount",PolicyType="TargetTrackingScaling",TargetTrackingScalingPolicyConfiguration={"TargetValue":a.target_backlog_per_instance,"CustomizedMetricSpecification":{"MetricName":"ApproximateBacklogSizePerInstance","Namespace":"AWS/SageMaker","Dimensions":[{"Name":"EndpointName","Value":a.endpoint_name}],"Statistic":"Average"},"ScaleInCooldown":300,"ScaleOutCooldown":60})
    print("Configured autoscaling for",rid)

if __name__=="__main__": main()
