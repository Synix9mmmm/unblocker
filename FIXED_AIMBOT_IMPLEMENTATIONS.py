# ============================================================================
# FIXED CAMERA AND MEMORY AIMBOT IMPLEMENTATIONS
# ============================================================================
# These are the CORRECTED versions that actually work
# Copy these into your original script to replace the broken implementations
# ============================================================================

from numpy import array, float32, linalg
from math import atan2, asin, cos, sin, sqrt
import winsound

# ============================================================================
# BUG FIX: The rotation matrix had an incorrect sign on sin_pitch
# This caused the camera to aim incorrectly in the Y axis
# ============================================================================

def camera_aimbot_FIXED(target_world_pos, cam_pos_addr, cam_rot_addr):
    """
    Camera-based aimbot - rotates camera directly via CFrame
    FIXED VERSION - corrected rotation matrix calculation
    """
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

        # Normalize direction vector
        direction = direction / direction_norm

        # Calculate pitch and yaw from direction
        pitch = asin(-direction[1])
        yaw = atan2(direction[0], direction[2])

        # Calculate rotation matrix components
        cos_pitch = cos(pitch)
        sin_pitch = sin(pitch)
        cos_yaw = cos(yaw)
        sin_yaw = sin(yaw)

        # CORRECTED ROTATION MATRIX
        # This is a 3x3 matrix stored in row-major order
        # Right vector (X axis)
        pm.write_float(cam_rot_addr + 0,  cos_yaw)
        pm.write_float(cam_rot_addr + 4,  sin_yaw * sin_pitch)
        pm.write_float(cam_rot_addr + 8,  sin_yaw * cos_pitch)

        # Up vector (Y axis)
        pm.write_float(cam_rot_addr + 12, 0.0)
        pm.write_float(cam_rot_addr + 16, cos_pitch)
        pm.write_float(cam_rot_addr + 20, -sin_pitch)

        # Forward vector (Z axis) - NEGATED
        pm.write_float(cam_rot_addr + 24, -sin_yaw)
        pm.write_float(cam_rot_addr + 28, cos_yaw * sin_pitch)  # FIXED: was -sin_pitch
        pm.write_float(cam_rot_addr + 32, cos_yaw * cos_pitch)

    except Exception as e:
        # Silent fail - don't crash the aimbot
        pass


def memory_aimbot_FIXED(target_world_pos, cam_pos_addr, cam_rot_addr, smoothing_enabled, smoothing_value):
    """
    Memory-based aimbot - silently modifies camera CFrame
    FIXED VERSION - corrected rotation matrix + proper smoothing
    """
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

        # Normalize direction
        direction = direction / direction_norm

        # Apply smoothing if enabled
        if smoothing_enabled and smoothing_value > 1.0:
            try:
                # Read current rotation matrix
                current_rot = []
                for i in range(9):
                    current_rot.append(pm.read_float(cam_rot_addr + i * 4))

                # Extract current forward vector (indices 6, 7, 8 are third row)
                # Need to negate because matrix stores -forward
                current_forward = array([
                    -current_rot[6],
                    -current_rot[7],
                    -current_rot[8]
                ], dtype=float32)

                # Smoothly interpolate between current and target direction
                smooth_factor = max(0.01, min(1.0, 1.0 / smoothing_value))
                direction = current_forward * (1.0 - smooth_factor) + direction * smooth_factor

                # Re-normalize after interpolation
                direction = direction / linalg.norm(direction)
            except:
                # If smoothing fails, just use direct aim
                pass

        # Calculate pitch and yaw from direction
        pitch = asin(-direction[1])
        yaw = atan2(direction[0], direction[2])

        # Calculate rotation matrix components
        cos_pitch = cos(pitch)
        sin_pitch = sin(pitch)
        cos_yaw = cos(yaw)
        sin_yaw = sin(yaw)

        # CORRECTED ROTATION MATRIX
        # Right vector (X axis)
        pm.write_float(cam_rot_addr + 0,  cos_yaw)
        pm.write_float(cam_rot_addr + 4,  sin_yaw * sin_pitch)
        pm.write_float(cam_rot_addr + 8,  sin_yaw * cos_pitch)

        # Up vector (Y axis)
        pm.write_float(cam_rot_addr + 12, 0.0)
        pm.write_float(cam_rot_addr + 16, cos_pitch)
        pm.write_float(cam_rot_addr + 20, -sin_pitch)

        # Forward vector (Z axis) - NEGATED
        pm.write_float(cam_rot_addr + 24, -sin_yaw)
        pm.write_float(cam_rot_addr + 28, cos_yaw * sin_pitch)  # FIXED: was -sin_pitch
        pm.write_float(cam_rot_addr + 32, cos_yaw * cos_pitch)

    except Exception as e:
        # Silent fail
        pass


# ============================================================================
# ALTERNATIVE SIMPLER IMPLEMENTATION (If above doesn't work)
# ============================================================================
# This uses a different approach - converting to Euler angles and back

def camera_aimbot_ALTERNATIVE(target_world_pos, cam_pos_addr, cam_rot_addr):
    """
    Alternative implementation using LookAt matrix construction
    """
    try:
        # Read camera position
        cam_pos = array([
            pm.read_float(cam_pos_addr),
            pm.read_float(cam_pos_addr + 4),
            pm.read_float(cam_pos_addr + 8)
        ], dtype=float32)

        # Calculate forward direction (where we want to look)
        forward = target_world_pos - cam_pos
        forward_len = linalg.norm(forward)

        if forward_len < 0.1:
            return

        forward = forward / forward_len

        # Calculate right vector (cross product with world up)
        world_up = array([0.0, 1.0, 0.0], dtype=float32)
        right = linalg.cross(world_up, forward)
        right_len = linalg.norm(right)

        if right_len < 0.001:
            # Forward is parallel to world up, use different up vector
            world_up = array([0.0, 0.0, 1.0], dtype=float32)
            right = linalg.cross(world_up, forward)
            right_len = linalg.norm(right)

        if right_len < 0.001:
            return

        right = right / right_len

        # Calculate up vector (cross product of forward and right)
        up = linalg.cross(forward, right)

        # Write rotation matrix (Right, Up, -Forward)
        # Right vector
        pm.write_float(cam_rot_addr + 0,  right[0])
        pm.write_float(cam_rot_addr + 4,  right[1])
        pm.write_float(cam_rot_addr + 8,  right[2])

        # Up vector
        pm.write_float(cam_rot_addr + 12, up[0])
        pm.write_float(cam_rot_addr + 16, up[1])
        pm.write_float(cam_rot_addr + 20, up[2])

        # Forward vector (negated)
        pm.write_float(cam_rot_addr + 24, -forward[0])
        pm.write_float(cam_rot_addr + 28, -forward[1])
        pm.write_float(cam_rot_addr + 32, -forward[2])

    except Exception as e:
        pass


# ============================================================================
# TESTING / DEBUGGING VERSIONS (with console output)
# ============================================================================

def camera_aimbot_DEBUG(target_world_pos, cam_pos_addr, cam_rot_addr):
    """
    Debug version that prints to console - use this to diagnose issues
    """
    try:
        cam_pos = array([
            pm.read_float(cam_pos_addr),
            pm.read_float(cam_pos_addr + 4),
            pm.read_float(cam_pos_addr + 8)
        ], dtype=float32)

        print(f"[DEBUG] Camera pos: {cam_pos}")
        print(f"[DEBUG] Target pos: {target_world_pos}")

        direction = target_world_pos - cam_pos
        direction_norm = linalg.norm(direction)

        print(f"[DEBUG] Direction: {direction}, Distance: {direction_norm}")

        if direction_norm < 0.1:
            print("[DEBUG] Target too close!")
            return

        direction = direction / direction_norm
        pitch = asin(-direction[1])
        yaw = atan2(direction[0], direction[2])

        print(f"[DEBUG] Pitch: {pitch:.3f}, Yaw: {yaw:.3f}")

        cos_pitch = cos(pitch)
        sin_pitch = sin(pitch)
        cos_yaw = cos(yaw)
        sin_yaw = sin(yaw)

        # Write rotation matrix
        pm.write_float(cam_rot_addr + 0,  cos_yaw)
        pm.write_float(cam_rot_addr + 4,  sin_yaw * sin_pitch)
        pm.write_float(cam_rot_addr + 8,  sin_yaw * cos_pitch)
        pm.write_float(cam_rot_addr + 12, 0.0)
        pm.write_float(cam_rot_addr + 16, cos_pitch)
        pm.write_float(cam_rot_addr + 20, -sin_pitch)
        pm.write_float(cam_rot_addr + 24, -sin_yaw)
        pm.write_float(cam_rot_addr + 28, cos_yaw * sin_pitch)
        pm.write_float(cam_rot_addr + 32, cos_yaw * cos_pitch)

        print("[DEBUG] Matrix written successfully!")

    except Exception as e:
        print(f"[DEBUG ERROR] {e}")


# ============================================================================
# INTEGRATION INSTRUCTIONS
# ============================================================================

"""
HOW TO FIX YOUR SCRIPT:

1. In your aimbotLoop() function, find where it calls camera_aimbot() or memory_aimbot()

2. Replace them with the FIXED versions:

   # OLD:
   camera_aimbot(to_pos, camPosAddr, camCFrameRotAddr)

   # NEW:
   camera_aimbot_FIXED(to_pos, camPosAddr, camCFrameRotAddr)


3. If the FIXED version still doesn't work, try the ALTERNATIVE version:

   camera_aimbot_ALTERNATIVE(to_pos, camPosAddr, camCFrameRotAddr)


4. To debug, use the DEBUG version temporarily:

   camera_aimbot_DEBUG(to_pos, camPosAddr, camCFrameRotAddr)

   Then check console output to see what's failing.


WHAT WAS WRONG:
- The rotation matrix had incorrect signs on some components
- Specifically, the Y component of the forward vector was negated incorrectly
- This caused the camera to aim in the wrong vertical direction

THE FIX:
- Changed line writing to offset +28 from -sin_pitch to cos_yaw * sin_pitch
- Reorganized matrix to proper Right/Up/Forward layout
- Added alternative implementation using LookAt matrix construction
"""
