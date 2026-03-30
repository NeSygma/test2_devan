#!/usr/bin/env python3
"""
Reference model for the Two-Part Counterpoint Composition problem.
Validates a composition against a set of music theory rules.
"""

import json
import sys

NOTE_TO_MIDI = {
    'C0': 12, 'D0': 14, 'E0': 16, 'F0': 17, 'G0': 19, 'A0': 21, 'B0': 23,
    'C1': 24, 'D1': 26, 'E1': 28, 'F1': 29, 'G1': 31, 'A1': 33, 'B1': 35,
    'C2': 36, 'D2': 38, 'E2': 40, 'F2': 41, 'G2': 43, 'A2': 45, 'B2': 47,
    'C3': 48, 'D3': 50, 'E3': 52, 'F3': 53, 'G3': 55, 'A3': 57, 'B3': 59,
    'C4': 60, 'D4': 62, 'E4': 64, 'F4': 65, 'G4': 67, 'A4': 69, 'B4': 71,
    'C5': 72, 'D5': 74, 'E5': 76, 'F5': 77, 'G5': 79, 'A5': 81, 'B5': 83,
    'C6': 84, 'D6': 86, 'E6': 88, 'F6': 89, 'G6': 91, 'A6': 93, 'B6': 95,
}
C_MAJOR_SCALE = {'C', 'D', 'E', 'F', 'G', 'A', 'B'}
CONSONANT_INTERVALS = {3, 4, 7, 8, 9, 12, 15, 16} # m3, M3, P5, m6, M6, P8, m10, M10
V_CHORD_NOTES = {'G', 'B', 'D'}
I_CHORD_NOTES = {'C', 'E', 'G'}

def validate_solution(solution):
    """Validates the two-part composition."""
    if not isinstance(solution, dict) or "composition" not in solution:
        return False, "Invalid JSON structure: 'composition' field missing."

    comp = solution.get("composition")
    if not isinstance(comp, list) or len(comp) != 8:
        return False, f"Composition must be a list of 8 time steps, got {len(comp)}."

    sop_notes, alto_notes = [], []
    sop_midis, alto_midis = [], []
    h_intervals = []

    for i, step in enumerate(comp):
        if step.get("time") != i + 1:
            return False, f"Time step {i+1} has incorrect 'time' field."

        for key in ["soprano_note", "alto_note", "harmonic_interval_semitones"]:
            if key not in step:
                return False, f"Missing key '{key}' in time step {i+1}."

        sop_note, alto_note = step["soprano_note"], step["alto_note"]
        if sop_note not in NOTE_TO_MIDI or alto_note not in NOTE_TO_MIDI:
            return False, f"Invalid note name found in step {i+1}."

        if sop_note[0] not in C_MAJOR_SCALE or alto_note[0] not in C_MAJOR_SCALE:
            return False, f"Note not in C Major scale in step {i+1}."

        sop_midi, alto_midi = NOTE_TO_MIDI[sop_note], NOTE_TO_MIDI[alto_note]
        sop_notes.append(sop_note); sop_midis.append(sop_midi)
        alto_notes.append(alto_note); alto_midis.append(alto_midi)

        # Rule: No voice crossing
        if sop_midi <= alto_midi:
            return False, f"Voice crossing at step {i+1}: Soprano({sop_midi}) <= Alto({alto_midi})."

        # Rule: Harmonic intervals
        h_int = sop_midi - alto_midi
        if h_int != step["harmonic_interval_semitones"]:
            return False, f"Incorrect harmonic interval at step {i+1}."
        if h_int not in CONSONANT_INTERVALS:
            return False, f"Dissonant harmonic interval {h_int} at step {i+1}."
        h_intervals.append(h_int)

    # Rule: Voice Ranges
    sop_range = (NOTE_TO_MIDI['C4'], NOTE_TO_MIDI['A5'])
    alto_range = (NOTE_TO_MIDI['E3'], NOTE_TO_MIDI['C5'])
    if not (sop_range[0] <= min(sop_midis) and max(sop_midis) <= sop_range[1]):
        return False, "Soprano voice out of range."
    if not (alto_range[0] <= min(alto_midis) and max(alto_midis) <= alto_range[1]):
        return False, "Alto voice out of range."

    # Rule: Melodic leaps
    for i in range(7):
        if abs(sop_midis[i+1] - sop_midis[i]) > 7:
            return False, f"Soprano melodic leap > P5 at step {i+2}."
        if abs(alto_midis[i+1] - alto_midis[i]) > 7:
            return False, f"Alto melodic leap > P5 at step {i+2}."

    # Rule: Parallel P5/P8
    for i in range(7):
        if h_intervals[i] in {7, 12} and h_intervals[i] == h_intervals[i+1]:
            return False, f"Parallel {h_intervals[i]} at steps {i+1}-{i+2}."

    # Rule: Start
    if not (alto_notes[0] == 'C4' and sop_notes[0] in ['E4', 'G4']):
        return False, "Invalid starting notes."

    # Rule: Cadence
    if sop_notes[6][0] not in V_CHORD_NOTES or alto_notes[6][0] not in V_CHORD_NOTES:
        return False, "Step 7 notes do not form a V-chord."
    if not (sop_notes[7] == 'C5' and alto_notes[7] == 'C4'):
        return False, "Final chord is not a C5/C4 octave."

    return True, "Valid two-part composition"

def main():
    try:
        solution = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        print(json.dumps({"valid": False, "message": "Invalid or empty JSON input."}))
        return

    is_valid, message = validate_solution(solution)
    print(json.dumps({"valid": is_valid, "message": message}))

if __name__ == "__main__":
    main()
