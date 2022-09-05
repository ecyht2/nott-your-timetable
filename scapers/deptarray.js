#!/usr/bin/env node
const fs = require("node:fs");

var deptarray = new Array(35);
for (var i=0; i<deptarray.length; i++) {
    deptarray[i] = new Array(1);
}

deptarray[0] [0] = "Central";
deptarray[0] [1] = "%23SPLUS2";
deptarray[1] [0] = "Chem & EE";
deptarray[1] [1] = "MSC-CEE";
deptarray[2] [0] = "Civ Eng";
deptarray[2] [1] = "MSC-CIVE";
deptarray[3] [0] = "E & EE";
deptarray[3] [1] = "MSC-EEE";
deptarray[4] [0] = "MMME";
deptarray[4] [1] = "MSC-MMME";
deptarray[5] [0] = "App Math";
deptarray[5] [1] = "MSC-AMATH";
deptarray[6] [0] = "Biosci";
deptarray[6] [1] = "MSC-BIOSCI";
deptarray[7] [0] = "Comp Sci";
deptarray[7] [1] = "MSC-CS";
deptarray[8] [0] = "Pharmacy";
deptarray[8] [1] = "MSC-PHARM";
deptarray[9] [0] = "App Psych";
deptarray[9] [1] = "MSC-APPPSY";
deptarray[10] [0] = "NUBS";
deptarray[10] [1] = "MSC-NUBS";
deptarray[11] [0] = "Education";
deptarray[11] [1] = "MSC-ED";
deptarray[12] [0] = "Law";
deptarray[12] [1] = "005011";
deptarray[13] [0] = "C of EL";
deptarray[13] [1] = "MSC-CEL";
deptarray[14] [0] = "No Subject";
deptarray[14] [1] = "005014";
deptarray[15] [0] = "Psychology";
deptarray[15] [1] = "MSC-PSGY";
deptarray[16] [0] = "MLC";
deptarray[16] [1] = "MSC-MLC";
deptarray[17] [0] = "English Language Education";
deptarray[17] [1] = "005017";
deptarray[18] [0] = "Eng (Fn)";
deptarray[18] [1] = "MSC-ENGF";
deptarray[19] [0] = "Sci (F)";
deptarray[19] [1] = "MSC-SCIF";
deptarray[20] [0] = "Economics";
deptarray[20] [1] = "MSC-ECON";
deptarray[21] [0] = "Bus & M F";
deptarray[21] [1] = "MSC-BMF";
deptarray[22] [0] = "Art & Ed F";
deptarray[22] [1] = "MSC-AEF";
deptarray[23] [0] = "Pol, H, IR";
deptarray[23] [1] = "MSC-PHIR";
deptarray[24] [0] = "SoE&GS";
deptarray[24] [1] = "MSC-GEOG";
deptarray[25] [0] = "GSD (MSC)";
deptarray[25] [1] = "MSC-GSD";
deptarray[26] [0] = "American and Canadian Studies";
deptarray[26] [1] = "005024";
deptarray[27] [0] = "Computer Science - (Foundation)";
deptarray[27] [1] = "005025";
deptarray[28] [0] = "Biosciences - (Foundation)";
deptarray[28] [1] = "005027";
deptarray[29] [0] = "Biom Sci";
deptarray[29] [1] = "MSC-BIOMED";
deptarray[30] [0] = "Eng Fac";
deptarray[30] [1] = "MSC-ENGFAC";
deptarray[31] [0] = "UNMC";
deptarray[31] [1] = "UNMC";
deptarray[32] [0] = "Science";
deptarray[32] [1] = "MFY-SCI";
deptarray[33] [0] = "English";
deptarray[33] [1] = "MSC-ENGL";
deptarray[34] [0] = "GSD (MDD)";
deptarray[34] [1] = "MDD-GSD";
deptarray.sort();

let obj = new Object();
for (var i of deptarray) {
  obj[i[0]] = i[1];
}

let str = JSON.stringify(obj, null, 2);
fs.writeFileSync('dept.json', str);
