"""A parser for HTML"""
# Copyright (C) 2000,2001  Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import sys
try:
    import htmlsax
except ImportError:
    sys.stderr.write("""
Could not import the "htmlsax" module.
Please run 'python setup.py install' to install WebCleaner
completely on your system.
For local installation you can copy the file
build/lib.../htmlsax.so into the wc/parser/ directory.
Then you can run 'python webcleaner' from the source directory.
""")
    sys.exit(1)

class HtmlParser:
    """Use an internal C SAX parser. We do not define any callbacks
    here for compatibility. Currently recognized callbacks are:
    comment(data): <!-- data -->
    startElement(tag, attrs): <tag {attr1:value1,attr2:value2,..}>
    endElement(tag): </tag>
    doctype(data): <!DOCTYPE data?>
    pi(name, data=None): <?name data?>
    cdata(data): <![CDATA[data]]>
    characters(data): data

    additionally, there are error and warning callbacks:
    error(msg)
    warning(msg)
    fatalError(msg)
    """
    def __init__(self):
        """initialize the internal parser"""
        self.parser = htmlsax.parser(self)

    def feed (self, data):
        """feed some data to the parser"""
        self.parser.feed(data)

    def flush (self):
        """flush all data"""
        self.parser.flush()

    def reset (self):
        """reset the parser (without flushing)"""
        self.parser.reset()


class HtmlPrinter(HtmlParser):
    """handles all functions by printing the function name and
       attributes"""
    def __getattr__(self, name):
        self.mem = name
        return self._print

    def _print (self, *attrs):
        print self.mem, attrs


def _test():
    p = HtmlPrinter()
    p.feed("<hTml>")
    p.feed("<a href>")
    p.feed("<a href=''>")
    p.feed('<a href="">')
    p.feed("<a href='a'>")
    p.feed('<a href="a">')
    p.feed("<a href=a>")
    p.feed("<a href='\"'>")
    p.feed("<a href=\"'\">")
    p.feed("<a href=' '>")
    p.feed("<a href=a href=b>")
    p.feed("<a/>")
    p.feed("<a href/>")
    p.feed("<a href=a />")
    p.feed("</a>")
    p.feed("<?bla foo?>")
    p.feed("<?bla?>")
    p.feed("<!-- - comment -->")
    p.feed("<!---->")
    p.feed("<!DOCTYPE \"vla foo>")
    p.flush()

def _broken ():
    p = HtmlPrinter()
    p.feed("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML>

<HEAD>

<META NAME="Description" 				CONTENT="Obsession Development: Products">
<META NAME="Resource-Type"  			CONTENT="document">
<META NAME="Content-Type"   			CONTENT="text/html, charset=iso-8859-1">
<META HTTP-EQUIV="Content-Style-Type" 	CONTENT="text/css">

<LINK REL="Stylesheet" 					HREF="../obsession.css" TYPE="text/css">

<TITLE>Obsession Development: gentoo</TITLE>

<!-- SCRIPT LANGUAGE="JavaScript">

          <!--
          if (document.images) {
            var obsessionoff = new Image()
            obsessionoff.src = "../ObsessionOff.GIF"
            var obsessionon = new Image()
            obsessionon.src = "../ObsessionOn.GIF"

            var contactoff = new Image()
            contactoff.src = "../ContactOff.GIF"
            var contacton = new Image()
            contacton.src = "../ContactOn.GIF"

            var projectsoff = new Image()
            projectsoff.src = "../ProjectsOff.GIF"
            var projectson = new Image()
            projectson.src = "../ProjectsOn.GIF"

          }

          function actMenuItem(img1,img2) {
            act(img1)
          }

          function inactMenuItem(img1, img2) {
            inact(img1)
          }

          function act(imgName) {
            if (document.images) 
              document[imgName].src = eval(imgName + 'on.src')
			  window.status = "Click me!"
          }

          function inact(imgName) {
            if (document.images)
              document[imgName].src = eval(imgName + 'off.src')
			  window.status = "Obsession - Just ideas."
          }
          // -->
 
</SCRIPT -->

</HEAD>

<BODY BACKGROUND="../bk14.gif" BGCOLOR="#33517A" TEXT="#66AAFF" LINK="#FF9922" VLINK="#999999" style="background-repeat: repeat-x;">

<TABLE COLS=3 ROWS=2 CELLPADDING=0 CELLSPACING=0 BORDER=0>
<TR>
<TD WIDTH=164 HEIGHT=36><IMG CLASS="Hemlig" SRC="../spacer.GIF" WIDTH=1 HEIGHT=36 BORDER="0"></TD><TD></TD>
</TR>
<TR>
<TD></TD><TD>
<TABLE COLS=2 CELLPADDING=0 CELLSPACING=0 BORDER=0>
<TR>
    <TD WIDTH=127 VALIGN=Top ALIGN="CENTER">
	<IMG SRC="../OD_Logo-Small.GIF" WIDTH=127 HEIGHT=136 ALT="Magic" BORDER="0">
	<BR>
	<A HREF="MAILTO:emil@obsession.se?subject=[gentoo]"><IMG SRC="../Junk.GIF" WIDTH=25 HEIGHT=19 ALT="E-mail Emil" BORDER="0"></A>
	<BR>
	<FONT FACE="Verdana, Arial, Helvetica, sans-serif" SIZE="1"><B><A HREF="MAILTO:emil@obsession.se?subject=[gentoo]">E-mail Author</A>
	<BR><BR><BR>
            <P align="center" class="Margin">
		<B>Download</B><BR>
		<A href="http://prdownloads.sourceforge.net/gentoo/gentoo-0.11.25.tar.gz?download" title="Download gentoo">
		<IMG border=0 height=17 src="../download.gif" width="19">&nbsp;&nbsp;<B>Download<BR>
                gentoo 0.11.25 (http)</A>
		</B> <BR>[711 KB, tar.gz] 
            <BR>Requires GTK+ 1.2.x </P>
            <P align=center class=Margin>
			
		<B>Patch</B><BR>
		<A href="http://prdownloads.sourceforge.net/gentoo/diff-0.11.24-to-0.11.25.gz?download" title="Download Patch">
		<IMG border=0 height=17 src="../download.gif" width=19>&nbsp;&nbsp; <B>Download<BR>0.11.24 to 0.11.25 (http)</A>
		</B> <BR>[28 KB diff -ruN patch, gzipped] </P><BR>
            <P align=center class=Margin>
			
		<P align=center class=Margin>Packages<BR>
		<A href="ftp://ftp.falsehope.com/pub/gentoo">Red Hat RPMs</A><BR>
		[Maintainer: <A href="mailto:ryanw@infohwy.com">Ryan Weaver</A>]
		<BR>
		<BR>
		<A href="http://www.debian.org/Packages/unstable/x11/gentoo.html">Debian DEBs</A><BR>
		[Maintainer: <A href="mailto:jrodin@jagor.srce.hr">Josip Rodin</A>]<BR>
		<BR>
		Gentoo Linux users, type<BR>
		<TT>emerge app-misc/gentoo</TT>
		<BR>
		<BR>
		<A HREF="http://www.openbsd.org/cgi-bin/cvsweb/ports/x11/gentoo">OpenBSD Port</A><BR>
		[Maintainer: Jim Geovedi]<BR>
</P>

		<P align=center class=Margin>AppIndex<BR>
		New releases of gentoo are announced on
		<A href="http://freshmeat.net/">FreshMeat</A>
		You can go directly to gentoo's
		<A href="http://freshmeat.net/appindex/1998/09/24/906621975.html">AppIndex page</A>.
		</P></FONT>
	</TD>

	<TD WIDTH=16></TD>
	<TD WIDTH=256>

    <TABLE WIDTH=512 COLS=2 CELLPADDING=0 CELLSPACING=0 BORDER="0">
        <TR>
		<TD WIDTH="8" ROWSPAN="2"></TD
		<TD WIDTH="512" HEIGHT="88">

		<IMG NAME="obsession" SRC="../spacer.GIF" WIDTH=32 HEIGHT=32 BORDER="0" HSPACE=8>
		<BR CLEAR=All> 
		<IMG SRC="../Just02.GIF" WIDTH=256 HEIGHT=88 ALT="gentoo logo" BORDER="0"></TD>
		</TR
		><TR>
		<TD>
		<BR><FONT FACE="Arial, Geneva, Helvetica, sans-serif" SIZE="2">
		  <P>
		  gentoo is a modern, powerful, flexible, and utterly 
                  configurable file manager for UNIX systems, written using the 
                  GTK+ toolkit. It aims to be 100% graphically configurable; 
                  there's no need to edit config files by hand and then restart 
                  the application. gentoo is somewhat inspired in its look &amp; 
                  feel by the classic Amiga program DirectoryOpus. It has been 
                  successfully tested on a variety of platforms, including 
                  Linux/x86, Linux/Alpha, Solaris, FreeBSD and OpenBSD.
		  </P> 
                  <P>
		  (If you came here looking for the <A href="http://www.gentoo.org/">Gentoo Linux</A> distribution,
                  you know where to click. Then come back and download gentoo to manage your files with! :)
		  </P>
				  
                  <B>Features</B>
                  <P>Some of the main features of gentoo are: 
                  <UL>
		   <FONT face="Arial, Geneva, Helvetica, sans-serif" size="2">
                    <LI>Written from scratch, using ANSI C and the GTK+ toolkit.
                    <LI>Aims to be 100% graphically configurable, and comes 
                        pretty close, too. 
                    <LI>Very cool (!) file typing and -styling systems allows 
                        you to configure how files of different types are shown 
                        (with colors and icons), and what happens when you 
                        doubleclick them (spawn image viewers, music players, etc). 
                    <LI>Includes more than 120 original pixmaps icons (16x15 
                        pixels). 
                    <LI>Internal support for most file operations (copy, move, 
                        rename, rename, makedir etc).
		   </FONT>
		  </UL>
		  </P>

                  <B>Requirements</B>
                  <P>
		  The most modern (0.11.x) releases of <B>gentoo</B> require 
                  GTK+ 1.2.x. As is normal with GTK+ applications, gentoo also 
                  requires the GDK and glib libraries. If you have a working 
                  GTK+ installation, you will have these too, so don't worry. If 
                  your system does <B>not</B> have GTK+ installed, you need to 
                  download it (and glib) from <A href="http://www.gtk.org/">http://www.gtk.org/</A>.
		  </P>
                  <P>
		  It is nice, but not required, to have the <CODE>file(1)</CODE> command
		  installed, since gentoo can use it to identify filetypes. Please be aware
		  that not all <CODE>file</CODE> commands supplied with commercial Un*xes are
                  good enough to be used with gentoo (this is the case with Sun's <CODE>file</CODE>
		  implementation, for example). You might want to look for a replacement. The
		  version found <A href="http://freshmeat.net/projects/file/?highlight=file">here</A>
                  is recommended.
		  </P>
                  <P>
		  A few <B>screenshots</B> of gentoo are also available (Shots show gentoo version 0.11.11,
		  running under <A href="http://www.windowmaker.org/">Window Maker</A> and were 
                  taken on 2000-01-04):
                  <UL>
		   <FONT face="Arial, Geneva, Helvetica, sans-serif">
                    <LI><A href="/gentoo/main.gif" title="Screenshot of gentoo">Main Window</A> [41 KB GIF] 
                    <LI><A href="/gentoo/cfg_dirpane.gif" title="Screenshot of gentoo">Dir Pane Config</A> [21 KB GIF] 
                    <LI><A href="/gentoo/cfg_styles.gif" title="Screenshot of gentoo">File Style Config</A> [15 KB GIF] 
                    <LI><A href="/gentoo/cfg_types.gif" title="Screenshot of gentoo">File Type Config</A> [18 KB GIF] 
                    <LI><A href="/gentoo/cfg_buttons.gif" title="Screenshot of gentoo">Action Button Config</A> [16 KB GIF]
		   </FONT>
		  </UL>
                  <P></P>
				  
		<P>
		<B>User-Contributed Screenshots</B>
                <UL>
		 <FONT face="Arial, Geneva, Helvetica, sans-serif">
                  <LI><A href="/gentoo/contrib/Stefan_Eiserman.gif">Main Window</A>
		      [By Stefan Eiserman, 77 KB GIF]</LI>
                  <LI><A href="/gentoo/contrib/Stefan_Eiserman2.jpg">Main Window, big</A>
		      [Also by Stefan Eiserman, 333 KB JPG]</LI>
                  <LI><A href="/gentoo/contrib/theduke_dockicon.xpm">Window Maker dock icon</A>
		      [By Kris, &lt;<A href="mailto:theduke@planetinternet.be">theduke@planetinternet.be</A>&gt;, 21 KB XPM]</LI>
		  <LI><A HREF="/gentoo/contrib/Stefan_Nicolin.jpg">Main Window (themed GTK+)</A>
		      [By Stefan Nicolin, 75 KB JPG]</LI>
		  <LI><A HREF="/gentoo/contrib/Johannes_Tevessen.gif">Main Window (themed GTK+)</A>
		      [By Johannes Tevessen, 58 KB GIF]</LI>
		  <LI><A HREF="/gentoo/contrib/Erik_Sittmann.jpg">Main Window (Cygwin/Win32)</A>
		      [By Erik Sittmann, 388 KB JPG]</LI>
		 </FONT>
		</UL>
		</P>
		</TD>
        </TR>
	</TABLE>
    </TD>
    </TR>
</TABLE>
</TD>
</TR>
</TABLE>	

</BODY>
</HTML>
""")
    p.flush()


if __name__ == '__main__':
    _broken()
