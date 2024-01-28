# MY AMP SWITCHER

MyAmpSwitcher is a Python application that allows you to control your amplifier, amp-cab-switcher or any device through MIDI messages. You can switch between different profiles, each containing customizable buttons that send MIDI Program Change and Control Change messages.

This software is released under [the MIT license](./license).

## Overview

This application provides a graphical user interface for managing your amplifier or amp and cab switcher profiles and MIDI settings. It allows you to create, edit, load, import, and export profiles. You can easily switch between profiles and send MIDI messages to control your amplifier settings.

![icon.jpeg](icon.jpeg)


## Settings

The application uses a settings file (`settings.json`) to store MIDI output port, channel, default profile, and other configuration details. You can edit these settings within the application to customize the behavior according to your setup.

This is a sample of the [settings.json](./settings.json):
```json
{
    "port_name": "USB MIDI CABLE",
    "profile": "test1.json",
    "icon": "icon.icns",
    "channel": 0,
    "font": "Arial",
    "size": 16,
    "buttons_per_row": 4
}
```

## Profiles

Profiles are JSON files stored in the ["profiles"](./profiles/) folder. Each profile contains information about the channel, button configurations, and other settings. You can create new profiles, edit existing ones, and switch between them seamlessly.
Profiles can be edited within the app or via any text editor.

This is a profile for a Brunetti XL" R-EVO: 

```json
{
    "name": "Brunetti XL\" R-EVO",
    "channel": 0,
    "buttons": [
        {
            "order": 0,
            "color": "green",
            "program_change": 2,
            "name": "clean"
        },
        {
            "order": 1,
            "color": "yellow",
            "program_change": 1,
            "name": "boost"
        },
        {
            "order": 2,
            "color": "red",
            "program_change": 3,
            "name": "xlead"
        }
    ]
}
```

## Profile Notes
Each profile should be saved with a meaningful ```"name"``` field, when loaded the name will appear as window's title. Each button should have ```"name"``` have a ```"program_change"``` and/or ```"cc_number" ```and ```"cc_value"```.

## Installation instruction from GitHub

To run the MyAmpSwitcher application, follow these steps:

1. Clone the repository to your local machine.

   ```bash
   git clone https://github.com/paolofrigo/my-amp-switcher.git
   ```

2. Create a virtual environment and activate it
    ```bash
    cd my-amp-switcher
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. Installing the dependencies
    ```bash
    pip install -r requirements.txt
    ```

4. Running the app.
    ```
    python3 MyAmpSwitcher.py
    ```

## Usage
Please make sure you connect the your midi interface before opening My-Amp-Swticher.

## Show Your Support
Don't forget to give a ⭐️ on GitHub if you find this app useful!

## Disclaimer
THE SOFTWARE IS PROVIDED "AS IS," WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.