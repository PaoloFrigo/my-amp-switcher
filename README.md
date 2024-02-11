# MY AMP SWITCHER

MyAmpSwitcher is a Python application that allows you to control your amplifier, amp-cab-switcher or any device through MIDI messages. You can switch between different profiles, each containing customizable buttons that send MIDI Program Change and Control Change messages.

This software is released under [the MIT license](./license).

## Overview

This application provides a graphical user interface written using QT libraries for managing your amplifier or amp and cab switcher profiles and MIDI settings. It allows you to create, edit, load, import, and export profiles. You can easily switch between profiles and send MIDI messages to control your amplifier settings.

Preview of the MacOS version:
![preview](./media/preview.png)

With colors:
![preview](./media/preview-colored.png)

Please note that MyAmpSwitcher can run on MacOS/Windows/Linux considering that is built with Python and QT and Midi libraries are ported across these platforms.

![icon.jpeg](media/icon.jpeg)


## Settings

The application uses a settings file (`settings.json`) to store MIDI output port, channel, default profile, and other configuration details. You can edit these settings within the application to customize the behaviour according to your setup.

This is a sample of the [settings.json](./settings.json):
```json
{
    "port_name": "USB MIDI CABLE",
    "profile": "n-audio-8X7.json",
    "icon": "icon.ico",
    "font": "Arial",
    "size": 14,
    "buttons_per_row": 3
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
            "program_change": 2,
            "name": "clean"
        },
        {
            "order": 1,
            "program_change": 1,
            "name": "boost"
        },
        {
            "order": 2,
            "program_change": 3,
            "name": "xlead"
        }
    ]
}
```

## Profile Notes
Each profile should be saved with a meaningful ```"name"``` field, when loaded the name will appear as the window's title. Each button should have ```"name"``` have a ```"program_change"``` and/or ```"cc_number" ```and ```"cc_value"```.

You can also assign a different ```"color"``` for each button e.g. "color": "green". The color name is not case-sentive.

This is the list of available colours:
```AliceBlue, AntiqueWhite, Aqua, Aquamarine, Azure, Beige, Bisque, Black, BlanchedAlmond, Blue, BlueViolet, Brown, BurlyWood, CadetBlue, Chartreuse, Chocolate, Coral, CornflowerBlue, Cornsilk, Crimson, Cyan, DarkBlue, DarkCyan, DarkGoldenrod, DarkGray, DarkGreen, DarkKhaki, DarkMagenta, DarkOliveGreen, DarkOrange, DarkOrchid, DarkRed, DarkSalmon, DarkSeaGreen, DarkSlateBlue, DarkSlateGray, DarkTurquoise, DarkViolet, DeepPink, DeepSkyBlue, DimGray, DodgerBlue, Firebrick, FloralWhite, ForestGreen, Fuchsia, Gainsboro, GhostWhite, Gold, Goldenrod, Gray, Green, GreenYellow, Honeydew, HotPink, IndianRed, Indigo, Ivory, Khaki, Lavender, LavenderBlush, LawnGreen, LemonChiffon, LightBlue, LightCoral, LightCyan, LightGoldenrodYellow, LightGray, LightGreen, LightPink, LightSalmon, LightSeaGreen, LightSkyBlue, LightSlateGray, LightSteelBlue, LightYellow, Lime, LimeGreen, Linen, Magenta, Maroon, MediumAquamarine, MediumBlue, MediumOrchid, MediumPurple, MediumSeaGreen, MediumSlateBlue, MediumSpringGreen, MediumTurquoise, MediumVioletRed, MidnightBlue, MintCream, MistyRose, Moccasin, NavajoWhite, Navy, OldLace, Olive, OliveDrab, Orange, OrangeRed, Orchid, PaleGoldenrod, PaleGreen, PaleTurquoise, PaleVioletRed, PapayaWhip, PeachPuff, Peru, Pink, Plum, PowderBlue, Purple, Red, RosyBrown, RoyalBlue, SaddleBrown, Salmon, SandyBrown, SeaGreen, SeaShell, Sienna, Silver, SkyBlue, SlateBlue, SlateGray, Snow, SpringGreen, SteelBlue, Tan, Teal, Thistle, Tomato, Turquoise, Violet, Wheat, White, WhiteSmoke, Yellow, YellowGreen ```

## Installation from the DMG file

Download the latest release as a dmg file from the GitHub repository for your platform.

After mounting the image the following window will appear.
![App Install](./media/install.png)

Select the MyAmpSwitcher icon and drag it over the Application window to complete the installation.
.

## Uninstalling the MyAmpSwitcher App
Open Finder. Select the MyAmpSwitcher App and move it to the bin.

## Installation instruction from GitHub

To run the MyAmpSwitcher application, follow these steps:

1. Clone the repository to your local machine.

   ```bash
   git clone https://github.com/paolofrigo/my-amp-switcher.git
   ```

2. Create a virtual environment and activate it

   on macOS/Linux
    ```bash
    cd my-amp-switcher
    python3 -m venv .venv
    source .venv/bin/activate
    ```
   on windows
   ```powershell
    cd my-amp-switcher
    python3 -m venv .venv
    .venv\bin\activate
    ```

4. Installing the dependencies
    ```bash
    pip install -r requirements.txt
    ```

5. Running the app.
    ```
    python3 MyAmpSwitcher.py
    ```

## User Interface Notes
The application has 2 main configuration files. "Settings" (settings.json) for visualization preferences/defaults and profiles (individually saved under the profiles folder) specific to the functions they are designed to perform.

This is the layout of the app:
![Gui](./media/gui_sections.png)
1. The window title is set to the profile name loaded.
2. The file menu allows users to manage profiles under 'Profiles', general 'Settings', and review the current version using the 'About' section.
   
Toolbar 

4. Dropdown with all available options and showing the MIDI Output currently selected.
5. Refresh button to reload all available MIDI Outputs (in case they have changed since the app startup)
6. Dropdown of Midi Channel and showing what is selected in the loaded profile.
   
The "Save" button will write any change applied to the dropdown in the toolbar to the settings (Midi Output) and profile (Channel) files.

8. All Button labels and MIDI messages are defined in the profile, instead text size and the number of buttons for each row are defined in the settings.
9. The status bar displays MIDI Messages and user notifications.

## Usage
* Please make sure you connect your MIDI interface before opening My-Amp-Swticher.

* Please consider that your OS when launching the app may require your authorisation to allow the app to access your microphone.
![microphone](./media/microphone_access.png)

## Show Your Support
Don't forget to give a ⭐️ on GitHub if you find this app useful!

## Disclaimer
THE SOFTWARE IS PROVIDED "AS IS," WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
