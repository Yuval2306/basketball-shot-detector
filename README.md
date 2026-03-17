#  Basketball Shot Detector

A Python system that detects when a basketball goes through the hoop and reports the event to an API in real time.

---

## Project Structure

```
basketball-shot-detector/
├── main.py                          # Shot detection – video processing
├── mock_server.py                   # Flask API server + live dashboard
├── requirements.txt                 # Dependencies
├── Dockerfile                       # Linux/Docker support
├── System Design Thinking.pdf       # System design document (Part 3)
└── data/
    ├── video1.mp4
    └── video2.mp4
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## How to Run

**Terminal 1 – Start the API server:**
```bash
python mock_server.py
```

**Terminal 2 – Run the detector:**
```bash
python main.py data/video1.mp4
```

When the video opens, draw a box around the **hoop ring** and press ENTER.

| Key | Action |
|-----|--------|
| `Q` | Quit |
| `O` | Open dashboard in browser |

**Expected output:**
```
timestamp: 9.16s – SHOT_MADE
```

---

## Docker & Linux

The project runs on Linux and supports Docker deployment.

**Build:**
```bash
docker build -t basketball-detector .
```

**Run:**
```bash
docker run --net=host -v $(pwd)/data:/app/data basketball-detector data/video1.mp4
```

> `--net=host` allows the container to communicate with the mock server running on your machine.

--- 

## Solution Approach

1. **Calibration** – The user selects the hoop area on the first frame. The system analyzes the first 40 frames to compute baseline thresholds automatically.

2. **Ball Detection** – Two methods combined:
   - *Color detection* – counts orange pixels (HSV) in the hoop zone
   - *Motion detection* – frame differencing to catch any movement in the zone

3. **Event Trigger** – Ball must stay in the zone for 3+ consecutive frames to avoid false positives. A 3-second cooldown prevents double-counting.

4. **API Integration** – On detection, sends a POST request to `http://localhost:5000/event` with the event name and timestamp. Connection errors are handled gracefully.

---

## Author

[Yuval Boker](https://www.linkedin.com/in/yuval-boker-43792537b/)