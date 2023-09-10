#!/usr/bin/env python3

import numpy as np
import cv2
import os
import shutil
import argparse
import sys

PPP = {
    "w": 480,
    "h": 360
}

PP = {
    "w": 640,
    "h": 480
}

P = {
    "w": 1280,
    "h": 720
}

SIZE = {
    "360p": PPP,
    "480p": PP,
    "720p": P,
}

def hello(input):
    print(f'its work bro! {input}')

def print_progress_bar(index, total, label):
    n_bar = 50  # Progress bar width
    progress = index / total
    sys.stdout.write('\r')
    sys.stdout.write(f"[{'=' * int(n_bar * progress):{n_bar}s}] {int(100 * progress)}%  {label}")
    sys.stdout.flush()

# for next update :
# this settings is more realistic and lossless but huge output find better encoder or make it?
# this tool is so slowwwww, maybe find some better algo?
# im try using cv2.videowriter, but must find good encoder
def encode_fn(input, size, output, mask):
    f = open(input,'rb').read()
    ff = [f[i:i+int((SIZE[size]["w"]*SIZE[size]["h"])/8)] for i in range(0, len(f), int((SIZE[size]["w"]*SIZE[size]["h"])/8))]
    t_ff = len(ff)//30
    if t_ff == 0:
        tt_ff = 1
    elif t_ff > 60:
        tt_ff = (t_ff % 60) + 1
        t_ff = t_ff // 60
    else:
        tt_ff = t_ff + 1
        t_ff = 0

    if 'sq' not in os.listdir():
        os.mkdir('sq')
    else:
        shutil.rmtree('sq')
        os.mkdir('sq')
    os.system(f'ffmpeg -ss 0:0 -to {t_ff}:{tt_ff} -i {mask} -r 30 sq/frame%6d.png > /dev/null 2>&1')

    num = 1
    ll = 0
    os.mkdir('dq')
    for x in ff:
        res = ''
        for b in x:
            res += '0'*(8 - len(bin(b)[2:])) + bin(b)[2:]

        num2 = '0'*(6 - len(str(num))) + str(num)
        try:
            msk = cv2.imread(f'sq/frame{num2}.png')
        except:
            num = 1
            num2 = '0'*(6 - len(str(num))) + str(num)
            msk = cv2.imread(f'sq/frame{num2}.png')
            ll += 1

        bi = np.zeros((SIZE[size]["h"],SIZE[size]["w"],3), np.uint8)
        c = 0
        for col in range(0,SIZE[size]["h"]):
            for row in range(0,SIZE[size]["w"]):
                try:
                    val = msk[col, row]
                    var = val[2] % 2
                    if val[2] > 253:
                        val[2] = val[2] - 2
                    val[2] = val[2] + var + 1 if res[c] == '1' else val[2] + var
                    bi[col, row] = val
                    c += 1
                except:
                    break
        
        print_progress_bar(num, len(ff), "Encoding ...")
        num += 1
        if not ll:
            cv2.imwrite(f'dq/frame{num2}.png', bi)
        else:
            num2 = 'e'*ll + num2
            cv2.imwrite(f'dq/frame{num2}.png', bi)
    
    try:
        os.remove('output.mp4')
    except:
        pass

    os.system(f'ffmpeg -framerate 30 -i dq/frame%06d.png -c:v libx264rgb -crf 0 {output}.mp4 > /dev/null 2>&1')
    shutil.rmtree('dq')
    try:
        shutil.rmtree('sq')
    except:
        pass

def main():
    parser = argparse.ArgumentParser(
        prog="VaaS",
        description="List the content of a directory",
        epilog="Thanks for using %(prog)s! :)",
    )

    parser.add_argument('function',
                        help='You can use encode or decode or hello:D')
    parser.add_argument('-i', 
                        '--input',
                        metavar="FILE",
                        default=None, 
                        type=str, 
                        required=True,
                        help="Put your secret file for the storage")
    parser.add_argument('-m', 
                        '--mask',
                        metavar="FILE",
                        default=None, 
                        type=str,
                        help="Put your mask for the storage")
    parser.add_argument('-o', 
                        '--output',
                        default='output', 
                        type=str, 
                        help="Name for the result video .avi")
    parser.add_argument('-s', 
                        '--size',
                        default='720p', 
                        type=str, 
                        help="Resolution for result video (360p / 480p / 720p)")
    
    args = parser.parse_args()
    if args.function is None:
        parser.error("Please select a function to run")
    match args.function:
        case "hello":
            hello(args.input)
        case "encode":
            if args.mask is None:
                parser.error("Please select a video to be a mask")
            encode_fn(args.input, args.size, args.output, args.mask)
        case "decode":
            print("maybe after this final:D")

main()