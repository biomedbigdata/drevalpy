from typing import List
import numpy as np
from sklearn.ensemble import RandomForestRegressor

from dreval.dataset import FeatureDataset, DrugResponseDataset
from dreval.drp_model import DRPModel
from ..utils import load_ge_features_from_landmark_genes, load_drug_features_from_fingerprints


class RandomForest(DRPModel):
    model_name = 'RandomForest'
    cell_line_views = ['gene_expression']
    drug_views = ['fingerprints']

    @staticmethod
    def get_hyperparameter_set() -> List[dict]:
        """
        Returns a list of hyperparameters for the model.
        Hyperparameters to consider:
        - n_estimators: The number of trees in the forest.
        - max_depth: The maximum depth of the tree.
        - feature_path: Path to the feature dataset.
        :return: List of hyperparameters including the default combination.
        """
        hpams = [
            {'n_estimators': 100, 'criterion': 'squared_error', 'max_depth': None, 'min_samples_split': 2,
             'min_samples_leaf': 1, 'n_jobs': 3, 'max_samples': 0.7},
            {'n_estimators': 100, 'criterion': 'absolute_error', 'max_depth': 10, 'min_samples_split': 5,
             'min_samples_leaf': 2, 'n_jobs': 3, 'max_samples': 0.7},
            {'n_estimators': 50, 'criterion': 'squared_error', 'max_depth': 5, 'min_samples_split': 10,
             'min_samples_leaf': 5, 'n_jobs': 3, 'max_samples': 0.7}
        ]
        for hpam in hpams:
            hpam['feature_path'] = 'data/GDSC'
        return hpams

    def build_model(self, hyperparameters: dict):
        """
        Builds the model from hyperparameters.
        :param hyperparameters: Hyperparameters for the model.
        """
        self.model = RandomForestRegressor(n_estimators=hyperparameters['n_estimators'],
                                           criterion=hyperparameters['criterion'],
                                           max_depth=hyperparameters['max_depth'],
                                           min_samples_split=hyperparameters['min_samples_split'],
                                           min_samples_leaf=hyperparameters['min_samples_leaf'],
                                           n_jobs=hyperparameters['n_jobs'],
                                           max_samples=hyperparameters['max_samples'])

    def train(self, output: DrugResponseDataset,
              gene_expression: np.ndarray = None,
              fingerprints: np.ndarray = None) -> None:
        """
        Trains the model: the number of features is the number of genes + the number of fingerprints.
        :param output: training dataset containing the response output
        :param gene_expression: training dataset containing gene expression data
        :param fingerprints: training dataset containing fingerprints data
        """
        X = np.concatenate((gene_expression, fingerprints), axis=1)
        self.model.fit(X, output.response)

    def predict(self,
                gene_expression: np.ndarray = None,
                fingerprints: np.ndarray = None) -> np.ndarray:
        """
        Predicts the response for the given input.
        :param gene_expression: gene expression data
        :param fingerprints: fingerprints data
        :return: predicted response
        """
        X = np.concatenate((gene_expression, fingerprints), axis=1)
        return self.model.predict(X)

    def save(self, path):
        raise NotImplementedError('RF does not support saving yet ...')

    def load(self, path):
        raise NotImplementedError('RF does not support loading yet ...')

    def load_cell_line_features(self, path: str) -> FeatureDataset:
        """
        Loads the cell line features.
        :param path: Path to the gene expression and landmark genes
        :return: FeatureDataset containing the cell line gene expression features, filtered through the landmark genes
        """
        return load_ge_features_from_landmark_genes(path)

    def load_drug_features(self, path: str) -> FeatureDataset:
        """
        Loads the drug features.
        :param path: Path to the drug fingerprints
        :return: FeatureDataset containing the drug fingerprints
        """
        return load_drug_features_from_fingerprints(path)