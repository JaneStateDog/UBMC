import os
import UnityPy
from typing import Dict
import json


ROOT = os.path.dirname(os.path.realpath(__file__))
TYPETREE_GENERATOR_PATH = os.path.join(ROOT, "TypeTreeGenerator")



def main(thingsToGet: list, asset_path: str, dll_folder: str, assets_to_use: list):

    trees = dump_assembly_trees(dll_folder)

    #thingsToGet = ["BeatmapIndex", "10940"]
    #assets_to_use = ["resources.assets", "resources.assets.resS"]

    export_monobehaviours(asset_path, trees, dll_folder, thingsToGet, assets_to_use)




def export_monobehaviours(asset_path: str, trees: dict, dll_folder, thingsToGet: list, assets_to_use: list):
    pythonnet_init()
    g = create_generator(dll_folder)
    for r, d, fs in os.walk(asset_path):
        for f in fs:

            if str(f) not in assets_to_use:
                continue
            
            try:
                env = UnityPy.load(os.path.join(r, f))
            except:
                continue
            for obj in env.objects:
                if obj.type == "MonoBehaviour":

                    d = obj.read()
                    name = d.name

                    if name == "":
                        name = str(d.path_id)

                    if name not in thingsToGet:
                        continue
                        
                    if obj.serialized_type.nodes:
                        tree = obj.read_typetree()
                    else:
                        if not d.m_Script:
                            continue

                        script = d.m_Script.read()
                        nodesForDump = generate_tree(g, script.m_AssemblyName, script.m_ClassName, script.m_Namespace)

                        if script.m_ClassName not in trees:
                            continue

                        nodes = [FakeNode(**X) for X in trees[script.m_ClassName]]
                        tree = obj.read_typetree(nodes)

                        with open(os.path.join(ROOT, f"out\\{name}Nodes.json"), "w") as testFile:
                            json.dump(nodesForDump, testFile, ensure_ascii=False, indent = 4)

                
                    with open(os.path.join(ROOT, f"out\\{name}.json"), "wt", encoding="utf8") as testFile:
                        json.dump(tree, testFile, ensure_ascii=False, indent = 4)
                    
                    

def dump_assembly_trees(dll_folder: str):

    pythonnet_init()

    g = create_generator(dll_folder)
    trees = generate_tree(g, "Assembly-CSharp.dll", "", "")

    return trees



def pythonnet_init():

    from clr_loader import get_coreclr
    from pythonnet import set_runtime

    rt = get_coreclr(os.path.join(TYPETREE_GENERATOR_PATH, "TypeTreeGenerator.runtimeconfig.json"))
    set_runtime(rt)


def create_generator(dll_folder: str):

    import sys

    sys.path.append(TYPETREE_GENERATOR_PATH)

    import clr

    clr.AddReference("TypeTreeGenerator")
    from Generator import Generator

    g = Generator()
    g.loadFolder(dll_folder)

    return g


class FakeNode:
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)


def generate_tree(g: "Generator", assembly: str, class_name: str, namespace: str, unity_version=[2019, 2, 0, 1]) -> Dict[str, Dict]:
    from System import Array

    unity_version_cs = Array[int](unity_version)
    def_iter = g.getTypeDefs(assembly, class_name, namespace)

    trees = {}
    for d in def_iter:
        try:
            nodes = g.convertToTypeTreeNodes(d, unity_version_cs)
        except Exception as e:
            print(d.Name, e)
            continue
        trees[d.Name] = [{"level" : node.m_Level, "type" : node.m_Type, "name" : node.m_Name, "meta_flag" : node.m_MetaFlag} for node in nodes]

    return trees

