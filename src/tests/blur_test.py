"""
Testing file for observing the effects of the preprocessing pipeline,
blur detection, and contour detection.

**( EXPERIMENTAL )
"""

import cv2
from src.classes.ContourProcessor import ContourProcessor


if __name__ == "__main__":
    cp = ContourProcessor()

    # base = cv2.imread("./tests/blur_img/baseline.png")
    # std = cv2.imread("./tests/blur_img/standard.png")
    # img1 = cv2.imread("./tests/blur_img/im1.png")
    # img2 = cv2.imread("./tests/blur_img/im2.png")
    # img3 = cv2.imread("./tests/blur_img/im3.png")

    # for i in [base, std, img1, img2, img3]:
    #     print(cp.calculate_blur(i, True))
    # # new = cp.apply_brightness_contrast(img3, 0, 400)
    # # new = cp.apply_brightness_contrast(new, 2, 127)
    # new = img3
    # post, blur = cp.apply_pipeline(new)
    # contours, blur = cp.get_contours(new, debug_mode=True)
    # cv2.imshow("im", post)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # cp.plot_contours(contours)

    ##################################################################

    std = cv2.imread("./tests/blur_img/standard.png")
    # post = cp.apply_cuda_pipeline(std)
    post = cp.apply_cuda_pipeline(std)
    cv2.imshow("im", post)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
