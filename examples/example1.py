__author__ = 'schriste'

from saaspy.image import image
import matplotlib.pyplot as plt

file = "/Users/schriste/Desktop/SAAS/FOXSI_SAAS_141113_203247.fits"

if __name__ == '__main__':
    s = image(file)
    plt.figure()
    s.imshow()
    plt.show()