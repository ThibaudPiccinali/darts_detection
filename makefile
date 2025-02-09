all : bin/P2

bin/main : source/main.cpp
	g++ $^ -o $@ `pkg-config --cflags --libs opencv4`

bin/P2 : source/P2.cpp source/processing.cpp
	g++ $^ -o $@ `pkg-config --cflags --libs opencv4` -Iinclude

bin/P4 : source/P4.cpp source/processing.cpp source/vision.cpp
	g++ $^ -o $@ `pkg-config --cflags --libs opencv4` -Iinclude -I/usr/include/eigen3

bin/P5 : source/P5.cpp source/object.cpp
	g++  $^ -o $@ -Iinclude

clean: 
	rm -rf bin/*