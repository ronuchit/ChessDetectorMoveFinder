#!/usr/bin/env python

import rospy
import cv2
import threading
import os
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

IMAGE_F_NAME = "../images/pic.jpg"
end = False

def callback(data, bridge):
    img = bridge.imgmsg_to_cv2(data, "bgr8")
    cv2.imwrite(IMAGE_F_NAME, img)
    cv2.imshow("img", img)
    cv2.waitKey(5)

def listener():
    bridge = CvBridge()
    rospy.init_node("listener", anonymous=True, disable_signals=True)
    rospy.Subscriber("/camera/rgb/image_raw", Image, callback, bridge)
    while not end:
        pass
    cv2.destroyAllWindows()

def main():
    t = threading.Thread(target=listener)
    t.start()
    try:
        while True:
            os.system("scp -i ~/.ssh/id_rsa.pub %s temp@lfd2.banatao.berkeley.edu:~"%(IMAGE_F_NAME))
            rospy.sleep(0.5)
    except KeyboardInterrupt as e:
        global end
        end = True
        raise e

if __name__ == '__main__':
    main()
