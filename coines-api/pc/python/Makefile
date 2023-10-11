COMPILER_PREFIX ?=
CC = $(COMPILER_PREFIX)gcc
LD = $(COMPILER_PREFIX)gcc
TARGET = PC
COINES_INSTALL_PATH ?= ../../../

# On using Software reset API(coines_soft_reset()) from COINES, After reset device jumps to the address specified in APP_START_ADDRESS.
export APP_START_ADDRESS ?= 0x00030000

ARCH = $(shell $(CC) -dumpmachine)

ifneq (,$(findstring x86_64,$(ARCH)))
     SUFFIX = 64
else
     SUFFIX = 32
endif

ifeq ($(OS),Windows_NT)
    PLATFORM = windows
    DRIVER = LEGACY_USB_DRIVER
    CFLAGS += -D PLATFORM_WINDOWS -std=c99 -DAPP_START_ADDRESS=$(APP_START_ADDRESS)
    VARIANT = win$(SUFFIX)
    EXT = dll
    LIBS += setupapi
    ifeq ($(notdir $(MAKE)),mingw32-make)
        SHELL = cmd
        RM  = del /s /q
        MKDIR = mkdir
        syspath = $(subst /,\,$(1))
    else
        RM = rm -rf
        MKDIR = mkdir -p
        syspath = $(subst /,/,$(1))
    endif
else
    PLATFORM = unix
    DRIVER = LIBUSB_DRIVER
    CFLAGS += -D PLATFORM_LINUX -fPIC -std=c99 -DAPP_START_ADDRESS=$(APP_START_ADDRESS)
    ifeq ($(shell uname -s),Linux)
        EXT = so
        VARIANT = linux$(SUFFIX)
    else ifeq ($(shell uname -s),Darwin)
        EXT = dylib
        VARIANT = mac$(SUFFIX)
    endif

    ifeq ($(COINES_BACKEND),COINES_BRIDGE)
        ifeq ($(shell uname -s),Linux)
            HOST_OS = Linux
        else ifeq ($(shell uname -s),Darwin)
            HOST_OS = Darwin
        endif
        ifeq ($(shell uname -m),x86_64)
            HOST_ARCH = x64
        else ifneq ($(filter %86 ,$(shell uname -m)),)
            HOST_ARCH = x86
        endif

        DRIVER = LIBUSBP_DRIVER

        LIB_PATH = $(COINES_INSTALL_PATH)/coines-api/pc/serial_com/libusbp-1.0
        LIB_PATH_ARCH += $(LIB_PATH)/$(HOST_OS)/$(HOST_ARCH)
    else
        DRIVER = LIBUSB_DRIVER
        INCLUDEPATHS_COINES += comm_driver/libusb-1.0
    endif

    ifeq ($(DRIVER),LIBUSB_DRIVER)
        LIBS += usb-1.0
    endif

    ifeq ($(DRIVER),LIBUSBP_DRIVER)
        ifeq ($(HOST_OS),Linux)
            EXTRA_LIBS += -l:libusbp-1.a
            EXTRA_LIBS += -ludev
        endif
        ifeq ($(HOST_OS),Darwin)
            EXTRA_LIBS += -framework IOKit -framework CoreFoundation
            EXTRA_LIBS += $(LIB_PATH_ARCH)/libusbp-1.a
        endif
    endif

    MKDIR = mkdir -p
    RM  = rm -rf
    syspath = $(subst /,/,$(1))

endif

LIBPATHS += \
$(LIB_PATH_ARCH) \
$(COINES_INSTALL_PATH)/coines-api \

OBJ_DIR = build/$(VARIANT)

SRC_DIR = ..

ifeq ($(COINES_BACKEND),COINES_BRIDGE)
    C_SRCS_COINES += \
    coines_bridge.c \
    serial_com/serial_com.c \
    ble_com/simpleble_lib_loader.c \
    ble_com/ble_com.c 

    INCLUDEPATHS_COINES += \
    . \
    .. \
    serial_com \
    ble_com \
    ble_com/simpleble-0.6.0/simpleble_c

else
    CFLAGS += -D $(DRIVER)

    C_SRCS_COINES += \
    coines.c \
    comm_intf/comm_intf.c \
    comm_intf/comm_ringbuffer.c \
    comm_driver/usb.c

    ifeq ($(PLATFORM), windows)
        C_SRCS_COINES += \
        comm_driver/legacy_usb/legacy_usb_support.c
    endif

    INCLUDEPATHS_COINES += \
    . \
    .. \
    coines_api \
    comm_intf \
    comm_driver \
    comm_driver/legacy_usb

endif

C_SRCS = $(addprefix $(SRC_DIR)/,$(C_SRCS_COINES))
INCLUDEPATHS = $(addprefix $(SRC_DIR)/,$(INCLUDEPATHS_COINES))

C_FILES = $(notdir $(C_SRCS))
C_OBJS = $(addprefix $(OBJ_DIR)/, $(C_FILES:.c=.c.o))
C_PATHS = $(sort $(dir $(C_SRCS)))
DEP = $(C_OBJS:%.o=%.d)

vpath %.c $(C_PATHS)

CFLAGS += -c -D $(TARGET)

# Define COINES_VERSION as Git revision string, if
# - Git is installed
# - it was run inside a Git repository
ifneq ($(shell $(WHERE) git) ,)
GIT_REVISION_STRING = $(shell git describe  --always --dirty --tags)
ifneq ($(GIT_REVISION_STRING),)
CFLAGS += -D COINES_VERSION=\"$(GIT_REVISION_STRING)\"
endif
endif

LDFLAGS += -shared

SHARED_LIB += coinespy/libcoines_$(SUFFIX).$(EXT)

all: $(SHARED_LIB)
	@echo CFLAGS_SAVE = $(CFLAGS) > $(OBJ_DIR)/cflags.save

$(OBJ_DIR):
	@echo [ MKDIR ] $@
	@$(MKDIR) $(call syspath,$@)

$(SHARED_LIB): $(OBJ_DIR) $(C_OBJS)
	@echo [ LD ] $@
	@$(CC) $(LDFLAGS) -o "$@" $(C_OBJS) $(addprefix -L,$(LIBPATHS)) $(addprefix -l,$(LIBS)) $(EXTRA_LIBS)

-include $(DEP)

$(OBJ_DIR)/%.c.o: %.c
	@echo [ CC ] $<
	@$(CC) $(CFLAGS) -MMD -I . $(addprefix -I,$(INCLUDEPATHS)) -o "$@" "$<"

clean:
	@echo "Cleaning..."
	@$(RM) $(call syspath,$(SHARED_LIB)) build