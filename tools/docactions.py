import inspect
from src import tgbounce

methods = inspect.getmembers(tgbounce.Message,
                             predicate=lambda x: inspect.isfunction(x) and not x.__name__.startswith("_"))

for name, member in methods:
    cur_sig = inspect.signature(member)
    selfless_params = [param for param in cur_sig.parameters.values() if param.name != "self"]
    stripped_sig = cur_sig.replace(parameters=selfless_params)

    definition = f'- **{name}{stripped_sig}**: '
    doc = inspect.getdoc(member)

    if doc is not None:
        definition += doc
    else:
        definition += "No documentation available."

    print(definition)
