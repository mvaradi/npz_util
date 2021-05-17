# TODO Change matrix writer method for means (to create smaller matrix)
# TODO Deal with cases when the matrix is not the right size for the window
    # Remove the last element if needed

import sys
import ntpath

import numpy as np
from numpy.lib.stride_tricks import as_strided


class Loader(object):

    def __init__(self, path):
        self.path = path
        self.data = None
        self.tiled_data = None

    def load_file(self):
        """
        Loads the contents of a compressed .npz file

        The expected input file only has the contents of a single file (i.e. data.files[] has only 1 element)
        That single element is an array with a single embedded array-of-arrays:
        [[[0,1][2,3]]]

        :return: None
        """
        archive = np.load(self.path)
        self.data = archive[archive.files[0]][0]

    def get_data(self):
        """
        Get the data
        :return: Numpy array of arrays
        """
        return self.data

    def get_identifier(self):
        """
        Sets the identifier attribute

        The input file name is expected to be in the format of [identifier]_[*]+.npz
        For example: identifier_example.npz

        :return: None
        """
        return ntpath.basename(self.path).split('_')[0]

    def get_range(self):
        """
        Gets the minimum and maximum values from the data array-of-arrays

        :return: Tuple, min and max values in the data
        """
        return np.amin(self.data), np.amax(self.data)

    def create_tiled_data(self):
        """
        This method takes an input n x n numpy array-of-arrays (i.e. matrix) and creates a new matrix
        that has the average or an i x i size slice matrix in a new matrix

        For example:
        input = [[0,1],[2,3]]
        output with a window of 2x2 = [[1.5]]
        :return: Numpy array of arrays
        """
        data = self.data
        tiled_data = [data]
        while len(data) > 300:
            dimension = data.shape[0]
            if dimension % 2 != 0:
                trimmed_data = data[0:len(data)-1, 0:len(data)-1]
                data = trimmed_data
            data = self.sum_submatrices(data, 2)
            tiled_data.append(data)
        self.tiled_data = tiled_data
        return tiled_data

    def as_submatrices(self, x, rows, cols=None, writeable=False):
        """
        Create sub-matrices from an input Numpy array-of-arrays (i.e. matrix)
        It uses "rows" and "cols" to set the window size for getting the sub-matrices

        :param x: Numpy array (matrix)
        :param rows: Number; the size of the window in terms of rows
        :param cols: Number; the size of the window in terms of colums
        :param writeable: Boolean; seems to be required by "as_strided()"
        :return: Numpy array of sub-matrices
        """
        if cols is None: cols = rows
        x = np.asarray(x)
        x_rows, x_cols = x.shape
        s1, s2 = x.strides
        if x_rows % rows != 0 or x_cols % cols != 0:
            print(x_rows, rows, x_cols, cols)
            raise ValueError('Invalid dimensions.')
        out_shape = (x_rows // rows, x_cols // cols, rows, cols)
        out_strides = (s1 * rows, s2 * cols, s1, s2)
        return as_strided(x, out_shape, out_strides, writeable=writeable)

    def sum_submatrices(self, x, rows, cols=None):
        """
        Calculate the sum over a window in a matrix

        :param x: Numpy array (matrix)
        :param rows: Number; the size of the window in terms of rows
        :param cols: Number; the size of the window in terms of colums
        :return: Numpy array (matrix); same size as x
        """
        if cols is None:
            cols = rows
        x = np.asarray(x)
        x_sub = self.as_submatrices(x, rows, cols)
        x_sum = np.mean(x_sub, axis=(2, 3))
        return x_sum


if __name__ == "__main__":
    loader = Loader(sys.argv[1])
    loader.load_file()
    #
    # # Get data range
    # data_range = loader.get_range()
    # print("Min: %.2f" % data_range[0])
    # print("Max: %.2f" % data_range[1])

    # loader = Loader("")
    # x = np.arange(64).reshape((8, 8))
    # print(x)
    # print()
    # print(loader.sum_submatrices(x, 2))
    # print(loader.data)

    tiled_data = loader.create_tiled_data()



    # print(loader.create_tiled_data())

# x < 300 => nothing
# x < 600 => window 2
# 150 => 300 => 600 => 1200 => 2400 => 4800 => 9600


# 1153 > 576 > 288