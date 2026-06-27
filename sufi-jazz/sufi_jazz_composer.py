"""
Sufi-Jazz Composition Generator
Produces a raw MIDI file using Python's struct module (no external deps).

Musical design:
- Maqam Hijaz scale (D, Eb, F#, G, A, Bb, C, D) – classic Sufi/Middle-Eastern flavour
- Slow tempo: 68 BPM
- Jazz harmony: Dm(maj7), Gm9, Bbmaj7#11, A7b9 voicings in the bass/chord track
- Three tracks: lead melody (ney-like), chord pads, walking bass
"""

import struct, os

# ── MIDI low-level helpers ──────────────────────────────────────────────────

def var_len(value):
    """Encode integer as MIDI variable-length quantity."""
    result = [value & 0x7F]
    value >>= 7
    while value:
        result.insert(0, (value & 0x7F) | 0x80)
        value >>= 7
    return bytes(result)

def note_on(channel, pitch, velocity, delta=0):
    return var_len(delta) + bytes([0x90 | channel, pitch, velocity])

def note_off(channel, pitch, delta=0):
    return var_len(delta) + bytes([0x80 | channel, pitch, 0])

def program_change(channel, program, delta=0):
    return var_len(delta) + bytes([0xC0 | channel, program])

def tempo_event(bpm):
    uspb = int(60_000_000 / bpm)
    return b'\x00\xFF\x51\x03' + struct.pack('>I', uspb)[1:]

def time_sig(num, den_power):
    return b'\x00\xFF\x58\x04' + bytes([num, den_power, 24, 8])

def end_of_track():
    return b'\x00\xFF\x2F\x00'

def make_track(events_bytes):
    data = b''.join(events_bytes)
    return b'MTrk' + struct.pack('>I', len(data)) + data

def make_header(num_tracks, ppq=480):
    return b'MThd\x00\x00\x00\x06\x00\x01' + struct.pack('>HH', num_tracks, ppq)

# ── Musical constants ───────────────────────────────────────────────────────

PPQ   = 480   # ticks per quarter note
BPM   = 68
TICKS_BEAT = PPQ
TICKS_BAR  = PPQ * 4   # 4/4

# Maqam Hijaz on D: D Eb F# G A Bb C D
# MIDI pitches (octave 4 starts at 60)
HIJAZ_D = [62, 63, 66, 67, 69, 70, 72, 74]   # D4..D5
HIJAZ_LOW = [x - 12 for x in HIJAZ_D]         # D3..D4

def p(name):
    """Named pitch helper."""
    names = {'C3':48,'D3':50,'Eb3':51,'F3':53,'F#3':54,'G3':55,'A3':57,'Bb3':58,'C4':60,
             'D4':62,'Eb4':63,'F4':65,'F#4':66,'G4':67,'A4':69,'Bb4':70,'C5':72,'D5':74,
             'Eb5':75,'F5':77,'F#5':78,'G5':79,'A5':81,'Bb5':82,'C6':84}
    return names[name]

# ── Track 1: Lead melody (channel 0, program 73 = Flute / ney-like) ─────────

def melody_track():
    events = [
        program_change(0, 73),          # Flute
        tempo_event(BPM),
        time_sig(4, 2),                 # 4/4
    ]

    # Phrase A – 4 bars, contemplative ascent
    phrase_a = [
        # bar 1
        (p('D4'),  PPQ*2,  60),
        (p('Eb4'), PPQ,    55),
        (p('F#4'), PPQ,    58),
        # bar 2
        (p('G4'),  PPQ*3,  65),
        (p('A4'),  PPQ,    60),
        # bar 3
        (p('Bb4'), PPQ*2,  62),
        (p('A4'),  PPQ,    58),
        (p('G4'),  PPQ,    55),
        # bar 4
        (p('F#4'), PPQ*2,  60),
        (p('Eb4'), PPQ,    55),
        (p('D4'),  PPQ,    50),
    ]

    # Phrase B – 4 bars, jazzy chromatic touch
    phrase_b = [
        # bar 5
        (p('D4'),  PPQ,    55),
        (p('Eb4'), PPQ,    60),
        (p('F#4'), PPQ,    65),
        (p('G4'),  PPQ,    68),
        # bar 6
        (p('A4'),  PPQ*2,  70),
        (p('Bb4'), PPQ,    65),
        (p('C5'),  PPQ,    60),
        # bar 7
        (p('D5'),  PPQ*3,  72),
        (p('C5'),  PPQ,    65),
        # bar 8 – cadence back to D
        (p('Bb4'), PPQ,    60),
        (p('A4'),  PPQ,    58),
        (p('G4'),  PPQ,    55),
        (p('F#4'), PPQ,    52),
    ]

    # Phrase C – ornamented variation (2× for depth)
    phrase_c = [
        # bar 9
        (p('Eb4'), PPQ//2, 62),
        (p('D4'),  PPQ//2, 58),
        (p('Eb4'), PPQ,    65),
        (p('F#4'), PPQ,    68),
        (p('G4'),  PPQ,    65),
        # bar 10
        (p('A4'),  PPQ*2,  70),
        (p('Bb4'), PPQ,    65),
        (p('A4'),  PPQ,    60),
        # bar 11
        (p('G4'),  PPQ,    58),
        (p('F#4'), PPQ,    55),
        (p('Eb4'), PPQ*2,  52),
        # bar 12
        (p('D4'),  PPQ*4,  60),
    ]

    # Repeat structure: A A B A C A (24 bars total)
    full = phrase_a + phrase_a + phrase_b + phrase_a + phrase_c + phrase_a

    cursor = 0
    for pitch, dur, vel in full:
        events.append(note_on(0, pitch, vel, delta=0))
        events.append(note_off(0, pitch, delta=dur))
    events.append(end_of_track())
    return make_track(events)

# ── Track 2: Jazz chord pads (channel 1, program 89 = Pad warm) ─────────────

def chord_voicings():
    """Returns list of (chord_notes_list, dur_ticks) per bar × 24."""
    # Dm(maj7): D F A C#  → jazz: D F A C (Dm7 softened)
    # Gm9: G Bb D F A
    # Bbmaj7: Bb D F A
    # A7b9: A C# E G Bb
    dm7  = [p('D3'), p('F3'), p('A3'), p('C4')]
    gm9  = [p('G3'), p('Bb3'), p('D4'), p('F4')]
    bbm7 = [p('Bb3'), p('D4'), p('F4'), p('A4')]
    a7b9 = [p('A3'), p('C4'), p('Eb4'), p('G4')]   # A7b9 (Eb=b9)

    # 24-bar progression (1 chord per bar mostly)
    prog = [
        dm7, dm7, gm9, dm7,    # bars 1-4
        dm7, dm7, gm9, a7b9,   # bars 5-8
        dm7, gm9, bbm7, dm7,   # bars 9-12
        dm7, dm7, gm9, dm7,    # bars 13-16 (repeat A)
        dm7, gm9, bbm7, a7b9,  # bars 17-20
        dm7, gm9, a7b9, dm7,   # bars 21-24 (outro)
    ]
    return [(chord, TICKS_BAR) for chord in prog]

def chord_track():
    events = [program_change(1, 89)]   # Pad warm

    for chord, dur in chord_voicings():
        # Stagger attack (arpeggiate slightly) for organic feel
        stagger = PPQ // 8
        events.append(note_on(1, chord[0], 45, delta=0))
        for n in chord[1:]:
            events.append(note_on(1, n, 42, delta=stagger))
        # Hold for bar length minus stagger overhead
        hold = dur - stagger * (len(chord) - 1) - stagger
        events.append(note_off(1, chord[0], delta=hold))
        for n in chord[1:]:
            events.append(note_off(1, n, delta=stagger))

    events.append(end_of_track())
    return make_track(events)

# ── Track 3: Walking bass (channel 2, program 32 = Acoustic Bass) ───────────

def bass_track():
    events = [program_change(2, 32)]

    # Simple quarter-note walking lines per bar
    # Each bar: list of (pitch, vel)
    bars = [
        [(p('D3'),55),(p('F3'),50),(p('A3'),52),(p('C4'),48)],   # Dm7
        [(p('D3'),55),(p('Eb3'),50),(p('F3'),52),(p('A3'),50)],  # Dm7 var
        [(p('G3'),55),(p('Bb3'),52),(p('D4'),50),(p('F4'),48)],  # Gm9
        [(p('D3'),55),(p('A3'),50),(p('F3'),52),(p('D3'),48)],   # Dm7
        [(p('D3'),55),(p('F3'),50),(p('A3'),52),(p('C4'),48)],
        [(p('D3'),55),(p('Eb3'),50),(p('F3'),52),(p('G3'),50)],
        [(p('G3'),55),(p('Bb3'),52),(p('D4'),50),(p('A3'),48)],
        [(p('A3'),55),(p('C4'),52),(p('Eb4'),50),(p('G3'),48)],  # A7b9
        [(p('D3'),55),(p('F3'),50),(p('A3'),52),(p('C4'),48)],
        [(p('G3'),55),(p('Bb3'),52),(p('D4'),50),(p('F4'),48)],
        [(p('Bb3'),55),(p('D4'),52),(p('F4'),50),(p('A4'),48)],
        [(p('D3'),55),(p('A3'),50),(p('F3'),52),(p('D3'),48)],
        [(p('D3'),55),(p('F3'),50),(p('A3'),52),(p('C4'),48)],
        [(p('D3'),55),(p('Eb3'),50),(p('F3'),52),(p('A3'),50)],
        [(p('G3'),55),(p('Bb3'),52),(p('D4'),50),(p('F4'),48)],
        [(p('D3'),55),(p('A3'),50),(p('F3'),52),(p('D3'),48)],
        [(p('D3'),55),(p('F3'),50),(p('A3'),52),(p('C4'),48)],
        [(p('G3'),55),(p('Bb3'),52),(p('D4'),50),(p('F4'),48)],
        [(p('Bb3'),55),(p('D4'),52),(p('F4'),50),(p('A4'),48)],
        [(p('A3'),55),(p('C4'),52),(p('Eb4'),50),(p('G3'),48)],
        [(p('D3'),55),(p('F3'),50),(p('A3'),52),(p('C4'),48)],
        [(p('G3'),55),(p('Bb3'),52),(p('D4'),50),(p('F4'),48)],
        [(p('A3'),55),(p('C4'),52),(p('Eb4'),50),(p('G3'),48)],
        [(p('D3'),60),(p('D3'),55),(p('D3'),50),(p('D3'),45)],   # final bar
    ]

    for bar in bars:
        for pitch, vel in bar:
            events.append(note_on(2, pitch, vel, delta=0))
            events.append(note_off(2, pitch, delta=PPQ - PPQ//8))
            # tiny gap between bass notes
            events.append(note_on(2, pitch, 0, delta=PPQ//8))   # silence filler (vel 0 = off)

    events.append(end_of_track())
    return make_track(events)

# ── Assemble & write ────────────────────────────────────────────────────────

out_path = '/tmp/claude-0/-home-user-Claude-Skills/7958c1be-0230-515c-a482-36da17e1334d/scratchpad/sufi_jazz_composition.mid'

tracks = [melody_track(), chord_track(), bass_track()]
midi = make_header(len(tracks), PPQ) + b''.join(tracks)

with open(out_path, 'wb') as f:
    f.write(midi)

print(f"MIDI written → {out_path}  ({len(midi)} bytes)")
EOF
