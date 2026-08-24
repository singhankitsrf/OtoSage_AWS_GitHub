# AWS Deployment Notes

The architecture follows current AWS service capabilities: SageMaker Asynchronous Inference, SageMaker Pipelines, Model Registry, and parameterized PyTorch DLC versions.

Environment overrides:

```bash
export SAGEMAKER_PYTORCH_VERSION=2.5.1
export SAGEMAKER_PYTHON_VERSION=py311
```

Always verify service availability and pricing in the selected AWS Region before a real deployment.
