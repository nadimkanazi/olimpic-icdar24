from ..linearization.Delinearizer import Delinearizer
from .TEDn import TEDn, TEDnResult
from ..symbolic.Pruner import Pruner
from ..symbolic.actual_durations_to_fractional import actual_durations_to_fractional
from ..symbolic.debug_compare import compare_parts
import xml.etree.ElementTree as ET
from typing import TextIO, Optional
import traceback


def TEDn_lmx_xml(
    predicted_lmx: str,
    gold_musicxml: str,
    prune=True,
    debug=False,
    errout: Optional[TextIO] = None
) -> TEDnResult:
    # remove whitespace from gold XML
    # THIS IS IMPORTANT!
    # TEDn as is currently implemented introduces some error when
    # whitespace is not stripped. Maybe whitespace between elements? IDK...
    gold_musicxml = ET.canonicalize(
        gold_musicxml,
        strip_text=True
    )

    # prepare gold data
    gold_score = ET.fromstring(gold_musicxml)
    assert gold_score.tag == "score-partwise"
    gold_parts = gold_score.findall("part")
    assert len(gold_parts) == 1
    gold_part = gold_parts[0]
    actual_durations_to_fractional(gold_part) # evaluate in fractional durations

    # prepare predicted data
    try:
        delinearizer = Delinearizer(
            errout=errout,
            keep_fractional_durations=True # evaluate in fractional durations
        )
        delinearizer.process_text(predicted_lmx)
        predicted_part = delinearizer.part_element
    except Exception:
        # should not happen, unless there's a bug in the delinearizer
        if errout is not None:
            print("DELINEARIZATION CRASHED:", traceback.format_exc(), file=errout)
        predicted_part = ET.Element("part")
    
    # prune down to the elements that we actually predict
    # (otherwise TEDn penalizes missing <direction> and various ornaments)
    if prune:
        pruner = Pruner(
            
            # these are acutally also ignored by TEDn
            prune_durations=False, # MUST BE FALSE! Is used in backups and forwards
            prune_measure_attributes=False,
            prune_prints=True,
            prune_slur_numbering=True,

            # these measure elements are not encoded in LMX, prune them
            prune_directions=True,
            prune_barlines=True,
            prune_harmony=True,
            
            # LMX encodes time-modification in the reduced form,
            # so this information is actually lost by design
            reduce_time_modification=True,

            # tremolos should have their number encoded in some future
            # LMX version, that is a valid error to be counted
            prune_tremolo_marks=False,
            
        )
        pruner.process_part(gold_part)
        pruner.process_part(predicted_part)

    if debug:
        compare_parts(expected=gold_part, given=predicted_part)

    return TEDn(predicted_part, gold_part)
    # return TEDnResult(1, 1, 1)