from __future__ import annotations

import os
import boto3
import sagemaker
from sagemaker.inputs import TrainingInput
from sagemaker.model_metrics import MetricsSource, ModelMetrics
from sagemaker.processing import ProcessingInput, ProcessingOutput, ScriptProcessor
from sagemaker.pytorch import PyTorch, PyTorchModel
from sagemaker.workflow.condition_step import ConditionStep
from sagemaker.workflow.conditions import ConditionGreaterThanOrEqualTo, ConditionLessThanOrEqualTo
from sagemaker.workflow.functions import JsonGet
from sagemaker.workflow.model_step import ModelStep
from sagemaker.workflow.parameters import ParameterFloat, ParameterInteger, ParameterString
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.pipeline_context import PipelineSession
from sagemaker.workflow.properties import PropertyFile
from sagemaker.workflow.steps import ProcessingStep, TrainingStep


def build_pipeline(
    region,
    role_arn,
    data_bucket,
    pipeline_name="otosage-aws-training-pipeline",
    model_package_group="otosage-aws-models",
):
    boto_session = boto3.Session(region_name=region)
    session = PipelineSession(boto_session=boto_session)
    input_data = ParameterString(name="InputData", default_value=f"s3://{data_bucket}/raw/")
    processing_instance = ParameterString(
        name="ProcessingInstanceType", default_value="ml.m5.xlarge"
    )
    training_instance = ParameterString(name="TrainingInstanceType", default_value="ml.g4dn.xlarge")
    epochs = ParameterInteger(name="Epochs", default_value=25)
    macro_f1_threshold = ParameterFloat(name="MacroF1Threshold", default_value=0.80)
    ece_threshold = ParameterFloat(name="ECEThreshold", default_value=0.15)
    approval = ParameterString(name="ModelApprovalStatus", default_value="PendingManualApproval")
    framework_version = os.getenv("SAGEMAKER_PYTORCH_VERSION", "2.5.1")
    py_version = os.getenv("SAGEMAKER_PYTHON_VERSION", "py311")
    image_uri = sagemaker.image_uris.retrieve(
        framework="pytorch",
        region=region,
        version=framework_version,
        py_version=py_version,
        image_scope="training",
        instance_type="ml.m5.xlarge",
    )
    processor = ScriptProcessor(
        image_uri=image_uri,
        command=["python3"],
        role=role_arn,
        instance_count=1,
        instance_type=processing_instance,
        sagemaker_session=session,
    )
    preprocess_args = processor.run(
        code="ml/src/preprocess.py",
        inputs=[ProcessingInput(source=input_data, destination="/opt/ml/processing/input")],
        outputs=[
            ProcessingOutput(
                output_name="train",
                source="/opt/ml/processing/output/train",
                destination=f"s3://{data_bucket}/processed/train/",
            ),
            ProcessingOutput(
                output_name="val",
                source="/opt/ml/processing/output/val",
                destination=f"s3://{data_bucket}/processed/val/",
            ),
            ProcessingOutput(
                output_name="test",
                source="/opt/ml/processing/output/test",
                destination=f"s3://{data_bucket}/processed/test/",
            ),
            ProcessingOutput(
                output_name="audit",
                source="/opt/ml/processing/output",
                destination=f"s3://{data_bucket}/audit/",
            ),
        ],
        arguments=["--seed", "42"],
    )
    step_preprocess = ProcessingStep(name="ValidateDedupeAndSplit", step_args=preprocess_args)
    estimator = PyTorch(
        entry_point="train.py",
        source_dir="ml/src",
        role=role_arn,
        framework_version=framework_version,
        py_version=py_version,
        instance_count=1,
        instance_type=training_instance,
        hyperparameters={
            "epochs": epochs,
            "batch-size": 32,
            "learning-rate": 0.0003,
            "weight-decay": 0.0001,
            "image-size": 224,
            "patience": 6,
            "seed": 42,
        },
        metric_definitions=[
            {"Name": "validation:macro_f1", "Regex": r"best_validation_macro_f1=([0-9\.]+)"}
        ],
        sagemaker_session=session,
    )
    train_args = estimator.fit(
        inputs={
            "train": TrainingInput(
                step_preprocess.properties.ProcessingOutputConfig.Outputs["train"].S3Output.S3Uri
            ),
            "val": TrainingInput(
                step_preprocess.properties.ProcessingOutputConfig.Outputs["val"].S3Output.S3Uri
            ),
        }
    )
    step_train = TrainingStep(name="TrainEfficientNetV2S", step_args=train_args)
    evaluator = ScriptProcessor(
        image_uri=image_uri,
        command=["python3"],
        role=role_arn,
        instance_count=1,
        instance_type=processing_instance,
        sagemaker_session=session,
    )
    eval_report = PropertyFile(
        name="EvaluationReport", output_name="evaluation", path="evaluation.json"
    )
    eval_args = evaluator.run(
        code="ml/src/evaluate.py",
        inputs=[
            ProcessingInput(
                source=step_train.properties.ModelArtifacts.S3ModelArtifacts,
                destination="/opt/ml/processing/model",
            ),
            ProcessingInput(
                source=step_preprocess.properties.ProcessingOutputConfig.Outputs[
                    "test"
                ].S3Output.S3Uri,
                destination="/opt/ml/processing/test",
            ),
        ],
        outputs=[
            ProcessingOutput(
                output_name="evaluation",
                source="/opt/ml/processing/evaluation",
                destination=f"s3://{data_bucket}/evaluation/",
            )
        ],
    )
    step_eval = ProcessingStep(
        name="EvaluateModel", step_args=eval_args, property_files=[eval_report]
    )
    pytorch_model = PyTorchModel(
        model_data=step_train.properties.ModelArtifacts.S3ModelArtifacts,
        role=role_arn,
        entry_point="inference.py",
        source_dir="ml/src",
        framework_version=framework_version,
        py_version=py_version,
        sagemaker_session=session,
    )
    model_metrics = ModelMetrics(
        model_statistics=MetricsSource(
            s3_uri=step_eval.properties.ProcessingOutputConfig.Outputs["evaluation"].S3Output.S3Uri
            + "/evaluation.json",
            content_type="application/json",
        )
    )
    register_args = pytorch_model.register(
        content_types=["image/jpeg", "image/png", "image/webp"],
        response_types=["application/json"],
        inference_instances=["ml.m5.large", "ml.m5.xlarge"],
        transform_instances=["ml.m5.large"],
        model_package_group_name=model_package_group,
        approval_status=approval,
        model_metrics=model_metrics,
    )
    step_register = ModelStep(name="RegisterQualifiedModel", step_args=register_args)
    quality_gate = ConditionStep(
        name="ModelQualityGate",
        conditions=[
            ConditionGreaterThanOrEqualTo(
                left=JsonGet(
                    step_name=step_eval.name,
                    property_file=eval_report,
                    json_path="classification_metrics.macro_f1",
                ),
                right=macro_f1_threshold,
            ),
            ConditionLessThanOrEqualTo(
                left=JsonGet(
                    step_name=step_eval.name,
                    property_file=eval_report,
                    json_path="classification_metrics.ece",
                ),
                right=ece_threshold,
            ),
        ],
        if_steps=[step_register],
        else_steps=[],
    )
    return Pipeline(
        name=pipeline_name,
        parameters=[
            input_data,
            processing_instance,
            training_instance,
            epochs,
            macro_f1_threshold,
            ece_threshold,
            approval,
        ],
        steps=[step_preprocess, step_train, step_eval, quality_gate],
        sagemaker_session=session,
    )
