all : bin/main

bin/main : source/main.cpp source/object.cpp source/vision.cpp source/processing.cpp  source/config.cpp
	mkdir -p bin
	g++ $^ -o $@ `pkg-config --cflags --libs opencv4` -Iinclude

clean: 
	rm -rf bin/*