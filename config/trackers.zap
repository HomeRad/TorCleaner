<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder sid="wc.366" title="Trackers and counters"
 desc="Statistic links and tracker images deserve now a separate category as they became a lot more in the last couple of months." oid="5">
<block sid="wc.363" title="Statistic sites"
 desc="Some tracker sites"
 url="https?://(nedstatbasic\.net|nedstat\.nl|ivwbox\.de)"/>

<rewrite sid="wc.364" title="1x1 tracker images"
 desc="Several sites use 1x1 images to track users."
 tag="img">
<attr name="width">^1$</attr>
<attr name="height">^1$</attr>
<replacement part="complete"/>
</rewrite>

<image sid="wc.365" title="1x1 tracker images 2"
 desc="In case the width and height attributes are missing"
 width="1"
 height="1"/>

<block sid="wc.1" title="Siemens StatServ"
 url="siemens\.com/tracking_engine/StatServ"/>
</folder>
