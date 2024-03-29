
# definition of the Eternity II puzzle pieces

# pieces are numbered 1..256
# color coding: X = border, A..Q = sides
# encoding is clockwise, start at the top

# source: https://github.com/AntonFagerberg/Eternity-II-Puzzle-Solver/blob/master/Eternity2.java

# TODO: verify against own set

# noinspection SpellCheckingInspection
PIECES = [
    "AQXX",     # 1 = first corner
    "AEXX",
    "IQXX",
    "QIXX",     # 4 = last corner
    "BAXA",     # 5 = first border
    "JIXA",
    "FAXA",
    "FMXA",
    "KQXA",
    "GEXA",
    "OIXA",
    "HEXA",
    "HMXA",
    "UEXA",
    "JAXI",
    "RQXI",
    "NMXI",
    "SMXI",
    "GIXI",
    "OIXI",
    "DEXI",
    "LAXI",
    "LMXI",
    "TAXI",
    "UAXI",
    "BIXQ",
    "BQXQ",
    "JQXQ",
    "RQXQ",
    "GMXQ",
    "OIXQ",
    "TQXQ",
    "HIXQ",
    "HEXQ",
    "PMXQ",
    "VEXQ",
    "RAXE",
    "CMXE",
    "KMXE",
    "SIXE",
    "SQXE",
    "OAXE",
    "OIXE",
    "OQXE",
    "DAXE",
    "TEXE",
    "HEXE",
    "PEXE",
    "BMXM",
    "JAXM",
    "JIXM",
    "FAXM",
    "GEXM",
    "DEXM",
    "DMXM",
    "HQXM",
    "PAXM",
    "PMXM",
    "UIXM",
    "VQXM",     # 60 = last border
    "FRBB",
    "NGBB",
    "JCBJ",
    "BHBR",
    "RVBR",
    "NNBR",
    "KJBR",
    "TFBR",
    "VHBR",
    "CGBC",
    "GLBC",
    "NRBK",
    "ODBK",
    "TOBK",
    "HCBK",
    "NOBS",
    "SOBS",
    "CPBG",
    "TCBG",
    "PUBG",
    "SRBO",
    "RRBD",
    "KDBD",
    "RSBL",
    "FNBL",
    "HLBL",
    "PTBL",
    "BUBT",
    "FVBT",
    "DPBT",
    "KLBH",
    "SOBH",
    "SDBH",
    "DUBH",
    "LNBH",
    "UCBU",
    "DSBV",
    "THBV",
    "UFBV",
    "VUBV",
    "LOJJ",
    "LPJJ",
    "PSJJ",
    "VFJJ",
    "DOJR",
    "CHJF",
    "SHJF",
    "DOJF",
    "PKJF",
    "OLJN",
    "LOJN",
    "TSJC",
    "TPJC",
    "NDJK",
    "GLJK",
    "LKJK",
    "VPJK",
    "CUJS",
    "PLJG",
    "HVJO",
    "NVJD",
    "FPJT",
    "NSJT",
    "TOJT",
    "LVJH",
    "UOJH",
    "NFJP",
    "SUJP",
    "DCJP",
    "THJP",
    "FTJU",
    "LNJU",
    "NPJV",
    "KDJV",
    "DCJV",
    "PTJV",
    "TGRR",
    "FCRF",
    "FKRF",     # 139 = center hint
    "FLRF",
    "SURF",
    "OFRF",
    "PLRF",
    "UURF",
    "CDRN",
    "RLRC",
    "RVRC",
    "CNRC",
    "OLRC",
    "FKRS",
    "DVRS",
    "KKRG",
    "KSRG",
    "VPRG",
    "GGRD",
    "GLRD",
    "VGRD",
    "GPRT",
    "HFRT",
    "UURH",
    "FTRP",
    "NTRP",
    "OKRV",
    "DPRV",
    "CDFN",
    "DHFN",
    "CCFK",
    "KOFS",
    "SUFS",
    "DHFG",
    "TPFG",
    "UKFG",
    "OOFO",
    "LTFO",
    "GUFD",
    "GSFL",
    "NDFT",
    "LPFH",
    "HOFH",
    "GPFP",
    "KPFU",
    "GKFU",
    "SHNN",
    "VGNC",
    "SLNK",
    "HHNK",
    "UGNS",
    "NUNG",
    "CSNG",
    "PSNG",
    "CCNO",
    "OTNO",
    "KGND",
    "UKNL",
    "UVNL",
    "VONL",
    "KVNT",
    "SHNT",
    "TTNT",
    "SCNH",
    "UHNP",
    "VGNP",
    "LSNU",
    "LHNU",
    "PCNU",
    "VUNU",
    "VGCC",
    "SVCK",
    "HOCK",
    "KSCG",
    "POCG",
    "CPCO",
    "HHCD",
    "CTCL",
    "DVCL",
    "VUCL",
    "SOCT",
    "DLCP",
    "KDCU",
    "KPCV",
    "UUCV",
    "UVCV",
    "LVKK",
    "TGKK",
    "POKK",
    "SOKG",
    "LLKG",
    "SHKD",
    "GVKT",
    "PHKT",
    "LTKH",
    "LUKH",
    "STSS",
    "PDSG",
    "GDSD",
    "GTSD",
    "LOSD",
    "DPSL",
    "OVST",
    "UOST",
    "GUSH",
    "DUSH",
    "OLGO",
    "THGO",
    "VTGD",
    "PVGU",
    "UVOO",
    "LDOD",
    "DUOL",
    "PUOT",
    "VHDD",
    "HLDL",
    "PTLH",
    "UPTP",
    "PVTV",
    "UVHV",     # 256 = last piece
]

EXTERNAL_BORDER = "X"
INTERNAL_BORDER_SIDES = "AEIMQ"
INTERNAL_SIDES = "BCDFGHJKLNOPRSTUV"


# end of file
