# Invoke this function to prepare the dataset:
# $> .venv/bin/python3 -m app.datasets.synthetic_01 prepare

import yaml
import os
import json
import glob
import cv2
import numpy as np
from app.symbolic.MxlFile import MxlFile
from app.symbolic.Mxl2Msq import Mxl2Msq
from app.symbolic.split_part_to_systems import split_part_to_systems


IGNORED_SCORE_IDS = [
    # Does not contain piano part:
    8708253, # https://musescore.com/openscore-lieder-corpus/scores/8708253
    8708688, # https://musescore.com/openscore-lieder-corpus/scores/8708688
    8712405, # https://musescore.com/openscore-lieder-corpus/scores/8712405
    8712648, # https://musescore.com/openscore-lieder-corpus/scores/8712648
    8702982, # https://musescore.com/openscore-lieder-corpus/scores/8702982
    8718660, # https://musescore.com/openscore-lieder-corpus/scores/8718660
    6022950, # https://musescore.com/openscore-lieder-corpus/scores/6022950
    6023075, # https://musescore.com/openscore-lieder-corpus/scores/6023075
    6024601, # https://musescore.com/openscore-lieder-corpus/scores/6024601
    6034442, # https://musescore.com/openscore-lieder-corpus/scores/6034442
    6034473, # https://musescore.com/openscore-lieder-corpus/scores/6034473
    6034767, # https://musescore.com/openscore-lieder-corpus/scores/6034767
    5092551, # https://musescore.com/openscore-lieder-corpus/scores/5092551

    # Has three staves per system for piano
    6005658, # https://musescore.com/openscore-lieder-corpus/scores/6005658

    # Has four voices (on piano) written as four part lines, no pianoform here
    5908953, # https://musescore.com/openscore-lieder-corpus/scores/5908953

    # The piano is two monophonic staves, not one grandstaff
    4982535, # https://musescore.com/openscore-lieder-corpus/scores/4982535

    # Guitar part, one or two staves, complicated -> ignore
    # Also, may lack the grand-staff brace
    6598368, # https://musescore.com/openscore-lieder-corpus/scores/6598368
    6666995, # https://musescore.com/openscore-lieder-corpus/scores/6666995
    6158642, # https://musescore.com/openscore-lieder-corpus/scores/6158642
    6159296, # https://musescore.com/openscore-lieder-corpus/scores/6159296
    6159273, # https://musescore.com/openscore-lieder-corpus/scores/6159273
    6163298, # https://musescore.com/openscore-lieder-corpus/scores/6163298
    6158825, # https://musescore.com/openscore-lieder-corpus/scores/6158825
]
OS_CORPUS_PATH = "datasets/OpenScore-Lieder"
TEST_SCORES_YAML = "testset/test_scores.yaml"
DATASET_PATH = "datasets/synthetic_01"
MSCORE = "musescore/musescore.AppImage"
MS_CONVERSION_JSON = os.path.join(DATASET_PATH, "ms_conversion.json")


# extract this into a file
from svgelements import *
def find_systems_in_svg(
    svg_path: str,
    bracket_grow=1.1, # multiplier
    vertical_margin=0.5, # in the multiples of system height
    horizontal_margin=0.5 # in the multiples of system height
):
    with open(svg_path) as file:
        svg_file: SVG = SVG.parse(file, reify=True)
    
    # vertical pixel ranges (from-to) for system stafflines
    system_ranges = []
    for element in svg_file.elements():
        if element.values.get("class") == "Bracket":
            _, start, _, stop = element.bbox(with_stroke=True)
            height = stop - start
            start -= height * (1 - bracket_grow) / 2
            stop += height * (1 - bracket_grow) / 2
            system_ranges.append((start, stop))
    system_ranges.sort(key=lambda range: range[0])
    
    # sort stafflines into system bins
    system_stafflines = [[] for _ in system_ranges]
    for element in svg_file.elements():
        if element.values.get("class") == "StaffLines":
            _, y, _, _ = element.bbox()
            for i, (start, stop) in enumerate(system_ranges):
                if start <= y and y <= stop:
                    system_stafflines[i].append(element)
    
    # get system bounding boxes (tight)
    system_bboxes = [
        Group.union_bbox(stafflines)
        for stafflines in system_stafflines
    ]

    # get system crop boxes
    system_cropboxes = []
    for x1, y1, x2, y2 in system_bboxes:
        height = y2 - y1
        # grow by margin
        x1 -= horizontal_margin * height
        x2 += horizontal_margin * height
        y1 -= vertical_margin * height
        y2 += vertical_margin * height
        # hit page border
        x1 = max(x1, 0)
        y1 = max(y1, 0)
        x2 = min(x2, svg_file.width - 1)
        y2 = min(y2, svg_file.height - 1)
        # round to pixel
        system_cropboxes.append((
            int(x1), int(y1), int(x2), int(y2)
        ))

    return system_cropboxes


def prepare():
    with open(os.path.join(OS_CORPUS_PATH, "data/scores.yaml")) as f:
        corpus_scores = yaml.load(f, Loader=yaml.FullLoader)
    with open(TEST_SCORES_YAML) as f:
        test_scores = yaml.load(f, Loader=yaml.FullLoader)
    
    for score_id in IGNORED_SCORE_IDS:
        del corpus_scores[score_id]
    
    # TODO: split up the dataset into slices and run only one slice
    # in order to be parallelizable via slurm

    # DEBUG: reduce the size to something iterable
    # corpus_scores = dict(list(corpus_scores.items())[:10])
    
    # clear the dataset folder to get a fresh start
    assert os.system(f"rm -rf {DATASET_PATH}") == 0
    assert os.system(f"mkdir -p {DATASET_PATH}") == 0
    assert os.system(f"mkdir -p {DATASET_PATH}/svg") == 0
    assert os.system(f"mkdir -p {DATASET_PATH}/mxl") == 0
    assert os.system(f"mkdir -p {DATASET_PATH}/png") == 0
    
    # use musescore to create svg and mxl files
    conversion = []
    for suffix in ["mxl", "svg", "png"]:
        for score_id, score in corpus_scores.items():
            conversion.append({
                "in": os.path.join(
                    OS_CORPUS_PATH, "scores", score["path"], f"lc{score_id}.mscx"
                ),
                "out": os.path.join(
                    DATASET_PATH, suffix, f"{score_id}.{suffix}"
                )
            })
    
    with open(MS_CONVERSION_JSON, "w") as file:
        json.dump(conversion, file)
    
    assert os.system(f"{MSCORE} -j {MS_CONVERSION_JSON}") == 0
    
    # slice up the SVG into PNG pages
    for score_id in corpus_scores.keys():
        pattern = os.path.join(DATASET_PATH, "svg", f"{score_id}-*.svg")
        for svg_path in glob.glob(pattern):
            basename = os.path.basename(svg_path)
            page_number = int(basename[len(str(score_id))+1:-len(".svg")])
            png_path = svg_path.replace("svg", "png")
            
            print("Slicing to PNG:", svg_path, "...")
            system_cropboxes = find_systems_in_svg(svg_path)
            
            img = cv2.imread(png_path, cv2.IMREAD_UNCHANGED)
            img = 255 - img[:, :, 3] # alpha becomes black on white

            for i, (x1, y1, x2, y2) in enumerate(system_cropboxes):
                system_number = i + 1
                system_png_path = os.path.join(
                    DATASET_PATH, "samples", str(score_id),
                    f"p{page_number}-s{system_number}.png"
                )
                os.makedirs(os.path.dirname(system_png_path), exist_ok=True)
                system_img = img[y1:y2,x1:x2]
                cv2.imwrite(system_png_path, system_img)

    # convert MusicXML to MusicSequence (msq)
    msq_vocabulary = set()
    with open(os.path.join(DATASET_PATH, "msq_errors.txt"), "w") as errout:
        for score_id in corpus_scores.keys():
            mxl_path = os.path.join(DATASET_PATH, "mxl", f"{score_id}.mxl")

            print("Converting to MSQ:", mxl_path, "...")

            print("\n\n", file=errout)
            print("#" * (len(mxl_path) + 4), file=errout)
            print("# " + mxl_path + " #", file=errout)
            print("#" * (len(mxl_path) + 4), file=errout)
            
            mxl = MxlFile.load_mxl(mxl_path)
            part = mxl.get_piano_part()

            for (page_number, system_number), system in split_part_to_systems(part):
                convertor = Mxl2Msq(errout=errout)
                msq = convertor.process_part(system)
                msq_vocabulary.update(convertor.msq_tokens)
                
                msq_path = os.path.join(
                    DATASET_PATH, "samples", str(score_id),
                    f"p{page_number}-s{system_number}.msq"
                )
                os.makedirs(os.path.dirname(msq_path), exist_ok=True)
                with open(msq_path, "w") as file:
                    print(msq, file=file)

    with open(os.path.join(DATASET_PATH, "vocabulary.txt"), "w") as file:
        for token in sorted(msq_vocabulary):
            print(token, file=file)
    print(msq_vocabulary)
        