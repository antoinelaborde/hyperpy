#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to for working with ENVI header files

Author: Dan Clewley
Creation Date: 07/08/2015

find_hdr_file and read_hdr_file written by Ben Taylor
"""

###########################################################
# This file has been created by ARSF Data Analysis Node and
# is licensed under the GPL v3 Licence. A copy of this
# licence is available to download with this file.
###########################################################

from __future__ import print_function
import collections
import os
import re
import sys
import numpy

ENVI_TO_NUMPY_DTYPE = {
    "1": numpy.uint8,
    "2": numpy.int16,
    "3": numpy.int32,
    "4": numpy.float32,
    "5": numpy.float64,
    "6": numpy.complex64,
    "9": numpy.complex128,
    "12": numpy.uint16,
    "13": numpy.uint32,
    "14": numpy.int64,
    "15": numpy.uint64,
}


def find_hdr_file(raw_file_name: str) -> str:
    """
    Return the header file corresponding to the raw file name
    :param raw_file_name: filename of the raw data file
    :return: hdr_filename
    """
    if not os.path.isfile(raw_file_name):
        raise IOError(f"Could not find file {raw_file_name}")
    # Get the filename without path or extension
    filename = os.path.basename(raw_file_name)
    file_split = os.path.splitext(filename)
    file_base = file_split[0]
    dir_name = os.path.dirname(raw_file_name)

    # See if we can find the header file to use
    if os.path.isfile(os.path.join(dir_name, file_base + ".hdr")):
        hdr_filename = os.path.join(dir_name, file_base + ".hdr")
    elif os.path.isfile(os.path.join(dir_name, filename + ".hdr")):
        hdr_filename = os.path.join(dir_name, filename + ".hdr")
    else:
        hdr_filename = None

    return hdr_filename


def read_hdr_file(hdrfilename, keep_case=False):
    """
    Read information from ENVI header file to a dictionary.

    By default all keys are converted to lowercase. To stop this behaviour
    and keep the origional case set 'keep_case = True'

    """
    output = collections.OrderedDict()
    comments = ""
    inblock = False

    try:
        hdrfile = open(hdrfilename, "r")
    except:
        raise IOError(
            "Could not open hdr file "
            + str(hdrfilename)
            + ". Reason: "
            + str(sys.exc_info()[1]),
            sys.exc_info()[2],
        )

    # Read line, split it on equals, strip whitespace from resulting strings
    # and add key/value pair to output
    for currentline in hdrfile:
        # ENVI headers accept blocks bracketed by curly braces - check for these
        if not inblock:
            # Check for a comment
            if re.search("^;", currentline) is not None:
                comments += currentline
            # Split line on first equals sign
            elif re.search("=", currentline) is not None:
                linesplit = re.split("=", currentline, 1)
                key = linesplit[0].strip()
                # Convert all values to lower case unless requested to keep.
                if not keep_case:
                    key = key.lower()
                value = linesplit[1].strip()

                # If value starts with an open brace, it's the start of a block
                # - strip the brace off and read the rest of the block
                if re.match("{", value) is not None:
                    inblock = True
                    value = re.sub("^{", "", value, 1)

                    # If value ends with a close brace it's the end
                    # of the block as well - strip the brace off
                    if re.search("}$", value):
                        inblock = False
                        value = re.sub("}$", "", value, 1)
                value = value.strip()
                output[key] = value
        else:
            # If we're in a block, just read the line, strip whitespace
            # (and any closing brace ending the block) and add the whole thing
            value = currentline.strip()
            if re.search("}$", value):
                inblock = False
                value = re.sub("}$", "", value, 1)
                value = value.strip()
            output[key] = output[key] + value

    hdrfile.close()

    output["_comments"] = comments

    return output


def write_envi_header(filename, header_dict):
    """
    Writes a dictionary to an ENVI header file

    Comments can be added to the end of the file using the '_comments' key.
    """

    # Open header file for writing
    try:
        hdrfile = open(filename, "w")
    except:
        raise IOError("Could not open hdr file {}. ".format(filename))

    hdrfile.write("ENVI\n")
    for key in header_dict.keys():
        # Check not comments key (will write separately)
        if key != "_comments":
            # If it contains commas likely a list so put in curly braces
            if str(header_dict[key]).count(",") > 0:
                hdrfile.write("{} = {{{}}}\n".format(key, header_dict[key]))
            else:
                # Write key at start of line
                hdrfile.write("{} = {}\n".format(key, header_dict[key]))

    # Write out comments at the end
    # Check they start with ';' and add one if they don't
    for comment_line in header_dict["_comments"].split("\n"):
        if re.search("^;", comment_line) is None:
            comment_line = ";{}\n".format(comment_line)
        else:
            comment_line = "{}\n".format(comment_line)
        # Check line contains a comment before writing out.
        if comment_line.strip() != ";":
            hdrfile.write(comment_line)
    hdrfile.close()
