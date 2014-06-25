#Convert all tif files in directory to png
#Useful when putting tif sem images into report directory

for img in *.tif; do
    filename=${img%.*}
    convert -quiet "$filename.tif" "$filename.png"
    echo "Converting $filename.tif to $filename.png"
done
echo " :::: Now arrange files by type :::: "
