<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder sid="wc.366" title="Trackers and counters"
 desc="Statistic links and tracker images deserve now a separate category as they became a lot more in the last couple of months." oid="5">
<block sid="wc.363" title="Statistic sites"
 desc="Some tracker sites"
 url="^https?://[0-9a-z.]*(nedstatbasic\.net|nedstat\.nl|ivwbox\.de)"/>

<rewrite sid="wc.6" title="Statistic sites 2">
<attr>^https?://[0-9a-z.]*(nedstatbasic\.net|nedstat\.nl|ivwbox\.de)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.364" title="tracker images"
 desc="Several sites use images to track users."
 tag="img">
<attr name="width">^(0|1)$</attr>
<attr name="height">^(0|1)$</attr>
<replacement part="complete"/>
</rewrite>

<image sid="wc.5" title="0x0 tracker images"
 desc="In case the width and height attributes are missing"/>

<image sid="wc.365" title="1x1 tracker images"
 desc="In case the width and height attributes are missing"
 width="1"
 height="1"/>

<block sid="wc.1" title="Siemens StatServ"
 url="siemens\.com/tracking_engine/StatServ"/>
</folder>
