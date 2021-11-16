import pandas as pd
import re
from xml.etree import ElementTree as ET

def convert_dict(type_func, dict_to_convert):
    return {k:type_func(v)  for k,v in dict_to_convert.items()}

def make_type_df(result_list, chamber_type):
    return pd.DataFrame(list(filter(lambda x: x['type']==chamber_type, result_list)))

def create_geom_df(xmlfile):
    xmltree = ET.parse(xmlfile)
    root = xmltree.getroot()
    result_list = []
    for child in root:
        result_dict = {}
        for op_child in child:
            tag = op_child.tag
            if bool(re.match('.+Chamber', tag)):
                attrib_dict = convert_dict(int, op_child.attrib)
                result_dict = {**result_dict, **attrib_dict, 'type':tag}
            else:
                attrib_dict = op_child.attrib.pop('relativeto', None)
                attrib_dict = convert_dict(float, op_child.attrib)
                result_dict = {**result_dict, **attrib_dict}
        result_list.append(result_dict)
    
    dt_df = make_type_df(result_list, 'DTChamber')
    csc_df = make_type_df(result_list, 'CSCChamber')
    return dt_df, csc_df