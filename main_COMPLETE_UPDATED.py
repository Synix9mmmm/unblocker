# COMPLETE UPDATED ACKWARE - WITH 3 AIMBOT TYPES, HIT SOUNDS, FIXED TRIGGERBOT
# Roblox Version: version-e380c8edc8f6477c
# Updated: 2025

import sys
import time
import subprocess
import threading
import base64
import os
import winsound  # NEW: For hit sounds

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
    try:
        encoded = base64.b64encode(f"{username}:{password}".encode()).decode()
        with open(REMEMBER_ME_FILE, 'w') as f:
            f.write(encoded)
    except Exception as e:
        print(f"Failed to save credentials: {e}")

def load_credentials():
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
                    if expiry == 0 or expiry > 1893456000:
                        return "Expires: Never (Lifetime)"
                    try:
                        dt = datetime.fromtimestamp(expiry)
                        if dt.year >= 2030:
                            return "Expires: Never (Lifetime)"
                        return f"Expires: {dt.strftime('%B %d, %Y at %I:%M %p')}"
                    except:
                        return "Expires: Never (Lifetime)"
                elif isinstance(expiry, str):
                    if any(word in expiry.lower() for word in ['lifetime', 'never', 'permanent']):
                        return "Expires: Never (Lifetime)"
                    return f"Expires: {expiry}"
                return f"Expires: {str(expiry)}"

        return "Expires: Active (No expiry data)"
    except Exception as e:
        return "Expires: Unknown"

def fire_auth_ui(hwid):
    global _auth_ok, _auth_userdata

    import dearpygui.dearpygui as dpg

    dpg.create_context()

    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (12, 12, 16, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (16, 16, 20, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Button, (90, 50, 180, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (110, 70, 200, 255))
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)

    dpg.bind_theme(global_theme)
    is_loading = [False]
    saved_user, saved_pass = load_credentials()

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

        remember_me = dpg.get_value("remember_me_checkbox")

        is_loading[0] = True
        dpg.configure_item("login_button", enabled=False, label="AUTHENTICATING...")
        update_status("Verifying...", (168, 85, 247))

        def login_thread():
            global _auth_ok, _auth_userdata
            try:
                time.sleep(0.5)
                try_login_with_hwid(username, password, hwid)

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
                update_status(f"Failed: {str(e)}", (239, 68, 68))
                dpg.configure_item("login_button", enabled=True, label="LOGIN")
                is_loading[0] = False

        threading.Thread(target=login_thread, daemon=True).start()

    with dpg.window(tag="auth_window", no_scrollbar=True, no_title_bar=True,
                    pos=[100, 100], width=450, height=560):
        dpg.add_text("ACKWARE", color=(200, 200, 210, 255))
        dpg.add_separator()

        with dpg.tab_bar():
            with dpg.tab(label="LOGIN"):
                dpg.add_text("Username", color=(150, 150, 160, 255))
                dpg.add_input_text(tag="login_username", width=-1, height=30,
                                  default_value=saved_user if saved_user else "")
                dpg.add_text("Password", color=(150, 150, 160, 255))
                dpg.add_input_text(tag="login_password", password=True, width=-1,
                                  height=30, default_value=saved_pass if saved_pass else "")
                dpg.add_checkbox(label="Remember Me", tag="remember_me_checkbox",
                                default_value=bool(saved_user and saved_pass))
                dpg.add_button(label="LOGIN", tag="login_button",
                              callback=do_login, width=-1, height=36)
                dpg.add_text("", tag="status_text", wrap=-1)

    dpg.create_viewport(title="AckWare", width=900, height=600, decorated=False)
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

    _hwid = get_windows_sid_hwid()
    print(f"[+] HWID: {_hwid}")

    fire_auth_ui(_hwid)

    if not _auth_ok:
        safe_exit("✕ Authentication cancelled.")

    print("\n✓ Authentication Successful!")
    print(f"User: {_auth_userdata.get('username', 'User')}")
    time.sleep(1)

authenticate()
print("[+] Loading main application...")

# ============================================================================
# MAIN APPLICATION CODE
# ============================================================================

from lib import *
from numpy import array, float32, linalg, cross, dot, reshape
from math import sqrt, pi, sin, cos, atan2
from ctypes import windll, byref, Structure, wintypes
from time import time, sleep
from threading import Thread
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

# ============================================================================
# GLOBALS - INCLUDING NEW FEATURES
# ============================================================================

# Core state
game_detected = False
auto_inject_attempted = False
console_output = []
injected = False
menu_visible = True
waiting_for_keybind = False
waiting_for_triggerbot_keybind = False

# Aimbot settings
aimbot_enabled = False
aimbot_keybind = 2
aimbot_mode = "Hold"
aimbot_toggled = False
aimbot_ignoreteam = False
aimbot_ignoredead = False
aimbot_unlock_on_death = True
aimbot_visibility_check = True
aimbot_distance_check = True
aimbot_max_distance = 500.0
aimbot_smoothing_enabled = False
aimbot_smoothing = 1.0
aimbot_bodypart = "Head"
prediction_x = 0.0
prediction_y = 0.0
sticky_aim_enabled = True
sticky_aim_fov = 200.0
show_fov_circle = True
fov_circle_color = [255, 255, 255]
fov_follow_mouse = False

# NEW: Aimbot Type Selection
aimbot_type = "Mouse"  # Options: "Mouse", "Camera", "Memory"

# NEW: Hit Sound System
hit_sound_enabled = True
hit_sound_volume = 50
last_hit_time = 0.0
hit_sound_cooldown = 0.1
target_health_tracker = {}

# ESP settings
esp_enabled = False
esp_ignoreteam = False
esp_ignoredead = False
esp_boxes = False
esp_names = False
esp_distance = False
esp_skeletons = False
esp_healthbar = False
esp_tracers = False
esp_chams_enabled = False
esp_box_color = [255, 255, 255]
esp_name_color = [255, 255, 255]
esp_tracer_color = [255, 255, 255]
esp_healthbar_color = [0, 255, 0]
esp_chams_color = [255, 100, 255]
character_fov = 70.0

# Triggerbot settings
triggerbot_enabled = False
triggerbot_keybind = 88
triggerbot_mode = "Hold"
triggerbot_toggled = False
triggerbot_ignore_team = True
triggerbot_ignore_dead = True
triggerbot_delay = 0.05
triggerbot_visibility_check = True

# Movement settings
walkspeed_enabled = False
walkspeed_value = 16.0
jumppower_enabled = False
jumppower_value = 50.0
infinite_jump_enabled = False
ctrl_click_teleport_enabled = False
auto_inject = False

# Target tracking
target_positions = {}
target_last_update = {}
target_velocities = {}
locked_target_id = 0
target = 0
target_id = 0
last_target_health = 100.0

# Memory addresses
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

# Spectate
spectate_mode_enabled = False
spectate_target_addr = None
original_camera_subject = None
player_list_for_spectate = []

# Mouse FOV tracking
mouse_fov_x = 0
mouse_fov_y = 0

# ============================================================================
# UPDATED OFFSETS - Roblox Version: version-e380c8edc8f6477c
# ============================================================================

print('Loading offsets...')
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
    'FakeDataModelPointer': '0x77A03A8',  # UPDATED
    'FakeDataModelToDataModel': '0x1C0',
    'VisualEnginePointer': '0x75278C0',    # UPDATED
    'viewmatrix': '0x4B0',
}

setOffsets(int(offsets['Name'], 16), int(offsets['Children'], 16))

# ============================================================================
# NEW: HIT SOUND SYSTEM
# ============================================================================

def play_hit_sound():
    """Play hit confirmation sound"""
    if not hit_sound_enabled:
        return

    try:
        # Windows beep (frequency, duration)
        frequency = int(800 * (hit_sound_volume / 100.0))
        winsound.Beep(frequency, 50)
    except:
        pass

def check_hit_detection(target_id, current_health):
    """Check if we hit the target and play sound"""
    global target_health_tracker, last_hit_time

    if not hit_sound_enabled or target_id == 0:
        return

    current_time = time()

    if target_id in target_health_tracker:
        last_health = target_health_tracker[target_id]

        if current_health < last_health and current_health > 0:
            if current_time - last_hit_time >= hit_sound_cooldown:
                play_hit_sound()
                last_hit_time = current_time
                console_print(f"[HIT] Dealt {last_health - current_health:.1f} damage!")

    target_health_tracker[target_id] = current_health

# ============================================================================
# NEW: 3 AIMBOT TYPE IMPLEMENTATIONS
# ============================================================================

def mouse_aimbot(delta_x, delta_y, smoothing_enabled, smoothing_value):
    """Mouse-based aimbot - moves physical mouse cursor"""
    import win32api
    import win32con

    if smoothing_enabled and smoothing_value > 1.0:
        smooth_factor = max(0.01, min(1.0, 1.0 / smoothing_value))
        move_x = int(delta_x * smooth_factor)
        move_y = int(delta_y * smooth_factor)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, move_x, move_y, 0, 0)
    else:
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(delta_x), int(delta_y), 0, 0)

def camera_aimbot(target_world_pos, cam_pos_addr, cam_rot_addr):
    """Camera-based aimbot - rotates camera directly via CFrame"""
    try:
        cam_x = pm.read_float(cam_pos_addr)
        cam_y = pm.read_float(cam_pos_addr + 4)
        cam_z = pm.read_float(cam_pos_addr + 8)

        cam_pos = array([cam_x, cam_y, cam_z], dtype=float32)
        direction = target_world_pos - cam_pos
        direction_norm = linalg.norm(direction)

        if direction_norm < 0.1:
            return

        direction = direction / direction_norm

        from math import atan2, asin, cos, sin

        pitch = asin(-direction[1])
        yaw = atan2(direction[0], direction[2])

        cos_pitch = cos(pitch)
        sin_pitch = sin(pitch)
        cos_yaw = cos(yaw)
        sin_yaw = sin(yaw)

        # Write rotation matrix
        pm.write_float(cam_rot_addr, cos_yaw)
        pm.write_float(cam_rot_addr + 4, 0.0)
        pm.write_float(cam_rot_addr + 8, -sin_yaw)
        pm.write_float(cam_rot_addr + 12, sin_yaw * sin_pitch)
        pm.write_float(cam_rot_addr + 16, cos_pitch)
        pm.write_float(cam_rot_addr + 20, cos_yaw * sin_pitch)
        pm.write_float(cam_rot_addr + 24, sin_yaw * cos_pitch)
        pm.write_float(cam_rot_addr + 28, -sin_pitch)
        pm.write_float(cam_rot_addr + 32, cos_yaw * cos_pitch)

    except:
        pass

def memory_aimbot(target_world_pos, cam_pos_addr, cam_rot_addr, smoothing_enabled, smoothing_value):
    """Memory-based aimbot - silently modifies camera CFrame"""
    try:
        cam_x = pm.read_float(cam_pos_addr)
        cam_y = pm.read_float(cam_pos_addr + 4)
        cam_z = pm.read_float(cam_pos_addr + 8)

        cam_pos = array([cam_x, cam_y, cam_z], dtype=float32)
        direction = target_world_pos - cam_pos
        direction_norm = linalg.norm(direction)

        if direction_norm < 0.1:
            return

        direction = direction / direction_norm

        if smoothing_enabled and smoothing_value > 1.0:
            current_rot = []
            for i in range(9):
                current_rot.append(pm.read_float(cam_rot_addr + i * 4))

            current_forward = array([-current_rot[6], -current_rot[7], -current_rot[8]], dtype=float32)
            smooth_factor = 1.0 / smoothing_value
            direction = current_forward * (1 - smooth_factor) + direction * smooth_factor
            direction = direction / linalg.norm(direction)

        from math import atan2, asin, cos, sin

        pitch = asin(-direction[1])
        yaw = atan2(direction[0], direction[2])

        cos_pitch = cos(pitch)
        sin_pitch = sin(pitch)
        cos_yaw = cos(yaw)
        sin_yaw = sin(yaw)

        pm.write_float(cam_rot_addr, cos_yaw)
        pm.write_float(cam_rot_addr + 4, 0.0)
        pm.write_float(cam_rot_addr + 8, -sin_yaw)
        pm.write_float(cam_rot_addr + 12, sin_yaw * sin_pitch)
        pm.write_float(cam_rot_addr + 16, cos_pitch)
        pm.write_float(cam_rot_addr + 20, cos_yaw * sin_pitch)
        pm.write_float(cam_rot_addr + 24, sin_yaw * cos_pitch)
        pm.write_float(cam_rot_addr + 28, -sin_pitch)
        pm.write_float(cam_rot_addr + 32, cos_yaw * cos_pitch)

    except:
        pass

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

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
    if clip[3] == 0:
        return None
    ndc = clip[:3] / clip[3]
    if ndc[2] < 0 or ndc[2] > 1:
        return None
    x = (ndc[0] + 1) * 0.5 * screen_width
    y = (1 - ndc[1]) * 0.5 * screen_height
    return round(x), round(y)

def console_print(message):
    global console_output
    print(message)
    console_output.append(str(message))
    if len(console_output) > 50:
        console_output.pop(0)
    try:
        if dpg.does_item_exist("console_text"):
            display_text = "\n".join(console_output)
            dpg.set_value("console_text", display_text)
            if dpg.does_item_exist("console_child"):
                dpg.set_y_scroll("console_child", -1.0)
    except:
        pass

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

    if 0.005 < time_delta < 0.5:
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

# ============================================================================
# UPDATED AIMBOT LOOP - WITH 3 TYPES AND HIT DETECTION
# ============================================================================

def aimbotLoop():
    global target, target_id, aimbot_toggled, locked_target_id
    key_pressed_last_frame = False

    while True:
        try:
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

                    # Sticky aim - keep locked target
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

                                        # NEW: HIT DETECTION
                                        check_hit_detection(locked_target_id, health)

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

                    # Execute aim based on type
                    if target > 0 and matrixAddr > 0 and target_id > 0:
                        try:
                            hwnd_roblox = find_window_by_title("Roblox")
                            if not hwnd_roblox:
                                sleep(0.005)
                                continue

                            left, top, right, bottom = get_client_rect_on_screen(hwnd_roblox)
                            width = right - left
                            height = bottom - top

                            # Read target position
                            current_pos = array([
                                pm.read_float(target),
                                pm.read_float(target+4),
                                pm.read_float(target+8)
                            ], dtype=float32)

                            # Apply prediction
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

                            # ============================================
                            # AIMBOT TYPE SELECTION
                            # ============================================

                            if aimbot_type == "Mouse":
                                # Mouse-based aimbot
                                matrix_flat = [pm.read_float(matrixAddr + i * 4) for i in range(16)]
                                matrix = reshape(array(matrix_flat, dtype=float32), (4, 4))

                                screen_coords = world_to_screen_with_matrix(to_pos, matrix, width, height)

                                if screen_coords is not None:
                                    screen_center_x = width / 2
                                    screen_center_y = height / 2
                                    target_x, target_y = screen_coords
                                    delta_x = target_x - screen_center_x
                                    delta_y = target_y - screen_center_y

                                    if abs(delta_x) >= 0.5 or abs(delta_y) >= 0.5:
                                        mouse_aimbot(delta_x, delta_y, aimbot_smoothing_enabled, aimbot_smoothing)

                            elif aimbot_type == "Camera":
                                # Camera-based aimbot (direct CFrame manipulation)
                                camera_aimbot(to_pos, camPosAddr, camCFrameRotAddr)

                            elif aimbot_type == "Memory":
                                # Memory-based aimbot (silent)
                                memory_aimbot(to_pos, camPosAddr, camCFrameRotAddr, aimbot_smoothing_enabled, aimbot_smoothing)

                            sleep(0.001)

                        except Exception as e:
                            target = 0
                            target_id = 0
                            locked_target_id = 0
                            sleep(0.005)
                            continue
                    else:
                        # Find new target
                        target = 0
                        target_id = 0

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

# ============================================================================
# FIXED TRIGGERBOT - IMPROVED DETECTION
# ============================================================================

def triggerbot_loop():
    """FIXED Triggerbot with improved crosshair detection"""
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

            # Handle keybind
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

            # Cooldown check
            current_time = time()
            if current_time - last_shot_time < triggerbot_delay:
                sleep(0.001)
                continue

            # Get camera data
            if camAddr == 0 or camCFrameRotAddr == 0 or camPosAddr == 0:
                sleep(0.01)
                continue

            try:
                # Read camera position
                cam_x = pm.read_float(camPosAddr)
                cam_y = pm.read_float(camPosAddr + 4)
                cam_z = pm.read_float(camPosAddr + 8)

                # Read camera rotation matrix
                cam_matrix = []
                for i in range(9):
                    cam_matrix.append(pm.read_float(camCFrameRotAddr + i * 4))

                # Forward vector (where camera is looking) - negated
                look_x = -cam_matrix[6]
                look_y = -cam_matrix[7]
                look_z = -cam_matrix[8]

                # Normalize
                look_length = sqrt(look_x**2 + look_y**2 + look_z**2)
                if look_length > 0:
                    look_x /= look_length
                    look_y /= look_length
                    look_z /= look_length

                # Get local team
                local_team = None
                if triggerbot_ignore_team:
                    try:
                        team_ptr = pm.read_longlong(lpAddr + int(offsets['Team'], 16))
                        if team_ptr:
                            local_team = pm.read_longlong(team_ptr + int(offsets['TeamColor'], 16))
                    except:
                        pass

                target_found = False

                # Check all players
                if plrsAddr:
                    try:
                        players = GetChildren(plrsAddr)

                        for player in players:
                            if player == lpAddr or target_found:
                                continue

                            try:
                                # Team check
                                if triggerbot_ignore_team and local_team is not None:
                                    try:
                                        player_team_ptr = pm.read_longlong(player + int(offsets['Team'], 16))
                                        if player_team_ptr:
                                            player_team = pm.read_longlong(player_team_ptr + int(offsets['TeamColor'], 16))
                                            if player_team == local_team:
                                                continue
                                    except:
                                        pass

                                # Get character
                                char = pm.read_longlong(player + int(offsets['ModelInstance'], 16))
                                if not char:
                                    continue

                                # Dead check
                                if triggerbot_ignore_dead:
                                    try:
                                        hum = FindFirstChildOfClass(char, 'Humanoid')
                                        if hum:
                                            health = pm.read_float(hum + int(offsets['Health'], 16))
                                            if health <= 0:
                                                continue
                                    except:
                                        pass

                                # Check all body parts
                                body_parts = [
                                    'Head', 'UpperTorso', 'LowerTorso', 'HumanoidRootPart',
                                    'LeftUpperArm', 'RightUpperArm',
                                    'LeftLowerArm', 'RightLowerArm',
                                    'LeftHand', 'RightHand',
                                    'LeftUpperLeg', 'RightUpperLeg',
                                    'LeftLowerLeg', 'RightLowerLeg',
                                    'LeftFoot', 'RightFoot'
                                ]

                                for part_name in body_parts:
                                    try:
                                        part = FindFirstChild(char, part_name)
                                        if not part:
                                            continue

                                        primitive = pm.read_longlong(part + int(offsets['Primitive'], 16))
                                        if not primitive:
                                            continue

                                        # Get part position
                                        px = pm.read_float(primitive + int(offsets['Position'], 16))
                                        py = pm.read_float(primitive + int(offsets['Position'], 16) + 4)
                                        pz = pm.read_float(primitive + int(offsets['Position'], 16) + 8)

                                        # Direction from camera to part
                                        dx = px - cam_x
                                        dy = py - cam_y
                                        dz = pz - cam_z

                                        dist = sqrt(dx*dx + dy*dy + dz*dz)

                                        if dist < 1 or dist > 500:
                                            continue

                                        # Normalize direction
                                        dx /= dist
                                        dy /= dist
                                        dz /= dist

                                        # Calculate dot product (how aligned)
                                        dot = look_x * dx + look_y * dy + look_z * dz

                                        # FIXED: More lenient threshold for better detection
                                        # 0.998 = ~3.6 degrees (easier to trigger)
                                        if dot > 0.998:
                                            target_found = True
                                            break
                                    except:
                                        continue

                                if target_found:
                                    break

                            except:
                                continue
                    except:
                        pass

                # Shoot if target found
                if target_found:
                    try:
                        import win32api
                        import win32con

                        # Click
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        sleep(0.05)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

                        last_shot_time = current_time
                        console_print("[TRIGGERBOT] Shot fired!")
                    except:
                        pass

                sleep(0.001)

            except Exception as e:
                sleep(0.01)

        except Exception as e:
            sleep(0.01)

# ============================================================================
# INITIALIZATION
# ============================================================================

def init():
    global dataModel, wsAddr, camAddr, camCFrameRotAddr, plrsAddr, lpAddr, matrixAddr, camPosAddr, injected

    try:
        console_print('\n[*] Initializing memory pointers...')

        fake_dm_ptr = baseAddr + int(offsets['FakeDataModelPointer'], 16)
        fakeDatamodel = pm.read_longlong(fake_dm_ptr)

        real_dm_offset = fakeDatamodel + int(offsets['FakeDataModelToDataModel'], 16)
        dataModel = pm.read_longlong(real_dm_offset)

        ws_offset = dataModel + int(offsets['Workspace'], 16)
        wsAddr = pm.read_longlong(ws_offset)

        cam_offset = wsAddr + int(offsets['Camera'], 16)
        camAddr = pm.read_longlong(cam_offset)
        camCFrameRotAddr = camAddr + int(offsets['CameraRotation'], 16)
        camPosAddr = camAddr + int(offsets['CameraPos'], 16)

        ve_ptr = baseAddr + int(offsets['VisualEnginePointer'], 16)
        visualEngine = pm.read_longlong(ve_ptr)
        matrixAddr = visualEngine + int(offsets['viewmatrix'], 16)

        plrsAddr = FindFirstChildOfClass(dataModel, 'Players')

        lp_offset = plrsAddr + int(offsets['LocalPlayer'], 16)
        lpAddr = pm.read_longlong(lp_offset)

        console_print('\n[SUCCESS] Injected successfully!')
        injected = True

    except ProcessError as e:
        console_print(f'\nProcessError: {e}')
        console_print('Make sure Roblox is running!')
        return
    except Exception as e:
        console_print(f'\nError during initialization: {e}')
        return

def background_process_monitor():
    global baseAddr
    while True:
        if is_process_dead():
            while not yield_for_program("RobloxPlayerBeta.exe"):
                sleep(0.5)
            baseAddr = get_base_addr()
        sleep(0.1)

# ============================================================================
# START THREADS
# ============================================================================

Thread(target=background_process_monitor, daemon=True).start()
Thread(target=aimbotLoop, daemon=True).start()
Thread(target=triggerbot_loop, daemon=True).start()

# ============================================================================
# NEW: CALLBACKS FOR UI
# ============================================================================

def aimbot_type_callback(sender, app_data):
    global aimbot_type
    aimbot_type = app_data
    console_print(f"[AIMBOT] Type changed to: {aimbot_type}")

def hit_sound_callback(sender, app_data):
    global hit_sound_enabled
    hit_sound_enabled = app_data

def hit_sound_volume_callback(sender, app_data):
    global hit_sound_volume
    hit_sound_volume = int(app_data)

def aimbot_callback(sender, app_data):
    global aimbot_enabled, aimbot_toggled
    if not injected:
        return
    aimbot_enabled = app_data
    if not app_data:
        aimbot_toggled = False

def triggerbot_callback(sender, app_data):
    global triggerbot_enabled, triggerbot_toggled
    if not injected:
        return
    triggerbot_enabled = app_data
    if not app_data:
        triggerbot_toggled = False

# ============================================================================
# SIMPLIFIED UI (BASIC VERSION)
# ============================================================================

dpg.create_context()

with dpg.window(label="AckWare COMPLETE", tag="Primary Window",
                pos=[50, 50], width=400, height=600):

    dpg.add_text("ACKWARE - COMPLETE EDITION", color=(180, 140, 255))
    dpg.add_text("With 3 Aimbot Types + Hit Sounds + Fixed Triggerbot", color=(120, 120, 140))
    dpg.add_separator()

    with dpg.group():
        dpg.add_text("INJECTION", color=(255, 200, 100))
        dpg.add_button(label="INJECT NOW", callback=lambda: Thread(target=init, daemon=True).start(),
                      width=-1, height=30)

    dpg.add_spacer(height=10)

    with dpg.group():
        dpg.add_text("AIMBOT TYPE", color=(255, 100, 100))
        dpg.add_combo(["Mouse", "Camera", "Memory"],
                     default_value=aimbot_type,
                     tag="aimbot_type_combo",
                     callback=aimbot_type_callback,
                     width=-1)
        dpg.add_text("• Mouse = Cursor movement", color=(150, 150, 160))
        dpg.add_text("• Camera = Rotate view (smooth)", color=(150, 150, 160))
        dpg.add_text("• Memory = Silent (BEST)", color=(150, 150, 160))

    dpg.add_spacer(height=10)

    with dpg.group():
        dpg.add_text("HIT SOUND", color=(100, 255, 200))
        dpg.add_checkbox(label="Enable Hit Sound",
                        default_value=hit_sound_enabled,
                        callback=hit_sound_callback)
        dpg.add_text("Volume:", color=(200, 200, 200))
        dpg.add_slider_int(default_value=hit_sound_volume,
                          min_value=0, max_value=100,
                          callback=hit_sound_volume_callback,
                          width=-1, format="%d%%")

    dpg.add_spacer(height=10)

    with dpg.group():
        dpg.add_text("FEATURES", color=(100, 200, 255))
        dpg.add_checkbox(label="Aimbot", default_value=aimbot_enabled,
                        callback=aimbot_callback, tag="aimbot_checkbox")
        dpg.add_checkbox(label="Triggerbot (FIXED)", default_value=triggerbot_enabled,
                        callback=triggerbot_callback, tag="triggerbot_checkbox")

    dpg.add_spacer(height=10)

    with dpg.group():
        dpg.add_text("STATUS", color=(255, 200, 100))
        dpg.add_text("Ready to inject!", color=(100, 255, 100))

dpg.create_viewport(title="ACKWARE COMPLETE", width=450, height=650)
dpg.setup_dearpygui()
dpg.set_primary_window("Primary Window", True)
dpg.show_viewport()

print("\n" + "="*60)
print("ACKWARE COMPLETE - READY")
print("="*60)
print("Features:")
print("✓ 3 Aimbot Types: Mouse, Camera, Memory")
print("✓ Hit Sound System")
print("✓ Fixed Triggerbot")
print("✓ Updated Offsets for latest Roblox")
print("="*60)

dpg.start_dearpygui()
dpg.destroy_context()
