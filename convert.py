# -*- coding: utf-8 -*-
"""
Convert LEMS and NeuroML schema definitions from xsd to rng and rnc
formats.
"""
import subprocess
import os.path
from pkg_resources import resource_string

def insert_string(in_string, separator, string_to_insert):
    first_half, second_half = in_string.split(separator, 1)
    out_string = ''.join([first_half,
                          separator,
                          string_to_insert,
                          second_half])
    return out_string

def insert_string_in_file(filename, separator, string_to_insert):
    with open(filename) as f:
        in_string = f.read()
    out_string = insert_string(in_string,
                               separator,
                               string_to_insert)
    with open(filename, "w") as f:
        f.write(out_string)

def main(xsd_filename, rnc_filename=None):
    """convert LEMS/NeuroML xsd schema to rng and rnc formats"""
    base_name = os.path.splitext(os.path.split(xsd_filename)[1])[0]
    if not rnc_filename:
        rng_filename = base_name + ".rng"
        rnc_filename = base_name + ".rnc"
    else:
        rng_filename = os.path.splitext(rnc_filename)[0] + ".rng"

    # load XSDtoRNG.xsl stylesheet as a resource string
    xsdtorng_resource = resource_string(__name__, "resources/XSDtoRNG.xsl")
    # perform automatic xsl transformation: xsd -> rng using xsltproc
    # (note that the stylesheet contents are passed as a string
    # through stdin)
    p = subprocess.Popen(["xsltproc -o {} - {}".format(rng_filename,
                                                       xsd_filename)],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         shell=True)
    xsltproc_stdout = p.communicate(input=xsdtorng_resource)
    print(xsltproc_stdout[0])

    # patch rng file by adding the declaration of an xsi:schemaLocation attribute
    if "NeuroML" in xsd_filename:
        element_to_modify = "<rng:define name=\"NeuroMLDocument\">"
    elif "LEMS" in xsd_filename:
        # insert xsi namespace declaration
        insert_string_in_file(rng_filename,
                              "<rng:grammar ",
                              "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" ")
        lems_version = [int(x) for x in base_name.rsplit('_v')[1].split('.')]
        if lems_version <= [0, 7, 2]:
            element_to_modify = "<rng:define name=\"Lems\">"
        else:
            element_to_modify = "<rng:element name=\"Lems\">"
    else:
        raise ValueError("This only works with LEMS or NeuroML schemas!")

    
    insert_string_in_file(rng_filename,
                          element_to_modify,
                          "\n<rng:attribute name=\"xsi:schemaLocation\"><text/></rng:attribute>\n")




    # convert rng -> rnc
    subprocess.call(["trang {} {}".format(rng_filename,
                                          rnc_filename)],
                    shell=True)
