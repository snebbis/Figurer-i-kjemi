import csv
import io
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- INNSTILLINGEN SOM LÅSER TEKSTEN TIL PATHS I SVG ---
plt.rcParams['svg.fonttype'] = 'path' 
# -------------------------------------------------------

CSV_DATA = '''Atomnummer,Navn,Kjemisk symbol,Atommasse,Elektronfordeling,Tilstand ved romtemperatur,Farge_symbol,Type,Farge_rute
1,"Hydrogen","H",1.008,"1s1","gas","red","ikke-metall","blue"
2,"Helium","He",4.003,"1s2","gas","red","ikke-metall","blue"
3,"Litium","Li",6.941,"1s2 2s1","solid","black","metall","green"
4,"Beryllium","Be",9.012,"1s2 2s2","solid","black","metall","green"
5,"Bor","B",10.81,"1s2 2s2 2p1","solid","black","halv-metall","orange"
6,"Karbon","C",12.01,"1s2 2s2 2p2","solid","black","ikke-metall","blue"
7,"Nitrogen","N",14.01,"1s2 2s2 2p3","gas","red","ikke-metall","blue"
8,"Oksygen","O",16.00,"1s2 2s2 2p4","gas","red","ikke-metall","blue"
9,"Fluor","F",19.00,"1s2 2s2 2p5","gas","red","ikke-metall","blue"
10,"Neon","Ne",20.18,"1s2 2s2 2p6","gas","red","ikke-metall","blue"
11,"Natrium","Na",22.99,"1s2 2s2 2p6 3s1","solid","black","metall","green"
12,"Magnesium","Mg",24.31,"1s2 2s2 2p6 3s2","solid","black","metall","green"
13,"Aluminium","Al",26.98,"1s2 2s2 2p6 3s2 3p1","solid","black","metall","green"
14,"Silisium","Si",28.09,"1s2 2s2 2p6 3s2 3p2","solid","black","halv-metall","orange"
15,"Fosfor","P",30.97,"1s2 2s2 2p6 3s2 3p3","solid","black","ikke-metall","blue"
16,"Svovel","S",32.06,"1s2 2s2 2p6 3s2 3p4","solid","black","ikke-metall","blue"
17,"Klor","Cl",35.45,"1s2 2s2 2p6 3s2 3p5","gas","red","ikke-metall","blue"
18,"Argon","Ar",39.95,"1s2 2s2 2p6 3s2 3p6","gas","red","ikke-metall","blue"
19,"Kalium","K",39.10,"1s2 2s2 2p6 3s2 3p6 4s1","solid","black","metall","green"
20,"Kalsium","Ca",40.08,"1s2 2s2 2p6 3s2 3p6 4s2","solid","black","metall","green"
21,"Scandium","Sc",44.96,"1s2 2s2 2p6 3s2 3p6 4s2 3d1","solid","black","metall","green"
22,"Titan","Ti",47.87,"1s2 2s2 2p6 3s2 3p6 4s2 3d2","solid","black","metall","green"
23,"Vanadium","V",50.94,"1s2 2s2 2p6 3s2 3p6 4s2 3d3","solid","black","metall","green"
24,"Krom","Cr",52.00,"1s2 2s2 2p6 3s2 3p6 4s1 3d5","solid","black","metall","green"
25,"Mangan","Mn",54.94,"1s2 2s2 2p6 3s2 3p6 4s2 3d5","solid","black","metall","green"
26,"Jern","Fe",55.85,"1s2 2s2 2p6 3s2 3p6 4s2 3d6","solid","black","metall","green"
27,"Kobolt","Co",58.93,"1s2 2s2 2p6 3s2 3p6 4s2 3d7","solid","black","metall","green"
28,"Nikkel","Ni",58.69,"1s2 2s2 2p6 3s2 3p6 4s2 3d8","solid","black","metall","green"
29,"Kobber","Cu",63.55,"1s2 2s2 2p6 3s2 3p6 4s1 3d10","solid","black","metall","green"
30,"Sink","Zn",65.39,"1s2 2s2 2p6 3s2 3p6 4s2 3d10","solid","black","metall","green"
31,"Gallium","Ga",69.72,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p1","solid","black","metall","green"
32,"Germanium","Ge",72.63,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p2","solid","black","halv-metall","orange"
33,"Arsen","As",74.92,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p3","solid","black","halv-metall","orange"
34,"Selen","Se",78.96,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p4","solid","black","ikke-metall","blue"
35,"Brom","Br",79.90,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p5","liquid","blue","ikke-metall","blue"
36,"Krypton","Kr",83.80,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6","gas","red","ikke-metall","blue"
37,"Rubidium","Rb",85.47,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s1","solid","black","metall","green"
38,"Strontium","Sr",87.62,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2","solid","black","metall","green"
39,"Yttrium","Y",88.91,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d1","solid","black","metall","green"
40,"Zirkonium","Zr",91.22,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d2","solid","black","metall","green"
41,"Niob","Nb",92.21,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s1 4d4","solid","black","metall","green"
42,"Molybden","Mo",95.94,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s1 4d5","solid","black","metall","green"
43,"Technetium","Tc",97.91,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d5","solid","black","metall","green"
44,"Ruthenium","Ru",101.1,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s1 4d7","solid","black","metall","green"
45,"Rhodium","Rh",102.9,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s1 4d8","solid","black","metall","green"
46,"Palladium","Pd",106.4,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 4d10","solid","black","metall","green"
47,"Sølv","Ag",107.9,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s1 4d10","solid","black","metall","green"
48,"Kadmium","Cd",112.4,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10","solid","black","metall","green"
49,"Indium","In",114.8,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p1","solid","black","metall","green"
50,"Tinn","Sn",118.7,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p2","solid","black","metall","green"
51,"Antimon","Sb",121.8,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p3","solid","black","halv-metall","orange"
52,"Tellur","Te",127.6,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p4","solid","black","halv-metall","orange"
53,"Jod","I",126.9,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p5","solid","black","ikke-metall","blue"
54,"Xenon","Xe",131.3,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6","gas","red","ikke-metall","blue"
55,"Cesium","Cs",132.9,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s1","solid","black","metall","green"
56,"Barium","Ba",137.3,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2","solid","black","metall","green"
57,"Lantan","La",138.9,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 5d1","solid","black","metall","green"
58,"Cerium","Ce",140.1,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f1 5d1","solid","black","metall","green"
59,"Praseodym","Pr",140.9,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f3","solid","black","metall","green"
60,"Neodym","Nd",144.2,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f4","solid","black","metall","green"
61,"Promethium","Pm",144.9,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f5","solid","black","metall","green"
62,"Samarium","Sm",150.4,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f6","solid","black","metall","green"
63,"Europium","Eu",152.0,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f7","solid","black","metall","green"
64,"Gadolinium","Gd",157.3,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f7 5d1","solid","black","metall","green"
65,"Terbium","Tb",158.9,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f9","solid","black","metall","green"
66,"Dysprosium","Dy",162.5,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f10","solid","black","metall","green"
67,"Holmium","Ho",164.9,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f11","solid","black","metall","green"
68,"Erbium","Er",167.3,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f12","solid","black","metall","green"
69,"Thulium","Tm",168.9,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f13","solid","black","metall","green"
70,"Ytterbium","Yb",173.1,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14","solid","black","metall","green"
71,"Lutetium","Lu",175.0,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d1","solid","black","metall","green"
72,"Hafnium","Hf",178.5,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d2","solid","black","metall","green"
73,"Tantal","Ta",180.8,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d3","solid","black","metall","green"
74,"Wolfram","W",183.8,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d4","solid","black","metall","green"
75,"Rhenium","Re",186.2,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d5","solid","black","metall","green"
76,"Osmium","Os",190.2,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d6","solid","black","metall","green"
77,"Iridium","Ir",192.2,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d7","solid","black","metall","green"
78,"Platina","Pt",195.1,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s1 4f14 5d9","solid","black","metall","green"
79,"Gull","Au",197.0,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s1 4f14 5d10","solid","black","metall","green"
80,"Kvikksølv","Hg",200.6,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10","liquid","blue","metall","green"
81,"Thallium","Tl",204.4,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p1","solid","black","metall","green"
82,"Bly","Pb",207.2,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p2","solid","black","metall","green"
83,"Vismut","Bi",209.0,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p3","solid","black","metall","green"
84,"Polonium","Po",209.0,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p4","solid","black","halv-metall","orange"
85,"Astat","At",210.0,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p5","solid","black","ikke-metall","blue"
86,"Radon","Rn",222.0,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6","gas","red","ikke-metall","blue"
87,"Francium","Fr",223.0,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s1","solid","black","metall","green"
88,"Radium","Ra",226.0,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2","solid","black","metall","green"
89,"Actinium","Ac",227.0,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 6d1","solid","black","metall","green"
90,"Thorium","Th",232.0,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 6d2","solid","black","metall","green"
91,"Protactinium","Pa",231.0,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f2 6d1","solid","black","metall","green"
92,"Uran","U",238.0,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f3 6d1","solid","black","metall","green"
93,"Neptunium","Np",237.1,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f4 6d1","solid","black","metall","green"
94,"Plutonium","Pu",244.1,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f6","solid","black","metall","green"
95,"Americium","Am",243.1,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f7","solid","black","metall","green"
96,"Curium","Cm",247.1,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f7 6d1","solid","black","metall","green"
97,"Berkelium","Bk",247.1,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f9","solid","black","metall","green"
98,"Californium","Cf",251.1,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f10","solid","black","metall","green"
99,"Einsteinium","Es",252.1,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f11","solid","black","metall","green"
100,"Fermium","Fm",257.1,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f12","solid","black","metall","green"
101,"Mendelevium","Md",258.1,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f13","solid","black","metall","green"
102,"Nobelium","No",259.1,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f14","solid","black","metall","green"
103,"Lawrencium","Lr",262.1,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f14 7p1","solid","black","metall","green"
104,"Rutherfordium","Rf",268.1,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f14 6d2","solid","black","metall","green"
105,"Dubnium","Db",271.1,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f14 6d3","solid","black","metall","green"
106,"Seaborgium","Sg",265.1,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f14 6d4","solid","black","metall","green"
107,"Bohrium","Bh",270.0,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f14 6d5","solid","black","metall","green"
108,"Hassium","Hs",276.2,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f14 6d6","solid","black","metall","green"
109,"Meitnerium","Mt",277.2,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f14 6d7","solid","black","metall","green"
110,"Darmstadtium","Ds",281.2,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f14 6d8","solid","black","metall","green"
111,"Røntgenium","Rg",280.2,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f14 6d9","solid","black","metall","green"
112,"Copernicium","Cn",285.2,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f14 6d10","solid","black","metall","green"
113,"Nihonium","Nh",284.2,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f14 6d10 7p1","solid","black","metall","green"
114,"Flerovium","Fl",289.2,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f14 6d10 7p2","solid","black","metall","green"
115,"Moscovium","Mc",288.2,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 5d10 6p6 7s2 5f14 6d10 7p3","solid","black","metall","green"
116,"Livermorium","Lv",293.0,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 6d10 7p4","solid","black","metall","green"
117,"Tennessine","Ts",294.0,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 6d10 7p5","solid","black","metall","green"
118,"Oganesson","Og",294.0,"1s2 2s2 2p6 3s2 3p6 4s2 3d10 4p6 5s2 4d10 5p6 6s2 4f14 6d10 7p6","solid","black","metall","green"
'''

BG_COLORS = {'blue': '#BFD6E8', 'green': '#C5DEC0', 'orange': '#F4CFA0'}
SYM_COLORS = {'red': '#C53030', 'blue': '#1E5A9E', 'black': '#1A1A1A'}

def shell_distribution(config):
    shells = {}
    for tok in config.split():
        m = re.match(r'(\d+)[spdf](\d+)', tok)
        if m:
            n = int(m.group(1))
            c = int(m.group(2))
            shells[n] = shells.get(n, 0) + c
    return [shells[n] for n in sorted(shells.keys())]

def cell_position(z):
    if z == 1: return (14, 190-23-14)
    if z == 2: return (252, 190-23-14)
    if 3 <= z <= 4: return (14 + (z - 3) * 14, 190-37-14)
    if 5 <= z <= 10: return (182 + (z - 5) * 14, 190-37-14)
    if 11 <= z <= 12: return (14 + (z - 11) * 14, 190-51-14)
    if 13 <= z <= 18: return (182 + (z - 13) * 14, 190-51-14)
    if 19 <= z <= 36: return (14 + (z - 19) * 14, 190-65-14)
    if 37 <= z <= 54: return (14 + (z - 37) * 14, 190-79-14)
    if 55 <= z <= 56: return (14 + (z - 55) * 14, 190-93-14)
    if 57 <= z <= 71: return (42 + (z - 57) * 14, 190-125-14)
    if 72 <= z <= 86: return (56 + (z - 72) * 14, 190-93-14)
    if 87 <= z <= 88: return (14 + (z - 87) * 14, 190-107-14)
    if 89 <= z <= 103: return (42 + (z - 89) * 14, 190-139-14)
    if 104 <= z <= 118: return (56 + (z - 104) * 14, 190-107-14)
    return (0, 0)

def main():
    fig, ax = plt.subplots(figsize=(10.9, 7.48)) 
    ax.set_xlim(0, 277)
    ax.set_ylim(0, 190)
    ax.set_aspect('equal')
    ax.axis('off')

    reader = csv.DictReader(io.StringIO(CSV_DATA))
    
    for elem in reader:
        z = int(elem['Atomnummer'])
        x, y = cell_position(z)
        shells = shell_distribution(elem['Elektronfordeling'])
        
        rect = patches.Rectangle((x, y), 14, 14, facecolor=BG_COLORS.get(elem["Farge_rute"]), edgecolor='#333', linewidth=0.5)
        ax.add_patch(rect)
        
        main_x = x + 7.5
        
        # Atomnummer (Z)
        ax.text(x+12.5, y+11.4, str(z), fontsize=8, fontweight='bold', ha='right', va='center')
        
        # Kjemisk symbol
        ax.text(main_x, y+7.2, elem['Kjemisk symbol'], fontsize=12, fontweight='bold', ha='center', va='center', color=SYM_COLORS.get(elem["Farge_symbol"]))
        
        # Atommasse
        ax.text(main_x, y+3.3, elem['Atommasse'].replace('.', ','), fontsize=4, ha='center', va='center')
        
        # Navn
        ax.text(main_x, y+1.5, elem['Navn'], fontsize=3.5, ha='center', va='center')
        
        # Skalfordeling
        n_shells = len(shells)
        if n_shells == 7: s_y0, s_lh = 2.4, 1.45
        elif n_shells == 6: s_y0, s_lh = 2.7, 1.65
        else: s_y0, s_lh = 3.0, 1.8

        for i, s in enumerate(shells):
            ax.text(x+0.8, y+14-(s_y0 + i * s_lh), str(s), fontsize=4, ha='left', va='center')

    # GRUPPE OG PERIODE-MERKING
    ax.text(2.5, 190-21.8, "Gruppe", fontsize=6, fontweight='bold')
    for g in range(1, 19):
        gx = 14 + (g - 1) * 14 + 7
        ax.text(gx, 190-21.8, str(g), fontsize=7, fontweight='bold', ha='center')
    
    ax.text(3.5, 190-58, "Periode", fontsize=6, fontweight='bold', ha='center', rotation=90, va='center')
    for p in range(1, 8):
        py = 190-(23 + (p - 1) * 14 + 8)
        ax.text(11, py, str(p), fontsize=8, fontweight='bold', ha='center', va='center')

    ax.text(40, 190-133.5, "Lantanoidene", fontsize=6, fontweight='bold', ha='right', va='center')
    ax.text(40, 190-147.5, "Actinoidene", fontsize=6, fontweight='bold', ha='right', va='center')

    for py, txt in [(190-93-14, "57–71"), (190-107-14, "89–103")]:
        ax.add_patch(patches.Rectangle((42, py), 14, 14, facecolor='#E8E8E8', edgecolor='#333', linewidth=0.5))
        ax.text(42+7, py+7, txt, fontsize=6, fontweight='bold', ha='center', va='center')

    # FORKLARING (LEGEND)
    scale, sx, sy = 1.7, 68, 190-32-14*1.7
    ax.add_patch(patches.Rectangle((sx, sy), 14*scale, 14*scale, facecolor=BG_COLORS["green"], edgecolor='#333', linewidth=0.5))
    
    main_ex = sx + 7.5*scale
    ax.text(sx+12.5*scale, sy+11.4*scale, "20", fontsize=8*scale, fontweight='bold', ha='right', va='center')
    ax.text(main_ex, sy+7.2*scale, "Ca", fontsize=12*scale, fontweight='bold', ha='center', va='center')
    ax.text(main_ex, sy+3.3*scale, "40,08", fontsize=4*scale, ha='center', va='center')
    ax.text(main_ex, sy+1.5*scale, "Kalsium", fontsize=3.5*scale, ha='center', va='center')
    for i, s in enumerate([2, 8, 8, 2]):
        ax.text(sx+0.8*scale, sy+14*scale-(3.0 + i * 1.8)*scale, str(s), fontsize=4*scale, ha='left', va='center')

    tx = sx + 13*scale + 8.5
    labels = [
        ("Atomnummer", 11.4, 11.5), 
        ("Symbol", 7.2, 10.5),      
        ("Atommasse", 3.3, 11.5),   
        ("Navn", 1.5, 10.5)          
    ]
    for txt, y_cell, x_target in labels:
        y_abs = sy + y_cell * scale
        ax.annotate(txt, xy=(sx + x_target*scale, y_abs), xytext=(tx, y_abs),
                    arrowprops=dict(arrowstyle="-", lw=0.5, color='#555'), fontsize=6, va='center')
    
    ax.text(sx-3, sy+14*scale-5.5*scale, "Elektron-\nfordeling", fontsize=6, ha='right', va='center')

    type_x, type_y0 = 125, 190-33
    for i, (color, label) in enumerate([(BG_COLORS['green'], 'Metall'), (BG_COLORS['blue'], 'Ikke-metall'), (BG_COLORS['orange'], 'Halvmetall')]):
        ax.add_patch(patches.Rectangle((type_x, type_y0 - i*8 - 6), 6, 6, facecolor=color, edgecolor='#333', linewidth=0.5))
        ax.text(type_x + 8, type_y0 - i*8 - 3, label, fontsize=7, va='center')

    state_x, state_y0 = 158, 190-33
    for i, (col, sym, lab) in enumerate([(SYM_COLORS['red'], 'H', 'Gassform'), (SYM_COLORS['blue'], 'Br', 'Flytende'), (SYM_COLORS['black'], 'Li', 'Fast form')]):
        ax.text(state_x, state_y0 - i*8 - 3, sym, fontsize=10, fontweight='bold', color=col, ha='center', va='center')
        ax.text(state_x + 5, state_y0 - i*8 - 3, lab, fontsize=7, va='center')

    ax.text(138.5, 180, "GRUNNSTOFFENES PERIODESYSTEM", fontsize=14, fontweight='bold', ha='center')

    plt.savefig('periodesystem.svg', format='svg', bbox_inches='tight', pad_inches=0)
    print("Ferdig! Scriptet har nå rettet datatypoen og generert en perfekt SVG.")

if __name__ == '__main__':
    main()