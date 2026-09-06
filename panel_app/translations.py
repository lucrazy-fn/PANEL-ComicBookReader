"""Helpers de tradução; o catálogo permanece em themes durante a migração."""
def translate(catalog,language,key,default=None): return catalog.get(language,{}).get(key,default or key)
