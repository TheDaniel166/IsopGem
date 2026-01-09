from PyQt6.QtCore import QUrl

def test_url_parsing():
    ids = ["123", "8", "916"]
    
    print("Testing URL parsing for docimg IDs:")
    
    for i in ids:
        u_str = f"docimg://{i}"
        u = QUrl(u_str)
        print(f"\nString: {u_str}")
        print(f"  Scheme: '{u.scheme()}'")
        print(f"  Host:   '{u.host()}'")
        print(f"  Path:   '{u.path()}'")
        print(f"  Auth:   '{u.authority()}'")
        
        # Test extraction logic
        try:
            val = int(u.path().strip('/'))
            print(f"  Parsed ID from path: {val}")
        except ValueError:
            print(f"  FAILED to parse ID from path")
            
        try:
            val = int(u.host())
            print(f"  Parsed ID from host: {val}")
        except ValueError:
            print(f"  FAILED to parse ID from host")
        
        print(f"  Full String: '{u.toString()}'")

    print("\nTesting triple slash:")
    u3 = QUrl("docimg:///123")
    print(f"String: docimg:///123")
    print(f"  Scheme: '{u3.scheme()}'")
    print(f"  Host:   '{u3.host()}'")
    print(f"  Path:   '{u3.path()}'")
    print(f"  Path stripped: '{u3.path().strip('/')}'")

    print("\nTesting validation of IP reconstruction:")
    # 916 -> 0.0.3.148
    # 3 * 256 + 148 = 916
    ip_str = "0.0.3.148"
    parts = [int(p) for p in ip_str.split('.')]
    reconstructed = (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]
    print(f"IP {ip_str} -> {reconstructed} (Expected: 916)")

    ip_str2 = "0.0.0.8"
    parts = [int(p) for p in ip_str2.split('.')]
    reconstructed = (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]
    print(f"IP {ip_str2} -> {reconstructed} (Expected: 8)")
    
if __name__ == "__main__":
    test_url_parsing()
