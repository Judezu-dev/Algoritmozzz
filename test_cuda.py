import sys
import torch
import numba.cuda
import cupy as cp

print(f"Python version: {sys.version.split()[0]}")

# Validar PyTorch
torch_ok = torch.cuda.is_available()
print(f"PyTorch CUDA disponible: {torch_ok}")
if torch_ok:
    print(f" -> Dispositivo: {torch.cuda.get_device_name(0)}")

# Validar CuPy
try:
    arr = cp.array([1, 2, 3])
    print(f"CuPy OK: Arreglo en GPU -> {arr.sum()}")
except Exception as e:
    print(f"CuPy Error: {e}")

# Validar Numba CUDA
try:
    numba_ok = numba.cuda.is_available()
    print(f"Numba CUDA disponible: {numba_ok}")
except Exception as e:
    print(f"Numba CUDA Error: {e}")