"""Estado persistente específico do leitor."""
import os
from .storage import APPDATA_DIR,json_load,json_save
STATE_FILE=os.path.join(APPDATA_DIR,"reader_state.json")
def load_state(content_key): return json_load(STATE_FILE,{}).get(content_key,{})
def save_state(content_key,**state):
    data=json_load(STATE_FILE,{}); current=data.get(content_key,{}); current.update(state); data[content_key]=current; json_save(STATE_FILE,data)
