reset
cd "/home/mquezada/git/cc6909/v2/data/"
file = "dvorak"
evento = "New York Philarmonic Dvoraks New World Symphony"
filename = sprintf('%s-domain-freqs.png', file)
datafile = sprintf('%s-domains.dat', file)
set title "Frecuencia relativa de dominios en evento \n".evento

set terminal pngcairo size 800,480 enhanced font 'CMU Typewriter Text,10'
#set terminal epslatex size 8.89cm,6.65cm color colortext

set style line 11 lc rgb '#000000' lt 1
set border 3 back ls 11
set tics nomirror
set style line 12 lc rgb '#000000' lt 0 lw 1
set grid back ls 12

#set logscale y
set yrange [0:*]

set output filename
set xlabel "Dominio"
set ylabel "Frecuencia relativa"
set grid
set size .99,1
set xtics border in scale 0,0 nomirror rotate by -45  offset character 0, 0, 0
set boxwidth 0.95 relative
set style fill transparent solid 0.5 noborder
plot "< head -30 ".datafile u 2:xticlabels(1) w boxes lc rgb"green" notitle