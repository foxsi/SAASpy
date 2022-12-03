# -*- coding: utf-8 -*-
__author__ = 'Steven Christe'

from astropy.io import fits

from skimage import feature
from skimage.transform import hough_circle
from skimage.feature import peak_local_max
from skimage.draw import circle_perimeter
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from datetime import datetime


class image(object):
    def __init__(self, filename):
        """
        A class to handle a SAAS fits image.

        :param filename: Path to SAAS fits file as a string.

        properties
        ----------
        data: holds the data in the fits file
        header: holds the fits header (i.e. meta data)
        roi: the region of interest [x1, x2, y1, y2]
        fov: the field of view of the Region of Interest
        calibrated_center: the calibrated center of the SAAS [x, y]
        max_index: the index of the maximum pixel
        exposure: exposure time in seconds
        date: datetime object when image was taken
        """
        self.filename = filename
        try:
            f = fits.open(filename)
        except Exception:
            print("Warning. Can't open file %f" % filename)
            f = None

        if f is not None:
            self.data = f[1].data
            self.data = self.data.astype(np.ubyte)
            self.header = f[0].header
            self.max_index = np.unravel_index(self.data.argmax(), np.shape(self.data))
            self.fov = np.array([100, 100])
            self.roi = None
            # Set the default roi as the entire image
            self.roi_reset()
            self.calibrated_center = np.array([659, 483])
            self.exposure = self.header.get('EXPTIME')
            self.gain_preamp = self.header.get('GAIN_PRE')
            self.gain_analog = self.header.get('GAIN_ANA')
            self.date = datetime.strptime(self.header.get("DATE_OBS"), "%c")
            self.max = np.max(self.data)
            self.min = np.min(self.data)
            self.std = np.std(self.data)

    def imshow(self):
        """
        Plot the image.
        """
        ax = plt.imshow(self.roi_data, origin='upper', cmap=cm.Greys_r, vmin=0, vmax=255)
        plt.title('FOXSI SAAS ' + self.header['DATE_OBS'])
        ax.set_interpolation('nearest')

    def overlay(self):
        """
        Overplot a pre-defined overlay onto the image plot.
        """
        plt.plot(self.calibrated_center[0], self.calibrated_center[1], 'x')
        plt.plot(self.max_index[1], self.max_index[0], ".")
        plt.axhline(self.calibrated_center[1], self.calibrated_center[1])
        plt.axvline(self.calibrated_center[0], self.calibrated_center[0])
        # circle1 = plt.circle(self.calibrated_center, 10)
        #circle2 = plt.circle(self.calibrated_center, 20)
        #circle3 = plt.circle(self.calibrated_center, 30)
        #fig = plt.gcf()
        #fig.gca().add_artist(circle1)
        #fig.gca().add_artist(circle2)
        #fig.gca().add_artist(circle3)

    def roi_auto(self):
        """
        Set the region of interest (ROI) automatically centered around the image max.
        """
        self.roi = np.array([self.max_index[1] - self.fov[0] * 0.5, self.max_index[1] + self.fov[0] * 0.5,
                             self.max_index[0] - self.fov[1] * 0.5, self.max_index[0] + self.fov[1] * 0.5])

    @property
    def roi_data(self):
        """
        The data inside the ROI.

        :return: nd.array
        """
        return self.data[self.roi[2]:self.roi[3], self.roi[0]:self.roi[1]]

    def roi_reset(self):
        """
        Set the region of interest (ROI) to the entire image.
        """
        self.roi = [0, np.shape(self.data)[1], 0, np.shape(self.data)[0]]

    def hist(self):
        """
        Plot a histogram of the image.
        """
        plt.hist(self.roi_data.ravel())

    def set_fov(self, fov):
        """
        Set the field of the view of the ROI.

        """
        self.fov = fov
        self.roi = np.array([self.max_index[1] - self.fov[0] * 0.5, self.max_index[1] + self.fov[0] * 0.5,
                             self.max_index[0] - self.fov[1] * 0.5, self.max_index[0] + self.fov[1] * 0.5])


def find_center(saas_image, sigma=0.8, num_circles=5):
    """
    Find the center of the image

    :param saas_image: A SAAS image object.
    :param sigma: The amount of gaussian blurring
    :param num_circles: The number of circles to find.

    Returns:

    """
    edges = feature.canny(saas_image.roi_data, sigma=sigma)
    hough_radii = np.arange(10, 70, 1)
    hough_res = hough_circle(edges, hough_radii)
    centers = []
    accums = []
    radii = []
    for radius, h in zip(hough_radii, hough_res):
        # For each radius, extract two circles
        peaks = peak_local_max(h, num_peaks=2)
        if peaks != []:
            centers.extend(peaks)
            accums.extend(h[peaks[:, 0], peaks[:, 1]])
            radii.extend([radius, radius])

    best_centers = []
    best_radii = []
    best_x = []
    best_y = []
    number_of_best_circles = num_circles
    for idx in np.argsort(accums)[::-1][:number_of_best_circles]:
        center_x, center_y = centers[idx]
        best_x.append(center_x)
        best_y.append(center_y)
        best_centers.append(centers[idx])
        best_radii.append(radii[idx])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 6))
    ax1.imshow(edges)
    ax2.imshow(self.roi_data, cmap=cm.gray)
    for center, radius in zip(best_centers, best_radii):
        circle = plt.Circle((center[1], center[0]), radius, color='r', fill=False)
        ax2.add_patch(circle)
    print("Calibrated Center X = %s +/- %s" % (np.average(best_x), np.std(best_x)))
    print("Calibrated Center Y = %s +/- %s" % (np.average(best_y), np.std(best_y)))
    return np.array([[np.average(best_x), np.std(best_x)],
                     [np.average(best_y), np.std(best_y)]])
