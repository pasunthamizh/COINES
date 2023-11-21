
echo positive case
file_common -l 2
file_common -w Sensor.txt "Pressure Sensor OK"
file_common -a Sensor.txt " Pressure value = 25psi"
file_common -r Sensor.txt 5
file_common -s Sensor.txt
file_common -d Sensor.txt

echo negative  case
file_common -d Sensor.txt
file_common -a Sensor.txt " Pressure value = 25psi"
file_common -l -5
file_common -w Sensor.txt ""
file_common -r Sensor.txt -1
file_common -s Sensor1.txt 

echo cornor case
file_common -l 0
file_common -r Sensor.txt 100
pause
