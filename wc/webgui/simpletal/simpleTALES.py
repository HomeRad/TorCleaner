# -*- coding: iso-8859-1 -*-
""" simpleTALES Implementation

Copyright (c) 2003 Colin Stewart (http://www.owlfish.com/)
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
 1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
 3. The name of the author may not be used to endorse or promote products
    derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

If you make any bug fixes or feature enhancements please let me know!

The classes in this module implement the TALES specification, used
by the simpleTAL module.

Module Dependencies: logging
"""

import copy
import logging
import wc.webgui.simpleTal

__version__ = wc.webgui.simpletal.__version__


class ContextVariable (object):
    """store one variable value"""

    def __init__ (self, value = None):
        self.ourValue = value


    def isDefault (self):
        return False


    def isNothing (self):
        return self.value() is None


    def isSequence (self):
        # Return the length of the sequence - if it's zero length then it's handled
        # as though it wasn't a sequence at all.
        try:
            seqLength = len(self.value())
            dummy = self.value()[1:1]
            return seqLength>0
        except:
            return False


    def isCallable (self):
        return callable(self.ourValue)


    def isTrue (self):
        if self.isNothing():
            return False
        if self.isDefault():
            return True
        if self.isSequence():
            return len(self.value())>0
        return self.value()


    def value (self, currentPath=None):
        if callable(self.ourValue):
            return self.ourValue()
        return self.ourValue


    def rawValue (self):
        return self.ourValue


    def __str__ (self):
        return str(self.ourValue)


class DefaultVariable (ContextVariable):
    """default variable value"""

    def __init__ (self):
        super(DefaultVariable, self).__init__(1)


    def isNothing (self):
        return False


    def isDefault (self):
        return True


    def value (self, currentPath=None):
        # We return our self so that define works properly.
        return self


    def __str__ (self):
        return "Default"


class NothingVariable (ContextVariable):
    """variable value representing a no-value"""
    def __init__ (self):
        super(NothingVariable, self).__init__(None)


    def isNothing (self):
        return True


class NoCallVariable (ContextVariable):
    """variable value without call semantic"""
    def __init__ (self, variable):
        super(NoCallVariable, self).__init__(variable.ourValue)
        self.variable = variable


    def value (self, currentPath=None):
        return self.ourValue


class RepeatVariable (ContextVariable):
    """variable representing a list of values"""

    def __init__ (self, sequence):
        super(RepeatVariable, self).__init__(1)
        self.sequence = sequence
        self.position = 0
        self.vmap = None


    def value (self, currentPath=None):
        if self.vmap is None:
            self.createMap()
        return self.vmap


    def rawValue (self):
        return self.value()


    def increment (self):
        self.position += 1


    def createMap (self):
        self.vmap = {}
        self.vmap['index'] = self.getIndex
        self.vmap['number'] = self.getNumber
        self.vmap['even'] = self.getEven
        self.vmap['odd'] = self.getOdd
        self.vmap['start'] = self.getStart
        self.vmap['end'] = self.getEnd
        # TODO: first and last need to be implemented.
        self.vmap['length'] = len(self.sequence)
        self.vmap['letter'] = self.getLowerLetter
        self.vmap['Letter'] = self.getUpperLetter
        self.vmap['roman'] = self.getLowerRoman
        self.vmap['Roman'] = self.getUpperRoman


    # Repeat implementation goes here
    def getIndex (self):
        return self.position


    def getNumber (self):
        return self.position + 1


    def getEven (self):
        if (self.position % 2) != 0:
            return 0
        return 1


    def getOdd (self):
        if (self.position % 2) == 0:
            return 0
        return 1


    def getStart (self):
        if self.position == 0:
            return 1
        return 0


    def getEnd (self):
        if self.position == len(self.sequence) - 1:
            return 1
        return 0


    def getLowerLetter (self):
        result = ""
        nextCol = self.position
        if nextCol == 0:
            return 'a'
        while nextCol > 0:
            nextCol, thisCol = divmod(nextCol, 26)
            result = chr(ord('a') + thisCol) + result
        return result


    def getUpperLetter (self):
        return self.getLowerLetter().upper()


    def getLowerRoman (self):
        romanNumeralList = (('m', 1000)
                   ,('cm', 900)
                   ,('d', 500)
                   ,('cd', 400)
                   ,('c', 100)
                   ,('xc', 90)
                   ,('l', 50)
                   ,('xl', 40)
                   ,('x', 10)
                   ,('ix', 9)
                   ,('v', 5)
                   ,('iv', 4)
                   ,('i', 1)
                   )
        if self.position > 3999:
            # Roman numbers only supported up to 4000
            return ' '
        num = self.position + 1
        result = ""
        for roman, integer in romanNumeralList:
            while num >= integer:
                result += roman
                num -= integer
        return result


    def getUpperRoman (self):
        return self.getLowerRoman().upper()


class PathFunctionVariable (ContextVariable):
    """variable getting its value from a context path it traverses"""
    def __init__ (self, func):
        super(PathFunctionVariable, self).__init__(value=func)
        self.func = func


    def value (self, currentPath=None):
        if currentPath is not None:
            index, paths = currentPath
            args = ('/'.join(paths[index:]),)
            result = ContextVariable(self.func(*args))
            # Fast track the result
            raise result


class PythonPathFunctions (object):
    """variable getting its value from a python module path it traverses"""

    def __init__ (self, context):
        self.context = context


    def path (self, expr):
        result = self.context.evaluatePath(expr)
        if isinstance(result, ContextVariable):
            return result.value()
        else:
            return result


    def string (self, expr):
        result = self.context.evaluateString(expr)
        if isinstance(result, ContextVariable):
            return result.value()
        else:
            return result


    def exists (self, expr):
        result = self.context.evaluateExists(expr)
        if isinstance(result, ContextVariable):
            return result.value()
        else:
            return result


    def nocall (self, expr):
        result = self.context.evaluateNoCall(expr)
        if isinstance(result, ContextVariable):
            return result.value()
        else:
            return result


    def test (self, *arguments):
        if len(arguments) % 2:
            # We have an odd number of arguments - which means the last one is a default
            pairs = arguments[:-1]
            defaultValue = arguments[-1]
        else:
            # No default - so use None
            pairs = arguments
            defaultValue = None

        index = 0
        while index < len(pairs):
            _test = pairs[index]
            index += 1
            value = pairs[index]
            index += 1
            if _test:
                return value

        return defaultValue


class Context (object):
    """context storing variable values"""


    def __init__ (self, options=None, allowPythonPath=0):
        self.allowPythonPath = allowPythonPath
        self.cglobals = {}
        self.clocals = {}
        self.localStack = []
        self.repeatStack = []
        self.populateDefaultVariables(options)
        self.log = logging.getLogger("simpleTALES.Context")
        self.true = ContextVariable(1)
        self.false = ContextVariable(0)
        self.pythonPathFuncs = PythonPathFunctions(self)


    def addRepeat (self, name, var):
        # Pop the current repeat map onto the stack
        self.repeatStack.append(self.repeatMap)
        self.repeatMap = copy.copy(self.repeatMap)
        self.repeatMap[name] = var
        # Map this repeatMap into the global space
        self.addGlobal('repeat', self.repeatMap)


    def removeRepeat (self, name):
        # Bring the old repeat map back
        self.repeatMap = self.repeatStack.pop()
        # Map this repeatMap into the global space
        self.addGlobal('repeat', self.repeatMap)


    def addGlobal (self, name, value):
        if isinstance(value, ContextVariable):
            self.cglobals[name] = value
        else:
            self.cglobals[name] = ContextVariable(value)


    def addLocals (self, localVarList):
        # Pop the current locals onto the stack
        self.localStack.append(self.clocals)
        self.clocals = copy.copy(self.clocals)
        for name,value in localVarList:
            if isinstance(value, ContextVariable):
                self.clocals[name] = value
            else:
                self.clocals[name] = ContextVariable(value)


    def setLocal (self, name, value):
        # Override the current local if present with the new one
        if isinstance(value, ContextVariable):
            self.clocals[name] = value
        else:
            self.clocals[name] = ContextVariable(value)


    def getVariableMap (self):
        """return a mapping of all context variables"""
        d = {}
        for key, var in self.cglobals.items():
            d[key] = var.value()
        for key, var in self.clocals.items():
            d[key] = var.value()
        return d


    def popLocals (self):
        self.clocals = self.localStack.pop()


    def evaluate (self, expr, originalAtts = None):
        # Returns a ContextVariable
        self.log.debug("Evaluating %s ...", expr)
        if originalAtts is not None:
            # Call from outside
            self.cglobals['attrs'] = ContextVariable(originalAtts)

        # Supports path, exists, nocall, not, and string
        expr = expr.strip()
        if expr.startswith('path:'):
            res = self.evaluatePath(expr[5:].lstrip())
        elif expr.startswith('exists:'):
            res = self.evaluateExists(expr[7:].lstrip())
        elif expr.startswith('nocall:'):
            res = self.evaluateNoCall(expr[7:].lstrip())
        elif expr.startswith('not:'):
            res = self.evaluateNot(expr[4:].lstrip())
        elif expr.startswith('string:'):
            res = self.evaluateString(expr[7:].lstrip())
        elif expr.startswith('python:'):
            res = self.evaluatePython(expr[7:].lstrip())
        else:
            # Not specified - so it's a path
            res = self.evaluatePath(expr)
        self.log.debug("... result %s", res)
        return res


    def evaluatePython (self, expr):
        if not self.allowPythonPath:
            self.log.warn("Parameter allowPythonPath is false.  NOT Evaluating python expression %s" % expr)
            return self.false

        self.log.debug("Evaluating python expression %s" % expr)

        cglobals={}
        for name, value in self.cglobals.items():
            cglobals[name] = value.rawValue()
        cglobals['path'] = self.pythonPathFuncs.path
        cglobals['string'] = self.pythonPathFuncs.string
        cglobals['exists'] = self.pythonPathFuncs.exists
        cglobals['nocall'] = self.pythonPathFuncs.nocall
        cglobals['test'] = self.pythonPathFuncs.test

        clocals={}
        for name, value in self.clocals.items():
            clocals[name] = value.rawValue()

        try:
            result = eval(expr, cglobals, clocals)
        except Exception, e:
            # An exception occurred evaluating the template, return the exception as text
            self.log.warn("Exception occurred evaluting python path, exception: " + str(e))
            return ContextVariable("Exception: %s" % str(e))
        return ContextVariable(result)


    def evaluatePath (self, expr):
        self.log.debug("Evaluating path expression %s" % expr)
        allPaths = expr.split('|')
        if len(allPaths) > 1:
            for path in allPaths:
                # Evaluate this path
                pathResult = self.evaluate(path.strip())
                if pathResult is not None:
                    return pathResult
            return None
        else:
            # A single path - so let's evaluate it
            return self.traversePath(allPaths[0])


    def evaluateExists (self, expr):
        self.log.debug("Evaluating %s to see if it exists" % expr)
        allPaths = expr.split('|')
        if len(allPaths) > 1:
            # The first path is for us
            # Return true if this first bit evaluates, otherwise test the rest
            result = self.traversePath(allPaths[0])
            if result is not None:
                return self.true

            for path in allPaths[1:]:
                # Evaluate this path
                pathResult = self.evaluate(path.strip())
                if pathResult is not None:
                    return self.true
            return None
        else:
            # A single path - so let's evaluate it
            result =  self.traversePath(allPaths[0])
            if result is None:
                return None
            return self.true


    def evaluateNoCall (self, expr):
        self.log.debug("Evaluating %s using nocall" % expr)
        allPaths = expr.split('|')
        if len(allPaths) > 1:
            # The first path is for us
            result = self.traversePath(allPaths[0], canCall = 0)
            if result is not None:
                return result

            for path in allPaths[1:]:
                # Evaluate this path
                pathResult = self.evaluate(path.strip())
                if pathResult is not None:
                    return pathResult
            return None
        else:
            # A single path - so let's evaluate it
            return self.traversePath(allPaths[0], canCall=0)


    def evaluateNot (self, expr):
        self.log.debug("Evaluating NOT value of %s" % expr)

        # Evaluate what I was passed
        pathResult = self.evaluate(expr)
        if pathResult is None:
            # None of these paths exist!
            return self.true
        if pathResult.isTrue():
            return self.false
        return self.true


    def evaluateString (self, expr):
        self.log.debug("Evaluating String %s" % expr)
        result = ""
        skipCount = 0
        for position in xrange(0,len(expr)):
            if skipCount > 0:
                skipCount -= 1
            else:
                if expr[position] == '$':
                    try:
                        if expr[position + 1] == '$':
                            # Escaped $ sign
                            result += '$'
                            skipCount = 1
                        elif expr[position + 1] == '{':
                            # Looking for a path!
                            endPos = expr.find('}', position + 1)
                            if endPos > 0:
                                path = expr[position + 2:endPos]
                                # Evaluate the path
                                pathResult = self.evaluate(path)
                                if pathResult is not None and not pathResult.isNothing():
                                    resultVal = pathResult.value()
                                    if isinstance(resultVal, basestring):
                                        result += resultVal
                                    else:
                                        result += str(resultVal)
                                skipCount = endPos - position
                        else:
                            # It's a variable
                            endPos = expr.find(' ', position + 1)
                            if endPos == -1:
                                endPos = len(expr)
                            path = expr[position + 1:endPos]
                            # Evaluate the variable
                            pathResult = self.traversePath(path)
                            if pathResult is not None and not pathResult.isNothing():
                                resultVal = pathResult.value()
                                if isinstance(resultVal, basestring):
                                    result += resultVal
                                else:
                                    result += str(resultVal)
                            skipCount = endPos - position - 1
                    except Exception:
                        # Trailing $ sign - just suppress it
                        self.log.warn("Trailing $ detected")
                        pass
                else:
                    result += expr[position]
        return ContextVariable(result)


    def traversePath (self, expr, canCall=1):
        self.log.debug("Traversing path %s" % expr)
        # Check for and correct for trailing/leading quotes
        if expr[0] == '"' or expr[0] == "'":
            expr = expr[1:]
        if expr[-1] == '"' or expr[-1] == "'":
            expr = expr[0:-1]
        pathList = expr.split('/')

        path = pathList[0]
        if path.startswith('?'):
            path = path[1:]
            if self.clocals.has_key(path):
                path = self.clocals[path].value()
            elif self.cglobals.has_key(path):
                path = self.cglobals[path].value()
                #self.log.debug("Dereferenced to %s" % path)
        if self.clocals.has_key(path):
            val = self.clocals[path]
        elif self.cglobals.has_key(path):
            val = self.cglobals[path]
        else:
            # If we can't find it then return None
            return None
        index = 1
        for path in pathList[1:]:
            #self.log.debug("Looking for path element %s" % path)
            if path.startswith('?'):
                path = path[1:]
                if self.clocals.has_key(path):
                    path = self.clocals[path].value()
                elif self.cglobals.has_key(path):
                    path = self.cglobals[path].value()
                #self.log.debug("Dereferenced to %s" % path)
            if canCall:
                try:
                    temp = val.value((index,pathList))
                except ContextVariable, e:
                    return e
            else:
                temp = NoCallVariable(val).value()

            if hasattr(temp, path):
                val = getattr(temp, path)
                if not isinstance(val, ContextVariable):
                    val = ContextVariable(val)
            else:
                try:
                    val = temp[path]
                    if not isinstance(val, ContextVariable):
                        val = ContextVariable(val)
                except:
                    #self.log.debug("Not found.")
                    return None
            index += 1
        #self.log.debug("Found value %s" % str(val))
        if not canCall:
            return NoCallVariable(val)
        return val


    def __str__ (self):
        return "Globals: "+str(self.cglobals) + "Locals: "+str(self.clocals)


    def populateDefaultVariables (self, options):
        dvars = {}
        self.repeatMap = {}
        self.nothing = NothingVariable()
        dvars['nothing'] = self.nothing
        dvars['default'] = DefaultVariable()
        dvars['options'] = options
        # To start with there are no repeats
        dvars['repeat'] = self.repeatMap
        dvars['attrs'] = self.nothing

        # Add all of these to the global context
        for name in dvars.keys():
            self.addGlobal(name, dvars[name])

        # Add also under CONTEXTS
        self.addGlobal('CONTEXTS', dvars)

