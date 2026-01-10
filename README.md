# Ecovacs CN Domestic

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

**Ecovacs CN Domestic** (`ecovacs_cn`) is a custom Home Assistant integration developed for **domestic (Mainlain China-region) Ecovacs cleaning robots**.

**_This project is maintained in my free time. A coffee ☕ is always appreciated!_**

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/hoangminh1109)

## 🤔 Why this exists?

If you bought your Ecovacs robot in China or it is a specific domestic model, you likely found that the standard Home Assistant Ecovacs integration does not work. This could be due to differences in servers and protocols between the Oversea and Chinese versions.

This integration is built based on documentation from [open.ecovacs.cn](http://open.ecovacs.cn/) and the [ecovacs-mcp](https://github.com/ecovacs-ai/ecovacs-mcp) project to bridge that gap.

## ✨ Features

Due to limitations in the currently available API, this integration focuses on core essential controls.

* **Status Monitoring:** View current robot cleaning and charging status.
* **Cleaning Control:** Start, Pause, Resume, and Stop cleaning sessions.
* **Charging Control:** Return to dock (charge) or cancel returning.

## 💾 Installation

### Option 1: HACS
1.  Go to **HACS** -> **Integrations**.
2.  Select **Custom repositories** from the menu.
3.  Add this repository URL and select **Integration**.
4.  Click **Add**, search for "Ecovacs CN Domestic", and install.
5.  Restart Home Assistant.

### Option 2: Manual
1.  Download the `ecovacs_cn` folder from the releases.
2.  Copy it to `/config/custom_components/ecovacs_cn`.
3.  Restart Home Assistant.

## 🔑 Configuration & Getting your API Key

To use this integration, you need an **API Key (AK)**.

1.  Go to the [Ecovacs Open Platform](https://open.ecovacs.cn).
2.  Click **"Get AK"** (usually at the top right corner).
3.  **Log in** using the same Ecovacs ID (phone number/email) you use in your **Ecovacs Home app**.
4.  Copy the generated API Key.
5.  In Home Assistant, go to **Settings** -> **Devices & Services** -> **Add Integration**.
6.  Search for **Ecovacs CN Domestic**.
7.  Paste your API Key when prompted.

## ⚠️ Important Limitation: 90-Day Key Expiry

**Please read this carefully.**
The API Key provided by the Ecovacs Open Platform has a hard limit of **90 days**.

1.  The integration will stop working after 90 days.
2.  You must manually generate a new key and update the integration configuration.
3.  **Recommendation:** Create a generic **Reminder** or **To-Do** item in Home Assistant or your calendar to remind yourself to refresh the token every 85 days.

## 🛠️ Usage

Once installed, control buttons and status sensors will be created under your robot's name. They can be used in dashboards, automations, scripts as you like.

## 🔍 Testing

This custom integration has been tested on:
- Ecovacs Deebot T5 Neo (DX55) domestic version (the only one I have 😆)

Any user is welcome to test on yours, and create an issue if you find any problem.

## 📖 Refererence

- [Ecovacs Open Platform](https://open.ecovacs.cn)
- [ecovacs-mcp](https://github.com/ecovacs-ai/ecovacs-mcp)

## ⚠️ Disclaimer
This is a custom integration and is not affiliated with or endorsed by Ecovacs. Use at your own risk.
