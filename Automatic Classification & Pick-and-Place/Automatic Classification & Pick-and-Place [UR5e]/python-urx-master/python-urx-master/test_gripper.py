import sys
import urx
import time
from urx.gripper import OnRobotGripperRG2

if __name__ == '__main__':
    rob = urx.Robot("192.168.0.2")
    gripper = OnRobotGripperRG2(rob)
    
    rob.set_tcp((0, 0, 0.1, 0, 0, 0))
    rob.set_payload(2, (0, 0, 0.1))
    
    rob.set_tool_voltage(24)
    
    #rob.set_analog_out
    #gripper.open_gripper()

    gripper.open_gripper(
        target_width=110,          # Width in mm, 110 is fully open
        target_force=40,           # Maximum force applied in N, 40 is maximum
        payload=0.5,               # Payload in kg
        set_payload=False,         # If any payload is attached
        depth_compensation=False,  # Whether to compensate for finger depth
        slave=False,               # Is this gripper the master or slave gripper?
        wait=3                     # Wait up to 2s for movement
    )

    print("done")
    rob.close()
    sys.exit()

# import sys
# import urx
# from urx.gripper import OnRobotGripperRG2

# if __name__ == '__main__':
#     rob = urx.Robot("192.168.0.2")
#     gripper = OnRobotGripperRG2(rob)

#     if len(sys.argv) != 2:
#         print("false")
#         sys.exit()

#     if sys.argv[1] == "close":
#         gripper.close_gripper()
#     if sys.argv[1] == "open":
#         gripper.open_gripper()

#     rob.close()
#     print("true")
#     sys.exit()

import sys
import urx
from urx.gripper import OnRobotGripperRG2
if __name__ == '__main__':
    rob = urx.Robot("192.168.0.2")
    gripper = OnRobotGripperRG2(rob)
    if len(sys.argv) != 2:
       print("false")
       sys.exit()
    if sys.argv[1] == "close":
        gripper.close_gripper()
    if sys.argv[1] == "open":
        gripper.open_gripper()
    rob.close()
    print("true")
    sys.exit()