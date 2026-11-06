# duml_c -- DUML v1 protocol library (C++17). No external dependencies.
#
#   make            build libduml.a + duml_cli
#   make test       build and run the unit tests
#   make examples   build the example programs
#   make clean
#
# Serial transport uses POSIX termios (macOS/Linux). On other platforms,
# build with DUML_NO_SERIAL=1 to exclude it.

CXX      ?= c++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -Iinclude
AR       ?= ar

LIB_SRCS = src/crc.cpp src/enums.cpp src/frame.cpp src/codecs.cpp src/registry.cpp \
           generated/registry_data.cpp src/transport_stream.cpp src/transport_tcp.cpp \
           src/client.cpp
ifndef DUML_NO_SERIAL
LIB_SRCS += src/transport_serial.cpp
endif
LIB_OBJS = $(LIB_SRCS:%.cpp=build/%.o)

TEST_SRCS = tests/test_frame.cpp tests/test_codecs.cpp tests/test_registry.cpp tests/test_client.cpp
TEST_BINS = $(TEST_SRCS:tests/%.cpp=build/tests/%)

EXAMPLES = build/examples/send_gimbal_control build/examples/listen_and_decode

all: build/libduml.a build/duml_cli

build/%.o: %.cpp
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -c $< -o $@

build/libduml.a: $(LIB_OBJS)
	$(AR) rcs $@ $^

build/duml_cli: tools/duml_cli.cpp build/libduml.a
	$(CXX) $(CXXFLAGS) $< build/libduml.a -lpthread -o $@

build/tests/%: tests/%.cpp tests/test_harness.hpp build/libduml.a
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -Itests $< build/libduml.a -lpthread -o $@

test: $(TEST_BINS)
	@for t in $(TEST_BINS); do echo "== $$t"; ./$$t || exit 1; done

build/examples/%: examples/%.cpp build/libduml.a
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) $< build/libduml.a -lpthread -o $@

examples: $(EXAMPLES)

clean:
	rm -rf build

.PHONY: all test examples clean
