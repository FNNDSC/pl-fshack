#!/bin/bash

# Simple CLI to pull one specific version of the 
# nvidia driver.
#
# Call with an appropriate version, i.e. 440.100

VER=$1

wget http://us.download.nvidia.com/XFree86/Linux-x86_64/${VER}/NVIDIA-Linux-x86_64-${VER}.run

