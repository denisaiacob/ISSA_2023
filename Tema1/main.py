import cv2
import numpy as np

cam = cv2.VideoCapture('Lane Detection Test Video 01.mp4')

while True:
    ret, frame = cam.read()

    if ret is False:
        break

    # cv2.imshow('Original', frame)

    # Ex2 Shrink the frame!
    width = int(frame.shape[1] / 4)
    height = int(frame.shape[0] / 3)
    dim = (width, height)
    resized = cv2.resize(frame, dim)
    cv2.imshow("Small", resized)
    # .

    # Ex3 Convert the frame to Grayscale!
    gray_image = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    cv2.imshow("Grayscale", gray_image)
    # .

    # Ex4 Select only the road!
    # a.i
    # int(height *0,55/0,65)
    upper_right = (int(height * 0.55), int(width * 0.58))
    upper_left = (int(height * 0.75), int(width * 0.58))
    lower_left = (width, height)
    lower_right = (0, height)
    # a.ii
    trapezoid_points = np.array([upper_right, upper_left, lower_left, lower_right], dtype=np.int32)
    # a.iii
    trapezoid_frame = np.zeros((height, width), dtype=np.uint8)
    cv2.fillConvexPoly(trapezoid_frame, trapezoid_points, 1)
    # cv2.imshow("Trapezoid", trapezoid_frame * 255)
    # b
    cv2.imshow("Road", trapezoid_frame * gray_image)
    # .

    # Ex5 Get a top-down view!
    frame_points = np.array([(0, 0), (width, 0), (width, height), (0, height)], dtype=np.float32)
    trapezoid_bounds = np.float32(trapezoid_points)
    magic_matrix = cv2.getPerspectiveTransform(trapezoid_bounds, frame_points)
    top_down = cv2.warpPerspective(trapezoid_frame * gray_image, magic_matrix, (width, height-5))
    cv2.imshow("Top-Down", top_down)
    # .

    # Ex6 Add a bit of blur
    blur_frame = cv2.blur(top_down, ksize=(3, 3))
    cv2.imshow("Blur", blur_frame)
    # .

    # Ex7 Do edge detection
    sobel_vertical = np.float32([[-1, -2, -1], [0, 0, 0], [+1, +2, +1]])
    sobel_horizontal = np.transpose(sobel_vertical)
    blur1 = blur_frame.copy()
    blur1 = np.float32(blur1)
    blur2 = blur_frame.copy()
    blur2 = np.float32(blur2)
    matrix1 = cv2.filter2D(blur1, -1, sobel_vertical)
    matrix2 = cv2.filter2D(blur2, -1, sobel_horizontal)
    matrix3 = np.sqrt(matrix1 ** 2 + matrix2 ** 2)
    matrix3 = cv2.convertScaleAbs(matrix3)
    cv2.imshow("Sobel", matrix3)
    # .

    # Ex8  Binarize the frame!
    prag, binarized_frame = cv2.threshold(matrix3, 128, 255, cv2.THRESH_BINARY)
    cv2.imshow("Binarized", binarized_frame)
    # .

    # Ex9 Get the coordinates of street markings on each side of the road
    # a
    new_frame = binarized_frame.copy()
    new_frame[0:width, 0:int(width * 0.10)] = 0
    new_frame[0:width, -int(width * 0.10):width] = 0
    # b
    row, col = new_frame.shape
    col2 = col // 2
    left_frame = new_frame[:row, :col2]
    right_frame = new_frame[:row, col2:]
    left = np.argwhere(left_frame)
    right = np.argwhere(right_frame)

    left_xs = np.array([-1])
    left_ys = np.array([-1])
    right_xs = np.array([-1])
    right_ys = np.array([-1])

    for i in left:
        left_ys = np.append(left_ys, [i[0]])
        left_xs = np.append(left_xs, [i[1]])
    left_xs = np.delete(left_xs, 0)
    left_ys = np.delete(left_ys, 0)

    for i in right:
        right_ys = np.append(right_ys, [i[0]])
        right_xs = np.append(right_xs, [int(i[1] + col2)])
    right_xs = np.delete(right_xs, 0)
    right_ys = np.delete(right_ys, 0)
    # .

    # Ex10 Find the lines that detect the edges of the lane!
    # a
    left_b, left_a = np.polynomial.polynomial.polyfit(left_xs, left_ys, deg=1)
    right_b, right_a = np.polynomial.polynomial.polyfit(right_xs, right_ys, deg=1)
    # b
    left_top_y = 0
    left_top_x = int((left_top_y - left_b) / left_a)
    left_bottom_y = height
    left_bottom_x = int((left_bottom_y - left_b) / left_a)

    right_top_y = 0
    right_top_x = int((right_top_y - right_b) / right_a)
    right_bottom_y = height
    right_bottom_x = int((right_bottom_y - right_b) / right_a)
    # c
    left_top = int(left_top_x), int(left_top_y)
    left_bottom = int(left_bottom_x), int(left_bottom_y)
    right_top = int(right_top_x), int(right_top_y)
    right_bottom = int(right_bottom_x), int(right_bottom_y)

    # d
    middle1 = int(width / 2), 0
    middle2 = int(width / 2), height
    if np.abs(left_top[0]) < 10 ** 8:
        cv2.line(binarized_frame, left_top, left_bottom, (200, 0, 0), 5)
    if np.abs(right_top[0]) < 10 ** 8:
        cv2.line(binarized_frame, right_top, right_bottom, (100, 0, 0), 5)
    cv2.line(binarized_frame, middle1, middle2, (255, 0, 0), 1)
    cv2.imshow("Lines", binarized_frame)
    # .

    # Ex11
    final_new_frame1 = np.zeros((height, width), dtype=np.uint8)
    final_new_frame2 = np.zeros((height, width), dtype=np.uint8)
    # b
    if np.abs(left_top[0]) < 10 ** 8:
        cv2.line(final_new_frame1, left_top, left_bottom, (255, 0, 0), 3)
    if np.abs(right_top[0]) < 10 ** 8:
        cv2.line(final_new_frame2, right_top, right_bottom, (255, 0, 0), 3)
    # c
    magic_matrix = cv2.getPerspectiveTransform(np.float32(frame_points), np.float32(trapezoid_points))
    # d
    final_new_frame1 = cv2.warpPerspective(final_new_frame1, magic_matrix, (width, height))
    final_new_frame2 = cv2.warpPerspective(final_new_frame2, magic_matrix, (width, height))
    # e
    coordinates_left_line = np.argwhere(final_new_frame1)
    coordinates_right_line = np.argwhere(final_new_frame2)
    # g
    final_frame = resized.copy()
    for i in coordinates_left_line:
        final_frame[i[0]][i[1]] = [50, 50, 250]
    for j in coordinates_right_line:
        final_frame[j[0]][j[1]] = [50, 250, 50]
    cv2.imshow("Final", final_frame)
    # .

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()

