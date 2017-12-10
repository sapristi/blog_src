page = {"type" : "default"}
import re

def hook_preconvert_link_path():
    
    for p in pages:
        if "path" in p:
            path = p["path"]
            
            p.source = re.sub(
                "\[(.*?)\]\((.*?)\)",
                lambda matchobj :
                "[" + matchobj.group(1) + "](/" +
                path + "/" + matchobj.group(2)+ ")",
                p.source)
            
