"""
Windows Tray Monitor (preserves tray icons for minimized windows)
Fixes:
 - Monitored windows are not removed when hidden (minimized to tray)
 - Tray icons remain active so user can restore the window
"""

import ctypes
import json
import os
import sys
import threading
import time
import traceback
from ctypes import wintypes

import psutil
import win32api
import win32con
import win32gui
import win32ui
from PIL import Image

try:
    import win32con
    import win32gui
    import win32process
except Exception:
    print("pywin32 is required. pip install pywin32")
    raise

try:
    import psutil
except Exception:
    psutil = None

try:
    import pystray
    from PIL import Image, ImageDraw
except Exception:
    print("pystray and pillow are required. pip install pystray pillow")
    raise

USER32 = ctypes.windll.user32
WINEVENT_OUTOFCONTEXT = 0x0000
EVENT_SYSTEM_MINIMIZESTART = 0x0016
EVENT_OBJECT_DESTROY = 0x8001

SW_HIDE = 0
SW_RESTORE = 9

def get_icon_from_exe(exe_path):
    try:
        large, small = win32gui.ExtractIconEx(exe_path, 0)
        hicon = large[0] if large else small[0] if small else None
        if not hicon:
            return None

        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        mem_dc = hdc.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(hdc, 64, 64)
        mem_dc.SelectObject(bmp)

        win32gui.DrawIconEx(mem_dc.GetSafeHdc(), 0, 0, hicon, 64, 64, 0, None, win32con.DI_NORMAL)

        bmpinfo = bmp.GetInfo()
        bmpstr = bmp.GetBitmapBits(True)
        img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)

        win32gui.DestroyIcon(hicon)
        mem_dc.DeleteDC()
        hdc.DeleteDC()

        return img
    except Exception:
        traceback.print_exc()
        return None


def get_shell_icon(index=122):  # Index 167 is the blue arrow icon
    try:
        dll_path = os.path.join(os.environ['SystemRoot'], 'System32', 'shell32.dll')
        large, small = win32gui.ExtractIconEx(dll_path, index)
        hicon = large[0] if large else small[0] if small else None
        if not hicon:
            return None

        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        mem_dc = hdc.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(hdc, 64, 64)
        mem_dc.SelectObject(bmp)

        win32gui.DrawIconEx(mem_dc.GetSafeHdc(), 0, 0, hicon, 64, 64, 0, None, win32con.DI_NORMAL)

        bmpinfo = bmp.GetInfo()
        bmpstr = bmp.GetBitmapBits(True)
        img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)

        win32gui.DestroyIcon(hicon)
        mem_dc.DeleteDC()
        hdc.DeleteDC()

        return img
    except Exception:
        traceback.print_exc()
        return None


def get_app_icon():
    try:
        exe_path = sys.executable  # Path to your running .exe or python.exe
        large, small = win32gui.ExtractIconEx(exe_path, 0)
        hicon = large[0] if large else small[0] if small else None
        if not hicon:
            return None

        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        mem_dc = hdc.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(hdc, 64, 64)
        mem_dc.SelectObject(bmp)

        win32gui.DrawIconEx(mem_dc.GetSafeHdc(), 0, 0, hicon, 64, 64, 0, None, win32con.DI_NORMAL)

        bmpinfo = bmp.GetInfo()
        bmpstr = bmp.GetBitmapBits(True)
        img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)

        win32gui.DestroyIcon(hicon)
        mem_dc.DeleteDC()
        hdc.DeleteDC()

        return img
    except Exception:
        traceback.print_exc()
        return None


def get_window_icon(hwnd):
    try:
        tid, pid = win32process.GetWindowThreadProcessId(hwnd)
        exe_path = psutil.Process(pid).exe()

        large, small = win32gui.ExtractIconEx(exe_path, 0)
        hicon = large[0] if large else small[0] if small else None
        if not hicon:
            return None

        # Create a memory DC and compatible bitmap
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        mem_dc = hdc.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(hdc, 64, 64)
        mem_dc.SelectObject(bmp)

        # Draw the icon into the memory DC
        win32gui.DrawIconEx(mem_dc.GetSafeHdc(), 0, 0, hicon, 64, 64, 0, None, win32con.DI_NORMAL)

        # Convert to PIL image
        bmpinfo = bmp.GetInfo()
        bmpstr = bmp.GetBitmapBits(True)
        img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)

        # Cleanup
        win32gui.DestroyIcon(hicon)
        mem_dc.DeleteDC()
        hdc.DeleteDC()

        return img
    except Exception:
        traceback.print_exc()
        return None




def make_image(text="T"):
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([(0, 0), (63, 63)], fill=(30, 144, 255))
    d.text((18, 18), text, fill=(255, 255, 255))
    return img


class WindowMatch:
    def __init__(self, title_contains=None, class_name=None, exe_name=None, icon_exe=None):
        self.title_contains = title_contains.lower() if title_contains else None
        self.class_name = class_name.lower() if class_name else None
        self.exe_name = exe_name.lower() if exe_name else None
        self.icon_exe = icon_exe


    def matches(self, hwnd):
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return False
            title = win32gui.GetWindowText(hwnd) or ""
            cls = win32gui.GetClassName(hwnd) or ""
            if self.title_contains and self.title_contains not in title.lower():
                return False
            if self.class_name and self.class_name != cls.lower():
                return False
            if self.exe_name:
                tid, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    proc = psutil.Process(pid) if psutil else None
                    name = proc.name() if proc else None
                except Exception:
                    name = None
                if not name or self.exe_name != name.lower():
                    return False
            return True
        except Exception:
            return False

import pystray._win32 as win32_impl  # Only works on Windows


class MonitoredWindow:
    def __init__(self, hwnd, match: WindowMatch):
        self.hwnd = hwnd
        self.title = win32gui.GetWindowText(hwnd)
        self.tray_icon = None
        self.hidden = False
        self.match = match


 
    def create_tray_icon(self, on_restore):
        if self.tray_icon:
            return

        # Use icon_exe if specified
        if self.match.icon_exe:
            img = get_icon_from_exe(self.match.icon_exe)
        else:
            img = get_window_icon(self.hwnd)

        img = img or make_image(self.title[:1] or "W")


        icon = pystray.Icon(
            name=f"win-{self.hwnd}",
            icon=img,
            title=self.title,
            menu=pystray.Menu(
                pystray.MenuItem('Restore', lambda: on_restore(self.hwnd), default=True),
                pystray.MenuItem('Quit', lambda: icon.stop())
            )
        )

        t = threading.Thread(target=icon.run, daemon=True)
        t.start()
        self.tray_icon = icon



 
    def destroy_tray_icon(self):
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
            self.tray_icon = None


class TrayMonitorApp:
    def __init__(self, config_path='config.json', poll_interval=5):
        self.config_path = config_path
        self.poll_interval = poll_interval
        self.matches = []
        self.monitored = {}
        self.lock = threading.Lock()
        self.running = False
        self._hook_min = None
        self._hook_destroy = None
        self._we_proc = None
        self._load_config()
        self.main_icon = self._create_main_tray_icon()
        self.show_main_icon = True


    def _toggle_main_icon(self):
        self.show_main_icon = not self.show_main_icon
        self._save_config()

        if not self.show_main_icon and self.main_icon:
            try:
                self.main_icon.stop()
            except Exception:
                pass
        elif self.show_main_icon and not self.main_icon.visible:
            threading.Thread(target=self.main_icon.run, daemon=True).start()

    def _create_main_tray_icon(self):

        menu = pystray.Menu(
            pystray.MenuItem('Status', lambda: self._print_status()),
            pystray.MenuItem(
                'Hide Main Icon',
                lambda: self._toggle_main_icon(),
                checked=lambda item: not self.show_main_icon
            ),
            pystray.MenuItem('Exit', lambda: self.stop())
        )
        
        img = get_shell_icon(122) or make_image('M')
        icon = pystray.Icon('tray-monitor', img, 'Window Tray Monitor', menu=menu)

        def run_icon():
            icon.run()

        self.main_icon = icon
        if self.show_main_icon:
            threading.Thread(target=run_icon, daemon=True).start()
        return icon

    def _print_status(self):
        with self.lock:
            print("Monitored windows:")
            for hwnd, mw in self.monitored.items():
                print(f"  {hex(hwnd)} - {mw.title} - hidden={mw.hidden}")

    def _load_config(self):
        if not os.path.exists(self.config_path):
            print(f"Config {self.config_path} not found. Creating example config.")
            example = {
                "settings": {"show_main_icon": True},
                "windows": [{"title_contains": "notepad", "exe_name": "notepad.exe"}]
            }
            with open(self.config_path, 'w') as f:
                json.dump(example, f, indent=2)

        with open(self.config_path, 'r') as f:
            cfg = json.load(f)

        self.show_main_icon = cfg.get("settings", {}).get("show_main_icon", True)
        self.matches = [WindowMatch(**w) for w in cfg.get('windows', [])]

    def _save_config(self):
        try:
            with open(self.config_path, 'r') as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}

        cfg.setdefault("settings", {})["show_main_icon"] = self.show_main_icon

        with open(self.config_path, 'w') as f:
            json.dump(cfg, f, indent=2)


    def _enumerate_and_update(self):
        found = set()
        def enum_proc(hwnd, lparam):
            for m in self.matches:
                if m.matches(hwnd):
                    found.add(hwnd)
                    with self.lock:
                        if hwnd not in self.monitored:
                            print(f"Adding monitor for {hex(hwnd)} - {win32gui.GetWindowText(hwnd)}")
                            self.monitored[hwnd] = MonitoredWindow(hwnd, m)

            return True
        win32gui.EnumWindows(enum_proc, None)

        # Remove windows that truly no longer exist (not hidden ones)
        with self.lock:
            remove = []
            for h, mw in self.monitored.items():
                if not win32gui.IsWindow(h):
                    remove.append(h)
                elif h not in found and not mw.hidden:
                    remove.append(h)
            for h in remove:
                print(f"Removing monitor for {hex(h)}")
                mw = self.monitored.pop(h)
                mw.destroy_tray_icon()

    def start(self):
        self.running = True
        threading.Thread(target=self._poll_loop, daemon=True).start()
        threading.Thread(target=self._setup_win_event_hooks, daemon=True).start()

    def stop(self):
        self.running = False
        with self.lock:
            for mw in list(self.monitored.values()):
                mw.destroy_tray_icon()
        try:
            if self.main_icon:
                self.main_icon.stop()
        except Exception:
            pass
        print("Stopped")

        # Exit in a separate thread to avoid crashing the message handler
        threading.Thread(target=lambda: os._exit(0), daemon=True).start()


    def _poll_loop(self):
        while self.running:
            try:
                self._load_config()
                self._enumerate_and_update()
            except Exception:
                traceback.print_exc()
            time.sleep(self.poll_interval)

    def _on_restore(self, hwnd):
        try:
            with self.lock:
                mw = self.monitored.get(hwnd)
                if not mw:
                    return
                USER32.ShowWindow(hwnd, SW_RESTORE)
                USER32.SetForegroundWindow(hwnd)
                mw.hidden = False
                mw.destroy_tray_icon()
        except Exception:
            traceback.print_exc()

    WinEventProcType = ctypes.WINFUNCTYPE(None, wintypes.HANDLE, wintypes.DWORD, wintypes.HWND,
                                          wintypes.LONG, wintypes.LONG, wintypes.DWORD, wintypes.DWORD)

    def _setup_win_event_hooks(self):
        def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
            try:
                if not hwnd or idObject != 0:
                    return
                if event == EVENT_SYSTEM_MINIMIZESTART:
                    with self.lock:
                        mw = self.monitored.get(hwnd)
                        if mw and not mw.hidden:
                            print(f"Window {hex(hwnd)} minimized -> tray")
                            mw.create_tray_icon(self._on_restore)
                            USER32.ShowWindow(hwnd, SW_HIDE)
                            mw.hidden = True
                elif event == EVENT_OBJECT_DESTROY:
                    with self.lock:
                        if hwnd in self.monitored:
                            mw = self.monitored.pop(hwnd)
                            mw.destroy_tray_icon()
                            print(f"Window {hex(hwnd)} destroyed")
            except Exception:
                traceback.print_exc()

        self._we_proc = TrayMonitorApp.WinEventProcType(callback)
        self._hook_min = USER32.SetWinEventHook(EVENT_SYSTEM_MINIMIZESTART, EVENT_SYSTEM_MINIMIZESTART, 0,
                                               self._we_proc, 0, 0, WINEVENT_OUTOFCONTEXT)
        self._hook_destroy = USER32.SetWinEventHook(EVENT_OBJECT_DESTROY, EVENT_OBJECT_DESTROY, 0,
                                                   self._we_proc, 0, 0, WINEVENT_OUTOFCONTEXT)
        if not self._hook_min or not self._hook_destroy:
            print("Warning: WinEvent hooks failed.")

        msg = wintypes.MSG()
        while USER32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            USER32.TranslateMessage(ctypes.byref(msg))
            USER32.DispatchMessageW(ctypes.byref(msg))


if __name__ == '__main__':
    app = TrayMonitorApp()
    app.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        app.stop()
