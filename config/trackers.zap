<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Trackers and Counters" oid="9"
 desc="Statistic links and tracker images deserve now a separate category as they became a lot more in the last couple of months.">

<block title="Statistic sites" oid="0"
 desc="Some tracker sites"
 scheme=""
 host="(nedstatbasic\.net|nedstat\.nl)"
 port=""
 path=""
 parameters=""
 query=""
 fragment=""/>

<rewrite title="1x1 Tracker images" oid="1"
 desc="Several sites use 1x1 images to track users."
 tag="img">
<attr name="width">^1$</attr>
<attr name="height">^1$</attr>
</rewrite>
</folder>
