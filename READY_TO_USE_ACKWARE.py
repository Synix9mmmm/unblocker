# --- BEGIN FIRE LOGIN UI ---
import sys
import time
import subprocess
import threading
import base64
import os

try:
    from keyauth import api as KeyAuthAPI
except Exception as e:
    print("Missing 'keyauth' module. Install with: pip install keyauth-python")
    input("Press Enter to exit...")
    sys.exit(1)

keyauthapp = KeyAuthAPI(
    name="acklite",
    ownerid="MMUpBpG2za",
    version="1.0"
)

_auth_ok = False
_auth_userdata = {}
_hwid = None

# Remember Me functionality
REMEMBER_ME_FILE = os.path.join(os.getenv('APPDATA'), 'ackware_remember.dat')

def save_credentials(username, password):
    """Save encrypted credentials for remember me"""
    try:
        # Simple base64 encoding (use proper encryption in production)
        encoded = base64.b64encode(f"{username}:{password}".encode()).decode()
        with open(REMEMBER_ME_FILE, 'w') as f:
            f.write(encoded)
    except Exception as e:
        print(f"Failed to save credentials: {e}")

def load_credentials():
    """Load saved credentials"""
    try:
        if os.path.exists(REMEMBER_ME_FILE):
            with open(REMEMBER_ME_FILE, 'r') as f:
                encoded = f.read().strip()
                decoded = base64.b64decode(encoded).decode()
                username, password = decoded.split(':', 1)
                return username, password
    except Exception as e:
        print(f"Failed to load credentials: {e}")
    return None, None

def clear_credentials():
    """Clear saved credentials"""
    try:
        if os.path.exists(REMEMBER_ME_FILE):
            os.remove(REMEMBER_ME_FILE)
    except Exception as e:
        print(f"Failed to clear credentials: {e}")

def safe_exit(msg):
    print(f"\n{msg}")
    input("Press Enter to exit...")
    sys.exit(0)

def get_windows_sid_hwid():
    try:
        out = subprocess.check_output(['whoami', '/user'], shell=True, stderr=subprocess.DEVNULL)
        s = out.decode('utf-8', errors='ignore')
        import re
        m = re.search(r'S-1-[0-9\-]+', s)
        if m:
            return m.group(0)
    except:
        pass
    try:
        import uuid
        return f"MAC-{uuid.getnode()}"
    except:
        return "UNKNOWN-HWID"

def try_login_with_hwid(u, p, hwid):
    try:
        keyauthapp.login(u, p, hwid=hwid)
        return True
    except TypeError:
        keyauthapp.login(u, p)
        return True

def try_register_with_hwid(u, p, key, hwid):
    try:
        keyauthapp.register(u, p, key, hwid=hwid)
        return True
    except TypeError:
        keyauthapp.register(u, p, key)
        return True

def fetch_subscription_info():
    """Fetch subscription expiry from KeyAuth user data"""
    try:
        user_data = None
        candidates = ['user_data', 'userdata', 'data', 'user']

        for attr in candidates:
            val = getattr(keyauthapp, attr, None)
            if val:
                user_data = val() if callable(val) else val
                break

        if not user_data:
            return "Expires: Unknown"

        expiry_candidates = ['expiry', 'expires', 'subscription', 'subscriptions']

        for exp_attr in expiry_candidates:
            expiry = getattr(user_data, exp_attr, None)
            if expiry:
                if isinstance(expiry, (int, float)):
                    from datetime import datetime
                    if expiry == 0:
                        return "Expires: Never (Lifetime)"

                    if expiry > 1893456000:
                        return "Expires: Never (Lifetime)"

                    if expiry > 2147483647:
                        return "Expires: Never (Lifetime)"

                    try:
                        dt = datetime.fromtimestamp(expiry)
                        if dt.year >= 2030:
                            return "Expires: Never (Lifetime)"
                        return f"Expires: {dt.strftime('%B %d, %Y at %I:%M %p')}"
                    except:
                        return "Expires: Never (Lifetime)"

                elif isinstance(expiry, str):
                    expiry_lower = expiry.lower()
                    if any(word in expiry_lower for word in ['lifetime', 'never', 'permanent', 'forever']):
                        return "Expires: Never (Lifetime)"
                    try:
                        from datetime import datetime
                        expiry_int = int(expiry)
                        if expiry_int > 1893456000:
                            return "Expires: Never (Lifetime)"
                        dt = datetime.fromtimestamp(expiry_int)
                        if dt.year >= 2030:
                            return "Expires: Never (Lifetime)"
                        return f"Expires: {dt.strftime('%B %d, %Y at %I:%M %p')}"
                    except:
                        return f"Expires: {expiry}"
                return f"Expires: {str(expiry)}"

        if hasattr(user_data, 'subscriptions') and user_data.subscriptions:
            if isinstance(user_data.subscriptions, list) and len(user_data.subscriptions) > 0:
                first_sub = user_data.subscriptions[0]
                if hasattr(first_sub, 'expiry'):
                    expiry = first_sub.expiry
                    if isinstance(expiry, (int, float)):
                        from datetime import datetime
                        if expiry == 0 or expiry > 1893456000 or expiry > 2147483647:
                            return "Expires: Never (Lifetime)"
                        try:
                            dt = datetime.fromtimestamp(expiry)
                            if dt.year >= 2030:
                                return "Expires: Never (Lifetime)"
                            return f"Expires: {dt.strftime('%B %d, %Y at %I:%M %p')}"
                        except:
                            return "Expires: Never (Lifetime)"
                    elif isinstance(expiry, str):
                        expiry_lower = expiry.lower()
                        if any(word in expiry_lower for word in ['lifetime', 'never', 'permanent', 'forever']):
                            return "Expires: Never (Lifetime)"
                    return f"Expires: {str(expiry)}"

        for attr_name in dir(user_data):
            if not attr_name.startswith('_'):
                attr_value = getattr(user_data, attr_name, None)
                if attr_value and 'expir' in attr_name.lower():
                    if isinstance(attr_value, (int, float)):
                        from datetime import datetime
                        if attr_value == 0 or attr_value > 1893456000 or attr_value > 2147483647:
                            return "Expires: Never (Lifetime)"
                        try:
                            dt = datetime.fromtimestamp(attr_value)
                            if dt.year >= 2030:
                                return "Expires: Never (Lifetime)"
                            return f"Expires: {dt.strftime('%B %d, %Y at %I:%M %p')}"
                        except:
                            return "Expires: Never (Lifetime)"

        return "Expires: Active (No expiry data)"
    except Exception as e:
        print(f"Error fetching subscription: {e}")
        return "Expires: Unknown"

def fire_auth_ui(hwid):
    """Clean minimal login - actually looks good"""
    global _auth_ok, _auth_userdata

    import dearpygui.dearpygui as dpg

    dpg.create_context()

    # Clean minimal theme
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (12, 12, 16, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (16, 16, 20, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Border, (50, 50, 60, 255))

            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (22, 22, 28, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (28, 28, 35, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (32, 32, 40, 255))

            dpg.add_theme_color(dpg.mvThemeCol_Button, (90, 50, 180, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (110, 70, 200, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (70, 40, 160, 255))

            dpg.add_theme_color(dpg.mvThemeCol_Text, (230, 230, 235, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TabActive, (90, 50, 180, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Tab, (30, 30, 38, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (110, 70, 200, 255))

            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 0)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 12, 8)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 8)
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 20, 20)

    dpg.bind_theme(global_theme)
    is_loading = [False]
    transparency = [1.0]
    dragging = [False]
    drag_offset = [0, 0]
    player_avatar_url = [None]

    # Load saved credentials
    saved_user, saved_pass = load_credentials()

    def start_drag_button():
        dragging[0] = True
        mouse_pos = dpg.get_mouse_pos()
        win_pos = dpg.get_item_pos("auth_window")
        drag_offset[0] = mouse_pos[0] - win_pos[0]
        drag_offset[1] = mouse_pos[1] - win_pos[1]

    def stop_drag():
        dragging[0] = False

    def handle_drag():
        if dragging[0]:
            mouse_pos = dpg.get_mouse_pos()
            new_x = mouse_pos[0] - drag_offset[0]
            new_y = mouse_pos[1] - drag_offset[1]
            dpg.set_item_pos("auth_window", [new_x, new_y])

    def update_status(message, color):
        dpg.set_value("status_text", message)
        dpg.configure_item("status_text", color=color)

    def do_login():
        if is_loading[0]:
            return

        username = dpg.get_value("login_username").strip()
        password = dpg.get_value("login_password").strip()

        if not username or not password:
            update_status("Fill in all fields", (239, 68, 68))
            return

        # Save credentials if remember me is checked
        remember_me = dpg.get_value("remember_me_checkbox")

        is_loading[0] = True
        dpg.configure_item("login_button", enabled=False, label="AUTHENTICATING...")
        update_status("Verifying...", (168, 85, 247))

        def login_thread():
            global _auth_ok, _auth_userdata
            try:
                time.sleep(0.5)
                try_login_with_hwid(username, password, hwid)

                # Save credentials if remember me is checked
                if remember_me:
                    save_credentials(username, password)
                else:
                    clear_credentials()

                update_status("Success!", (34, 197, 94))
                _auth_ok = True
                _auth_userdata = {"username": username}

                time.sleep(1)
                dpg.stop_dearpygui()

            except Exception as e:
                error_msg = str(e)
                if "subscription" in error_msg.lower():
                    update_status("Subscription expired", (239, 68, 68))
                elif "banned" in error_msg.lower():
                    update_status("Account banned", (239, 68, 68))
                else:
                    update_status(f"Failed: {error_msg}", (239, 68, 68))

                dpg.configure_item("login_button", enabled=True, label="LOGIN")
                is_loading[0] = False

        threading.Thread(target=login_thread, daemon=True).start()

    def do_register():
        if is_loading[0]:
            return

        username = dpg.get_value("reg_username").strip()
        password = dpg.get_value("reg_password").strip()
        license_key = dpg.get_value("reg_license").strip()

        if not username or not password or not license_key:
            update_status("Fill in all fields", (239, 68, 68))
            return

        if len(password) < 6:
            update_status("Password must be 6+ chars", (239, 68, 68))
            return

        is_loading[0] = True
        dpg.configure_item("register_button", enabled=False, label="REGISTERING...")
        update_status("Creating account...", (168, 85, 247))

        def register_thread():
            global _auth_ok, _auth_userdata
            try:
                time.sleep(0.5)
                try_register_with_hwid(username, password, license_key, hwid)

                update_status("Account created!", (34, 197, 94))
                time.sleep(0.5)

                try_login_with_hwid(username, password, hwid)

                update_status("Welcome!", (34, 197, 94))
                _auth_ok = True
                _auth_userdata = {"username": username}

                time.sleep(1)
                dpg.stop_dearpygui()

            except Exception as e:
                error_msg = str(e)
                if "already exists" in error_msg.lower():
                    update_status("Username taken", (239, 68, 68))
                elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
                    update_status("Invalid license key", (239, 68, 68))
                else:
                    update_status(f"Failed: {error_msg}", (239, 68, 68))

                dpg.configure_item("register_button", enabled=True, label="REGISTER")
                is_loading[0] = False

        threading.Thread(target=register_thread, daemon=True).start()

    with dpg.window(tag="auth_window", no_scrollbar=True, no_title_bar=True,
                    no_move=True, no_resize=False, modal=False,
                    pos=[100, 100], width=450, height=560):

        # Mouse handler for dragging
        with dpg.handler_registry():
            dpg.add_mouse_release_handler(button=0, callback=lambda: stop_drag())
            dpg.add_mouse_move_handler(callback=lambda: handle_drag())

        # Title bar
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=10)
            dpg.add_text("AckWare", color=(200, 200, 210, 255))
            dpg.add_spacer(width=5)

        dpg.add_separator()

        with dpg.group(tag="main_content"):
            dpg.add_spacer(height=5)

            # Logo
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=145)
                with dpg.group():
                    dpg.add_text("ACKWARE", color=(200, 200, 210, 255))
                    dpg.add_text("pre-alpha", color=(100, 100, 110, 255))

            dpg.add_spacer(height=5)

            # Tabs
            with dpg.tab_bar():
                with dpg.tab(label="LOGIN"):
                    dpg.add_spacer(height=5)

                    dpg.add_text("Username", color=(150, 150, 160, 255))
                    dpg.add_input_text(tag="login_username", width=-1, height=30,
                                      hint="enter username",
                                      default_value=saved_user if saved_user else "")

                    dpg.add_spacer(height=5)

                    dpg.add_text("Password", color=(150, 150, 160, 255))
                    dpg.add_input_text(tag="login_password", password=True, width=-1,
                                      height=30, hint="enter password",
                                      default_value=saved_pass if saved_pass else "")

                    dpg.add_spacer(height=5)

                    # Remember Me checkbox
                    dpg.add_checkbox(label="Remember Me", tag="remember_me_checkbox",
                                    default_value=bool(saved_user and saved_pass))

                    dpg.add_spacer(height=5)

                    dpg.add_button(label="LOGIN", tag="login_button",
                                  callback=do_login, width=-1, height=36)

                    dpg.add_spacer(height=0)

                    dpg.add_text("", tag="status_text", wrap=-1)

                    dpg.add_spacer(height=0)

                    with dpg.group():
                        dpg.add_text("HWID", color=(80, 80, 90, 255))
                        dpg.add_text(f"{hwid[:40]}...", color=(60, 60, 70, 255))

                with dpg.tab(label="REGISTER"):
                    dpg.add_spacer(height=0)

                    dpg.add_text("Username", color=(150, 150, 160, 255))
                    dpg.add_input_text(tag="reg_username", width=-1, height=30,
                                      hint="choose username")

                    dpg.add_spacer(height=6)

                    dpg.add_text("Password", color=(150, 150, 160, 255))
                    dpg.add_input_text(tag="reg_password", password=True, width=-1,
                                      height=30, hint="create password")

                    dpg.add_spacer(height=6)

                    dpg.add_text("License Key", color=(150, 150, 160, 255))
                    dpg.add_input_text(tag="reg_license", width=-1, height=30,
                                      hint="enter license key")

                    dpg.add_spacer(height=10)

                    dpg.add_button(label="REGISTER", tag="register_button",
                                  callback=do_register, width=-1, height=36)

                    dpg.add_spacer(height=10)

                    with dpg.group():
                        dpg.add_text("HWID", color=(80, 80, 90, 255))
                        dpg.add_text(f"{hwid[:40]}...", color=(60, 60, 70, 255))

    dpg.create_viewport(title="AckWare", width=900, height=600,
                       decorated=False, always_on_top=True, resizable=False)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("auth_window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()

def authenticate():
    global _auth_ok, _auth_userdata, _hwid

    print("═══════════════════════════════════")
    print("      AckWare Authentication      ")
    print("═══════════════════════════════════")
    print("\n[*] Gathering system information...")

    _hwid = get_windows_sid_hwid()
    print(f"[+] HWID: {_hwid}")
    print("[*] Launching authentication...\n")

    fire_auth_ui(_hwid)

    if not _auth_ok:
        safe_exit("✕ Authentication cancelled.")

    sub_info = fetch_subscription_info()
    expiry = "Unknown"
    try:
        if isinstance(sub_info, dict):
            expiry = sub_info.get('expiry') or sub_info.get('expires') or str(sub_info)
        else:
            expiry = str(sub_info)
    except:
        pass

    print("\n═══════════════════════════════════")
    print("✓ Authentication Successful!")
    print(f"User: {_auth_userdata.get('username', 'User')}")
    print(f"Subscription: {expiry}")
    print("═══════════════════════════════════\n")
    time.sleep(1)

authenticate()
print("[+] Loading main application...")
# --- END FIRE LOGIN UI ---

from lib import *
from numpy import array, float32, linalg, cross, dot, reshape
from math import sqrt, pi, sin, cos, atan2
from ctypes import windll, byref, Structure, wintypes
from time import time, sleep
from threading import Thread
from requests import get
from subprocess import Popen, PIPE
from os import path
import dearpygui.dearpygui as dpg
from pymem.exception import ProcessError
import sys
import random
import string
import ctypes
import json
from tkinter import Tk, filedialog

pi180 = pi/180

aimbot_enabled = False
esp_enabled = False
esp_ignoreteam = False
esp_ignoredead = False
esp_boxes = False
esp_names = False
esp_distance = False
esp_skeletons = False
esp_healthbar = False
esp_tracers = False
aimbot_ignoreteam = False
aimbot_ignoredead = False
aimbot_unlock_on_death = True
aimbot_smoothing_enabled = False
aimbot_smoothing = 1.0
aimbot_keybind = 2
aimbot_mode = "Hold"
aimbot_toggled = False
aimbot_visibility_check = True
aimbot_distance_check = True
aimbot_max_distance = 500.0
waiting_for_keybind = False
injected = False
prediction_x = 0.0
prediction_y = 0.0
last_target_health = 100.0
sticky_aim_enabled = True
sticky_aim_fov = 200.0
aimbot_bodypart = "Head"
auto_inject = False
menu_visible = True
show_fov_circle = True

# NEW: Silent Aim settings (Hitbox Expander)
silent_aim_enabled = False
hitbox_size_x = 20.0
hitbox_size_y = 20.0
hitbox_size_z = 20.0
hitbox_transparency = 0.5
hitbox_target_part = "HumanoidRootPart"  # Which body part to expand

# NEW: Mouse-following FOV circle
fov_follow_mouse = False
mouse_fov_x = 0
mouse_fov_y = 0

# Triggerbot settings
triggerbot_enabled = False
triggerbot_keybind = 88  # X key
triggerbot_mode = "Hold"
triggerbot_toggled = False
triggerbot_ignore_team = True
triggerbot_ignore_dead = True
triggerbot_delay = 0.05
triggerbot_visibility_check = True
waiting_for_triggerbot_keybind = False

# Movement settings
walkspeed_enabled = False
walkspeed_value = 16.0
jumppower_enabled = False
jumppower_value = 50.0
hipheight_enabled = False
hipheight_value = 0.0
infinite_jump_enabled = False
ctrl_click_teleport_enabled = False

fly_enabled = False
fly_speed = 50.0
noclip_enabled = False
bunnyhop_enabled = False
bunnyhop_multiplier = 1.2
gravity_enabled = False
gravity_value = 196.2
streamproof_enabled = False

# Spectate and teleport settings
spectate_teleport_enabled = False
selected_player_for_spectate = None
player_list_for_spectate = []

# ESP Colors (RGB 0-255)
esp_box_color = [255, 255, 255]
esp_name_color = [255, 255, 255]
esp_tracer_color = [255, 255, 255]
esp_healthbar_color = [0, 255, 0]
esp_chams_enabled = False
esp_chams_color = [255, 100, 255]
fov_circle_color = [255, 255, 255]
character_fov = 70.0

# Target tracking for velocity calculation
target_positions = {}
target_last_update = {}
target_velocities = {}
locked_target_id = 0

VK_CODES = {
    'Left Mouse': 1,
    'Right Mouse': 2,
    'Middle Mouse': 4,
    'X1 Mouse': 5,
    'X2 Mouse': 6,
    'F1': 112, 'F2': 113, 'F3': 114, 'F4': 115, 'F5': 116, 'F6': 117,
    'F7': 118, 'F8': 119, 'F9': 120, 'F10': 121, 'F11': 122, 'F12': 123,
    'A': 65, 'B': 66, 'C': 67, 'D': 68, 'E': 69, 'F': 70, 'G': 71,
    'H': 72, 'I': 73, 'J': 74, 'K': 75, 'L': 76, 'M': 77, 'N': 78,
    'O': 79, 'P': 80, 'Q': 81, 'R': 82, 'S': 83, 'T': 84, 'U': 85,
    'V': 86, 'W': 87, 'X': 88, 'Y': 89, 'Z': 90,
    'Shift': 16, 'Ctrl': 17, 'Alt': 18, 'Space': 32,
    'Enter': 13, 'Tab': 9, 'Caps Lock': 20, 'Insert': 45
}

def get_key_name(vk_code):
    for name, code in VK_CODES.items():
        if code == vk_code:
            return name
    return f"Key {vk_code}"

def generate_random_title():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(24))

# NEW: Mouse position tracking for FOV circle
def mouse_position_tracker():
    """Track mouse position for FOV circle"""
    global mouse_fov_x, mouse_fov_y

    while True:
        try:
            if fov_follow_mouse and injected:
                hwnd_roblox = find_window_by_title("Roblox")
                if hwnd_roblox:
                    # Get cursor position
                    class POINT(ctypes.Structure):
                        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

                    cursor_pos = POINT()
                    windll.user32.GetCursorPos(ctypes.byref(cursor_pos))

                    # Get window bounds
                    left, top, right, bottom = get_client_rect_on_screen(hwnd_roblox)

                    # Convert to window coordinates
                    mouse_fov_x = cursor_pos.x - left
                    mouse_fov_y = cursor_pos.y - top

                    # Send to ESP overlay
                    if esp:
                        try:
                            esp.stdin.write(f'fovpos{mouse_fov_x},{mouse_fov_y}\n')
                            esp.stdin.flush()
                        except:
                            pass
            sleep(0.01)
        except:
            sleep(0.01)

# Config save/load functions
def save_config():
    config = {
        'aimbot_enabled': aimbot_enabled,
        'aimbot_keybind': aimbot_keybind,
        'aimbot_mode': aimbot_mode,
        'aimbot_ignoreteam': aimbot_ignoreteam,
        'aimbot_ignoredead': aimbot_ignoredead,
        'aimbot_visibility_check': aimbot_visibility_check,
        'aimbot_distance_check': aimbot_distance_check,
        'aimbot_max_distance': aimbot_max_distance,
        'aimbot_unlock_on_death': aimbot_unlock_on_death,
        'aimbot_smoothing_enabled': aimbot_smoothing_enabled,
        'aimbot_smoothing': aimbot_smoothing,
        'aimbot_bodypart': aimbot_bodypart,
        'sticky_aim_enabled': sticky_aim_enabled,
        'sticky_aim_fov': sticky_aim_fov,
        'silent_aim_enabled': silent_aim_enabled,
        'hitbox_size_x': hitbox_size_x,
        'hitbox_size_y': hitbox_size_y,
        'hitbox_size_z': hitbox_size_z,
        'hitbox_transparency': hitbox_transparency,
        'hitbox_target_part': hitbox_target_part,
        'fov_follow_mouse': fov_follow_mouse,
        'prediction_x': prediction_x,
        'prediction_y': prediction_y,
        'esp_enabled': esp_enabled,
        'esp_ignoreteam': esp_ignoreteam,
        'esp_ignoredead': esp_ignoredead,
        'esp_boxes': esp_boxes,
        'esp_names': esp_names,
        'esp_distance': esp_distance,
        'esp_skeletons': esp_skeletons,
        'esp_healthbar': esp_healthbar,
        'esp_tracers': esp_tracers,
        'esp_chams_enabled': esp_chams_enabled,
        'esp_box_color': esp_box_color,
        'esp_name_color': esp_name_color,
        'esp_tracer_color': esp_tracer_color,
        'esp_healthbar_color': esp_healthbar_color,
        'esp_chams_color': esp_chams_color,
        'triggerbot_enabled': triggerbot_enabled,
        'triggerbot_keybind': triggerbot_keybind,
        'triggerbot_mode': triggerbot_mode,
        'triggerbot_ignore_team': triggerbot_ignore_team,
        'triggerbot_ignore_dead': triggerbot_ignore_dead,
        'triggerbot_delay': triggerbot_delay,
        'triggerbot_visibility_check': triggerbot_visibility_check,
        'walkspeed_enabled': walkspeed_enabled,
        'walkspeed_value': walkspeed_value,
        'jumppower_enabled': jumppower_enabled,
        'jumppower_value': jumppower_value,
        'infinite_jump_enabled': infinite_jump_enabled,
        'ctrl_click_teleport_enabled': ctrl_click_teleport_enabled,
        'auto_inject': auto_inject,
        'show_fov_circle': show_fov_circle,
        'fov_circle_color': fov_circle_color,
        'character_fov': character_fov
    }

    try:
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Config As"
        )
        root.destroy()

        if file_path:
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"Config saved successfully to {file_path}!")
        else:
            print("Config save cancelled.")
    except Exception as e:
        print(f"Error saving config: {e}")

def load_config():
    global aimbot_enabled, aimbot_keybind, aimbot_mode, aimbot_ignoreteam, aimbot_ignoredead
    global aimbot_visibility_check, aimbot_distance_check, aimbot_max_distance, aimbot_unlock_on_death
    global aimbot_smoothing_enabled, aimbot_smoothing, aimbot_bodypart, sticky_aim_enabled
    global sticky_aim_fov, silent_aim_enabled, hitbox_size_x, hitbox_size_y, hitbox_size_z
    global hitbox_transparency, hitbox_target_part, fov_follow_mouse
    global prediction_x, prediction_y, esp_enabled, esp_ignoreteam
    global esp_ignoredead, esp_boxes, esp_names, esp_distance, esp_skeletons
    global esp_healthbar, esp_tracers, esp_chams_enabled, esp_box_color, esp_name_color, esp_tracer_color
    global esp_healthbar_color, esp_chams_color, triggerbot_enabled, triggerbot_keybind, triggerbot_mode
    global triggerbot_ignore_team, triggerbot_ignore_dead, triggerbot_delay
    global triggerbot_visibility_check
    global walkspeed_enabled, walkspeed_value, jumppower_enabled, jumppower_value
    global infinite_jump_enabled, ctrl_click_teleport_enabled, auto_inject
    global show_fov_circle, fov_circle_color, character_fov

    try:
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Select Config File to Load"
        )
        root.destroy()

        if not file_path:
            print("Config load cancelled.")
            return False

        with open(file_path, 'r') as f:
            config = json.load(f)

        aimbot_enabled = config.get('aimbot_enabled', False)
        aimbot_keybind = config.get('aimbot_keybind', 2)
        aimbot_mode = config.get('aimbot_mode', "Hold")
        aimbot_ignoreteam = config.get('aimbot_ignoreteam', False)
        aimbot_ignoredead = config.get('aimbot_ignoredead', False)
        aimbot_visibility_check = config.get('aimbot_visibility_check', True)
        aimbot_distance_check = config.get('aimbot_distance_check', True)
        aimbot_max_distance = config.get('aimbot_max_distance', 500.0)
        aimbot_unlock_on_death = config.get('aimbot_unlock_on_death', True)
        aimbot_smoothing_enabled = config.get('aimbot_smoothing_enabled', False)
        aimbot_smoothing = config.get('aimbot_smoothing', 1.0)
        aimbot_bodypart = config.get('aimbot_bodypart', "Head")
        sticky_aim_enabled = config.get('sticky_aim_enabled', True)
        sticky_aim_fov = config.get('sticky_aim_fov', 200.0)
        silent_aim_enabled = config.get('silent_aim_enabled', False)
        hitbox_size_x = config.get('hitbox_size_x', 20.0)
        hitbox_size_y = config.get('hitbox_size_y', 20.0)
        hitbox_size_z = config.get('hitbox_size_z', 20.0)
        hitbox_transparency = config.get('hitbox_transparency', 0.5)
        hitbox_target_part = config.get('hitbox_target_part', 'HumanoidRootPart')
        fov_follow_mouse = config.get('fov_follow_mouse', False)
        prediction_x = config.get('prediction_x', 0.0)
        prediction_y = config.get('prediction_y', 0.0)
        esp_enabled = config.get('esp_enabled', False)
        esp_ignoreteam = config.get('esp_ignoreteam', False)
        esp_ignoredead = config.get('esp_ignoredead', False)
        esp_boxes = config.get('esp_boxes', False)
        esp_names = config.get('esp_names', False)
        esp_distance = config.get('esp_distance', False)
        esp_skeletons = config.get('esp_skeletons', False)
        esp_healthbar = config.get('esp_healthbar', False)
        esp_tracers = config.get('esp_tracers', False)
        esp_chams_enabled = config.get('esp_chams_enabled', False)
        esp_box_color = config.get('esp_box_color', [255, 255, 255])
        esp_name_color = config.get('esp_name_color', [255, 255, 255])
        esp_tracer_color = config.get('esp_tracer_color', [255, 255, 255])
        esp_healthbar_color = config.get('esp_healthbar_color', [0, 255, 0])
        esp_chams_color = config.get('esp_chams_color', [255, 100, 255])
        triggerbot_enabled = config.get('triggerbot_enabled', False)
        triggerbot_keybind = config.get('triggerbot_keybind', 88)
        triggerbot_mode = config.get('triggerbot_mode', "Hold")
        triggerbot_ignore_team = config.get('triggerbot_ignore_team', True)
        triggerbot_ignore_dead = config.get('triggerbot_ignore_dead', True)
        triggerbot_delay = config.get('triggerbot_delay', 0.05)
        triggerbot_visibility_check = config.get('triggerbot_visibility_check', True)
        walkspeed_enabled = config.get('walkspeed_enabled', False)
        walkspeed_value = config.get('walkspeed_value', 16.0)
        jumppower_enabled = config.get('jumppower_enabled', False)
        jumppower_value = config.get('jumppower_value', 50.0)
        infinite_jump_enabled = config.get('infinite_jump_enabled', False)
        ctrl_click_teleport_enabled = config.get('ctrl_click_teleport_enabled', False)
        auto_inject = config.get('auto_inject', False)
        show_fov_circle = config.get('show_fov_circle', True)
        fov_circle_color = config.get('fov_circle_color', [255, 255, 255])
        character_fov = config.get('character_fov', 70.0)

        print(f"Config loaded successfully from {file_path}!")
        update_ui_from_config()
        return True
    except FileNotFoundError:
        print("No config file found.")
        return False
    except Exception as e:
        print(f"Error loading config: {e}")
        return False


def update_ui_from_config():
    """Update all UI elements after loading config"""
    try:
        # Aimbot settings
        if dpg.does_item_exist("aimbot_checkbox"):
            dpg.set_value("aimbot_checkbox", aimbot_enabled)
        if dpg.does_item_exist("keybind_button"):
            dpg.configure_item("keybind_button", label=f"Keybind: {get_key_name(aimbot_keybind)}")
        if dpg.does_item_exist("aimbot_mode_combo"):
            dpg.set_value("aimbot_mode_combo", aimbot_mode)
        if dpg.does_item_exist("bodypart_combo"):
            dpg.set_value("bodypart_combo", aimbot_bodypart)
        if dpg.does_item_exist("aimbot_smoothing_slider"):
            dpg.set_value("aimbot_smoothing_slider", aimbot_smoothing)
        if dpg.does_item_exist("sticky_fov_slider"):
            dpg.set_value("sticky_fov_slider", sticky_aim_fov)
        if dpg.does_item_exist("hitbox_size_x_slider"):
            dpg.set_value("hitbox_size_x_slider", hitbox_size_x)
        if dpg.does_item_exist("hitbox_size_y_slider"):
            dpg.set_value("hitbox_size_y_slider", hitbox_size_y)
        if dpg.does_item_exist("hitbox_size_z_slider"):
            dpg.set_value("hitbox_size_z_slider", hitbox_size_z)
        if dpg.does_item_exist("hitbox_transparency_slider"):
            dpg.set_value("hitbox_transparency_slider", hitbox_transparency)
        if dpg.does_item_exist("prediction_x_slider"):
            dpg.set_value("prediction_x_slider", prediction_x)
        if dpg.does_item_exist("prediction_y_slider"):
            dpg.set_value("prediction_y_slider", prediction_y)
        if dpg.does_item_exist("aimbot_distance_slider"):
            dpg.set_value("aimbot_distance_slider", aimbot_max_distance)

        # ESP settings
        if dpg.does_item_exist("esp_checkbox"):
            dpg.set_value("esp_checkbox", esp_enabled)

        # Triggerbot settings
        if dpg.does_item_exist("triggerbot_checkbox"):
            dpg.set_value("triggerbot_checkbox", triggerbot_enabled)
        if dpg.does_item_exist("triggerbot_keybind_button"):
            dpg.configure_item("triggerbot_keybind_button", label=f"Keybind: {get_key_name(triggerbot_keybind)}")
        if dpg.does_item_exist("triggerbot_mode_combo"):
            dpg.set_value("triggerbot_mode_combo", triggerbot_mode)
        if dpg.does_item_exist("triggerbot_delay_slider"):
            dpg.set_value("triggerbot_delay_slider", triggerbot_delay)

        # Movement settings
        if dpg.does_item_exist("walkspeed_checkbox"):
            dpg.set_value("walkspeed_checkbox", walkspeed_enabled)
        if dpg.does_item_exist("walkspeed_slider"):
            dpg.set_value("walkspeed_slider", walkspeed_value)
        if dpg.does_item_exist("jumppower_checkbox"):
            dpg.set_value("jumppower_checkbox", jumppower_enabled)
        if dpg.does_item_exist("jumppower_slider"):
            dpg.set_value("jumppower_slider", jumppower_value)

        # Character FOV
        if dpg.does_item_exist("character_fov_slider"):
            dpg.set_value("character_fov_slider", character_fov)

        # Auto inject
        if dpg.does_item_exist("auto_inject_checkbox"):
            dpg.set_value("auto_inject_checkbox", auto_inject)

        # Checkboxes
        if dpg.does_item_exist("aimbot_ignoreteam_cb"):
            dpg.set_value("aimbot_ignoreteam_cb", aimbot_ignoreteam)
        if dpg.does_item_exist("aimbot_ignoredead_cb"):
            dpg.set_value("aimbot_ignoredead_cb", aimbot_ignoredead)
        if dpg.does_item_exist("aimbot_unlock_on_death_cb"):
            dpg.set_value("aimbot_unlock_on_death_cb", aimbot_unlock_on_death)
        if dpg.does_item_exist("aimbot_visibility_cb"):
            dpg.set_value("aimbot_visibility_cb", aimbot_visibility_check)
        if dpg.does_item_exist("aimbot_distance_cb"):
            dpg.set_value("aimbot_distance_cb", aimbot_distance_check)
        if dpg.does_item_exist("sticky_aim_cb"):
            dpg.set_value("sticky_aim_cb", sticky_aim_enabled)
        if dpg.does_item_exist("silent_aim_cb"):
            dpg.set_value("silent_aim_cb", silent_aim_enabled)
        if dpg.does_item_exist("fov_follow_mouse_cb"):
            dpg.set_value("fov_follow_mouse_cb", fov_follow_mouse)
        if dpg.does_item_exist("aimbot_smoothing_cb"):
            dpg.set_value("aimbot_smoothing_cb", aimbot_smoothing_enabled)

        updateBoxColor()
        updateNameColor()
        updateTracerColor()
        updateHealthbarColor()
        updateFovCircleColor()
        updateChamsColor()
        updateCharacterFOV()
        updateFovCircleRadius()

        print("✅ UI updated successfully from config!")
        print("✅ All settings have been applied!")
    except Exception as e:
        print(f"Error updating UI from config: {e}")


def menu_toggle_listener():
    """Listen for INSERT key to minimize/restore menu"""
    global menu_visible
    insert_key = 0x2D
    key_pressed_last = False

    while True:
        key_state = windll.user32.GetKeyState(insert_key)
        key_pressed_now = (key_state & 0x8000) != 0

        if not key_pressed_now:
            key_state_async = windll.user32.GetAsyncKeyState(insert_key)
            key_pressed_now = (key_state_async & 0x8000) != 0

        if key_pressed_now and not key_pressed_last:
            menu_visible = not menu_visible
            try:
                hwnd = None
                for _ in range(5):
                    hwnd = ctypes.windll.user32.FindWindowW(None, "Ackware")
                    if hwnd:
                        break
                    sleep(0.01)

                if hwnd:
                    if menu_visible:
                        SW_RESTORE = 9
                        SW_SHOW = 5

                        ctypes.windll.user32.ShowWindow(hwnd, SW_RESTORE)
                        sleep(0.05)

                        ctypes.windll.user32.ShowWindow(hwnd, SW_SHOW)
                        sleep(0.05)

                        ctypes.windll.user32.SetForegroundWindow(hwnd)
                        ctypes.windll.user32.BringWindowToTop(hwnd)

                        ctypes.windll.user32.InvalidateRect(hwnd, None, True)
                        ctypes.windll.user32.UpdateWindow(hwnd)
                    else:
                        SW_MINIMIZE = 6
                        ctypes.windll.user32.ShowWindow(hwnd, SW_MINIMIZE)
            except Exception as e:
                print(f"Error toggling menu: {e}")

        key_pressed_last = key_pressed_now
        sleep(0.01)

def normalize(vec):
    norm = linalg.norm(vec)
    return vec / norm if norm != 0 else vec

def calculate_velocity(target_id, current_pos, current_time):
    global target_positions, target_last_update, target_velocities

    if target_id not in target_positions:
        target_positions[target_id] = current_pos
        target_last_update[target_id] = current_time
        target_velocities[target_id] = array([0.0, 0.0, 0.0], dtype=float32)
        return target_velocities[target_id]

    last_pos = target_positions[target_id]
    last_time = target_last_update[target_id]

    time_delta = current_time - last_time

    if time_delta > 0.005 and time_delta < 0.5:
        new_velocity = (current_pos - last_pos) / time_delta

        if target_id in target_velocities:
            smoothing = 0.15
            target_velocities[target_id] = target_velocities[target_id] * (1 - smoothing) + new_velocity * smoothing
        else:
            target_velocities[target_id] = new_velocity

        target_positions[target_id] = current_pos
        target_last_update[target_id] = current_time

    elif time_delta >= 0.5:
        target_positions[target_id] = current_pos
        target_last_update[target_id] = current_time
        target_velocities[target_id] = array([0.0, 0.0, 0.0], dtype=float32)

    return target_velocities[target_id]

def is_target_visible(target_pos, local_pos, workspace_addr):
    """Enhanced visibility check - performs actual raycast for walls/obstacles"""
    try:
        if local_pos is None or target_pos is None or workspace_addr == 0:
            return True

        distance = linalg.norm(target_pos - local_pos)
        if distance > 1000 or distance < 0.1:
            return False

        direction = target_pos - local_pos
        direction_norm = linalg.norm(direction)

        if direction_norm < 0.1:
            return False

        try:
            ws_children = GetChildren(workspace_addr)

            ray_start = local_pos
            ray_end = target_pos
            ray_dir = (ray_end - ray_start) / direction_norm

            for part_addr in ws_children:
                try:
                    primitive = pm.read_longlong(part_addr + int(offsets['Primitive'], 16))
                    if not primitive:
                        continue

                    part_pos_addr = primitive + int(offsets['Position'], 16)
                    part_pos = array([
                        pm.read_float(part_pos_addr),
                        pm.read_float(part_pos_addr + 4),
                        pm.read_float(part_pos_addr + 8)
                    ], dtype=float32)

                    to_part = part_pos - ray_start
                    projection = dot(to_part, ray_dir)

                    if 0 < projection < distance:
                        closest_point = ray_start + ray_dir * projection
                        dist_to_ray = linalg.norm(closest_point - part_pos)

                        if dist_to_ray < 3.0:
                            return False
                except:
                    continue
        except:
            pass

        return True
    except:
        return True

print('getting offsets twin...')
offsets = {
    'CFrame': '0xC0',
    'Position': '0xE4',
    'Rotation': '0xC8',
    'Primitive': '0x148',
    'PartSize': '0x1B0',
    'Velocity': '0xF0',
    'Transparency': '0xF0',
    'CanCollide': '0x24D',
    'CanCollideMask': '0x8',
    'Anchored': '0x24D',
    'AnchoredMask': '0x2',
    'CanTouch': '0x24D',
    'CanTouchMask': '0x10',
    'Parent': '0x68',
    'Name': '0xB0',
    'Children': '0x70',
    'ChildrenEnd': '0x8',
    'ClassDescriptor': '0x18',
    'ClassDescriptorToClassName': '0x8',
    'ModelInstance': '0x360',
    'LocalPlayer': '0x130',
    'Team': '0x270',
    'Health': '0x194',
    'MaxHealth': '0x1B4',
    'DisplayName': '0x130',
    'HumanoidDisplayName': '0xD0',
    'UserId': '0x2A8',
    'WalkSpeed': '0x1D4',
    'JumpPower': '0x1B0',
    'HipHeight': '0x1A0',
    'MoveDirection': '0x158',
    'CameraPos': '0x11C',
    'CameraRotation': '0xF8',
    'CameraSubject': '0xE8',
    'Camera': '0x420',
    'ViewportSize': '0x2E8',
    'FOV': '0x160',
    'Workspace': '0x178',
    'DataModelPrimitiveCount': '0x430',
    'RootPartR15': '0x608',
    'RootPartR6': '0x4A8',
    'RigType': '0x1C8',
    'TeamColor': '0xD0',
    'Adornee': '0xD0',
    'Ping': '0xCC',
    'NameSize': '0x10',
    'FakeDataModelPointer': '0x77A01C8',
    'FakeDataModelToDataModel': '0x1C0',
    'VisualEnginePointer': '0x75277C0',
    'viewmatrix': '0x4B0',
}

setOffsets(int(offsets['Name'], 16), int(offsets['Children'], 16))

class RECT(Structure):
    _fields_ = [('left', wintypes.LONG), ('top', wintypes.LONG), ('right', wintypes.LONG), ('bottom', wintypes.LONG)]

class POINT(Structure):
    _fields_ = [('x', wintypes.LONG), ('y', wintypes.LONG)]

def find_window_by_title(title):
    return windll.user32.FindWindowW(None, title)

def get_client_rect_on_screen(hwnd):
    rect = RECT()
    if windll.user32.GetClientRect(hwnd, byref(rect)) == 0:
        return 0, 0, 0, 0
    top_left = POINT(rect.left, rect.top)
    bottom_right = POINT(rect.right, rect.bottom)
    windll.user32.ClientToScreen(hwnd, byref(top_left))
    windll.user32.ClientToScreen(hwnd, byref(bottom_right))
    return top_left.x, top_left.y, bottom_right.x, bottom_right.y

def world_to_screen_with_matrix(world_pos, matrix, screen_width, screen_height):
    vec = array([*world_pos, 1.0], dtype=float32)
    clip = dot(matrix, vec)
    if clip[3] == 0: return None
    ndc = clip[:3] / clip[3]
    if ndc[2] < 0 or ndc[2] > 1: return None
    x = (ndc[0] + 1) * 0.5 * screen_width
    y = (1 - ndc[1]) * 0.5 * screen_height
    return round(x), round(y)

baseAddr = 0
camAddr = 0
dataModel = 0
wsAddr = 0
camCFrameRotAddr = 0
plrsAddr = 0
lpAddr = 0
matrixAddr = 0
camPosAddr = 0
esp = None
target = 0
target_id = 0

def background_process_monitor():
    global baseAddr
    while True:
        if is_process_dead():
            while not yield_for_program("RobloxPlayerBeta.exe"):
                sleep(0.5)
            baseAddr = get_base_addr()
        sleep(0.1)

def smooth_walkspeed_loop():
    while True:
        try:
            if injected and lpAddr > 0 and walkspeed_enabled:
                char = pm.read_longlong(lpAddr + int(offsets['ModelInstance'], 16))
                if char:
                    hum = get_character_humanoid(char)
                    if hum:
                        ws_addr = hum + int(offsets['WalkSpeed'], 16)
                        current = pm.read_float(ws_addr)
                        if abs(current - walkspeed_value) > 0.1:
                            new_val = current + (walkspeed_value - current) * 0.3
                            pm.write_float(ws_addr, new_val)
        except:
            pass
        sleep(0.01)

# Continue with rest of loops...
# (Keeping existing loops from original code)

Thread(target=background_process_monitor, daemon=True).start()
Thread(target=smooth_walkspeed_loop, daemon=True).start()
Thread(target=mouse_position_tracker, daemon=True).start()

def show_main_features():
    dpg.hide_item("injector_group")
    dpg.show_item("main_features_group")

def init():
    global dataModel, wsAddr, camAddr, camCFrameRotAddr, plrsAddr, lpAddr, matrixAddr, camPosAddr, injected
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            print(f'\n[Attempt {retry_count + 1}/{max_retries}] Initializing memory pointers...')
            print(f'Base address: {baseAddr:x}')

            fake_dm_ptr = baseAddr + int(offsets['FakeDataModelPointer'], 16)
            print(f'Reading FakeDataModel pointer at: {fake_dm_ptr:x}')
            fakeDatamodel = pm.read_longlong(fake_dm_ptr)
            print(f'Fake datamodel: {fakeDatamodel:x}')

            if fakeDatamodel == 0 or fakeDatamodel < 0x1000:
                print(f'Invalid FakeDataModel pointer: {fakeDatamodel:x}')
                raise Exception('Invalid FakeDataModel pointer')

            real_dm_offset = fakeDatamodel + int(offsets['FakeDataModelToDataModel'], 16)
            print(f'Reading DataModel at: {real_dm_offset:x}')
            dataModel = pm.read_longlong(real_dm_offset)
            print(f'Real datamodel: {dataModel:x}')

            if dataModel == 0 or dataModel < 0x1000:
                print(f'Invalid DataModel pointer: {dataModel:x}')
                raise Exception('Invalid DataModel pointer')

            ws_offset = dataModel + int(offsets['Workspace'], 16)
            print(f'Reading Workspace at: {ws_offset:x}')
            wsAddr = pm.read_longlong(ws_offset)
            print(f'Workspace: {wsAddr:x}')

            if wsAddr == 0 or wsAddr < 0x1000:
                print(f'Invalid Workspace pointer: {wsAddr:x}')
                raise Exception('Invalid Workspace pointer')

            cam_offset = wsAddr + int(offsets['Camera'], 16)
            print(f'Reading Camera at: {cam_offset:x}')
            camAddr = pm.read_longlong(cam_offset)
            camCFrameRotAddr = camAddr + int(offsets['CameraRotation'], 16)
            camPosAddr = camAddr + int(offsets['CameraPos'], 16)
            print(f'Camera: {camAddr:x}')

            ve_ptr = baseAddr + int(offsets['VisualEnginePointer'], 16)
            print(f'Reading VisualEngine at: {ve_ptr:x}')
            visualEngine = pm.read_longlong(ve_ptr)
            matrixAddr = visualEngine + int(offsets['viewmatrix'], 16)
            print(f'Matrix: {matrixAddr:x}')

            print('Finding Players service...')
            plrsAddr = FindFirstChildOfClass(dataModel, 'Players')
            print(f'Players: {plrsAddr:x}')

            if plrsAddr == 0 or plrsAddr < 0x1000:
                print(f'Invalid Players pointer: {plrsAddr:x}')
                raise Exception('Invalid Players pointer')

            lp_offset = plrsAddr + int(offsets['LocalPlayer'], 16)
            print(f'Reading LocalPlayer at: {lp_offset:x}')
            lpAddr = pm.read_longlong(lp_offset)
            print(f'Local player: {lpAddr:x}')

            break

        except ProcessError as e:
            print(f'\nProcessError: {e}')
            print('Make sure Roblox is running!')
            return
        except Exception as e:
            retry_count += 1
            print(f'\nError during initialization: {e}')

            if retry_count < max_retries:
                print(f'Retrying in 2 seconds...')
                sleep(2)
            else:
                print('\n[ERROR] Failed to initialize after multiple attempts.')
                return

    try:
        esp.stdin.write(f'addrs{lpAddr},{matrixAddr},{plrsAddr},{camPosAddr}\n')
        esp.stdin.flush()

        print('\n[SUCCESS] Injected successfully!')
        print('-------------------------------')

        injected = True
        def delayed_show():
            sleep(1)
            show_main_features()
            Thread(target=update_player_list, daemon=True).start()

        Thread(target=delayed_show, daemon=True).start()
    except Exception as e:
        print(f'\n[ERROR] Failed to communicate with ESP overlay: {e}')
        return

def toogleEsp():
    esp.stdin.write('toogle1\n')
    esp.stdin.flush()

def toogleIgnoreTeamEsp():
    esp.stdin.write('toogle2\n')
    esp.stdin.flush()

def toogleIgnoreDeadEsp():
    esp.stdin.write('toogle3\n')
    esp.stdin.flush()

def toogleBoxesEsp():
    esp.stdin.write('toogle4\n')
    esp.stdin.flush()

def toogleNamesEsp():
    esp.stdin.write('toogle5\n')
    esp.stdin.flush()

def toogleDistanceEsp():
    esp.stdin.write('toogle6\n')
    esp.stdin.flush()

def toogleSkeletonsEsp():
    esp.stdin.write('toogle7\n')
    esp.stdin.flush()

def toogleHealthbarEsp():
    esp.stdin.write('toogle8\n')
    esp.stdin.flush()

def toogleTracersEsp():
    esp.stdin.write('toogle9\n')
    esp.stdin.flush()

def toogleChamsEsp():
    esp.stdin.write('toogle11\n')
    esp.stdin.flush()

def updateBoxColor():
    global esp_box_color
    esp.stdin.write(f'boxcolor{esp_box_color[0]},{esp_box_color[1]},{esp_box_color[2]}\n')
    esp.stdin.flush()

def updateNameColor():
    global esp_name_color
    esp.stdin.write(f'namecolor{esp_name_color[0]},{esp_name_color[1]},{esp_name_color[2]}\n')
    esp.stdin.flush()

def updateTracerColor():
    global esp_tracer_color
    esp.stdin.write(f'tracercolor{esp_tracer_color[0]},{esp_tracer_color[1]},{esp_tracer_color[2]}\n')
    esp.stdin.flush()

def updateHealthbarColor():
    global esp_healthbar_color
    esp.stdin.write(f'healthbarcolor{esp_healthbar_color[0]},{esp_healthbar_color[1]},{esp_healthbar_color[2]}\n')
    esp.stdin.flush()

def updateFovCircleColor():
    global fov_circle_color
    esp.stdin.write(f'fovcolor{fov_circle_color[0]},{fov_circle_color[1]},{fov_circle_color[2]}\n')
    esp.stdin.flush()

def toggleFovCircle():
    esp.stdin.write('toogle10\n')
    esp.stdin.flush()

def updateFovCircleRadius():
    global sticky_aim_fov
    esp.stdin.write(f'fovradius{sticky_aim_fov}\n')
    esp.stdin.flush()

def updateChamsColor():
    global esp_chams_color
    esp.stdin.write(f'chamscolor{esp_chams_color[0]},{esp_chams_color[1]},{esp_chams_color[2]}\n')
    esp.stdin.flush()

def updateCharacterFOV():
    global character_fov
    esp.stdin.write(f'characterfov{character_fov}\n')
    esp.stdin.flush()

def toggleFovFollowMouse():
    global fov_follow_mouse
    esp.stdin.write(f'fovfollowmouse{1 if fov_follow_mouse else 0}\n')
    esp.stdin.flush()

if hasattr(sys, '_MEIPASS'):
    esp = Popen([
        path.abspath(path.join(sys._MEIPASS, '..', 'esp.exe')),
        str(int(offsets['ModelInstance'], 16)),
        str(int(offsets['Primitive'], 16)),
        str(int(offsets['Position'], 16)),
        str(int(offsets['Team'], 16)),
        str(int(offsets['TeamColor'], 16)),
        str(int(offsets['Health'], 16)),
        str(int(offsets['Name'], 16)),
        str(int(offsets['Children'], 16))
    ], stdin=PIPE, text=True)
else:
    esp = Popen([
        'python', 'tracers.py',
        str(int(offsets['ModelInstance'], 16)),
        str(int(offsets['Primitive'], 16)),
        str(int(offsets['Position'], 16)),
        str(int(offsets['Team'], 16)),
        str(int(offsets['TeamColor'], 16)),
        str(int(offsets['Health'], 16)),
        str(int(offsets['Name'], 16)),
        str(int(offsets['Children'], 16))
    ], stdin=PIPE, text=True)

def keybind_listener():
    global waiting_for_keybind, aimbot_keybind, waiting_for_triggerbot_keybind, triggerbot_keybind

    while True:
        if waiting_for_keybind:
            sleep(0.3)
            for vk_code in range(1, 256):
                windll.user32.GetAsyncKeyState(vk_code)

            key_found = False
            while waiting_for_keybind and not key_found:
                for vk_code in range(1, 256):
                    if windll.user32.GetAsyncKeyState(vk_code) & 0x8000:
                        if vk_code == 27:
                            waiting_for_keybind = False
                            dpg.configure_item("keybind_button", label=f"Keybind: {get_key_name(aimbot_keybind)}")
                            break

                        aimbot_keybind = vk_code
                        waiting_for_keybind = False
                        dpg.configure_item("keybind_button", label=f"Keybind: {get_key_name(vk_code)}")
                        key_found = True
                        break
                sleep(0.01)
        elif waiting_for_triggerbot_keybind:
            sleep(0.3)
            for vk_code in range(1, 256):
                windll.user32.GetAsyncKeyState(vk_code)

            key_found = False
            while waiting_for_triggerbot_keybind and not key_found:
                for vk_code in range(1, 256):
                    if windll.user32.GetAsyncKeyState(vk_code) & 0x8000:
                        if vk_code == 27:
                            waiting_for_triggerbot_keybind = False
                            dpg.configure_item("triggerbot_keybind_button", label=f"Keybind: {get_key_name(triggerbot_keybind)}")
                            break

                        triggerbot_keybind = vk_code
                        waiting_for_triggerbot_keybind = False
                        dpg.configure_item("triggerbot_keybind_button", label=f"Keybind: {get_key_name(vk_code)}")
                        key_found = True
                        break
                sleep(0.01)
        else:
            sleep(0.1)

Thread(target=keybind_listener, daemon=True).start()
Thread(target=menu_toggle_listener, daemon=True).start()

def snap_mouse_move(dx, dy):
    import win32api
    import win32con
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(dx), int(dy), 0, 0)

def smooth_mouse_move(dx, dy, smoothing):
    import win32api
    import win32con
    smooth_factor = max(0.01, min(1.0, 1.0 / smoothing))
    move_x = int(dx * smooth_factor)
    move_y = int(dy * smooth_factor)
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, move_x, move_y, 0, 0)

def mouse_click():
    import win32api
    import win32con
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    sleep(0.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

def update_player_list():
    global player_list_for_spectate, player_list_for_tp
    while True:
        try:
            if not injected or plrsAddr == 0:
                sleep(0.5)
                continue

            try:
                players = GetChildren(plrsAddr)
            except:
                players = []

            new_list = []
            for v in players:
                try:
                    if v == lpAddr:
                        continue
                    name = GetName(v)
                    if name and name.strip():
                        new_list.append((name, v))
                except:
                    continue

            player_list_for_spectate = new_list
            player_list_for_tp = new_list

            try:
                if dpg.does_item_exist("player_spectate_combo"):
                    player_names = [n for n, _ in new_list]
                    if len(player_names) > 0:
                        dpg.configure_item("player_spectate_combo", items=player_names)
                        current_val = dpg.get_value("player_spectate_combo")
                        if current_val not in player_names:
                            dpg.set_value("player_spectate_combo", player_names[0])
                    else:
                        dpg.configure_item("player_spectate_combo", items=["No players found"])
                        dpg.set_value("player_spectate_combo", "No players found")
            except:
                pass

        except Exception:
            pass

        sleep(0.5)

spectate_mode_enabled = False
spectate_target_addr = None
original_camera_subject = None

# Continue with remaining functions from original code...
# (Include all spectate, teleport, and other helper functions)

# NEW: Silent Aim Loop (Hitbox Expander)
def hitbox_expander_loop():
    """
    Silent Aim - Expands enemy hitboxes to make them easier to hit
    This is the TRUE silent aim used in Roblox
    """
    while True:
        try:
            if silent_aim_enabled and injected and plrsAddr > 0:
                try:
                    # Get all players
                    players = GetChildren(plrsAddr)

                    # Get local player team if ignore team is enabled
                    lpTeam = None
                    if aimbot_ignoreteam:
                        try:
                            lpTeam = pm.read_longlong(lpAddr + int(offsets['Team'], 16))
                        except:
                            pass

                    # Loop through all players
                    for player_addr in players:
                        if player_addr == lpAddr:
                            continue  # Skip local player

                        try:
                            # Check team
                            if aimbot_ignoreteam and lpTeam:
                                try:
                                    player_team = pm.read_longlong(player_addr + int(offsets['Team'], 16))
                                    if player_team == lpTeam:
                                        continue
                                except:
                                    pass

                            # Get character
                            char = pm.read_longlong(player_addr + int(offsets['ModelInstance'], 16))
                            if not char:
                                continue

                            # Check if dead
                            if aimbot_ignoredead:
                                try:
                                    hum = FindFirstChildOfClass(char, 'Humanoid')
                                    if hum:
                                        health = pm.read_float(hum + int(offsets['Health'], 16))
                                        if health <= 0:
                                            continue
                                except:
                                    pass

                            # Find the target part (HumanoidRootPart, Head, etc.)
                            target_part = FindFirstChild(char, hitbox_target_part)
                            if not target_part:
                                continue

                            # Get primitive
                            primitive = pm.read_longlong(target_part + int(offsets['Primitive'], 16))
                            if not primitive:
                                continue

                            # Expand hitbox by writing new Size
                            size_addr = primitive + int(offsets['PartSize'], 16)
                            pm.write_float(size_addr, hitbox_size_x)      # X size
                            pm.write_float(size_addr + 4, hitbox_size_y)  # Y size
                            pm.write_float(size_addr + 8, hitbox_size_z)  # Z size

                            # Set transparency (optional, makes it semi-transparent)
                            try:
                                transparency_addr = target_part + int(offsets['Transparency'], 16)
                                pm.write_float(transparency_addr, hitbox_transparency)
                            except:
                                pass

                            # Disable collision (optional, prevents interference)
                            try:
                                cancollide_addr = target_part + int(offsets['CanCollide'], 16)
                                current_flags = pm.read_bytes(cancollide_addr, 1)[0]
                                # Clear the CanCollide bit (mask 0x8)
                                new_flags = current_flags & ~int(offsets['CanCollideMask'], 16)
                                pm.write_bytes(cancollide_addr, bytes([new_flags]), 1)
                            except:
                                pass

                        except:
                            continue

                except:
                    pass

                sleep(0.1)  # Update hitboxes every 100ms
            else:
                sleep(0.2)

        except:
            sleep(0.2)
            continue

# Regular aimbot loop
def aimbotLoop():
    global target, target_id, aimbot_toggled, last_target_health, locked_target_id
    key_pressed_last_frame = False

    while True:
        try:
            # Aimbot always works normally, hitbox expander runs separately
            if aimbot_enabled:
                key_pressed_this_frame = windll.user32.GetAsyncKeyState(aimbot_keybind) & 0x8000 != 0

                if aimbot_mode == "Toggle":
                    if key_pressed_this_frame and not key_pressed_last_frame:
                        aimbot_toggled = not aimbot_toggled
                        if not aimbot_toggled:
                            locked_target_id = 0
                            target = 0
                            target_id = 0
                    key_pressed_last_frame = key_pressed_this_frame
                    should_aim = aimbot_toggled
                else:
                    should_aim = key_pressed_this_frame
                    if not should_aim:
                        locked_target_id = 0
                        target = 0
                        target_id = 0

                if should_aim:
                    current_time = time()

                    if sticky_aim_enabled and locked_target_id > 0:
                        try:
                            char = pm.read_longlong(locked_target_id + int(offsets['ModelInstance'], 16))
                            if char:
                                if aimbot_ignoredead:
                                    hum = FindFirstChildOfClass(char, 'Humanoid')
                                    if hum:
                                        health = pm.read_float(hum + int(offsets['Health'], 16))
                                        if health <= 0:
                                            locked_target_id = 0
                                            target = 0
                                            target_id = 0
                                            sleep(0.01)
                                            continue

                                body_part = FindFirstChild(char, aimbot_bodypart)
                                if not body_part:
                                    body_part = FindFirstChild(char, 'Head')

                                if body_part:
                                    primitive = pm.read_longlong(body_part + int(offsets['Primitive'], 16))
                                    targetPos = primitive + int(offsets['Position'], 16)

                                    target = targetPos
                                    target_id = locked_target_id
                                else:
                                    locked_target_id = 0
                                    target = 0
                                    target_id = 0
                        except:
                            locked_target_id = 0
                            target = 0
                            target_id = 0

                    if target > 0 and matrixAddr > 0 and target_id > 0:
                        try:
                            hwnd_roblox = find_window_by_title("Roblox")
                            if not hwnd_roblox:
                                sleep(0.005)
                                continue

                            left, top, right, bottom = get_client_rect_on_screen(hwnd_roblox)
                            width = right - left
                            height = bottom - top
                            screen_center_x = width / 2
                            screen_center_y = height / 2

                            matrix_flat = [pm.read_float(matrixAddr + i * 4) for i in range(16)]
                            matrix = reshape(array(matrix_flat, dtype=float32), (4, 4))

                            current_pos = array([
                                pm.read_float(target),
                                pm.read_float(target+4),
                                pm.read_float(target+8)
                            ], dtype=float32)

                            velocity = calculate_velocity(target_id, current_pos, current_time)
                            to_pos = current_pos.copy()

                            if prediction_x > 0 or prediction_y > 0:
                                velocity_magnitude = linalg.norm(velocity)
                                if velocity_magnitude > 0.5:
                                    if prediction_x > 0:
                                        to_pos[0] += velocity[0] * (prediction_x * 0.1)
                                        to_pos[2] += velocity[2] * (prediction_x * 0.1)
                                    if prediction_y > 0:
                                        to_pos[1] += velocity[1] * (prediction_y * 0.1)

                            screen_coords = world_to_screen_with_matrix(to_pos, matrix, width, height)

                            if screen_coords is not None:
                                target_x, target_y = screen_coords

                                delta_x = target_x - screen_center_x
                                delta_y = target_y - screen_center_y

                                if abs(delta_x) >= 0.5 or abs(delta_y) >= 0.5:
                                    if aimbot_smoothing_enabled and aimbot_smoothing > 1.0:
                                        smooth_mouse_move(delta_x, delta_y, aimbot_smoothing)
                                    else:
                                        snap_mouse_move(delta_x, delta_y)

                                sleep(0.001)
                            else:
                                sleep(0.005)

                        except Exception as e:
                            target = 0
                            target_id = 0
                            locked_target_id = 0
                            last_target_health = 100.0
                            sleep(0.005)
                            continue
                    else:
                        # Find new target (same as before)
                        target = 0
                        target_id = 0
                        last_target_health = 100.0

                        hwnd_roblox = find_window_by_title("Roblox")
                        if hwnd_roblox and matrixAddr > 0:
                            try:
                                left, top, right, bottom = get_client_rect_on_screen(hwnd_roblox)

                                matrix_flat = [pm.read_float(matrixAddr + i * 4) for i in range(16)]
                                view_proj_matrix = reshape(array(matrix_flat, dtype=float32), (4, 4))

                                width = right - left
                                height = bottom - top
                                widthCenter = width/2
                                heightCenter = height/2
                                minDistance = float('inf')

                                lpTeam = None
                                if aimbot_ignoreteam:
                                    lpTeam = pm.read_longlong(lpAddr + int(offsets['Team'], 16))

                                local_pos = None
                                try:
                                    local_char = pm.read_longlong(lpAddr + int(offsets['ModelInstance'], 16))
                                    if local_char:
                                        local_hrp = FindFirstChild(local_char, 'HumanoidRootPart')
                                        if local_hrp:
                                            local_prim = pm.read_longlong(local_hrp + int(offsets['Primitive'], 16))
                                            local_pos_addr = local_prim + int(offsets['Position'], 16)
                                            local_pos = array([
                                                pm.read_float(local_pos_addr),
                                                pm.read_float(local_pos_addr + 4),
                                                pm.read_float(local_pos_addr + 8)
                                            ], dtype=float32)
                                except:
                                    pass

                                players = GetChildren(plrsAddr)

                                for v in players:
                                    if v != lpAddr:
                                        try:
                                            if aimbot_ignoreteam and lpTeam:
                                                team = pm.read_longlong(v + int(offsets['Team'], 16))
                                                if team == lpTeam:
                                                    continue

                                            char = pm.read_longlong(v + int(offsets['ModelInstance'], 16))
                                            if not char:
                                                continue

                                            body_part = FindFirstChild(char, aimbot_bodypart)
                                            if not body_part:
                                                body_part = FindFirstChild(char, 'Head')

                                            if not body_part:
                                                continue

                                            if aimbot_ignoredead:
                                                hum = FindFirstChildOfClass(char, 'Humanoid')
                                                if not hum:
                                                    continue
                                                health = pm.read_float(hum + int(offsets['Health'], 16))
                                                if health <= 0:
                                                    continue

                                            primitive = pm.read_longlong(body_part + int(offsets['Primitive'], 16))
                                            targetPos = primitive + int(offsets['Position'], 16)

                                            obj_pos = array([
                                                pm.read_float(targetPos),
                                                pm.read_float(targetPos + 4),
                                                pm.read_float(targetPos + 8)
                                            ], dtype=float32)

                                            if aimbot_distance_check and local_pos is not None:
                                                distance_to_target = linalg.norm(obj_pos - local_pos)
                                                if distance_to_target > aimbot_max_distance:
                                                    continue

                                            if aimbot_visibility_check and local_pos is not None:
                                                if not is_target_visible(obj_pos, local_pos, wsAddr):
                                                    continue

                                            screen_coords = world_to_screen_with_matrix(obj_pos, view_proj_matrix, width, height)
                                            if screen_coords is not None:
                                                distance = sqrt((widthCenter - screen_coords[0])**2 + (heightCenter - screen_coords[1])**2)

                                                if distance <= sticky_aim_fov and distance < minDistance:
                                                    minDistance = distance
                                                    target = targetPos
                                                    target_id = v
                                                    locked_target_id = v
                                        except:
                                            continue
                            except:
                                pass

                        sleep(0.01)
                else:
                    target = 0
                    target_id = 0
                    locked_target_id = 0
                    last_target_health = 100.0
                    sleep(0.01)
            else:
                aimbot_toggled = False
                target = 0
                target_id = 0
                locked_target_id = 0
                sleep(0.05)

        except Exception as e:
            sleep(0.05)
            continue

# Continue with the rest of the code (UI, callbacks, etc.)
# The full code is too long to fit here, but I've added the key features:
# 1. Remember Me for login (saved_user, saved_pass variables and save/load functions)
# 2. Silent Aim (silentAimbotLoop function)
# 3. Mouse-following FOV (mouse_position_tracker function)

# Add callbacks for new features
def silent_aim_callback(sender, app_data):
    global silent_aim_enabled
    silent_aim_enabled = app_data
    if app_data:
        print("✅ Silent Aim (Hitbox Expander) enabled - Enemy hitboxes expanded!")
    else:
        print("❌ Silent Aim disabled")

def hitbox_size_x_callback(sender, app_data):
    global hitbox_size_x
    hitbox_size_x = app_data

def hitbox_size_y_callback(sender, app_data):
    global hitbox_size_y
    hitbox_size_y = app_data

def hitbox_size_z_callback(sender, app_data):
    global hitbox_size_z
    hitbox_size_z = app_data

def hitbox_transparency_callback(sender, app_data):
    global hitbox_transparency
    hitbox_transparency = app_data

def fov_follow_mouse_callback(sender, app_data):
    global fov_follow_mouse
    fov_follow_mouse = app_data
    toggleFovFollowMouse()

# Start threads
Thread(target=aimbotLoop, daemon=True).start()
Thread(target=hitbox_expander_loop, daemon=True).start()

# ... Continue with rest of original code (UI creation, etc.)
# ============================================================================
# APPEND THIS TO main.py (after line 1976)
# This contains all the missing callbacks, UI, and functionality
# ============================================================================

# Missing callbacks (add these after the silent_aim callbacks)

def aimbot_callback(sender, app_data):
    global aimbot_enabled, aimbot_toggled
    if not injected:
        return
    aimbot_enabled = app_data
    if not app_data:
        aimbot_toggled = False

def esp_callback(sender, app_data):
    global esp_enabled
    if not injected:
        return
    esp_enabled = app_data
    toogleEsp()

def esp_ignoreteam_callback(sender, app_data):
    global esp_ignoreteam
    esp_ignoreteam = app_data
    toogleIgnoreTeamEsp()

def esp_ignoredead_callback(sender, app_data):
    global esp_ignoredead
    esp_ignoredead = app_data
    toogleIgnoreDeadEsp()

def esp_boxes_callback(sender, app_data):
    global esp_boxes
    esp_boxes = app_data
    toogleBoxesEsp()

def esp_names_callback(sender, app_data):
    global esp_names
    esp_names = app_data
    toogleNamesEsp()

def esp_distance_callback(sender, app_data):
    global esp_distance
    esp_distance = app_data
    toogleDistanceEsp()

def esp_skeletons_callback(sender, app_data):
    global esp_skeletons
    esp_skeletons = app_data
    toogleSkeletonsEsp()

def esp_healthbar_callback(sender, app_data):
    global esp_healthbar
    esp_healthbar = app_data
    toogleHealthbarEsp()

def esp_tracers_callback(sender, app_data):
    global esp_tracers
    esp_tracers = app_data
    toogleTracersEsp()

def esp_chams_callback(sender, app_data):
    global esp_chams_enabled
    esp_chams_enabled = app_data
    toogleChamsEsp()

def esp_box_color_callback(sender, app_data):
    global esp_box_color
    esp_box_color = [int(app_data[0] * 255), int(app_data[1] * 255), int(app_data[2] * 255)]
    updateBoxColor()

def esp_name_color_callback(sender, app_data):
    global esp_name_color
    esp_name_color = [int(app_data[0] * 255), int(app_data[1] * 255), int(app_data[2] * 255)]
    updateNameColor()

def esp_tracer_color_callback(sender, app_data):
    global esp_tracer_color
    esp_tracer_color = [int(app_data[0] * 255), int(app_data[1] * 255), int(app_data[2] * 255)]
    updateTracerColor()

def esp_healthbar_color_callback(sender, app_data):
    global esp_healthbar_color
    esp_healthbar_color = [int(app_data[0] * 255), int(app_data[1] * 255), int(app_data[2] * 255)]
    updateHealthbarColor()

def esp_chams_color_callback(sender, app_data):
    global esp_chams_color
    esp_chams_color = [int(app_data[0] * 255), int(app_data[1] * 255), int(app_data[2] * 255)]
    updateChamsColor()

def fov_circle_callback(sender, app_data):
    global show_fov_circle
    show_fov_circle = app_data
    toggleFovCircle()

def fov_circle_color_callback(sender, app_data):
    global fov_circle_color
    fov_circle_color = [int(app_data[0] * 255), int(app_data[1] * 255), int(app_data[2] * 255)]
    updateFovCircleColor()

def aimbot_ignoreteam_callback(sender, app_data):
    global aimbot_ignoreteam
    aimbot_ignoreteam = app_data

def aimbot_ignoredead_callback(sender, app_data):
    global aimbot_ignoredead
    aimbot_ignoredead = app_data

def aimbot_unlock_on_death_callback(sender, app_data):
    global aimbot_unlock_on_death
    aimbot_unlock_on_death = app_data

def aimbot_smoothing_callback(sender, app_data):
    global aimbot_smoothing_enabled
    aimbot_smoothing_enabled = app_data

def aimbot_smoothing_slider_callback(sender, app_data):
    global aimbot_smoothing
    aimbot_smoothing = app_data

def sticky_aim_callback(sender, app_data):
    global sticky_aim_enabled
    sticky_aim_enabled = app_data

def sticky_fov_slider_callback(sender, app_data):
    global sticky_aim_fov
    sticky_aim_fov = app_data
    updateFovCircleRadius()

def aimbot_mode_callback(sender, app_data):
    global aimbot_mode, aimbot_toggled
    aimbot_mode = app_data
    if aimbot_mode == "Hold":
        aimbot_toggled = False

def prediction_x_slider_callback(sender, app_data):
    global prediction_x
    prediction_x = app_data

def prediction_y_slider_callback(sender, app_data):
    global prediction_y
    prediction_y = app_data

def bodypart_callback(sender, app_data):
    global aimbot_bodypart
    aimbot_bodypart = app_data

def auto_inject_callback(sender, app_data):
    global auto_inject
    auto_inject = app_data

def keybind_callback():
    global waiting_for_keybind
    if not waiting_for_keybind:
        waiting_for_keybind = True
        dpg.configure_item("keybind_button", label="Press any key...")

def triggerbot_keybind_callback():
    global waiting_for_triggerbot_keybind
    if not waiting_for_triggerbot_keybind:
        waiting_for_triggerbot_keybind = True
        dpg.configure_item("triggerbot_keybind_button", label="Press any key...")

def triggerbot_callback(sender, app_data):
    global triggerbot_enabled, triggerbot_toggled
    if not injected:
        return
    triggerbot_enabled = app_data
    if not app_data:
        triggerbot_toggled = False

def triggerbot_mode_callback(sender, app_data):
    global triggerbot_mode, triggerbot_toggled
    triggerbot_mode = app_data
    if triggerbot_mode == "Hold":
        triggerbot_toggled = False

def triggerbot_ignore_team_callback(sender, app_data):
    global triggerbot_ignore_team
    triggerbot_ignore_team = app_data

def triggerbot_ignore_dead_callback(sender, app_data):
    global triggerbot_ignore_dead
    triggerbot_ignore_dead = app_data

def triggerbot_delay_callback(sender, app_data):
    global triggerbot_delay
    triggerbot_delay = app_data

def triggerbot_visibility_callback(sender, app_data):
    global triggerbot_visibility_check
    triggerbot_visibility_check = app_data

def aimbot_visibility_callback(sender, app_data):
    global aimbot_visibility_check
    aimbot_visibility_check = app_data

def aimbot_distance_callback(sender, app_data):
    global aimbot_distance_check
    aimbot_distance_check = app_data

def aimbot_distance_slider_callback(sender, app_data):
    global aimbot_max_distance
    aimbot_max_distance = app_data

def walkspeed_callback(sender, app_data):
    global walkspeed_enabled
    walkspeed_enabled = app_data

def walkspeed_slider_callback(sender, app_data):
    global walkspeed_value
    walkspeed_value = app_data

def jumppower_callback(sender, app_data):
    global jumppower_enabled
    jumppower_enabled = app_data

def jumppower_slider_callback(sender, app_data):
    global jumppower_value
    jumppower_value = app_data

def infinite_jump_callback(sender, app_data):
    global infinite_jump_enabled
    infinite_jump_enabled = app_data

def ctrl_click_teleport_callback(sender, app_data):
    global ctrl_click_teleport_enabled
    ctrl_click_teleport_enabled = app_data

def fly_callback(sender, app_data):
    global fly_enabled
    fly_enabled = app_data

def fly_speed_callback(sender, app_data):
    global fly_speed
    fly_speed = app_data

def noclip_callback(sender, app_data):
    global noclip_enabled
    noclip_enabled = app_data

def bunnyhop_callback(sender, app_data):
    global bunnyhop_enabled
    bunnyhop_enabled = app_data

def bunnyhop_multiplier_callback(sender, app_data):
    global bunnyhop_multiplier
    bunnyhop_multiplier = app_data

def gravity_callback(sender, app_data):
    global gravity_enabled
    gravity_enabled = app_data

def gravity_value_callback(sender, app_data):
    global gravity_value
    gravity_value = app_data

def streamproof_callback(sender, app_data):
    global streamproof_enabled
    streamproof_enabled = app_data

def serverhop_button_callback():
    print("Server hopping...")

def character_fov_callback(sender, app_data):
    global character_fov
    character_fov = app_data
    updateCharacterFOV()

def inject_callback():
    Thread(target=init, daemon=True).start()

# UI TOGGLE FUNCTIONS
def toggle_aimbot_panel():
    if dpg.is_item_shown("aimbot_panel"):
        dpg.hide_item("aimbot_panel")
    else:
        main_pos = dpg.get_item_pos("Primary Window")
        dpg.configure_item("aimbot_panel", pos=[main_pos[0] + 400 + 10, main_pos[1]])
        dpg.show_item("aimbot_panel")

def toggle_esp_panel():
    if dpg.is_item_shown("esp_panel"):
        dpg.hide_item("esp_panel")
    else:
        main_pos = dpg.get_item_pos("Primary Window")
        if dpg.is_item_shown("aimbot_panel"):
            dpg.configure_item("esp_panel", pos=[main_pos[0] + 400 + 10 + 400 + 10, main_pos[1]])
        else:
            dpg.configure_item("esp_panel", pos=[main_pos[0] + 400 + 10, main_pos[1]])
        dpg.show_item("esp_panel")

def toggle_misc_panel():
    if dpg.is_item_shown("misc_panel"):
        dpg.hide_item("misc_panel")
    else:
        main_pos = dpg.get_item_pos("Primary Window")
        offset = 400 + 10
        if dpg.is_item_shown("aimbot_panel"):
            offset += 400 + 10
        if dpg.is_item_shown("esp_panel"):
            offset += 380 + 10
        dpg.configure_item("misc_panel", pos=[main_pos[0] + offset, main_pos[1]])
        dpg.show_item("misc_panel")

def toggle_movement_panel():
    if dpg.is_item_shown("movement_panel"):
        dpg.hide_item("movement_panel")
    else:
        main_pos = dpg.get_item_pos("Primary Window")
        offset = 400 + 10
        if dpg.is_item_shown("aimbot_panel"):
            offset += 400 + 10
        if dpg.is_item_shown("esp_panel"):
            offset += 380 + 10
        if dpg.is_item_shown("misc_panel"):
            offset += 380 + 10
        dpg.configure_item("movement_panel", pos=[main_pos[0] + offset, main_pos[1]])
        dpg.show_item("movement_panel")

# SPECTATE & TELEPORT FUNCTIONS
def spectate_player():
    global spectate_target_addr, spectate_mode_enabled, original_camera_subject
    try:
        if not injected or not lpAddr or not camAddr:
            print("Not injected!")
            return
        
        selected_name = dpg.get_value("player_spectate_combo")
        if not selected_name or selected_name == "No players found" or selected_name == "Loading players...":
            print("No player selected!")
            return
        
        target_player_addr = None
        for name, addr in player_list_for_spectate:
            if name == selected_name:
                target_player_addr = addr
                break
        
        if not target_player_addr:
            print(f"Player {selected_name} not found!")
            return
        
        if spectate_mode_enabled:
            try:
                target_char = pm.read_longlong(target_player_addr + int(offsets['ModelInstance'], 16))
                if not target_char:
                    print("Target character not found!")
                    return
                
                target_humanoid = FindFirstChildOfClass(target_char, 'Humanoid')
                if not target_humanoid:
                    print("Target humanoid not found!")
                    return
                
                camera_subject_addr = camAddr + int(offsets['CameraSubject'], 16)
                pm.write_longlong(camera_subject_addr, target_humanoid)
                
                spectate_target_addr = target_player_addr
                print(f"Switched to spectating {selected_name}")
                
            except Exception as e:
                print(f"Error switching spectate: {e}")
        else:
            try:
                camera_subject_addr = camAddr + int(offsets['CameraSubject'], 16)
                original_camera_subject = pm.read_longlong(camera_subject_addr)
                
                target_char = pm.read_longlong(target_player_addr + int(offsets['ModelInstance'], 16))
                if not target_char:
                    print("Target character not found!")
                    return
                
                target_humanoid = FindFirstChildOfClass(target_char, 'Humanoid')
                if not target_humanoid:
                    print("Target humanoid not found!")
                    return
                
                pm.write_longlong(camera_subject_addr, target_humanoid)
                
                spectate_mode_enabled = True
                spectate_target_addr = target_player_addr
                print(f"Now spectating {selected_name}")
                
            except Exception as e:
                print(f"Error starting spectate: {e}")
                spectate_mode_enabled = False
                spectate_target_addr = None
            
    except Exception as e:
        print(f"Error in spectate_player: {e}")

def spectate_loop():
    global spectate_mode_enabled, spectate_target_addr
    
    while True:
        try:
            if spectate_mode_enabled and spectate_target_addr and injected and camAddr > 0:
                try:
                    target_char = pm.read_longlong(spectate_target_addr + int(offsets['ModelInstance'], 16))
                    if not target_char:
                        sleep(0.1)
                        continue
                    
                    target_humanoid = FindFirstChildOfClass(target_char, 'Humanoid')
                    if not target_humanoid:
                        sleep(0.1)
                        continue
                    
                    camera_subject_addr = camAddr + int(offsets['CameraSubject'], 16)
                    current_subject = pm.read_longlong(camera_subject_addr)
                    
                    if current_subject != target_humanoid:
                        pm.write_longlong(camera_subject_addr, target_humanoid)
                    
                except:
                    pass
                
                sleep(0.1)
            else:
                sleep(0.2)
        except:
            sleep(0.2)

def stop_spectate():
    global spectate_mode_enabled, spectate_target_addr, original_camera_subject
    try:
        if spectate_mode_enabled and original_camera_subject:
            camera_subject_addr = camAddr + int(offsets['CameraSubject'], 16)
            pm.write_longlong(camera_subject_addr, original_camera_subject)
            print("Stopped spectating - camera restored to you")
        
        spectate_mode_enabled = False
        spectate_target_addr = None
        original_camera_subject = None
        
    except Exception as e:
        print(f"Error stopping spectate: {e}")
        spectate_mode_enabled = False
        spectate_target_addr = None
        original_camera_subject = None

def teleport_to_player():
    try:
        if not injected or not lpAddr:
            print("Not injected!")
            return
        
        selected_name = dpg.get_value("player_spectate_combo")
        if not selected_name or selected_name == "No players found" or selected_name == "Loading players...":
            print("No player selected!")
            return
        
        target_player_addr = None
        for name, addr in player_list_for_spectate:
            if name == selected_name:
                target_player_addr = addr
                break
        
        if not target_player_addr:
            print(f"Player {selected_name} not found!")
            return
        
        target_char = pm.read_longlong(target_player_addr + int(offsets['ModelInstance'], 16))
        if not target_char:
            print("Target character not found!")
            return
        
        target_hrp = FindFirstChild(target_char, 'HumanoidRootPart')
        if not target_hrp:
            print("Target HRP not found!")
            return
        
        target_prim = pm.read_longlong(target_hrp + int(offsets['Primitive'], 16))
        if not target_prim:
            print("Target primitive not found!")
            return
            
        target_pos_addr = target_prim + int(offsets['Position'], 16)
        
        char = pm.read_longlong(lpAddr + int(offsets['ModelInstance'], 16))
        if not char:
            print("Your character not found!")
            return
            
        hrp = FindFirstChild(char, 'HumanoidRootPart')
        if not hrp:
            print("Your HRP not found!")
            return
            
        primitive = pm.read_longlong(hrp + int(offsets['Primitive'], 16))
        if not primitive:
            print("Your primitive not found!")
            return
            
        pos_addr = primitive + int(offsets['Position'], 16)
        
        try:
            for i in range(100):
                target_x = pm.read_float(target_pos_addr)
                target_y = pm.read_float(target_pos_addr + 4)
                target_z = pm.read_float(target_pos_addr + 8)
                
                if abs(target_x) < 100000 and abs(target_y) < 100000 and abs(target_z) < 100000:
                    pm.write_float(pos_addr, float(target_x))
                    pm.write_float(pos_addr + 4, float(target_y) + 3.0)
                    pm.write_float(pos_addr + 8, float(target_z))
                
                sleep(0.001)
            
            print(f"Teleported to {selected_name}")
        except Exception as e:
            print(f"Teleport failed: {e}")
                
    except Exception as e:
        print(f"Error teleporting to player: {e}")

# MOVEMENT LOOPS
def walkspeed_loop():
    while True:
        try:
            if injected and lpAddr > 0 and walkspeed_enabled:
                try:
                    char = pm.read_longlong(lpAddr + int(offsets['ModelInstance'], 16))
                    if char:
                        hrp = FindFirstChild(char, 'HumanoidRootPart')
                        if hrp:
                            hum = FindFirstChildOfClass(char, 'Humanoid')
                            if hum:
                                move_dir_offset = int(offsets['MoveDirection'], 16)
                                try:
                                    move_x = pm.read_float(hum + move_dir_offset)
                                    move_y = pm.read_float(hum + move_dir_offset + 4)
                                    move_z = pm.read_float(hum + move_dir_offset + 8)
                                    
                                    is_moving = abs(move_x) > 0.01 or abs(move_z) > 0.01
                                    
                                    if is_moving:
                                        primitive = pm.read_longlong(hrp + int(offsets['Primitive'], 16))
                                        if primitive:
                                            pos_offset = int(offsets['Position'], 16)
                                            current_x = pm.read_float(primitive + pos_offset)
                                            current_y = pm.read_float(primitive + pos_offset + 4)
                                            current_z = pm.read_float(primitive + pos_offset + 8)
                                            
                                            speed_multiplier = (walkspeed_value / 16.0) * 0.15
                                            
                                            new_x = current_x + (move_x * speed_multiplier)
                                            new_y = current_y + (move_y * speed_multiplier)
                                            new_z = current_z + (move_z * speed_multiplier)
                                            
                                            displacement = ((new_x - current_x)**2 + (new_z - current_z)**2)**0.5
                                            if displacement < 5.0:
                                                pm.write_float(primitive + pos_offset, new_x)
                                                pm.write_float(primitive + pos_offset + 4, new_y)
                                                pm.write_float(primitive + pos_offset + 8, new_z)
                                except:
                                    pass
                except:
                    pass
            sleep(0.005)
        except:
            sleep(0.005)
            continue

def jumppower_loop():
    last_write_time = 0
    write_interval = 0.5
    
    while True:
        try:
            current_time = time()
            if injected and lpAddr > 0 and jumppower_enabled:
                if current_time - last_write_time >= write_interval:
                    try:
                        char = pm.read_longlong(lpAddr + int(offsets['ModelInstance'], 16))
                        if char:
                            hum = FindFirstChildOfClass(char, 'Humanoid')
                            if hum:
                                try:
                                    jumppower_addr = hum + int(offsets['JumpPower'], 16)
                                    current_val = pm.read_float(jumppower_addr)
                                    
                                    if current_val != jumppower_value and 1.0 <= current_val <= 1000.0:
                                        pm.write_float(jumppower_addr, jumppower_value)
                                        last_write_time = current_time
                                except:
                                    pass
                    except:
                        pass
            sleep(0.1)
        except:
            sleep(0.1)
            continue

def infinite_jump_loop():
    while True:
        try:
            if injected and lpAddr > 0 and infinite_jump_enabled:
                space_pressed = windll.user32.GetAsyncKeyState(0x20) & 0x8000 != 0
                
                if space_pressed:
                    try:
                        char = pm.read_longlong(lpAddr + int(offsets['ModelInstance'], 16))
                        if char:
                            hrp = FindFirstChild(char, 'HumanoidRootPart')
                            if hrp:
                                primitive = pm.read_longlong(hrp + int(offsets['Primitive'], 16))
                                velocity_addr = primitive + int(offsets['Velocity'], 16)
                                
                                pm.write_float(velocity_addr + 4, 50.0)
                    except:
                        pass
                
            sleep(0.005)
        except:
            sleep(0.005)
            continue

def ctrl_click_teleport_loop():
    left_click_last = False
    
    while True:
        try:
            if injected and lpAddr > 0 and ctrl_click_teleport_enabled:
                ctrl_pressed = (windll.user32.GetAsyncKeyState(0x11) & 0x8000) != 0
                left_click_now = (windll.user32.GetAsyncKeyState(0x01) & 0x8000) != 0
                
                if ctrl_pressed and left_click_now and not left_click_last:
                    try:
                        if camAddr == 0 or camCFrameRotAddr == 0 or camPosAddr == 0:
                            left_click_last = left_click_now
                            continue
                        
                        hwnd_roblox = find_window_by_title("Roblox")
                        if not hwnd_roblox:
                            left_click_last = left_click_now
                            continue
                        
                        class POINT(ctypes.Structure):
                            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
                        
                        cursor_pos = POINT()
                        windll.user32.GetCursorPos(ctypes.byref(cursor_pos))
                        
                        left, top, right, bottom = get_client_rect_on_screen(hwnd_roblox)
                        width = right - left
                        height = bottom - top
                        
                        mouse_x = cursor_pos.x - left
                        mouse_y = cursor_pos.y - top
                        
                        ndc_x = (2.0 * mouse_x / width) - 1.0
                        ndc_y = 1.0 - (2.0 * mouse_y / height)
                        
                        cam_x = pm.read_float(camPosAddr)
                        cam_y = pm.read_float(camPosAddr + 4)
                        cam_z = pm.read_float(camPosAddr + 8)
                        
                        cam_matrix = []
                        for i in range(9):
                            cam_matrix.append(pm.read_float(camCFrameRotAddr + i * 4))
                        
                        right_x, right_y, right_z = cam_matrix[0], cam_matrix[1], cam_matrix[2]
                        up_x, up_y, up_z = cam_matrix[3], cam_matrix[4], cam_matrix[5]
                        forward_x, forward_y, forward_z = -cam_matrix[6], -cam_matrix[7], -cam_matrix[8]
                        
                        ray_dir_x = forward_x + ndc_x * right_x + ndc_y * up_x
                        ray_dir_y = forward_y + ndc_x * right_y + ndc_y * up_y
                        ray_dir_z = forward_z + ndc_x * right_z + ndc_y * up_z
                        
                        ray_length = (ray_dir_x**2 + ray_dir_y**2 + ray_dir_z**2)**0.5
                        ray_dir_x /= ray_length
                        ray_dir_y /= ray_length
                        ray_dir_z /= ray_length
                        
                        teleport_distance = 100.0
                        
                        teleport_x = cam_x + ray_dir_x * teleport_distance
                        teleport_y = cam_y + ray_dir_y * teleport_distance
                        teleport_z = cam_z + ray_dir_z * teleport_distance
                        
                        char = pm.read_longlong(lpAddr + int(offsets['ModelInstance'], 16))
                        if not char:
                            left_click_last = left_click_now
                            continue
                        
                        hrp = FindFirstChild(char, 'HumanoidRootPart')
                        if not hrp:
                            left_click_last = left_click_now
                            continue
                        
                        primitive = pm.read_longlong(hrp + int(offsets['Primitive'], 16))
                        if not primitive:
                            left_click_last = left_click_now
                            continue
                        
                        pos_addr = primitive + int(offsets['Position'], 16)
                        
                        for i in range(100):
                            pm.write_float(pos_addr, teleport_x)
                            pm.write_float(pos_addr + 4, teleport_y)
                            pm.write_float(pos_addr + 8, teleport_z)
                            sleep(0.001)
                        
                        print(f"Teleported to cursor position!")
                        
                    except Exception as e:
                        print(f"Teleport error: {e}")
                
                left_click_last = left_click_now
            else:
                left_click_last = False
            sleep(0.01)
        except Exception as e:
            sleep(0.01)

def triggerbot_loop():
    """Triggerbot implementation"""
    global triggerbot_toggled
    last_shot_time = 0
    key_pressed_last = False
    
    while True:
        try:
            if not injected or lpAddr == 0:
                sleep(0.05)
                continue
            
            if not triggerbot_enabled:
                sleep(0.05)
                continue
            
            key_pressed_now = (windll.user32.GetAsyncKeyState(triggerbot_keybind) & 0x8000) != 0
            
            if triggerbot_mode == "Toggle":
                if key_pressed_now and not key_pressed_last:
                    triggerbot_toggled = not triggerbot_toggled
                key_pressed_last = key_pressed_now
                should_shoot = triggerbot_toggled
            else:
                should_shoot = key_pressed_now
            
            if not should_shoot:
                sleep(0.01)
                continue
            
            current_time = time()
            if current_time - last_shot_time < triggerbot_delay:
                sleep(0.001)
                continue
            
            if camAddr == 0 or camCFrameRotAddr == 0 or camPosAddr == 0:
                sleep(0.01)
                continue
            
            try:
                cam_x = pm.read_float(camPosAddr)
                cam_y = pm.read_float(camPosAddr + 4)
                cam_z = pm.read_float(camPosAddr + 8)
                
                rot_x = pm.read_float(camCFrameRotAddr)
                rot_y = pm.read_float(camCFrameRotAddr + 4)
                
                from math import sin, cos, sqrt
                look_x = sin(rot_y) * cos(rot_x)
                look_y = -sin(rot_x)
                look_z = cos(rot_y) * cos(rot_x)
                
                local_team = ""
                if triggerbot_ignore_team:
                    try:
                        team_ptr = pm.read_longlong(lpAddr + int(offsets['Team'], 16))
                        if team_ptr:
                            local_team = ReadRobloxString(team_ptr + int(offsets['Name'], 16))
                    except:
                        pass
                
                target_found = False
                
                if plrsAddr:
                    children_start = pm.read_longlong(plrsAddr + int(offsets['Children'], 16))
                    if children_start:
                        children_end = pm.read_longlong(children_start + int(offsets['ChildrenEnd'], 16))
                        current = children_start
                        
                        while current != children_end and not target_found:
                            try:
                                player = pm.read_longlong(current)
                                
                                if player and player != lpAddr:
                                    if triggerbot_ignore_team and local_team:
                                        try:
                                            player_team_ptr = pm.read_longlong(player + int(offsets['Team'], 16))
                                            if player_team_ptr:
                                                player_team = ReadRobloxString(player_team_ptr + int(offsets['Name'], 16))
                                                if player_team == local_team:
                                                    current += 8
                                                    continue
                                        except:
                                            pass
                                    
                                    player_name = ReadRobloxString(player + int(offsets['Name'], 16))
                                    if player_name:
                                        char = FindFirstChild(player, player_name)
                                        if char:
                                            if triggerbot_ignore_dead:
                                                try:
                                                    hum = FindFirstChildOfClass(char, 'Humanoid')
                                                    if hum:
                                                        health = pm.read_float(hum + int(offsets['Health'], 16))
                                                        if health <= 0:
                                                            current += 8
                                                            continue
                                                except:
                                                    pass
                                            
                                            body_parts = [
                                                'Head', 'Torso', 'UpperTorso', 'LowerTorso',
                                                'LeftUpperArm', 'RightUpperArm', 
                                                'LeftLowerArm', 'RightLowerArm',
                                                'LeftUpperLeg', 'RightUpperLeg',
                                                'LeftLowerLeg', 'RightLowerLeg',
                                                'LeftHand', 'RightHand',
                                                'LeftFoot', 'RightFoot'
                                            ]
                                            
                                            for part_name in body_parts:
                                                try:
                                                    part = FindFirstChild(char, part_name)
                                                    if part:
                                                        primitive = pm.read_longlong(part + int(offsets['Primitive'], 16))
                                                        if primitive:
                                                            px = pm.read_float(primitive + int(offsets['Position'], 16))
                                                            py = pm.read_float(primitive + int(offsets['Position'], 16) + 4)
                                                            pz = pm.read_float(primitive + int(offsets['Position'], 16) + 8)
                                                            
                                                            dx = px - cam_x
                                                            dy = py - cam_y
                                                            dz = pz - cam_z
                                                            
                                                            dist = sqrt(dx*dx + dy*dy + dz*dz)
                                                            
                                                            if dist < 1:
                                                                continue
                                                            
                                                            dx /= dist
                                                            dy /= dist
                                                            dz /= dist
                                                            
                                                            dot = look_x * dx + look_y * dy + look_z * dz
                                                            
                                                            if dot > 0.9994:
                                                                if triggerbot_visibility_check:
                                                                    if dist > 500:
                                                                        continue
                                                                
                                                                target_found = True
                                                                break
                                                except:
                                                    continue
                                            
                                            if target_found:
                                                break
                                
                                current += 8
                            except:
                                current += 8
                                continue
                
                if target_found:
                    try:
                        windll.user32.mouse_event(2, 0, 0, 0, 0)
                        sleep(0.05)
                        windll.user32.mouse_event(4, 0, 0, 0, 0)
                        last_shot_time = current_time
                    except:
                        pass
                
                sleep(0.001)
            
            except Exception as e:
                sleep(0.01)
        
        except Exception as e:
            sleep(0.01)

# Start all threads
Thread(target=walkspeed_loop, daemon=True).start()
Thread(target=jumppower_loop, daemon=True).start()
Thread(target=infinite_jump_loop, daemon=True).start()
Thread(target=ctrl_click_teleport_loop, daemon=True).start()
Thread(target=spectate_loop, daemon=True).start()
Thread(target=triggerbot_loop, daemon=True).start()

def auto_inject_startup():
    sleep(2)
    if auto_inject:
        init()

Thread(target=auto_inject_startup, daemon=True).start()

print("✅ All systems loaded and threads started!")
print("✅ Script is ready to use!")
# ============================================================================
# UI SECTION - Add this after APPEND_TO_MAIN.py
# Complete DearPyGUI interface setup
# ============================================================================

dpg.create_context()

# Theme setup
with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (5, 5, 8, 200))
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (8, 8, 12, 180))
        dpg.add_theme_color(dpg.mvThemeCol_Border, (120, 80, 255, 180))
        
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (15, 15, 20, 140))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (25, 25, 35, 180))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (35, 35, 50, 200))
        
        dpg.add_theme_color(dpg.mvThemeCol_Button, (100, 60, 255, 180))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (130, 90, 255, 220))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (80, 40, 235, 240))
        
        dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (180, 140, 255))
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (150, 100, 255, 240))
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (200, 160, 255, 255))
        
        dpg.add_theme_color(dpg.mvThemeCol_Header, (80, 50, 200, 100))
        dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (100, 70, 220, 140))
        dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (120, 90, 240, 180))
        
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (10, 10, 15, 200))
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (15, 15, 25, 230))
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgCollapsed, (8, 8, 12, 180))
        
        dpg.add_theme_color(dpg.mvThemeCol_Separator, (140, 100, 255, 200))
        dpg.add_theme_color(dpg.mvThemeCol_Text, (240, 240, 250))
        
        dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (10, 10, 15, 220))
        
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (10, 10, 15, 100))
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (100, 60, 255, 180))
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (130, 90, 255, 220))
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, (160, 120, 255, 255))
        
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 4)
        dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 3)
        dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 3)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 3)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 4, 2)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 8, 8)
        dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 1)
        dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize, 10)
        dpg.add_theme_style(dpg.mvStyleVar_IndentSpacing, 12)

dpg.bind_theme(global_theme)

# Main Window
with dpg.window(label="AckWare", tag="Primary Window", no_scrollbar=False, 
                no_title_bar=True, no_move=False, no_resize=False, pos=[50, 50], 
                on_close=lambda: None):
    
    dpg.add_text("AckWare - the best 2 do it.", color=(180, 140, 255))
    dpg.add_text("Press INSERT to minimize", color=(120, 120, 140))
    dpg.add_separator()
    dpg.add_spacer(height=3)
    
    with dpg.group(tag="injector_group", horizontal=False):
        with dpg.child_window(height=140, border=True):
            dpg.add_text("INJECTION", color=(255, 200, 100))
            dpg.add_separator()
            dpg.add_spacer(height=3)
            
            dpg.add_checkbox(label="Auto-Inject", default_value=auto_inject, 
                           callback=auto_inject_callback, tag="auto_inject_checkbox")
            dpg.add_spacer(height=3)
            dpg.add_button(label="INJECT NOW", callback=inject_callback, 
                          width=-1, height=30)
    
    with dpg.group(tag="main_features_group", show=False):
        dpg.add_spacer(height=3)
        
        with dpg.child_window(height=350, border=True):
            dpg.add_text("COMBAT", color=(255, 100, 100))
            dpg.add_separator()
            dpg.add_spacer(height=3)
            
            with dpg.child_window(height=70, border=True):
                with dpg.group(horizontal=True):
                    dpg.add_checkbox(label="Aimbot", default_value=aimbot_enabled, 
                                   callback=aimbot_callback, tag="aimbot_checkbox")
                dpg.add_spacer(height=3)
                dpg.add_button(label="Settings", 
                              callback=toggle_aimbot_panel, width=-1, height=24)
            
            dpg.add_spacer(height=3)
            
            with dpg.child_window(height=70, border=True):
                with dpg.group(horizontal=True):
                    dpg.add_checkbox(label="Triggerbot", default_value=triggerbot_enabled, 
                                   callback=triggerbot_callback, tag="triggerbot_checkbox")
                dpg.add_spacer(height=3)
                dpg.add_button(label="Settings", 
                              callback=lambda: toggle_misc_panel(), width=-1, height=24)
            
            dpg.add_spacer(height=3)
            
            with dpg.child_window(height=70, border=True):
                with dpg.group(horizontal=True):
                    dpg.add_checkbox(label="ESP", default_value=esp_enabled, 
                                   callback=esp_callback, tag="esp_checkbox")
                dpg.add_spacer(height=3)
                dpg.add_button(label="Settings", 
                              callback=toggle_esp_panel, width=-1, height=24)
            
            dpg.add_spacer(height=3)
            
            with dpg.group(horizontal=True):
                dpg.add_text("Status: ", color=(150, 150, 170))
                dpg.add_text("ACTIVE", color=(100, 255, 100))
        
        dpg.add_spacer(height=3)
        
        with dpg.child_window(height=75, border=True):
            dpg.add_text("MOVEMENT", color=(100, 200, 255))
            dpg.add_separator()
            dpg.add_spacer(height=3)
            dpg.add_button(label="Settings Panel", 
                          callback=toggle_movement_panel, width=-1, height=24)
        
        dpg.add_spacer(height=3)
        
        with dpg.child_window(height=100, border=True):
            dpg.add_text("CONFIG", color=(255, 200, 100))
            dpg.add_separator()
            dpg.add_spacer(height=3)
            
            with dpg.group(horizontal=True):
                dpg.add_button(label="SAVE CONFIG", callback=lambda: save_config(), 
                              width=185, height=30)
                dpg.add_button(label="LOAD CONFIG", callback=lambda: load_config(), 
                              width=185, height=30)

# Aimbot Panel
with dpg.window(label="AIMBOT", tag="aimbot_panel", width=600, height=700, 
                show=False, no_close=True, pos=[400, 80], no_scrollbar=False, 
                no_title_bar=True, on_close=lambda: None):
    
    dpg.add_text("AIMBOT CONFIG", color=(255, 100, 100))
    dpg.add_separator()
    dpg.add_spacer(height=3)
    
    with dpg.child_window(height=-35, border=False):
        
        with dpg.child_window(height=100, border=True):
            dpg.add_text("Controls", color=(255, 200, 100))
            dpg.add_separator()
            dpg.add_spacer(height=2)
            
            dpg.add_button(label=f"Keybind: {get_key_name(aimbot_keybind)}", 
                          tag="keybind_button", callback=keybind_callback, 
                          width=-1, height=26)
            dpg.add_spacer(height=2)
            dpg.add_text("Mode:", color=(200, 200, 200))
            dpg.add_combo(["Hold", "Toggle"], default_value=aimbot_mode, 
                         tag="aimbot_mode_combo", callback=aimbot_mode_callback, 
                         width=-1)
        
        dpg.add_spacer(height=3)
        
        with dpg.child_window(height=90, border=True):
            dpg.add_text("Target", color=(255, 100, 100))
            dpg.add_separator()
            dpg.add_spacer(height=2)
            
            dpg.add_text("Body Part:", color=(200, 200, 200))
            dpg.add_combo(["Head", "HumanoidRootPart", "UpperTorso", "LowerTorso"], 
                         default_value=aimbot_bodypart, 
                         tag="bodypart_combo", callback=bodypart_callback, 
                         width=-1)
        
        dpg.add_spacer(height=3)
        
        with dpg.child_window(height=160, border=True):
            dpg.add_text("Filters", color=(100, 200, 255))
            dpg.add_separator()
            dpg.add_spacer(height=2)
            
            dpg.add_checkbox(label="Ignore Team", default_value=aimbot_ignoreteam, 
                            callback=aimbot_ignoreteam_callback, tag="aimbot_ignoreteam_cb")
            dpg.add_checkbox(label="Ignore Dead", default_value=aimbot_ignoredead, 
                            callback=aimbot_ignoredead_callback, tag="aimbot_ignoredead_cb")
            dpg.add_checkbox(label="Unlock on Death", default_value=aimbot_unlock_on_death, 
                            callback=aimbot_unlock_on_death_callback, tag="aimbot_unlock_on_death_cb")
            dpg.add_checkbox(label="Visibility Check", default_value=aimbot_visibility_check, 
                            callback=aimbot_visibility_callback, tag="aimbot_visibility_cb")
            dpg.add_checkbox(label="Distance Check", default_value=aimbot_distance_check, 
                            callback=aimbot_distance_callback, tag="aimbot_distance_cb")
            dpg.add_spacer(height=2)
            dpg.add_text("Max Distance (studs):", color=(200, 200, 200))
            dpg.add_slider_float(default_value=aimbot_max_distance, 
                                min_value=50.0, max_value=1000.0, 
                                callback=aimbot_distance_slider_callback, width=-1, 
                                tag="aimbot_distance_slider", format="%.0f")
        
        dpg.add_spacer(height=3)
        
        with dpg.child_window(height=110, border=True):
            dpg.add_text("Sticky Aim", color=(255, 150, 255))
            dpg.add_separator()
            dpg.add_spacer(height=2)
            
            dpg.add_checkbox(label="Enable", default_value=sticky_aim_enabled, callback=sticky_aim_callback, tag="sticky_aim_cb")
            dpg.add_spacer(height=2)
            dpg.add_text("FOV Range:", color=(200, 200, 200))
            dpg.add_slider_float(default_value=sticky_aim_fov, 
                                min_value=50.0, max_value=400.0, 
                                callback=sticky_fov_slider_callback, width=-1, 
                                tag="sticky_fov_slider", format="%.0f px")
        
        dpg.add_spacer(height=3)
        
        # NEW: Silent Aim Section (Hitbox Expander)
        with dpg.child_window(height=230, border=True):
            dpg.add_text("Silent Aim (Hitbox Expander)", color=(255, 100, 100))
            dpg.add_separator()
            dpg.add_spacer(height=2)

            dpg.add_checkbox(label="Enable Silent Aim (Expand Enemy Hitboxes)",
                            default_value=silent_aim_enabled,
                            callback=silent_aim_callback,
                            tag="silent_aim_cb")
            dpg.add_text("Makes enemies easier to hit by expanding their hitboxes", color=(150, 150, 160))
            dpg.add_spacer(height=2)

            dpg.add_text("Hitbox Size X:", color=(200, 200, 200))
            dpg.add_slider_float(default_value=hitbox_size_x,
                                min_value=2.0, max_value=50.0,
                                callback=hitbox_size_x_callback,
                                width=-1,
                                tag="hitbox_size_x_slider",
                                format="%.1f")

            dpg.add_text("Hitbox Size Y:", color=(200, 200, 200))
            dpg.add_slider_float(default_value=hitbox_size_y,
                                min_value=2.0, max_value=50.0,
                                callback=hitbox_size_y_callback,
                                width=-1,
                                tag="hitbox_size_y_slider",
                                format="%.1f")

            dpg.add_text("Hitbox Size Z:", color=(200, 200, 200))
            dpg.add_slider_float(default_value=hitbox_size_z,
                                min_value=2.0, max_value=50.0,
                                callback=hitbox_size_z_callback,
                                width=-1,
                                tag="hitbox_size_z_slider",
                                format="%.1f")

            dpg.add_text("Transparency (0=invisible, 1=visible):", color=(200, 200, 200))
            dpg.add_slider_float(default_value=hitbox_transparency,
                                min_value=0.0, max_value=1.0,
                                callback=hitbox_transparency_callback,
                                width=-1,
                                tag="hitbox_transparency_slider",
                                format="%.2f")
        
        dpg.add_spacer(height=3)
        
        # NEW: FOV Circle Options
        with dpg.child_window(height=130, border=True):
            dpg.add_text("FOV Circle Options", color=(100, 255, 255))
            dpg.add_separator()
            dpg.add_spacer(height=2)
            
            dpg.add_checkbox(label="Show FOV Circle", default_value=show_fov_circle, 
                            callback=fov_circle_callback)
            dpg.add_checkbox(label="FOV Circle Follows Mouse (Instead of Center)", 
                            default_value=fov_follow_mouse, 
                            callback=fov_follow_mouse_callback, 
                            tag="fov_follow_mouse_cb")
            dpg.add_spacer(height=2)
            dpg.add_text("Circle Color:", color=(200, 200, 200))
            dpg.add_color_edit(default_value=(1.0, 1.0, 1.0, 1.0),
                              callback=fov_circle_color_callback, no_alpha=True, 
                              input_mode=dpg.mvColorEdit_input_rgb, width=150)
        
        dpg.add_spacer(height=3)
        
        with dpg.child_window(height=110, border=True):
            dpg.add_text("Smoothing", color=(200, 200, 100))
            dpg.add_separator()
            dpg.add_spacer(height=2)
            
            dpg.add_checkbox(label="Enable", default_value=aimbot_smoothing_enabled, callback=aimbot_smoothing_callback, tag="aimbot_smoothing_cb")
            dpg.add_spacer(height=2)
            dpg.add_text("Smooth Factor:", color=(200, 200, 200))
            dpg.add_slider_float(default_value=aimbot_smoothing, 
                                min_value=1.0, max_value=20.0, 
                                callback=aimbot_smoothing_slider_callback, width=-1, 
                                tag="aimbot_smoothing_slider", format="%.1f")
        
        dpg.add_spacer(height=3)
        
        with dpg.child_window(height=125, border=True):
            dpg.add_text("Prediction", color=(100, 255, 200))
            dpg.add_separator()
            dpg.add_spacer(height=2)
            
            dpg.add_text("Horizontal:", color=(200, 200, 200))
            dpg.add_slider_float(default_value=prediction_x, 
                                min_value=0.0, max_value=1.0, 
                                callback=prediction_x_slider_callback, width=-1, 
                                tag="prediction_x_slider", format="%.2f")
            dpg.add_spacer(height=2)
            dpg.add_text("Vertical:", color=(200, 200, 200))
            dpg.add_slider_float(default_value=prediction_y, 
                                min_value=0.0, max_value=1.0, 
                                callback=prediction_y_slider_callback, width=-1, 
                                tag="prediction_y_slider", format="%.2f")
    
    dpg.add_spacer(height=3)
    dpg.add_button(label="CLOSE", callback=lambda: dpg.hide_item("aimbot_panel"), 
                  width=-1, height=28)

# ESP Panel  
with dpg.window(label="ESP", tag="esp_panel", width=380, height=630, 
                show=False, no_close=True, pos=[820, 50], no_title_bar=True,
                on_close=lambda: None):
    
    dpg.add_text("ESP CONFIG", color=(100, 255, 150))
    dpg.add_separator()
    dpg.add_spacer(height=3)
    
    with dpg.child_window(height=-35, border=False):
        
        with dpg.child_window(height=80, border=True):
            dpg.add_text("Filters", color=(100, 200, 255))
            dpg.add_separator()
            dpg.add_spacer(height=2)
            
            dpg.add_checkbox(label="Ignore Team", default_value=esp_ignoreteam, callback=esp_ignoreteam_callback, tag="esp_ignoreteam_cb")
            dpg.add_checkbox(label="Ignore Dead", default_value=esp_ignoredead, callback=esp_ignoredead_callback, tag="esp_ignoredead_cb")
        
        dpg.add_spacer(height=3)
        
        with dpg.child_window(height=185, border=True):
            dpg.add_text("Visuals", color=(255, 150, 255))
            dpg.add_separator()
            dpg.add_spacer(height=2)
            
            dpg.add_checkbox(label="Boxes", default_value=esp_boxes, callback=esp_boxes_callback, tag="esp_boxes_cb")
            dpg.add_checkbox(label="Names", default_value=esp_names, callback=esp_names_callback, tag="esp_names_cb")
            dpg.add_checkbox(label="Distance", default_value=esp_distance, callback=esp_distance_callback, tag="esp_distance_cb")
            dpg.add_checkbox(label="Skeletons", default_value=esp_skeletons, callback=esp_skeletons_callback, tag="esp_skeletons_cb")
            dpg.add_checkbox(label="Health Bars", default_value=esp_healthbar, callback=esp_healthbar_callback, tag="esp_healthbar_cb")
            dpg.add_checkbox(label="Tracers", default_value=esp_tracers, callback=esp_tracers_callback, tag="esp_tracers_cb")
            dpg.add_checkbox(label="Chams (Wallhack)", default_value=esp_chams_enabled, 
                            callback=esp_chams_callback)
        
        dpg.add_spacer(height=3)
        
        with dpg.child_window(height=280, border=True):
            dpg.add_text("Colors", color=(255, 200, 100))
            dpg.add_separator()
            dpg.add_spacer(height=2)
            
            dpg.add_text("Box Color:", color=(200, 200, 200))
            dpg.add_color_edit(default_value=(1.0, 1.0, 1.0, 1.0),
                              callback=esp_box_color_callback, no_alpha=True, 
                              input_mode=dpg.mvColorEdit_input_rgb, width=150)
            dpg.add_spacer(height=2)
            dpg.add_text("Name Color:", color=(200, 200, 200))
            dpg.add_color_edit(default_value=(1.0, 1.0, 1.0, 1.0),
                              callback=esp_name_color_callback, no_alpha=True, 
                              input_mode=dpg.mvColorEdit_input_rgb, width=150)
            dpg.add_spacer(height=2)
            dpg.add_text("Tracer Color:", color=(200, 200, 200))
            dpg.add_color_edit(default_value=(1.0, 1.0, 1.0, 1.0),
                              callback=esp_tracer_color_callback, no_alpha=True, 
                              input_mode=dpg.mvColorEdit_input_rgb, width=150)
            dpg.add_spacer(height=2)
            dpg.add_text("Healthbar Color:", color=(200, 200, 200))
            dpg.add_color_edit(default_value=(0.0, 1.0, 0.0, 1.0),
                              callback=esp_healthbar_color_callback, no_alpha=True, 
                              input_mode=dpg.mvColorEdit_input_rgb, width=150)
            dpg.add_spacer(height=2)
            dpg.add_text("Chams Color:", color=(200, 200, 200))
            dpg.add_color_edit(default_value=(1.0, 0.39, 1.0, 1.0),
                              callback=esp_chams_color_callback, no_alpha=True, 
                              input_mode=dpg.mvColorEdit_input_rgb, width=150)
    
    dpg.add_spacer(height=3)
    dpg.add_button(label="CLOSE", callback=lambda: dpg.hide_item("esp_panel"), 
                  width=-1, height=28)

# Misc Panel (Triggerbot + Character FOV)
with dpg.window(label="MISC", tag="misc_panel", width=380, height=510, 
                show=False, no_close=True, pos=[1210, 50], no_title_bar=True,
                on_close=lambda: None):
    
    dpg.add_text("COMBAT SETTINGS", color=(255, 200, 100))
    dpg.add_separator()
    dpg.add_spacer(height=3)
    
    with dpg.child_window(height=-35, border=False):
        
        with dpg.child_window(height=350, border=True):
            dpg.add_text("Triggerbot", color=(255, 100, 150))
            dpg.add_separator()
            dpg.add_spacer(height=2)
            
            dpg.add_checkbox(label="Enable", default_value=triggerbot_enabled, 
                            callback=triggerbot_callback)
            dpg.add_spacer(height=2)
            
            dpg.add_button(label=f"Keybind: {get_key_name(triggerbot_keybind)}", 
                          tag="triggerbot_keybind_button", callback=triggerbot_keybind_callback, 
                          width=-1, height=26)
            dpg.add_spacer(height=2)
            
            dpg.add_text("Mode:", color=(200, 200, 200))
            dpg.add_combo(["Hold", "Toggle"], default_value=triggerbot_mode, 
                         tag="triggerbot_mode_combo", callback=triggerbot_mode_callback, 
                         width=-1)
            dpg.add_spacer(height=2)
            
            dpg.add_checkbox(label="Ignore Team", default_value=triggerbot_ignore_team, callback=triggerbot_ignore_team_callback, tag="triggerbot_ignoreteam_cb")
            dpg.add_checkbox(label="Ignore Dead", default_value=triggerbot_ignore_dead, callback=triggerbot_ignore_dead_callback, tag="triggerbot_ignoredead_cb")
            dpg.add_checkbox(label="Visibility Check", default_value=triggerbot_visibility_check, callback=triggerbot_visibility_callback, tag="triggerbot_visibility_cb")
            dpg.add_spacer(height=2)
            
            dpg.add_text("Delay (seconds):", color=(200, 200, 200))
            dpg.add_slider_float(default_value=triggerbot_delay, 
                                min_value=0.0, max_value=0.5, 
                                callback=triggerbot_delay_callback, width=-1, 
                                tag="triggerbot_delay_slider", format="%.2f")
        
        dpg.add_spacer(height=3)
        
        with dpg.child_window(height=85, border=True):
            dpg.add_text("Character FOV", color=(150, 200, 255))
            dpg.add_separator()
            dpg.add_spacer(height=2)
            
            dpg.add_text("FOV (Field of View):", color=(200, 200, 200))
            dpg.add_slider_float(default_value=character_fov, 
                                min_value=30.0, max_value=120.0, 
                                callback=character_fov_callback, width=-1, 
                                tag="character_fov_slider", format="%.0f")
    
    dpg.add_spacer(height=3)
    dpg.add_button(label="CLOSE", callback=lambda: dpg.hide_item("misc_panel"), 
                  width=-1, height=28)

# Movement Panel
with dpg.window(label="MOVEMENT", tag="movement_panel", width=380, height=750, 
                show=False, no_close=True, pos=[1600, 50], no_title_bar=True,
                on_close=lambda: None):
    
    dpg.add_text("MOVEMENT SETTINGS", color=(100, 200, 255))
    dpg.add_separator()
    dpg.add_spacer(height=3)
    
    with dpg.child_window(height=-35, border=False):
        
        with dpg.child_window(height=100, border=True):
            dpg.add_text("WalkSpeed", color=(150, 255, 200))
            dpg.add_separator()
            dpg.add_spacer(height=2)
            
            dpg.add_checkbox(label="Enable WalkSpeed", default_value=walkspeed_enabled, 
                            callback=walkspeed_callback, tag="walkspeed_checkbox")
            dpg.add_spacer(height=2)
            
            dpg.add_text("Speed Value:", color=(200, 200, 200))
            dpg.add_slider_float(default_value=walkspeed_value, 
                                min_value=16.0, max_value=200.0, 
                                callback=walkspeed_slider_callback, width=-1, 
                                tag="walkspeed_slider", format="%.0f")
        
        dpg.add_spacer(height=3)
        
        with dpg.child_window(height=100, border=True):
            dpg.add_text("JumpPower", color=(255, 220, 150))
            dpg.add_separator()
            dpg.add_spacer(height=2)
            
            dpg.add_checkbox(label="Enable JumpPower", default_value=jumppower_enabled, 
                            callback=jumppower_callback, tag="jumppower_checkbox")
            dpg.add_spacer(height=2)
            
            dpg.add_text("Jump Value:", color=(200, 200, 200))
            dpg.add_slider_float(default_value=jumppower_value, 
                                min_value=50.0, max_value=500.0, 
                                callback=jumppower_slider_callback, width=-1, 
                                tag="jumppower_slider", format="%.0f")
        
        dpg.add_spacer(height=3)
        
        with dpg.child_window(height=70, border=True):
            dpg.add_text("Infinite Jump", color=(255, 200, 150))
            dpg.add_separator()
            dpg.add_spacer(height=2)
            
            dpg.add_checkbox(label="Enable Infinite Jump (Hold Space to Fly)", default_value=infinite_jump_enabled, callback=infinite_jump_callback, tag="infinite_jump_cb")
        
        dpg.add_spacer(height=3)
        
        with dpg.child_window(height=70, border=True):
            dpg.add_text("Ctrl+Click Teleport", color=(200, 150, 255))
            dpg.add_separator()
            dpg.add_spacer(height=2)
            
            dpg.add_checkbox(label="Enable Ctrl+Click TP", default_value=ctrl_click_teleport_enabled, callback=ctrl_click_teleport_callback, tag="ctrl_click_tp_cb")
        
        dpg.add_spacer(height=3)
        
        with dpg.child_window(height=130, border=True):
            dpg.add_text("Spectate & Teleport", color=(255, 255, 150))
            dpg.add_separator()
            dpg.add_spacer(height=2)
            
            dpg.add_text("Select Player:", color=(200, 200, 200))
            dpg.add_combo(["Loading players..."], default_value="Loading players...", 
                         tag="player_spectate_combo", 
                         width=-1)
            dpg.add_spacer(height=3)
            
            with dpg.group(horizontal=True):
                dpg.add_button(label="SPECTATE", callback=lambda: spectate_player(), 
                              width=112, height=26)
                dpg.add_button(label="STOP", callback=lambda: stop_spectate(), 
                              width=112, height=26)
                dpg.add_button(label="TELEPORT", callback=lambda: teleport_to_player(), 
                              width=135, height=26)
    
    dpg.add_spacer(height=3)
    dpg.add_button(label="CLOSE", callback=lambda: dpg.hide_item("movement_panel"), 
                  width=-1, height=28)

dpg.create_viewport(title="ACKWARE", width=900, height=600, decorated=False, 
                    always_on_top=True, resizable=False)
dpg.setup_dearpygui()

def set_always_on_top():
    sleep(0.3)
    hwnd = ctypes.windll.user32.FindWindowW(None, "ACKWARE")
    if hwnd:
        HWND_TOPMOST = -1
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_SHOWWINDOW = 0x0040
        ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)

Thread(target=set_always_on_top, daemon=True).start()

dpg.set_primary_window("Primary Window", True)
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
esp.terminate()
