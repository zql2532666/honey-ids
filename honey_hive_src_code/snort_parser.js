// Run Snort on a PCAP
// Parse Snort alert log , combine like alerts ,
// and other metada in JSON format (src IP , dst IP , port range )
// keep count of occurances
// dstIP should be the same since the pcaps are transfered as individually for each IP
//
// Send back results to main .js for compilation and monitoring
// which will have some threshold for alerting if so much traffic is seen
// sent to one host , or a smaller amount of traffic sent to multiple hosts
// Snort Alert Example
/*
[**] [1:10000005:2] NMAP TCP Scan [**]
[ Priority : 0]
10/01 -16:22:13.304233 192.168.1.11:61273 -> 192.168.1.150:80
TCP TTL :128 TOS :0 x0 ID :28818 IpLen :20 DgmLen :52 DF
****** S* Seq: 0 x5F62CB19 Ack : 0x0 Win : 0 xFAF0 TcpLen : 32
TCP Options (6) => MSS: 1460 NOP WS: 8 NOP NOP SackOK
*/
// Snort Alert Example
/*
[**] [1:2009582:3] ET SCAN NMAP -sS window 1024 [**]
[ Classification : Attempted Information Leak ] [ Priority : 2]
10/30 -14:41:29.472407 192.168.1.230:43923 -> 192.168.1.150:111
TCP TTL :56 TOS :0 x0 ID :13589 IpLen :20 DgmLen :44
****** S* Seq: 0 x15754519 Ack : 0x0 Win : 0 x400 TcpLen : 24
TCP Options (1) => MSS: 1460
[ Xref => http :// doc. emergingthreats .net /2009582]
*/
var fs = require('fs ');
const readline = require('readline ');
var exec = require(' child_process ').exec;
var params = process.argv;
var iteration = parseInt(params.slice(2, 3));
var dir = "C:\\ Snort \\ log \\";
var individually = parseInt(params.slice(3, 4));
var lineCounter = 0;
const numLinesSnortAlert = 8;
var snortLogResults = [];
var found = false;
var indx = 0;
var lastAlert = "";

if (!fs.existsSync(dir + ' individually ' + iteration)) {
    fs.mkdirSync(dir + ' individually ' + iteration);
    fs.mkdirSync(dir + 'merged ' + iteration);
}

function execute(command, callback) {
    exec(command, function (error, stdout, stderr) {
        // process . send ( stdout );
        // process . send ( stderr );
        callback(stdout);
    });
};

var noop = function () { }; // do nothing .

function snortLog(output) {
    process.send(output);
}

async function processLineByLine() {
    const fileStream = fs.createReadStream(dir + '\\ alert .ids ');
    const rl = readline.createInterface({
        input: fileStream,
        crlfDelay: Infinity
    });

    // Note : we use the crlfDelay option to recognize all instances of CR LF
    // ('\r\n ') in input .txt as a single line break .
    for await (const line of rl) {
        try {
            // Type of Alert :[**] [1:10000005:2] NMAP TCP Scan [**]
            if (lineCounter % numLinesSnortAlert == 0) {
                var regex = /[\]]([ 0-9A-z]) +[\[]/g;
                var alert = line.match(regex);
                var alertType = alert[1].replace(']', ' ');
                alertType = alertType.replace('[', ' ');
                alertType = alertType.trim();
                // checks to see if alert is same as prev , so we can skip searching
                if (alertType == lastAlert) {
                    snortLogResults[indx].Count += 1;
                }
                else {
                    found = false;
                    for (var i = 0; i < snortLogResults.length; i++) {
                        if (snortLogResults[i].Type == alertType) {
                            found = true;
                            indx = i;
                            snortLogResults[i].Count += 1;
                            break;
                        }
                    }
                    if (found == false) {
                        snortLogResults.push({
                            Type: alertType, Count: 1,
                            StartDate: "", EndDate: "", StartTime: "", EndTime: "", Src: [],
                            Dst: []
                        });
                        found = true;
                        indx = snortLogResults.length - 1;
                        lastAlert = alertType;
                    }
                }
            }

            // Priority :[ Priority : 0]
            // else if ( lineCounter % numLinesSnortAlert == 1)
            //{
            // Each line in input .txt will be successively available here as `line `.
            // process . send (` Line from file : ${ line }`);
            //}
            // Timestamp and Src -> Dst '10/01 -16:22:13.304233 192.168.1.11:61273 -> 192.168.1.150:80 '
            else if (lineCounter % numLinesSnortAlert == 2) {
                var dateSrcDst = line.split(' ');
                var dateTime = dateSrcDst[0].split('-');
                var date = dateTime[0];
                var time = dateTime[1].split('.')[0];
                var src = dateSrcDst[1];
                var srcSplit = src.split(':');
                var srcIP = srcSplit[0];
                var srcPrt = parseInt(srcSplit[1], 10);
                var dst = dateSrcDst[3];
                var dstSplit = dst.split(':');
                var dstIP = dstSplit[0];
                var dstPrt = parseInt(dstSplit[1], 10);
                // first entry
                if (snortLogResults[indx].StartDate == "") {
                    snortLogResults[indx].StartDate = date;
                    snortLogResults[indx].StartTime = time;
                }
                else {
                    snortLogResults[indx].EndDate = date;
                    snortLogResults[indx].EndTime = time;
                }
                if (!snortLogResults[indx].Src.includes(src)) {
                    snortLogResults[indx].Src.push(src);
                }
                if (!snortLogResults[indx].Dst.includes(dst)) {
                    snortLogResults[indx].Dst.push(dst);
                }
                // process . send ( snortLogResults );
            }

            // TCP TTL :128 TOS :0 x0 ID :28818 IpLen :20 DgmLen :52 DF
            // else if ( lineCounter % numLinesSnortAlert == 3)
            //{
            // Each line in input .txt will be successively available here as `line `.
            // process . send (` Line from file : ${ line }`);
            //}
            // ****** S* Seq : 0 x5F62CB19 Ack : 0x0 Win : 0 xFAF0 TcpLen : 32
            // else if ( lineCounter % numLinesSnortAlert == 4)
            //{
            // Each line in input .txt will be successively available here as `line `.
            // process . send (` Line from file : ${ line }`);
            //}
            // TCP Options (6) => MSS : 1460 NOP WS: 8 NOP NOP SackOK
            else if (lineCounter % numLinesSnortAlert == 5) {
                // has 5 lines for alert instead of 6 or 7
                // modify by 2 to catch up
                if (!(line.includes('TCP Options '))) {
                    lineCounter += 2;
                }
            }
            else if (lineCounter % numLinesSnortAlert == 6) {
                // has 6 lines for alert instead of 7
                // modify by 1 to catch up
                if (!(line.includes('Xref '))) {
                    lineCounter += 1;
                }
            }
            // blank line between alerts
            // else if ( lineCounter % numLinesSnortAlert == 7)
            //{
            //}
            lineCounter += 1;
        }
process.send(snortLogResults);
    }
catch (err) {
        process.send(err)
    }
    // process . exit ()
}
var cmd = '"C:\\ Snort \\ bin \\ snort .exe" -c "C:\\ Snort \\ etc \\ snort .conf " ';
if (individually == 1) {
    dir = dir + ' individually ' + iteration;
    cmd = cmd + '--pcap - file "C:\\ Snort \\ log \\ pcaps .txt" --pcap - reset -l ' + dir;
}
else {
    dir = dir + 'merged ' + iteration;
    cmd = cmd + '-r "C:\\ Snort \\ log \\ merged ' + iteration + '. pcap " -l ' +
        dir;
}
execute(cmd, processLineByLine);
