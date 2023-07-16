import cv2
import mediapipe as mp
import time
import hand_tracking_module as ht
import math
# import mouse
# import win32api, win32con
from pynput.mouse import Button, Controller

def dist_points(p1, p2):
   dist = math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
   return dist

def dist_line_and_point(a, b, p): # y = a + bx
   numer = abs(b*p[0]-p[1] + a)
   denum = math.sqrt(b*b + 1)
   dist = numer / denum
   return dist

def best_fit(points):
   X = [point[0] for point in points]
   Y = [point[1] for point in points]
   xbar = sum(X)/len(X)
   ybar = sum(Y)/len(Y)
   n = len(X) # or len(Y)

   numer = sum([xi*yi for xi,yi in zip(X, Y)]) - n * xbar * ybar
   denum = sum([xi**2 for xi in X]) - n * xbar**2

   b = numer / denum
   a = ybar - b * xbar

   return a, b

def best_fit_intersect(points, intersect_point): # best fit line which intersects specified point
   X = [point[0] for point in points]
   Y = [point[1] for point in points]
   n = len(X)

   mean_X = sum(X) / n
   mean_Y = sum(Y) / n
   numerator = sum((xi) * (yi) for xi, yi in zip(X, Y))  - n * mean_X * mean_Y
   denominator = sum((xi) ** 2 for xi in X) - n * mean_X**2
   b = numerator / denominator

   a = intersect_point[1] - b * intersect_point[0]

   return a, b

# def interp_depth_from_distance_linear(min, max):
#    c = []
#    d = []
#    for i in range(0,3):
#       x1 = min[i][0]
#       y1 = min[i][1]
#       x2 = max[i][0]
#       y2 = max[i][1]
#       c.append((y2-y1)/(x2-x1))
#       d.append(y1 - c[i] * x1)
#    # print(c,d)
#    return c,d

# max = [[20.515,71], [13.693,71], [11.233,71]] # [distance in px, depth in cm]
# min = [[56.943,0], [37.196,0], [30.723,0]] # [distance in px, depth in cm]
# c,d = interp_depth_from_distance_linear(min, max)

# def depth_from_distance_linear(c, d, x):
#    depth = 0
#    # y=cx+d, where y=depth and x=distance
#    for i in range(0, 3):
#       depth += c[i] * x[i] + d[i]
#    print(depth, x)
#    depth /= 3
#    return depth

distance_to_screen = 34 # cm
max = [[20.515,71 + distance_to_screen], [13.693,71 + distance_to_screen], [11.233,71 + distance_to_screen]] # [length in px, depth in cm]
# d_max = # max depth in cm
# l_1 = # length at Rmax depth in px
def depth_from_length(l_1, l_2, l_3, l_4):
   # d = f(l) = (l_max * d_max) / l
   d_1 = (max[0][1] * max[0][0]) / l_1
   d_2 = (max[1][1] * max[1][0]) / l_2
   d_3 = (max[2][1] * max[2][0]) / l_3
   d_4 = ((max[0][0] + max[1][0] + max[2][0]) * 105) / l_4
   d = (d_4)
   return d

failure = False

average_of = 2

pTime = 0
cTime = 0
cap = cv2.VideoCapture(1)
detector = ht.handDetector(detectionCon = 0.7, trackCon = 0.7)

reject_valid = 0
frame = 0

x=0
y_i = 0
dist_1_2 = 0
dist_2_3 = 0
dist_3_4 = 0
dist_1_4 = 0

failure_x = False
reject_valid_x = 0
prev_valid_x = 0
prev_invalid_x = 0

points = []
points_prev_valid = []
points_prev_invalid = []

SCREEN_X = -2560
SCREEN_Y = 1447

time.sleep(1)
mouse = Controller()
mouse.press(Button.left)

# draw = dm.Draw(SCREEN_X, SCREEN_Y)
while True:
   # pyautogui.displayMousePosition()
   # video
   try:
      cTime = time.time() # current time
      fps = 1/(cTime - pTime)
      pTime = cTime

      # decorations

      cv2.putText(img, "X:"+str(x), (100,70), cv2.FONT_HERSHEY_PLAIN, 2,
               (200,50,200),3)
      cv2.putText(img, "Y:"+str(y), (100,110), cv2.FONT_HERSHEY_PLAIN, 2,
                  (200,50,200),3)

      for i in range(0,4):
         if points:
            draw_point = points[i]
            cv2.circle(img, (draw_point[0], draw_point[1]), 3, (205,2,205), 2)

      cv2.line(img, (10,620), (10, 6), (205,2,205), 2)
      cv2.putText(img, "F:"+str(int(fps)), (100,30), cv2.FONT_HERSHEY_PLAIN, 2, # on image, display fps, position, font, font size
                  (200,50,200),3) # color and thickess

      img_scaled = cv2.resize(img, (int(2 * w), int(2 * h)))
      cv2.imshow("Image",img_scaled)
      cv2.waitKey(1)
   except:
      None


   success, img = cap.read()  # video = img
   img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
   h,w,_ = img.shape

   x_crop_l, y_crop_l = 250, 0
   x_crop_r, y_crop_r = 0, 0
   # Crop image to specified area using slicing
   img = img[y_crop_l:h-y_crop_r, x_crop_l:w-x_crop_r]
   w = w-x_crop_r-x_crop_l # new height and width
   h = h-y_crop_r-y_crop_l

   detector.findHands(img, draw=False)
   lmList = detector.findPosition(img, lmNo = 8) # return list of all landmarks, but only draw one

   # reduce noise by keeping points in the same position if they are close /
   # ensure finger is straight by referencing 4 points (pitch straightness) /
   # measure distance between points/
   # calculate the ratio between the distances, if this ratio is valid, the depth will be calculated from the min and max distance by interpolation (yaw straightness)/
   # the y value is calculated from image y and corrected using depth /
   # final point is determined /

   if lmList:
      #! remove noise
      points = []
      for i in range(5, 9): #the pointer is point 8
         point = lmList[i]
         point = [point[1], point[2]]
         if points_prev_valid:
            point_prev = points_prev_valid[i-5]
            if dist_points(point, point_prev) < 2: # jitter reduction
               point = point_prev

         points.append(point)

      #! remove anomalous detection
      if points_prev_valid:
         if dist_points(points[3], points_prev_valid[3]) > 20: #* failure 2 - rejected position
            # a new position of pointer is chosen when it is rejected and has stayed in the same place consistently (valid rejection), a rejection is done when the pointer is too far from its previous position and a valid rejection has not been found. if there is no consistency, a position is not chosen
            if points_prev_invalid:
               if dist_points(points_prev_invalid[3], points[3]) < 7: # a valid rejection
                  reject_valid += 1 # it will loop here until a new position is resolved
                  if reject_valid >= 7: # new position resolved
                     print("reject-accept")
                     failure = False
                     reject_valid = 0
                     points_prev_invalid = []

                     frame = 0
                     y_i = 0
                     dist_1_2 = 0
                     dist_2_3 = 0
                     dist_3_4 = 0
                     dist_1_4 = 0
                  else: # consistency but unresolved
                     failure = True
               else: # no consistency
                  reject_valid = 0
                  failure = True
            else: # no prev
               reject_valid = 0
               failure = True
         else: # pass
            reject_valid = 0
            failure = False

      if failure:
         print("failure")
         points_prev_invalid = list(points)
         depth = 0
         y=0
         continue

      #! length over an average of points to reduce number of drawn points and increase stability
      y_i += points[3][1] # interpreted or displayed y in px
      dist_1_2 += dist_points(points[0], points[1])
      dist_2_3 += dist_points(points[1], points[2])
      dist_3_4 += dist_points(points[2], points[3])
      dist_1_4 += dist_points(points[0], points[3])
      # print("add", frame, dist_1_2)
      if frame >= average_of:
         # print("divide", frame, dist_1_2)
         y_i /= average_of # interpreted or displayed y in px
         dist_1_2 /= average_of
         dist_2_3 /= average_of
         dist_3_4 /= average_of
         dist_1_4 /= average_of

         #! verify the placement of the hand using length
         ratio_wrt_3_4 = [dist_2_3/dist_3_4, dist_1_2/dist_3_4]
         ratio_wrt_3_4_reference = [1.2189543649971524, 1.826286508102113]
         ratio_validity = True if (abs(ratio_wrt_3_4[0]/ratio_wrt_3_4_reference[0] - 1) < 0.2) and (abs(ratio_wrt_3_4[1]/ratio_wrt_3_4_reference[1] - 1) < 0.2) else False

         #! verify the straightness of the finger using best fit line
         a,b = best_fit_intersect(points, points[3]) # best fit y=bx+a which itersects the pointer
         straight = 0
         # print(dist_line_and_point(a,b,points[handNo][3]))
         for i in range(0,3):
            # print(points[handNo][i], a ,b, dist_line_and_point(a,b,points[handNo][i]))
            if dist_line_and_point(a,b,points[i]) < 10:
               straight+=1
         if straight == 3:
            straightness_validity = True
            cv2.line(img, (0,int(a)), (w, int(b*w+a)), (50,205,50), 1)
         else:
            straightness_validity = False
            cv2.line(img, (0,int(a)), (w, int(b*w+a)), (50,205,205), 1)

         #! calculate the depth from the length
         if ratio_validity and straightness_validity:
            depth = depth_from_length(dist_1_2,dist_2_3,dist_3_4,dist_1_4)
            # print(y_i, h/2, y_i - h/2)
            y_i -= h/2
            y = ((y_i * depth) / distance_to_screen) + h/2
            depth -= distance_to_screen

            # map depth and y to value between 0-1. multiply by screen resolution.
            y /= h
            depth = depth / 71

            y = y * SCREEN_Y
            x = (1 - depth) * SCREEN_X
            if prev_valid_x:
               if abs(x - prev_valid_x) > 40:
                  if prev_invalid_x:
                     if abs(prev_invalid_x - x) < 40:
                        reject_valid_x += 1
                        if reject_valid_x >= 1:
                           reject_valid_x = 0
                           prev_invalid_x = 0
                           failure_x = False
                        else:
                           failure_x = True
                     else:
                        reject_valid_x = 0
                        failure_x = True
                  else:
                     reject_valid_x = 0
                     failure_x = True
               else:
                  failure = False
            else:
               failure_x = False
               prev_valid_x = x

            if failure_x:
               prev_invalid_x = x
               print("reject depth")
            else:
               mouse.press(Button.left)
               mouse.position = (x, y)
               mouse.release(Button.left)
               prev_valid_x = x

         else: #* failure 3 - invalid hand arrangement
            print("invalid hand arrangement")
            depth = 0
            y=0

         y_i = 0
         dist_1_2 = 0
         dist_2_3 = 0
         dist_3_4 = 0
         dist_1_4 = 0

      frame = (frame % average_of) + 1

      points_prev_valid = list(points)

   else: #* failure 1 - no hand
      mouse.release(Button.left)
      failure = False
      reject_valid = 0
      points_prev_invalid = []
      points_prev_valid = []
      points = []

      frame = 0
      y_i = 0
      dist_1_2 = 0
      dist_2_3 = 0
      dist_3_4 = 0
      dist_1_4 = 0

      depth = 0
      y=0
      continue
