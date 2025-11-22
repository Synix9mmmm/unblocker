# UPDATED MAIN.PY with 3 Aimbot Types, Hit Sounds, and Fixed Triggerbot
# Place this code at the TOP of your main.py (after the KeyAuth section)

import winsound
import threading
from time import time, sleep

# ============================================================================
# ADDITIONAL GLOBALS FOR NEW FEATURES
# ============================================================================

# Aimbot Type Selection
aimbot_type = "Mouse"  # Options: "Mouse", "Camera", "Memory"

# Hit Sound System
hit_sound_enabled = True
hit_sound_volume = 50  # 0-100
last_hit_time = 0.0
hit_sound_cooldown = 0.1  # Prevent spam

# Hit Detection
target_health_tracker = {}  # {target_id: last_health}

# ============================================================================
# HIT SOUND SYSTEM
# ============================================================================

def play_hit_sound():
    """Play hit confirmation sound"""
    if not hit_sound_enabled:
        return

    try:
        # Play Windows beep (frequency, duration)
        # You can replace with custom .wav file: winsound.PlaySound("hitsound.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
        winsound.Beep(800, 50)  # 800Hz for 50ms
    except:
        pass

def check_hit_detection(target_id, current_health):
    """Check if we hit the target and play sound"""
    global target_health_tracker, last_hit_time

    if not hit_sound_enabled or target_id == 0:
        return

    current_time = time()

    # Check if we have previous health data
    if target_id in target_health_tracker:
        last_health = target_health_tracker[target_id]

        # Health decreased = we hit them
        if current_health < last_health and current_health > 0:
            # Cooldown check to prevent spam
            if current_time - last_hit_time >= hit_sound_cooldown:
                play_hit_sound()
                last_hit_time = current_time
                console_print(f"[HIT] Dealt {last_health - current_health:.1f} damage!")

    # Update health tracker
    target_health_tracker[target_id] = current_health

# ============================================================================
# AIMBOT IMPLEMENTATIONS
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
        # Read camera position
        cam_x = pm.read_float(cam_pos_addr)
        cam_y = pm.read_float(cam_pos_addr + 4)
        cam_z = pm.read_float(cam_pos_addr + 8)

        cam_pos = array([cam_x, cam_y, cam_z], dtype=float32)

        # Calculate direction to target
        direction = target_world_pos - cam_pos
        direction_norm = linalg.norm(direction)

        if direction_norm < 0.1:
            return

        direction = direction / direction_norm

        # Calculate pitch and yaw
        from math import atan2, asin, pi

        pitch = asin(-direction[1])  # Y component for pitch
        yaw = atan2(direction[0], direction[2])  # X and Z for yaw

        # Write rotation to camera
        # Camera rotation matrix format (3x3)
        from math import cos, sin

        # Build rotation matrix
        cos_pitch = cos(pitch)
        sin_pitch = sin(pitch)
        cos_yaw = cos(yaw)
        sin_yaw = sin(yaw)

        # Right vector
        pm.write_float(cam_rot_addr, cos_yaw)
        pm.write_float(cam_rot_addr + 4, 0.0)
        pm.write_float(cam_rot_addr + 8, -sin_yaw)

        # Up vector
        pm.write_float(cam_rot_addr + 12, sin_yaw * sin_pitch)
        pm.write_float(cam_rot_addr + 16, cos_pitch)
        pm.write_float(cam_rot_addr + 20, cos_yaw * sin_pitch)

        # Forward vector (negated look)
        pm.write_float(cam_rot_addr + 24, sin_yaw * cos_pitch)
        pm.write_float(cam_rot_addr + 28, -sin_pitch)
        pm.write_float(cam_rot_addr + 32, cos_yaw * cos_pitch)

    except Exception as e:
        pass

def memory_aimbot(target_world_pos, cam_pos_addr, cam_rot_addr, smoothing_enabled, smoothing_value):
    """Memory-based aimbot - silently modifies camera CFrame (no visual shake)"""
    try:
        # Read current camera position
        cam_x = pm.read_float(cam_pos_addr)
        cam_y = pm.read_float(cam_pos_addr + 4)
        cam_z = pm.read_float(cam_pos_addr + 8)

        cam_pos = array([cam_x, cam_y, cam_z], dtype=float32)

        # Calculate target direction
        direction = target_world_pos - cam_pos
        direction_norm = linalg.norm(direction)

        if direction_norm < 0.1:
            return

        direction = direction / direction_norm

        # Read current camera rotation
        current_rot = []
        for i in range(9):
            current_rot.append(pm.read_float(cam_rot_addr + i * 4))

        # Current forward vector (negated)
        current_forward = array([-current_rot[6], -current_rot[7], -current_rot[8]], dtype=float32)

        # Apply smoothing to direction
        if smoothing_enabled and smoothing_value > 1.0:
            smooth_factor = 1.0 / smoothing_value
            direction = current_forward * (1 - smooth_factor) + direction * smooth_factor
            direction = direction / linalg.norm(direction)

        # Calculate pitch and yaw from smoothed direction
        from math import atan2, asin, cos, sin

        pitch = asin(-direction[1])
        yaw = atan2(direction[0], direction[2])

        # Build rotation matrix
        cos_pitch = cos(pitch)
        sin_pitch = sin(pitch)
        cos_yaw = cos(yaw)
        sin_yaw = sin(yaw)

        # Write to memory (silent, no screen shake)
        # Right vector
        pm.write_float(cam_rot_addr, cos_yaw)
        pm.write_float(cam_rot_addr + 4, 0.0)
        pm.write_float(cam_rot_addr + 8, -sin_yaw)

        # Up vector
        pm.write_float(cam_rot_addr + 12, sin_yaw * sin_pitch)
        pm.write_float(cam_rot_addr + 16, cos_pitch)
        pm.write_float(cam_rot_addr + 20, cos_yaw * sin_pitch)

        # Forward vector
        pm.write_float(cam_rot_addr + 24, sin_yaw * cos_pitch)
        pm.write_float(cam_rot_addr + 28, -sin_pitch)
        pm.write_float(cam_rot_addr + 32, cos_yaw * cos_pitch)

    except Exception as e:
        pass

# ============================================================================
# UPDATED AIMBOT LOOP (REPLACE EXISTING)
# ============================================================================

def aimbotLoop_UPDATED():
    """Updated aimbot loop with 3 types and hit detection"""
    global target, target_id, aimbot_toggled, last_target_health, locked_target_id
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

                                        # HIT DETECTION
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
# FIXED TRIGGERBOT (IMPROVED DETECTION)
# ============================================================================

def triggerbot_loop_FIXED():
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
            if camAddr == 0 or camCFrameRotAddr == 0 or camPosAddr == 0 or matrixAddr == 0:
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
                                        # 0.9994 = ~2 degrees, 0.999 = ~2.5 degrees
                                        if dot > 0.998:  # Increased threshold for easier triggering
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
# CALLBACKS FOR NEW FEATURES
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

# ============================================================================
# INSTRUCTIONS TO INTEGRATE
# ============================================================================
"""
1. REPLACE the existing aimbotLoop() function call with:
   Thread(target=aimbotLoop_UPDATED, daemon=True).start()

2. REPLACE the existing triggerbot_loop() function call with:
   Thread(target=triggerbot_loop_FIXED, daemon=True).start()

3. ADD to the Aimbot Panel UI (in the DearPyGUI section):

   with dpg.child_window(height=120, border=True):
       dpg.add_text("Aimbot Type", color=(255, 150, 100))
       dpg.add_separator()
       dpg.add_spacer(height=2)

       dpg.add_text("Select Type:", color=(200, 200, 200))
       dpg.add_combo(["Mouse", "Camera", "Memory"],
                    default_value=aimbot_type,
                    tag="aimbot_type_combo",
                    callback=aimbot_type_callback,
                    width=-1)
       dpg.add_text("Mouse = Move cursor | Camera = Rotate view | Memory = Silent",
                   color=(150, 150, 160))

   dpg.add_spacer(height=3)

   with dpg.child_window(height=100, border=True):
       dpg.add_text("Hit Sound", color=(100, 255, 200))
       dpg.add_separator()
       dpg.add_spacer(height=2)

       dpg.add_checkbox(label="Enable Hit Sound",
                       default_value=hit_sound_enabled,
                       callback=hit_sound_callback)
       dpg.add_text("Volume:", color=(200, 200, 200))
       dpg.add_slider_int(default_value=hit_sound_volume,
                         min_value=0, max_value=100,
                         callback=hit_sound_volume_callback,
                         width=-1, format="%d%%")

4. UPDATE config save/load to include new settings:
   - Add to save_config(): 'aimbot_type', 'hit_sound_enabled', 'hit_sound_volume'
   - Add to load_config(): Load these values and update UI
"""
