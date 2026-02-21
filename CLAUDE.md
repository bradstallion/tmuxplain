# tmux-navigator

## Stack
- Python 3.10+, Textual

## Struttura
- `tmux.py` — tutti i subprocess tmux, nessuna logica UI qui
- `app.py` — schermate e widget Textual
- `config.py` — config TOML, no hardcoded defaults altrove

## Convenzioni
- Niente libtmux, solo subprocess
- Ogni azione tmux deve gestire gracefully il caso "tmux non installato"
- Il footer si aggiorna contestualmente alla schermata attiva

## Test
- `python -m pytest tests/`

Usa il virtualenv già presente in venv3.
