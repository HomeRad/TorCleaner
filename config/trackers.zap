<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder sid="wc.366" oid="5" title="Trackers and counters"
 desc="Statistic links and tracker images deserve now a separate category as they became a lot more in the last couple of months.">

<block sid="wc.363" oid="0" title="Statistic sites"
 desc="Some tracker sites"
 scheme=""
 host="(nedstatbasic\.net|nedstat\.nl|ivwbox\.de)"
 port=""
 path=""
 parameters=""
 query=""
 fragment=""/>

<rewrite sid="wc.364" oid="1" title="1x1 tracker images"
 desc="Several sites use 1x1 images to track users."
 tag="img">
<attr name="width">^1$</attr>
<attr name="height">^1$</attr>
<replacement part="complete"/>
</rewrite>

<image sid="wc.365" oid="2" title="1x1 tracker images 2"
 desc="In case the width and height attributes are missing"
 width="1"
 height="1"/>
</folder>
