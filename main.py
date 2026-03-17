import cv2
import numpy as np
import sys
import requests
import webbrowser

# Target URL for the Mock API server
API_URL = "http://localhost:5000/event"

def send_shot_event(timestamp):
    """
    Sends a POST request to the API endpoint when a shot is detected.
    Includes the specific timestamp of the event.
    """
    payload = {"event": "shot_made", "timestamp": round(float(timestamp), 2)}
    try:
        # Attempt to send data to the server with a short timeout
        response = requests.post(API_URL, json=payload, timeout=0.8)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        # Gracefully handle connection errors (e.g., if the server is offline)
        return False

def get_roi_from_user(frame, title):
    """
    Opens a UI window allowing the user to manually select the 
    Region of Interest (ROI) for the basketball hoop.
    """
    print(f"--- Calibration: Please select the {title} and press ENTER ---")
    # OpenCV built-in function for manual bounding box selection
    roi = cv2.selectROI(f"Select {title}", frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow(f"Select {title}")
    return roi

def main(video_path):
    # Initialize video capture
    cap = cv2.VideoCapture(video_path)
    ret, first_frame = cap.read()
    if not ret:
        print("Error: Could not read video file.")
        return

    # Calibration Phase: Define where the hoop is located
    hoop_roi = get_roi_from_user(first_frame, "HOOP AREA")
    hx, hy, hw, hh = hoop_roi

    # Define the HSV range for detecting the orange basketball
    LOWER_ORANGE = np.array([0, 100, 100])
    UPPER_ORANGE = np.array([25, 255, 255])

    # --- Dynamic Baseline Computation ---
    print("Computing baselines...")
    hoop_orange_vals, hoop_motion_vals = [], []
    prev_gray = None
    
    # Analyze the first 40 frames to establish 'normal' noise levels in the hoop area
    for fi in range(40):
        cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
        ret, f = cap.read()
        if not ret: break
        
        # Crop to the hoop ROI
        region = f[hy:hy+hh, hx:hx+hw]
        
        # Measure initial orange color presence
        mask = cv2.inRange(cv2.cvtColor(region, cv2.COLOR_BGR2HSV), LOWER_ORANGE, UPPER_ORANGE)
        hoop_orange_vals.append(np.count_nonzero(mask))
        
        # Measure initial motion levels (Frame Differencing)
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        if prev_gray is not None:
            hoop_motion_vals.append(np.count_nonzero(cv2.absdiff(gray, prev_gray) > 20))
        prev_gray = gray

    # Set sensitivity thresholds based on the environment's baseline
    ORANGE_THRESHOLD = np.mean(hoop_orange_vals) * 1.5
    MOTION_THRESHOLD = np.mean(hoop_motion_vals) * 3.0
    print(f"Orange threshold: {ORANGE_THRESHOLD:.0f} | Motion threshold: {MOTION_THRESHOLD:.0f}")

    # Prepare for the main processing loop
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cooldown = 0
    first_ball_seen_ts = None
    frame_index = 0
    prev_hoop_gray = None

    print("\n Basketball Shooting: Monitoring for shots...")

    # --- Main Video Processing Loop ---
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        # Calculate current video time in seconds
        timestamp = frame_index / fps

        # Process the hoop area for ball detection
        hoop_region = frame[hy:hy+hh, hx:hx+hw]
        hoop_gray = cv2.cvtColor(hoop_region, cv2.COLOR_BGR2GRAY)
        
        # Detect orange pixels
        orange_count = np.count_nonzero(cv2.inRange(cv2.cvtColor(hoop_region, cv2.COLOR_BGR2HSV), LOWER_ORANGE, UPPER_ORANGE))
        
        # Detect motion pixels
        motion_count = 0
        if prev_hoop_gray is not None:
            motion_count = np.count_nonzero(cv2.absdiff(hoop_gray, prev_hoop_gray) > 20)
        
        # Logic: Ball is "detected" if either orange or motion exceeds the threshold
        ball_in_hoop = (orange_count > ORANGE_THRESHOLD) or (motion_count > MOTION_THRESHOLD)
        prev_hoop_gray = hoop_gray

        # Event Trigger Logic: Ball must persist in the hoop area for a minimum duration
        if ball_in_hoop and cooldown == 0:
            if first_ball_seen_ts is None:
                first_ball_seen_ts = timestamp
            elif (timestamp - first_ball_seen_ts) >= (3 / fps):
                # Trigger detected: Output to console and send API request
                print(f"timestamp: {first_ball_seen_ts:.2f}s – SHOT_MADE")
                send_shot_event(first_ball_seen_ts) 
                
                # Prevent multiple triggers for the same shot (3-second cooldown)
                cooldown = int(fps * 3)
                first_ball_seen_ts = None
        else:
            # Reset if the ball leaves the area too quickly
            first_ball_seen_ts = None

        if cooldown > 0: cooldown -= 1
        
        # --- Visualization ---
        # Draw the hoop box: Green if ball detected, White otherwise
        cv2.rectangle(frame, (hx, hy), (hx+hw, hy+hh), (0, 255, 0) if ball_in_hoop else (255, 255, 255), 2)
        cv2.putText(frame, "Basketball Shooting - Active", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Basketball Shooting", frame)
        
        # Key listeners
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): # Quit
            break
        elif key == ord('o'): # Open API Dashboard in browser
            webbrowser.open(API_URL)
            
        frame_index += 1

    # Cleanup resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Support command line arguments for video path
    video_path = sys.argv[1] if len(sys.argv) > 1 else "data/video1.mp4"
    main(video_path)