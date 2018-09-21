r"""
A set of rotation utilites for manipuklating 3D vectors
"""

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)
import numpy as np
from .vector_calculations import *


__all__=['rotate_vector_collection', 'random_rotation', 'rotation_matrices_from_angles',
         'rotation_matrices_from_vectors', 'random_perpendicular_directions']
__author__ = ['Duncan Campbell', 'Andrew Hearin']


def rotate_vector_collection(rotation_matrices, vectors, optimize=False):
    r""" 
    Given a collection of rotation matrices and a collection of 2d vectors,
    apply each matrix to rotate the corresponding vector.
    
    Parameters
    ----------
    rotation_matrices : ndarray
        Numpy array of shape (npts, 2, 2) storing a collection of rotation matrices.
        If an array of shape (2, 2) is passed, all the vectors
        are rotated using the same rotation matrix.
    
    vectors : ndarray
        Numpy array of shape (npts, 2) storing a collection of 3d vectors
    
    Returns
    -------
    rotated_vectors : ndarray
        Numpy array of shape (npts, 2) storing a collection of 3d vectors
    
    Examples
    --------
    In this example, we'll randomly generate two sets of unit-vectors, `v0` and `v1`.
    We'll use the `rotation_matrices_from_vectors` function to generate the
    rotation matrices that rotate each `v0` into the corresponding `v1`.
    Then we'll use the `rotate_vector_collection` function to apply each
    rotation, and verify that we recover each of the `v1`.
    
    >>> npts = int(1e4)
    >>> v0 = normalized_vectors(np.random.random((npts, 2)))
    >>> v1 = normalized_vectors(np.random.random((npts, 2)))
    >>> rotation_matrices = rotation_matrices_from_vectors(v0, v1)
    >>> v2 = rotate_vector_collection(rotation_matrices, v0)
    >>> assert np.allclose(v1, v2)
    """

    # apply same rotation matrix to all vectors
    if np.shape(rotation_matrices) == (2, 2):
        return np.dot(rotation_matrices, vectors.T).T
    # rotate each vector by associated rotation matrix
    else:
        try:
            return np.einsum('ijk,ik->ij', rotation_matrices, vectors, optimize=optimize)
        except TypeError:
            return np.einsum('ijk,ik->ij', rotation_matrices, vectors)


def random_rotation(vectors):
    r"""
    Apply a random rotation to a set of 3d vectors.

    Parameters
    ----------
    vectors : ndarray
        Numpy array of shape (npts, 3) storing a collection of 3d vectors
    
    Returns
    -------
    rotated_vectors : ndarray
        Numpy array of shape (npts, 3) storing a collection of 3d vectors
    """

    ran_angle = np.random.random(size=1)*(np.pi)
    ran_direction = normalized_vectors(np.random.random((2,)))*2.0 - 1.0
    ran_rot = rotation_matrices_from_angles(ran_angle, ran_direction)

    return rotate_vector_collection(ran_rot, vectors)


def rotation_matrices_from_angles(angles):
    r""" 
    Calculate a collection of rotation matrices defined by
    an input collection of rotation angles and rotation axes.

    Parameters
    ----------
    angles : ndarray
        Numpy array of shape (npts, ) storing a collection of rotation angles

    Returns
    -------
    matrices : ndarray
        Numpy array of shape (npts, 2, 2) storing a collection of rotation matrices

    Examples
    --------
    >>> npts = int(1e4)
    >>> angles = np.random.uniform(-np.pi/2., np.pi/2., npts)
    >>> rotation_matrices = rotation_matrices_from_angles(angles, directions)

    Notes
    -----
    The function `rotate_vector_collection` can be used to efficiently
    apply the returned collection of matrices to a collection of 2d vectors
    """

    angles = np.atleast_1d(angles)
    npts = len(angles)

    sina = np.sin(angles)
    cosa = np.cos(angles)

    R = np.zeros((npts, 2, 2))
    R[:, 0, 0] = cosa
    R[:, 1, 1] = cosa

    R[:, 0, 1] = sina
    R[:, 1, 0] = -sina
    
    return R


def rotation_matrices_from_vectors(v0, v1):
    r""" 
    Calculate a collection of rotation matrices defined by the unique
    transformation rotating v1 into v2 about the mutually perpendicular axis.

    Parameters
    ----------
    v0 : ndarray
        Numpy array of shape (npts, 2) storing a collection of initial vector orientations.

        Note that the normalization of `v0` will be ignored.

    v1 : ndarray
        Numpy array of shape (npts, 2) storing a collection of final vectors.

        Note that the normalization of `v1` will be ignored.

    Returns
    -------
    matrices : ndarray
        Numpy array of shape (npts, 2, 2) rotating each v0 into the corresponding v1

    Examples
    --------
    >>> npts = int(1e4)
    >>> v0 = np.random.random((npts, 2))
    >>> v1 = np.random.random((npts, 2))
    >>> rotation_matrices = rotation_matrices_from_vectors(v0, v1)

    Notes
    -----
    The function `rotate_vector_collection` can be used to efficiently
    apply the returned collection of matrices to a collection of 3d vectors

    """
    v0 = normalized_vectors(v0)
    v1 = normalized_vectors(v1)
    angles = angles_between_list_of_vectors(v0, v1)

    # where angles are 0.0, replace directions with v0
    mask = (angles==0.0)
    return rotation_matrices_from_angles(angles)


def random_perpendicular_directions(v, seed=None):
    r"""
    Given an input list of 2d vectors, v, return a list of 2d vectors
    such that each returned vector has unit-length and is
    orthogonal to the corresponding vector in v.
    
    Parameters
    ----------
    v : ndarray
        Numpy array of shape (npts, 2) storing a collection of 2d vectors
    seed : int, optional
        Random number seed used to choose a random orthogonal direction
    
    Returns
    -------
    result : ndarray
        Numpy array of shape (npts, 2)
    """
    v = np.atleast_2d(v)
    npts = v.shape[0]
    with NumpyRNGContext(seed):
        w = np.random.random((npts, 2))

    vnorms = elementwise_norm(v).reshape((npts, 1))
    wnorms = elementwise_norm(w).reshape((npts, 1))

    e_v = v/vnorms
    e_w = w/wnorms

    v_dot_w = elementwise_dot(e_v, e_w).reshape((npts, 1))

    e_v_perp = e_w - v_dot_w*e_v
    e_v_perp_norm = elementwise_norm(e_v_perp).reshape((npts, 1))
    return e_v_perp/e_v_perp_norm


def rotation2d(ux, uy):
    """
    Calculate a collection of rotation matrices defined by an input collection
    of basis vectors.
    
    Parameters
    ----------
    ux : array_like
        Numpy array of shape (npts, 2) storing a collection of unit vexctors
    
    uy : array_like
        Numpy array of shape (npts, 2) storing a collection of unit vexctors
    
    Returns
    -------
    matrices : ndarray
        Numpy array of shape (npts, 2, 2) storing a collection of rotation matrices
    """

    N = np.shape(ux)[0]

    # assume initial unit vectors are the standard ones
    ex = np.array([1.0, 0.0]*N).reshape(N, 3)
    ey = np.array([0.0, 1.0]*N).reshape(N, 3)

    ux = normalized_vectors(ux)
    uy = normalized_vectors(uy)

    r_11 = elementwise_dot(ex, ux)
    r_12 = elementwise_dot(ex, uy)

    r_21 = elementwise_dot(ey, ux)
    r_22 = elementwise_dot(ey, uy)

    r = np.zeros((N, 2, 2))
    r[:,0,0] = r_11
    r[:,0,1] = r_12
    r[:,1,0] = r_21
    r[:,1,1] = r_22

    return r