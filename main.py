import cv2
import numpy as np
import sys

def get_roi_from_user(frame, title):
    print(f"--- Calibration: Please select the {title} and press ENTER ---")
    roi = cv2.selectROI(f"Select {title}", frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow(f"Select {title}")
    return roi

def main(video_path):
    cap = cv2.VideoCapture(video_path)
    ret, first_frame = cap.read()
    if not ret:
        print("Error: Could not read video file.")
        return

    hoop_roi = get_roi_from_user(first_frame, "HOOP AREA")
    hx, hy, hw, hh = hoop_roi

    LOWER_ORANGE = np.array([0, 100, 100])
    UPPER_ORANGE = np.array([25, 255, 255])

    print("Computing baselines...")
    hoop_orange_vals, hoop_motion_vals = [], []
    prev_gray = None
    
    for fi in range(40):
        cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
        ret, f = cap.read()
        if not ret: break
        
        region = f[hy:hy+hh, hx:hx+hw]
        
        hsv_region = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_region, LOWER_ORANGE, UPPER_ORANGE)
        hoop_orange_vals.append(np.count_nonzero(mask))
        
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        if prev_gray is not None:
            diff = cv2.absdiff(gray, prev_gray)
            hoop_motion_vals.append(np.count_nonzero(diff > 20))
        prev_gray = gray

    ORANGE_THRESHOLD = np.mean(hoop_orange_vals) * 1.5
    MOTION_THRESHOLD = np.mean(hoop_motion_vals) * 3.0
    
    print(f"Orange threshold: {ORANGE_THRESHOLD:.0f} | Motion threshold: {MOTION_THRESHOLD:.0f}")
    print("\nBaseline computation complete. Ready for main loop.")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/video1.mp4"
    main(path)