# ble-aoa-direction-finding

![Picture of AOA simulated via Silicon Lab's software](imgs/image-2.png)
Exploring Bluetooth 5.1 direction finding using Silicon Labs hardware and the RTL (Real-Time Locating) library.

## Current Project Status

- [x] Hardware is fully functional (BRD4191A locator + BG22 tag).
- [x] AoA Analyzer successfully detects azimuth/elevation from the tag.
- [x] Python visualizer (`app.py`) runs and connects to MQTT.
- [ ] (bt_aoa_host_locator, bt_host_positioning) work/available
- [x] Temporary config files were created manually to test the visualizer.
- [ ] Angle/position data appears

## Mosquitto + Reminder

Use: `mosquitto -c /opt/homebrew/etc/mosquitto/mosquitto.conf`
in terminal to run mosquitto service (via brew install) before running python file!

## **Motivation**

Indoor positioning remains an open challenge for navigation, asset tracking, and smart environments. While GPS has transformed outdoor localization, it does not work indoors due to multipath and signal attenuation. Bluetooth 5.1 introduced **Direction Finding**, enabling receivers with antenna arrays to estimate **Angle of Arrival (AoA)** and thus localize BLE tags. In this project, we move beyond simulations to **build a real Bluetooth indoor localization platform** using commercial development boards, antenna arrays, and Silicon Labs’ RTL library. This hands-on system will let us stream real-time angle and position estimates, evaluate localization accuracy, and gain experience with both wireless signal processing and end-to-end IoT system design.

## **Background (what we’ll build on)**

Silicon Labs’ SDK ships a complete reference stack to accelerate DF development: **AoA asset-tag** (CTE transmitter), **AoA locator** (CTE receiver in NCP mode), a **host locator app** that runs the **RTL library** to compute angles, and a **positioning host app** that fuses angles from multiple locators via MQTT into (x,y,z) positions. The app note also documents the software architecture, sample projects, and tools (AoA Analyzer, Positioning Tool).

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

## **Bill of Materials (minimum viable)**

- 1× **Tag**: EFR32xG22/G24 dev board (e.g., Thunderboard BG22), **BRD4184A with CR2032 battery**
- **Locators**: ~~at least **2** antenna array boards (recommended **4** for robust 2D/3D), each on a WSTK + EFR32xG22 running NCP locator FW.~~ We sticking with 1 :D
- **Antenna array**: Silicon Labs **BRD4191A 4×4 dual-polarized** URA (per locator).
- **PC/Host**: Windows (MSYS2/MinGW-64) or Linux (Ubuntu) box to run host apps, MQTT broker, and optional Python viz.
- Stands/ceiling mounts, tape measure, power, USB cables.

---

## **Software you’ll install**

- **Simplicity Studio 5** + **Gecko SDK** + **Bluetooth SDK ≥ v3.1** (for sample projects).
- **RTL Library** (bundled with SDK) and **Direction Finding Tool Suite (UG514)**.
- **Mosquitto** MQTT broker + (optional) **MQTT Explorer**.
- **Windows**: **MSYS2/MinGW-64** toolchain; **Linux**: libmosquitto-dev.
- **Python 3.7** with pyqtgraph, pyqt5==5.14.0 (Linux), pyopengl, numpy, Pillow, paho-mqtt for the GUI.
