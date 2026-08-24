from __future__ import annotations
import os
from ml.pipeline.build_pipeline import build_pipeline
def main():
    region=os.getenv("AWS_REGION","us-east-1"); role=os.environ["SAGEMAKER_ROLE_ARN"]; bucket=os.environ["DATA_BUCKET"]; name=os.getenv("PIPELINE_NAME","otosage-aws-training-pipeline"); group=os.getenv("MODEL_PACKAGE_GROUP","otosage-aws-models"); pipeline=build_pipeline(region,role,bucket,name,group); pipeline.upsert(role_arn=role); print(f"Upserted SageMaker Pipeline: {name}")
if __name__=="__main__": main()
