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
        
        # NEW: Silent Aim Section
        with dpg.child_window(height=140, border=True):
            dpg.add_text("Silent Aim (No Mouse Movement)", color=(255, 100, 100))
            dpg.add_separator()
            dpg.add_spacer(height=2)
            
            dpg.add_checkbox(label="Enable Silent Aim", 
                            default_value=silent_aim_enabled, 
                            callback=silent_aim_callback, 
                            tag="silent_aim_cb")
            dpg.add_text("Note: Disables normal aimbot smoothing", color=(150, 150, 160))
            dpg.add_spacer(height=2)
            dpg.add_text("Silent Aim FOV:", color=(200, 200, 200))
            dpg.add_slider_float(default_value=silent_aim_fov, 
                                min_value=50.0, max_value=400.0, 
                                callback=silent_aim_fov_slider_callback, 
                                width=-1, 
                                tag="silent_aim_fov_slider", 
                                format="%.0f px")
        
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
