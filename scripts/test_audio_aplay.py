import sys
import os
import subprocess
sys.path.append("/home/burkettdaniel927/projects/isopgem/src")

from pillars.tq.services.amun_audio_service import AmunAudioService

def test_playback():
    print("Generating test sound...")
    # 440Hz carrier, 2Hz modulation
    path = AmunAudioService.generate_wave_file(440.0, 2.0, duration=1.0)
    print(f"Generated: {path}")
    
    print("Attempting playback with aplay...")
    try:
        result = subprocess.run(['aplay', path], capture_output=True, text=True)
        if result.returncode == 0:
            print("SUCCESS: aplay completed successfully.")
            print(result.stdout)
        else:
            print("FAILURE: aplay returned error code.")
            print(result.stderr)
    except FileNotFoundError:
        print("FAILURE: aplay command not found.")
    
    # Cleanup
    if os.path.exists(path):
        os.remove(path)

if __name__ == "__main__":
    test_playback()
