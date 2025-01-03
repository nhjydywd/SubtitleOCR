cd ../subocr-alg &&
# if [  -d "build" ]; then
#     rm -r build
# fi &&
# mkdir build &&
if [ ! -d "build" ]; then
    mkdir build
fi &&
cd build &&
cmake .. &&
make &&
make install