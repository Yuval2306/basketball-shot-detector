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
        mask = cv2.inRange(cv2.cvtColor(region, cv2.COLOR_BGR2HSV), LOWER_ORANGE, UPPER_ORANGE)
        hoop_orange_vals.append(np.count_nonzero(mask))
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        if prev_gray is not None:
            hoop_motion_vals.append(np.count_nonzero(cv2.absdiff(gray, prev_gray) > 20))
        prev_gray = gray

    ORANGE_THRESHOLD = np.mean(hoop_orange_vals) * 1.5
    MOTION_THRESHOLD = np.mean(hoop_motion_vals) * 3.0
    print(f"Orange threshold: {ORANGE_THRESHOLD:.0f} | Motion threshold: {MOTION_THRESHOLD:.0f}")

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cooldown = 0
    first_ball_seen_ts = None
    frame_index = 0
    prev_hoop_gray = None

    print("\nCoreSport AI: Monitoring for shots...")

    while True:
        ret, frame = cap.read()
        if not ret: break
        timestamp = frame_index / fps

        hoop_region = frame[hy:hy+hh, hx:hx+hw]
        hoop_gray = cv2.cvtColor(hoop_region, cv2.COLOR_BGR2GRAY)
        orange_count = np.count_nonzero(cv2.inRange(cv2.cvtColor(hoop_region, cv2.COLOR_BGR2HSV), LOWER_ORANGE, UPPER_ORANGE))
        
        motion_count = 0
        if prev_hoop_gray is not None:
            motion_count = np.count_nonzero(cv2.absdiff(hoop_gray, prev_hoop_gray) > 20)
        
        ball_in_hoop = (orange_count > ORANGE_THRESHOLD) or (motion_count > MOTION_THRESHOLD)
        prev_hoop_gray = hoop_gray

        if ball_in_hoop and cooldown == 0:
            if first_ball_seen_ts is None:
                first_ball_seen_ts = timestamp
            elif (timestamp - first_ball_seen_ts) >= (3 / fps):
                print(f"timestamp: {first_ball_seen_ts:.2f}s – SHOT_MADE")
                cooldown = int(fps * 3)
                first_ball_seen_ts = None
        else:
            first_ball_seen_ts = None

        if cooldown > 0: cooldown -= 1
        
        cv2.rectangle(frame, (hx, hy), (hx+hw, hy+hh), (0, 255, 0) if ball_in_hoop else (255, 255, 255), 2)
        cv2.putText(frame, "Monitoring...", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("CoreSport AI", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
        frame_index += 1

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    video_path = sys.argv[1] if len(sys.argv) > 1 else "data/video1.mp4"
    main(video_path)