import os
import json

from kepler_model.train import DefaultExtractor
from kepler_model.util.train_types import FeatureGroup, XGBoostRegressionTrainType
from kepler_model.train.profiler.profiler import response_to_result
from kepler_model.train.trainer.XGBoostTrainer.main import XGBoostRegressionStandalonePipeline

energy_components = ["package", "core", "uncore", "dram"]
feature_group = FeatureGroup.BPFIRQ.name
energy_source = "rapl-sysfs"

prom_response_file = os.path.join(os.path.dirname(__file__), "data", "prom_output", "prom_response.json")


def read_sample_query_results():
    with open(prom_response_file) as f:
        response = json.load(f)
        return response_to_result(response)


if __name__ == "__main__":
    # Note that extractor mutates the query results
    query_results = read_sample_query_results()
    assert len(query_results) > 0, "cannot read_sample_query_results"
    instance = DefaultExtractor()
    extracted_data, power_columns, _, _ = instance.extract(query_results, energy_components, feature_group, energy_source, node_level=True)
    xgb_container_level_pipeline_kfold = XGBoostRegressionStandalonePipeline(XGBoostRegressionTrainType.KFoldCrossValidation, "test_models/XGBoost/", node_level=True)
    xgb_node_pipeline_kfold = XGBoostRegressionStandalonePipeline(XGBoostRegressionTrainType.KFoldCrossValidation, "test_models/XGBoost/", node_level=False)
    xgb_container_level_pipeline_tts = XGBoostRegressionStandalonePipeline(XGBoostRegressionTrainType.TrainTestSplitFit, "test_models/XGBoost/", node_level=False)
    xgb_node_pipeline_tts = XGBoostRegressionStandalonePipeline(XGBoostRegressionTrainType.TrainTestSplitFit, "test_models/XGBoost/", node_level=True)
    xgb_node_pipeline_kfold.train(None, query_results)
    xgb_container_level_pipeline_tts.train(None, query_results)
    xgb_node_pipeline_tts.train(None, query_results)
    xgb_container_level_pipeline_kfold.train(None, query_results)
