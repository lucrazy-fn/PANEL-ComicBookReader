def translate(catalog,language,key,default=None): return catalog.get(language,{}).get(key,default or key)
