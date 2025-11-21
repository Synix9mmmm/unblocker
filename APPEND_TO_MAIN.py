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
