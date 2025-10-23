"""
Test script untuk skin detection feature
Run this script untuk test skin detection secara standalone
"""

import cv2
import numpy as np
import sys
import os

# Add server directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from skin_detector import SkinDetector

def main():
    """
    Test skin detection dengan webcam
    """
    print("=== Skin Detection Test ===")
    print("Press 'q' to quit")
    print("Press 's' to save screenshot")
    print("Press 'm' to toggle mask view")
    print("Press 'b' to toggle bounding box")
    print("Press 'c' to toggle contour drawing")
    print()
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Initialize skin detector
    detector = SkinDetector()
    
    # State variables
    show_mask = False
    screenshot_count = 0
    
    print("Camera initialized successfully")
    print(f"Skin range: {detector.lower_skin} - {detector.upper_skin}")
    print(f"Min contour area: {detector.min_contour_area}")
    print()
    
    while True:
        # Capture frame
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Failed to read frame")
            break
        
        # Process frame with skin detection
        processed_frame, mask, contour = detector.process_frame(frame)
        
        # Display contour information
        if contour is not None:
            info = detector.get_contour_info(contour)
            
            # Display text info on frame
            cv2.putText(
                processed_frame,
                f"Hand Detected!",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
            
            cv2.putText(
                processed_frame,
                f"Area: {int(info['area'])}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
            
            cv2.putText(
                processed_frame,
                f"Center: ({info['centroid']['x']}, {info['centroid']['y']})",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
        else:
            cv2.putText(
                processed_frame,
                "No hand detected",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )
        
        # Display instructions
        cv2.putText(
            processed_frame,
            "Press 'q' to quit | 'm' for mask | 's' to save",
            (10, processed_frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )
        
        # Show processed frame
        cv2.imshow('Skin Detection - Processed', processed_frame)
        
        # Show mask if enabled
        if show_mask:
            # Convert mask to 3-channel for side-by-side display
            mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            
            # Create side-by-side view
            combined = np.hstack([frame, mask_colored])
            cv2.imshow('Original vs Mask', combined)
        
        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print("Quitting...")
            break
        elif key == ord('m'):
            show_mask = not show_mask
            print(f"Mask view: {'ON' if show_mask else 'OFF'}")
            if not show_mask:
                cv2.destroyWindow('Original vs Mask')
        elif key == ord('s'):
            # Save screenshot
            screenshot_count += 1
            filename = f"screenshot_{screenshot_count}.jpg"
            cv2.imwrite(filename, processed_frame)
            print(f"Screenshot saved: {filename}")
        elif key == ord('b'):
            # Toggle bounding box
            detector.toggle_bounding_box(not detector.show_bounding_box)
            print(f"Bounding box: {'ON' if detector.show_bounding_box else 'OFF'}")
        elif key == ord('c'):
            # Toggle contour drawing
            detector.toggle_contour_drawing(not detector.draw_contours)
            print(f"Contour drawing: {'ON' if detector.draw_contours else 'OFF'}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("Test completed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
