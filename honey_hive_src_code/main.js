var cyan = '\x1b [36 m%s\x1b [0m';
var green = '\x1b [32 m%s\x1b [0m';
var blue = '\x1b [34 m%s\x1b [0m';
var yellow = '\x1b [33 m%s\x1b [0m';
var red = '\x1b [31 m%s\x1b [0m';
var magenta = '\x1b [35m%s\x1b [0m';
var net = require('net ');
var fs = require('fs ');
var buffer = require('buffer ');
var path = require(" path ");
var fork = require(' child_process ').fork;
const sqlite3 = require('sqlite3 ').verbose();
var exec = require(' child_process ').exec;
var encrypt_decrypt = require('./ encrypt_decrypt .js ');
var crypto = require('crypto ');
var password = 'honeyhive ';
var algorithm = 'aes -256 - cbc ';
var HOST = '0.0.0.0 ';
var PORT = 9830;
var resetCounter = 0;
var honeydIP = [];
var honeyPots = [];
var completeTransfers = [];
var alerts = [];
var srcIPs = {};
var dstIPs = {};
var srcPrts = {};
var dstPrts = {};
var percentage = 0.35;
var numInteractions = 0
var numSnortAlerts = 0;
var numPackets = 0;
var numSuricataAlerts = 0;
var numSuricataTypes = 0;
var suricataPackets = 0;
var numSnortAlerts_Merged = 0;
var numSnortTypes = 0;
var numSnortTypesMerged = 0;
var snortICount = 0;
var snortMCount = 0;
// Check for DB and create it if it doesn 't exists
// spawns a child process to check / create DB
const database_creator = path.resolve(" database_creator .js");
console.log(green, 'Checking Database FIle \n');
const params = [];
const options = {
    stdio: ['pipe ', 'pipe ', 'pipe ', 'ipc ']
};
const database_child = fork(database_creator, params, options);
database_child.on('message ', message => {
    console.log(green, 'message from Database Child :', message);
});
// //////////////////////////////////////////////////////////////////
function execute(command, callback) {
    exec(command, function (error, stdout, stderr) {
        callback(stdout);
    });
};
function countPackets(output) {
    numPackets += parseInt(output.split('Number of packets :')[1].
        trim())
    console.log(green, "Num Packets : " + numPackets);
}
// Assumptions : Honeypots are not emitting malicious traffic / haven 't been compromised
function alertAnalyzer() {
    // threshold for number of honeypots that can be interacted with before an alert is generated
    var hpThreshold = (Object.keys(dstIPs).length / (honeyPots.length)
    );
    if (hpThreshold > percentage) {
        createAlert('Alert : Multiple Honeypot Interaction Detected !')
    }
}
function createAlert(msg) {
    console.log(red, msg)
}
function parsePCAP(filename) {
    /*
    "C:\ Program Files \ Wireshark \ capinfos .exe" -c C:\ Snort \log
    \192.168.1.152 _2019 -10 -14 _0939 \192.168.1.152 _2019 -10 -14 _0939 . pcap
    File name : C:\ Snort \log \192.168.1.152 _2019 -10 -14 _0939
    \192.168.1.152 _2019 -10 -14 _0939 . pcap
    Number of packets : 1894
    */
    var cmd = '"C:\\ Program Files \\ Wireshark \\ capinfos .exe" -c "C:\\Snort \\ log \\ ' + filename
    execute(cmd, countPackets);
}
function snortMerge(mergeOutput) {
    console.log('Starting Snort Parser on Merged File \n');
    const snort_parser_merge = path.resolve(" snort_parser .js");
    const paramsMerge = [resetCounter, 0];
    const optionsMerge = {
        stdio: ['pipe ', 'pipe ', 'pipe ', 'ipc ']
    };
    const snort_child_merge = fork(snort_parser_merge, paramsMerge,
        optionsMerge);
    snort_child_merge.on('message ', message => {
        console.log(red, 'message from Snort Child Merged :', message);
        snortMCount += 1;
        message.forEach(function (alert) {
            if (alert.Count != undefined) {
                numSnortAlerts_Merged += alert.Count;
            }
            numSnortTypesMerged += 1;
        });
    });
    snort_child_merge.on('exit ', (code) => {
        snortMCount += 1;
        console.log(" Snort M Child Exited ");
    });
}
// looks at interfaces to automatically grab and bind on an IP
var os = require('os ');
var ifaces = os.networkInterfaces();
var serverIP;
Object.keys(ifaces).forEach(function (ifname) {
    var alias = 0;
    ifaces[ifname].forEach(function (iface) {
        if ('IPv4 ' !== iface.family || iface.internal !== false ||
            ifname.includes('VMware ')) {
            // skip over internal (i.e. 127.0.0.1) and non - ipv4 addresses
            return;
        }
        if (alias >= 1) {
            // this single interface has multiple ipv4 addresses
            console.log(ifname + ':' + alias, iface.address);
        } else {
            // this interface has only one ipv4 adress
            console.log(ifname, iface.address);
            serverIP = iface.address;
        }
        ++alias;
    });
});
console.log(cyan, " Sever IP: " + serverIP);
// Create a server instance , and chain the listen function to it
// The function passed to net . createServer () becomes the event handler for the 'connection ' event
// The sock object the callback function receives UNIQUE for each connection
var server = net.createServer(function (sock) {
    // Add a 'data ' event handler to this instance of socket
    sock.on('data ', function (data) {
        var JSONData = JSON.parse(data);
        /*
        header = {" Honeyd ": honeydIP ,
        " Honeypots ": honeypots
        "MSG ": 'AUTHENTICATE '}
        */
        if (JSONData.MSG == ' AUTHENTICATE ') {
            if (!honeydIP.includes(JSONData.Honeyd)) {
                honeydIP.push(JSONData.Honeyd);
            }
            JSONData.Honeypots.forEach(function (pot) {
                if (!honeyPots.includes(pot)) {
                    honeyPots.push(pot);
                }
            });
            console.log(green, " Connected Honeypots ");
            console.log(green, honeyPots);
        }
        // receive suricata alert count
        else if (JSONData.MSG == 'SURICATA ') {
            numSuricataAlerts += JSONData.NumAlerts;
            numSuricataTypes += JSONData.NumTypes;
            suricataPackets = JSONData.NumPackets;
            console.log(green, 'Suricata Alerts Received : ' +
                numSuricataAlerts + ', ' + numSuricataTypes + ', ' +
                suricataPackets);
        }
        // reboot machine for fresh stable state
        // C2 server should be relaunched automatically at startup
        else if (JSONData.MSG == 'REBOOT ') {
            // deletes all snort log files and then
            // reboots when the cmd is finished
            execute("del C:\\ Snort \\ log \\* /S /F /Q",
                function (output) {
                    execute(" shutdown /g /f /t 0", function () { });
                });
        }
        else if (JSONData.MSG == 'SNORT ') {
            console.log(" SNORT Command received , parsing PCAPS \n");
            // parse unscanned PCAPS
            if (!(completeTransfers === undefined || completeTransfers.
                length == 0)) {
                // mergecap -w outfile . pcapng dhcp - capture . pcapng imap -1.
                pcapng
                // have to add all their dirs in front of the filename
                too
                // then run through Snort
                var cmd = '"C:\\ Program Files \\ Wireshark \\ mergecap " -F pcap -w "C:\\ Snort \\ log \\ merged ' + resetCounter + '. pcap "';
                completeTransfers.forEach(function (filename) {
                    parsePCAP(filename);
                    cmd = cmd + ' ' + "C:\\ Snort \\ log \\" + filename;
                });
                console.log('Starting Snort Parser individually \n');
                const snort_parser = path.resolve(" snort_parser .js");
                const params = [resetCounter, 1];
                const options = {
                    stdio: ['pipe ', 'pipe ', 'pipe ', 'ipc ']
                };
                const snort_child = fork(snort_parser, params, options);
                snort_child.on('message ', message => {
                    console.log(red, 'message from Snort Child individually :', message);
                    message.forEach(function (alert) {
                        if (alert.Count != undefined) {
                            numSnortAlerts += alert.Count;
                        }
                        numSnortTypes += 1;
                    });
                });
                snort_child.on('exit ', (code) => {
                    snortICount += 1;
                    console.log(" Snort I Child Exited ");
                });
                if (completeTransfers.length > 1) {
                    // function noop () {}
                    execute(cmd, snortMerge);
                }
            }
        }
        else if (JSONData.MSG == 'RESET ') {
            // need to add a wait for all the snort processes to end
            sock.write(JSON.stringify({
                Interactions: numInteractions,
                SnortICount: snortICount, Snort: numSnortAlerts, SnortTypes:
                    numSnortTypes, SnortMCount: snortMCount, SnortMerged:
                    numSnortAlerts_Merged, SnortTypesMerged: numSnortTypesMerged,
                Packets: numPackets, Suricata: numSuricataAlerts, SuricataTypes:
                    numSuricataTypes, suricataPackets: suricataPackets, numHoneypots:
                    honeyPots.length, numPCAPs: completeTransfers.length
            }));
            honeydIP = [];
            honeyPots = [];
            completeTransfers = [];
            alerts = [];
            srcIPs = {};
            dstIPs = {};
            srcPrts = {};
            dstPrts = {};
            snortICount = 0;
            snortMCount = 0;
            numInteractions = 0
            numSnortAlerts = 0;
            numPackets = 0;
            numSuricataAlerts = 0;
            numSuricataTypes = 0;
            suricataPackets = 0;
            numSnortAlerts_Merged = 0;
            numSnortTypes = 0;
            numSnortTypesMerged = 0;
            resetCounter += 1;
            fs.writeFile("C:\\ Snort \\ log \\ pcaps .txt ", '', function () {
                console.log('Snort PCAP File cleared \n')
            });
            console.log(yellow, " Reset Received \n");
        }
        /*
        header = {" Time ": time . strftime ("%Y -%m -% d_%H%M") ,
        " Honeyd ": honeydIP ,
        "IP ": '192.168.72.150 ' ,
        "MSG ": 'HEARTBEAT '}
        */
        else if (JSONData.MSG == 'HEARTBEAT ') {
            console.log(green, " Honeypot Heartbeat - Time : " + JSONData
                .Time + " Honeyd : " + JSONData.honeydIP + " Honeypot IP: " +
                JSONData.IP);
        }
        /*
        header = {" Time ": time . strftime ("%Y -%m -% d_%H%M") ,
        " TransLayer ": transLayer ,
        " IP_SRC ": pckt_src ,
        " IP_DST ": pckt_dst ,
        " SPORT ": sport ,
        " DPORT ": dport ,
        "MSG ": 'ALERT '}
        */
        else if (JSONData.MSG == 'ALERT ') {
            numInteractions += 1;
            console.log(yellow, " Honeypot interaction detected \n\ tTime : " + JSONData.Time +
                "\n\ tTransport Protocol : " + JSONData.TransLayer +
                "\n\tIP SRC: " + JSONData.IP_SRC +
                "\n\ tSRC Port : " + JSONData.SPORT +
                "\n\tIP DST: " + JSONData.IP_DST +
                "\n\ tDST Port : " + JSONData.DPORT);
            if (JSONData.IP_SRC in srcIPs) {
                srcIPs[JSONData.IP_SRC] += 1;
            }
            else {
                srcIPs[JSONData.IP_SRC] = 1;
            }
            // --------------------------
            if (JSONData.SPORT in srcPrts) {
                srcPrts[JSONData.SPORT] += 1;
            }
            else {
                srcPrts[JSONData.SPORT] = 1;
            }
            // ---------------------------
            if (JSONData.IP_DST in dstIPs) {
                dstIPs[JSONData.IP_DST] += 1;
            }
            else {
                dstIPs[JSONData.IP_DST] = 1;
            }
            // ---------------------------
            if (JSONData.DPORT in dstPrts) {
                dstPrts[JSONData.DPORT] += 1;
            }
            else {
                dstPrts[JSONData.DPORT] = 1;
            }
            alerts.push({
                Time: JSONData.Time, Protocol: JSONData.
                    TransLayer, SrcIP: JSONData.IP_SRC, SrcPort: JSONData.SPORT, DstIP
                    : JSONData.IP_DST, DstPort: JSONData.DPORT
            });
            alertAnalyzer();
            // spawns a child process to check / create DB
            const database_inserter = path.resolve(" database_inserter . js");
            console.log(green, 'Adding to Database \n');
            // would need to re -JSON -ify JSONData , so just sending the
            // original data
            const params = [data];
            const options = {
                stdio: ['pipe ', 'pipe ', 'pipe ', 'ipc ']
            };
            const inserter_child = fork(database_inserter, params,
                options);
            inserter_child.on('message ', message => {
                console.log(green, 'message from Inserter Child :',
                    message);
            });
        }
        // client is sending PCAP , open a new port for transfer state
        // open a server / port for the file transfer to keep command
        // data and binary data separate
        else if (JSONData.MSG == 'PCAP ') {
            // console .log (green , JSONData . Filename + "\n" + JSONData . File_Size + "\n" + JSONData .MD5);
            // var callbackPort = JSONData . listenPort
            const transfer_server = path.resolve(" transfer_server .js");
            const params = [JSONData.Filename, JSONData.File_Size,
            JSONData.MD5, JSONData.Port];
            const options = {
                stdio: ['pipe ', 'pipe ', 'pipe ', 'ipc ']
            };
            const transferChild = fork(transfer_server, params, options)
                ;
            transferChild.on('message ', message => {
                console.log(green, 'message from transfer child :',
                    message + '\n');
                if (message == 'Download Complete ') {
                    fs.appendFile("C:\\ Snort \\ log \\ pcaps .txt ", "C:\\ Snort \\ log \\" + JSONData.Filename + '\n', function (err) {
                        if (err) throw err;
                        console.log('PCAP File added to Snort File list \n');
                    });
                    completeTransfers.push(JSONData.Filename);
                }
            });
        }
        // end of PCAP
        // end of on data
    });
    // Add a 'close ' event handler to this instance of socket
    sock.on('close ', function (data) {
        // console .log (yellow , 'CLOSED : ' + sock . remoteAddress +' '+ sock . remotePort );
    });
});
server.once('error ', function (err) {
    if (err.code === 'EADDRINUSE ') {
        console.log('Port Already in Use !: \n');
        process.exit()
    }
});
server.listen(PORT, HOST);
console.log(cyan, 'Server bound on ' + HOST + ':' + PORT);
