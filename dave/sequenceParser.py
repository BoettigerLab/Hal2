#!/usr/bin/python
#
## @file
#
# Handles parsing sequence xml files and generating movie objects.
#
# Hazen 12/10
#

from xml.dom import minidom, Node

import sc_library.hdebug as hdebug

## parseText
#
# Parses text using the functions specified by func.
#
# @param text The text to parse.
# @param func The function to parse the text with.
#
def parseText(text, func):
    if (len(text) > 0):
        return func(text)
    else:
        return None

## Progression
#
# The progression object.
#
class Progression:

    ## __init__
    #
    # Creates a progression object from the progression XML.
    #
    # @param progression_xml A xml node describing the progression.
    #
    def __init__(self, progression_xml):
        self.channels = []
        self.type = "none"

        if progression_xml:
            for node in progression_xml.childNodes:
                if node.nodeType == Node.ELEMENT_NODE:
                    if node.nodeName == "type":
                        self.type = node.firstChild.nodeValue
                    elif node.nodeName == "channel":
                        channel = int(node.firstChild.nodeValue)
                        start = parseText(node.getAttribute("start"), float)
                        frames = parseText(node.getAttribute("frames"), int)
                        inc = parseText(node.getAttribute("inc"), float)
                        self.channels.append([channel, start, frames, inc])
                    elif node.nodeName == "filename":
                        self.filename = node.firstChild.nodeValue


## Movie
#
# The movie object.
#
class Movie:

    ## __init__
    #
    # Dynamically create the class by processing the movie xml object.
    #
    # @param movie_xml A xml node describing the movie.
    #
    def __init__(self, movie_xml):

        # Node type
        self.type = "movie"

        # default settings
        self.delay = 0
        self.find_sum = 0.0
        self.length = 1
        self.min_spots = 0
        self.name = "default"
        self.pause = 1
        self.progression = None
        self.recenter = 0

        # parse settings
        for node in movie_xml.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                if (node.nodeName == "delay"):
                    self.delay = int(node.firstChild.nodeValue)
                elif (node.nodeName == "find_sum"):
                    self.find_sum = float(node.firstChild.nodeValue)
                elif (node.nodeName == "length"):
                    self.length = int(node.firstChild.nodeValue)
                elif (node.nodeName == "lock_target"):
                    self.lock_target = float(node.firstChild.nodeValue)
                elif (node.nodeName == "min_spots"):
                    self.min_spots = int(node.firstChild.nodeValue)
                elif (node.nodeName == "name"):
                    self.name = node.firstChild.nodeValue
                elif (node.nodeName == "parameters"):
                    self.parameters = int(node.firstChild.nodeValue)
                elif (node.nodeName == "pause"):
                    self.pause = int(node.firstChild.nodeValue)
                elif (node.nodeName == "recenter"):
                    self.recenter = int(node.firstChild.nodeValue)
                elif (node.nodeName == "stage_x"):
                    self.stage_x = float(node.firstChild.nodeValue)
                elif (node.nodeName == "stage_y"):
                    self.stage_y = float(node.firstChild.nodeValue)

        # parse progressions
        progression_xml = movie_xml.getElementsByTagName("progression")
        if (len(progression_xml) > 0):
            self.progression = Progression(progression_xml[0])
        else:
            self.progression = Progression(None)

    ## getNodeType
    #
    # Return the type of node so that other classes can determine how to process the xml command
    #
    def getType(self):
        return self.type

    ## __repr__
    #
    def __repr__(self):
        return hdebug.objectToString(self, "sequenceParser.Movie", ["name", "length", "stage_x", "stage_y"])

## ValveProtocol
#
# The fluidics protocol object.  This class controls communication with a valve chain
#
class ValveProtocol:
    ## __init__
    #
    # Dynamically create the class by processing the fluidics xml object.
    #
    # @param fluidics_xml A xml node describing the fluidics command.
    #
    def __init__(self, fluidics_xml):

        # node type
        self.type = "fluidics"

        # default settings
        self.protocol_name = []
        
        # passed single node
        node = fluidics_xml
        
        # parse settings
        if node.nodeType == Node.ELEMENT_NODE:
            if (node.nodeName == "valve_protocol"):
                self.protocol_name = node.firstChild.nodeValue

    ## getNodeType
    #
    # Return the type of node so that other classes can determine how to process the xml command
    #
    def getType(self):
        return self.type
    
    ## __repr__
    #
    def __repr__(self):
        return hdebug.objectToString(self, "sequenceParser.ValveProtocol", ["protocol_name"])

## parseMovieXml
#
# Parses the XML file that describes the movies.
#
# @param movie_xml_filename The name of the XML file.
#
def parseMovieXml(movie_xml_filename):
    xml = minidom.parse(movie_xml_filename)
    sequence = xml.getElementsByTagName("sequence").item(0)

    commands = []
    children = sequence.childNodes
    for child in children:
        if child.nodeType == Node.ELEMENT_NODE:
            if child.tagName == "movie":
                commands.append(Movie(child))
            elif child.tagName == "valve_protocol":
                commands.append(ValveProtocol(child))

    return commands

#
# Testing
# 
if __name__ == "__main__":
    parsed_commands = parseMovieXml("sequence.xml")
    print "Parsed the following commands: "
    for command in parsed_commands:
        print "   " + command.getType() + ": " + str(command)
    
#
# The MIT License
#
# Copyright (c) 2010 Zhuang Lab, Harvard University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
