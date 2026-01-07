# Dino-Runner

Dino-Runner is an advanced automation bot that plays Chrome's offline T-Rex game autonomously. Using real-time screen capture, edge detection algorithms, and dynamic obstacle recognition, the bot achieves elite performance and can accumulate scores over 30,000 points.

### Highlights
- **Adaptive Vision System**: Dynamically scales field-of-view based on game speed.
- **Intelligent Jump Detection**: Uses Canny edge detection with configurable sensitivity thresholds. Determines which type of jump to used based on the height of the obstacle.
- **Performance Optimised**: Achieves 1,000+ point scores consistently and regularly hits over 10,000 points every 1 in 5 attempts.
- **Cross-Monitor Support**: Automatically calibrates to your specific display setup.

---

### Computer Vision
- Real-time screen capture using `mss` 
- Template matching for dino and replay button detection
- Multi-scale image recognition for different DPI settings
- Adaptive Region of Interest scaling based on game velocity


### Analytics & Monitoring
- Round-by-round performance tracking
- Statistical analysis (mean, median, best/worst scores)
- Vision range debugging output
- Automatic game-over detection

---

##  Installation

### Prerequisites

- **Python**
- **uv** ([installation guide](https://github.com/astral-sh/uv))
- **Chrome Browser**
- **Windows** (not required, but recommended)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone git@github.com:HarryAidanCSC/Dino-Runner.git
   cd Dino-Runner
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Verify installation**
   ```bash
   uv run src/main.py
   ```

---

### Usage

### Basic Execution
1. Start by opening a chrome browser (it can be minimised)
2. Run the command below
```bash
uv run src/main.py
```
3. Press `Ctrl+C` to stop

Note that the chrome window and tab will automatically be setup perfectly for the bot to work.

### Configuration

Edit `src/Bot.py` to customize performance:

```python
# Vision System
self.SCALE_RATE = 1.3      # Vision expansion rate (pixels/second)
self.MAX_DELTA_WIDTH = 140  # Maximum lookahead distance

# Jump Detection
edge_threshold=60           # Sensitivity (50-80 recommended)

# ROI Update Frequency
frame_count % 5 == 0       # Update every N frames
```

You can also adjust values in the `ScreenRecorder.py` file to customise the template matching and game-over detection. 

---

## How It Works

```
┌─────────────────┐
│  ScreenRecorder │  ──► Captures game region via mss
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ FrameProcessor  │  ──► Detects obstacles using Canny edges
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│      Bot        │  ──► Executes jumps, manages game loop
└─────────────────┘
```

---

## Performance

### Benchmark Results

Highest score: 32,410 


## Known Issues

### Bot Not Detecting Game

**Issue**: "No dino found" error  
**Solution**: 
- Ensure dino is fully visible on screen
- Try adjusting `dino_threshold` in `ScreenRecorder.__init__()`
- Check `template_dino.png` matches your game's dino sprite

### Inconsistent Performance

**Issue**: Sometimes certain rounds perform well, subsequent rounds fail very early on.
**Solution**:
- Verify `gc.collect()` is called between rounds
- Check that ROI scaling resets properly
- Ensure game window doesn't move between rounds
- Run again a few times to see if the issue persists or is just bad RNG.

### Bot not resetting correctly

**Issue**: The bot sometimes doesn't reset correctly and the game-over detection doesn't work becuase the bot incorrectly thinks there is an object in its way, attempts to jump over it and in doing so accidently starts a new round. This means the bot will not correctly log its run and will start a new run with ROI delta too high for the initial speed.
**Solution**:
- End the bot with `Ctrl+C` and restart it.
- Allow the bot to die and automatically restart after a few attempts.
---

## Development

### Project Structure

```
Dino-Runner/
├── src/
│   ├── main.py              # Entry point
│   ├── Bot.py               # Main game loop & logic
│   ├── FrameProcessor.py    # Edge detection & analysis
│   ├── ScreenRecorder.py    # Screen capture & template matching
│   ├── setup_chrome_macro.py # Chrome automation
│   └── utils/
│       └── fix_dpi_scaling.py
├── assets/
│   ├── template_dino.png    # Dino sprite template
│   └── template_replay.png  # Replay button template
├── pyproject.toml           # Dependencies
└── README.md
```