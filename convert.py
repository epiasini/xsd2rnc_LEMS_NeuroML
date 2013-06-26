#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convert LEMS and NeuroML schema definitions from xsd to rng and rnc
formats.
"""
import subprocess
import os.path
#from pkg_resources import resource_string

xsdtorng_resource = "resources/XSDtoRNG.xsl"#resource_string(__name__, "resources/XSDtoRNG.xsl")

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
    if not rnc_filename:
        rng_filename = os.path.splitext(os.path.split(xsd_filename)[1])[0] + ".rng"
        rnc_filename = os.path.splitext(os.path.split(xsd_filename)[1])[0] + ".rnc"
    else:
        rng_filename = os.path.splitext(os.path.split(rnc_filename)[1])[0] + ".rng"

    # perform automatic xsl transformation: xsd -> rng
    subprocess.call(["xsltproc -o {} {} {}".format(rng_filename,
                                                   xsdtorng_resource,
                                                   xsd_filename)],
                    shell=True)

    # patch rng file by adding the declaration of an xsi:schemaLocation attribute
    if "NeuroML" in xsd_filename:
        definition_to_modify = "NeuroMLDocument"
    elif "LEMS" in xsd_filename:
        # insert xsi namespace declaration
        insert_string_in_file(rng_filename,
                              "<rng:grammar ",
                              "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" ")
        definition_to_modify ="Lems"
    else:
        raise ValueError("This only works with LEMS or NeuroML schemas!")

    insert_string_in_file(rng_filename,
                          "<rng:define name=\"{}\">".format(definition_to_modify),
                          "\n<rng:attribute name=\"xsi:schemaLocation\"><text/></rng:attribute>\n")




    # convert rng -> rnc
    subprocess.call(["trang {} {}".format(rng_filename,
                                          rnc_filename)],
                    shell=True)



if __name__=="__main__":
    import argparse
    # create the top-level parser
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("xsdfile",
                        help="input xsd schema file (eg LEMS_v0.7.xsd)")
    parser.add_argument("rncfile",
                        help="output rnc schema path (eg LEMS_v0.7.rnc). Must have .rnc extension.")
    # parse the args
    args = parser.parse_args()
    xsd_filename = args.xsdfile

    # call main function
    main(xsd_filename)
