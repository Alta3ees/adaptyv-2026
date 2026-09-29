# Repository conventions

Every notebook must begin with this code cell as its very first cell (before
markdown or other code). Preserve this convention when creating or editing notebooks:

```python
from pathlib import Path
repo = Path("/content/adaptyv-2026")
if not repo.exists():
    !git clone https://github.com/Alta3ees/adaptyv-2026.git /content/adaptyv-2026
%cd /content/adaptyv-2026
```

This bootstrap targets Colab/IPython and clones the repository only when the
directory is absent.
