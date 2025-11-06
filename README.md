# PYTRAY

Inspired by [Trayy](https://github.com/alirezagsm/Trayy) which is great but only worked intermittently for me.

I do Python but this was unashamedly vibecoded with cgpt & copilot. The Python knowledge helped with debugging :)

# RUNNING

Create a JSON file `config.json` in the same folder as the executable like this:

```json
{
  "settings": {
    "show_main_icon": true
  },
  "windows": [
    {
      "title_contains": "Slack PWA",
      "exe_name": "chrome.exe",
      "icon_path": "C:\\Users\\brian\\AppData\\Local\\slack\\slack.exe"
    },
    {
      "title_contains": "Visual Studio Code",
      "exe_name": "Code.exe",
      "icon_path": "C:\\Users\\brian\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
    },
    {
      "title_contains": "Realtek Audio Console",
      "exe_name": "ApplicationFrameHost.exe",
      "icon_path": "C:\\Program Files\\WindowsApps\\RealtekSemiconductorCorp.RealtekAudioControl_1.52.356.0_x64__dt26b99r8h8gj\\Assets\\Square44x44Logo.targetsize-32.png"
    }
  ]
}
```

and run it. Apps in the config will now be minimised to tray on taskbar.

`icon_path` optionally points to a .exe or image file to use as the tray icon.

Right clicking the main app tray icon and selecting "Hide Main Icon" will remove the main icon from the tray and set `"show_main_icon": false`.

If an app icon changes the code will attempt to reflect that change in the tray icon.


# TODO
1. Add right click for "Show main icon" to minimised apps to restore the main tray icon.