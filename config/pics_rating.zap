<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="PICS ratings" oid="13"
 desc="Contains rules deploying the Platform for Internet Content Selection (PICS).">

<pics title="PICS ratings" oid="0"
 desc="Enabling this rule turns WebCleaner into a whitelist-based kids-safe proxy. Only sites which meet the specified rating criterias are displayed, blocked sites display an error message or the given default url. Websites which have no PICS rating can be configured by you after password authorization."
 disable="1">
<url>http://www.calvinandhobbes.com/</url>
<service name="icra">
<category name="badexample">1</category>
<category name="chat">1</category>
<category name="drugsuse">1</category>
<category name="intolerance">1</category>
<category name="moderatedchat">1</category>
<category name="nudityobscuredsexualacts">1</category>
<category name="nuditysexualacts">1</category>
<category name="nuditysexualtouching">1</category>
<category name="pgmaterial">1</category>
<category name="violenceartistic">1</category>
<category name="violencejuryanimals">1</category>
<category name="violencejuryfantasy">1</category>
<category name="violencejuryhumans">1</category>
<category name="violencekillinganimals">1</category>
<category name="violencekillingfantasy">1</category>
<category name="violencekillinghumans">1</category>
<category name="violencemedical">1</category>
<category name="violencerape">1</category>
<category name="violencetoanimals">1</category>
<category name="violencetohumans">1</category>
<category name="weaponuse">1</category>
</service>
<service name="microsys">
<category name="sexrating">1</category>
</service>
<service name="rsac">
<category name="violence">1</category>
</service>
<service name="safesurf">
<category name="homosexualthemes">1</category>
<category name="otheradultthemes">1</category>
<category name="sexviolenceandprofanity">1</category>
<category name="violence">1</category>
</service>
<service name="vancouver">
<category name="sex">1</category>
<category name="violence">1</category>
</service>
</pics>
</folder>
