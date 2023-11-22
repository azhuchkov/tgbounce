# Developer Guide

## Generate supported actions list

```bash
python -c 'import inspect; import tgbounce; print("\n".join(f"{name}{inspect.signature(method)}" for name, method in inspect.getmembers(tgbounce.Message, predicate=lambda x: inspect.isfunction(x) and not x.__name__.startswith("_"))))' \
  | sed -E 's/self(,[ ])?//'
```