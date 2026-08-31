#!/usr/bin/env python3
"""
Sanity test for display_Partial() on Waveshare 7.5" V2 e-ink display.

This script:
1. Displays a full white screen
2. Uses display_Partial() to update a small black box
3. Compares visual result with full display

If partial refresh works:
  - You should see a black box appear without the full-screen flash
  - The box should be at exactly coordinates (100, 50) to (200, 150)

If partial refresh is broken:
  - The output will be stretched/distorted
  - Or the box will appear in the wrong location
"""

import time
from display import init_display, clear_and_sleep, test_partial_refresh

def main():
    epd = init_display()
    
    try:
        print("Starting display_Partial() sanity test...")
        print("Watch the screen for a small black box at the left side.\n")
        
        time.sleep(1)
        
        # Run the test
        test_partial_refresh(epd)
        
        print("\n✓ Test complete. Observe the display:")
        print("  - If black box appears cleanly at left (100-200px H, 50-150px V) → partial works ✓")
        print("  - If output is stretched or in wrong spot → driver issue ✗")
        print("\nScreen will clear in 5 seconds...")
        time.sleep(5)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        clear_and_sleep(epd)

if __name__ == "__main__":
    main()
