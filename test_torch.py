"""
Test PyTorch installation
"""
import torch
import sys

def test_pytorch():
    print(f"Python version: {sys.version}")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA device: {torch.cuda.get_device_name(0)}")
        print(f"CUDA version: {torch.version.cuda}")
        
        # Test CUDA tensor creation
        x = torch.tensor([1, 2, 3]).cuda()
        print(f"CUDA tensor: {x}")
        print(f"CUDA tensor device: {x.device}")
    else:
        print("CUDA not available, using CPU only")
        x = torch.tensor([1, 2, 3])
        print(f"CPU tensor: {x}")
    
    # Test basic operations
    y = x * 2
    print(f"Basic operation result: {y}")
    
    print("PyTorch test completed successfully!")

if __name__ == "__main__":
    test_pytorch() 