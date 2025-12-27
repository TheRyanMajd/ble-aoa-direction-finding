# Technical Report: Bluetooth 5.1 Direction Finding with AoA
[![Youtube Thumbnail](https://img.youtube.com/vi/wrYFgcZ45No/0.jpg)](https://www.youtube.com/watch?v=wrYFgcZ45No)
## 1. Introduction

Indoor localization remains a difficult problem due to multipath, signal attenuation, and the absence of GPS indoors. Bluetooth 5.1 introduced **Direction Finding**, enabling receivers equipped with antenna arrays to estimate the **Angle of Arrival (AoA)** of BLE constant-tone-extension (CTE) packets. With this capability, it becomes possible to infer **azimuth**, **elevation**, and approximate **(x, y, z)** positions of BLE tags.

This project implements a complete **end-to-end indoor direction-finding pipeline** using Silicon Labs hardware (BRD4191A antenna array + BG22 BLE tag) and the RTL library. After building the system, I evaluated its real-world performance under two tag placements:

- **In-hand**, where the tag is freely held
- **In-pocket**, where the tag is partially obstructed by the user’s torso

The goal was to observe how placement and human-body obstruction affect AoA accuracy, especially in **azimuth**, **elevation**, **distance**, and **polar** coordinate representations.

---

## 2. System Design

### 2.1 Hardware Setup

- **BLE Tag:** EFR32BG22 Thunderboard transmitting CTE packets
- **Locator:** Silicon Labs BRD4191A 4×4 dual-polarized antenna array
- **Host Machine:** Windows PC running:
  - AoA Host Locator app (RTL library)
  - Mosquitto MQTT broker
  - Custom Python visualizer (`app.py`)

### 2.2 Data Pipeline

1. BLE tag transmits CTE packets.
2. AoA locator samples IQ data across its antenna array.
3. Host application processes IQ using the RTL library.
4. Angle estimates (azimuth, elevation) are published to **MQTT**.
5. Python visualizer reads MQTT data and renders real-time plots.

### 2.3 Commands Used

#### Mosquitto + Reminder

> Mosquitto is required to run things outside of SimplicityStudio. Make sure this runs before starting the Python file.

To run the visualizer:

```bash
python3 app.py -c pos_config.json
```

To run the AoA host locator:

```bash
bt_aoa_host_locator.exe -u COM6 -b 115200 \
  -m localhost:1883 \
  -c config/locator_config.json \
  -l debug
```

To collect raw data:

```bash
mosquitto_sub -h localhost -t "silabs/aoa/position/#" -v
```

### 2.4 Experiment Setup

- Sampling rate: ~50 sequences/second
- Antenna: fixed position
- Tag placements:
  - In-pocket
  - In-hand
    User remained mostly still but performed small motions and one turn at the end (in-pocket case).

## 3. Evaluation

### 3.1 Azimuth

**In-hand:**

- Very smooth and tightly grouped
- Clear response to small horizontal rotations
- Minimal noise

**In-pocket:**

- Highly unstable; large swings even when still
- Severe drift due to torso blockage
- Turning the body produced abrupt, extreme angle jumps

**Conclusion:**
Azimuth is very sensitive to human-body obstruction.
Holding the tag yields drastically better results.

---

### 3.2 Elevation

**In-hand:**

- More reactive and “spiky”
- Sensitive to natural wrist tilt and hand motion

**In-pocket:**

- Flatter and smoother, but not more accurate
- Absorption from the torso reduces variation, creating a “compressed” elevation profile

**Conclusion:**
In-pocket elevation looks smoother by being flattened by absorption.

---

### 3.3 Distance

**In-hand:**

- Clear peaks and recognizable structure
- Good stability across runs

**In-pocket:**

- Peaks smear and shift
- Much noisier due to attenuation through the torso
- Global maximum still identifies the moment standing directly over the array

**Conclusion:**
Distance estimates degrade significantly in-pocket.

---

### 3.4 Polar Plots

**In-hand:**

- Clean, consistent polar lobes
- Good geometric correlation to movement

**In-pocket:**

- Chaotic and jittery
- Jumps at the start and end of sequences
- Poor correlation to actual movement

**Conclusion:**
Polar representaion shows how destructive pocket placement is to calculated distance.

---

## 4. Overall Performance Summary

| Metric        | In-Hand Performance | In-Pocket Performance      |
| ------------- | ------------------- | -------------------------- |
| **Azimuth**   | ★★★★★ stable        | ★★☆☆☆ unstable and erratic |
| **Elevation** | ★★★☆☆ reactive      | ★★★★☆ smoother but biased  |
| **Distance**  | ★★★★☆ reliable      | ★★★☆☆ smeared + attenuated |
| **Polar**     | ★★★★★ clean         | ★★★☆☆ missing spots        |

### Final Conclusion

The system works reliably when the BLE tag is **held in the hand**, but experiences significant degradation in the **pocket** due to:

- Human-body attenuation
- Multipath interference (human body)
- Reduced signal strength (in pocket)
- Loss of line-of-sight to the antenna array

Overall, tag placement is a dominant factor in achieving accurate AoA-based indoor localization.

![Picture of AOA simulated via Silicon Lab's software](imgs/image-2.png)
Exploring Bluetooth 5.1 direction finding using Silicon Labs hardware and the RTL (Real-Time Locating) library.

## Current Project Status

- [x] Hardware is fully functional (BRD4191A locator + BG22 tag).
- [x] AoA Analyzer successfully detects azimuth/elevation from the tag.
- [x] Python visualizer (`app.py`) runs and connects to MQTT.
- [x] (bt_aoa_host_locator, bt_host_positioning) work/available
- [x] Temporary config files were created manually to test the visualizer.
- [x] Angle/position data appears
- [x] Video Made
- [x] Video Edited
- [x] Project + [Video Here](https://www.youtube.com/watch?v=wrYFgcZ45No&feature=youtu.be)

## Related Documentation:

- [Course Homepage](https://anplus.notion.site/2025-cs4900-6900)
- [Quick Start Guide](https://www.silabs.com/documents/public/quick-start-guides/qsg175-direction-finding-solution-quick-start-guide.pdf)
- [Development Guide](https://www.silabs.com/documents/public/application-notes/an1296-application-development-with-rtl-library.pdf)
- [Antenna Board BRD4191A Hardware Guide](https://www.silabs.com/documents/public/user-guides/ug531-brd4191a-user-guide.pdf)

## **What you will build (system design)**

**Inputs:**

- IQ samples from CTE packets at each locator + locator configuration (antenna type, switching pattern, masks), and the deployment topology (locator IDs, **coordinates**, **orientations**).

**Output:**

- Continuous **(x, y, z)** position estimates for each BLE tag (plus per-locator azimuth/elevation and uncertainty), published as JSON over **MQTT**.
  > Hardware Architecture
  > ![Hardware](imgs/image-1.png)
  > Software Architecture
  > ![Software](imgs/image.png)

## Software Architecture

Pipeline (end-to-end):

1. BLE **asset tag** transmits CTE (connection, connectionless, or Silabs Enhanced).
2. One or more **AoA locators** capture IQ, switch antennas per pattern, stream IQ to the host over USB.
3. **Host locator app** runs RTL to produce **angles** and publishes to MQTT topics.
4. **Positioning host** subscribes to angles from multiple locators, fuses them, and publishes tag **positions** to MQTT for visualization/apps.

---

## Bill Materials

- 1× **Tag**: EFR32xG22/G24 dev board (e.g., Thunderboard BG22), **BRD4184A with CR2032 battery**
- **Locators**: ~~at least **2** antenna array boards (recommended **4** for robust 2D/3D), each on a WSTK + EFR32xG22 running NCP locator FW.~~ We're sticking with 1 :D
- **Antenna array**: Silicon Labs **BRD4191A 4×4 dual-polarized** URA (per locator).
- **PC/Host**: Windows (MSYS2/MinGW-64) or Linux (Ubuntu) box to run host apps, MQTT broker, and optional Python viz.
- Stands/ceiling mounts, tape measure, power, USB cables.

---

## Software You’ll Need

- **Simplicity Studio 5** - main IDE and tooling for Silicon Labs hardware  
  👉 Download: https://www.silabs.com/software-and-tools/simplicity-studio/simplicity-studio-version-5

- **Gecko SDK** - I downloaded this separately and added it into Simplecity Studio via after unzipping.  
  👉 Releases: https://github.com/SiliconLabs/gecko_sdk/releases  
  _(Use the latest release and grab it from the **Assets** section.)_

- **Bluetooth SDK ≥ v3.1** - installs automatically via Simplicity Studio’s Package Manager (used for the AoA sample projects).

- **RTL Library + Direction Finding Tool Suite (UG514)** - included as part of the Gecko/BT SDK packages in Simplicity Studio (used by the AoA Locator Host and Positioning Host apps).

- **MQTT stack**
  - **Mosquitto** MQTT broker - used as the message bus between the host apps and visualizer  
    👉 https://mosquitto.org/download
  - (Optional) **MQTT Explorer** - nice GUI to inspect MQTT topics  
    👉 https://mqtt-explorer.com

- **Build toolchain for the AoA Host apps**
  - **Windows:** `MSYS2`/`MinGW-w64` (for `make`, `gcc`, etc.)
  - **Linux:** standard `build-essential` + `libmosquitto-dev` (or distro equivalent)

- **Python 3.x** for the visualizer GUI (tested with Python 3.7+)
  - Install from https://www.python.org/ or your OS package manager
  - Python packages (via `pip`):
    ```bash
    pip install pyqtgraph pyqt5==5.14.0 pyopengl numpy Pillow paho-mqtt
    ```

## What I ended up doing (Shown in the video):

To preface, I used Windows since MacOS was being weird.
So I built the python program using this command:

```bash
python3 app.py -c .\pos_config.json
```

At this moment, the python3 GUI graph was open but there was no data from the transmitter yet. (The graph was static with no change on movement of the transmitter). This is what using the SDK is for.

Then I compiled the aoa_host_locator using C's `make export` then I went into the `/export` folder, all the way to the new executable:

```bash
C:\Users\Ryan\Downloads\gecko-sdk\app\bluetooth\example_host\bt_aoa_host_locator\export\app\bluetooth\example_host\bt_aoa_host_locator
```

> Make sure to run the executible when it is in your present working directory since it will need to communicate with files inside the Gecko SDK, I ran into issues when moving it out of that directory.

Below is the command I ran for the bluetooth transmission signal to be picked up by the python graph

```bash
bt_aoa_host_locator.exe -u COM6 -b 115200 -m localhost:1883 -c config/locator_config.json -l debug
```

After running this, this is what the CLI returns:

```Subscribing to topic 'silabs/aoa/correction/ble-pd-0C4314F0325A/+'.
Subscribing to topic 'silabs/aoa/config/ble-pd-0C4314F0325A'.
New tag added (1): 60:A4:23:C9:66:AA
```

> You can Ctrl+C to exit this, but it will stop the receiving of the BTE transmission.
> ![alt text](./imgs/graph1.png) > ![alt text](./imgs/graph2.png)

---

# Experiment 1: Human Obstruction & Placement Effects on Bluetooth 5.1 AoA

This first experiment explores how **tag placement** (hand vs pocket) and **human-body obstruction** affect the RTL library’s **azimuth**, **elevation**, and **distance** estimates.
All captures were collected at **50 sequences per second**, from the same static position, with only the _human_ changing position relative to the antenna array.

---

## What I Learned (Summary of Key Findings)

- **In-hand azimuth is much more stable than in-pocket**
  (in-hand = tight curves; in-pocket = high variability even when still, plus large swings during motion)

- **In-hand distance shows clearer multi-peak structure**
  (in-hand peaks are sharp; in-pocket peaks smear, shift, and show more noise)

- **Elevation differs: in-hand is spikier, in-pocket is flatter**
  (in-hand reacts strongly to small orientation changes; in-pocket is flattened by torso absorption but still noisy)

- **Polar plots: in-hand is clean, in-pocket is chaotic**
  (in-hand = well-defined lobes; in-pocket = jumps at beginning/end, inward “snaps,” and unstable angles)

---

## Coolest Visuals from Experiment 1

Below are the plots that demonstrate the biggest differences between **in-hand** vs **in-pocket** placement.

---

## 1. In-Hand Stability (Run A)

### Azimuth

![](experiment1/plots_trimmed/inhand_a_azimuth_trimmed.png)

### Elevation

![](experiment1/plots_trimmed/inhand_a_elevation_trimmed.png)

### Distance

![](experiment1/plots_trimmed/inhand_a_distance_trimmed.png)

### Polar Plot

![](experiment1/plots_trimmed/inhand_a_polar_distance_azimuth_trimmed.png)

---

## 2. In-Pocket (Run A)

In this run, the tag was in my pocket. I stayed mostly still at first, then **turned around near the end of the sequence**.

### Azimuth

![In-pocket azimuth](experiment1/plots_trimmed/inpocket_a_azimuth_trimmed.png)

- Early in the capture, azimuth is biased but somewhat clustered.
- When I turn around at the end, the combination of **body blockage + rotation** causes large, abrupt swings in the estimated angle.

### Elevation

![In-pocket elevation](experiment1/plots_trimmed/inpocket_a_elevation_trimmed.png)

- Elevation stays loosely grouped and shows spread than the hand-held case. (Given my hand was moving while this was just sitting in my pocket)
- Small posture changes are enough to move the estimate around.

### Distance

![In-pocket distance](experiment1/plots_trimmed/inpocket_a_distance_trimmed.png)

- The Global Maxima of the graph represents the exact time I was right above the antenna array.

### Polar Plot

![In-pocket polar](experiment1/plots_trimmed/inpocket_a_polar_distance_azimuth_trimmed.png)

- Very similar to the inhand varient.

---

## Side-by-Side Norm Comparison

### Polar (My Favorite)

<table>
<tr>
<td align="center"><b></b><br><img src="experiment1/plots_trimmed/inhand_all_polar.png" width="400"></td>
<td align="center"><b></b><br><img src="experiment1/plots_trimmed/inpocket_all_polar.png" width="400"></td>
</tr>
</table>

### Azimuth (Normalized)

<table>
<tr>
<td align="center"><b></b><br><img src="experiment1/plots_trimmed/inhand_all_azimuth_norm.png" width="400"></td>
<td align="center"><b></b><br><img src="experiment1/plots_trimmed/inpocket_all_azimuth_norm.png" width="400"></td>
</tr>
</table>

---

## Elevation (Normalized)

<table>
<tr>
<td align="center"><b></b><br><img src="experiment1/plots_trimmed/inhand_all_elevation_norm.png" width="400"></td>
<td align="center"><b></b><br><img src="experiment1/plots_trimmed/inpocket_all_elevation_norm.png" width="400"></td>
</tr>
</table>

---

## Distance (Normalized)

<table>
<tr>
<td align="center"><b></b><br><img src="experiment1/plots_trimmed/inhand_all_distance_norm.png" width="400"></td>
<td align="center"><b></b><br><img src="experiment1/plots_trimmed/inpocket_all_distance_norm.png" width="400"></td>
</tr>
</table>

---

### Data Collection

Collect the positioning data from MQTT for each calibration point and condition:

```bash
mosquitto_sub -h localhost -t "silabs/aoa/position/#" -v > conditionA_attemptX.txt
```
