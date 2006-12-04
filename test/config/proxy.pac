// example proxy.pac file for WebCleaner
// see http://wp.netscape.com/eng/mozilla/2.0/relnotes/demo/proxy-live.html
// for more info about proxy.pac files

function FindProxyForURL(url, host) {
    return "PROXY localhost:8080; DIRECT";
}

