[![make.fun · the-catalogue-photo-of-an-2-20261121-0341](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341.svg)](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341?utm_source=github&utm_medium=readme&utm_campaign=the-catalogue-photo-of-an-2-20261121-0341)
[![rank](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341/yuyan5319-crypto/makefun-the-catalogue-photo-of-an-2-20261121-0341/rank.svg)](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-catalogue-photo-of-an-2-20261121-0341)
[![reward](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341/yuyan5319-crypto/makefun-the-catalogue-photo-of-an-2-20261121-0341/reward.svg)](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341?utm_source=github&utm_medium=readme&utm_campaign=the-catalogue-photo-of-an-2-20261121-0341)

# The Catalogue Photo of an Impossible Gadget — SOCKMATIC

A studio catalogue photograph of an impossible gadget, drawn procedurally
with Python (PIL + numpy, no network, no external assets).

**The gadget:** the SOCKMATIC 2-Slice Sock Toaster — a chrome two-slice
toaster with two cream socks popping out of its slots, mid-toast, golden-brown
at the bottoms, thin steam curling up. The brand plate reads "SOCKMATIC /
2-SLICE SOCK TOASTER". Exactly one accessory sits on the floor to the right:
a neat stack of three folded socks waiting their turn.

## Run

```sh
python3 main.py
```

Writes one image to `/output/entry.png` (1024×1024 JPEG, under 1 MiB).
Runs in a few seconds; output is deterministic (fixed seed).

## How it is made

`main.py` renders the scene at 2048×2048 — warm grey seamless studio
backdrop with a radial glow, floor line, contact shadow, brushed-metal
toaster body with specular highlight, knitted socks with ribbed cuffs, red
stripes and toasted browning, steam wisps, dial, lever and brand plate —
then downscales to 1024×1024 with LANCZOS, adds faint film grain and a
subtle vignette, and saves as JPEG quality 88.
