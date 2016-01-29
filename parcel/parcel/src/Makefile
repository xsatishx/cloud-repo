C++ := g++
GCC := gcc

APP = parcel

ifndef os
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Linux)
		os = LINUX
    endif
    ifeq ($(UNAME_S),Darwin)
		os = UNIX
    endif
endif

################################################################################
# Paths
################################################################################
# The name of the library
  SO_NAME         = lparcel.so
# The full instal path of the library
  SO_PATH         = $(abspath $(dir mkfile_path))/$(SO_NAME)
# Include directories
  INC_DIRS        = udt4/src

################################################################################
# UDT
################################################################################
# The udt source directory
  UDT_DIR         = $(abspath $(dir mkfile_path))/udt4/src
# The udt library name
  _UDT_OBJECTS    = api.o buffer.o cache.o ccc.o channel.o common.o \
					core.o epoll.o list.o md5.o packet.o queue.o window.o
# Construct the full path to local udt library
  UDT_OBJECTS     = $(patsubst %,$(UDT_DIR)/%,$(_UDT_OBJECTS))

################################################################################
# Dependencies
################################################################################
# Construct all depencency paths
  DEP_DIRS        = $(UDT_DIR)
# Construct all depencency objects
  DEP_OBJS        = $(UDT_OBJECTS)

################################################################################
# Compiler flags
################################################################################
# Construct include flags from INC_DIRS and dependencies
  INCLUDES        = $(patsubst %,-I%,$(INC_DIRS)) $(patsubst %,-I%,$(DEP_DIRS))
# Optimization flags
  OPTFLAGS        = -finline-functions -O3
# Error flags
  ERRFLAGS        = -Wall
# File system flags
  FSFLAGS         = -D_LARGE_FILE_SOURCE=1
# Misc flags
  MISCFLAGS       = -g -fPIC -static
# Construct compiler flags
  CCFLAGS         = $(INCLUDES) $(OPTFLAGS) $(FSFLAGS) $(ERRFLAGS) $(MISCFLAGS) -D$(os)
ifeq ($(os), LINUX)
# LD linking flags
  LDFLAGS         = -lstdc++ -lpthread -lm -ludt $(patsubst %,-L%,$(INC_DIRS))
# Other linking flags
  LINK_FLAGS      = -shared -Wl,-soname,lparcel.so
endif
ifeq ($(os), UNIX)
# LD linking flags
  LDFLAGS         = -lstdc++ $(patsubst %,-L%,$(INC_DIRS))
# Other linking flags
  LINK_FLAGS      = -shared -Wl,-install_name,lparcel.so
endif

################################################################################
# Library objects
################################################################################
  OBJECTS         = transcribers.o udt2tcp.o tcp2udt.o cbuffer.o

################################################################################
# OS options
################################################################################

ifndef arch
   arch = IA32
endif

ifeq ($(arch), IA32)
    CCFLAGS += -DIA32
endif

ifeq ($(arch), POWERPC)
   CCFLAGS += -mcpu=powerpc
endif

ifeq ($(arch), IA64)
   CCFLAGS += -DIA64
endif

ifeq ($(arch), SPARC)
   CCFLAGS += -DSPARC
endif

ifeq ($(os), SUNOS)
   LDFLAGS += -lrt -lsocket
endif

################################################################################
# Build library
################################################################################

all: $(APP)

%.o: %.c
	$(GCC) $(CCFLAGS) $(LDFLAGS) $< -o $@ -c

%.o: %.cpp
	$(C++) $(CCFLAGS) $(LDFLAGS) $< -o $@ -c

parcel: $(OBJECTS) $(DEP_OBJS)
	$(C++) $(LINK_FLAGS) -o $(SO_PATH) $(DEP_OBJS) $(OBJECTS) $(LIBS)

################################################################################
# Build dependencies
################################################################################

$(UDT_OBJECTS):
	make -C udt4/src os=$(os)

################################################################################
# Manage library
################################################################################

clean:
	rm -f $(OBJECTS) $(DEP_OBJS) $(SO_NAME)
