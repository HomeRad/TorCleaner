# -*- coding: iso-8859-1 -*-
"""magic module"""
#    Magic - Python module to classify like the 'file' command using a 'magic' file
#    See: 'man 4 magic' and 'man file'
#
#    Copyright (C) 2002 Thomas Mangin
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# modified by Bastian Kleineidam

import os, re, string, convert

# Need to have a checksum on the cache and source file to update at object creation
# Could use circle safe_pickle (see speed performance impact)
# This program take some input file, we should check the permission on those files ..
# Some code cleanup and better error catching are needed
# Implement the missing part of the magic file definition


class Failed (Exception):
    pass


class Magic (object):

    data_size = {'byte':1, 'short':2, 'long':4, 'string':1, 'pstring':1, 'date': 4, 'ldate': 4}
    type_size = {'b':1, 'B':1, 's':2, 'S':2, 'l':4, 'L':5}


    se_offset_abs="^\(([0\\\][xX][\dA-Fa-f]+|[0\\\][0-7]*|\d+)(\.[bslBSL])*\)"
    se_offset_add="^\(([0\\\][xX][\dA-Fa-f]+|[0\\\][0-7]*|\d+)(\.[bslBSL])*([-+])([0\\\][xX][\dA-Fa-f]+|[0\\\][0-7]*|\d+)\)"


    def __init__ (self,filename, cachename):
        self.entries = 0
        self._leveldict = {}
        self._direct = {}
        self._offset_relatif = {}
        self._offset_type = {}
        self._offset_delta = {}
        self._endiandict = {}
        self._kinddict = {}
        self._oper = {}
        self._mask = {}
        self._test = {}
        self._datadict = {}
        self._lengthdict = {}
        self._mimedict = {}
        if not os.path.isfile(cachename):
            self.read_magic(filename)
            self.write_cache(cachename)
        self.read_cache(cachename)


    # read_magic subfunction
    def _split (self, line):
        result = ''
        split = line.split()
        again = True
        # Make sure the split function did not split too much
        while again:
            again = False
            pos = 0
            part = []
            top = len(split)
            while pos < top:
                if convert.is_final_dash(split[pos]):
                    result = split[pos] + ' '
                    index = line.find(result)
                    if index != -1:
                        char = line[index+len(result)]
                        if char != ' ' and char != '\t':
                            pos += 1
                            result += split[pos]
                            again = True
                else:
                    result = split[pos]
                part.append(result)
                pos += 1
            split = part
        return part


    def _level (self, text):
        return text.count('>')


    def _strip_start (self,char,text):
        if text[0] == char:
            return text[1:]
        return text


    def _direct_offset (self,text):
        if text[0] == '(' and text[-1] == ')':
            return 0
        return 1


    def _offset (self,text):
        direct = self._direct_offset(text)
        offset_type = 'l'
        offset_delta = 0L
        offset_relatif = 0L

        # Get the offset information
        if direct:
            offset_delta = convert.convert(text)
        else:
            match_abs = re.compile(self.se_offset_abs).match(text)
            match_add = re.compile(self.se_offset_add).match(text)

            if match_abs:
                offset_relatif = convert.convert(match_abs.group(1))

                if match_abs.group(2) != None:
                    offset_type = match_abs.group(2)[1]


            elif match_add:
                offset_relatif = convert.convert(match_add.group(1))

                if match_add.group(2) != None:
                    offset_type = match_add.group(2)[1]

                if match_add.group(3) == '-':
                    offset_delta = 0L - match_add.group(4)
                else:
                    offset_delta = convert.convert(match_add.group(4))

        return (direct,offset_type,offset_delta,offset_relatif)


    def _oper_mask (self,text):
        type_mask_and = text.split('&')
        type_mask_or = text.split('^')

        if len(type_mask_and) > 1:
            oper = '&'
            mask = convert.convert(type_mask_and[1])
            rest = type_mask_and[0]
            return (oper,mask,rest)
        if len(type_mask_or) > 1:
            oper = '^'
            mask = convert.convert(type_mask_or[1])
            rest = type_mask_or[0]
            return (oper,mask,rest)
        return ('',0L,text)


    def _endian (self,full_type):
        if full_type.startswith('be'):
            return 'big'
        elif full_type.startswith('le'):
            return 'little'
        return 'local'


    def _kind (self,full_type,endian):
        if endian == 'local':
            kind = full_type
        else:
            kind = full_type[2:]

        # XXX: string case and white space compaction option not implemented
        # XXX: Not very used ...
        if kind.startswith("string/"):
            # XXX todo
            #NOT_DONE_YET = kind[7:]
            kind = "string"

        # XXX: No idea what are those extension
        if kind.startswith("ldate-"):
            # XXX todo
            #NOT_DONE_YET = kind[6:]
            kind = "ldate"

        return kind


    def _test_result (self,test_result):
        if test_result[0] in "=><&!^":
            test = test_result[0]
            result = test_result[1:]
            return (test,result)
        elif test_result == 'x':
            test = 'x'
            result = 'x'
            return (test,result)
        else:
            test = '='
            result = test_result
            return (test,result)


    def _string (self,list):
        r = []
        for s in list:
            if type(s) is str:
                if s == "\\0":
                    r.append(chr(0))
                else:
                    r.append(s)
            elif s <10:
                r.append(ord(str(s)))
            else:
                r.append(s)
        return r


    def _data (self,kind,result):
        pos = 0
        data = list('')
        while pos < len(result):
            if convert.is_c_escape(result[pos:]):
                # \0 is not a number it is the null string
                if result[pos+1] == '0':
                    data.append(result[pos])
                    data.append(0L)
                # \rnt are special
                else:
                    data.append(result[pos:pos+2])
                pos +=2
            elif kind == "string" and (result[pos] in string.ascii_letters or result[pos] in string.digits):
                data.append(ord(result[pos])*1L)
                pos +=1
            else:
                base = convert.which_base(result[pos:])

                if base == 0:
                    data.append(ord(result[pos])*1L)
                    pos += 1
                else:
                    size_base = convert.size_base(base)
                    size_number = convert.size_number(result[pos:])
                    start = pos + size_base
                    end = pos + size_number
                    nb = convert.base10(result[start:end],base)
                    pos += size_number
                    data.append(nb*1L)
        return data


    def _length (self, kind, data):
        # Calculate the size of the data to read in the file
        if kind == "string":
            replace = ""
            for i in data:
                # except: Too lazy to handle the '\r' and co otherwise
                try: replace += chr(i)
                except: replace+='*'
            # This is for "\0"
            replace = replace.replace('*\0','*')
            # This is for two "\"
            replace = replace.replace('\\\\','*')
            # This is for the remaining "\{whatever}"
            replace = replace.replace('\\','')
            length = len(replace)
        else:
            length = self.data_size[kind]
        return length


    def _mime (self,list):
        mime=''
        for name in list:
            mime += name + " "
        mime = mime.rstrip()
        mime = mime.replace("\\a","\a")
        mime = mime.replace("\\b","\b")
        mime = mime.replace("\\f","\f")
        mime = mime.replace("\\n","\n")
        mime = mime.replace("\\r","\r")
        mime = mime.replace("\\t","\t")
        mime = mime.replace("\\v","\v")
        mime = mime.replace("\\0","\0")
        return mime


    def read_magic (self, magic_file):
        self.magic = []

        try:
            f = file(magic_file, 'rb')
        except:
            raise StandardError("No valid magic file called %r"%magic_file)
        index = 0
        for line in f.readlines():
            line = line.strip()

            if line and not line.startswith('#'):
                part = self._split(line)

                # If the line is missing a text string assume it is '\b'
                while len(part) < 4:
                    part.append('\b')

                # Get the level of the test
                level = self._level(part[0])

                # XXX: What does the & is used for in ">>&2" as we do not know skip it
                offset_string = self._strip_start('&',part[0][level:])

                # offset such as (<number>[.[bslBSL]][+-][<number>]) are indirect offset
                (direct,offset_type,offset_delta,offset_relatif) = self._offset(offset_string)

                # The type can be associated to a netmask
                (oper,mask,rest) = self._oper_mask(part[1])

                # No idea what this 'u' is so skip it
                full_type = self._strip_start('u',rest)

                endian = self._endian(full_type)
                kind = self._kind(full_type,endian)

                # Get the comparaison test and result
                (test,result) = self._test_result(part[2])

                # Get the value to check against
                data = self._data(kind,result)

                # Get the length of the data
                length = self._length(kind,data)

                # Special characters
                mime = self._mime(part[3:])

                # Append the line to the list
                self._leveldict[index] = level
                self._direct[index] = direct
                self._offset_type[index] = offset_type
                self._offset_delta[index] = offset_delta
                self._offset_relatif[index] = offset_relatif
                self._endiandict[index] = endian
                self._kinddict[index] = kind
                self._oper[index] = oper
                self._mask[index] = mask
                self._test[index] = test
                self._datadict[index] = data
                self._lengthdict[index] = length
                self._mimedict[index] = mime

                self.entries = index
                index += 1

        f.close()


    def write_cache (self,name):
        f = file(name,'wb')
        import cPickle
        cPickle.dump(self._leveldict,f,1)
        cPickle.dump(self._direct,f,1)
        cPickle.dump(self._offset_relatif,f,1)
        cPickle.dump(self._offset_type,f,1)
        cPickle.dump(self._offset_delta,f,1)
        cPickle.dump(self._endiandict,f,1)
        cPickle.dump(self._kinddict,f,1)
        cPickle.dump(self._oper,f,1)
        cPickle.dump(self._mask,f,1)
        cPickle.dump(self._test,f,1)
        cPickle.dump(self._datadict,f,1)
        cPickle.dump(self._lengthdict,f,1)
        cPickle.dump(self._mimedict,f,1)
        f.close()


    def read_cache (self,name):
        f = file(name,'rb')
        import cPickle
        self._leveldict = cPickle.load(f)
        self._direct = cPickle.load(f)
        self._offset_relatif = cPickle.load(f)
        self._offset_type = cPickle.load(f)
        self._offset_delta = cPickle.load(f)
        self._endiandict = cPickle.load(f)
        self._kinddict = cPickle.load(f)
        self._oper = cPickle.load(f)
        self._mask = cPickle.load(f)
        self._test = cPickle.load(f)
        self._datadict = cPickle.load(f)
        self._lengthdict = cPickle.load(f)
        self._mimedict = cPickle.load(f)
        self.entries = len(self._leveldict)
        f.close()


    # classify subfuntions

    def _indirect_offset (self,f,type,offset):
        # Raise file error if file too short    
        f.seek(offset)
        if type == 'l':
            delta = convert.little4(self._read(f,4))
        elif type == 'L':
            delta = convert.big4(self._read(f,4))
        elif type == 's':
            delta = convert.little2(self._read(f,2))
        elif type == 'S':
            delta = convert.big2(self._read(f,2))
        elif type == 'b':
            delta = ord(self._read(f,1))
        elif type == 'B':
            delta = ord(self._read(f,1))
        return offset + delta


    def _read (self, fp, number):
        # This may retun IOError
        data = fp.read(number)
        if not data:
            raise IOError("out of file access")
        return data


    def _convert (self, kind, endian, data):
        # Can raise StandardError and IOError
        value = 0

        # Convert the data from the file
        if kind == 'byte':
            if len(data) < 1:
                raise StandardError("Should never happen, not enough data")
            value= ord(data[0])
        elif kind == 'short':
            if len(data) < 2:
                raise StandardError("Should never happen, not enough data")
            if endian == 'local':
                value= convert.local2(data)
            elif endian == 'little':
                value= convert.little2(data)
            elif endian == 'big':
                value= convert.big2(data)
            else:
                raise StandardError("Endian type unknown")
        elif kind == 'long':
            if len(data) < 4:
                raise StandardError("Should never happen, not enough data")
            if endian == 'local':
                value= convert.local4(data)
            elif endian == 'little':
                value= convert.little4(data)
            elif endian == 'big':
                value= convert.big4(data)
            else:
                raise StandardError("Endian type unknown")
        elif kind == 'date':
            # XXX: Not done yet
            pass
        elif kind == 'ldate':
            # XXX: Not done yet
            pass
        elif kind == 'string':
            # Nothing to do
            pass
        elif kind == 'pstring':
            # Not done here anymore
            pass
            #    #Convert it to be like a string
            #    size=ord(data[0])
            #    # Not sure the test is right (at one byte)
            #    if file_length < offset + size:
            #        value= self._read(f,size)
            #        leng = size
            #        kind = "string"
        else:
            raise StandardError("Type %r not recognised"%kind)
        return value


    def _binary_mask (self,oper,value,mask):
        if oper == '&':
            value &= mask
        elif oper == '^':
            value ^= mask
        elif oper == '':
            pass
        else:
            raise StandardError("Binary operator unknown %r"%oper)
        return value


    def _read_string (self, fp):
        # This may retun IOError
        limit = 0
        result = "" 
        while limit < 100:
            char = self._read(fp, 1)
            # chr(0) == '\x00'
            if char == '\x00' or char == '\n':
                break
            result += char
            limit += 1
        if limit == 100:
            raise Failed("too much NULL bytes in input")
        return result


    def _is_null_string (self, data):
        return len(data) == 2 and data[0] == '\\' and data[1] == 0L


    def classify (self, f):
        if not self.entries:
            raise StandardError("Not initialised properly")
        # Are we still looking for the ruleset to apply or are we in a rule
        found_rule = False
        # When we found the rule, what is the level that we successfull passed
        in_level = 0
        # If we failed part of the rule there is no point looking for higher level subrule
        allow_next = 0
        # String provided by the successfull rule
        result = ""

        f.seek(0,2)
        file_length = f.tell()

        for i in range(self.entries):
            level = self._leveldict[i]

            # Optimisation: Skipping all the rule we do not match the first prerequesite
            if not found_rule and level > 0:
                # Nothing to do with this rule
                continue

            # We are currently working a rule
            if found_rule:
                # Finished: we performed a series of test and it is now completed
                if level == 0:
                    break

                # No need to check a level if the previous one failed
                if level > allow_next:
                    # Safely ignore this rule
                    continue

            # The full magic rule
            direct = self._direct[i]
            offset_type = self._offset_type[i]
            offset_delta = self._offset_delta[i]
            offset_relatif = self._offset_relatif[i]
            endian = self._endiandict[i]
            kind = self._kinddict[i]
            oper = self._oper[i]
            mask = self._mask[i]
            test = self._test[i]
            data = self._datadict[i]
            leng = self._lengthdict[i]
            mime = self._mimedict[i]

            # This is what the file should contain to succed the test
            value = 0

            # Does the magic line checked match the content of the file ?
            success = False

            # The content of the file that may be used for substitution with %s
            replace = None

            try:
                # Get the offset of the information to read
                if direct == 1:
                    offset = offset_delta
                else:
                    offset = self._indirect_offset(f,offset_type,offset_delta)

                # If it is out of the file then the test fails.
                if file_length < offset:
                    raise Failed("Data length %d too small, needed %d"%(file_length, offset))

                # Make sure we can read the data at the offset position
                f.seek(offset)
                extract = self._read(f,leng)
                if not extract:
                    raise Failed("Could not extract %d bytes from offset %d"%(leng, offset))

                # Convert the little/big endian value from the file
                value = self._convert(kind,endian,extract)

                # If the value is masked, remove the unwanted bits
                value = self._binary_mask(oper,value,mask)

                # Perform the test
                if test == '=':
                    # If we are comparing string the string is already read
                    if kind == 'string':
                        # The string \0 seems special and it seems to be what to do
                        if self._is_null_string(data):
                            success = True
                        # Other string perform a byte to byte comparaison
                        elif len(data) == len(extract):
                            success = True
                            for index in range(len(data)):
                                # XXX: Does this fail for '\r' test
                                if ord(extract[index]) != data[index]:
                                    success = False
                    elif kind == 'pstring':
                        raise Failed("pstring not implemented")
                    else:
                        success = (data[0] == value)
                        replace = value

                elif test == '>':
                    # If we are > a string, we have to read it from the file
                    if kind == 'string':
                        if self._is_null_string(data):
                            if ord(extract[0]) != 0:
                                replace = extract + self._read_string(f)
                                success = True
                        else:
                            raise Failed(">[^0] Not implemented")
                    elif kind == 'pstring':
                        raise Failed("pstring not implemented")
                    else:
                        success = (value > data[0])
                        replace = value

                elif test == '<':
                    if kind == 'string':
                        success = True
                        minimum = min(len(data),len(extract))
                        if len(extract) > minimum:
                            success = False
                        else:
                            for index in range(minimum):
                                if data[index] > extract[index]:
                                    success = False
                                    break
                    elif kind == 'pstring':
                        raise Failed("pstring not implemented")
                    else:
                        success = (value < data[0])
                        replace = value

                elif test == '&':
                    success = ((value & data[0]) == data[0])
                    replace = value
                    
                elif test == '^':
                    # XXX: To be tested with a known file
                    success = ((value ^ data[0]) == 0)
                    replace = value
                    
                elif test == '!':
                    # XXX: To be tested with a known file
                    # XXX: Wrong so must be a binary inversion test
                    # success = (value != data[0])
                    success = False
                    replace = value
                    
                elif test == 'x':
                    # XXX: copy from the code in test == '>', should create a function
                    if kind == 'string':
                        limit = 0
                        while True:
                            if ord(extract[0]) == 0 or limit > 100:
                                break
                            replace += extract
                            extract = self._read(f,1)
                            limit += 1
                        if limit <= 100:
                            success = True
                    elif kind == 'pstring':
                        raise Failed("pstring not implemented")
                    else:
                        success = True
                        replace = value
                else:
                    raise StandardError("test used %r is not defined"%test)

                if success:
                    found_rule = True
                    in_level = level
                    allow_next = level+1

                    if replace is not None:
                        try:
                            mime = mime % replace
                        except:
                            pass

                    if mime != []:
                        result += mime
                        result += ' '
                else:
                    raise Failed("No success")
            except (Failed, IOError):
                allow_next = level
        f.close()

        if not found_rule:
            # XXX: API Change this was previously returning "unknown"
            return None

        # The magic file use "backspace" to concatenate what is normally separated with a space"
        return result.rstrip().lstrip('\x08').replace(' \x08','')
