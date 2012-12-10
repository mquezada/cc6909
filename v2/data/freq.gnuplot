reset
file = "fujimori"
evento = "La presion politica esta enturbiando el indulto a Fujimori"
filename = sprintf('%s-domain-freqs.tex', file)
datafile = sprintf('%s-domain-freqs.dat', file)
set title "Frecuencia de dominios en evento \n".evento

#set terminal pngcairo size 800,480 enhanced font 'CMU Typewriter Text,10'
set terminal epslatex size 8.89cm,6.65cm color colortext

set style line 11 lc rgb '#000000' lt 1
set border 3 back ls 11
set tics nomirror
set style line 12 lc rgb '#000000' lt 0 lw 1
set grid back ls 12

#set logscale y
set yrange [0:12]

set output filename
set xlabel "Dominio"
set ylabel "Frecuencia en documentos"
set grid
set size .99,1
set xtics border in scale 0,0 nomirror rotate by -45  offset character 0, 0, 0
set boxwidth 0.95 relative
set style fill transparent solid 0.5 noborder
plot datafile u 2:xticlabels(1) w boxes lc rgb"green" notitle