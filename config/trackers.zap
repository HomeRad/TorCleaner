<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.366" oid="5">
<title lang="en">Trackers and counters</title>
<description lang="en">Statistic links and tracker images deserve now a separate category as they became a lot more in the last couple of months.</description>
<block sid="wc.363"
 url="https?://(nedstatbasic\.net|nedstat\.nl|ivwbox\.de)">
<title lang="en">Statistic sites</title>
<description lang="en">Some tracker sites</description>
</block>

<rewrite sid="wc.6">
<title lang="en">Statistic sites 2</title>
<attr>^https?://[0-9a-z.]*(nedstatbasic\.net|nedstat\.nl|ivwbox\.de)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.364" tag="img">
<title lang="en">1x1 tracker images</title>
<description lang="en">Several sites use 1x1 images to track users.</description>
<attr name="width">^1$</attr>
<attr name="height">^1$</attr>
<replacement part="complete"/>
</rewrite>

<image sid="wc.5">
<title lang="en">In case the width and height attributes are missing</title>
<description lang="en">In case the width and height attributes are missing</description>
</image>

<image sid="wc.365"
 width="1"
 height="1">
<title lang="en">1x1 tracker images 2</title>
<description lang="en">In case the width and height attributes are missing</description>
</image>

<block sid="wc.1"
 url="siemens\.com/tracking_engine/StatServ">
<title lang="en">Siemens StatServ</title>
</block>
</folder>
