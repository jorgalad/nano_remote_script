# =============== DEFAULT (CLIP) MODE ===============
# TRACK <>      = SESSION UP/DOWN
# CYCLE         = LOOP ON/OFF
# SET           = TOGGLE LAUNCH QUANT    # Not in session framework anymore
# MARKER < >    = DEVICE LEFT/RIGHT
# << >>         = LAUNCH PREV/NEXT SCENE
# STOP          = STOP ALL CLIPS
# PLAY          = LAUNCH CURRENT SCENE
# REC           = GLOBAL RECORD

#MODE SPECIFIC
# ENCODERS      = PAN
# SLIDERS       = VOLUME
# SOLO          = SOLO
# MUTE          = MUTE
# RECORD        = RECORD ARM

# =============== SHIFT (DEVICE) MODE ===============
#MODE SPECIFIC
# ENCODERS      = DEVICE CONTROLS
# SLIDERS       = VOLUME
# SOLO          = SOLO
# MUTE          = MUTE
# RECORD        = RESET ALL DEVICE CONTROLS

chan = 0


num_tracks = 8
num_scenes = 4
GC = 0

setBtn = 60

sesUp = 58
sesDown = 59
cycleOn = 46


# SHIFT MODE CONSTS
track_solo_cc = [32, 33, 34, 35, 36, 37, 38, 39]
track_mute_cc = [48, 49, 50, 51, 52, 53, 54, 55]
track_arm_cc = [64, 65, 66, 67, 68, 69, 70, 71]

mixSend = [16, 17, 18, 19, 20, 21, 22, 23]
mixVol = [0, 1, 2, 3, 4, 5, 6, 7]