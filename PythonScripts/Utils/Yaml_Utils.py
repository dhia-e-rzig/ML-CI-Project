def find_langs(yml):
    langs=set()
    if yml is None:
        return langs
    for k,v in yml.items():
        if str(k).lower() == "language":
            if isinstance(v, list):
                for a in v:
                    langs.add(a)
            else:
                langs.add(v)
        elif  isinstance(v, dict):
            langs.update(find_langs(v))
    return langs
