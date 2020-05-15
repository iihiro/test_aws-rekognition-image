#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import json
from PIL import Image, ImageDraw
import boto3

def detect_faces(filepath):
    cli = boto3.client('rekognition')

    with open(filepath, 'rb') as img:
        res = cli.detect_faces(Image={'Bytes': img.read()}, Attributes=['ALL'])
        #res = cli.detect_faces(Image={'Bytes': img.read()})

    print('Detected faces for ' + filepath)

    #for face in res['FaceDetails']:
    #    print('The detected face is between ' + str(face['AgeRange']['Low']) 
    #          + ' and ' + str(face['AgeRange']['High']) + ' years old')
    #    print('Here are the other attributes:')
    #    print(json.dumps(face, indent=4, sort_keys=True))

    return len(res['FaceDetails']), res

def convBB_awsbb2px(awsbb, imgW_px, imgH_px):
    """
    convert bounding box from AWS format to pixel

    AWS format:

    {
        "Height": 0.39612752199172974,
        "Left": 0.3137926757335663,
        "Top": 0.1848856657743454,
        "Width": 0.42014431953430176
    }

    ** each value is ratio of the overall image size **
    """
    print('(%f, %f, %f, %f)' % (float(awsbb["Left"]),
                                float(awsbb["Top"]),
                                float(awsbb["Width"]),
                                float(awsbb["Height"])))
    return [int(imgW_px * float(awsbb["Left"])),
            int(imgH_px * float(awsbb["Top"])),
            int(imgW_px * float(awsbb["Width"])),
            int(imgH_px * float(awsbb["Height"]))]

def drawBB(in_filepath, out_filepath, bb_arry, col=(0,128,0)):
    with Image.open(in_filepath) as img:
        draw = ImageDraw.Draw(img)
        for bb in bb_arry:
            #draw.rectangle(bb, outline = col)
            tl = [bb[0], bb[1]]
            br = [bb[0] + bb[2], bb[1] + bb[3]]
            draw.rectangle((tl[0], tl[1], br[0], br[1]), outline = col, width=2)
        img.save(out_filepath)
    
def main(filepath):
    cnt, res = detect_faces(filepath)

    bb_arry = []
    for face in res['FaceDetails']:
        dic = json.dumps(face)
        with Image.open(filepath) as img:
            imgW_px, imgH_px = img.size
        print('imgWH: (%d, %d)' % (imgW_px, imgH_px))
        bb = convBB_awsbb2px(face['BoundingBox'], imgW_px, imgH_px)
        bb_arry.append(bb)
        print(bb)
        
    splitpath    = os.path.splitext(filepath)
    out_filepath = splitpath[0] + '_out' + splitpath[1]
    drawBB(filepath, out_filepath, bb_arry)
        
    print('Faces detected: ' + str(cnt))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=u"aws-rekog-image test")
    ap.add_argument("-i", "--input_file", help="input image file (*.jpg, *.png)")
    args = ap.parse_args()
    
    main(args.input_file)
