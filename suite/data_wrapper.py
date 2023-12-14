from abc import ABC, abstractmethod
from typing import Dict, List, Union
import numpy as np
from numpy.typing import ArrayLike
from .utils import leave_pair_out_cv


class Dataset(ABC):
    """
    Abstract wrapper class for datasets.
    """

    @abstractmethod
    def load(self):
        """
        Loads the dataset from data.
        """
        pass

    @abstractmethod
    def save(self):
        """
        Saves the dataset to data.
        """
        pass


class DrugResponseDataset(Dataset):
    """
    Drug response dataset.
    """

    def __init__(
        self,
        target_type: str,
        response: ArrayLike,
        cell_line_ids: ArrayLike,
        drug_ids: ArrayLike,
        *args,
        **kwargs,
    ):
        """
        Initializes the drug response dataset.
        :param target_type: type of the target value (IC50, EC50, AUC, classification)
        :param response: drug response values per cell line and drug
        :param cell_line_ids: cell line IDs
        :param drug_ids: drug IDs

        Variables:
        response: drug response values per cell line and drug
        cell_line_ids: cell line IDs
        drug_ids: drug IDs
        predictions: optional. Predicted drug response values per cell line and drug
        """
        super(DrugResponseDataset, self).__init__()
        self.target_type = target_type
        self.response = response
        self.cell_line_ids = cell_line_ids
        self.drug_ids = drug_ids
        self.predictions = None

    def load(self):
        """
        Loads the drug response dataset from data.
        """
        raise NotImplementedError("load method not implemented")

    def save(self):
        """
        Saves the drug response dataset to data.
        """
        raise NotImplementedError("save method not implemented")

    def split_dataset(
        self,
        n_cv_splits,
        mode,
        split_validation=True,
        validation_ratio=0.1,
        random_state=42,
    ) -> List[dict]:
        """
        Splits the dataset into training, validation and test sets for crossvalidation
        :param mode: split mode (LPO=Leave-random-Pairs-Out, LCO=Leave-Cell-line-Out, LDO=Leave-Drug-Out)
        :return: training, validation and test sets
        """

        cell_line_ids = self.cell_line_ids
        drug_ids = self.drug_ids
        response = self.response

        if mode == "LPO":
            cv_splits = leave_pair_out_cv(
                n_cv_splits,
                response,
                cell_line_ids,
                drug_ids,
                split_validation,
                validation_ratio,
                random_state,
            )

        elif mode == "LCO":
            # TODO
            raise NotImplementedError("LCO split mode not implemented")
        elif mode == "LDO":
            # TODO
            raise NotImplementedError("LDO split mode not implemented")
        self.cv_splits = cv_splits
        return cv_splits


class FeatureDataset(Dataset):
    """
    Class for feature datasets.
    """

    def __init__(self, features: Dict[str, Dict[str, np.ndarray]], *args, **kwargs):
        """
        Initializes the feature dataset.
        :features: dictionary of features, key: drug ID, value: Dict of feature views, key: feature name, value: feature vector
        """
        super(FeatureDataset, self).__init__()
        self.features = features
        self.view_names = self.get_view_names()
        self.identifier = self.get_ids()

    @staticmethod
    def load():
        """
        Loads the feature dataset from data.
        """
        raise NotImplementedError("load method not implemented")

    def save(self):
        """
        Saves the feature dataset to data.
        """
        raise NotImplementedError("save method not implemented")

    def randomize_features(
        self, views_to_randomize: Union[str, list], mode: str
    ) -> None:
        """
        Randomizes the feature vectors.
        :views_to_randomize: name of feature view or list of names of multiple feature views to randomize. The other views are not randomized.
        :mode: randomization mode (permutation, gaussian, zeroing)
        """
        if isinstance(views, str):
            views = [views]

        if mode == "permutation":
            # Get the entity names
            identifiers = self.get_ids()

            # Permute the specified views for each entity (= cell line or drug)
            self.features = {
                entity: {
                    view: self.features[entity][view]
                    if view not in views_to_randomize
                    else self.features[other_entity][view]
                    for view, other_entity in zip(
                        self.features[entity].keys(), np.random.permutation(identifiers)
                    )
                }
                for entity in identifiers
            }

        elif mode == "gaussian":
            for view in views:
                for identifier in self.get_ids():
                    self.features[identifier][view] = np.random.normal(
                        self.features[identifier][view].mean(),
                        self.features[identifier][view].std(),
                        self.features[identifier][view].shape,
                    )
        elif mode == "zeroing":
            for view in views:
                for identifier in self.get_ids():
                    self.features[identifier][view] = np.zeros(
                        self.features[identifier][view].shape
                    )
        else:
            raise ValueError(
                f"Unknown randomization mode '{mode}'. Choose from 'permutation', 'gaussian', 'zeroing'."
            )

    def normalize_features(
        self, views: Union[str, list], normalization_parameter
    ) -> None:
        """
        normalize the feature vectors.
        :views: name of feature view or list of names of multiple feature views to normalize. The other views are not normalized.
        :normalization_parameter:
        """
        # TODO
        raise NotImplementedError("normalize_features method not implemented")

    def get_mean_and_standard_deviation(self) -> None:
        """
        get columnwise mean and standard deviation of the feature vectors for all views.
        """
        # TODO
        raise NotImplementedError(
            "get_mean_and_standard_deviation method not implemented"
        )

    def get_ids(self):
        """
        returns drug ids of the dataset
        """
        return list(self.features.keys())

    def get_view_names(self):
        """
        returns feature view names
        """
        return list(self.features[list(self.features.keys())[0]].keys())

    def get_feature_matrix(self, view: str, identifiers: str) -> np.ndarray:
        """
        Returns the feature matrix for the given view.
        :param drug_input: drug input
        :param cell_line_input: cell line input
        :param view: view name
        :return: feature matrix
        """
        return np.stack([self.features[identifier][view] for identifier in identifiers])
