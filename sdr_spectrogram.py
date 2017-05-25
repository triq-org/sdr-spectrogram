#!/usr/bin/env python

"""Generate spectrogram thumbnails for SDR data."""

import os.path
import os
import argparse
import subprocess


rates = {
    "1024k": 1024000,
    "2048k": 2048000,
    "2560k": 2560000,
    "3200k": 3200000
}

# bits, channels, format, dyn_range
formats = {
    ".cfile": (32, 2, "signed-integer",  120),
    ".data":  (8,  2, "unsigned-integer", 50),
    ".cu8":   (8,  2, "unsigned-integer", 50),
    ".cs8":   (8,  2, "signed-integer",   50),
    ".cs16":  (16, 2, "signed-integer",  100),
    ".s16":   (16, 1, "signed-integer",  100),
    ".cs32":  (32, 2, "signed-integer",  120),
    ".s32":   (32, 1, "signed-integer",  120),
    ".cf32":  (32, 2, "float",           120),
    ".f32":   (32, 1, "float",           120)
}


def generate_thumbnail(path, width=1024, height=257):
    """Generate a single thumbnail."""
    rate = 250000  # default
    peak = 0  # stat from input someday
    outpath = path + ".png"
    basename = os.path.basename(path)
    (_, ext) = os.path.splitext(path)

    try:
        (bits, channels, bit_format, dyn_range) = formats[ext]
    except KeyError:
        return

    if ext is ".data" and not basename.startswith("gfile"):
        return

    for key in rates:
        if key in basename:
            rate = rates[key]

    subprocess.call(["sox",
                     "-t", "raw",
                     "-b", str(bits),
                     "-c", str(channels),
                     "-e", bit_format,
                     "-r", "250000",
                     path,
                     "-n", "spectrogram",
                     "-c", "@" + str(rate),
                     "-z", str(dyn_range),
                     "-Z", str(peak),
                     "-x", str(width),
                     "-y", str(height),
                     "-o", outpath])


def main():
    """Parse arguments and create thumbnails."""
    parser = argparse.ArgumentParser(description="Create thumbnails for SDR"
                                     " data files.")
    parser.add_argument('--width', type=int, default=1024, help="Image width")
    parser.add_argument('--height', type=int, default=257, help="Image height")
    parser.add_argument('paths', type=str, nargs=1, help="Input paths."
                        " Directories will be proccesed recursively."
                        " Accepts .cu8 .cs8 .cs16 .s16 .cs32 .s32 .cf32 .f32"
                        " .cfile (cf32) and gfile*.data (cu8).")

    args = parser.parse_args()

    for path in args.paths:
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for name in files:
                    generate_thumbnail(os.path.join(root, name),
                                       args.width, args.height)
        else:
            generate_thumbnail(path, args.width, args.height)


if __name__ == '__main__':
    main()
