# The World in One Day — 26 November 2026

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![make.fun bounty](https://img.shields.io/badge/make.fun-news--image--20261126-orange.svg)](https://make.fun/bounty/news-image-20261126)

A front-page-style summary of Thursday 26 November 2026's world news in a
single 1024×1024 image, built for the make.fun bounty
[news-image-20261126](https://make.fun/bounty/news-image-20261126).

Try make.fun yourself: https://make.fun/r/n99wbh60

## The image

`main.py` draws the whole page from scratch — masthead, lead story, six
story cards, a ticker strip and a source line — using only the Python
standard library: its own 5×7 bitmap font and its own zlib PNG encoder.
No network, no external assets, no fonts on disk. Two runs write
byte-identical files.

Stories covered:

- **Lead — Washington:** the US proposes sweeping new tariffs on 14 trading partners
- **Egypt:** fuel tanker fire kills at least 31 on Cairo's ring road
- **Saudi Arabia:** Houthis strike Saudi oil heartland, including Ras Tanura
- **Ukraine:** Kyiv says it hit five jets at Russia's Savasleyka airbase
- **North Korea:** Kim orders a wider spread of tactical nuclear weapons
- **Space:** SpaceX cleared to launch up to a million satellites
- **United States:** Macy's 100th Thanksgiving parade postponed, a first

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png` (1024×1024, under 1 MiB). Without
`MAKEFUN_OUTPUT_DIR` it writes to `/output/entry.png`.

## License

MIT — see [LICENSE](LICENSE).
