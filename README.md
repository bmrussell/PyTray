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
      "title_contains": "Visual Studio Code",
      "exe_name": "Code.exe",
      "icon_exe": "C:\\Users\\brian\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
    },
    {
      "title_contains": "Microsoft To Do",
      "exe_name": "C:\\Program Files\\WindowsApps\\Microsoft.Todos_2.148.3611.0_x64__8wekyb3d8bbwe\\Todo.exe"
    }
  ]
}
```

and run it. Apps in the config will now be minimised to tray on taskbar.

Right clicking the main app tray icon and selecting "Hide Main Icon" will remove the main icon from the tray and set `"show_main_icon": false`.

If an app icon changes the code will attempt to reflect that change in the tray icon.


# TODO
1. Add right click for "Show main icon" to minimised apps to restore the main tray icon.