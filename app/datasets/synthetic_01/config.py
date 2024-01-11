LIEDER_CORPUS_PATH = "datasets/OpenScore-Lieder"
DATASET_PATH = "datasets/synthetic_01"
MSCORE = "musescore/musescore.AppImage"
TESTSET_SCORES_YAML = "testset/test_scores.yaml"

IGNORED_SCORE_IDS = [
    # Do not contain piano part:
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

    # contains piano brace for non-piano parts
    # --> it's hard to crop out the piano part
    6681689, # https://musescore.com/openscore-lieder-corpus/scores/6681689
    6690090, # https://musescore.com/openscore-lieder-corpus/scores/6690090
    6683493, # https://musescore.com/openscore-lieder-corpus/scores/6683493
    6684909, # https://musescore.com/openscore-lieder-corpus/scores/6684909
    6550942, # https://musescore.com/openscore-lieder-corpus/scores/6550942
    6688667, # https://musescore.com/openscore-lieder-corpus/scores/6688667

    # lacks piano bracket for the piano system
    6214840, # https://musescore.com/openscore-lieder-corpus/scores/6214840

    # contains a music-less page in the middle of the piece
    # (cant be found from the MusicXML)
    6010628, # https://musescore.com/openscore-lieder-corpus/scores/6010628

    # contains broken system on one line (page 2), breaks PNG cropping
    6177442, # https://musescore.com/openscore-lieder-corpus/scores/6177442

    # contains a piano brace on a text page
    # (muse score rendering error?)
    5907870, # https://musescore.com/openscore-lieder-corpus/scores/5907870

    # contains invisible piano sections that cannot be found in the MusicXML
    # (can be found, it's just that there's no information about them being invisible)
    # (they just contain measure-rests, but those might as well be visible)
    6593095, # https://musescore.com/openscore-lieder-corpus/scores/6593095
    6625925, # https://musescore.com/openscore-lieder-corpus/scores/6625925
    6624112, # https://musescore.com/openscore-lieder-corpus/scores/6624112
    6613355, # https://musescore.com/openscore-lieder-corpus/scores/6613355
    6613436, # https://musescore.com/openscore-lieder-corpus/scores/6613436
    6613481, # https://musescore.com/openscore-lieder-corpus/scores/6613481
    6614717, # https://musescore.com/openscore-lieder-corpus/scores/6614717
    6614760, # https://musescore.com/openscore-lieder-corpus/scores/6614760
    6667483, # https://musescore.com/openscore-lieder-corpus/scores/6667483
    6669339, # https://musescore.com/openscore-lieder-corpus/scores/6669339
    6670960, # https://musescore.com/openscore-lieder-corpus/scores/6670960
    6162644, # https://musescore.com/openscore-lieder-corpus/scores/6162644
]
