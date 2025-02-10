all : bin/main

bin/main : source/main.cpp source/object.cpp source/vision.cpp source/processing.cpp
	g++ $^ -o $@ `pkg-config --cflags --libs opencv4` -Iinclude

bin/P1 : source/P1.cpp source/object.cpp
	g++  $^ -o $@ `pkg-config --cflags --libs opencv4` -Iinclude

bin/P2 : source/P2.cpp source/processing.cpp
	g++ $^ -o $@ `pkg-config --cflags --libs opencv4` -Iinclude

bin/P4 : source/P4.cpp source/processing.cpp source/vision.cpp
	g++ $^ -o $@ `pkg-config --cflags --libs opencv4` -Iinclude

bin/P5 : source/P5.cpp source/object.cpp
	g++  $^ -o $@ `pkg-config --cflags --libs opencv4` -Iinclude

clean: 
	rm -rf bin/*