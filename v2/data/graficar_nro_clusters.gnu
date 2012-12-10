reset
cd "/home/mquezada/git/cc6909/v2/data/"
set terminal pngcairo size 800,480 enhanced font 'CMU Typewriter Text,10'


filename = "telaviv.clusters"
fileout = "telaviv-clusters.tex"
fileout2 = "telaviv-clusters-radio.tex"
event = "Police arrest suspects in Tel Aviv"

set output fileout

# similitudes
set title sprintf("Numero de clusters vs Medidas de similitud \n Evento: \"%s\"", event)
set xlabel "Numero de clusters"
set ylabel "Similitud"

set yrange[*:*]

set style line 11 lc rgb '#000000' lt 1
set style line 12 lc rgb '#000000' lt 0 lw 1

set style func linespoints

set border 3 back ls 11
set tics nomirror
set grid back ls 12

set style fill transparent solid 0.5 noborder
plot filename using 1:2 lt -1 pi -4 pt 6 title "ISim", \
     filename using 1:3 lt -1 pi -3 pt 4 title "ESim"


# radio
set output fileout2
plot filename using 1:4 lt -1 pi -3 pt 4 title "ISim/Esim"