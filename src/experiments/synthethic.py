import numpy as np
from scipy.spatial import distance
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import MinMaxScaler

from src.learners import *
from .experiment import Experiment


class Synthetic(Experiment):
    def __init__(self, rng, balanced_db=True, tiny_clusters=True):

        # Generate mock data with balanced number of positive and negative examples
        X_pos, y_pos = self.generate_positive(1, 13, 8)

        if not balanced_db:
            # Generate mock data with rare grid class
            proportion = 0.3
            perm = rng.permutation(len(X_pos))
            X_pos = X_pos[perm[: int(proportion*len(X_pos))]]
            y_pos = y_pos[perm[: int(proportion*len(X_pos))]]

        if tiny_clusters:
            # Generate tiny clusters (0 to 10 points) around the positive points
            centers = X_pos
            n_samples = rng.randint(0, 10, size=len(centers))
            cluster_std = rng.uniform(0, 2, size=len(centers))

            X_pos_add, _ = make_blobs(n_samples=n_samples, cluster_std=cluster_std, centers=centers, n_features=2, random_state=1)
            X_pos = np.concatenate((X_pos, X_pos_add), axis=0)
            y_pos = np.concatenate((y_pos, np.ones((len(X_pos_add)), dtype=int)), axis=0)
            # y_pos = np.ones((len(X_pos)), dtype=int)

            X_neg, y_neg = self.generate_negative(100, 1500, rng, centers, cluster_std)
        else:
            X_neg, y_neg = self.generate_negative(100, 1000, rng)

        X = np.concatenate((X_pos, X_neg), axis=0)
        y = np.concatenate((y_pos, y_neg), axis=0)

        sc = MinMaxScaler()
        X_processed = sc.fit_transform(X)

        model = SVM(name='svm_rbf', rng=rng, gamma=1e3, C=1)

        super().__init__(model, X_processed, y, feature_names=['x', 'y'], name="Synthetic", prop_known=0.001, rng=rng)

    @staticmethod
    def generate_positive(start, end, skip):
        """
        Generate points that lie on a grid.

        :param start: The start point of the interval for generating points
        :param end: The end point of the interval for generating points
        :param skip: How far apart the points should be on the grid

        :return: Coordinates of the generated points and an array of ones as their labels
        """
        x_coord = np.arange(start, end) * skip
        y_coord = np.arange(start, end) * skip
        pointsp = np.array([[a, b] for a in x_coord for b in y_coord])
        yp = np.ones((len(pointsp)), dtype=int)
        return pointsp, yp

    def generate_negative(self, axis, how_many, rng, centers=None, cluster_std=None):
        """
        Generate randomly distributed points.

        :param axis: Specifies the length of the axis
        :param how_many: How many points to be generated
        :param rng: RandomState object
        :param centers: The centers of the Gaussian blobs (the positive points)
        :param cluster_std: The standard deviation for each of the Gaussian blobs

        :return: Coordinates of the generated points and an array of zeros as their labels
        """
        pointsn = rng.rand(how_many, 2) * axis
        if centers is not None and cluster_std is not None:
          for i, center in enumerate(centers):
            distances = [distance.euclidean(center, point) for point in pointsn]
            to_keep = np.where(np.asarray(distances) > 2* cluster_std[i])[0]
            pointsn = pointsn[to_keep]

        yn = np.zeros((len(pointsn)), dtype=int)
        return pointsn, yn
