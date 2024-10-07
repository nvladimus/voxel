# Copyright Euresys 2020

"""Generated helpers for internal use."""

import ctypes as ct
import os
import platform
import sys

from .errors import errorCheck, MissingSymbol


def get_arch():
    arch = platform.machine().lower()
    if arch.startswith("i") and arch.endswith("86"):
        return "x86"
    elif arch == "amd64":
        return "x86_64"
    elif arch == "arm64":
        arch = "aarch64"
    return arch


def get_library_name(name):
    system = platform.system().lower()
    arch = get_arch()
    if system == "darwin":
        lib_name = "lib%s.dylib" % name
        lib_path = "/usr/local/opt/euresys/egrabber/lib/" + arch
    elif system == "linux":
        lib_name = "lib%s.so" % name
        lib_path = "/opt/euresys/egrabber/lib/" + arch
    else:
        lib_name = "%s.dll" % name
        lib_path = r"C:\Program Files%s\Euresys\eGrabber\cti\%s" % (" (x86)" if arch == "x86" else "", arch)
    bits = "64" if sys.maxsize > 2**32 else "32"
    lib_env = os.environ.get("EURESYS_%s_LIB%s" % (name.upper(), bits))
    lib_path = lib_env if lib_env else os.environ.get("EURESYS_EGRABBER_LIB" + bits, lib_path)
    return os.path.join(lib_path, lib_name)


class DynamicLibrary:
    def __init__(self, path):
        self.path = path
        self._dll = ct.CDLL(path)

    def __getattr__(self, name):
        try:
            return getattr(self._dll, name)
        except AttributeError:
            raise MissingSymbol(self.path, name)


dll = DynamicLibrary(get_library_name("egrabber"))


# Opaque types
class Eur_Buffer(ct.c_void_p):
    pass


class Eur_BufferIndexRange(ct.c_void_p):
    pass


class Eur_BufferInfo(ct.c_void_p):
    pass


class Eur_BusMemory(ct.c_void_p):
    pass


class Eur_CicData(ct.c_void_p):
    pass


class Eur_CxpDeviceData(ct.c_void_p):
    pass


class Eur_CxpInterfaceData(ct.c_void_p):
    pass


class Eur_DataStreamData(ct.c_void_p):
    pass


class Eur_DeviceErrorData(ct.c_void_p):
    pass


class Eur_EGenTL(ct.c_void_p):
    pass


class Eur_EGrabberBase(ct.c_void_p):
    pass


class Eur_EGrabberCameraInfo(ct.c_void_p):
    pass


class Eur_EGrabberDiscovery(ct.c_void_p):
    pass


class Eur_EGrabberInfo(ct.c_void_p):
    pass


class Eur_EGrabber_CallbackMultiThread(ct.c_void_p):
    pass


class Eur_EGrabber_CallbackOnDemand(ct.c_void_p):
    pass


class Eur_EGrabber_CallbackSingleThread(ct.c_void_p):
    pass


class Eur_GenTLMemory(ct.c_void_p):
    pass


class Eur_InfoCommandInfo(ct.c_void_p):
    pass


class Eur_IoToolboxData(ct.c_void_p):
    pass


class Eur_NewBufferData(ct.c_void_p):
    pass


class Eur_NvidiaRdmaMemory(ct.c_void_p):
    pass


class Eur_OneOfAll(ct.c_void_p):
    pass


class Eur_RemoteDeviceData(ct.c_void_p):
    pass


class Eur_UserMemory(ct.c_void_p):
    pass


class Eur_UserMemoryArray(ct.c_void_p):
    pass


class Eur_action_GenApiActionBuilder(ct.c_void_p):
    pass


class Eur_client_error(ct.c_void_p):
    pass


class Eur_cti_loading_error(ct.c_void_p):
    pass


class Eur_genapi_error(ct.c_void_p):
    pass


class Eur_gentl_error(ct.c_void_p):
    pass


class Eur_internal_error(ct.c_void_p):
    pass


class Eur_missing_gentl_symbol(ct.c_void_p):
    pass


class Eur_not_allowed(ct.c_void_p):
    pass


class Eur_query_GenApiQueryBuilder(ct.c_void_p):
    pass


class Eur_thread_error(ct.c_void_p):
    pass


class Eur_unexpected_data_size(ct.c_void_p):
    pass


class Eur_unexpected_data_type(ct.c_void_p):
    pass


class std_const_string(ct.c_void_p):
    pass


class std_exception(ct.c_void_p):
    pass


class std_logic_error(ct.c_void_p):
    pass


class std_map_std_string_std_string(ct.c_void_p):
    pass


class std_runtime_error(ct.c_void_p):
    pass


class std_string(ct.c_void_p):
    pass


class std_vector_BUFFER_HANDLE(ct.c_void_p):
    pass


class std_vector_EURESYS_EVENT_GET_DATA_ENTRY(ct.c_void_p):
    pass


class std_vector_PORT_HANDLE(ct.c_void_p):
    pass


class std_vector_PORT_REGISTER_STACK_ENTRY(ct.c_void_p):
    pass


class std_vector_char(ct.c_void_p):
    pass


class std_vector_std_string(ct.c_void_p):
    pass


# Imported functions
Eur_InfoCommandInfo_get_dataType = errorCheck(dll.euEurCINFO_get_dataType, "Eur_InfoCommandInfo_get_dataType")
Eur_InfoCommandInfo_get_dataSize = errorCheck(dll.euEurCINFO_get_dataSize, "Eur_InfoCommandInfo_get_dataSize")
Eur_InfoCommandInfo_destroy = errorCheck(dll.euEurCINFO_destroy, "Eur_InfoCommandInfo_destroy")
from_box_Eur_InfoCommandInfo__from__cInfoCommandInfo_p = errorCheck(
    dll.eufrom_box_EurCINFOFcInfoCommandInfo_p, "from_box_Eur_InfoCommandInfo__from__cInfoCommandInfo_p"
)
Eur_EGrabberInfo_create = errorCheck(dll.euEurEGInfo_create, "Eur_EGrabberInfo_create")
Eur_EGrabberInfo_destroy = errorCheck(dll.euEurEGInfo_destroy, "Eur_EGrabberInfo_destroy")
Eur_EGrabberCameraInfo_create = errorCheck(dll.euEurEGCameraInfo_create, "Eur_EGrabberCameraInfo_create")
Eur_EGrabberCameraInfo_destroy = errorCheck(dll.euEurEGCameraInfo_destroy, "Eur_EGrabberCameraInfo_destroy")
Eur_GenTLMemory_create__from__size_t__void_p = errorCheck(
    dll.euGenTLMemory_createFsvp, "Eur_GenTLMemory_create__from__size_t__void_p"
)
Eur_GenTLMemory_create__from__size_t = errorCheck(dll.euGenTLMemory_createFs, "Eur_GenTLMemory_create__from__size_t")
Eur_GenTLMemory_create = errorCheck(dll.euGenTLMemory_create, "Eur_GenTLMemory_create")
Eur_GenTLMemory_destroy = errorCheck(dll.euGenTLMemory_destroy, "Eur_GenTLMemory_destroy")
Eur_UserMemory_create__from__void_p__size_t__void_p = errorCheck(
    dll.euUserMemory_createFvpsvp, "Eur_UserMemory_create__from__void_p__size_t__void_p"
)
Eur_UserMemory_create__from__void_p__size_t = errorCheck(
    dll.euUserMemory_createFvps, "Eur_UserMemory_create__from__void_p__size_t"
)
Eur_UserMemory_destroy = errorCheck(dll.euUserMemory_destroy, "Eur_UserMemory_destroy")
Eur_BusMemory_create__from__uint64_t__size_t__void_p = errorCheck(
    dll.euBusMemory_createFu64svp, "Eur_BusMemory_create__from__uint64_t__size_t__void_p"
)
Eur_BusMemory_create__from__uint64_t__size_t = errorCheck(
    dll.euBusMemory_createFu64s, "Eur_BusMemory_create__from__uint64_t__size_t"
)
Eur_BusMemory_destroy = errorCheck(dll.euBusMemory_destroy, "Eur_BusMemory_destroy")
Eur_NvidiaRdmaMemory_create__from__void_p__size_t__void_p = errorCheck(
    dll.euNvidiaRdmaMemory_createFvpsvp, "Eur_NvidiaRdmaMemory_create__from__void_p__size_t__void_p"
)
Eur_NvidiaRdmaMemory_create__from__void_p__size_t = errorCheck(
    dll.euNvidiaRdmaMemory_createFvps, "Eur_NvidiaRdmaMemory_create__from__void_p__size_t"
)
Eur_NvidiaRdmaMemory_destroy = errorCheck(dll.euNvidiaRdmaMemory_destroy, "Eur_NvidiaRdmaMemory_destroy")
Eur_UserMemoryArray_create__from__Eur_UserMemory__size_t = errorCheck(
    dll.euUserMemoryArray_createFEur_UserMemorys, "Eur_UserMemoryArray_create__from__Eur_UserMemory__size_t"
)
Eur_UserMemoryArray_destroy = errorCheck(dll.euUserMemoryArray_destroy, "Eur_UserMemoryArray_destroy")
Eur_BufferIndexRange_create__from__size_t__size_t__bool8_t = errorCheck(
    dll.euBufferIndexRange_createFssb8, "Eur_BufferIndexRange_create__from__size_t__size_t__bool8_t"
)
Eur_BufferIndexRange_create__from__size_t__size_t = errorCheck(
    dll.euBufferIndexRange_createFss, "Eur_BufferIndexRange_create__from__size_t__size_t"
)
Eur_BufferIndexRange_create__from__size_t = errorCheck(
    dll.euBufferIndexRange_createFs, "Eur_BufferIndexRange_create__from__size_t"
)
Eur_BufferIndexRange_create = errorCheck(dll.euBufferIndexRange_create, "Eur_BufferIndexRange_create")
Eur_BufferIndexRange_create__from__Eur_BufferIndexRange = errorCheck(
    dll.euBufferIndexRange_createFEur_BufferIndexRange, "Eur_BufferIndexRange_create__from__Eur_BufferIndexRange"
)
Eur_BufferIndexRange_indexAt__from__size_t = errorCheck(
    dll.euBufferIndexRange_indexAtFs, "Eur_BufferIndexRange_indexAt__from__size_t"
)
Eur_BufferIndexRange_size = errorCheck(dll.euBufferIndexRange_size, "Eur_BufferIndexRange_size")
Eur_BufferIndexRange_destroy = errorCheck(dll.euBufferIndexRange_destroy, "Eur_BufferIndexRange_destroy")
Eur_NewBufferData_create = errorCheck(dll.euNewBufferData_create, "Eur_NewBufferData_create")
Eur_NewBufferData_destroy = errorCheck(dll.euNewBufferData_destroy, "Eur_NewBufferData_destroy")
Eur_IoToolboxData_create = errorCheck(dll.euIoToolboxData_create, "Eur_IoToolboxData_create")
Eur_IoToolboxData_destroy = errorCheck(dll.euIoToolboxData_destroy, "Eur_IoToolboxData_destroy")
Eur_CicData_create = errorCheck(dll.euCicData_create, "Eur_CicData_create")
Eur_CicData_destroy = errorCheck(dll.euCicData_destroy, "Eur_CicData_destroy")
Eur_DataStreamData_create = errorCheck(dll.euDataStreamData_create, "Eur_DataStreamData_create")
Eur_DataStreamData_destroy = errorCheck(dll.euDataStreamData_destroy, "Eur_DataStreamData_destroy")
Eur_CxpInterfaceData_create = errorCheck(dll.euCxpInterfaceData_create, "Eur_CxpInterfaceData_create")
Eur_CxpInterfaceData_destroy = errorCheck(dll.euCxpInterfaceData_destroy, "Eur_CxpInterfaceData_destroy")
Eur_DeviceErrorData_create = errorCheck(dll.euDeviceErrorData_create, "Eur_DeviceErrorData_create")
Eur_DeviceErrorData_destroy = errorCheck(dll.euDeviceErrorData_destroy, "Eur_DeviceErrorData_destroy")
Eur_CxpDeviceData_create = errorCheck(dll.euCxpDeviceData_create, "Eur_CxpDeviceData_create")
Eur_CxpDeviceData_destroy = errorCheck(dll.euCxpDeviceData_destroy, "Eur_CxpDeviceData_destroy")
Eur_RemoteDeviceData_create = errorCheck(dll.euRemoteDeviceData_create, "Eur_RemoteDeviceData_create")
Eur_RemoteDeviceData_destroy = errorCheck(dll.euRemoteDeviceData_destroy, "Eur_RemoteDeviceData_destroy")
Eur_Coaxlink = errorCheck(dll.euCoaxlink, "Eur_Coaxlink")
Eur_Grablink = errorCheck(dll.euGrablink, "Eur_Grablink")
Eur_Gigelink = errorCheck(dll.euGigelink, "Eur_Gigelink")
Eur_query_attributes = errorCheck(dll.euquery_attributes, "Eur_query_attributes")
Eur_query_features__from__bool8_t = errorCheck(dll.euquery_featuresFb8, "Eur_query_features__from__bool8_t")
Eur_query_features = errorCheck(dll.euquery_features, "Eur_query_features")
Eur_query_featuresOf__from__const_char_p__bool8_t = errorCheck(
    dll.euquery_featuresOfFccpb8, "Eur_query_featuresOf__from__const_char_p__bool8_t"
)
Eur_query_featuresOf__from__const_char_p = errorCheck(
    dll.euquery_featuresOfFccp, "Eur_query_featuresOf__from__const_char_p"
)
Eur_query_categories__from__bool8_t = errorCheck(dll.euquery_categoriesFb8, "Eur_query_categories__from__bool8_t")
Eur_query_categories = errorCheck(dll.euquery_categories, "Eur_query_categories")
Eur_query_categoriesOf__from__const_char_p__bool8_t = errorCheck(
    dll.euquery_categoriesOfFccpb8, "Eur_query_categoriesOf__from__const_char_p__bool8_t"
)
Eur_query_categoriesOf__from__const_char_p = errorCheck(
    dll.euquery_categoriesOfFccp, "Eur_query_categoriesOf__from__const_char_p"
)
Eur_query_enumEntries__from__const_char_p__bool8_t = errorCheck(
    dll.euquery_enumEntriesFccpb8, "Eur_query_enumEntries__from__const_char_p__bool8_t"
)
Eur_query_enumEntries__from__const_char_p = errorCheck(
    dll.euquery_enumEntriesFccp, "Eur_query_enumEntries__from__const_char_p"
)
Eur_query_available__from__const_char_p = errorCheck(
    dll.euquery_availableFccp, "Eur_query_available__from__const_char_p"
)
Eur_query_readable__from__const_char_p = errorCheck(dll.euquery_readableFccp, "Eur_query_readable__from__const_char_p")
Eur_query_writeable__from__const_char_p = errorCheck(
    dll.euquery_writeableFccp, "Eur_query_writeable__from__const_char_p"
)
Eur_query_implemented__from__const_char_p = errorCheck(
    dll.euquery_implementedFccp, "Eur_query_implemented__from__const_char_p"
)
Eur_query_command__from__const_char_p = errorCheck(dll.euquery_commandFccp, "Eur_query_command__from__const_char_p")
Eur_query_done__from__const_char_p = errorCheck(dll.euquery_doneFccp, "Eur_query_done__from__const_char_p")
Eur_query_interfaces__from__const_char_p = errorCheck(
    dll.euquery_interfacesFccp, "Eur_query_interfaces__from__const_char_p"
)
Eur_query_source__from__const_char_p = errorCheck(dll.euquery_sourceFccp, "Eur_query_source__from__const_char_p")
Eur_query_xml = errorCheck(dll.euquery_xml, "Eur_query_xml")
Eur_query_info__from__const_char_p__const_char_p = errorCheck(
    dll.euquery_infoFccpccp, "Eur_query_info__from__const_char_p__const_char_p"
)
Eur_query_declared = errorCheck(dll.euquery_declared, "Eur_query_declared")
Eur_action_declareInteger = errorCheck(dll.euaction_declareInteger, "Eur_action_declareInteger")
Eur_action_declareFloat = errorCheck(dll.euaction_declareFloat, "Eur_action_declareFloat")
Eur_action_declareString = errorCheck(dll.euaction_declareString, "Eur_action_declareString")
Eur_action_undeclare = errorCheck(dll.euaction_undeclare, "Eur_action_undeclare")
Eur_EGenTL_create__from__const_char_p__bool8_t = errorCheck(
    dll.euEGenTL_createFccpb8, "Eur_EGenTL_create__from__const_char_p__bool8_t"
)
Eur_EGenTL_create__from__const_char_p = errorCheck(dll.euEGenTL_createFccp, "Eur_EGenTL_create__from__const_char_p")
Eur_EGenTL_create = errorCheck(dll.euEGenTL_create, "Eur_EGenTL_create")
Eur_EGenTL_create__from__char_p__bool8_t = errorCheck(
    dll.euEGenTL_createFcpb8, "Eur_EGenTL_create__from__char_p__bool8_t"
)
Eur_EGenTL_create__from__char_p = errorCheck(dll.euEGenTL_createFcp, "Eur_EGenTL_create__from__char_p")
Eur_EGenTL_create__from__bool8_t__const_char_p = errorCheck(
    dll.euEGenTL_createFb8ccp, "Eur_EGenTL_create__from__bool8_t__const_char_p"
)
Eur_EGenTL_create__from__bool8_t = errorCheck(dll.euEGenTL_createFb8, "Eur_EGenTL_create__from__bool8_t")
Eur_EGenTL_gcGetInfo__as__size_t__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoAsFTIC, "Eur_EGenTL_gcGetInfo__as__size_t__from__TL_INFO_CMD"
)
Eur_EGenTL_gcGetInfo__as__int8_t__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoAi8FTIC, "Eur_EGenTL_gcGetInfo__as__int8_t__from__TL_INFO_CMD"
)
Eur_EGenTL_gcGetInfo__as__int16_t__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoAi16FTIC, "Eur_EGenTL_gcGetInfo__as__int16_t__from__TL_INFO_CMD"
)
Eur_EGenTL_gcGetInfo__as__int32_t__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoAi32FTIC, "Eur_EGenTL_gcGetInfo__as__int32_t__from__TL_INFO_CMD"
)
Eur_EGenTL_gcGetInfo__as__int64_t__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoAi64FTIC, "Eur_EGenTL_gcGetInfo__as__int64_t__from__TL_INFO_CMD"
)
Eur_EGenTL_gcGetInfo__as__uint8_t__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoAu8FTIC, "Eur_EGenTL_gcGetInfo__as__uint8_t__from__TL_INFO_CMD"
)
Eur_EGenTL_gcGetInfo__as__uint16_t__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoAu16FTIC, "Eur_EGenTL_gcGetInfo__as__uint16_t__from__TL_INFO_CMD"
)
Eur_EGenTL_gcGetInfo__as__uint32_t__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoAu32FTIC, "Eur_EGenTL_gcGetInfo__as__uint32_t__from__TL_INFO_CMD"
)
Eur_EGenTL_gcGetInfo__as__uint64_t__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoAu64FTIC, "Eur_EGenTL_gcGetInfo__as__uint64_t__from__TL_INFO_CMD"
)
Eur_EGenTL_gcGetInfo__as__double__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoAdFTIC, "Eur_EGenTL_gcGetInfo__as__double__from__TL_INFO_CMD"
)
Eur_EGenTL_gcGetInfo__as__float__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoAfFTIC, "Eur_EGenTL_gcGetInfo__as__float__from__TL_INFO_CMD"
)
Eur_EGenTL_gcGetInfo__as__uint8_t_ptr__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoAu8pFTIC, "Eur_EGenTL_gcGetInfo__as__uint8_t_ptr__from__TL_INFO_CMD"
)
Eur_EGenTL_gcGetInfo__as__std_string__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoASsFTIC, "Eur_EGenTL_gcGetInfo__as__std_string__from__TL_INFO_CMD"
)
Eur_EGenTL_gcGetInfo__as__void_ptr__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoAvptrFTIC, "Eur_EGenTL_gcGetInfo__as__void_ptr__from__TL_INFO_CMD"
)
Eur_EGenTL_gcGetInfo__as__std_vector_char__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoASvcFTIC, "Eur_EGenTL_gcGetInfo__as__std_vector_char__from__TL_INFO_CMD"
)
Eur_EGenTL_gcGetInfo__as__std_vector_std_string__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoASv_std_stringFTIC, "Eur_EGenTL_gcGetInfo__as__std_vector_std_string__from__TL_INFO_CMD"
)
Eur_EGenTL_gcGetInfo__as__bool8_t__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoAb8FTIC, "Eur_EGenTL_gcGetInfo__as__bool8_t__from__TL_INFO_CMD"
)
Eur_EGenTL_gcGetInfo__as__char_ptr__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoAcptrFTIC, "Eur_EGenTL_gcGetInfo__as__char_ptr__from__TL_INFO_CMD"
)
Eur_EGenTL_gcGetInfo__as__InfoCommandInfo__from__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetInfoA_CINFOFTIC, "Eur_EGenTL_gcGetInfo__as__InfoCommandInfo__from__TL_INFO_CMD"
)
Eur_EGenTL_gcReadPort__from__PORT_HANDLE__uint64_t__std_vector_char = errorCheck(
    dll.euEGenTL_gcReadPortFPHu64Svc, "Eur_EGenTL_gcReadPort__from__PORT_HANDLE__uint64_t__std_vector_char"
)
Eur_EGenTL_gcReadPortString__from__PORT_HANDLE__uint64_t__size_t = errorCheck(
    dll.euEGenTL_gcReadPortStringFPHu64s, "Eur_EGenTL_gcReadPortString__from__PORT_HANDLE__uint64_t__size_t"
)
Eur_EGenTL_gcReadPort__from__PORT_HANDLE__uint64_t = errorCheck(
    dll.euEGenTL_gcReadPortFPHu64, "Eur_EGenTL_gcReadPort__from__PORT_HANDLE__uint64_t"
)
Eur_EGenTL_gcWritePort__from__PORT_HANDLE__uint64_t__std_vector_char = errorCheck(
    dll.euEGenTL_gcWritePortFPHu64Svc, "Eur_EGenTL_gcWritePort__from__PORT_HANDLE__uint64_t__std_vector_char"
)
Eur_EGenTL_gcReadPortData__from__PORT_HANDLE__uint64_t__void_p__size_t = errorCheck(
    dll.euEGenTL_gcReadPortDataFPHu64vps, "Eur_EGenTL_gcReadPortData__from__PORT_HANDLE__uint64_t__void_p__size_t"
)
Eur_EGenTL_gcWritePortData__from__PORT_HANDLE__uint64_t__void_p__size_t = errorCheck(
    dll.euEGenTL_gcWritePortDataFPHu64vps, "Eur_EGenTL_gcWritePortData__from__PORT_HANDLE__uint64_t__void_p__size_t"
)
Eur_EGenTL_gcGetPortURL__from__PORT_HANDLE = errorCheck(
    dll.euEGenTL_gcGetPortURLFPH, "Eur_EGenTL_gcGetPortURL__from__PORT_HANDLE"
)
Eur_EGenTL_gcGetPortInfo__as__size_t__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoAsFPHPIC, "Eur_EGenTL_gcGetPortInfo__as__size_t__from__PORT_HANDLE__PORT_INFO_CMD"
)
Eur_EGenTL_gcGetPortInfo__as__int8_t__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoAi8FPHPIC, "Eur_EGenTL_gcGetPortInfo__as__int8_t__from__PORT_HANDLE__PORT_INFO_CMD"
)
Eur_EGenTL_gcGetPortInfo__as__int16_t__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoAi16FPHPIC, "Eur_EGenTL_gcGetPortInfo__as__int16_t__from__PORT_HANDLE__PORT_INFO_CMD"
)
Eur_EGenTL_gcGetPortInfo__as__int32_t__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoAi32FPHPIC, "Eur_EGenTL_gcGetPortInfo__as__int32_t__from__PORT_HANDLE__PORT_INFO_CMD"
)
Eur_EGenTL_gcGetPortInfo__as__int64_t__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoAi64FPHPIC, "Eur_EGenTL_gcGetPortInfo__as__int64_t__from__PORT_HANDLE__PORT_INFO_CMD"
)
Eur_EGenTL_gcGetPortInfo__as__uint8_t__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoAu8FPHPIC, "Eur_EGenTL_gcGetPortInfo__as__uint8_t__from__PORT_HANDLE__PORT_INFO_CMD"
)
Eur_EGenTL_gcGetPortInfo__as__uint16_t__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoAu16FPHPIC, "Eur_EGenTL_gcGetPortInfo__as__uint16_t__from__PORT_HANDLE__PORT_INFO_CMD"
)
Eur_EGenTL_gcGetPortInfo__as__uint32_t__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoAu32FPHPIC, "Eur_EGenTL_gcGetPortInfo__as__uint32_t__from__PORT_HANDLE__PORT_INFO_CMD"
)
Eur_EGenTL_gcGetPortInfo__as__uint64_t__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoAu64FPHPIC, "Eur_EGenTL_gcGetPortInfo__as__uint64_t__from__PORT_HANDLE__PORT_INFO_CMD"
)
Eur_EGenTL_gcGetPortInfo__as__double__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoAdFPHPIC, "Eur_EGenTL_gcGetPortInfo__as__double__from__PORT_HANDLE__PORT_INFO_CMD"
)
Eur_EGenTL_gcGetPortInfo__as__float__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoAfFPHPIC, "Eur_EGenTL_gcGetPortInfo__as__float__from__PORT_HANDLE__PORT_INFO_CMD"
)
Eur_EGenTL_gcGetPortInfo__as__uint8_t_ptr__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoAu8pFPHPIC, "Eur_EGenTL_gcGetPortInfo__as__uint8_t_ptr__from__PORT_HANDLE__PORT_INFO_CMD"
)
Eur_EGenTL_gcGetPortInfo__as__std_string__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoASsFPHPIC, "Eur_EGenTL_gcGetPortInfo__as__std_string__from__PORT_HANDLE__PORT_INFO_CMD"
)
Eur_EGenTL_gcGetPortInfo__as__void_ptr__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoAvptrFPHPIC, "Eur_EGenTL_gcGetPortInfo__as__void_ptr__from__PORT_HANDLE__PORT_INFO_CMD"
)
Eur_EGenTL_gcGetPortInfo__as__std_vector_char__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoASvcFPHPIC,
    "Eur_EGenTL_gcGetPortInfo__as__std_vector_char__from__PORT_HANDLE__PORT_INFO_CMD",
)
Eur_EGenTL_gcGetPortInfo__as__std_vector_std_string__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoASv_std_stringFPHPIC,
    "Eur_EGenTL_gcGetPortInfo__as__std_vector_std_string__from__PORT_HANDLE__PORT_INFO_CMD",
)
Eur_EGenTL_gcGetPortInfo__as__bool8_t__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoAb8FPHPIC, "Eur_EGenTL_gcGetPortInfo__as__bool8_t__from__PORT_HANDLE__PORT_INFO_CMD"
)
Eur_EGenTL_gcGetPortInfo__as__char_ptr__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoAcptrFPHPIC, "Eur_EGenTL_gcGetPortInfo__as__char_ptr__from__PORT_HANDLE__PORT_INFO_CMD"
)
Eur_EGenTL_gcGetPortInfo__as__InfoCommandInfo__from__PORT_HANDLE__PORT_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortInfoA_CINFOFPHPIC,
    "Eur_EGenTL_gcGetPortInfo__as__InfoCommandInfo__from__PORT_HANDLE__PORT_INFO_CMD",
)
Eur_EGenTL_gcRegisterEvent__from__EVENTSRC_HANDLE__EVENT_TYPE = errorCheck(
    dll.euEGenTL_gcRegisterEventFEHET, "Eur_EGenTL_gcRegisterEvent__from__EVENTSRC_HANDLE__EVENT_TYPE"
)
Eur_EGenTL_gcUnregisterEvent__from__EVENTSRC_HANDLE__EVENT_TYPE = errorCheck(
    dll.euEGenTL_gcUnregisterEventFEHET, "Eur_EGenTL_gcUnregisterEvent__from__EVENTSRC_HANDLE__EVENT_TYPE"
)
Eur_EGenTL_eventGetData__from__EVENT_HANDLE__void_p__size_t__uint64_t = errorCheck(
    dll.euEGenTL_eventGetDataFEHvpsu64, "Eur_EGenTL_eventGetData__from__EVENT_HANDLE__void_p__size_t__uint64_t"
)
Eur_EGenTL_eventsGetData__from__std_vector_EURESYS_EVENT_GET_DATA_ENTRY__uint64_t_p = errorCheck(
    dll.euEGenTL_eventsGetDataFSv_EEGDEu64p,
    "Eur_EGenTL_eventsGetData__from__std_vector_EURESYS_EVENT_GET_DATA_ENTRY__uint64_t_p",
)
Eur_EGenTL_eventGetDataInfo__as__size_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoAsFEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__size_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetDataInfo__as__int8_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoAi8FEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__int8_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetDataInfo__as__int16_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoAi16FEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__int16_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetDataInfo__as__int32_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoAi32FEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__int32_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetDataInfo__as__int64_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoAi64FEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__int64_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetDataInfo__as__uint8_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoAu8FEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__uint8_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetDataInfo__as__uint16_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoAu16FEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__uint16_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetDataInfo__as__uint32_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoAu32FEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__uint32_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetDataInfo__as__uint64_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoAu64FEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__uint64_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetDataInfo__as__double__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoAdFEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__double__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetDataInfo__as__float__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoAfFEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__float__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetDataInfo__as__uint8_t_ptr__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoAu8pFEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__uint8_t_ptr__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetDataInfo__as__std_string__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoASsFEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__std_string__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetDataInfo__as__void_ptr__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoAvptrFEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__void_ptr__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetDataInfo__as__std_vector_char__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoASvcFEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__std_vector_char__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetDataInfo__as__std_vector_std_string__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoASv_std_stringFEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__std_vector_std_string__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetDataInfo__as__bool8_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoAb8FEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__bool8_t__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetDataInfo__as__char_ptr__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoAcptrFEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__char_ptr__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetDataInfo__as__InfoCommandInfo__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetDataInfoA_CINFOFEHvpsEDIC,
    "Eur_EGenTL_eventGetDataInfo__as__InfoCommandInfo__from__EVENT_HANDLE__void_p__size_t__EVENT_DATA_INFO_CMD",
)
Eur_EGenTL_eventGetInfo__as__size_t__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoAsFEHEIC, "Eur_EGenTL_eventGetInfo__as__size_t__from__EVENT_HANDLE__EVENT_INFO_CMD"
)
Eur_EGenTL_eventGetInfo__as__int8_t__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoAi8FEHEIC, "Eur_EGenTL_eventGetInfo__as__int8_t__from__EVENT_HANDLE__EVENT_INFO_CMD"
)
Eur_EGenTL_eventGetInfo__as__int16_t__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoAi16FEHEIC, "Eur_EGenTL_eventGetInfo__as__int16_t__from__EVENT_HANDLE__EVENT_INFO_CMD"
)
Eur_EGenTL_eventGetInfo__as__int32_t__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoAi32FEHEIC, "Eur_EGenTL_eventGetInfo__as__int32_t__from__EVENT_HANDLE__EVENT_INFO_CMD"
)
Eur_EGenTL_eventGetInfo__as__int64_t__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoAi64FEHEIC, "Eur_EGenTL_eventGetInfo__as__int64_t__from__EVENT_HANDLE__EVENT_INFO_CMD"
)
Eur_EGenTL_eventGetInfo__as__uint8_t__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoAu8FEHEIC, "Eur_EGenTL_eventGetInfo__as__uint8_t__from__EVENT_HANDLE__EVENT_INFO_CMD"
)
Eur_EGenTL_eventGetInfo__as__uint16_t__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoAu16FEHEIC, "Eur_EGenTL_eventGetInfo__as__uint16_t__from__EVENT_HANDLE__EVENT_INFO_CMD"
)
Eur_EGenTL_eventGetInfo__as__uint32_t__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoAu32FEHEIC, "Eur_EGenTL_eventGetInfo__as__uint32_t__from__EVENT_HANDLE__EVENT_INFO_CMD"
)
Eur_EGenTL_eventGetInfo__as__uint64_t__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoAu64FEHEIC, "Eur_EGenTL_eventGetInfo__as__uint64_t__from__EVENT_HANDLE__EVENT_INFO_CMD"
)
Eur_EGenTL_eventGetInfo__as__double__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoAdFEHEIC, "Eur_EGenTL_eventGetInfo__as__double__from__EVENT_HANDLE__EVENT_INFO_CMD"
)
Eur_EGenTL_eventGetInfo__as__float__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoAfFEHEIC, "Eur_EGenTL_eventGetInfo__as__float__from__EVENT_HANDLE__EVENT_INFO_CMD"
)
Eur_EGenTL_eventGetInfo__as__uint8_t_ptr__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoAu8pFEHEIC, "Eur_EGenTL_eventGetInfo__as__uint8_t_ptr__from__EVENT_HANDLE__EVENT_INFO_CMD"
)
Eur_EGenTL_eventGetInfo__as__std_string__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoASsFEHEIC, "Eur_EGenTL_eventGetInfo__as__std_string__from__EVENT_HANDLE__EVENT_INFO_CMD"
)
Eur_EGenTL_eventGetInfo__as__void_ptr__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoAvptrFEHEIC, "Eur_EGenTL_eventGetInfo__as__void_ptr__from__EVENT_HANDLE__EVENT_INFO_CMD"
)
Eur_EGenTL_eventGetInfo__as__std_vector_char__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoASvcFEHEIC,
    "Eur_EGenTL_eventGetInfo__as__std_vector_char__from__EVENT_HANDLE__EVENT_INFO_CMD",
)
Eur_EGenTL_eventGetInfo__as__std_vector_std_string__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoASv_std_stringFEHEIC,
    "Eur_EGenTL_eventGetInfo__as__std_vector_std_string__from__EVENT_HANDLE__EVENT_INFO_CMD",
)
Eur_EGenTL_eventGetInfo__as__bool8_t__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoAb8FEHEIC, "Eur_EGenTL_eventGetInfo__as__bool8_t__from__EVENT_HANDLE__EVENT_INFO_CMD"
)
Eur_EGenTL_eventGetInfo__as__char_ptr__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoAcptrFEHEIC, "Eur_EGenTL_eventGetInfo__as__char_ptr__from__EVENT_HANDLE__EVENT_INFO_CMD"
)
Eur_EGenTL_eventGetInfo__as__InfoCommandInfo__from__EVENT_HANDLE__EVENT_INFO_CMD = errorCheck(
    dll.euEGenTL_eventGetInfoA_CINFOFEHEIC,
    "Eur_EGenTL_eventGetInfo__as__InfoCommandInfo__from__EVENT_HANDLE__EVENT_INFO_CMD",
)
Eur_EGenTL_eventFlush__from__EVENT_HANDLE = errorCheck(
    dll.euEGenTL_eventFlushFEH, "Eur_EGenTL_eventFlush__from__EVENT_HANDLE"
)
Eur_EGenTL_eventKill__from__EVENT_HANDLE = errorCheck(
    dll.euEGenTL_eventKillFEH, "Eur_EGenTL_eventKill__from__EVENT_HANDLE"
)
Eur_EGenTL_tlOpen = errorCheck(dll.euEGenTL_tlOpen, "Eur_EGenTL_tlOpen")
Eur_EGenTL_tlClose__from__TL_HANDLE = errorCheck(dll.euEGenTL_tlCloseFTH, "Eur_EGenTL_tlClose__from__TL_HANDLE")
Eur_EGenTL_tlGetInfo__as__size_t__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoAsFTHTIC, "Eur_EGenTL_tlGetInfo__as__size_t__from__TL_HANDLE__TL_INFO_CMD"
)
Eur_EGenTL_tlGetInfo__as__int8_t__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoAi8FTHTIC, "Eur_EGenTL_tlGetInfo__as__int8_t__from__TL_HANDLE__TL_INFO_CMD"
)
Eur_EGenTL_tlGetInfo__as__int16_t__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoAi16FTHTIC, "Eur_EGenTL_tlGetInfo__as__int16_t__from__TL_HANDLE__TL_INFO_CMD"
)
Eur_EGenTL_tlGetInfo__as__int32_t__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoAi32FTHTIC, "Eur_EGenTL_tlGetInfo__as__int32_t__from__TL_HANDLE__TL_INFO_CMD"
)
Eur_EGenTL_tlGetInfo__as__int64_t__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoAi64FTHTIC, "Eur_EGenTL_tlGetInfo__as__int64_t__from__TL_HANDLE__TL_INFO_CMD"
)
Eur_EGenTL_tlGetInfo__as__uint8_t__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoAu8FTHTIC, "Eur_EGenTL_tlGetInfo__as__uint8_t__from__TL_HANDLE__TL_INFO_CMD"
)
Eur_EGenTL_tlGetInfo__as__uint16_t__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoAu16FTHTIC, "Eur_EGenTL_tlGetInfo__as__uint16_t__from__TL_HANDLE__TL_INFO_CMD"
)
Eur_EGenTL_tlGetInfo__as__uint32_t__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoAu32FTHTIC, "Eur_EGenTL_tlGetInfo__as__uint32_t__from__TL_HANDLE__TL_INFO_CMD"
)
Eur_EGenTL_tlGetInfo__as__uint64_t__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoAu64FTHTIC, "Eur_EGenTL_tlGetInfo__as__uint64_t__from__TL_HANDLE__TL_INFO_CMD"
)
Eur_EGenTL_tlGetInfo__as__double__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoAdFTHTIC, "Eur_EGenTL_tlGetInfo__as__double__from__TL_HANDLE__TL_INFO_CMD"
)
Eur_EGenTL_tlGetInfo__as__float__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoAfFTHTIC, "Eur_EGenTL_tlGetInfo__as__float__from__TL_HANDLE__TL_INFO_CMD"
)
Eur_EGenTL_tlGetInfo__as__uint8_t_ptr__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoAu8pFTHTIC, "Eur_EGenTL_tlGetInfo__as__uint8_t_ptr__from__TL_HANDLE__TL_INFO_CMD"
)
Eur_EGenTL_tlGetInfo__as__std_string__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoASsFTHTIC, "Eur_EGenTL_tlGetInfo__as__std_string__from__TL_HANDLE__TL_INFO_CMD"
)
Eur_EGenTL_tlGetInfo__as__void_ptr__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoAvptrFTHTIC, "Eur_EGenTL_tlGetInfo__as__void_ptr__from__TL_HANDLE__TL_INFO_CMD"
)
Eur_EGenTL_tlGetInfo__as__std_vector_char__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoASvcFTHTIC, "Eur_EGenTL_tlGetInfo__as__std_vector_char__from__TL_HANDLE__TL_INFO_CMD"
)
Eur_EGenTL_tlGetInfo__as__std_vector_std_string__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoASv_std_stringFTHTIC,
    "Eur_EGenTL_tlGetInfo__as__std_vector_std_string__from__TL_HANDLE__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInfo__as__bool8_t__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoAb8FTHTIC, "Eur_EGenTL_tlGetInfo__as__bool8_t__from__TL_HANDLE__TL_INFO_CMD"
)
Eur_EGenTL_tlGetInfo__as__char_ptr__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoAcptrFTHTIC, "Eur_EGenTL_tlGetInfo__as__char_ptr__from__TL_HANDLE__TL_INFO_CMD"
)
Eur_EGenTL_tlGetInfo__as__InfoCommandInfo__from__TL_HANDLE__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInfoA_CINFOFTHTIC, "Eur_EGenTL_tlGetInfo__as__InfoCommandInfo__from__TL_HANDLE__TL_INFO_CMD"
)
Eur_EGenTL_tlGetNumInterfaces__from__TL_HANDLE = errorCheck(
    dll.euEGenTL_tlGetNumInterfacesFTH, "Eur_EGenTL_tlGetNumInterfaces__from__TL_HANDLE"
)
Eur_EGenTL_tlGetInterfaceID__from__TL_HANDLE__uint32_t = errorCheck(
    dll.euEGenTL_tlGetInterfaceIDFTHu32, "Eur_EGenTL_tlGetInterfaceID__from__TL_HANDLE__uint32_t"
)
Eur_EGenTL_tlGetInterfaceInfo__as__size_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoAsFTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__size_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInterfaceInfo__as__int8_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoAi8FTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__int8_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInterfaceInfo__as__int16_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoAi16FTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__int16_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInterfaceInfo__as__int32_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoAi32FTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__int32_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInterfaceInfo__as__int64_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoAi64FTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__int64_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInterfaceInfo__as__uint8_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoAu8FTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__uint8_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInterfaceInfo__as__uint16_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoAu16FTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__uint16_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInterfaceInfo__as__uint32_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoAu32FTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__uint32_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInterfaceInfo__as__uint64_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoAu64FTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__uint64_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInterfaceInfo__as__double__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoAdFTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__double__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInterfaceInfo__as__float__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoAfFTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__float__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInterfaceInfo__as__uint8_t_ptr__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoAu8pFTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__uint8_t_ptr__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInterfaceInfo__as__std_string__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoASsFTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__std_string__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInterfaceInfo__as__void_ptr__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoAvptrFTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__void_ptr__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInterfaceInfo__as__std_vector_char__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoASvcFTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__std_vector_char__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInterfaceInfo__as__std_vector_std_string__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoASv_std_stringFTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__std_vector_std_string__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInterfaceInfo__as__bool8_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoAb8FTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__bool8_t__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInterfaceInfo__as__char_ptr__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoAcptrFTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__char_ptr__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlGetInterfaceInfo__as__InfoCommandInfo__from__TL_HANDLE__const_char_p__TL_INFO_CMD = errorCheck(
    dll.euEGenTL_tlGetInterfaceInfoA_CINFOFTHccpTIC,
    "Eur_EGenTL_tlGetInterfaceInfo__as__InfoCommandInfo__from__TL_HANDLE__const_char_p__TL_INFO_CMD",
)
Eur_EGenTL_tlOpenInterface__from__TL_HANDLE__const_char_p = errorCheck(
    dll.euEGenTL_tlOpenInterfaceFTHccp, "Eur_EGenTL_tlOpenInterface__from__TL_HANDLE__const_char_p"
)
Eur_EGenTL_tlUpdateInterfaceList__from__TL_HANDLE__uint64_t = errorCheck(
    dll.euEGenTL_tlUpdateInterfaceListFTHu64, "Eur_EGenTL_tlUpdateInterfaceList__from__TL_HANDLE__uint64_t"
)
Eur_EGenTL_tlUpdateInterfaceList__from__TL_HANDLE = errorCheck(
    dll.euEGenTL_tlUpdateInterfaceListFTH, "Eur_EGenTL_tlUpdateInterfaceList__from__TL_HANDLE"
)
Eur_EGenTL_ifClose__from__IF_HANDLE = errorCheck(dll.euEGenTL_ifCloseFIH, "Eur_EGenTL_ifClose__from__IF_HANDLE")
Eur_EGenTL_ifGetInfo__as__size_t__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoAsFIHIIC, "Eur_EGenTL_ifGetInfo__as__size_t__from__IF_HANDLE__INTERFACE_INFO_CMD"
)
Eur_EGenTL_ifGetInfo__as__int8_t__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoAi8FIHIIC, "Eur_EGenTL_ifGetInfo__as__int8_t__from__IF_HANDLE__INTERFACE_INFO_CMD"
)
Eur_EGenTL_ifGetInfo__as__int16_t__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoAi16FIHIIC, "Eur_EGenTL_ifGetInfo__as__int16_t__from__IF_HANDLE__INTERFACE_INFO_CMD"
)
Eur_EGenTL_ifGetInfo__as__int32_t__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoAi32FIHIIC, "Eur_EGenTL_ifGetInfo__as__int32_t__from__IF_HANDLE__INTERFACE_INFO_CMD"
)
Eur_EGenTL_ifGetInfo__as__int64_t__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoAi64FIHIIC, "Eur_EGenTL_ifGetInfo__as__int64_t__from__IF_HANDLE__INTERFACE_INFO_CMD"
)
Eur_EGenTL_ifGetInfo__as__uint8_t__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoAu8FIHIIC, "Eur_EGenTL_ifGetInfo__as__uint8_t__from__IF_HANDLE__INTERFACE_INFO_CMD"
)
Eur_EGenTL_ifGetInfo__as__uint16_t__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoAu16FIHIIC, "Eur_EGenTL_ifGetInfo__as__uint16_t__from__IF_HANDLE__INTERFACE_INFO_CMD"
)
Eur_EGenTL_ifGetInfo__as__uint32_t__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoAu32FIHIIC, "Eur_EGenTL_ifGetInfo__as__uint32_t__from__IF_HANDLE__INTERFACE_INFO_CMD"
)
Eur_EGenTL_ifGetInfo__as__uint64_t__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoAu64FIHIIC, "Eur_EGenTL_ifGetInfo__as__uint64_t__from__IF_HANDLE__INTERFACE_INFO_CMD"
)
Eur_EGenTL_ifGetInfo__as__double__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoAdFIHIIC, "Eur_EGenTL_ifGetInfo__as__double__from__IF_HANDLE__INTERFACE_INFO_CMD"
)
Eur_EGenTL_ifGetInfo__as__float__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoAfFIHIIC, "Eur_EGenTL_ifGetInfo__as__float__from__IF_HANDLE__INTERFACE_INFO_CMD"
)
Eur_EGenTL_ifGetInfo__as__uint8_t_ptr__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoAu8pFIHIIC, "Eur_EGenTL_ifGetInfo__as__uint8_t_ptr__from__IF_HANDLE__INTERFACE_INFO_CMD"
)
Eur_EGenTL_ifGetInfo__as__std_string__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoASsFIHIIC, "Eur_EGenTL_ifGetInfo__as__std_string__from__IF_HANDLE__INTERFACE_INFO_CMD"
)
Eur_EGenTL_ifGetInfo__as__void_ptr__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoAvptrFIHIIC, "Eur_EGenTL_ifGetInfo__as__void_ptr__from__IF_HANDLE__INTERFACE_INFO_CMD"
)
Eur_EGenTL_ifGetInfo__as__std_vector_char__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoASvcFIHIIC, "Eur_EGenTL_ifGetInfo__as__std_vector_char__from__IF_HANDLE__INTERFACE_INFO_CMD"
)
Eur_EGenTL_ifGetInfo__as__std_vector_std_string__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoASv_std_stringFIHIIC,
    "Eur_EGenTL_ifGetInfo__as__std_vector_std_string__from__IF_HANDLE__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetInfo__as__bool8_t__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoAb8FIHIIC, "Eur_EGenTL_ifGetInfo__as__bool8_t__from__IF_HANDLE__INTERFACE_INFO_CMD"
)
Eur_EGenTL_ifGetInfo__as__char_ptr__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoAcptrFIHIIC, "Eur_EGenTL_ifGetInfo__as__char_ptr__from__IF_HANDLE__INTERFACE_INFO_CMD"
)
Eur_EGenTL_ifGetInfo__as__InfoCommandInfo__from__IF_HANDLE__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetInfoA_CINFOFIHIIC,
    "Eur_EGenTL_ifGetInfo__as__InfoCommandInfo__from__IF_HANDLE__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetNumDevices__from__IF_HANDLE = errorCheck(
    dll.euEGenTL_ifGetNumDevicesFIH, "Eur_EGenTL_ifGetNumDevices__from__IF_HANDLE"
)
Eur_EGenTL_ifGetDeviceID__from__IF_HANDLE__uint32_t = errorCheck(
    dll.euEGenTL_ifGetDeviceIDFIHu32, "Eur_EGenTL_ifGetDeviceID__from__IF_HANDLE__uint32_t"
)
Eur_EGenTL_ifUpdateDeviceList__from__IF_HANDLE__uint64_t = errorCheck(
    dll.euEGenTL_ifUpdateDeviceListFIHu64, "Eur_EGenTL_ifUpdateDeviceList__from__IF_HANDLE__uint64_t"
)
Eur_EGenTL_ifUpdateDeviceList__from__IF_HANDLE = errorCheck(
    dll.euEGenTL_ifUpdateDeviceListFIH, "Eur_EGenTL_ifUpdateDeviceList__from__IF_HANDLE"
)
Eur_EGenTL_ifGetDeviceInfo__as__size_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoAsFIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__size_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetDeviceInfo__as__int8_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoAi8FIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__int8_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetDeviceInfo__as__int16_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoAi16FIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__int16_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetDeviceInfo__as__int32_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoAi32FIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__int32_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetDeviceInfo__as__int64_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoAi64FIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__int64_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetDeviceInfo__as__uint8_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoAu8FIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__uint8_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetDeviceInfo__as__uint16_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoAu16FIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__uint16_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetDeviceInfo__as__uint32_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoAu32FIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__uint32_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetDeviceInfo__as__uint64_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoAu64FIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__uint64_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetDeviceInfo__as__double__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoAdFIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__double__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetDeviceInfo__as__float__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoAfFIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__float__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetDeviceInfo__as__uint8_t_ptr__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoAu8pFIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__uint8_t_ptr__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetDeviceInfo__as__std_string__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoASsFIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__std_string__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetDeviceInfo__as__void_ptr__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoAvptrFIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__void_ptr__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetDeviceInfo__as__std_vector_char__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoASvcFIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__std_vector_char__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetDeviceInfo__as__std_vector_std_string__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoASv_std_stringFIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__std_vector_std_string__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetDeviceInfo__as__bool8_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoAb8FIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__bool8_t__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetDeviceInfo__as__char_ptr__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoAcptrFIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__char_ptr__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifGetDeviceInfo__as__InfoCommandInfo__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD = errorCheck(
    dll.euEGenTL_ifGetDeviceInfoA_CINFOFIHccpIIC,
    "Eur_EGenTL_ifGetDeviceInfo__as__InfoCommandInfo__from__IF_HANDLE__const_char_p__INTERFACE_INFO_CMD",
)
Eur_EGenTL_ifOpenDevice__from__IF_HANDLE__const_char_p__DEVICE_ACCESS_FLAGS = errorCheck(
    dll.euEGenTL_ifOpenDeviceFIHccpDAF, "Eur_EGenTL_ifOpenDevice__from__IF_HANDLE__const_char_p__DEVICE_ACCESS_FLAGS"
)
Eur_EGenTL_ifOpenDevice__from__IF_HANDLE__const_char_p = errorCheck(
    dll.euEGenTL_ifOpenDeviceFIHccp, "Eur_EGenTL_ifOpenDevice__from__IF_HANDLE__const_char_p"
)
Eur_EGenTL_devGetPort__from__DEV_HANDLE = errorCheck(
    dll.euEGenTL_devGetPortFDH, "Eur_EGenTL_devGetPort__from__DEV_HANDLE"
)
Eur_EGenTL_devGetNumDataStreams__from__DEV_HANDLE = errorCheck(
    dll.euEGenTL_devGetNumDataStreamsFDH, "Eur_EGenTL_devGetNumDataStreams__from__DEV_HANDLE"
)
Eur_EGenTL_devGetDataStreamID__from__DEV_HANDLE__uint32_t = errorCheck(
    dll.euEGenTL_devGetDataStreamIDFDHu32, "Eur_EGenTL_devGetDataStreamID__from__DEV_HANDLE__uint32_t"
)
Eur_EGenTL_devOpenDataStream__from__DEV_HANDLE__const_char_p = errorCheck(
    dll.euEGenTL_devOpenDataStreamFDHccp, "Eur_EGenTL_devOpenDataStream__from__DEV_HANDLE__const_char_p"
)
Eur_EGenTL_devClose__from__DEV_HANDLE = errorCheck(dll.euEGenTL_devCloseFDH, "Eur_EGenTL_devClose__from__DEV_HANDLE")
Eur_EGenTL_devGetInfo__as__size_t__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoAsFDHDIC, "Eur_EGenTL_devGetInfo__as__size_t__from__DEV_HANDLE__DEVICE_INFO_CMD"
)
Eur_EGenTL_devGetInfo__as__int8_t__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoAi8FDHDIC, "Eur_EGenTL_devGetInfo__as__int8_t__from__DEV_HANDLE__DEVICE_INFO_CMD"
)
Eur_EGenTL_devGetInfo__as__int16_t__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoAi16FDHDIC, "Eur_EGenTL_devGetInfo__as__int16_t__from__DEV_HANDLE__DEVICE_INFO_CMD"
)
Eur_EGenTL_devGetInfo__as__int32_t__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoAi32FDHDIC, "Eur_EGenTL_devGetInfo__as__int32_t__from__DEV_HANDLE__DEVICE_INFO_CMD"
)
Eur_EGenTL_devGetInfo__as__int64_t__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoAi64FDHDIC, "Eur_EGenTL_devGetInfo__as__int64_t__from__DEV_HANDLE__DEVICE_INFO_CMD"
)
Eur_EGenTL_devGetInfo__as__uint8_t__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoAu8FDHDIC, "Eur_EGenTL_devGetInfo__as__uint8_t__from__DEV_HANDLE__DEVICE_INFO_CMD"
)
Eur_EGenTL_devGetInfo__as__uint16_t__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoAu16FDHDIC, "Eur_EGenTL_devGetInfo__as__uint16_t__from__DEV_HANDLE__DEVICE_INFO_CMD"
)
Eur_EGenTL_devGetInfo__as__uint32_t__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoAu32FDHDIC, "Eur_EGenTL_devGetInfo__as__uint32_t__from__DEV_HANDLE__DEVICE_INFO_CMD"
)
Eur_EGenTL_devGetInfo__as__uint64_t__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoAu64FDHDIC, "Eur_EGenTL_devGetInfo__as__uint64_t__from__DEV_HANDLE__DEVICE_INFO_CMD"
)
Eur_EGenTL_devGetInfo__as__double__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoAdFDHDIC, "Eur_EGenTL_devGetInfo__as__double__from__DEV_HANDLE__DEVICE_INFO_CMD"
)
Eur_EGenTL_devGetInfo__as__float__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoAfFDHDIC, "Eur_EGenTL_devGetInfo__as__float__from__DEV_HANDLE__DEVICE_INFO_CMD"
)
Eur_EGenTL_devGetInfo__as__uint8_t_ptr__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoAu8pFDHDIC, "Eur_EGenTL_devGetInfo__as__uint8_t_ptr__from__DEV_HANDLE__DEVICE_INFO_CMD"
)
Eur_EGenTL_devGetInfo__as__std_string__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoASsFDHDIC, "Eur_EGenTL_devGetInfo__as__std_string__from__DEV_HANDLE__DEVICE_INFO_CMD"
)
Eur_EGenTL_devGetInfo__as__void_ptr__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoAvptrFDHDIC, "Eur_EGenTL_devGetInfo__as__void_ptr__from__DEV_HANDLE__DEVICE_INFO_CMD"
)
Eur_EGenTL_devGetInfo__as__std_vector_char__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoASvcFDHDIC, "Eur_EGenTL_devGetInfo__as__std_vector_char__from__DEV_HANDLE__DEVICE_INFO_CMD"
)
Eur_EGenTL_devGetInfo__as__std_vector_std_string__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoASv_std_stringFDHDIC,
    "Eur_EGenTL_devGetInfo__as__std_vector_std_string__from__DEV_HANDLE__DEVICE_INFO_CMD",
)
Eur_EGenTL_devGetInfo__as__bool8_t__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoAb8FDHDIC, "Eur_EGenTL_devGetInfo__as__bool8_t__from__DEV_HANDLE__DEVICE_INFO_CMD"
)
Eur_EGenTL_devGetInfo__as__char_ptr__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoAcptrFDHDIC, "Eur_EGenTL_devGetInfo__as__char_ptr__from__DEV_HANDLE__DEVICE_INFO_CMD"
)
Eur_EGenTL_devGetInfo__as__InfoCommandInfo__from__DEV_HANDLE__DEVICE_INFO_CMD = errorCheck(
    dll.euEGenTL_devGetInfoA_CINFOFDHDIC,
    "Eur_EGenTL_devGetInfo__as__InfoCommandInfo__from__DEV_HANDLE__DEVICE_INFO_CMD",
)
Eur_EGenTL_dsAnnounceBuffer__from__DS_HANDLE__void_p__size_t__void_p = errorCheck(
    dll.euEGenTL_dsAnnounceBufferFDHvpsvp, "Eur_EGenTL_dsAnnounceBuffer__from__DS_HANDLE__void_p__size_t__void_p"
)
Eur_EGenTL_dsAnnounceBuffer__from__DS_HANDLE__void_p__size_t = errorCheck(
    dll.euEGenTL_dsAnnounceBufferFDHvps, "Eur_EGenTL_dsAnnounceBuffer__from__DS_HANDLE__void_p__size_t"
)
Eur_EGenTL_dsAllocAndAnnounceBuffer__from__DS_HANDLE__size_t__void_p = errorCheck(
    dll.euEGenTL_dsAllocAndAnnounceBufferFDHsvp, "Eur_EGenTL_dsAllocAndAnnounceBuffer__from__DS_HANDLE__size_t__void_p"
)
Eur_EGenTL_dsAllocAndAnnounceBuffer__from__DS_HANDLE__size_t = errorCheck(
    dll.euEGenTL_dsAllocAndAnnounceBufferFDHs, "Eur_EGenTL_dsAllocAndAnnounceBuffer__from__DS_HANDLE__size_t"
)
Eur_EGenTL_dsAnnounceBusBuffer__from__DS_HANDLE__uint64_t__size_t__void_p = errorCheck(
    dll.euEGenTL_dsAnnounceBusBufferFDHu64svp,
    "Eur_EGenTL_dsAnnounceBusBuffer__from__DS_HANDLE__uint64_t__size_t__void_p",
)
Eur_EGenTL_dsAnnounceBusBuffer__from__DS_HANDLE__uint64_t__size_t = errorCheck(
    dll.euEGenTL_dsAnnounceBusBufferFDHu64s, "Eur_EGenTL_dsAnnounceBusBuffer__from__DS_HANDLE__uint64_t__size_t"
)
Eur_EGenTL_dsAnnounceDeviceBuffer__from__DS_HANDLE__void_p__size_t__MEMORY_TYPE__void_p = errorCheck(
    dll.euEGenTL_dsAnnounceDeviceBufferFDHvpsMTvp,
    "Eur_EGenTL_dsAnnounceDeviceBuffer__from__DS_HANDLE__void_p__size_t__MEMORY_TYPE__void_p",
)
Eur_EGenTL_dsAnnounceDeviceBuffer__from__DS_HANDLE__void_p__size_t__MEMORY_TYPE = errorCheck(
    dll.euEGenTL_dsAnnounceDeviceBufferFDHvpsMT,
    "Eur_EGenTL_dsAnnounceDeviceBuffer__from__DS_HANDLE__void_p__size_t__MEMORY_TYPE",
)
Eur_EGenTL_dsAllocAndAnnounceBuffers__from__DS_HANDLE__size_t__std_vector_BUFFER_HANDLE = errorCheck(
    dll.euEGenTL_dsAllocAndAnnounceBuffersFDHsSv_BH,
    "Eur_EGenTL_dsAllocAndAnnounceBuffers__from__DS_HANDLE__size_t__std_vector_BUFFER_HANDLE",
)
Eur_EGenTL_dsFlushQueue__from__DS_HANDLE__ACQ_QUEUE_TYPE = errorCheck(
    dll.euEGenTL_dsFlushQueueFDHAQT, "Eur_EGenTL_dsFlushQueue__from__DS_HANDLE__ACQ_QUEUE_TYPE"
)
Eur_EGenTL_dsStartAcquisition__from__DS_HANDLE__ACQ_START_FLAGS__uint64_t = errorCheck(
    dll.euEGenTL_dsStartAcquisitionFDHASFu64,
    "Eur_EGenTL_dsStartAcquisition__from__DS_HANDLE__ACQ_START_FLAGS__uint64_t",
)
Eur_EGenTL_dsStartAcquisition__from__DS_HANDLE__ACQ_START_FLAGS = errorCheck(
    dll.euEGenTL_dsStartAcquisitionFDHASF, "Eur_EGenTL_dsStartAcquisition__from__DS_HANDLE__ACQ_START_FLAGS"
)
Eur_EGenTL_dsStartAcquisition__from__DS_HANDLE = errorCheck(
    dll.euEGenTL_dsStartAcquisitionFDH, "Eur_EGenTL_dsStartAcquisition__from__DS_HANDLE"
)
Eur_EGenTL_dsStopAcquisition__from__DS_HANDLE__ACQ_STOP_FLAGS = errorCheck(
    dll.euEGenTL_dsStopAcquisitionFDHASF, "Eur_EGenTL_dsStopAcquisition__from__DS_HANDLE__ACQ_STOP_FLAGS"
)
Eur_EGenTL_dsStopAcquisition__from__DS_HANDLE = errorCheck(
    dll.euEGenTL_dsStopAcquisitionFDH, "Eur_EGenTL_dsStopAcquisition__from__DS_HANDLE"
)
Eur_EGenTL_dsClose__from__DS_HANDLE = errorCheck(dll.euEGenTL_dsCloseFDH, "Eur_EGenTL_dsClose__from__DS_HANDLE")
Eur_EGenTL_dsGetInfo__as__size_t__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoAsFDHSIC, "Eur_EGenTL_dsGetInfo__as__size_t__from__DS_HANDLE__STREAM_INFO_CMD"
)
Eur_EGenTL_dsGetInfo__as__int8_t__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoAi8FDHSIC, "Eur_EGenTL_dsGetInfo__as__int8_t__from__DS_HANDLE__STREAM_INFO_CMD"
)
Eur_EGenTL_dsGetInfo__as__int16_t__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoAi16FDHSIC, "Eur_EGenTL_dsGetInfo__as__int16_t__from__DS_HANDLE__STREAM_INFO_CMD"
)
Eur_EGenTL_dsGetInfo__as__int32_t__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoAi32FDHSIC, "Eur_EGenTL_dsGetInfo__as__int32_t__from__DS_HANDLE__STREAM_INFO_CMD"
)
Eur_EGenTL_dsGetInfo__as__int64_t__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoAi64FDHSIC, "Eur_EGenTL_dsGetInfo__as__int64_t__from__DS_HANDLE__STREAM_INFO_CMD"
)
Eur_EGenTL_dsGetInfo__as__uint8_t__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoAu8FDHSIC, "Eur_EGenTL_dsGetInfo__as__uint8_t__from__DS_HANDLE__STREAM_INFO_CMD"
)
Eur_EGenTL_dsGetInfo__as__uint16_t__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoAu16FDHSIC, "Eur_EGenTL_dsGetInfo__as__uint16_t__from__DS_HANDLE__STREAM_INFO_CMD"
)
Eur_EGenTL_dsGetInfo__as__uint32_t__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoAu32FDHSIC, "Eur_EGenTL_dsGetInfo__as__uint32_t__from__DS_HANDLE__STREAM_INFO_CMD"
)
Eur_EGenTL_dsGetInfo__as__uint64_t__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoAu64FDHSIC, "Eur_EGenTL_dsGetInfo__as__uint64_t__from__DS_HANDLE__STREAM_INFO_CMD"
)
Eur_EGenTL_dsGetInfo__as__double__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoAdFDHSIC, "Eur_EGenTL_dsGetInfo__as__double__from__DS_HANDLE__STREAM_INFO_CMD"
)
Eur_EGenTL_dsGetInfo__as__float__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoAfFDHSIC, "Eur_EGenTL_dsGetInfo__as__float__from__DS_HANDLE__STREAM_INFO_CMD"
)
Eur_EGenTL_dsGetInfo__as__uint8_t_ptr__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoAu8pFDHSIC, "Eur_EGenTL_dsGetInfo__as__uint8_t_ptr__from__DS_HANDLE__STREAM_INFO_CMD"
)
Eur_EGenTL_dsGetInfo__as__std_string__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoASsFDHSIC, "Eur_EGenTL_dsGetInfo__as__std_string__from__DS_HANDLE__STREAM_INFO_CMD"
)
Eur_EGenTL_dsGetInfo__as__void_ptr__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoAvptrFDHSIC, "Eur_EGenTL_dsGetInfo__as__void_ptr__from__DS_HANDLE__STREAM_INFO_CMD"
)
Eur_EGenTL_dsGetInfo__as__std_vector_char__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoASvcFDHSIC, "Eur_EGenTL_dsGetInfo__as__std_vector_char__from__DS_HANDLE__STREAM_INFO_CMD"
)
Eur_EGenTL_dsGetInfo__as__std_vector_std_string__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoASv_std_stringFDHSIC,
    "Eur_EGenTL_dsGetInfo__as__std_vector_std_string__from__DS_HANDLE__STREAM_INFO_CMD",
)
Eur_EGenTL_dsGetInfo__as__bool8_t__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoAb8FDHSIC, "Eur_EGenTL_dsGetInfo__as__bool8_t__from__DS_HANDLE__STREAM_INFO_CMD"
)
Eur_EGenTL_dsGetInfo__as__char_ptr__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoAcptrFDHSIC, "Eur_EGenTL_dsGetInfo__as__char_ptr__from__DS_HANDLE__STREAM_INFO_CMD"
)
Eur_EGenTL_dsGetInfo__as__InfoCommandInfo__from__DS_HANDLE__STREAM_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetInfoA_CINFOFDHSIC, "Eur_EGenTL_dsGetInfo__as__InfoCommandInfo__from__DS_HANDLE__STREAM_INFO_CMD"
)
Eur_EGenTL_dsGetBufferID__from__DS_HANDLE__uint32_t = errorCheck(
    dll.euEGenTL_dsGetBufferIDFDHu32, "Eur_EGenTL_dsGetBufferID__from__DS_HANDLE__uint32_t"
)
Eur_EGenTL_dsRevokeBuffer__from__DS_HANDLE__BUFFER_HANDLE__void_pp__void_pp = errorCheck(
    dll.euEGenTL_dsRevokeBufferFDHBHvppvpp,
    "Eur_EGenTL_dsRevokeBuffer__from__DS_HANDLE__BUFFER_HANDLE__void_pp__void_pp",
)
Eur_EGenTL_dsRevokeBuffer__from__DS_HANDLE__BUFFER_HANDLE__void_pp = errorCheck(
    dll.euEGenTL_dsRevokeBufferFDHBHvpp, "Eur_EGenTL_dsRevokeBuffer__from__DS_HANDLE__BUFFER_HANDLE__void_pp"
)
Eur_EGenTL_dsRevokeBuffer__from__DS_HANDLE__BUFFER_HANDLE = errorCheck(
    dll.euEGenTL_dsRevokeBufferFDHBH, "Eur_EGenTL_dsRevokeBuffer__from__DS_HANDLE__BUFFER_HANDLE"
)
Eur_EGenTL_dsRevokeBuffers__from__DS_HANDLE__std_vector_BUFFER_HANDLE = errorCheck(
    dll.euEGenTL_dsRevokeBuffersFDHSv_BH, "Eur_EGenTL_dsRevokeBuffers__from__DS_HANDLE__std_vector_BUFFER_HANDLE"
)
Eur_EGenTL_dsQueueBuffer__from__DS_HANDLE__BUFFER_HANDLE = errorCheck(
    dll.euEGenTL_dsQueueBufferFDHBH, "Eur_EGenTL_dsQueueBuffer__from__DS_HANDLE__BUFFER_HANDLE"
)
Eur_EGenTL_dsQueueBuffers__from__DS_HANDLE__std_vector_BUFFER_HANDLE = errorCheck(
    dll.euEGenTL_dsQueueBuffersFDHSv_BH, "Eur_EGenTL_dsQueueBuffers__from__DS_HANDLE__std_vector_BUFFER_HANDLE"
)
Eur_EGenTL_dsGetBufferInfo__as__size_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoAsFDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__size_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__as__int8_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoAi8FDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__int8_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__as__int16_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoAi16FDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__int16_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__as__int32_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoAi32FDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__int32_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__as__int64_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoAi64FDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__int64_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__as__uint8_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoAu8FDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__uint8_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__as__uint16_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoAu16FDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__uint16_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__as__uint32_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoAu32FDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__uint32_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__as__uint64_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoAu64FDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__uint64_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__as__double__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoAdFDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__double__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__as__float__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoAfFDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__float__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__as__uint8_t_ptr__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoAu8pFDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__uint8_t_ptr__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__as__std_string__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoASsFDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__std_string__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__as__void_ptr__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoAvptrFDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__void_ptr__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__as__std_vector_char__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoASvcFDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__std_vector_char__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__as__std_vector_std_string__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoASv_std_stringFDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__std_vector_std_string__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__as__bool8_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoAb8FDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__bool8_t__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__as__char_ptr__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoAcptrFDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__char_ptr__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__as__InfoCommandInfo__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferInfoA_CINFOFDHBHBIC,
    "Eur_EGenTL_dsGetBufferInfo__as__InfoCommandInfo__from__DS_HANDLE__BUFFER_HANDLE__BUFFER_INFO_CMD",
)
Eur_EGenTL_dsGetBufferInfo__from__DS_HANDLE__BUFFER_HANDLE = errorCheck(
    dll.euEGenTL_dsGetBufferInfoFDHBH, "Eur_EGenTL_dsGetBufferInfo__from__DS_HANDLE__BUFFER_HANDLE"
)
Eur_EGenTL_dsGetNumBufferParts__from__DS_HANDLE__BUFFER_HANDLE = errorCheck(
    dll.euEGenTL_dsGetNumBufferPartsFDHBH, "Eur_EGenTL_dsGetNumBufferParts__from__DS_HANDLE__BUFFER_HANDLE"
)
Eur_EGenTL_dsGetBufferPartInfo__as__size_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferPartInfoAsFDHBHu32BPIC,
    "Eur_EGenTL_dsGetBufferPartInfo__as__size_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
)
Eur_EGenTL_dsGetBufferPartInfo__as__int8_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferPartInfoAi8FDHBHu32BPIC,
    "Eur_EGenTL_dsGetBufferPartInfo__as__int8_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
)
Eur_EGenTL_dsGetBufferPartInfo__as__int16_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = (
    errorCheck(
        dll.euEGenTL_dsGetBufferPartInfoAi16FDHBHu32BPIC,
        "Eur_EGenTL_dsGetBufferPartInfo__as__int16_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
    )
)
Eur_EGenTL_dsGetBufferPartInfo__as__int32_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = (
    errorCheck(
        dll.euEGenTL_dsGetBufferPartInfoAi32FDHBHu32BPIC,
        "Eur_EGenTL_dsGetBufferPartInfo__as__int32_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
    )
)
Eur_EGenTL_dsGetBufferPartInfo__as__int64_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = (
    errorCheck(
        dll.euEGenTL_dsGetBufferPartInfoAi64FDHBHu32BPIC,
        "Eur_EGenTL_dsGetBufferPartInfo__as__int64_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
    )
)
Eur_EGenTL_dsGetBufferPartInfo__as__uint8_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = (
    errorCheck(
        dll.euEGenTL_dsGetBufferPartInfoAu8FDHBHu32BPIC,
        "Eur_EGenTL_dsGetBufferPartInfo__as__uint8_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
    )
)
Eur_EGenTL_dsGetBufferPartInfo__as__uint16_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = (
    errorCheck(
        dll.euEGenTL_dsGetBufferPartInfoAu16FDHBHu32BPIC,
        "Eur_EGenTL_dsGetBufferPartInfo__as__uint16_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
    )
)
Eur_EGenTL_dsGetBufferPartInfo__as__uint32_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = (
    errorCheck(
        dll.euEGenTL_dsGetBufferPartInfoAu32FDHBHu32BPIC,
        "Eur_EGenTL_dsGetBufferPartInfo__as__uint32_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
    )
)
Eur_EGenTL_dsGetBufferPartInfo__as__uint64_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = (
    errorCheck(
        dll.euEGenTL_dsGetBufferPartInfoAu64FDHBHu32BPIC,
        "Eur_EGenTL_dsGetBufferPartInfo__as__uint64_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
    )
)
Eur_EGenTL_dsGetBufferPartInfo__as__double__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferPartInfoAdFDHBHu32BPIC,
    "Eur_EGenTL_dsGetBufferPartInfo__as__double__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
)
Eur_EGenTL_dsGetBufferPartInfo__as__float__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferPartInfoAfFDHBHu32BPIC,
    "Eur_EGenTL_dsGetBufferPartInfo__as__float__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
)
Eur_EGenTL_dsGetBufferPartInfo__as__uint8_t_ptr__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferPartInfoAu8pFDHBHu32BPIC,
    "Eur_EGenTL_dsGetBufferPartInfo__as__uint8_t_ptr__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
)
Eur_EGenTL_dsGetBufferPartInfo__as__std_string__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferPartInfoASsFDHBHu32BPIC,
    "Eur_EGenTL_dsGetBufferPartInfo__as__std_string__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
)
Eur_EGenTL_dsGetBufferPartInfo__as__void_ptr__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = (
    errorCheck(
        dll.euEGenTL_dsGetBufferPartInfoAvptrFDHBHu32BPIC,
        "Eur_EGenTL_dsGetBufferPartInfo__as__void_ptr__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
    )
)
Eur_EGenTL_dsGetBufferPartInfo__as__std_vector_char__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferPartInfoASvcFDHBHu32BPIC,
    "Eur_EGenTL_dsGetBufferPartInfo__as__std_vector_char__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
)
Eur_EGenTL_dsGetBufferPartInfo__as__std_vector_std_string__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferPartInfoASv_std_stringFDHBHu32BPIC,
    "Eur_EGenTL_dsGetBufferPartInfo__as__std_vector_std_string__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
)
Eur_EGenTL_dsGetBufferPartInfo__as__bool8_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = (
    errorCheck(
        dll.euEGenTL_dsGetBufferPartInfoAb8FDHBHu32BPIC,
        "Eur_EGenTL_dsGetBufferPartInfo__as__bool8_t__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
    )
)
Eur_EGenTL_dsGetBufferPartInfo__as__char_ptr__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = (
    errorCheck(
        dll.euEGenTL_dsGetBufferPartInfoAcptrFDHBHu32BPIC,
        "Eur_EGenTL_dsGetBufferPartInfo__as__char_ptr__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
    )
)
Eur_EGenTL_dsGetBufferPartInfo__as__InfoCommandInfo__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD = errorCheck(
    dll.euEGenTL_dsGetBufferPartInfoA_CINFOFDHBHu32BPIC,
    "Eur_EGenTL_dsGetBufferPartInfo__as__InfoCommandInfo__from__DS_HANDLE__BUFFER_HANDLE__uint32_t__BUFFER_PART_INFO_CMD",
)
Eur_EGenTL_gcGetNumPortURLs__from__PORT_HANDLE = errorCheck(
    dll.euEGenTL_gcGetNumPortURLsFPH, "Eur_EGenTL_gcGetNumPortURLs__from__PORT_HANDLE"
)
Eur_EGenTL_gcGetPortURLInfo__as__size_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoAsFPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__size_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcGetPortURLInfo__as__int8_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoAi8FPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__int8_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcGetPortURLInfo__as__int16_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoAi16FPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__int16_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcGetPortURLInfo__as__int32_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoAi32FPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__int32_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcGetPortURLInfo__as__int64_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoAi64FPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__int64_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcGetPortURLInfo__as__uint8_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoAu8FPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__uint8_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcGetPortURLInfo__as__uint16_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoAu16FPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__uint16_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcGetPortURLInfo__as__uint32_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoAu32FPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__uint32_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcGetPortURLInfo__as__uint64_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoAu64FPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__uint64_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcGetPortURLInfo__as__double__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoAdFPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__double__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcGetPortURLInfo__as__float__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoAfFPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__float__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcGetPortURLInfo__as__uint8_t_ptr__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoAu8pFPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__uint8_t_ptr__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcGetPortURLInfo__as__std_string__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoASsFPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__std_string__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcGetPortURLInfo__as__void_ptr__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoAvptrFPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__void_ptr__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcGetPortURLInfo__as__std_vector_char__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoASvcFPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__std_vector_char__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcGetPortURLInfo__as__std_vector_std_string__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoASv_std_stringFPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__std_vector_std_string__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcGetPortURLInfo__as__bool8_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoAb8FPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__bool8_t__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcGetPortURLInfo__as__char_ptr__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoAcptrFPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__char_ptr__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcGetPortURLInfo__as__InfoCommandInfo__from__PORT_HANDLE__uint32_t__URL_INFO_CMD = errorCheck(
    dll.euEGenTL_gcGetPortURLInfoA_CINFOFPHu32UIC,
    "Eur_EGenTL_gcGetPortURLInfo__as__InfoCommandInfo__from__PORT_HANDLE__uint32_t__URL_INFO_CMD",
)
Eur_EGenTL_gcReadPortStacked__from__PORT_HANDLE__std_vector_PORT_REGISTER_STACK_ENTRY = errorCheck(
    dll.euEGenTL_gcReadPortStackedFPHSv_PRSE,
    "Eur_EGenTL_gcReadPortStacked__from__PORT_HANDLE__std_vector_PORT_REGISTER_STACK_ENTRY",
)
Eur_EGenTL_gcWritePortStacked__from__PORT_HANDLE__std_vector_PORT_REGISTER_STACK_ENTRY = errorCheck(
    dll.euEGenTL_gcWritePortStackedFPHSv_PRSE,
    "Eur_EGenTL_gcWritePortStacked__from__PORT_HANDLE__std_vector_PORT_REGISTER_STACK_ENTRY",
)
Eur_EGenTL_ifGetParent__from__IF_HANDLE = errorCheck(
    dll.euEGenTL_ifGetParentFIH, "Eur_EGenTL_ifGetParent__from__IF_HANDLE"
)
Eur_EGenTL_devGetParent__from__DEV_HANDLE = errorCheck(
    dll.euEGenTL_devGetParentFDH, "Eur_EGenTL_devGetParent__from__DEV_HANDLE"
)
Eur_EGenTL_dsGetParent__from__DS_HANDLE = errorCheck(
    dll.euEGenTL_dsGetParentFDH, "Eur_EGenTL_dsGetParent__from__DS_HANDLE"
)
Eur_EGenTL_memento__from__const_char_p = errorCheck(dll.euEGenTL_mementoFccp, "Eur_EGenTL_memento__from__const_char_p")
Eur_EGenTL_memento__from__unsigned_char__unsigned_char__const_char_p = errorCheck(
    dll.euEGenTL_mementoFucucccp, "Eur_EGenTL_memento__from__unsigned_char__unsigned_char__const_char_p"
)
Eur_EGenTL_mementoWaveUp__from__unsigned_char__unsigned_char = errorCheck(
    dll.euEGenTL_mementoWaveUpFucuc, "Eur_EGenTL_mementoWaveUp__from__unsigned_char__unsigned_char"
)
Eur_EGenTL_mementoWaveDown__from__unsigned_char__unsigned_char = errorCheck(
    dll.euEGenTL_mementoWaveDownFucuc, "Eur_EGenTL_mementoWaveDown__from__unsigned_char__unsigned_char"
)
Eur_EGenTL_mementoWaveReset__from__unsigned_char__unsigned_char = errorCheck(
    dll.euEGenTL_mementoWaveResetFucuc, "Eur_EGenTL_mementoWaveReset__from__unsigned_char__unsigned_char"
)
Eur_EGenTL_mementoWaveValue__from__unsigned_char__unsigned_char__uint64_t = errorCheck(
    dll.euEGenTL_mementoWaveValueFucucu64, "Eur_EGenTL_mementoWaveValue__from__unsigned_char__unsigned_char__uint64_t"
)
Eur_EGenTL_mementoWaveNoValue__from__unsigned_char__unsigned_char = errorCheck(
    dll.euEGenTL_mementoWaveNoValueFucuc, "Eur_EGenTL_mementoWaveNoValue__from__unsigned_char__unsigned_char"
)
Eur_EGenTL_getTimestampUs = errorCheck(dll.euEGenTL_getTimestampUs, "Eur_EGenTL_getTimestampUs")
Eur_EGenTL_genapiSetString__from__PORT_HANDLE__const_char_p__const_char_p = errorCheck(
    dll.euEGenTL_genapiSetStringFPHccpccp, "Eur_EGenTL_genapiSetString__from__PORT_HANDLE__const_char_p__const_char_p"
)
Eur_EGenTL_genapiGetString__from__PORT_HANDLE__const_char_p = errorCheck(
    dll.euEGenTL_genapiGetStringFPHccp, "Eur_EGenTL_genapiGetString__from__PORT_HANDLE__const_char_p"
)
Eur_EGenTL_genapiGetStringData__from__PORT_HANDLE__const_char_p__std_vector_char = errorCheck(
    dll.euEGenTL_genapiGetStringDataFPHccpSvc,
    "Eur_EGenTL_genapiGetStringData__from__PORT_HANDLE__const_char_p__std_vector_char",
)
Eur_EGenTL_genapiGetStringList__from__PORT_HANDLE__const_char_p = errorCheck(
    dll.euEGenTL_genapiGetStringListFPHccp, "Eur_EGenTL_genapiGetStringList__from__PORT_HANDLE__const_char_p"
)
Eur_EGenTL_genapiSetInteger__from__PORT_HANDLE__const_char_p__int64_t = errorCheck(
    dll.euEGenTL_genapiSetIntegerFPHccpi64, "Eur_EGenTL_genapiSetInteger__from__PORT_HANDLE__const_char_p__int64_t"
)
Eur_EGenTL_genapiGetInteger__from__PORT_HANDLE__const_char_p = errorCheck(
    dll.euEGenTL_genapiGetIntegerFPHccp, "Eur_EGenTL_genapiGetInteger__from__PORT_HANDLE__const_char_p"
)
Eur_EGenTL_genapiGetIntegerWithDefault__from__PORT_HANDLE__const_char_p__int64_t = errorCheck(
    dll.euEGenTL_genapiGetIntegerWithDefaultFPHccpi64,
    "Eur_EGenTL_genapiGetIntegerWithDefault__from__PORT_HANDLE__const_char_p__int64_t",
)
Eur_EGenTL_genapiSetFloat__from__PORT_HANDLE__const_char_p__double = errorCheck(
    dll.euEGenTL_genapiSetFloatFPHccpd, "Eur_EGenTL_genapiSetFloat__from__PORT_HANDLE__const_char_p__double"
)
Eur_EGenTL_genapiGetFloat__from__PORT_HANDLE__const_char_p = errorCheck(
    dll.euEGenTL_genapiGetFloatFPHccp, "Eur_EGenTL_genapiGetFloat__from__PORT_HANDLE__const_char_p"
)
Eur_EGenTL_genapiGetFloatWithDefault__from__PORT_HANDLE__const_char_p__double = errorCheck(
    dll.euEGenTL_genapiGetFloatWithDefaultFPHccpd,
    "Eur_EGenTL_genapiGetFloatWithDefault__from__PORT_HANDLE__const_char_p__double",
)
Eur_EGenTL_genapiSetRegister__from__PORT_HANDLE__const_char_p__void_p__size_t = errorCheck(
    dll.euEGenTL_genapiSetRegisterFPHccpvps,
    "Eur_EGenTL_genapiSetRegister__from__PORT_HANDLE__const_char_p__void_p__size_t",
)
Eur_EGenTL_genapiGetRegister__from__PORT_HANDLE__const_char_p__void_p__size_t = errorCheck(
    dll.euEGenTL_genapiGetRegisterFPHccpvps,
    "Eur_EGenTL_genapiGetRegister__from__PORT_HANDLE__const_char_p__void_p__size_t",
)
Eur_EGenTL_genapiExecuteCommand__from__PORT_HANDLE__const_char_p = errorCheck(
    dll.euEGenTL_genapiExecuteCommandFPHccp, "Eur_EGenTL_genapiExecuteCommand__from__PORT_HANDLE__const_char_p"
)
Eur_EGenTL_genapiAttachEvent__from__PORT_HANDLE__uint64_t__void_p__size_t = errorCheck(
    dll.euEGenTL_genapiAttachEventFPHu64vps, "Eur_EGenTL_genapiAttachEvent__from__PORT_HANDLE__uint64_t__void_p__size_t"
)
Eur_EGenTL_genapiInvalidate__from__PORT_HANDLE__const_char_p = errorCheck(
    dll.euEGenTL_genapiInvalidateFPHccp, "Eur_EGenTL_genapiInvalidate__from__PORT_HANDLE__const_char_p"
)
Eur_EGenTL_genapiRunScript__from__PORT_HANDLE__const_char_p__GENAPI_UI_SCRIPT_CONTEXT_p = errorCheck(
    dll.euEGenTL_genapiRunScriptFPHccpGENAPI_UI_SCRIPT_CONTEXT_p,
    "Eur_EGenTL_genapiRunScript__from__PORT_HANDLE__const_char_p__GENAPI_UI_SCRIPT_CONTEXT_p",
)
Eur_EGenTL_genapiRunScript__from__PORT_HANDLE__const_char_p = errorCheck(
    dll.euEGenTL_genapiRunScriptFPHccp, "Eur_EGenTL_genapiRunScript__from__PORT_HANDLE__const_char_p"
)
Eur_EGenTL_genapiRunScript__from__std_vector_PORT_HANDLE__const_char_p__GENAPI_UI_SCRIPT_CONTEXT_p = errorCheck(
    dll.euEGenTL_genapiRunScriptFSv_PHccpGENAPI_UI_SCRIPT_CONTEXT_p,
    "Eur_EGenTL_genapiRunScript__from__std_vector_PORT_HANDLE__const_char_p__GENAPI_UI_SCRIPT_CONTEXT_p",
)
Eur_EGenTL_genapiRunScript__from__std_vector_PORT_HANDLE__const_char_p = errorCheck(
    dll.euEGenTL_genapiRunScriptFSv_PHccp, "Eur_EGenTL_genapiRunScript__from__std_vector_PORT_HANDLE__const_char_p"
)
Eur_EGenTL_genapiInterruptScript__from__const_char_p = errorCheck(
    dll.euEGenTL_genapiInterruptScriptFccp, "Eur_EGenTL_genapiInterruptScript__from__const_char_p"
)
Eur_EGenTL_imageGetPixelFormatValue__from__const_char_p__unsigned_int = errorCheck(
    dll.euEGenTL_imageGetPixelFormatValueFccpui, "Eur_EGenTL_imageGetPixelFormatValue__from__const_char_p__unsigned_int"
)
Eur_EGenTL_imageGetPixelFormat__from__uint64_t = errorCheck(
    dll.euEGenTL_imageGetPixelFormatFu64, "Eur_EGenTL_imageGetPixelFormat__from__uint64_t"
)
Eur_EGenTL_imageGetBytesPerPixel__from__const_char_p = errorCheck(
    dll.euEGenTL_imageGetBytesPerPixelFccp, "Eur_EGenTL_imageGetBytesPerPixel__from__const_char_p"
)
Eur_EGenTL_imageGetBitsPerPixel__from__const_char_p = errorCheck(
    dll.euEGenTL_imageGetBitsPerPixelFccp, "Eur_EGenTL_imageGetBitsPerPixel__from__const_char_p"
)
Eur_EGenTL_imageConvert__from__ImageConvertInput_p__ImageConvertOutput_p__ImageConvertROI_p = errorCheck(
    dll.euEGenTL_imageConvertF_ICI_p_ICO_pImageConvertROI_p,
    "Eur_EGenTL_imageConvert__from__ImageConvertInput_p__ImageConvertOutput_p__ImageConvertROI_p",
)
Eur_EGenTL_imageConvert__from__ImageConvertInput_p__ImageConvertOutput_p = errorCheck(
    dll.euEGenTL_imageConvertF_ICI_p_ICO_p, "Eur_EGenTL_imageConvert__from__ImageConvertInput_p__ImageConvertOutput_p"
)
Eur_EGenTL_imageSaveToDisk__from__ImageConvertInput_p__const_char_p__int64_t__ImageSaveToDiskParams_p = errorCheck(
    dll.euEGenTL_imageSaveToDiskF_ICI_pccpi64_ISTDP_p,
    "Eur_EGenTL_imageSaveToDisk__from__ImageConvertInput_p__const_char_p__int64_t__ImageSaveToDiskParams_p",
)
Eur_EGenTL_imageSaveToDisk__from__ImageConvertInput_p__const_char_p__int64_t = errorCheck(
    dll.euEGenTL_imageSaveToDiskF_ICI_pccpi64,
    "Eur_EGenTL_imageSaveToDisk__from__ImageConvertInput_p__const_char_p__int64_t",
)
Eur_EGenTL_imageSaveToDisk__from__ImageConvertInput_p__const_char_p = errorCheck(
    dll.euEGenTL_imageSaveToDiskF_ICI_pccp, "Eur_EGenTL_imageSaveToDisk__from__ImageConvertInput_p__const_char_p"
)
Eur_EGenTL_imageGet__from__ImageId__size_t_p = errorCheck(
    dll.euEGenTL_imageGetFImageIdsp, "Eur_EGenTL_imageGet__from__ImageId__size_t_p"
)
Eur_EGenTL_imageGet__from__ImageId = errorCheck(dll.euEGenTL_imageGetFImageId, "Eur_EGenTL_imageGet__from__ImageId")
Eur_EGenTL_imageRelease__from__ImageId = errorCheck(
    dll.euEGenTL_imageReleaseFImageId, "Eur_EGenTL_imageRelease__from__ImageId"
)
Eur_EGenTL_isShared = errorCheck(dll.euEGenTL_isShared, "Eur_EGenTL_isShared")
Eur_EGenTL_eventKillQuiet__from__EVENT_HANDLE = errorCheck(
    dll.euEGenTL_eventKillQuietFEH, "Eur_EGenTL_eventKillQuiet__from__EVENT_HANDLE"
)
Eur_EGenTL_lockUpdates = errorCheck(dll.euEGenTL_lockUpdates, "Eur_EGenTL_lockUpdates")
Eur_EGenTL_unlockUpdates = errorCheck(dll.euEGenTL_unlockUpdates, "Eur_EGenTL_unlockUpdates")
Eur_EGenTL_destroy = errorCheck(dll.euEGenTL_destroy, "Eur_EGenTL_destroy")
Eur_EGrabberDiscovery_create__from__Eur_EGenTL = errorCheck(
    dll.euEurEGDiscovery_createFEur_EGenTL, "Eur_EGrabberDiscovery_create__from__Eur_EGenTL"
)
Eur_EGrabberDiscovery_discover__from__bool8_t = errorCheck(
    dll.euEurEGDiscovery_discoverFb8, "Eur_EGrabberDiscovery_discover__from__bool8_t"
)
Eur_EGrabberDiscovery_discover = errorCheck(dll.euEurEGDiscovery_discover, "Eur_EGrabberDiscovery_discover")
Eur_EGrabberDiscovery_egrabberCount = errorCheck(
    dll.euEurEGDiscovery_egrabberCount, "Eur_EGrabberDiscovery_egrabberCount"
)
Eur_EGrabberDiscovery_egrabbers__from__int = errorCheck(
    dll.euEurEGDiscovery_egrabbersFi, "Eur_EGrabberDiscovery_egrabbers__from__int"
)
Eur_EGrabberDiscovery_cameraCount = errorCheck(dll.euEurEGDiscovery_cameraCount, "Eur_EGrabberDiscovery_cameraCount")
Eur_EGrabberDiscovery_cameras__from__int__int = errorCheck(
    dll.euEurEGDiscovery_camerasFii, "Eur_EGrabberDiscovery_cameras__from__int__int"
)
Eur_EGrabberDiscovery_cameras__from__int = errorCheck(
    dll.euEurEGDiscovery_camerasFi, "Eur_EGrabberDiscovery_cameras__from__int"
)
Eur_EGrabberDiscovery_cameras__from__const_char_p__int = errorCheck(
    dll.euEurEGDiscovery_camerasFccpi, "Eur_EGrabberDiscovery_cameras__from__const_char_p__int"
)
Eur_EGrabberDiscovery_cameras__from__const_char_p = errorCheck(
    dll.euEurEGDiscovery_camerasFccp, "Eur_EGrabberDiscovery_cameras__from__const_char_p"
)
Eur_EGrabberDiscovery_interfaceCount = errorCheck(
    dll.euEurEGDiscovery_interfaceCount, "Eur_EGrabberDiscovery_interfaceCount"
)
Eur_EGrabberDiscovery_interfaceInfo__from__int = errorCheck(
    dll.euEurEGDiscovery_interfaceInfoFi, "Eur_EGrabberDiscovery_interfaceInfo__from__int"
)
Eur_EGrabberDiscovery_deviceCount__from__int = errorCheck(
    dll.euEurEGDiscovery_deviceCountFi, "Eur_EGrabberDiscovery_deviceCount__from__int"
)
Eur_EGrabberDiscovery_deviceInfo__from__int__int = errorCheck(
    dll.euEurEGDiscovery_deviceInfoFii, "Eur_EGrabberDiscovery_deviceInfo__from__int__int"
)
Eur_EGrabberDiscovery_streamCount__from__int__int = errorCheck(
    dll.euEurEGDiscovery_streamCountFii, "Eur_EGrabberDiscovery_streamCount__from__int__int"
)
Eur_EGrabberDiscovery_streamInfo__from__int__int__int = errorCheck(
    dll.euEurEGDiscovery_streamInfoFiii, "Eur_EGrabberDiscovery_streamInfo__from__int__int__int"
)
Eur_EGrabberDiscovery_destroy = errorCheck(dll.euEurEGDiscovery_destroy, "Eur_EGrabberDiscovery_destroy")
Eur_getEventDescription__from__EVENT_DATA_NUMID_CUSTOM = errorCheck(
    dll.eugetEventDescriptionFEDNC, "Eur_getEventDescription__from__EVENT_DATA_NUMID_CUSTOM"
)
Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGenTL__int__int__int__DEVICE_ACCESS_FLAGS__bool8_t = errorCheck(
    dll.euEGCOD_createFEur_EGenTLiiiDAFb8,
    "Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGenTL__int__int__int__DEVICE_ACCESS_FLAGS__bool8_t",
)
Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGenTL__int__int__int__DEVICE_ACCESS_FLAGS = errorCheck(
    dll.euEGCOD_createFEur_EGenTLiiiDAF,
    "Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGenTL__int__int__int__DEVICE_ACCESS_FLAGS",
)
Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGenTL__int__int__int = errorCheck(
    dll.euEGCOD_createFEur_EGenTLiii, "Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGenTL__int__int__int"
)
Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGenTL__int__int = errorCheck(
    dll.euEGCOD_createFEur_EGenTLii, "Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGenTL__int__int"
)
Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGenTL__int = errorCheck(
    dll.euEGCOD_createFEur_EGenTLi, "Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGenTL__int"
)
Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGenTL = errorCheck(
    dll.euEGCOD_createFEur_EGenTL, "Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGenTL"
)
Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGrabberInfo__DEVICE_ACCESS_FLAGS__bool8_t = errorCheck(
    dll.euEGCOD_createFEurEGInfoDAFb8,
    "Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGrabberInfo__DEVICE_ACCESS_FLAGS__bool8_t",
)
Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGrabberInfo__DEVICE_ACCESS_FLAGS = errorCheck(
    dll.euEGCOD_createFEurEGInfoDAF, "Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGrabberInfo__DEVICE_ACCESS_FLAGS"
)
Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGrabberInfo = errorCheck(
    dll.euEGCOD_createFEurEGInfo, "Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGrabberInfo"
)
Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGrabberCameraInfo__DEVICE_ACCESS_FLAGS = errorCheck(
    dll.euEGCOD_createFEurEGCameraInfoDAF,
    "Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGrabberCameraInfo__DEVICE_ACCESS_FLAGS",
)
Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGrabberCameraInfo = errorCheck(
    dll.euEGCOD_createFEurEGCameraInfo, "Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGrabberCameraInfo"
)
Eur_EGrabber_CallbackOnDemand_reallocBuffers__from__size_t__size_t = errorCheck(
    dll.euEGCOD_reallocBuffersFss, "Eur_EGrabber_CallbackOnDemand_reallocBuffers__from__size_t__size_t"
)
Eur_EGrabber_CallbackOnDemand_reallocBuffers__from__size_t = errorCheck(
    dll.euEGCOD_reallocBuffersFs, "Eur_EGrabber_CallbackOnDemand_reallocBuffers__from__size_t"
)
Eur_EGrabber_CallbackOnDemand_announceAndQueue__from__Eur_GenTLMemory__size_t = errorCheck(
    dll.euEGCOD_announceAndQueueFEur_GenTLMemorys,
    "Eur_EGrabber_CallbackOnDemand_announceAndQueue__from__Eur_GenTLMemory__size_t",
)
Eur_EGrabber_CallbackOnDemand_announceAndQueue__from__Eur_GenTLMemory = errorCheck(
    dll.euEGCOD_announceAndQueueFEur_GenTLMemory,
    "Eur_EGrabber_CallbackOnDemand_announceAndQueue__from__Eur_GenTLMemory",
)
Eur_EGrabber_CallbackOnDemand_announceAndQueue__from__Eur_UserMemory = errorCheck(
    dll.euEGCOD_announceAndQueueFEur_UserMemory, "Eur_EGrabber_CallbackOnDemand_announceAndQueue__from__Eur_UserMemory"
)
Eur_EGrabber_CallbackOnDemand_announceAndQueue__from__Eur_UserMemoryArray = errorCheck(
    dll.euEGCOD_announceAndQueueFEur_UserMemoryArray,
    "Eur_EGrabber_CallbackOnDemand_announceAndQueue__from__Eur_UserMemoryArray",
)
Eur_EGrabber_CallbackOnDemand_announceAndQueue__from__Eur_UserMemoryArray__bool8_t = errorCheck(
    dll.euEGCOD_announceAndQueueFEur_UserMemoryArrayb8,
    "Eur_EGrabber_CallbackOnDemand_announceAndQueue__from__Eur_UserMemoryArray__bool8_t",
)
Eur_EGrabber_CallbackOnDemand_announceAndQueue__from__Eur_BusMemory = errorCheck(
    dll.euEGCOD_announceAndQueueFEur_BusMemory, "Eur_EGrabber_CallbackOnDemand_announceAndQueue__from__Eur_BusMemory"
)
Eur_EGrabber_CallbackOnDemand_announceAndQueue__from__Eur_NvidiaRdmaMemory = errorCheck(
    dll.euEGCOD_announceAndQueueFEur_NvidiaRdmaMemory,
    "Eur_EGrabber_CallbackOnDemand_announceAndQueue__from__Eur_NvidiaRdmaMemory",
)
Eur_EGrabber_CallbackOnDemand_flushBuffers__from__ACQ_QUEUE_TYPE = errorCheck(
    dll.euEGCOD_flushBuffersFAQT, "Eur_EGrabber_CallbackOnDemand_flushBuffers__from__ACQ_QUEUE_TYPE"
)
Eur_EGrabber_CallbackOnDemand_flushBuffers = errorCheck(
    dll.euEGCOD_flushBuffers, "Eur_EGrabber_CallbackOnDemand_flushBuffers"
)
Eur_EGrabber_CallbackOnDemand_resetBufferQueue = errorCheck(
    dll.euEGCOD_resetBufferQueue, "Eur_EGrabber_CallbackOnDemand_resetBufferQueue"
)
Eur_EGrabber_CallbackOnDemand_resetBufferQueue__from__Eur_BufferIndexRange = errorCheck(
    dll.euEGCOD_resetBufferQueueFEur_BufferIndexRange,
    "Eur_EGrabber_CallbackOnDemand_resetBufferQueue__from__Eur_BufferIndexRange",
)
Eur_EGrabber_CallbackOnDemand_queue__from__Eur_BufferIndexRange = errorCheck(
    dll.euEGCOD_queueFEur_BufferIndexRange, "Eur_EGrabber_CallbackOnDemand_queue__from__Eur_BufferIndexRange"
)
Eur_EGrabber_CallbackOnDemand_revoke__from__Eur_BufferIndexRange = errorCheck(
    dll.euEGCOD_revokeFEur_BufferIndexRange, "Eur_EGrabber_CallbackOnDemand_revoke__from__Eur_BufferIndexRange"
)
Eur_EGrabber_CallbackOnDemand_shouldReannounceBuffers = errorCheck(
    dll.euEGCOD_shouldReannounceBuffers, "Eur_EGrabber_CallbackOnDemand_shouldReannounceBuffers"
)
Eur_EGrabber_CallbackOnDemand_shouldReallocBuffers = errorCheck(
    dll.euEGCOD_shouldReallocBuffers, "Eur_EGrabber_CallbackOnDemand_shouldReallocBuffers"
)
Eur_EGrabber_CallbackOnDemand_start__from__uint64_t__bool8_t = errorCheck(
    dll.euEGCOD_startFu64b8, "Eur_EGrabber_CallbackOnDemand_start__from__uint64_t__bool8_t"
)
Eur_EGrabber_CallbackOnDemand_start__from__uint64_t = errorCheck(
    dll.euEGCOD_startFu64, "Eur_EGrabber_CallbackOnDemand_start__from__uint64_t"
)
Eur_EGrabber_CallbackOnDemand_start = errorCheck(dll.euEGCOD_start, "Eur_EGrabber_CallbackOnDemand_start")
Eur_EGrabber_CallbackOnDemand_stop = errorCheck(dll.euEGCOD_stop, "Eur_EGrabber_CallbackOnDemand_stop")
Eur_EGrabber_CallbackOnDemand_getWidth = errorCheck(dll.euEGCOD_getWidth, "Eur_EGrabber_CallbackOnDemand_getWidth")
Eur_EGrabber_CallbackOnDemand_getHeight = errorCheck(dll.euEGCOD_getHeight, "Eur_EGrabber_CallbackOnDemand_getHeight")
Eur_EGrabber_CallbackOnDemand_getPayloadSize = errorCheck(
    dll.euEGCOD_getPayloadSize, "Eur_EGrabber_CallbackOnDemand_getPayloadSize"
)
Eur_EGrabber_CallbackOnDemand_getPixelFormat = errorCheck(
    dll.euEGCOD_getPixelFormat, "Eur_EGrabber_CallbackOnDemand_getPixelFormat"
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__size_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAsOSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__size_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__int8_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAi8OSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__int8_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__int16_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAi16OSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__int16_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__int32_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAi32OSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__int32_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__int64_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAi64OSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__int64_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint8_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu8OSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint8_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint16_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu16OSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint16_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint32_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu32OSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint32_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint64_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu64OSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint64_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__double__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAdOSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__double__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__float__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAfOSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__float__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint8_t_ptr__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu8pOSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint8_t_ptr__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__std_string__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoASsOSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__std_string__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__void_ptr__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAvptrOSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__void_ptr__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__std_vector_char__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoASvcOSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__std_vector_char__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__std_vector_std_string__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoASv_std_stringOSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__std_vector_std_string__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__bool8_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAb8OSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__bool8_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__char_ptr__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAcptrOSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__char_ptr__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__InfoCommandInfo__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoA_CINFOOSystemModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__InfoCommandInfo__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__size_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAsOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__size_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__int8_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAi8OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__int8_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__int16_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAi16OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__int16_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__int32_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAi32OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__int32_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__int64_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAi64OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__int64_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint8_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu8OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint8_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint16_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu16OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint16_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint32_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu32OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint32_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint64_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu64OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint64_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__double__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAdOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__double__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__float__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAfOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__float__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint8_t_ptr__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu8pOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint8_t_ptr__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__std_string__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoASsOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__std_string__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__void_ptr__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAvptrOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__void_ptr__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__std_vector_char__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoASvcOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__std_vector_char__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__std_vector_std_string__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoASv_std_stringOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__std_vector_std_string__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__bool8_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAb8OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__bool8_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__char_ptr__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAcptrOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__char_ptr__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__InfoCommandInfo__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoA_CINFOOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__InfoCommandInfo__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__size_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAsODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__size_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__int8_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAi8ODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__int8_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__int16_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAi16ODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__int16_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__int32_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAi32ODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__int32_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__int64_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAi64ODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__int64_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint8_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu8ODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint8_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint16_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu16ODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint16_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint32_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu32ODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint32_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint64_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu64ODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint64_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__double__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAdODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__double__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__float__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAfODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__float__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint8_t_ptr__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu8pODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint8_t_ptr__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__std_string__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoASsODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__std_string__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__void_ptr__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAvptrODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__void_ptr__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__std_vector_char__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoASvcODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__std_vector_char__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__std_vector_std_string__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoASv_std_stringODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__std_vector_std_string__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__bool8_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAb8ODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__bool8_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__char_ptr__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAcptrODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__char_ptr__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__InfoCommandInfo__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoA_CINFOODeviceModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__InfoCommandInfo__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__size_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAsOStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__size_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__int8_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAi8OStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__int8_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__int16_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAi16OStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__int16_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__int32_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAi32OStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__int32_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__int64_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAi64OStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__int64_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint8_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu8OStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint8_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint16_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu16OStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint16_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint32_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu32OStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint32_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint64_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu64OStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint64_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__double__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAdOStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__double__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__float__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAfOStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__float__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__uint8_t_ptr__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAu8pOStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__uint8_t_ptr__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__std_string__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoASsOStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__std_string__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__void_ptr__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAvptrOStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__void_ptr__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__std_vector_char__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoASvcOStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__std_vector_char__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__std_vector_std_string__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoASv_std_stringOStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__std_vector_std_string__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__bool8_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAb8OStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__bool8_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__char_ptr__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoAcptrOStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__char_ptr__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getInfo__as__InfoCommandInfo__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGCOD_getInfoA_CINFOOStreamModuleFi32,
    "Eur_EGrabber_CallbackOnDemand_getInfo__as__InfoCommandInfo__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__size_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoAsFsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__size_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__int8_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoAi8FsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__int8_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__int16_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoAi16FsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__int16_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__int32_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoAi32FsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__int32_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__int64_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoAi64FsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__int64_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__uint8_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoAu8FsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__uint8_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__uint16_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoAu16FsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__uint16_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__uint32_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoAu32FsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__uint32_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__uint64_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoAu64FsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__uint64_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__double__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoAdFsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__double__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__float__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoAfFsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__float__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__uint8_t_ptr__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoAu8pFsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__uint8_t_ptr__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__std_string__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoASsFsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__std_string__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__void_ptr__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoAvptrFsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__void_ptr__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__std_vector_char__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoASvcFsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__std_vector_char__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__std_vector_std_string__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoASv_std_stringFsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__std_vector_std_string__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__bool8_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoAb8FsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__bool8_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__char_ptr__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoAcptrFsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__char_ptr__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__InfoCommandInfo__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGCOD_getBufferInfoA_CINFOFsBIC,
    "Eur_EGrabber_CallbackOnDemand_getBufferInfo__as__InfoCommandInfo__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackOnDemand_getBufferData__from__size_t = errorCheck(
    dll.euEGCOD_getBufferDataFs, "Eur_EGrabber_CallbackOnDemand_getBufferData__from__size_t"
)
Eur_EGrabber_CallbackOnDemand_isOpen__on__SystemModule = errorCheck(
    dll.euEGCOD_isOpenOSystemModule, "Eur_EGrabber_CallbackOnDemand_isOpen__on__SystemModule"
)
Eur_EGrabber_CallbackOnDemand_isOpen__on__InterfaceModule = errorCheck(
    dll.euEGCOD_isOpenOInterfaceModule, "Eur_EGrabber_CallbackOnDemand_isOpen__on__InterfaceModule"
)
Eur_EGrabber_CallbackOnDemand_isOpen__on__DeviceModule = errorCheck(
    dll.euEGCOD_isOpenODeviceModule, "Eur_EGrabber_CallbackOnDemand_isOpen__on__DeviceModule"
)
Eur_EGrabber_CallbackOnDemand_isOpen__on__StreamModule = errorCheck(
    dll.euEGCOD_isOpenOStreamModule, "Eur_EGrabber_CallbackOnDemand_isOpen__on__StreamModule"
)
Eur_EGrabber_CallbackOnDemand_isOpen__on__RemoteModule = errorCheck(
    dll.euEGCOD_isOpenORemoteModule, "Eur_EGrabber_CallbackOnDemand_isOpen__on__RemoteModule"
)
Eur_EGrabber_CallbackOnDemand_gcReadPortData__on__SystemModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGCOD_gcReadPortDataOSystemModuleFu64vps,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortData__on__SystemModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortData__on__InterfaceModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGCOD_gcReadPortDataOInterfaceModuleFu64vps,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortData__on__InterfaceModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortData__on__DeviceModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGCOD_gcReadPortDataODeviceModuleFu64vps,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortData__on__DeviceModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortData__on__StreamModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGCOD_gcReadPortDataOStreamModuleFu64vps,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortData__on__StreamModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortData__on__RemoteModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGCOD_gcReadPortDataORemoteModuleFu64vps,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortData__on__RemoteModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortData__on__SystemModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGCOD_gcWritePortDataOSystemModuleFu64vps,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortData__on__SystemModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortData__on__InterfaceModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGCOD_gcWritePortDataOInterfaceModuleFu64vps,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortData__on__InterfaceModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortData__on__DeviceModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGCOD_gcWritePortDataODeviceModuleFu64vps,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortData__on__DeviceModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortData__on__StreamModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGCOD_gcWritePortDataOStreamModuleFu64vps,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortData__on__StreamModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortData__on__RemoteModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGCOD_gcWritePortDataORemoteModuleFu64vps,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortData__on__RemoteModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPort__on__SystemModule__from__uint64_t__size_t = errorCheck(
    dll.euEGCOD_gcReadPortOSystemModuleFu64s,
    "Eur_EGrabber_CallbackOnDemand_gcReadPort__on__SystemModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPort__on__InterfaceModule__from__uint64_t__size_t = errorCheck(
    dll.euEGCOD_gcReadPortOInterfaceModuleFu64s,
    "Eur_EGrabber_CallbackOnDemand_gcReadPort__on__InterfaceModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPort__on__DeviceModule__from__uint64_t__size_t = errorCheck(
    dll.euEGCOD_gcReadPortODeviceModuleFu64s,
    "Eur_EGrabber_CallbackOnDemand_gcReadPort__on__DeviceModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPort__on__StreamModule__from__uint64_t__size_t = errorCheck(
    dll.euEGCOD_gcReadPortOStreamModuleFu64s,
    "Eur_EGrabber_CallbackOnDemand_gcReadPort__on__StreamModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPort__on__RemoteModule__from__uint64_t__size_t = errorCheck(
    dll.euEGCOD_gcReadPortORemoteModuleFu64s,
    "Eur_EGrabber_CallbackOnDemand_gcReadPort__on__RemoteModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePort__on__SystemModule__from__uint64_t__std_vector_char = errorCheck(
    dll.euEGCOD_gcWritePortOSystemModuleFu64Svc,
    "Eur_EGrabber_CallbackOnDemand_gcWritePort__on__SystemModule__from__uint64_t__std_vector_char",
)
Eur_EGrabber_CallbackOnDemand_gcWritePort__on__InterfaceModule__from__uint64_t__std_vector_char = errorCheck(
    dll.euEGCOD_gcWritePortOInterfaceModuleFu64Svc,
    "Eur_EGrabber_CallbackOnDemand_gcWritePort__on__InterfaceModule__from__uint64_t__std_vector_char",
)
Eur_EGrabber_CallbackOnDemand_gcWritePort__on__DeviceModule__from__uint64_t__std_vector_char = errorCheck(
    dll.euEGCOD_gcWritePortODeviceModuleFu64Svc,
    "Eur_EGrabber_CallbackOnDemand_gcWritePort__on__DeviceModule__from__uint64_t__std_vector_char",
)
Eur_EGrabber_CallbackOnDemand_gcWritePort__on__StreamModule__from__uint64_t__std_vector_char = errorCheck(
    dll.euEGCOD_gcWritePortOStreamModuleFu64Svc,
    "Eur_EGrabber_CallbackOnDemand_gcWritePort__on__StreamModule__from__uint64_t__std_vector_char",
)
Eur_EGrabber_CallbackOnDemand_gcWritePort__on__RemoteModule__from__uint64_t__std_vector_char = errorCheck(
    dll.euEGCOD_gcWritePortORemoteModuleFu64Svc,
    "Eur_EGrabber_CallbackOnDemand_gcWritePort__on__RemoteModule__from__uint64_t__std_vector_char",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__size_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAsOSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__size_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int8_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi8OSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int8_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int16_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi16OSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int16_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int32_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi32OSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int32_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int64_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi64OSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int64_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu8OSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint16_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu16OSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint16_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint32_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu32OSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint32_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint64_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu64OSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint64_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__double__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAdOSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__double__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__float__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAfOSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__float__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t_ptr__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu8pOSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t_ptr__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_string__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueASsOSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_string__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__void_ptr__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAvptrOSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__void_ptr__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_char__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueASvcOSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_char__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_std_string__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueASv_std_stringOSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_std_string__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__bool8_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAb8OSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__bool8_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__char_ptr__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAcptrOSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__char_ptr__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__InfoCommandInfo__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueA_CINFOOSystemModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__InfoCommandInfo__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__size_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAsOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__size_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int8_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi8OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int8_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int16_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi16OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int16_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int32_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi32OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int32_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int64_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi64OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int64_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu8OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint16_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu16OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint16_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint32_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu32OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint32_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint64_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu64OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint64_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__double__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAdOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__double__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__float__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAfOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__float__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t_ptr__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu8pOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t_ptr__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_string__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueASsOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_string__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__void_ptr__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAvptrOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__void_ptr__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_char__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueASvcOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_char__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_std_string__on__InterfaceModule__from__uint64_t = (
    errorCheck(
        dll.euEGCOD_gcReadPortValueASv_std_stringOInterfaceModuleFu64,
        "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_std_string__on__InterfaceModule__from__uint64_t",
    )
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__bool8_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAb8OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__bool8_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__char_ptr__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAcptrOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__char_ptr__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__InfoCommandInfo__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueA_CINFOOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__InfoCommandInfo__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__size_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAsODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__size_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int8_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi8ODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int8_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int16_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi16ODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int16_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int32_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi32ODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int32_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int64_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi64ODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int64_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu8ODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint16_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu16ODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint16_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint32_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu32ODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint32_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint64_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu64ODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint64_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__double__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAdODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__double__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__float__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAfODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__float__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t_ptr__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu8pODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t_ptr__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_string__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueASsODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_string__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__void_ptr__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAvptrODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__void_ptr__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_char__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueASvcODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_char__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_std_string__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueASv_std_stringODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_std_string__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__bool8_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAb8ODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__bool8_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__char_ptr__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAcptrODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__char_ptr__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__InfoCommandInfo__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueA_CINFOODeviceModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__InfoCommandInfo__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__size_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAsOStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__size_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int8_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi8OStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int8_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int16_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi16OStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int16_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int32_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi32OStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int32_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int64_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi64OStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int64_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu8OStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint16_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu16OStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint16_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint32_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu32OStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint32_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint64_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu64OStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint64_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__double__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAdOStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__double__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__float__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAfOStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__float__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t_ptr__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu8pOStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t_ptr__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_string__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueASsOStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_string__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__void_ptr__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAvptrOStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__void_ptr__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_char__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueASvcOStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_char__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_std_string__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueASv_std_stringOStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_std_string__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__bool8_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAb8OStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__bool8_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__char_ptr__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAcptrOStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__char_ptr__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__InfoCommandInfo__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueA_CINFOOStreamModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__InfoCommandInfo__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__size_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAsORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__size_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int8_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi8ORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int8_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int16_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi16ORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int16_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int32_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi32ORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int32_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int64_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAi64ORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__int64_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu8ORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint16_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu16ORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint16_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint32_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu32ORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint32_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint64_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu64ORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint64_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__double__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAdORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__double__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__float__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAfORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__float__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t_ptr__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAu8pORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__uint8_t_ptr__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_string__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueASsORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_string__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__void_ptr__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAvptrORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__void_ptr__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_char__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueASvcORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_char__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_std_string__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueASv_std_stringORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__std_vector_std_string__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__bool8_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAb8ORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__bool8_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__char_ptr__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueAcptrORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__char_ptr__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__InfoCommandInfo__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGCOD_gcReadPortValueA_CINFOORemoteModuleFu64,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortValue__as__InfoCommandInfo__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__size_t__on__SystemModule__from__uint64_t__size_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWsOSystemModuleFu64s,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__size_t__on__SystemModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int8_t__on__SystemModule__from__uint64_t__int8_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWi8OSystemModuleFu64i8,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int8_t__on__SystemModule__from__uint64_t__int8_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int16_t__on__SystemModule__from__uint64_t__int16_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWi16OSystemModuleFu64i16,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int16_t__on__SystemModule__from__uint64_t__int16_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int32_t__on__SystemModule__from__uint64_t__int32_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWi32OSystemModuleFu64i32,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int32_t__on__SystemModule__from__uint64_t__int32_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int64_t__on__SystemModule__from__uint64_t__int64_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWi64OSystemModuleFu64i64,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int64_t__on__SystemModule__from__uint64_t__int64_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint8_t__on__SystemModule__from__uint64_t__uint8_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWu8OSystemModuleFu64u8,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint8_t__on__SystemModule__from__uint64_t__uint8_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint16_t__on__SystemModule__from__uint64_t__uint16_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWu16OSystemModuleFu64u16,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint16_t__on__SystemModule__from__uint64_t__uint16_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint32_t__on__SystemModule__from__uint64_t__uint32_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWu32OSystemModuleFu64u32,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint32_t__on__SystemModule__from__uint64_t__uint32_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint64_t__on__SystemModule__from__uint64_t__uint64_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWu64OSystemModuleFu64u64,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint64_t__on__SystemModule__from__uint64_t__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__double__on__SystemModule__from__uint64_t__double = errorCheck(
    dll.euEGCOD_gcWritePortValueWdOSystemModuleFu64d,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__double__on__SystemModule__from__uint64_t__double",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__float__on__SystemModule__from__uint64_t__float = errorCheck(
    dll.euEGCOD_gcWritePortValueWfOSystemModuleFu64f,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__float__on__SystemModule__from__uint64_t__float",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__size_t__on__InterfaceModule__from__uint64_t__size_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWsOInterfaceModuleFu64s,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__size_t__on__InterfaceModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int8_t__on__InterfaceModule__from__uint64_t__int8_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWi8OInterfaceModuleFu64i8,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int8_t__on__InterfaceModule__from__uint64_t__int8_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int16_t__on__InterfaceModule__from__uint64_t__int16_t = (
    errorCheck(
        dll.euEGCOD_gcWritePortValueWi16OInterfaceModuleFu64i16,
        "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int16_t__on__InterfaceModule__from__uint64_t__int16_t",
    )
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int32_t__on__InterfaceModule__from__uint64_t__int32_t = (
    errorCheck(
        dll.euEGCOD_gcWritePortValueWi32OInterfaceModuleFu64i32,
        "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int32_t__on__InterfaceModule__from__uint64_t__int32_t",
    )
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int64_t__on__InterfaceModule__from__uint64_t__int64_t = (
    errorCheck(
        dll.euEGCOD_gcWritePortValueWi64OInterfaceModuleFu64i64,
        "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int64_t__on__InterfaceModule__from__uint64_t__int64_t",
    )
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint8_t__on__InterfaceModule__from__uint64_t__uint8_t = (
    errorCheck(
        dll.euEGCOD_gcWritePortValueWu8OInterfaceModuleFu64u8,
        "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint8_t__on__InterfaceModule__from__uint64_t__uint8_t",
    )
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint16_t__on__InterfaceModule__from__uint64_t__uint16_t = (
    errorCheck(
        dll.euEGCOD_gcWritePortValueWu16OInterfaceModuleFu64u16,
        "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint16_t__on__InterfaceModule__from__uint64_t__uint16_t",
    )
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint32_t__on__InterfaceModule__from__uint64_t__uint32_t = (
    errorCheck(
        dll.euEGCOD_gcWritePortValueWu32OInterfaceModuleFu64u32,
        "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint32_t__on__InterfaceModule__from__uint64_t__uint32_t",
    )
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint64_t__on__InterfaceModule__from__uint64_t__uint64_t = (
    errorCheck(
        dll.euEGCOD_gcWritePortValueWu64OInterfaceModuleFu64u64,
        "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint64_t__on__InterfaceModule__from__uint64_t__uint64_t",
    )
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__double__on__InterfaceModule__from__uint64_t__double = errorCheck(
    dll.euEGCOD_gcWritePortValueWdOInterfaceModuleFu64d,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__double__on__InterfaceModule__from__uint64_t__double",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__float__on__InterfaceModule__from__uint64_t__float = errorCheck(
    dll.euEGCOD_gcWritePortValueWfOInterfaceModuleFu64f,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__float__on__InterfaceModule__from__uint64_t__float",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__size_t__on__DeviceModule__from__uint64_t__size_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWsODeviceModuleFu64s,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__size_t__on__DeviceModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int8_t__on__DeviceModule__from__uint64_t__int8_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWi8ODeviceModuleFu64i8,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int8_t__on__DeviceModule__from__uint64_t__int8_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int16_t__on__DeviceModule__from__uint64_t__int16_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWi16ODeviceModuleFu64i16,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int16_t__on__DeviceModule__from__uint64_t__int16_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int32_t__on__DeviceModule__from__uint64_t__int32_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWi32ODeviceModuleFu64i32,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int32_t__on__DeviceModule__from__uint64_t__int32_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int64_t__on__DeviceModule__from__uint64_t__int64_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWi64ODeviceModuleFu64i64,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int64_t__on__DeviceModule__from__uint64_t__int64_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint8_t__on__DeviceModule__from__uint64_t__uint8_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWu8ODeviceModuleFu64u8,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint8_t__on__DeviceModule__from__uint64_t__uint8_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint16_t__on__DeviceModule__from__uint64_t__uint16_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWu16ODeviceModuleFu64u16,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint16_t__on__DeviceModule__from__uint64_t__uint16_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint32_t__on__DeviceModule__from__uint64_t__uint32_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWu32ODeviceModuleFu64u32,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint32_t__on__DeviceModule__from__uint64_t__uint32_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint64_t__on__DeviceModule__from__uint64_t__uint64_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWu64ODeviceModuleFu64u64,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint64_t__on__DeviceModule__from__uint64_t__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__double__on__DeviceModule__from__uint64_t__double = errorCheck(
    dll.euEGCOD_gcWritePortValueWdODeviceModuleFu64d,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__double__on__DeviceModule__from__uint64_t__double",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__float__on__DeviceModule__from__uint64_t__float = errorCheck(
    dll.euEGCOD_gcWritePortValueWfODeviceModuleFu64f,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__float__on__DeviceModule__from__uint64_t__float",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__size_t__on__StreamModule__from__uint64_t__size_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWsOStreamModuleFu64s,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__size_t__on__StreamModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int8_t__on__StreamModule__from__uint64_t__int8_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWi8OStreamModuleFu64i8,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int8_t__on__StreamModule__from__uint64_t__int8_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int16_t__on__StreamModule__from__uint64_t__int16_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWi16OStreamModuleFu64i16,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int16_t__on__StreamModule__from__uint64_t__int16_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int32_t__on__StreamModule__from__uint64_t__int32_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWi32OStreamModuleFu64i32,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int32_t__on__StreamModule__from__uint64_t__int32_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int64_t__on__StreamModule__from__uint64_t__int64_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWi64OStreamModuleFu64i64,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int64_t__on__StreamModule__from__uint64_t__int64_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint8_t__on__StreamModule__from__uint64_t__uint8_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWu8OStreamModuleFu64u8,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint8_t__on__StreamModule__from__uint64_t__uint8_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint16_t__on__StreamModule__from__uint64_t__uint16_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWu16OStreamModuleFu64u16,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint16_t__on__StreamModule__from__uint64_t__uint16_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint32_t__on__StreamModule__from__uint64_t__uint32_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWu32OStreamModuleFu64u32,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint32_t__on__StreamModule__from__uint64_t__uint32_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint64_t__on__StreamModule__from__uint64_t__uint64_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWu64OStreamModuleFu64u64,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint64_t__on__StreamModule__from__uint64_t__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__double__on__StreamModule__from__uint64_t__double = errorCheck(
    dll.euEGCOD_gcWritePortValueWdOStreamModuleFu64d,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__double__on__StreamModule__from__uint64_t__double",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__float__on__StreamModule__from__uint64_t__float = errorCheck(
    dll.euEGCOD_gcWritePortValueWfOStreamModuleFu64f,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__float__on__StreamModule__from__uint64_t__float",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__size_t__on__RemoteModule__from__uint64_t__size_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWsORemoteModuleFu64s,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__size_t__on__RemoteModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int8_t__on__RemoteModule__from__uint64_t__int8_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWi8ORemoteModuleFu64i8,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int8_t__on__RemoteModule__from__uint64_t__int8_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int16_t__on__RemoteModule__from__uint64_t__int16_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWi16ORemoteModuleFu64i16,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int16_t__on__RemoteModule__from__uint64_t__int16_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int32_t__on__RemoteModule__from__uint64_t__int32_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWi32ORemoteModuleFu64i32,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int32_t__on__RemoteModule__from__uint64_t__int32_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int64_t__on__RemoteModule__from__uint64_t__int64_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWi64ORemoteModuleFu64i64,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__int64_t__on__RemoteModule__from__uint64_t__int64_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint8_t__on__RemoteModule__from__uint64_t__uint8_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWu8ORemoteModuleFu64u8,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint8_t__on__RemoteModule__from__uint64_t__uint8_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint16_t__on__RemoteModule__from__uint64_t__uint16_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWu16ORemoteModuleFu64u16,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint16_t__on__RemoteModule__from__uint64_t__uint16_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint32_t__on__RemoteModule__from__uint64_t__uint32_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWu32ORemoteModuleFu64u32,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint32_t__on__RemoteModule__from__uint64_t__uint32_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint64_t__on__RemoteModule__from__uint64_t__uint64_t = errorCheck(
    dll.euEGCOD_gcWritePortValueWu64ORemoteModuleFu64u64,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__uint64_t__on__RemoteModule__from__uint64_t__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__double__on__RemoteModule__from__uint64_t__double = errorCheck(
    dll.euEGCOD_gcWritePortValueWdORemoteModuleFu64d,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__double__on__RemoteModule__from__uint64_t__double",
)
Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__float__on__RemoteModule__from__uint64_t__float = errorCheck(
    dll.euEGCOD_gcWritePortValueWfORemoteModuleFu64f,
    "Eur_EGrabber_CallbackOnDemand_gcWritePortValue__with__float__on__RemoteModule__from__uint64_t__float",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortString__on__SystemModule__from__uint64_t__size_t = errorCheck(
    dll.euEGCOD_gcReadPortStringOSystemModuleFu64s,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortString__on__SystemModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortString__on__InterfaceModule__from__uint64_t__size_t = errorCheck(
    dll.euEGCOD_gcReadPortStringOInterfaceModuleFu64s,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortString__on__InterfaceModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortString__on__DeviceModule__from__uint64_t__size_t = errorCheck(
    dll.euEGCOD_gcReadPortStringODeviceModuleFu64s,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortString__on__DeviceModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortString__on__StreamModule__from__uint64_t__size_t = errorCheck(
    dll.euEGCOD_gcReadPortStringOStreamModuleFu64s,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortString__on__StreamModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackOnDemand_gcReadPortString__on__RemoteModule__from__uint64_t__size_t = errorCheck(
    dll.euEGCOD_gcReadPortStringORemoteModuleFu64s,
    "Eur_EGrabber_CallbackOnDemand_gcReadPortString__on__RemoteModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackOnDemand_getInteger__on__SystemModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getIntegerOSystemModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getInteger__on__SystemModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getInteger__on__InterfaceModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getIntegerOInterfaceModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getInteger__on__InterfaceModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getInteger__on__DeviceModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getIntegerODeviceModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getInteger__on__DeviceModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getInteger__on__StreamModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getIntegerOStreamModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getInteger__on__StreamModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getInteger__on__RemoteModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getIntegerORemoteModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getInteger__on__RemoteModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getFloat__on__SystemModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getFloatOSystemModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getFloat__on__SystemModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getFloat__on__InterfaceModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getFloatOInterfaceModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getFloat__on__InterfaceModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getFloat__on__DeviceModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getFloatODeviceModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getFloat__on__DeviceModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getFloat__on__StreamModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getFloatOStreamModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getFloat__on__StreamModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getFloat__on__RemoteModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getFloatORemoteModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getFloat__on__RemoteModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getString__on__SystemModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getStringOSystemModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getString__on__SystemModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getString__on__InterfaceModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getStringOInterfaceModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getString__on__InterfaceModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getString__on__DeviceModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getStringODeviceModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getString__on__DeviceModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getString__on__StreamModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getStringOStreamModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getString__on__StreamModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getString__on__RemoteModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getStringORemoteModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getString__on__RemoteModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getStringData__on__SystemModule__from__const_char_p__std_vector_char = errorCheck(
    dll.euEGCOD_getStringDataOSystemModuleFccpSvc,
    "Eur_EGrabber_CallbackOnDemand_getStringData__on__SystemModule__from__const_char_p__std_vector_char",
)
Eur_EGrabber_CallbackOnDemand_getStringData__on__InterfaceModule__from__const_char_p__std_vector_char = errorCheck(
    dll.euEGCOD_getStringDataOInterfaceModuleFccpSvc,
    "Eur_EGrabber_CallbackOnDemand_getStringData__on__InterfaceModule__from__const_char_p__std_vector_char",
)
Eur_EGrabber_CallbackOnDemand_getStringData__on__DeviceModule__from__const_char_p__std_vector_char = errorCheck(
    dll.euEGCOD_getStringDataODeviceModuleFccpSvc,
    "Eur_EGrabber_CallbackOnDemand_getStringData__on__DeviceModule__from__const_char_p__std_vector_char",
)
Eur_EGrabber_CallbackOnDemand_getStringData__on__StreamModule__from__const_char_p__std_vector_char = errorCheck(
    dll.euEGCOD_getStringDataOStreamModuleFccpSvc,
    "Eur_EGrabber_CallbackOnDemand_getStringData__on__StreamModule__from__const_char_p__std_vector_char",
)
Eur_EGrabber_CallbackOnDemand_getStringData__on__RemoteModule__from__const_char_p__std_vector_char = errorCheck(
    dll.euEGCOD_getStringDataORemoteModuleFccpSvc,
    "Eur_EGrabber_CallbackOnDemand_getStringData__on__RemoteModule__from__const_char_p__std_vector_char",
)
Eur_EGrabber_CallbackOnDemand_getStringList__on__SystemModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getStringListOSystemModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getStringList__on__SystemModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getStringList__on__InterfaceModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getStringListOInterfaceModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getStringList__on__InterfaceModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getStringList__on__DeviceModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getStringListODeviceModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getStringList__on__DeviceModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getStringList__on__StreamModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getStringListOStreamModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getStringList__on__StreamModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getStringList__on__RemoteModule__from__const_char_p = errorCheck(
    dll.euEGCOD_getStringListORemoteModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_getStringList__on__RemoteModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_getRegister__on__SystemModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGCOD_getRegisterOSystemModuleFccpvps,
    "Eur_EGrabber_CallbackOnDemand_getRegister__on__SystemModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_getRegister__on__InterfaceModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGCOD_getRegisterOInterfaceModuleFccpvps,
    "Eur_EGrabber_CallbackOnDemand_getRegister__on__InterfaceModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_getRegister__on__DeviceModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGCOD_getRegisterODeviceModuleFccpvps,
    "Eur_EGrabber_CallbackOnDemand_getRegister__on__DeviceModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_getRegister__on__StreamModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGCOD_getRegisterOStreamModuleFccpvps,
    "Eur_EGrabber_CallbackOnDemand_getRegister__on__StreamModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_getRegister__on__RemoteModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGCOD_getRegisterORemoteModuleFccpvps,
    "Eur_EGrabber_CallbackOnDemand_getRegister__on__RemoteModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_setInteger__on__SystemModule__from__const_char_p__int64_t = errorCheck(
    dll.euEGCOD_setIntegerOSystemModuleFccpi64,
    "Eur_EGrabber_CallbackOnDemand_setInteger__on__SystemModule__from__const_char_p__int64_t",
)
Eur_EGrabber_CallbackOnDemand_setInteger__on__InterfaceModule__from__const_char_p__int64_t = errorCheck(
    dll.euEGCOD_setIntegerOInterfaceModuleFccpi64,
    "Eur_EGrabber_CallbackOnDemand_setInteger__on__InterfaceModule__from__const_char_p__int64_t",
)
Eur_EGrabber_CallbackOnDemand_setInteger__on__DeviceModule__from__const_char_p__int64_t = errorCheck(
    dll.euEGCOD_setIntegerODeviceModuleFccpi64,
    "Eur_EGrabber_CallbackOnDemand_setInteger__on__DeviceModule__from__const_char_p__int64_t",
)
Eur_EGrabber_CallbackOnDemand_setInteger__on__StreamModule__from__const_char_p__int64_t = errorCheck(
    dll.euEGCOD_setIntegerOStreamModuleFccpi64,
    "Eur_EGrabber_CallbackOnDemand_setInteger__on__StreamModule__from__const_char_p__int64_t",
)
Eur_EGrabber_CallbackOnDemand_setInteger__on__RemoteModule__from__const_char_p__int64_t = errorCheck(
    dll.euEGCOD_setIntegerORemoteModuleFccpi64,
    "Eur_EGrabber_CallbackOnDemand_setInteger__on__RemoteModule__from__const_char_p__int64_t",
)
Eur_EGrabber_CallbackOnDemand_setFloat__on__SystemModule__from__const_char_p__double = errorCheck(
    dll.euEGCOD_setFloatOSystemModuleFccpd,
    "Eur_EGrabber_CallbackOnDemand_setFloat__on__SystemModule__from__const_char_p__double",
)
Eur_EGrabber_CallbackOnDemand_setFloat__on__InterfaceModule__from__const_char_p__double = errorCheck(
    dll.euEGCOD_setFloatOInterfaceModuleFccpd,
    "Eur_EGrabber_CallbackOnDemand_setFloat__on__InterfaceModule__from__const_char_p__double",
)
Eur_EGrabber_CallbackOnDemand_setFloat__on__DeviceModule__from__const_char_p__double = errorCheck(
    dll.euEGCOD_setFloatODeviceModuleFccpd,
    "Eur_EGrabber_CallbackOnDemand_setFloat__on__DeviceModule__from__const_char_p__double",
)
Eur_EGrabber_CallbackOnDemand_setFloat__on__StreamModule__from__const_char_p__double = errorCheck(
    dll.euEGCOD_setFloatOStreamModuleFccpd,
    "Eur_EGrabber_CallbackOnDemand_setFloat__on__StreamModule__from__const_char_p__double",
)
Eur_EGrabber_CallbackOnDemand_setFloat__on__RemoteModule__from__const_char_p__double = errorCheck(
    dll.euEGCOD_setFloatORemoteModuleFccpd,
    "Eur_EGrabber_CallbackOnDemand_setFloat__on__RemoteModule__from__const_char_p__double",
)
Eur_EGrabber_CallbackOnDemand_setString__on__SystemModule__from__const_char_p__const_char_p = errorCheck(
    dll.euEGCOD_setStringOSystemModuleFccpccp,
    "Eur_EGrabber_CallbackOnDemand_setString__on__SystemModule__from__const_char_p__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_setString__on__InterfaceModule__from__const_char_p__const_char_p = errorCheck(
    dll.euEGCOD_setStringOInterfaceModuleFccpccp,
    "Eur_EGrabber_CallbackOnDemand_setString__on__InterfaceModule__from__const_char_p__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_setString__on__DeviceModule__from__const_char_p__const_char_p = errorCheck(
    dll.euEGCOD_setStringODeviceModuleFccpccp,
    "Eur_EGrabber_CallbackOnDemand_setString__on__DeviceModule__from__const_char_p__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_setString__on__StreamModule__from__const_char_p__const_char_p = errorCheck(
    dll.euEGCOD_setStringOStreamModuleFccpccp,
    "Eur_EGrabber_CallbackOnDemand_setString__on__StreamModule__from__const_char_p__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_setString__on__RemoteModule__from__const_char_p__const_char_p = errorCheck(
    dll.euEGCOD_setStringORemoteModuleFccpccp,
    "Eur_EGrabber_CallbackOnDemand_setString__on__RemoteModule__from__const_char_p__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_setRegister__on__SystemModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGCOD_setRegisterOSystemModuleFccpvps,
    "Eur_EGrabber_CallbackOnDemand_setRegister__on__SystemModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_setRegister__on__InterfaceModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGCOD_setRegisterOInterfaceModuleFccpvps,
    "Eur_EGrabber_CallbackOnDemand_setRegister__on__InterfaceModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_setRegister__on__DeviceModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGCOD_setRegisterODeviceModuleFccpvps,
    "Eur_EGrabber_CallbackOnDemand_setRegister__on__DeviceModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_setRegister__on__StreamModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGCOD_setRegisterOStreamModuleFccpvps,
    "Eur_EGrabber_CallbackOnDemand_setRegister__on__StreamModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_setRegister__on__RemoteModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGCOD_setRegisterORemoteModuleFccpvps,
    "Eur_EGrabber_CallbackOnDemand_setRegister__on__RemoteModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_execute__on__SystemModule__from__const_char_p = errorCheck(
    dll.euEGCOD_executeOSystemModuleFccp, "Eur_EGrabber_CallbackOnDemand_execute__on__SystemModule__from__const_char_p"
)
Eur_EGrabber_CallbackOnDemand_execute__on__InterfaceModule__from__const_char_p = errorCheck(
    dll.euEGCOD_executeOInterfaceModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_execute__on__InterfaceModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_execute__on__DeviceModule__from__const_char_p = errorCheck(
    dll.euEGCOD_executeODeviceModuleFccp, "Eur_EGrabber_CallbackOnDemand_execute__on__DeviceModule__from__const_char_p"
)
Eur_EGrabber_CallbackOnDemand_execute__on__StreamModule__from__const_char_p = errorCheck(
    dll.euEGCOD_executeOStreamModuleFccp, "Eur_EGrabber_CallbackOnDemand_execute__on__StreamModule__from__const_char_p"
)
Eur_EGrabber_CallbackOnDemand_execute__on__RemoteModule__from__const_char_p = errorCheck(
    dll.euEGCOD_executeORemoteModuleFccp, "Eur_EGrabber_CallbackOnDemand_execute__on__RemoteModule__from__const_char_p"
)
Eur_EGrabber_CallbackOnDemand_attachEvent__on__SystemModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGCOD_attachEventOSystemModuleFu64vps,
    "Eur_EGrabber_CallbackOnDemand_attachEvent__on__SystemModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_attachEvent__on__InterfaceModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGCOD_attachEventOInterfaceModuleFu64vps,
    "Eur_EGrabber_CallbackOnDemand_attachEvent__on__InterfaceModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_attachEvent__on__DeviceModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGCOD_attachEventODeviceModuleFu64vps,
    "Eur_EGrabber_CallbackOnDemand_attachEvent__on__DeviceModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_attachEvent__on__StreamModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGCOD_attachEventOStreamModuleFu64vps,
    "Eur_EGrabber_CallbackOnDemand_attachEvent__on__StreamModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_attachEvent__on__RemoteModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGCOD_attachEventORemoteModuleFu64vps,
    "Eur_EGrabber_CallbackOnDemand_attachEvent__on__RemoteModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_invalidate__on__SystemModule__from__const_char_p = errorCheck(
    dll.euEGCOD_invalidateOSystemModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_invalidate__on__SystemModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_invalidate__on__InterfaceModule__from__const_char_p = errorCheck(
    dll.euEGCOD_invalidateOInterfaceModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_invalidate__on__InterfaceModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_invalidate__on__DeviceModule__from__const_char_p = errorCheck(
    dll.euEGCOD_invalidateODeviceModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_invalidate__on__DeviceModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_invalidate__on__StreamModule__from__const_char_p = errorCheck(
    dll.euEGCOD_invalidateOStreamModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_invalidate__on__StreamModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_invalidate__on__RemoteModule__from__const_char_p = errorCheck(
    dll.euEGCOD_invalidateORemoteModuleFccp,
    "Eur_EGrabber_CallbackOnDemand_invalidate__on__RemoteModule__from__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_runScript__from__const_char_p__void_p = errorCheck(
    dll.euEGCOD_runScriptFccpvp, "Eur_EGrabber_CallbackOnDemand_runScript__from__const_char_p__void_p"
)
Eur_EGrabber_CallbackOnDemand_runScript__from__const_char_p = errorCheck(
    dll.euEGCOD_runScriptFccp, "Eur_EGrabber_CallbackOnDemand_runScript__from__const_char_p"
)
Eur_EGrabber_CallbackOnDemand_interruptScript__from__const_char_p = errorCheck(
    dll.euEGCOD_interruptScriptFccp, "Eur_EGrabber_CallbackOnDemand_interruptScript__from__const_char_p"
)
Eur_EGrabber_CallbackOnDemand_onScriptUiCallback__from__const_char_p__void_p__std_map_std_string_std_string__std_string = errorCheck(
    dll.euEGCOD_onScriptUiCallbackFccpvpSm_std_string_std_stringSs,
    "Eur_EGrabber_CallbackOnDemand_onScriptUiCallback__from__const_char_p__void_p__std_map_std_string_std_string__std_string",
)
Eur_EGrabber_CallbackOnDemand_memento__from__const_char_p = errorCheck(
    dll.euEGCOD_mementoFccp, "Eur_EGrabber_CallbackOnDemand_memento__from__const_char_p"
)
Eur_EGrabber_CallbackOnDemand_memento__from__unsigned_char__unsigned_char__const_char_p = errorCheck(
    dll.euEGCOD_mementoFucucccp,
    "Eur_EGrabber_CallbackOnDemand_memento__from__unsigned_char__unsigned_char__const_char_p",
)
Eur_EGrabber_CallbackOnDemand_mementoWaveUp__from__unsigned_char__unsigned_char = errorCheck(
    dll.euEGCOD_mementoWaveUpFucuc, "Eur_EGrabber_CallbackOnDemand_mementoWaveUp__from__unsigned_char__unsigned_char"
)
Eur_EGrabber_CallbackOnDemand_mementoWaveDown__from__unsigned_char__unsigned_char = errorCheck(
    dll.euEGCOD_mementoWaveDownFucuc,
    "Eur_EGrabber_CallbackOnDemand_mementoWaveDown__from__unsigned_char__unsigned_char",
)
Eur_EGrabber_CallbackOnDemand_mementoWaveReset__from__unsigned_char__unsigned_char = errorCheck(
    dll.euEGCOD_mementoWaveResetFucuc,
    "Eur_EGrabber_CallbackOnDemand_mementoWaveReset__from__unsigned_char__unsigned_char",
)
Eur_EGrabber_CallbackOnDemand_mementoWaveValue__from__unsigned_char__unsigned_char__uint64_t = errorCheck(
    dll.euEGCOD_mementoWaveValueFucucu64,
    "Eur_EGrabber_CallbackOnDemand_mementoWaveValue__from__unsigned_char__unsigned_char__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_mementoWaveNoValue__from__unsigned_char__unsigned_char = errorCheck(
    dll.euEGCOD_mementoWaveNoValueFucuc,
    "Eur_EGrabber_CallbackOnDemand_mementoWaveNoValue__from__unsigned_char__unsigned_char",
)
Eur_EGrabber_CallbackOnDemand_enableEvent__with__NewBufferData = errorCheck(
    dll.euEGCOD_enableEventWNewBufferData, "Eur_EGrabber_CallbackOnDemand_enableEvent__with__NewBufferData"
)
Eur_EGrabber_CallbackOnDemand_enableEvent__with__IoToolboxData = errorCheck(
    dll.euEGCOD_enableEventWIoToolboxData, "Eur_EGrabber_CallbackOnDemand_enableEvent__with__IoToolboxData"
)
Eur_EGrabber_CallbackOnDemand_enableEvent__with__CicData = errorCheck(
    dll.euEGCOD_enableEventWCicData, "Eur_EGrabber_CallbackOnDemand_enableEvent__with__CicData"
)
Eur_EGrabber_CallbackOnDemand_enableEvent__with__DataStreamData = errorCheck(
    dll.euEGCOD_enableEventWDataStreamData, "Eur_EGrabber_CallbackOnDemand_enableEvent__with__DataStreamData"
)
Eur_EGrabber_CallbackOnDemand_enableEvent__with__CxpInterfaceData = errorCheck(
    dll.euEGCOD_enableEventWCxpInterfaceData, "Eur_EGrabber_CallbackOnDemand_enableEvent__with__CxpInterfaceData"
)
Eur_EGrabber_CallbackOnDemand_enableEvent__with__DeviceErrorData = errorCheck(
    dll.euEGCOD_enableEventWDeviceErrorData, "Eur_EGrabber_CallbackOnDemand_enableEvent__with__DeviceErrorData"
)
Eur_EGrabber_CallbackOnDemand_enableEvent__with__CxpDeviceData = errorCheck(
    dll.euEGCOD_enableEventWCxpDeviceData, "Eur_EGrabber_CallbackOnDemand_enableEvent__with__CxpDeviceData"
)
Eur_EGrabber_CallbackOnDemand_enableEvent__with__RemoteDeviceData = errorCheck(
    dll.euEGCOD_enableEventWRemoteDeviceData, "Eur_EGrabber_CallbackOnDemand_enableEvent__with__RemoteDeviceData"
)
Eur_EGrabber_CallbackOnDemand_enableEvent__with__All = errorCheck(
    dll.euEGCOD_enableEventWAll, "Eur_EGrabber_CallbackOnDemand_enableEvent__with__All"
)
Eur_EGrabber_CallbackOnDemand_disableEvent__with__NewBufferData = errorCheck(
    dll.euEGCOD_disableEventWNewBufferData, "Eur_EGrabber_CallbackOnDemand_disableEvent__with__NewBufferData"
)
Eur_EGrabber_CallbackOnDemand_disableEvent__with__IoToolboxData = errorCheck(
    dll.euEGCOD_disableEventWIoToolboxData, "Eur_EGrabber_CallbackOnDemand_disableEvent__with__IoToolboxData"
)
Eur_EGrabber_CallbackOnDemand_disableEvent__with__CicData = errorCheck(
    dll.euEGCOD_disableEventWCicData, "Eur_EGrabber_CallbackOnDemand_disableEvent__with__CicData"
)
Eur_EGrabber_CallbackOnDemand_disableEvent__with__DataStreamData = errorCheck(
    dll.euEGCOD_disableEventWDataStreamData, "Eur_EGrabber_CallbackOnDemand_disableEvent__with__DataStreamData"
)
Eur_EGrabber_CallbackOnDemand_disableEvent__with__CxpInterfaceData = errorCheck(
    dll.euEGCOD_disableEventWCxpInterfaceData, "Eur_EGrabber_CallbackOnDemand_disableEvent__with__CxpInterfaceData"
)
Eur_EGrabber_CallbackOnDemand_disableEvent__with__DeviceErrorData = errorCheck(
    dll.euEGCOD_disableEventWDeviceErrorData, "Eur_EGrabber_CallbackOnDemand_disableEvent__with__DeviceErrorData"
)
Eur_EGrabber_CallbackOnDemand_disableEvent__with__CxpDeviceData = errorCheck(
    dll.euEGCOD_disableEventWCxpDeviceData, "Eur_EGrabber_CallbackOnDemand_disableEvent__with__CxpDeviceData"
)
Eur_EGrabber_CallbackOnDemand_disableEvent__with__RemoteDeviceData = errorCheck(
    dll.euEGCOD_disableEventWRemoteDeviceData, "Eur_EGrabber_CallbackOnDemand_disableEvent__with__RemoteDeviceData"
)
Eur_EGrabber_CallbackOnDemand_disableEvent__with__All = errorCheck(
    dll.euEGCOD_disableEventWAll, "Eur_EGrabber_CallbackOnDemand_disableEvent__with__All"
)
Eur_EGrabber_CallbackOnDemand_flushEvent__with__NewBufferData = errorCheck(
    dll.euEGCOD_flushEventWNewBufferData, "Eur_EGrabber_CallbackOnDemand_flushEvent__with__NewBufferData"
)
Eur_EGrabber_CallbackOnDemand_flushEvent__with__IoToolboxData = errorCheck(
    dll.euEGCOD_flushEventWIoToolboxData, "Eur_EGrabber_CallbackOnDemand_flushEvent__with__IoToolboxData"
)
Eur_EGrabber_CallbackOnDemand_flushEvent__with__CicData = errorCheck(
    dll.euEGCOD_flushEventWCicData, "Eur_EGrabber_CallbackOnDemand_flushEvent__with__CicData"
)
Eur_EGrabber_CallbackOnDemand_flushEvent__with__DataStreamData = errorCheck(
    dll.euEGCOD_flushEventWDataStreamData, "Eur_EGrabber_CallbackOnDemand_flushEvent__with__DataStreamData"
)
Eur_EGrabber_CallbackOnDemand_flushEvent__with__CxpInterfaceData = errorCheck(
    dll.euEGCOD_flushEventWCxpInterfaceData, "Eur_EGrabber_CallbackOnDemand_flushEvent__with__CxpInterfaceData"
)
Eur_EGrabber_CallbackOnDemand_flushEvent__with__DeviceErrorData = errorCheck(
    dll.euEGCOD_flushEventWDeviceErrorData, "Eur_EGrabber_CallbackOnDemand_flushEvent__with__DeviceErrorData"
)
Eur_EGrabber_CallbackOnDemand_flushEvent__with__CxpDeviceData = errorCheck(
    dll.euEGCOD_flushEventWCxpDeviceData, "Eur_EGrabber_CallbackOnDemand_flushEvent__with__CxpDeviceData"
)
Eur_EGrabber_CallbackOnDemand_flushEvent__with__RemoteDeviceData = errorCheck(
    dll.euEGCOD_flushEventWRemoteDeviceData, "Eur_EGrabber_CallbackOnDemand_flushEvent__with__RemoteDeviceData"
)
Eur_EGrabber_CallbackOnDemand_flushEvent__with__All = errorCheck(
    dll.euEGCOD_flushEventWAll, "Eur_EGrabber_CallbackOnDemand_flushEvent__with__All"
)
Eur_EGrabber_CallbackOnDemand_pop__from__uint64_t = errorCheck(
    dll.euEGCOD_popFu64, "Eur_EGrabber_CallbackOnDemand_pop__from__uint64_t"
)
Eur_EGrabber_CallbackOnDemand_pop = errorCheck(dll.euEGCOD_pop, "Eur_EGrabber_CallbackOnDemand_pop")
Eur_EGrabber_CallbackOnDemand_cancelPop = errorCheck(dll.euEGCOD_cancelPop, "Eur_EGrabber_CallbackOnDemand_cancelPop")
Eur_EGrabber_CallbackOnDemand_processEvent__with__NewBufferData__from__uint64_t = errorCheck(
    dll.euEGCOD_processEventWNewBufferDataFu64,
    "Eur_EGrabber_CallbackOnDemand_processEvent__with__NewBufferData__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_processEvent__with__IoToolboxData__from__uint64_t = errorCheck(
    dll.euEGCOD_processEventWIoToolboxDataFu64,
    "Eur_EGrabber_CallbackOnDemand_processEvent__with__IoToolboxData__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_processEvent__with__CicData__from__uint64_t = errorCheck(
    dll.euEGCOD_processEventWCicDataFu64, "Eur_EGrabber_CallbackOnDemand_processEvent__with__CicData__from__uint64_t"
)
Eur_EGrabber_CallbackOnDemand_processEvent__with__DataStreamData__from__uint64_t = errorCheck(
    dll.euEGCOD_processEventWDataStreamDataFu64,
    "Eur_EGrabber_CallbackOnDemand_processEvent__with__DataStreamData__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_processEvent__with__CxpInterfaceData__from__uint64_t = errorCheck(
    dll.euEGCOD_processEventWCxpInterfaceDataFu64,
    "Eur_EGrabber_CallbackOnDemand_processEvent__with__CxpInterfaceData__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_processEvent__with__DeviceErrorData__from__uint64_t = errorCheck(
    dll.euEGCOD_processEventWDeviceErrorDataFu64,
    "Eur_EGrabber_CallbackOnDemand_processEvent__with__DeviceErrorData__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_processEvent__with__CxpDeviceData__from__uint64_t = errorCheck(
    dll.euEGCOD_processEventWCxpDeviceDataFu64,
    "Eur_EGrabber_CallbackOnDemand_processEvent__with__CxpDeviceData__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_processEvent__with__RemoteDeviceData__from__uint64_t = errorCheck(
    dll.euEGCOD_processEventWRemoteDeviceDataFu64,
    "Eur_EGrabber_CallbackOnDemand_processEvent__with__RemoteDeviceData__from__uint64_t",
)
Eur_EGrabber_CallbackOnDemand_processEvent__with__Any__from__uint64_t = errorCheck(
    dll.euEGCOD_processEventWAnyFu64, "Eur_EGrabber_CallbackOnDemand_processEvent__with__Any__from__uint64_t"
)
Eur_EGrabber_CallbackOnDemand_processEvent__with__NewBufferData = errorCheck(
    dll.euEGCOD_processEventWNewBufferData, "Eur_EGrabber_CallbackOnDemand_processEvent__with__NewBufferData"
)
Eur_EGrabber_CallbackOnDemand_processEvent__with__IoToolboxData = errorCheck(
    dll.euEGCOD_processEventWIoToolboxData, "Eur_EGrabber_CallbackOnDemand_processEvent__with__IoToolboxData"
)
Eur_EGrabber_CallbackOnDemand_processEvent__with__CicData = errorCheck(
    dll.euEGCOD_processEventWCicData, "Eur_EGrabber_CallbackOnDemand_processEvent__with__CicData"
)
Eur_EGrabber_CallbackOnDemand_processEvent__with__DataStreamData = errorCheck(
    dll.euEGCOD_processEventWDataStreamData, "Eur_EGrabber_CallbackOnDemand_processEvent__with__DataStreamData"
)
Eur_EGrabber_CallbackOnDemand_processEvent__with__CxpInterfaceData = errorCheck(
    dll.euEGCOD_processEventWCxpInterfaceData, "Eur_EGrabber_CallbackOnDemand_processEvent__with__CxpInterfaceData"
)
Eur_EGrabber_CallbackOnDemand_processEvent__with__DeviceErrorData = errorCheck(
    dll.euEGCOD_processEventWDeviceErrorData, "Eur_EGrabber_CallbackOnDemand_processEvent__with__DeviceErrorData"
)
Eur_EGrabber_CallbackOnDemand_processEvent__with__CxpDeviceData = errorCheck(
    dll.euEGCOD_processEventWCxpDeviceData, "Eur_EGrabber_CallbackOnDemand_processEvent__with__CxpDeviceData"
)
Eur_EGrabber_CallbackOnDemand_processEvent__with__RemoteDeviceData = errorCheck(
    dll.euEGCOD_processEventWRemoteDeviceData, "Eur_EGrabber_CallbackOnDemand_processEvent__with__RemoteDeviceData"
)
Eur_EGrabber_CallbackOnDemand_processEvent__with__Any = errorCheck(
    dll.euEGCOD_processEventWAny, "Eur_EGrabber_CallbackOnDemand_processEvent__with__Any"
)
Eur_EGrabber_CallbackOnDemand_cancelEvent__with__NewBufferData = errorCheck(
    dll.euEGCOD_cancelEventWNewBufferData, "Eur_EGrabber_CallbackOnDemand_cancelEvent__with__NewBufferData"
)
Eur_EGrabber_CallbackOnDemand_cancelEvent__with__IoToolboxData = errorCheck(
    dll.euEGCOD_cancelEventWIoToolboxData, "Eur_EGrabber_CallbackOnDemand_cancelEvent__with__IoToolboxData"
)
Eur_EGrabber_CallbackOnDemand_cancelEvent__with__CicData = errorCheck(
    dll.euEGCOD_cancelEventWCicData, "Eur_EGrabber_CallbackOnDemand_cancelEvent__with__CicData"
)
Eur_EGrabber_CallbackOnDemand_cancelEvent__with__DataStreamData = errorCheck(
    dll.euEGCOD_cancelEventWDataStreamData, "Eur_EGrabber_CallbackOnDemand_cancelEvent__with__DataStreamData"
)
Eur_EGrabber_CallbackOnDemand_cancelEvent__with__CxpInterfaceData = errorCheck(
    dll.euEGCOD_cancelEventWCxpInterfaceData, "Eur_EGrabber_CallbackOnDemand_cancelEvent__with__CxpInterfaceData"
)
Eur_EGrabber_CallbackOnDemand_cancelEvent__with__DeviceErrorData = errorCheck(
    dll.euEGCOD_cancelEventWDeviceErrorData, "Eur_EGrabber_CallbackOnDemand_cancelEvent__with__DeviceErrorData"
)
Eur_EGrabber_CallbackOnDemand_cancelEvent__with__CxpDeviceData = errorCheck(
    dll.euEGCOD_cancelEventWCxpDeviceData, "Eur_EGrabber_CallbackOnDemand_cancelEvent__with__CxpDeviceData"
)
Eur_EGrabber_CallbackOnDemand_cancelEvent__with__RemoteDeviceData = errorCheck(
    dll.euEGCOD_cancelEventWRemoteDeviceData, "Eur_EGrabber_CallbackOnDemand_cancelEvent__with__RemoteDeviceData"
)
Eur_EGrabber_CallbackOnDemand_cancelEvent__with__Any = errorCheck(
    dll.euEGCOD_cancelEventWAny, "Eur_EGrabber_CallbackOnDemand_cancelEvent__with__Any"
)
Eur_EGrabber_CallbackOnDemand_getPendingEventCount__with__NewBufferData = errorCheck(
    dll.euEGCOD_getPendingEventCountWNewBufferData,
    "Eur_EGrabber_CallbackOnDemand_getPendingEventCount__with__NewBufferData",
)
Eur_EGrabber_CallbackOnDemand_getPendingEventCount__with__IoToolboxData = errorCheck(
    dll.euEGCOD_getPendingEventCountWIoToolboxData,
    "Eur_EGrabber_CallbackOnDemand_getPendingEventCount__with__IoToolboxData",
)
Eur_EGrabber_CallbackOnDemand_getPendingEventCount__with__CicData = errorCheck(
    dll.euEGCOD_getPendingEventCountWCicData, "Eur_EGrabber_CallbackOnDemand_getPendingEventCount__with__CicData"
)
Eur_EGrabber_CallbackOnDemand_getPendingEventCount__with__DataStreamData = errorCheck(
    dll.euEGCOD_getPendingEventCountWDataStreamData,
    "Eur_EGrabber_CallbackOnDemand_getPendingEventCount__with__DataStreamData",
)
Eur_EGrabber_CallbackOnDemand_getPendingEventCount__with__CxpInterfaceData = errorCheck(
    dll.euEGCOD_getPendingEventCountWCxpInterfaceData,
    "Eur_EGrabber_CallbackOnDemand_getPendingEventCount__with__CxpInterfaceData",
)
Eur_EGrabber_CallbackOnDemand_getPendingEventCount__with__DeviceErrorData = errorCheck(
    dll.euEGCOD_getPendingEventCountWDeviceErrorData,
    "Eur_EGrabber_CallbackOnDemand_getPendingEventCount__with__DeviceErrorData",
)
Eur_EGrabber_CallbackOnDemand_getPendingEventCount__with__CxpDeviceData = errorCheck(
    dll.euEGCOD_getPendingEventCountWCxpDeviceData,
    "Eur_EGrabber_CallbackOnDemand_getPendingEventCount__with__CxpDeviceData",
)
Eur_EGrabber_CallbackOnDemand_getPendingEventCount__with__RemoteDeviceData = errorCheck(
    dll.euEGCOD_getPendingEventCountWRemoteDeviceData,
    "Eur_EGrabber_CallbackOnDemand_getPendingEventCount__with__RemoteDeviceData",
)
Eur_EGrabber_CallbackOnDemand_getPendingEventCount__with__Any = errorCheck(
    dll.euEGCOD_getPendingEventCountWAny, "Eur_EGrabber_CallbackOnDemand_getPendingEventCount__with__Any"
)
Eur_EGrabber_CallbackOnDemand_onNewBufferEvent__from__Eur_NewBufferData = errorCheck(
    dll.euEGCOD_onNewBufferEventFEur_NewBufferData,
    "Eur_EGrabber_CallbackOnDemand_onNewBufferEvent__from__Eur_NewBufferData",
)
Eur_EGrabber_CallbackOnDemand_onIoToolboxEvent__from__Eur_IoToolboxData = errorCheck(
    dll.euEGCOD_onIoToolboxEventFEur_IoToolboxData,
    "Eur_EGrabber_CallbackOnDemand_onIoToolboxEvent__from__Eur_IoToolboxData",
)
Eur_EGrabber_CallbackOnDemand_onCicEvent__from__Eur_CicData = errorCheck(
    dll.euEGCOD_onCicEventFEur_CicData, "Eur_EGrabber_CallbackOnDemand_onCicEvent__from__Eur_CicData"
)
Eur_EGrabber_CallbackOnDemand_onDataStreamEvent__from__Eur_DataStreamData = errorCheck(
    dll.euEGCOD_onDataStreamEventFEur_DataStreamData,
    "Eur_EGrabber_CallbackOnDemand_onDataStreamEvent__from__Eur_DataStreamData",
)
Eur_EGrabber_CallbackOnDemand_onCxpInterfaceEvent__from__Eur_CxpInterfaceData = errorCheck(
    dll.euEGCOD_onCxpInterfaceEventFEur_CxpInterfaceData,
    "Eur_EGrabber_CallbackOnDemand_onCxpInterfaceEvent__from__Eur_CxpInterfaceData",
)
Eur_EGrabber_CallbackOnDemand_onDeviceErrorEvent__from__Eur_DeviceErrorData = errorCheck(
    dll.euEGCOD_onDeviceErrorEventFEur_DeviceErrorData,
    "Eur_EGrabber_CallbackOnDemand_onDeviceErrorEvent__from__Eur_DeviceErrorData",
)
Eur_EGrabber_CallbackOnDemand_onCxpDeviceEvent__from__Eur_CxpDeviceData = errorCheck(
    dll.euEGCOD_onCxpDeviceEventFEur_CxpDeviceData,
    "Eur_EGrabber_CallbackOnDemand_onCxpDeviceEvent__from__Eur_CxpDeviceData",
)
Eur_EGrabber_CallbackOnDemand_onRemoteDeviceEvent__from__Eur_RemoteDeviceData = errorCheck(
    dll.euEGCOD_onRemoteDeviceEventFEur_RemoteDeviceData,
    "Eur_EGrabber_CallbackOnDemand_onRemoteDeviceEvent__from__Eur_RemoteDeviceData",
)
Eur_EGrabber_CallbackOnDemand_getLastEventGrabberIndex = errorCheck(
    dll.euEGCOD_getLastEventGrabberIndex, "Eur_EGrabber_CallbackOnDemand_getLastEventGrabberIndex"
)
Eur_EGrabber_CallbackOnDemand_shutdown = errorCheck(dll.euEGCOD_shutdown, "Eur_EGrabber_CallbackOnDemand_shutdown")
Eur_EGrabber_CallbackOnDemand_push__from__Eur_NewBufferData = errorCheck(
    dll.euEGCOD_pushFEur_NewBufferData, "Eur_EGrabber_CallbackOnDemand_push__from__Eur_NewBufferData"
)
Eur_EGrabber_CallbackOnDemand_popEventFilter__from__size_t__uint64_t__Eur_OneOfAll__int_p = errorCheck(
    dll.euEGCOD_popEventFilterFsu64EurOOAi_p,
    "Eur_EGrabber_CallbackOnDemand_popEventFilter__from__size_t__uint64_t__Eur_OneOfAll__int_p",
)
Eur_EGrabber_CallbackOnDemand_processEventFilter__from__size_t__uint64_t = errorCheck(
    dll.euEGCOD_processEventFilterFsu64, "Eur_EGrabber_CallbackOnDemand_processEventFilter__from__size_t__uint64_t"
)
Eur_EGrabber_CallbackOnDemand_processEventFilter__from__size_t = errorCheck(
    dll.euEGCOD_processEventFilterFs, "Eur_EGrabber_CallbackOnDemand_processEventFilter__from__size_t"
)
Eur_EGrabber_CallbackOnDemand_cancelEventFilter__from__size_t = errorCheck(
    dll.euEGCOD_cancelEventFilterFs, "Eur_EGrabber_CallbackOnDemand_cancelEventFilter__from__size_t"
)
Eur_EGrabber_CallbackOnDemand_getPendingEventCountFilter__from__size_t = errorCheck(
    dll.euEGCOD_getPendingEventCountFilterFs, "Eur_EGrabber_CallbackOnDemand_getPendingEventCountFilter__from__size_t"
)
Eur_EGrabber_CallbackOnDemand_announceBusBuffer__from__uint64_t__size_t__void_p = errorCheck(
    dll.euEGCOD_announceBusBufferFu64svp,
    "Eur_EGrabber_CallbackOnDemand_announceBusBuffer__from__uint64_t__size_t__void_p",
)
Eur_EGrabber_CallbackOnDemand_announceBusBuffer__from__uint64_t__size_t = errorCheck(
    dll.euEGCOD_announceBusBufferFu64s, "Eur_EGrabber_CallbackOnDemand_announceBusBuffer__from__uint64_t__size_t"
)
Eur_EGrabber_CallbackOnDemand_announceNvidiaRdmaBuffer__from__void_p__size_t__void_p = errorCheck(
    dll.euEGCOD_announceNvidiaRdmaBufferFvpsvp,
    "Eur_EGrabber_CallbackOnDemand_announceNvidiaRdmaBuffer__from__void_p__size_t__void_p",
)
Eur_EGrabber_CallbackOnDemand_announceNvidiaRdmaBuffer__from__void_p__size_t = errorCheck(
    dll.euEGCOD_announceNvidiaRdmaBufferFvps,
    "Eur_EGrabber_CallbackOnDemand_announceNvidiaRdmaBuffer__from__void_p__size_t",
)
Eur_EGrabber_CallbackOnDemand_getSystemPort__from__int = errorCheck(
    dll.euEGCOD_getSystemPortFi, "Eur_EGrabber_CallbackOnDemand_getSystemPort__from__int"
)
Eur_EGrabber_CallbackOnDemand_getInterfacePort__from__int = errorCheck(
    dll.euEGCOD_getInterfacePortFi, "Eur_EGrabber_CallbackOnDemand_getInterfacePort__from__int"
)
Eur_EGrabber_CallbackOnDemand_getDevicePort__from__int = errorCheck(
    dll.euEGCOD_getDevicePortFi, "Eur_EGrabber_CallbackOnDemand_getDevicePort__from__int"
)
Eur_EGrabber_CallbackOnDemand_getStreamPort__from__int = errorCheck(
    dll.euEGCOD_getStreamPortFi, "Eur_EGrabber_CallbackOnDemand_getStreamPort__from__int"
)
Eur_EGrabber_CallbackOnDemand_getRemotePort__from__int = errorCheck(
    dll.euEGCOD_getRemotePortFi, "Eur_EGrabber_CallbackOnDemand_getRemotePort__from__int"
)
Eur_EGrabber_CallbackOnDemand_destroy = errorCheck(dll.euEGCOD_destroy, "Eur_EGrabber_CallbackOnDemand_destroy")
Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGenTL__int__int__int__DEVICE_ACCESS_FLAGS__bool8_t = errorCheck(
    dll.euEGST_createFEur_EGenTLiiiDAFb8,
    "Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGenTL__int__int__int__DEVICE_ACCESS_FLAGS__bool8_t",
)
Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGenTL__int__int__int__DEVICE_ACCESS_FLAGS = errorCheck(
    dll.euEGST_createFEur_EGenTLiiiDAF,
    "Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGenTL__int__int__int__DEVICE_ACCESS_FLAGS",
)
Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGenTL__int__int__int = errorCheck(
    dll.euEGST_createFEur_EGenTLiii, "Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGenTL__int__int__int"
)
Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGenTL__int__int = errorCheck(
    dll.euEGST_createFEur_EGenTLii, "Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGenTL__int__int"
)
Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGenTL__int = errorCheck(
    dll.euEGST_createFEur_EGenTLi, "Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGenTL__int"
)
Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGenTL = errorCheck(
    dll.euEGST_createFEur_EGenTL, "Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGenTL"
)
Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGrabberInfo__DEVICE_ACCESS_FLAGS__bool8_t = errorCheck(
    dll.euEGST_createFEurEGInfoDAFb8,
    "Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGrabberInfo__DEVICE_ACCESS_FLAGS__bool8_t",
)
Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGrabberInfo__DEVICE_ACCESS_FLAGS = errorCheck(
    dll.euEGST_createFEurEGInfoDAF,
    "Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGrabberInfo__DEVICE_ACCESS_FLAGS",
)
Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGrabberInfo = errorCheck(
    dll.euEGST_createFEurEGInfo, "Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGrabberInfo"
)
Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGrabberCameraInfo__DEVICE_ACCESS_FLAGS = errorCheck(
    dll.euEGST_createFEurEGCameraInfoDAF,
    "Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGrabberCameraInfo__DEVICE_ACCESS_FLAGS",
)
Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGrabberCameraInfo = errorCheck(
    dll.euEGST_createFEurEGCameraInfo, "Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGrabberCameraInfo"
)
Eur_EGrabber_CallbackSingleThread_reallocBuffers__from__size_t__size_t = errorCheck(
    dll.euEGST_reallocBuffersFss, "Eur_EGrabber_CallbackSingleThread_reallocBuffers__from__size_t__size_t"
)
Eur_EGrabber_CallbackSingleThread_reallocBuffers__from__size_t = errorCheck(
    dll.euEGST_reallocBuffersFs, "Eur_EGrabber_CallbackSingleThread_reallocBuffers__from__size_t"
)
Eur_EGrabber_CallbackSingleThread_announceAndQueue__from__Eur_GenTLMemory__size_t = errorCheck(
    dll.euEGST_announceAndQueueFEur_GenTLMemorys,
    "Eur_EGrabber_CallbackSingleThread_announceAndQueue__from__Eur_GenTLMemory__size_t",
)
Eur_EGrabber_CallbackSingleThread_announceAndQueue__from__Eur_GenTLMemory = errorCheck(
    dll.euEGST_announceAndQueueFEur_GenTLMemory,
    "Eur_EGrabber_CallbackSingleThread_announceAndQueue__from__Eur_GenTLMemory",
)
Eur_EGrabber_CallbackSingleThread_announceAndQueue__from__Eur_UserMemory = errorCheck(
    dll.euEGST_announceAndQueueFEur_UserMemory,
    "Eur_EGrabber_CallbackSingleThread_announceAndQueue__from__Eur_UserMemory",
)
Eur_EGrabber_CallbackSingleThread_announceAndQueue__from__Eur_UserMemoryArray = errorCheck(
    dll.euEGST_announceAndQueueFEur_UserMemoryArray,
    "Eur_EGrabber_CallbackSingleThread_announceAndQueue__from__Eur_UserMemoryArray",
)
Eur_EGrabber_CallbackSingleThread_announceAndQueue__from__Eur_UserMemoryArray__bool8_t = errorCheck(
    dll.euEGST_announceAndQueueFEur_UserMemoryArrayb8,
    "Eur_EGrabber_CallbackSingleThread_announceAndQueue__from__Eur_UserMemoryArray__bool8_t",
)
Eur_EGrabber_CallbackSingleThread_announceAndQueue__from__Eur_BusMemory = errorCheck(
    dll.euEGST_announceAndQueueFEur_BusMemory, "Eur_EGrabber_CallbackSingleThread_announceAndQueue__from__Eur_BusMemory"
)
Eur_EGrabber_CallbackSingleThread_announceAndQueue__from__Eur_NvidiaRdmaMemory = errorCheck(
    dll.euEGST_announceAndQueueFEur_NvidiaRdmaMemory,
    "Eur_EGrabber_CallbackSingleThread_announceAndQueue__from__Eur_NvidiaRdmaMemory",
)
Eur_EGrabber_CallbackSingleThread_flushBuffers__from__ACQ_QUEUE_TYPE = errorCheck(
    dll.euEGST_flushBuffersFAQT, "Eur_EGrabber_CallbackSingleThread_flushBuffers__from__ACQ_QUEUE_TYPE"
)
Eur_EGrabber_CallbackSingleThread_flushBuffers = errorCheck(
    dll.euEGST_flushBuffers, "Eur_EGrabber_CallbackSingleThread_flushBuffers"
)
Eur_EGrabber_CallbackSingleThread_resetBufferQueue = errorCheck(
    dll.euEGST_resetBufferQueue, "Eur_EGrabber_CallbackSingleThread_resetBufferQueue"
)
Eur_EGrabber_CallbackSingleThread_resetBufferQueue__from__Eur_BufferIndexRange = errorCheck(
    dll.euEGST_resetBufferQueueFEur_BufferIndexRange,
    "Eur_EGrabber_CallbackSingleThread_resetBufferQueue__from__Eur_BufferIndexRange",
)
Eur_EGrabber_CallbackSingleThread_queue__from__Eur_BufferIndexRange = errorCheck(
    dll.euEGST_queueFEur_BufferIndexRange, "Eur_EGrabber_CallbackSingleThread_queue__from__Eur_BufferIndexRange"
)
Eur_EGrabber_CallbackSingleThread_revoke__from__Eur_BufferIndexRange = errorCheck(
    dll.euEGST_revokeFEur_BufferIndexRange, "Eur_EGrabber_CallbackSingleThread_revoke__from__Eur_BufferIndexRange"
)
Eur_EGrabber_CallbackSingleThread_shouldReannounceBuffers = errorCheck(
    dll.euEGST_shouldReannounceBuffers, "Eur_EGrabber_CallbackSingleThread_shouldReannounceBuffers"
)
Eur_EGrabber_CallbackSingleThread_shouldReallocBuffers = errorCheck(
    dll.euEGST_shouldReallocBuffers, "Eur_EGrabber_CallbackSingleThread_shouldReallocBuffers"
)
Eur_EGrabber_CallbackSingleThread_start__from__uint64_t__bool8_t = errorCheck(
    dll.euEGST_startFu64b8, "Eur_EGrabber_CallbackSingleThread_start__from__uint64_t__bool8_t"
)
Eur_EGrabber_CallbackSingleThread_start__from__uint64_t = errorCheck(
    dll.euEGST_startFu64, "Eur_EGrabber_CallbackSingleThread_start__from__uint64_t"
)
Eur_EGrabber_CallbackSingleThread_start = errorCheck(dll.euEGST_start, "Eur_EGrabber_CallbackSingleThread_start")
Eur_EGrabber_CallbackSingleThread_stop = errorCheck(dll.euEGST_stop, "Eur_EGrabber_CallbackSingleThread_stop")
Eur_EGrabber_CallbackSingleThread_getWidth = errorCheck(
    dll.euEGST_getWidth, "Eur_EGrabber_CallbackSingleThread_getWidth"
)
Eur_EGrabber_CallbackSingleThread_getHeight = errorCheck(
    dll.euEGST_getHeight, "Eur_EGrabber_CallbackSingleThread_getHeight"
)
Eur_EGrabber_CallbackSingleThread_getPayloadSize = errorCheck(
    dll.euEGST_getPayloadSize, "Eur_EGrabber_CallbackSingleThread_getPayloadSize"
)
Eur_EGrabber_CallbackSingleThread_getPixelFormat = errorCheck(
    dll.euEGST_getPixelFormat, "Eur_EGrabber_CallbackSingleThread_getPixelFormat"
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__size_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAsOSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__size_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__int8_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAi8OSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__int8_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__int16_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAi16OSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__int16_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__int32_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAi32OSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__int32_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__int64_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAi64OSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__int64_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint8_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu8OSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint8_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint16_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu16OSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint16_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint32_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu32OSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint32_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint64_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu64OSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint64_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__double__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAdOSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__double__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__float__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAfOSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__float__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint8_t_ptr__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu8pOSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint8_t_ptr__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__std_string__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoASsOSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__std_string__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__void_ptr__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAvptrOSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__void_ptr__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__std_vector_char__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoASvcOSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__std_vector_char__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__std_vector_std_string__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoASv_std_stringOSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__std_vector_std_string__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__bool8_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAb8OSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__bool8_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__char_ptr__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAcptrOSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__char_ptr__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__InfoCommandInfo__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoA_CINFOOSystemModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__InfoCommandInfo__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__size_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAsOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__size_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__int8_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAi8OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__int8_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__int16_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAi16OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__int16_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__int32_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAi32OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__int32_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__int64_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAi64OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__int64_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint8_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu8OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint8_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint16_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu16OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint16_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint32_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu32OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint32_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint64_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu64OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint64_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__double__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAdOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__double__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__float__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAfOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__float__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint8_t_ptr__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu8pOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint8_t_ptr__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__std_string__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoASsOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__std_string__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__void_ptr__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAvptrOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__void_ptr__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__std_vector_char__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoASvcOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__std_vector_char__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__std_vector_std_string__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoASv_std_stringOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__std_vector_std_string__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__bool8_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAb8OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__bool8_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__char_ptr__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAcptrOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__char_ptr__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__InfoCommandInfo__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoA_CINFOOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__InfoCommandInfo__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__size_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAsODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__size_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__int8_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAi8ODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__int8_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__int16_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAi16ODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__int16_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__int32_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAi32ODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__int32_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__int64_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAi64ODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__int64_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint8_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu8ODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint8_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint16_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu16ODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint16_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint32_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu32ODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint32_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint64_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu64ODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint64_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__double__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAdODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__double__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__float__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAfODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__float__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint8_t_ptr__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu8pODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint8_t_ptr__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__std_string__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoASsODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__std_string__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__void_ptr__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAvptrODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__void_ptr__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__std_vector_char__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoASvcODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__std_vector_char__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__std_vector_std_string__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoASv_std_stringODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__std_vector_std_string__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__bool8_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAb8ODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__bool8_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__char_ptr__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAcptrODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__char_ptr__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__InfoCommandInfo__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoA_CINFOODeviceModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__InfoCommandInfo__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__size_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAsOStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__size_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__int8_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAi8OStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__int8_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__int16_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAi16OStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__int16_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__int32_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAi32OStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__int32_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__int64_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAi64OStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__int64_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint8_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu8OStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint8_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint16_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu16OStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint16_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint32_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu32OStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint32_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint64_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu64OStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint64_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__double__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAdOStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__double__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__float__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAfOStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__float__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__uint8_t_ptr__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAu8pOStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__uint8_t_ptr__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__std_string__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoASsOStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__std_string__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__void_ptr__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAvptrOStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__void_ptr__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__std_vector_char__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoASvcOStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__std_vector_char__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__std_vector_std_string__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoASv_std_stringOStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__std_vector_std_string__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__bool8_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAb8OStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__bool8_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__char_ptr__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoAcptrOStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__char_ptr__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getInfo__as__InfoCommandInfo__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGST_getInfoA_CINFOOStreamModuleFi32,
    "Eur_EGrabber_CallbackSingleThread_getInfo__as__InfoCommandInfo__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__size_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoAsFsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__size_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__int8_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoAi8FsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__int8_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__int16_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoAi16FsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__int16_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__int32_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoAi32FsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__int32_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__int64_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoAi64FsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__int64_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__uint8_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoAu8FsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__uint8_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__uint16_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoAu16FsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__uint16_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__uint32_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoAu32FsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__uint32_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__uint64_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoAu64FsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__uint64_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__double__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoAdFsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__double__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__float__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoAfFsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__float__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__uint8_t_ptr__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoAu8pFsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__uint8_t_ptr__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__std_string__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoASsFsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__std_string__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__void_ptr__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoAvptrFsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__void_ptr__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__std_vector_char__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoASvcFsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__std_vector_char__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__std_vector_std_string__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoASv_std_stringFsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__std_vector_std_string__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__bool8_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoAb8FsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__bool8_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__char_ptr__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoAcptrFsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__char_ptr__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__InfoCommandInfo__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGST_getBufferInfoA_CINFOFsBIC,
    "Eur_EGrabber_CallbackSingleThread_getBufferInfo__as__InfoCommandInfo__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackSingleThread_getBufferData__from__size_t = errorCheck(
    dll.euEGST_getBufferDataFs, "Eur_EGrabber_CallbackSingleThread_getBufferData__from__size_t"
)
Eur_EGrabber_CallbackSingleThread_isOpen__on__SystemModule = errorCheck(
    dll.euEGST_isOpenOSystemModule, "Eur_EGrabber_CallbackSingleThread_isOpen__on__SystemModule"
)
Eur_EGrabber_CallbackSingleThread_isOpen__on__InterfaceModule = errorCheck(
    dll.euEGST_isOpenOInterfaceModule, "Eur_EGrabber_CallbackSingleThread_isOpen__on__InterfaceModule"
)
Eur_EGrabber_CallbackSingleThread_isOpen__on__DeviceModule = errorCheck(
    dll.euEGST_isOpenODeviceModule, "Eur_EGrabber_CallbackSingleThread_isOpen__on__DeviceModule"
)
Eur_EGrabber_CallbackSingleThread_isOpen__on__StreamModule = errorCheck(
    dll.euEGST_isOpenOStreamModule, "Eur_EGrabber_CallbackSingleThread_isOpen__on__StreamModule"
)
Eur_EGrabber_CallbackSingleThread_isOpen__on__RemoteModule = errorCheck(
    dll.euEGST_isOpenORemoteModule, "Eur_EGrabber_CallbackSingleThread_isOpen__on__RemoteModule"
)
Eur_EGrabber_CallbackSingleThread_gcReadPortData__on__SystemModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGST_gcReadPortDataOSystemModuleFu64vps,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortData__on__SystemModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortData__on__InterfaceModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGST_gcReadPortDataOInterfaceModuleFu64vps,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortData__on__InterfaceModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortData__on__DeviceModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGST_gcReadPortDataODeviceModuleFu64vps,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortData__on__DeviceModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortData__on__StreamModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGST_gcReadPortDataOStreamModuleFu64vps,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortData__on__StreamModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortData__on__RemoteModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGST_gcReadPortDataORemoteModuleFu64vps,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortData__on__RemoteModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortData__on__SystemModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGST_gcWritePortDataOSystemModuleFu64vps,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortData__on__SystemModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortData__on__InterfaceModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGST_gcWritePortDataOInterfaceModuleFu64vps,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortData__on__InterfaceModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortData__on__DeviceModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGST_gcWritePortDataODeviceModuleFu64vps,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortData__on__DeviceModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortData__on__StreamModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGST_gcWritePortDataOStreamModuleFu64vps,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortData__on__StreamModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortData__on__RemoteModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGST_gcWritePortDataORemoteModuleFu64vps,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortData__on__RemoteModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPort__on__SystemModule__from__uint64_t__size_t = errorCheck(
    dll.euEGST_gcReadPortOSystemModuleFu64s,
    "Eur_EGrabber_CallbackSingleThread_gcReadPort__on__SystemModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPort__on__InterfaceModule__from__uint64_t__size_t = errorCheck(
    dll.euEGST_gcReadPortOInterfaceModuleFu64s,
    "Eur_EGrabber_CallbackSingleThread_gcReadPort__on__InterfaceModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPort__on__DeviceModule__from__uint64_t__size_t = errorCheck(
    dll.euEGST_gcReadPortODeviceModuleFu64s,
    "Eur_EGrabber_CallbackSingleThread_gcReadPort__on__DeviceModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPort__on__StreamModule__from__uint64_t__size_t = errorCheck(
    dll.euEGST_gcReadPortOStreamModuleFu64s,
    "Eur_EGrabber_CallbackSingleThread_gcReadPort__on__StreamModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPort__on__RemoteModule__from__uint64_t__size_t = errorCheck(
    dll.euEGST_gcReadPortORemoteModuleFu64s,
    "Eur_EGrabber_CallbackSingleThread_gcReadPort__on__RemoteModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePort__on__SystemModule__from__uint64_t__std_vector_char = errorCheck(
    dll.euEGST_gcWritePortOSystemModuleFu64Svc,
    "Eur_EGrabber_CallbackSingleThread_gcWritePort__on__SystemModule__from__uint64_t__std_vector_char",
)
Eur_EGrabber_CallbackSingleThread_gcWritePort__on__InterfaceModule__from__uint64_t__std_vector_char = errorCheck(
    dll.euEGST_gcWritePortOInterfaceModuleFu64Svc,
    "Eur_EGrabber_CallbackSingleThread_gcWritePort__on__InterfaceModule__from__uint64_t__std_vector_char",
)
Eur_EGrabber_CallbackSingleThread_gcWritePort__on__DeviceModule__from__uint64_t__std_vector_char = errorCheck(
    dll.euEGST_gcWritePortODeviceModuleFu64Svc,
    "Eur_EGrabber_CallbackSingleThread_gcWritePort__on__DeviceModule__from__uint64_t__std_vector_char",
)
Eur_EGrabber_CallbackSingleThread_gcWritePort__on__StreamModule__from__uint64_t__std_vector_char = errorCheck(
    dll.euEGST_gcWritePortOStreamModuleFu64Svc,
    "Eur_EGrabber_CallbackSingleThread_gcWritePort__on__StreamModule__from__uint64_t__std_vector_char",
)
Eur_EGrabber_CallbackSingleThread_gcWritePort__on__RemoteModule__from__uint64_t__std_vector_char = errorCheck(
    dll.euEGST_gcWritePortORemoteModuleFu64Svc,
    "Eur_EGrabber_CallbackSingleThread_gcWritePort__on__RemoteModule__from__uint64_t__std_vector_char",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__size_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAsOSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__size_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int8_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi8OSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int8_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int16_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi16OSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int16_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int32_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi32OSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int32_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int64_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi64OSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int64_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu8OSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint16_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu16OSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint16_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint32_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu32OSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint32_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint64_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu64OSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint64_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__double__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAdOSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__double__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__float__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAfOSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__float__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t_ptr__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu8pOSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t_ptr__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_string__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueASsOSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_string__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__void_ptr__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAvptrOSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__void_ptr__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_char__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueASvcOSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_char__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_std_string__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueASv_std_stringOSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_std_string__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__bool8_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAb8OSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__bool8_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__char_ptr__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAcptrOSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__char_ptr__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__InfoCommandInfo__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueA_CINFOOSystemModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__InfoCommandInfo__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__size_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAsOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__size_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int8_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi8OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int8_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int16_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi16OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int16_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int32_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi32OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int32_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int64_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi64OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int64_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu8OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint16_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu16OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint16_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint32_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu32OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint32_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint64_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu64OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint64_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__double__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAdOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__double__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__float__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAfOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__float__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t_ptr__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu8pOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t_ptr__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_string__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueASsOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_string__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__void_ptr__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAvptrOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__void_ptr__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_char__on__InterfaceModule__from__uint64_t = (
    errorCheck(
        dll.euEGST_gcReadPortValueASvcOInterfaceModuleFu64,
        "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_char__on__InterfaceModule__from__uint64_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_std_string__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueASv_std_stringOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_std_string__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__bool8_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAb8OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__bool8_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__char_ptr__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAcptrOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__char_ptr__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__InfoCommandInfo__on__InterfaceModule__from__uint64_t = (
    errorCheck(
        dll.euEGST_gcReadPortValueA_CINFOOInterfaceModuleFu64,
        "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__InfoCommandInfo__on__InterfaceModule__from__uint64_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__size_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAsODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__size_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int8_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi8ODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int8_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int16_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi16ODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int16_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int32_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi32ODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int32_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int64_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi64ODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int64_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu8ODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint16_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu16ODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint16_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint32_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu32ODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint32_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint64_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu64ODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint64_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__double__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAdODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__double__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__float__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAfODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__float__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t_ptr__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu8pODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t_ptr__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_string__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueASsODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_string__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__void_ptr__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAvptrODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__void_ptr__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_char__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueASvcODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_char__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_std_string__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueASv_std_stringODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_std_string__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__bool8_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAb8ODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__bool8_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__char_ptr__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAcptrODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__char_ptr__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__InfoCommandInfo__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueA_CINFOODeviceModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__InfoCommandInfo__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__size_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAsOStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__size_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int8_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi8OStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int8_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int16_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi16OStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int16_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int32_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi32OStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int32_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int64_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi64OStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int64_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu8OStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint16_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu16OStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint16_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint32_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu32OStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint32_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint64_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu64OStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint64_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__double__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAdOStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__double__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__float__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAfOStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__float__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t_ptr__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu8pOStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t_ptr__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_string__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueASsOStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_string__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__void_ptr__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAvptrOStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__void_ptr__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_char__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueASvcOStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_char__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_std_string__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueASv_std_stringOStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_std_string__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__bool8_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAb8OStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__bool8_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__char_ptr__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAcptrOStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__char_ptr__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__InfoCommandInfo__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueA_CINFOOStreamModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__InfoCommandInfo__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__size_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAsORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__size_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int8_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi8ORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int8_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int16_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi16ORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int16_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int32_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi32ORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int32_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int64_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAi64ORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__int64_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu8ORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint16_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu16ORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint16_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint32_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu32ORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint32_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint64_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu64ORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint64_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__double__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAdORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__double__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__float__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAfORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__float__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t_ptr__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAu8pORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__uint8_t_ptr__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_string__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueASsORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_string__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__void_ptr__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAvptrORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__void_ptr__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_char__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueASvcORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_char__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_std_string__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueASv_std_stringORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__std_vector_std_string__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__bool8_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAb8ORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__bool8_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__char_ptr__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueAcptrORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__char_ptr__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__InfoCommandInfo__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGST_gcReadPortValueA_CINFOORemoteModuleFu64,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortValue__as__InfoCommandInfo__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__size_t__on__SystemModule__from__uint64_t__size_t = errorCheck(
    dll.euEGST_gcWritePortValueWsOSystemModuleFu64s,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__size_t__on__SystemModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int8_t__on__SystemModule__from__uint64_t__int8_t = errorCheck(
    dll.euEGST_gcWritePortValueWi8OSystemModuleFu64i8,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int8_t__on__SystemModule__from__uint64_t__int8_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int16_t__on__SystemModule__from__uint64_t__int16_t = (
    errorCheck(
        dll.euEGST_gcWritePortValueWi16OSystemModuleFu64i16,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int16_t__on__SystemModule__from__uint64_t__int16_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int32_t__on__SystemModule__from__uint64_t__int32_t = (
    errorCheck(
        dll.euEGST_gcWritePortValueWi32OSystemModuleFu64i32,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int32_t__on__SystemModule__from__uint64_t__int32_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int64_t__on__SystemModule__from__uint64_t__int64_t = (
    errorCheck(
        dll.euEGST_gcWritePortValueWi64OSystemModuleFu64i64,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int64_t__on__SystemModule__from__uint64_t__int64_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint8_t__on__SystemModule__from__uint64_t__uint8_t = (
    errorCheck(
        dll.euEGST_gcWritePortValueWu8OSystemModuleFu64u8,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint8_t__on__SystemModule__from__uint64_t__uint8_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint16_t__on__SystemModule__from__uint64_t__uint16_t = errorCheck(
    dll.euEGST_gcWritePortValueWu16OSystemModuleFu64u16,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint16_t__on__SystemModule__from__uint64_t__uint16_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint32_t__on__SystemModule__from__uint64_t__uint32_t = errorCheck(
    dll.euEGST_gcWritePortValueWu32OSystemModuleFu64u32,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint32_t__on__SystemModule__from__uint64_t__uint32_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint64_t__on__SystemModule__from__uint64_t__uint64_t = errorCheck(
    dll.euEGST_gcWritePortValueWu64OSystemModuleFu64u64,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint64_t__on__SystemModule__from__uint64_t__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__double__on__SystemModule__from__uint64_t__double = errorCheck(
    dll.euEGST_gcWritePortValueWdOSystemModuleFu64d,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__double__on__SystemModule__from__uint64_t__double",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__float__on__SystemModule__from__uint64_t__float = errorCheck(
    dll.euEGST_gcWritePortValueWfOSystemModuleFu64f,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__float__on__SystemModule__from__uint64_t__float",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__size_t__on__InterfaceModule__from__uint64_t__size_t = (
    errorCheck(
        dll.euEGST_gcWritePortValueWsOInterfaceModuleFu64s,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__size_t__on__InterfaceModule__from__uint64_t__size_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int8_t__on__InterfaceModule__from__uint64_t__int8_t = (
    errorCheck(
        dll.euEGST_gcWritePortValueWi8OInterfaceModuleFu64i8,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int8_t__on__InterfaceModule__from__uint64_t__int8_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int16_t__on__InterfaceModule__from__uint64_t__int16_t = errorCheck(
    dll.euEGST_gcWritePortValueWi16OInterfaceModuleFu64i16,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int16_t__on__InterfaceModule__from__uint64_t__int16_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int32_t__on__InterfaceModule__from__uint64_t__int32_t = errorCheck(
    dll.euEGST_gcWritePortValueWi32OInterfaceModuleFu64i32,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int32_t__on__InterfaceModule__from__uint64_t__int32_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int64_t__on__InterfaceModule__from__uint64_t__int64_t = errorCheck(
    dll.euEGST_gcWritePortValueWi64OInterfaceModuleFu64i64,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int64_t__on__InterfaceModule__from__uint64_t__int64_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint8_t__on__InterfaceModule__from__uint64_t__uint8_t = errorCheck(
    dll.euEGST_gcWritePortValueWu8OInterfaceModuleFu64u8,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint8_t__on__InterfaceModule__from__uint64_t__uint8_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint16_t__on__InterfaceModule__from__uint64_t__uint16_t = errorCheck(
    dll.euEGST_gcWritePortValueWu16OInterfaceModuleFu64u16,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint16_t__on__InterfaceModule__from__uint64_t__uint16_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint32_t__on__InterfaceModule__from__uint64_t__uint32_t = errorCheck(
    dll.euEGST_gcWritePortValueWu32OInterfaceModuleFu64u32,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint32_t__on__InterfaceModule__from__uint64_t__uint32_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint64_t__on__InterfaceModule__from__uint64_t__uint64_t = errorCheck(
    dll.euEGST_gcWritePortValueWu64OInterfaceModuleFu64u64,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint64_t__on__InterfaceModule__from__uint64_t__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__double__on__InterfaceModule__from__uint64_t__double = (
    errorCheck(
        dll.euEGST_gcWritePortValueWdOInterfaceModuleFu64d,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__double__on__InterfaceModule__from__uint64_t__double",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__float__on__InterfaceModule__from__uint64_t__float = (
    errorCheck(
        dll.euEGST_gcWritePortValueWfOInterfaceModuleFu64f,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__float__on__InterfaceModule__from__uint64_t__float",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__size_t__on__DeviceModule__from__uint64_t__size_t = errorCheck(
    dll.euEGST_gcWritePortValueWsODeviceModuleFu64s,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__size_t__on__DeviceModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int8_t__on__DeviceModule__from__uint64_t__int8_t = errorCheck(
    dll.euEGST_gcWritePortValueWi8ODeviceModuleFu64i8,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int8_t__on__DeviceModule__from__uint64_t__int8_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int16_t__on__DeviceModule__from__uint64_t__int16_t = (
    errorCheck(
        dll.euEGST_gcWritePortValueWi16ODeviceModuleFu64i16,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int16_t__on__DeviceModule__from__uint64_t__int16_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int32_t__on__DeviceModule__from__uint64_t__int32_t = (
    errorCheck(
        dll.euEGST_gcWritePortValueWi32ODeviceModuleFu64i32,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int32_t__on__DeviceModule__from__uint64_t__int32_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int64_t__on__DeviceModule__from__uint64_t__int64_t = (
    errorCheck(
        dll.euEGST_gcWritePortValueWi64ODeviceModuleFu64i64,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int64_t__on__DeviceModule__from__uint64_t__int64_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint8_t__on__DeviceModule__from__uint64_t__uint8_t = (
    errorCheck(
        dll.euEGST_gcWritePortValueWu8ODeviceModuleFu64u8,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint8_t__on__DeviceModule__from__uint64_t__uint8_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint16_t__on__DeviceModule__from__uint64_t__uint16_t = errorCheck(
    dll.euEGST_gcWritePortValueWu16ODeviceModuleFu64u16,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint16_t__on__DeviceModule__from__uint64_t__uint16_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint32_t__on__DeviceModule__from__uint64_t__uint32_t = errorCheck(
    dll.euEGST_gcWritePortValueWu32ODeviceModuleFu64u32,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint32_t__on__DeviceModule__from__uint64_t__uint32_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint64_t__on__DeviceModule__from__uint64_t__uint64_t = errorCheck(
    dll.euEGST_gcWritePortValueWu64ODeviceModuleFu64u64,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint64_t__on__DeviceModule__from__uint64_t__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__double__on__DeviceModule__from__uint64_t__double = errorCheck(
    dll.euEGST_gcWritePortValueWdODeviceModuleFu64d,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__double__on__DeviceModule__from__uint64_t__double",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__float__on__DeviceModule__from__uint64_t__float = errorCheck(
    dll.euEGST_gcWritePortValueWfODeviceModuleFu64f,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__float__on__DeviceModule__from__uint64_t__float",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__size_t__on__StreamModule__from__uint64_t__size_t = errorCheck(
    dll.euEGST_gcWritePortValueWsOStreamModuleFu64s,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__size_t__on__StreamModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int8_t__on__StreamModule__from__uint64_t__int8_t = errorCheck(
    dll.euEGST_gcWritePortValueWi8OStreamModuleFu64i8,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int8_t__on__StreamModule__from__uint64_t__int8_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int16_t__on__StreamModule__from__uint64_t__int16_t = (
    errorCheck(
        dll.euEGST_gcWritePortValueWi16OStreamModuleFu64i16,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int16_t__on__StreamModule__from__uint64_t__int16_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int32_t__on__StreamModule__from__uint64_t__int32_t = (
    errorCheck(
        dll.euEGST_gcWritePortValueWi32OStreamModuleFu64i32,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int32_t__on__StreamModule__from__uint64_t__int32_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int64_t__on__StreamModule__from__uint64_t__int64_t = (
    errorCheck(
        dll.euEGST_gcWritePortValueWi64OStreamModuleFu64i64,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int64_t__on__StreamModule__from__uint64_t__int64_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint8_t__on__StreamModule__from__uint64_t__uint8_t = (
    errorCheck(
        dll.euEGST_gcWritePortValueWu8OStreamModuleFu64u8,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint8_t__on__StreamModule__from__uint64_t__uint8_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint16_t__on__StreamModule__from__uint64_t__uint16_t = errorCheck(
    dll.euEGST_gcWritePortValueWu16OStreamModuleFu64u16,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint16_t__on__StreamModule__from__uint64_t__uint16_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint32_t__on__StreamModule__from__uint64_t__uint32_t = errorCheck(
    dll.euEGST_gcWritePortValueWu32OStreamModuleFu64u32,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint32_t__on__StreamModule__from__uint64_t__uint32_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint64_t__on__StreamModule__from__uint64_t__uint64_t = errorCheck(
    dll.euEGST_gcWritePortValueWu64OStreamModuleFu64u64,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint64_t__on__StreamModule__from__uint64_t__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__double__on__StreamModule__from__uint64_t__double = errorCheck(
    dll.euEGST_gcWritePortValueWdOStreamModuleFu64d,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__double__on__StreamModule__from__uint64_t__double",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__float__on__StreamModule__from__uint64_t__float = errorCheck(
    dll.euEGST_gcWritePortValueWfOStreamModuleFu64f,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__float__on__StreamModule__from__uint64_t__float",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__size_t__on__RemoteModule__from__uint64_t__size_t = errorCheck(
    dll.euEGST_gcWritePortValueWsORemoteModuleFu64s,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__size_t__on__RemoteModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int8_t__on__RemoteModule__from__uint64_t__int8_t = errorCheck(
    dll.euEGST_gcWritePortValueWi8ORemoteModuleFu64i8,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int8_t__on__RemoteModule__from__uint64_t__int8_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int16_t__on__RemoteModule__from__uint64_t__int16_t = (
    errorCheck(
        dll.euEGST_gcWritePortValueWi16ORemoteModuleFu64i16,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int16_t__on__RemoteModule__from__uint64_t__int16_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int32_t__on__RemoteModule__from__uint64_t__int32_t = (
    errorCheck(
        dll.euEGST_gcWritePortValueWi32ORemoteModuleFu64i32,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int32_t__on__RemoteModule__from__uint64_t__int32_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int64_t__on__RemoteModule__from__uint64_t__int64_t = (
    errorCheck(
        dll.euEGST_gcWritePortValueWi64ORemoteModuleFu64i64,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__int64_t__on__RemoteModule__from__uint64_t__int64_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint8_t__on__RemoteModule__from__uint64_t__uint8_t = (
    errorCheck(
        dll.euEGST_gcWritePortValueWu8ORemoteModuleFu64u8,
        "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint8_t__on__RemoteModule__from__uint64_t__uint8_t",
    )
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint16_t__on__RemoteModule__from__uint64_t__uint16_t = errorCheck(
    dll.euEGST_gcWritePortValueWu16ORemoteModuleFu64u16,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint16_t__on__RemoteModule__from__uint64_t__uint16_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint32_t__on__RemoteModule__from__uint64_t__uint32_t = errorCheck(
    dll.euEGST_gcWritePortValueWu32ORemoteModuleFu64u32,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint32_t__on__RemoteModule__from__uint64_t__uint32_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint64_t__on__RemoteModule__from__uint64_t__uint64_t = errorCheck(
    dll.euEGST_gcWritePortValueWu64ORemoteModuleFu64u64,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__uint64_t__on__RemoteModule__from__uint64_t__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__double__on__RemoteModule__from__uint64_t__double = errorCheck(
    dll.euEGST_gcWritePortValueWdORemoteModuleFu64d,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__double__on__RemoteModule__from__uint64_t__double",
)
Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__float__on__RemoteModule__from__uint64_t__float = errorCheck(
    dll.euEGST_gcWritePortValueWfORemoteModuleFu64f,
    "Eur_EGrabber_CallbackSingleThread_gcWritePortValue__with__float__on__RemoteModule__from__uint64_t__float",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortString__on__SystemModule__from__uint64_t__size_t = errorCheck(
    dll.euEGST_gcReadPortStringOSystemModuleFu64s,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortString__on__SystemModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortString__on__InterfaceModule__from__uint64_t__size_t = errorCheck(
    dll.euEGST_gcReadPortStringOInterfaceModuleFu64s,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortString__on__InterfaceModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortString__on__DeviceModule__from__uint64_t__size_t = errorCheck(
    dll.euEGST_gcReadPortStringODeviceModuleFu64s,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortString__on__DeviceModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortString__on__StreamModule__from__uint64_t__size_t = errorCheck(
    dll.euEGST_gcReadPortStringOStreamModuleFu64s,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortString__on__StreamModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackSingleThread_gcReadPortString__on__RemoteModule__from__uint64_t__size_t = errorCheck(
    dll.euEGST_gcReadPortStringORemoteModuleFu64s,
    "Eur_EGrabber_CallbackSingleThread_gcReadPortString__on__RemoteModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackSingleThread_getInteger__on__SystemModule__from__const_char_p = errorCheck(
    dll.euEGST_getIntegerOSystemModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getInteger__on__SystemModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getInteger__on__InterfaceModule__from__const_char_p = errorCheck(
    dll.euEGST_getIntegerOInterfaceModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getInteger__on__InterfaceModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getInteger__on__DeviceModule__from__const_char_p = errorCheck(
    dll.euEGST_getIntegerODeviceModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getInteger__on__DeviceModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getInteger__on__StreamModule__from__const_char_p = errorCheck(
    dll.euEGST_getIntegerOStreamModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getInteger__on__StreamModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getInteger__on__RemoteModule__from__const_char_p = errorCheck(
    dll.euEGST_getIntegerORemoteModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getInteger__on__RemoteModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getFloat__on__SystemModule__from__const_char_p = errorCheck(
    dll.euEGST_getFloatOSystemModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getFloat__on__SystemModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getFloat__on__InterfaceModule__from__const_char_p = errorCheck(
    dll.euEGST_getFloatOInterfaceModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getFloat__on__InterfaceModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getFloat__on__DeviceModule__from__const_char_p = errorCheck(
    dll.euEGST_getFloatODeviceModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getFloat__on__DeviceModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getFloat__on__StreamModule__from__const_char_p = errorCheck(
    dll.euEGST_getFloatOStreamModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getFloat__on__StreamModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getFloat__on__RemoteModule__from__const_char_p = errorCheck(
    dll.euEGST_getFloatORemoteModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getFloat__on__RemoteModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getString__on__SystemModule__from__const_char_p = errorCheck(
    dll.euEGST_getStringOSystemModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getString__on__SystemModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getString__on__InterfaceModule__from__const_char_p = errorCheck(
    dll.euEGST_getStringOInterfaceModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getString__on__InterfaceModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getString__on__DeviceModule__from__const_char_p = errorCheck(
    dll.euEGST_getStringODeviceModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getString__on__DeviceModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getString__on__StreamModule__from__const_char_p = errorCheck(
    dll.euEGST_getStringOStreamModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getString__on__StreamModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getString__on__RemoteModule__from__const_char_p = errorCheck(
    dll.euEGST_getStringORemoteModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getString__on__RemoteModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getStringData__on__SystemModule__from__const_char_p__std_vector_char = errorCheck(
    dll.euEGST_getStringDataOSystemModuleFccpSvc,
    "Eur_EGrabber_CallbackSingleThread_getStringData__on__SystemModule__from__const_char_p__std_vector_char",
)
Eur_EGrabber_CallbackSingleThread_getStringData__on__InterfaceModule__from__const_char_p__std_vector_char = errorCheck(
    dll.euEGST_getStringDataOInterfaceModuleFccpSvc,
    "Eur_EGrabber_CallbackSingleThread_getStringData__on__InterfaceModule__from__const_char_p__std_vector_char",
)
Eur_EGrabber_CallbackSingleThread_getStringData__on__DeviceModule__from__const_char_p__std_vector_char = errorCheck(
    dll.euEGST_getStringDataODeviceModuleFccpSvc,
    "Eur_EGrabber_CallbackSingleThread_getStringData__on__DeviceModule__from__const_char_p__std_vector_char",
)
Eur_EGrabber_CallbackSingleThread_getStringData__on__StreamModule__from__const_char_p__std_vector_char = errorCheck(
    dll.euEGST_getStringDataOStreamModuleFccpSvc,
    "Eur_EGrabber_CallbackSingleThread_getStringData__on__StreamModule__from__const_char_p__std_vector_char",
)
Eur_EGrabber_CallbackSingleThread_getStringData__on__RemoteModule__from__const_char_p__std_vector_char = errorCheck(
    dll.euEGST_getStringDataORemoteModuleFccpSvc,
    "Eur_EGrabber_CallbackSingleThread_getStringData__on__RemoteModule__from__const_char_p__std_vector_char",
)
Eur_EGrabber_CallbackSingleThread_getStringList__on__SystemModule__from__const_char_p = errorCheck(
    dll.euEGST_getStringListOSystemModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getStringList__on__SystemModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getStringList__on__InterfaceModule__from__const_char_p = errorCheck(
    dll.euEGST_getStringListOInterfaceModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getStringList__on__InterfaceModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getStringList__on__DeviceModule__from__const_char_p = errorCheck(
    dll.euEGST_getStringListODeviceModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getStringList__on__DeviceModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getStringList__on__StreamModule__from__const_char_p = errorCheck(
    dll.euEGST_getStringListOStreamModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getStringList__on__StreamModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getStringList__on__RemoteModule__from__const_char_p = errorCheck(
    dll.euEGST_getStringListORemoteModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_getStringList__on__RemoteModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_getRegister__on__SystemModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGST_getRegisterOSystemModuleFccpvps,
    "Eur_EGrabber_CallbackSingleThread_getRegister__on__SystemModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_getRegister__on__InterfaceModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGST_getRegisterOInterfaceModuleFccpvps,
    "Eur_EGrabber_CallbackSingleThread_getRegister__on__InterfaceModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_getRegister__on__DeviceModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGST_getRegisterODeviceModuleFccpvps,
    "Eur_EGrabber_CallbackSingleThread_getRegister__on__DeviceModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_getRegister__on__StreamModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGST_getRegisterOStreamModuleFccpvps,
    "Eur_EGrabber_CallbackSingleThread_getRegister__on__StreamModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_getRegister__on__RemoteModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGST_getRegisterORemoteModuleFccpvps,
    "Eur_EGrabber_CallbackSingleThread_getRegister__on__RemoteModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_setInteger__on__SystemModule__from__const_char_p__int64_t = errorCheck(
    dll.euEGST_setIntegerOSystemModuleFccpi64,
    "Eur_EGrabber_CallbackSingleThread_setInteger__on__SystemModule__from__const_char_p__int64_t",
)
Eur_EGrabber_CallbackSingleThread_setInteger__on__InterfaceModule__from__const_char_p__int64_t = errorCheck(
    dll.euEGST_setIntegerOInterfaceModuleFccpi64,
    "Eur_EGrabber_CallbackSingleThread_setInteger__on__InterfaceModule__from__const_char_p__int64_t",
)
Eur_EGrabber_CallbackSingleThread_setInteger__on__DeviceModule__from__const_char_p__int64_t = errorCheck(
    dll.euEGST_setIntegerODeviceModuleFccpi64,
    "Eur_EGrabber_CallbackSingleThread_setInteger__on__DeviceModule__from__const_char_p__int64_t",
)
Eur_EGrabber_CallbackSingleThread_setInteger__on__StreamModule__from__const_char_p__int64_t = errorCheck(
    dll.euEGST_setIntegerOStreamModuleFccpi64,
    "Eur_EGrabber_CallbackSingleThread_setInteger__on__StreamModule__from__const_char_p__int64_t",
)
Eur_EGrabber_CallbackSingleThread_setInteger__on__RemoteModule__from__const_char_p__int64_t = errorCheck(
    dll.euEGST_setIntegerORemoteModuleFccpi64,
    "Eur_EGrabber_CallbackSingleThread_setInteger__on__RemoteModule__from__const_char_p__int64_t",
)
Eur_EGrabber_CallbackSingleThread_setFloat__on__SystemModule__from__const_char_p__double = errorCheck(
    dll.euEGST_setFloatOSystemModuleFccpd,
    "Eur_EGrabber_CallbackSingleThread_setFloat__on__SystemModule__from__const_char_p__double",
)
Eur_EGrabber_CallbackSingleThread_setFloat__on__InterfaceModule__from__const_char_p__double = errorCheck(
    dll.euEGST_setFloatOInterfaceModuleFccpd,
    "Eur_EGrabber_CallbackSingleThread_setFloat__on__InterfaceModule__from__const_char_p__double",
)
Eur_EGrabber_CallbackSingleThread_setFloat__on__DeviceModule__from__const_char_p__double = errorCheck(
    dll.euEGST_setFloatODeviceModuleFccpd,
    "Eur_EGrabber_CallbackSingleThread_setFloat__on__DeviceModule__from__const_char_p__double",
)
Eur_EGrabber_CallbackSingleThread_setFloat__on__StreamModule__from__const_char_p__double = errorCheck(
    dll.euEGST_setFloatOStreamModuleFccpd,
    "Eur_EGrabber_CallbackSingleThread_setFloat__on__StreamModule__from__const_char_p__double",
)
Eur_EGrabber_CallbackSingleThread_setFloat__on__RemoteModule__from__const_char_p__double = errorCheck(
    dll.euEGST_setFloatORemoteModuleFccpd,
    "Eur_EGrabber_CallbackSingleThread_setFloat__on__RemoteModule__from__const_char_p__double",
)
Eur_EGrabber_CallbackSingleThread_setString__on__SystemModule__from__const_char_p__const_char_p = errorCheck(
    dll.euEGST_setStringOSystemModuleFccpccp,
    "Eur_EGrabber_CallbackSingleThread_setString__on__SystemModule__from__const_char_p__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_setString__on__InterfaceModule__from__const_char_p__const_char_p = errorCheck(
    dll.euEGST_setStringOInterfaceModuleFccpccp,
    "Eur_EGrabber_CallbackSingleThread_setString__on__InterfaceModule__from__const_char_p__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_setString__on__DeviceModule__from__const_char_p__const_char_p = errorCheck(
    dll.euEGST_setStringODeviceModuleFccpccp,
    "Eur_EGrabber_CallbackSingleThread_setString__on__DeviceModule__from__const_char_p__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_setString__on__StreamModule__from__const_char_p__const_char_p = errorCheck(
    dll.euEGST_setStringOStreamModuleFccpccp,
    "Eur_EGrabber_CallbackSingleThread_setString__on__StreamModule__from__const_char_p__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_setString__on__RemoteModule__from__const_char_p__const_char_p = errorCheck(
    dll.euEGST_setStringORemoteModuleFccpccp,
    "Eur_EGrabber_CallbackSingleThread_setString__on__RemoteModule__from__const_char_p__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_setRegister__on__SystemModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGST_setRegisterOSystemModuleFccpvps,
    "Eur_EGrabber_CallbackSingleThread_setRegister__on__SystemModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_setRegister__on__InterfaceModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGST_setRegisterOInterfaceModuleFccpvps,
    "Eur_EGrabber_CallbackSingleThread_setRegister__on__InterfaceModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_setRegister__on__DeviceModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGST_setRegisterODeviceModuleFccpvps,
    "Eur_EGrabber_CallbackSingleThread_setRegister__on__DeviceModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_setRegister__on__StreamModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGST_setRegisterOStreamModuleFccpvps,
    "Eur_EGrabber_CallbackSingleThread_setRegister__on__StreamModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_setRegister__on__RemoteModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGST_setRegisterORemoteModuleFccpvps,
    "Eur_EGrabber_CallbackSingleThread_setRegister__on__RemoteModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_execute__on__SystemModule__from__const_char_p = errorCheck(
    dll.euEGST_executeOSystemModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_execute__on__SystemModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_execute__on__InterfaceModule__from__const_char_p = errorCheck(
    dll.euEGST_executeOInterfaceModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_execute__on__InterfaceModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_execute__on__DeviceModule__from__const_char_p = errorCheck(
    dll.euEGST_executeODeviceModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_execute__on__DeviceModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_execute__on__StreamModule__from__const_char_p = errorCheck(
    dll.euEGST_executeOStreamModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_execute__on__StreamModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_execute__on__RemoteModule__from__const_char_p = errorCheck(
    dll.euEGST_executeORemoteModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_execute__on__RemoteModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_attachEvent__on__SystemModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGST_attachEventOSystemModuleFu64vps,
    "Eur_EGrabber_CallbackSingleThread_attachEvent__on__SystemModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_attachEvent__on__InterfaceModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGST_attachEventOInterfaceModuleFu64vps,
    "Eur_EGrabber_CallbackSingleThread_attachEvent__on__InterfaceModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_attachEvent__on__DeviceModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGST_attachEventODeviceModuleFu64vps,
    "Eur_EGrabber_CallbackSingleThread_attachEvent__on__DeviceModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_attachEvent__on__StreamModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGST_attachEventOStreamModuleFu64vps,
    "Eur_EGrabber_CallbackSingleThread_attachEvent__on__StreamModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_attachEvent__on__RemoteModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGST_attachEventORemoteModuleFu64vps,
    "Eur_EGrabber_CallbackSingleThread_attachEvent__on__RemoteModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_invalidate__on__SystemModule__from__const_char_p = errorCheck(
    dll.euEGST_invalidateOSystemModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_invalidate__on__SystemModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_invalidate__on__InterfaceModule__from__const_char_p = errorCheck(
    dll.euEGST_invalidateOInterfaceModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_invalidate__on__InterfaceModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_invalidate__on__DeviceModule__from__const_char_p = errorCheck(
    dll.euEGST_invalidateODeviceModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_invalidate__on__DeviceModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_invalidate__on__StreamModule__from__const_char_p = errorCheck(
    dll.euEGST_invalidateOStreamModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_invalidate__on__StreamModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_invalidate__on__RemoteModule__from__const_char_p = errorCheck(
    dll.euEGST_invalidateORemoteModuleFccp,
    "Eur_EGrabber_CallbackSingleThread_invalidate__on__RemoteModule__from__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_runScript__from__const_char_p__void_p = errorCheck(
    dll.euEGST_runScriptFccpvp, "Eur_EGrabber_CallbackSingleThread_runScript__from__const_char_p__void_p"
)
Eur_EGrabber_CallbackSingleThread_runScript__from__const_char_p = errorCheck(
    dll.euEGST_runScriptFccp, "Eur_EGrabber_CallbackSingleThread_runScript__from__const_char_p"
)
Eur_EGrabber_CallbackSingleThread_interruptScript__from__const_char_p = errorCheck(
    dll.euEGST_interruptScriptFccp, "Eur_EGrabber_CallbackSingleThread_interruptScript__from__const_char_p"
)
Eur_EGrabber_CallbackSingleThread_onScriptUiCallback__from__const_char_p__void_p__std_map_std_string_std_string__std_string = errorCheck(
    dll.euEGST_onScriptUiCallbackFccpvpSm_std_string_std_stringSs,
    "Eur_EGrabber_CallbackSingleThread_onScriptUiCallback__from__const_char_p__void_p__std_map_std_string_std_string__std_string",
)
Eur_EGrabber_CallbackSingleThread_memento__from__const_char_p = errorCheck(
    dll.euEGST_mementoFccp, "Eur_EGrabber_CallbackSingleThread_memento__from__const_char_p"
)
Eur_EGrabber_CallbackSingleThread_memento__from__unsigned_char__unsigned_char__const_char_p = errorCheck(
    dll.euEGST_mementoFucucccp,
    "Eur_EGrabber_CallbackSingleThread_memento__from__unsigned_char__unsigned_char__const_char_p",
)
Eur_EGrabber_CallbackSingleThread_mementoWaveUp__from__unsigned_char__unsigned_char = errorCheck(
    dll.euEGST_mementoWaveUpFucuc, "Eur_EGrabber_CallbackSingleThread_mementoWaveUp__from__unsigned_char__unsigned_char"
)
Eur_EGrabber_CallbackSingleThread_mementoWaveDown__from__unsigned_char__unsigned_char = errorCheck(
    dll.euEGST_mementoWaveDownFucuc,
    "Eur_EGrabber_CallbackSingleThread_mementoWaveDown__from__unsigned_char__unsigned_char",
)
Eur_EGrabber_CallbackSingleThread_mementoWaveReset__from__unsigned_char__unsigned_char = errorCheck(
    dll.euEGST_mementoWaveResetFucuc,
    "Eur_EGrabber_CallbackSingleThread_mementoWaveReset__from__unsigned_char__unsigned_char",
)
Eur_EGrabber_CallbackSingleThread_mementoWaveValue__from__unsigned_char__unsigned_char__uint64_t = errorCheck(
    dll.euEGST_mementoWaveValueFucucu64,
    "Eur_EGrabber_CallbackSingleThread_mementoWaveValue__from__unsigned_char__unsigned_char__uint64_t",
)
Eur_EGrabber_CallbackSingleThread_mementoWaveNoValue__from__unsigned_char__unsigned_char = errorCheck(
    dll.euEGST_mementoWaveNoValueFucuc,
    "Eur_EGrabber_CallbackSingleThread_mementoWaveNoValue__from__unsigned_char__unsigned_char",
)
Eur_EGrabber_CallbackSingleThread_enableEvent__with__NewBufferData = errorCheck(
    dll.euEGST_enableEventWNewBufferData, "Eur_EGrabber_CallbackSingleThread_enableEvent__with__NewBufferData"
)
Eur_EGrabber_CallbackSingleThread_enableEvent__with__IoToolboxData = errorCheck(
    dll.euEGST_enableEventWIoToolboxData, "Eur_EGrabber_CallbackSingleThread_enableEvent__with__IoToolboxData"
)
Eur_EGrabber_CallbackSingleThread_enableEvent__with__CicData = errorCheck(
    dll.euEGST_enableEventWCicData, "Eur_EGrabber_CallbackSingleThread_enableEvent__with__CicData"
)
Eur_EGrabber_CallbackSingleThread_enableEvent__with__DataStreamData = errorCheck(
    dll.euEGST_enableEventWDataStreamData, "Eur_EGrabber_CallbackSingleThread_enableEvent__with__DataStreamData"
)
Eur_EGrabber_CallbackSingleThread_enableEvent__with__CxpInterfaceData = errorCheck(
    dll.euEGST_enableEventWCxpInterfaceData, "Eur_EGrabber_CallbackSingleThread_enableEvent__with__CxpInterfaceData"
)
Eur_EGrabber_CallbackSingleThread_enableEvent__with__DeviceErrorData = errorCheck(
    dll.euEGST_enableEventWDeviceErrorData, "Eur_EGrabber_CallbackSingleThread_enableEvent__with__DeviceErrorData"
)
Eur_EGrabber_CallbackSingleThread_enableEvent__with__CxpDeviceData = errorCheck(
    dll.euEGST_enableEventWCxpDeviceData, "Eur_EGrabber_CallbackSingleThread_enableEvent__with__CxpDeviceData"
)
Eur_EGrabber_CallbackSingleThread_enableEvent__with__RemoteDeviceData = errorCheck(
    dll.euEGST_enableEventWRemoteDeviceData, "Eur_EGrabber_CallbackSingleThread_enableEvent__with__RemoteDeviceData"
)
Eur_EGrabber_CallbackSingleThread_enableEvent__with__All = errorCheck(
    dll.euEGST_enableEventWAll, "Eur_EGrabber_CallbackSingleThread_enableEvent__with__All"
)
Eur_EGrabber_CallbackSingleThread_disableEvent__with__NewBufferData = errorCheck(
    dll.euEGST_disableEventWNewBufferData, "Eur_EGrabber_CallbackSingleThread_disableEvent__with__NewBufferData"
)
Eur_EGrabber_CallbackSingleThread_disableEvent__with__IoToolboxData = errorCheck(
    dll.euEGST_disableEventWIoToolboxData, "Eur_EGrabber_CallbackSingleThread_disableEvent__with__IoToolboxData"
)
Eur_EGrabber_CallbackSingleThread_disableEvent__with__CicData = errorCheck(
    dll.euEGST_disableEventWCicData, "Eur_EGrabber_CallbackSingleThread_disableEvent__with__CicData"
)
Eur_EGrabber_CallbackSingleThread_disableEvent__with__DataStreamData = errorCheck(
    dll.euEGST_disableEventWDataStreamData, "Eur_EGrabber_CallbackSingleThread_disableEvent__with__DataStreamData"
)
Eur_EGrabber_CallbackSingleThread_disableEvent__with__CxpInterfaceData = errorCheck(
    dll.euEGST_disableEventWCxpInterfaceData, "Eur_EGrabber_CallbackSingleThread_disableEvent__with__CxpInterfaceData"
)
Eur_EGrabber_CallbackSingleThread_disableEvent__with__DeviceErrorData = errorCheck(
    dll.euEGST_disableEventWDeviceErrorData, "Eur_EGrabber_CallbackSingleThread_disableEvent__with__DeviceErrorData"
)
Eur_EGrabber_CallbackSingleThread_disableEvent__with__CxpDeviceData = errorCheck(
    dll.euEGST_disableEventWCxpDeviceData, "Eur_EGrabber_CallbackSingleThread_disableEvent__with__CxpDeviceData"
)
Eur_EGrabber_CallbackSingleThread_disableEvent__with__RemoteDeviceData = errorCheck(
    dll.euEGST_disableEventWRemoteDeviceData, "Eur_EGrabber_CallbackSingleThread_disableEvent__with__RemoteDeviceData"
)
Eur_EGrabber_CallbackSingleThread_disableEvent__with__All = errorCheck(
    dll.euEGST_disableEventWAll, "Eur_EGrabber_CallbackSingleThread_disableEvent__with__All"
)
Eur_EGrabber_CallbackSingleThread_flushEvent__with__NewBufferData = errorCheck(
    dll.euEGST_flushEventWNewBufferData, "Eur_EGrabber_CallbackSingleThread_flushEvent__with__NewBufferData"
)
Eur_EGrabber_CallbackSingleThread_flushEvent__with__IoToolboxData = errorCheck(
    dll.euEGST_flushEventWIoToolboxData, "Eur_EGrabber_CallbackSingleThread_flushEvent__with__IoToolboxData"
)
Eur_EGrabber_CallbackSingleThread_flushEvent__with__CicData = errorCheck(
    dll.euEGST_flushEventWCicData, "Eur_EGrabber_CallbackSingleThread_flushEvent__with__CicData"
)
Eur_EGrabber_CallbackSingleThread_flushEvent__with__DataStreamData = errorCheck(
    dll.euEGST_flushEventWDataStreamData, "Eur_EGrabber_CallbackSingleThread_flushEvent__with__DataStreamData"
)
Eur_EGrabber_CallbackSingleThread_flushEvent__with__CxpInterfaceData = errorCheck(
    dll.euEGST_flushEventWCxpInterfaceData, "Eur_EGrabber_CallbackSingleThread_flushEvent__with__CxpInterfaceData"
)
Eur_EGrabber_CallbackSingleThread_flushEvent__with__DeviceErrorData = errorCheck(
    dll.euEGST_flushEventWDeviceErrorData, "Eur_EGrabber_CallbackSingleThread_flushEvent__with__DeviceErrorData"
)
Eur_EGrabber_CallbackSingleThread_flushEvent__with__CxpDeviceData = errorCheck(
    dll.euEGST_flushEventWCxpDeviceData, "Eur_EGrabber_CallbackSingleThread_flushEvent__with__CxpDeviceData"
)
Eur_EGrabber_CallbackSingleThread_flushEvent__with__RemoteDeviceData = errorCheck(
    dll.euEGST_flushEventWRemoteDeviceData, "Eur_EGrabber_CallbackSingleThread_flushEvent__with__RemoteDeviceData"
)
Eur_EGrabber_CallbackSingleThread_flushEvent__with__All = errorCheck(
    dll.euEGST_flushEventWAll, "Eur_EGrabber_CallbackSingleThread_flushEvent__with__All"
)
Eur_EGrabber_CallbackSingleThread_onNewBufferEvent__from__Eur_NewBufferData = errorCheck(
    dll.euEGST_onNewBufferEventFEur_NewBufferData,
    "Eur_EGrabber_CallbackSingleThread_onNewBufferEvent__from__Eur_NewBufferData",
)
Eur_EGrabber_CallbackSingleThread_onIoToolboxEvent__from__Eur_IoToolboxData = errorCheck(
    dll.euEGST_onIoToolboxEventFEur_IoToolboxData,
    "Eur_EGrabber_CallbackSingleThread_onIoToolboxEvent__from__Eur_IoToolboxData",
)
Eur_EGrabber_CallbackSingleThread_onCicEvent__from__Eur_CicData = errorCheck(
    dll.euEGST_onCicEventFEur_CicData, "Eur_EGrabber_CallbackSingleThread_onCicEvent__from__Eur_CicData"
)
Eur_EGrabber_CallbackSingleThread_onDataStreamEvent__from__Eur_DataStreamData = errorCheck(
    dll.euEGST_onDataStreamEventFEur_DataStreamData,
    "Eur_EGrabber_CallbackSingleThread_onDataStreamEvent__from__Eur_DataStreamData",
)
Eur_EGrabber_CallbackSingleThread_onCxpInterfaceEvent__from__Eur_CxpInterfaceData = errorCheck(
    dll.euEGST_onCxpInterfaceEventFEur_CxpInterfaceData,
    "Eur_EGrabber_CallbackSingleThread_onCxpInterfaceEvent__from__Eur_CxpInterfaceData",
)
Eur_EGrabber_CallbackSingleThread_onDeviceErrorEvent__from__Eur_DeviceErrorData = errorCheck(
    dll.euEGST_onDeviceErrorEventFEur_DeviceErrorData,
    "Eur_EGrabber_CallbackSingleThread_onDeviceErrorEvent__from__Eur_DeviceErrorData",
)
Eur_EGrabber_CallbackSingleThread_onCxpDeviceEvent__from__Eur_CxpDeviceData = errorCheck(
    dll.euEGST_onCxpDeviceEventFEur_CxpDeviceData,
    "Eur_EGrabber_CallbackSingleThread_onCxpDeviceEvent__from__Eur_CxpDeviceData",
)
Eur_EGrabber_CallbackSingleThread_onRemoteDeviceEvent__from__Eur_RemoteDeviceData = errorCheck(
    dll.euEGST_onRemoteDeviceEventFEur_RemoteDeviceData,
    "Eur_EGrabber_CallbackSingleThread_onRemoteDeviceEvent__from__Eur_RemoteDeviceData",
)
Eur_EGrabber_CallbackSingleThread_getLastEventGrabberIndex = errorCheck(
    dll.euEGST_getLastEventGrabberIndex, "Eur_EGrabber_CallbackSingleThread_getLastEventGrabberIndex"
)
Eur_EGrabber_CallbackSingleThread_shutdown = errorCheck(
    dll.euEGST_shutdown, "Eur_EGrabber_CallbackSingleThread_shutdown"
)
Eur_EGrabber_CallbackSingleThread_push__from__Eur_NewBufferData = errorCheck(
    dll.euEGST_pushFEur_NewBufferData, "Eur_EGrabber_CallbackSingleThread_push__from__Eur_NewBufferData"
)
Eur_EGrabber_CallbackSingleThread_announceBusBuffer__from__uint64_t__size_t__void_p = errorCheck(
    dll.euEGST_announceBusBufferFu64svp,
    "Eur_EGrabber_CallbackSingleThread_announceBusBuffer__from__uint64_t__size_t__void_p",
)
Eur_EGrabber_CallbackSingleThread_announceBusBuffer__from__uint64_t__size_t = errorCheck(
    dll.euEGST_announceBusBufferFu64s, "Eur_EGrabber_CallbackSingleThread_announceBusBuffer__from__uint64_t__size_t"
)
Eur_EGrabber_CallbackSingleThread_announceNvidiaRdmaBuffer__from__void_p__size_t__void_p = errorCheck(
    dll.euEGST_announceNvidiaRdmaBufferFvpsvp,
    "Eur_EGrabber_CallbackSingleThread_announceNvidiaRdmaBuffer__from__void_p__size_t__void_p",
)
Eur_EGrabber_CallbackSingleThread_announceNvidiaRdmaBuffer__from__void_p__size_t = errorCheck(
    dll.euEGST_announceNvidiaRdmaBufferFvps,
    "Eur_EGrabber_CallbackSingleThread_announceNvidiaRdmaBuffer__from__void_p__size_t",
)
Eur_EGrabber_CallbackSingleThread_getSystemPort__from__int = errorCheck(
    dll.euEGST_getSystemPortFi, "Eur_EGrabber_CallbackSingleThread_getSystemPort__from__int"
)
Eur_EGrabber_CallbackSingleThread_getInterfacePort__from__int = errorCheck(
    dll.euEGST_getInterfacePortFi, "Eur_EGrabber_CallbackSingleThread_getInterfacePort__from__int"
)
Eur_EGrabber_CallbackSingleThread_getDevicePort__from__int = errorCheck(
    dll.euEGST_getDevicePortFi, "Eur_EGrabber_CallbackSingleThread_getDevicePort__from__int"
)
Eur_EGrabber_CallbackSingleThread_getStreamPort__from__int = errorCheck(
    dll.euEGST_getStreamPortFi, "Eur_EGrabber_CallbackSingleThread_getStreamPort__from__int"
)
Eur_EGrabber_CallbackSingleThread_getRemotePort__from__int = errorCheck(
    dll.euEGST_getRemotePortFi, "Eur_EGrabber_CallbackSingleThread_getRemotePort__from__int"
)
Eur_EGrabber_CallbackSingleThread_destroy = errorCheck(dll.euEGST_destroy, "Eur_EGrabber_CallbackSingleThread_destroy")
Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGenTL__int__int__int__DEVICE_ACCESS_FLAGS__bool8_t = errorCheck(
    dll.euEGMT_createFEur_EGenTLiiiDAFb8,
    "Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGenTL__int__int__int__DEVICE_ACCESS_FLAGS__bool8_t",
)
Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGenTL__int__int__int__DEVICE_ACCESS_FLAGS = errorCheck(
    dll.euEGMT_createFEur_EGenTLiiiDAF,
    "Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGenTL__int__int__int__DEVICE_ACCESS_FLAGS",
)
Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGenTL__int__int__int = errorCheck(
    dll.euEGMT_createFEur_EGenTLiii, "Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGenTL__int__int__int"
)
Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGenTL__int__int = errorCheck(
    dll.euEGMT_createFEur_EGenTLii, "Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGenTL__int__int"
)
Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGenTL__int = errorCheck(
    dll.euEGMT_createFEur_EGenTLi, "Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGenTL__int"
)
Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGenTL = errorCheck(
    dll.euEGMT_createFEur_EGenTL, "Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGenTL"
)
Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGrabberInfo__DEVICE_ACCESS_FLAGS__bool8_t = errorCheck(
    dll.euEGMT_createFEurEGInfoDAFb8,
    "Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGrabberInfo__DEVICE_ACCESS_FLAGS__bool8_t",
)
Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGrabberInfo__DEVICE_ACCESS_FLAGS = errorCheck(
    dll.euEGMT_createFEurEGInfoDAF,
    "Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGrabberInfo__DEVICE_ACCESS_FLAGS",
)
Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGrabberInfo = errorCheck(
    dll.euEGMT_createFEurEGInfo, "Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGrabberInfo"
)
Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGrabberCameraInfo__DEVICE_ACCESS_FLAGS = errorCheck(
    dll.euEGMT_createFEurEGCameraInfoDAF,
    "Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGrabberCameraInfo__DEVICE_ACCESS_FLAGS",
)
Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGrabberCameraInfo = errorCheck(
    dll.euEGMT_createFEurEGCameraInfo, "Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGrabberCameraInfo"
)
Eur_EGrabber_CallbackMultiThread_reallocBuffers__from__size_t__size_t = errorCheck(
    dll.euEGMT_reallocBuffersFss, "Eur_EGrabber_CallbackMultiThread_reallocBuffers__from__size_t__size_t"
)
Eur_EGrabber_CallbackMultiThread_reallocBuffers__from__size_t = errorCheck(
    dll.euEGMT_reallocBuffersFs, "Eur_EGrabber_CallbackMultiThread_reallocBuffers__from__size_t"
)
Eur_EGrabber_CallbackMultiThread_announceAndQueue__from__Eur_GenTLMemory__size_t = errorCheck(
    dll.euEGMT_announceAndQueueFEur_GenTLMemorys,
    "Eur_EGrabber_CallbackMultiThread_announceAndQueue__from__Eur_GenTLMemory__size_t",
)
Eur_EGrabber_CallbackMultiThread_announceAndQueue__from__Eur_GenTLMemory = errorCheck(
    dll.euEGMT_announceAndQueueFEur_GenTLMemory,
    "Eur_EGrabber_CallbackMultiThread_announceAndQueue__from__Eur_GenTLMemory",
)
Eur_EGrabber_CallbackMultiThread_announceAndQueue__from__Eur_UserMemory = errorCheck(
    dll.euEGMT_announceAndQueueFEur_UserMemory,
    "Eur_EGrabber_CallbackMultiThread_announceAndQueue__from__Eur_UserMemory",
)
Eur_EGrabber_CallbackMultiThread_announceAndQueue__from__Eur_UserMemoryArray = errorCheck(
    dll.euEGMT_announceAndQueueFEur_UserMemoryArray,
    "Eur_EGrabber_CallbackMultiThread_announceAndQueue__from__Eur_UserMemoryArray",
)
Eur_EGrabber_CallbackMultiThread_announceAndQueue__from__Eur_UserMemoryArray__bool8_t = errorCheck(
    dll.euEGMT_announceAndQueueFEur_UserMemoryArrayb8,
    "Eur_EGrabber_CallbackMultiThread_announceAndQueue__from__Eur_UserMemoryArray__bool8_t",
)
Eur_EGrabber_CallbackMultiThread_announceAndQueue__from__Eur_BusMemory = errorCheck(
    dll.euEGMT_announceAndQueueFEur_BusMemory, "Eur_EGrabber_CallbackMultiThread_announceAndQueue__from__Eur_BusMemory"
)
Eur_EGrabber_CallbackMultiThread_announceAndQueue__from__Eur_NvidiaRdmaMemory = errorCheck(
    dll.euEGMT_announceAndQueueFEur_NvidiaRdmaMemory,
    "Eur_EGrabber_CallbackMultiThread_announceAndQueue__from__Eur_NvidiaRdmaMemory",
)
Eur_EGrabber_CallbackMultiThread_flushBuffers__from__ACQ_QUEUE_TYPE = errorCheck(
    dll.euEGMT_flushBuffersFAQT, "Eur_EGrabber_CallbackMultiThread_flushBuffers__from__ACQ_QUEUE_TYPE"
)
Eur_EGrabber_CallbackMultiThread_flushBuffers = errorCheck(
    dll.euEGMT_flushBuffers, "Eur_EGrabber_CallbackMultiThread_flushBuffers"
)
Eur_EGrabber_CallbackMultiThread_resetBufferQueue = errorCheck(
    dll.euEGMT_resetBufferQueue, "Eur_EGrabber_CallbackMultiThread_resetBufferQueue"
)
Eur_EGrabber_CallbackMultiThread_resetBufferQueue__from__Eur_BufferIndexRange = errorCheck(
    dll.euEGMT_resetBufferQueueFEur_BufferIndexRange,
    "Eur_EGrabber_CallbackMultiThread_resetBufferQueue__from__Eur_BufferIndexRange",
)
Eur_EGrabber_CallbackMultiThread_queue__from__Eur_BufferIndexRange = errorCheck(
    dll.euEGMT_queueFEur_BufferIndexRange, "Eur_EGrabber_CallbackMultiThread_queue__from__Eur_BufferIndexRange"
)
Eur_EGrabber_CallbackMultiThread_revoke__from__Eur_BufferIndexRange = errorCheck(
    dll.euEGMT_revokeFEur_BufferIndexRange, "Eur_EGrabber_CallbackMultiThread_revoke__from__Eur_BufferIndexRange"
)
Eur_EGrabber_CallbackMultiThread_shouldReannounceBuffers = errorCheck(
    dll.euEGMT_shouldReannounceBuffers, "Eur_EGrabber_CallbackMultiThread_shouldReannounceBuffers"
)
Eur_EGrabber_CallbackMultiThread_shouldReallocBuffers = errorCheck(
    dll.euEGMT_shouldReallocBuffers, "Eur_EGrabber_CallbackMultiThread_shouldReallocBuffers"
)
Eur_EGrabber_CallbackMultiThread_start__from__uint64_t__bool8_t = errorCheck(
    dll.euEGMT_startFu64b8, "Eur_EGrabber_CallbackMultiThread_start__from__uint64_t__bool8_t"
)
Eur_EGrabber_CallbackMultiThread_start__from__uint64_t = errorCheck(
    dll.euEGMT_startFu64, "Eur_EGrabber_CallbackMultiThread_start__from__uint64_t"
)
Eur_EGrabber_CallbackMultiThread_start = errorCheck(dll.euEGMT_start, "Eur_EGrabber_CallbackMultiThread_start")
Eur_EGrabber_CallbackMultiThread_stop = errorCheck(dll.euEGMT_stop, "Eur_EGrabber_CallbackMultiThread_stop")
Eur_EGrabber_CallbackMultiThread_getWidth = errorCheck(dll.euEGMT_getWidth, "Eur_EGrabber_CallbackMultiThread_getWidth")
Eur_EGrabber_CallbackMultiThread_getHeight = errorCheck(
    dll.euEGMT_getHeight, "Eur_EGrabber_CallbackMultiThread_getHeight"
)
Eur_EGrabber_CallbackMultiThread_getPayloadSize = errorCheck(
    dll.euEGMT_getPayloadSize, "Eur_EGrabber_CallbackMultiThread_getPayloadSize"
)
Eur_EGrabber_CallbackMultiThread_getPixelFormat = errorCheck(
    dll.euEGMT_getPixelFormat, "Eur_EGrabber_CallbackMultiThread_getPixelFormat"
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__size_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAsOSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__size_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__int8_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAi8OSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__int8_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__int16_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAi16OSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__int16_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__int32_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAi32OSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__int32_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__int64_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAi64OSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__int64_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint8_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu8OSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint8_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint16_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu16OSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint16_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint32_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu32OSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint32_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint64_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu64OSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint64_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__double__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAdOSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__double__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__float__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAfOSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__float__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint8_t_ptr__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu8pOSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint8_t_ptr__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__std_string__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoASsOSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__std_string__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__void_ptr__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAvptrOSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__void_ptr__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__std_vector_char__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoASvcOSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__std_vector_char__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__std_vector_std_string__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoASv_std_stringOSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__std_vector_std_string__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__bool8_t__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAb8OSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__bool8_t__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__char_ptr__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAcptrOSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__char_ptr__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__InfoCommandInfo__on__SystemModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoA_CINFOOSystemModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__InfoCommandInfo__on__SystemModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__size_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAsOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__size_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__int8_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAi8OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__int8_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__int16_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAi16OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__int16_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__int32_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAi32OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__int32_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__int64_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAi64OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__int64_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint8_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu8OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint8_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint16_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu16OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint16_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint32_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu32OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint32_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint64_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu64OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint64_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__double__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAdOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__double__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__float__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAfOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__float__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint8_t_ptr__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu8pOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint8_t_ptr__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__std_string__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoASsOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__std_string__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__void_ptr__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAvptrOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__void_ptr__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__std_vector_char__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoASvcOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__std_vector_char__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__std_vector_std_string__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoASv_std_stringOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__std_vector_std_string__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__bool8_t__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAb8OInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__bool8_t__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__char_ptr__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAcptrOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__char_ptr__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__InfoCommandInfo__on__InterfaceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoA_CINFOOInterfaceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__InfoCommandInfo__on__InterfaceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__size_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAsODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__size_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__int8_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAi8ODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__int8_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__int16_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAi16ODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__int16_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__int32_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAi32ODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__int32_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__int64_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAi64ODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__int64_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint8_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu8ODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint8_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint16_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu16ODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint16_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint32_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu32ODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint32_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint64_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu64ODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint64_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__double__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAdODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__double__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__float__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAfODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__float__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint8_t_ptr__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu8pODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint8_t_ptr__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__std_string__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoASsODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__std_string__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__void_ptr__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAvptrODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__void_ptr__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__std_vector_char__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoASvcODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__std_vector_char__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__std_vector_std_string__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoASv_std_stringODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__std_vector_std_string__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__bool8_t__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAb8ODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__bool8_t__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__char_ptr__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAcptrODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__char_ptr__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__InfoCommandInfo__on__DeviceModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoA_CINFOODeviceModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__InfoCommandInfo__on__DeviceModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__size_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAsOStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__size_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__int8_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAi8OStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__int8_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__int16_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAi16OStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__int16_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__int32_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAi32OStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__int32_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__int64_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAi64OStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__int64_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint8_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu8OStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint8_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint16_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu16OStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint16_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint32_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu32OStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint32_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint64_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu64OStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint64_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__double__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAdOStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__double__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__float__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAfOStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__float__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__uint8_t_ptr__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAu8pOStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__uint8_t_ptr__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__std_string__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoASsOStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__std_string__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__void_ptr__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAvptrOStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__void_ptr__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__std_vector_char__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoASvcOStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__std_vector_char__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__std_vector_std_string__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoASv_std_stringOStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__std_vector_std_string__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__bool8_t__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAb8OStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__bool8_t__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__char_ptr__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoAcptrOStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__char_ptr__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getInfo__as__InfoCommandInfo__on__StreamModule__from__int32_t = errorCheck(
    dll.euEGMT_getInfoA_CINFOOStreamModuleFi32,
    "Eur_EGrabber_CallbackMultiThread_getInfo__as__InfoCommandInfo__on__StreamModule__from__int32_t",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__size_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoAsFsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__size_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__int8_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoAi8FsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__int8_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__int16_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoAi16FsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__int16_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__int32_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoAi32FsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__int32_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__int64_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoAi64FsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__int64_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__uint8_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoAu8FsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__uint8_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__uint16_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoAu16FsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__uint16_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__uint32_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoAu32FsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__uint32_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__uint64_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoAu64FsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__uint64_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__double__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoAdFsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__double__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__float__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoAfFsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__float__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__uint8_t_ptr__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoAu8pFsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__uint8_t_ptr__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__std_string__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoASsFsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__std_string__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__void_ptr__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoAvptrFsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__void_ptr__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__std_vector_char__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoASvcFsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__std_vector_char__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__std_vector_std_string__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoASv_std_stringFsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__std_vector_std_string__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__bool8_t__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoAb8FsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__bool8_t__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__char_ptr__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoAcptrFsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__char_ptr__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__InfoCommandInfo__from__size_t__BUFFER_INFO_CMD = errorCheck(
    dll.euEGMT_getBufferInfoA_CINFOFsBIC,
    "Eur_EGrabber_CallbackMultiThread_getBufferInfo__as__InfoCommandInfo__from__size_t__BUFFER_INFO_CMD",
)
Eur_EGrabber_CallbackMultiThread_getBufferData__from__size_t = errorCheck(
    dll.euEGMT_getBufferDataFs, "Eur_EGrabber_CallbackMultiThread_getBufferData__from__size_t"
)
Eur_EGrabber_CallbackMultiThread_isOpen__on__SystemModule = errorCheck(
    dll.euEGMT_isOpenOSystemModule, "Eur_EGrabber_CallbackMultiThread_isOpen__on__SystemModule"
)
Eur_EGrabber_CallbackMultiThread_isOpen__on__InterfaceModule = errorCheck(
    dll.euEGMT_isOpenOInterfaceModule, "Eur_EGrabber_CallbackMultiThread_isOpen__on__InterfaceModule"
)
Eur_EGrabber_CallbackMultiThread_isOpen__on__DeviceModule = errorCheck(
    dll.euEGMT_isOpenODeviceModule, "Eur_EGrabber_CallbackMultiThread_isOpen__on__DeviceModule"
)
Eur_EGrabber_CallbackMultiThread_isOpen__on__StreamModule = errorCheck(
    dll.euEGMT_isOpenOStreamModule, "Eur_EGrabber_CallbackMultiThread_isOpen__on__StreamModule"
)
Eur_EGrabber_CallbackMultiThread_isOpen__on__RemoteModule = errorCheck(
    dll.euEGMT_isOpenORemoteModule, "Eur_EGrabber_CallbackMultiThread_isOpen__on__RemoteModule"
)
Eur_EGrabber_CallbackMultiThread_gcReadPortData__on__SystemModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGMT_gcReadPortDataOSystemModuleFu64vps,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortData__on__SystemModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortData__on__InterfaceModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGMT_gcReadPortDataOInterfaceModuleFu64vps,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortData__on__InterfaceModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortData__on__DeviceModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGMT_gcReadPortDataODeviceModuleFu64vps,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortData__on__DeviceModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortData__on__StreamModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGMT_gcReadPortDataOStreamModuleFu64vps,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortData__on__StreamModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortData__on__RemoteModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGMT_gcReadPortDataORemoteModuleFu64vps,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortData__on__RemoteModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortData__on__SystemModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGMT_gcWritePortDataOSystemModuleFu64vps,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortData__on__SystemModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortData__on__InterfaceModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGMT_gcWritePortDataOInterfaceModuleFu64vps,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortData__on__InterfaceModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortData__on__DeviceModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGMT_gcWritePortDataODeviceModuleFu64vps,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortData__on__DeviceModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortData__on__StreamModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGMT_gcWritePortDataOStreamModuleFu64vps,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortData__on__StreamModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortData__on__RemoteModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGMT_gcWritePortDataORemoteModuleFu64vps,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortData__on__RemoteModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPort__on__SystemModule__from__uint64_t__size_t = errorCheck(
    dll.euEGMT_gcReadPortOSystemModuleFu64s,
    "Eur_EGrabber_CallbackMultiThread_gcReadPort__on__SystemModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPort__on__InterfaceModule__from__uint64_t__size_t = errorCheck(
    dll.euEGMT_gcReadPortOInterfaceModuleFu64s,
    "Eur_EGrabber_CallbackMultiThread_gcReadPort__on__InterfaceModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPort__on__DeviceModule__from__uint64_t__size_t = errorCheck(
    dll.euEGMT_gcReadPortODeviceModuleFu64s,
    "Eur_EGrabber_CallbackMultiThread_gcReadPort__on__DeviceModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPort__on__StreamModule__from__uint64_t__size_t = errorCheck(
    dll.euEGMT_gcReadPortOStreamModuleFu64s,
    "Eur_EGrabber_CallbackMultiThread_gcReadPort__on__StreamModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPort__on__RemoteModule__from__uint64_t__size_t = errorCheck(
    dll.euEGMT_gcReadPortORemoteModuleFu64s,
    "Eur_EGrabber_CallbackMultiThread_gcReadPort__on__RemoteModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePort__on__SystemModule__from__uint64_t__std_vector_char = errorCheck(
    dll.euEGMT_gcWritePortOSystemModuleFu64Svc,
    "Eur_EGrabber_CallbackMultiThread_gcWritePort__on__SystemModule__from__uint64_t__std_vector_char",
)
Eur_EGrabber_CallbackMultiThread_gcWritePort__on__InterfaceModule__from__uint64_t__std_vector_char = errorCheck(
    dll.euEGMT_gcWritePortOInterfaceModuleFu64Svc,
    "Eur_EGrabber_CallbackMultiThread_gcWritePort__on__InterfaceModule__from__uint64_t__std_vector_char",
)
Eur_EGrabber_CallbackMultiThread_gcWritePort__on__DeviceModule__from__uint64_t__std_vector_char = errorCheck(
    dll.euEGMT_gcWritePortODeviceModuleFu64Svc,
    "Eur_EGrabber_CallbackMultiThread_gcWritePort__on__DeviceModule__from__uint64_t__std_vector_char",
)
Eur_EGrabber_CallbackMultiThread_gcWritePort__on__StreamModule__from__uint64_t__std_vector_char = errorCheck(
    dll.euEGMT_gcWritePortOStreamModuleFu64Svc,
    "Eur_EGrabber_CallbackMultiThread_gcWritePort__on__StreamModule__from__uint64_t__std_vector_char",
)
Eur_EGrabber_CallbackMultiThread_gcWritePort__on__RemoteModule__from__uint64_t__std_vector_char = errorCheck(
    dll.euEGMT_gcWritePortORemoteModuleFu64Svc,
    "Eur_EGrabber_CallbackMultiThread_gcWritePort__on__RemoteModule__from__uint64_t__std_vector_char",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__size_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAsOSystemModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__size_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int8_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi8OSystemModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int8_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int16_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi16OSystemModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int16_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int32_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi32OSystemModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int32_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int64_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi64OSystemModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int64_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu8OSystemModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint16_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu16OSystemModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint16_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint32_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu32OSystemModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint32_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint64_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu64OSystemModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint64_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__double__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAdOSystemModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__double__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__float__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAfOSystemModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__float__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t_ptr__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu8pOSystemModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t_ptr__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_string__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueASsOSystemModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_string__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__void_ptr__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAvptrOSystemModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__void_ptr__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_char__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueASvcOSystemModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_char__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_std_string__on__SystemModule__from__uint64_t = (
    errorCheck(
        dll.euEGMT_gcReadPortValueASv_std_stringOSystemModuleFu64,
        "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_std_string__on__SystemModule__from__uint64_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__bool8_t__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAb8OSystemModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__bool8_t__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__char_ptr__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAcptrOSystemModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__char_ptr__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__InfoCommandInfo__on__SystemModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueA_CINFOOSystemModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__InfoCommandInfo__on__SystemModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__size_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAsOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__size_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int8_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi8OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int8_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int16_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi16OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int16_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int32_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi32OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int32_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int64_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi64OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int64_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu8OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint16_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu16OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint16_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint32_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu32OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint32_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint64_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu64OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint64_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__double__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAdOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__double__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__float__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAfOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__float__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t_ptr__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu8pOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t_ptr__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_string__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueASsOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_string__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__void_ptr__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAvptrOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__void_ptr__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_char__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueASvcOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_char__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_std_string__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueASv_std_stringOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_std_string__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__bool8_t__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAb8OInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__bool8_t__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__char_ptr__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAcptrOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__char_ptr__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__InfoCommandInfo__on__InterfaceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueA_CINFOOInterfaceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__InfoCommandInfo__on__InterfaceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__size_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAsODeviceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__size_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int8_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi8ODeviceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int8_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int16_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi16ODeviceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int16_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int32_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi32ODeviceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int32_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int64_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi64ODeviceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int64_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu8ODeviceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint16_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu16ODeviceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint16_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint32_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu32ODeviceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint32_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint64_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu64ODeviceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint64_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__double__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAdODeviceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__double__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__float__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAfODeviceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__float__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t_ptr__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu8pODeviceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t_ptr__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_string__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueASsODeviceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_string__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__void_ptr__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAvptrODeviceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__void_ptr__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_char__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueASvcODeviceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_char__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_std_string__on__DeviceModule__from__uint64_t = (
    errorCheck(
        dll.euEGMT_gcReadPortValueASv_std_stringODeviceModuleFu64,
        "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_std_string__on__DeviceModule__from__uint64_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__bool8_t__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAb8ODeviceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__bool8_t__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__char_ptr__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAcptrODeviceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__char_ptr__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__InfoCommandInfo__on__DeviceModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueA_CINFOODeviceModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__InfoCommandInfo__on__DeviceModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__size_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAsOStreamModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__size_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int8_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi8OStreamModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int8_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int16_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi16OStreamModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int16_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int32_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi32OStreamModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int32_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int64_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi64OStreamModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int64_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu8OStreamModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint16_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu16OStreamModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint16_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint32_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu32OStreamModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint32_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint64_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu64OStreamModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint64_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__double__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAdOStreamModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__double__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__float__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAfOStreamModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__float__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t_ptr__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu8pOStreamModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t_ptr__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_string__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueASsOStreamModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_string__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__void_ptr__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAvptrOStreamModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__void_ptr__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_char__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueASvcOStreamModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_char__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_std_string__on__StreamModule__from__uint64_t = (
    errorCheck(
        dll.euEGMT_gcReadPortValueASv_std_stringOStreamModuleFu64,
        "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_std_string__on__StreamModule__from__uint64_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__bool8_t__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAb8OStreamModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__bool8_t__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__char_ptr__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAcptrOStreamModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__char_ptr__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__InfoCommandInfo__on__StreamModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueA_CINFOOStreamModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__InfoCommandInfo__on__StreamModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__size_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAsORemoteModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__size_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int8_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi8ORemoteModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int8_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int16_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi16ORemoteModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int16_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int32_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi32ORemoteModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int32_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int64_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAi64ORemoteModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__int64_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu8ORemoteModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint16_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu16ORemoteModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint16_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint32_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu32ORemoteModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint32_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint64_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu64ORemoteModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint64_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__double__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAdORemoteModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__double__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__float__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAfORemoteModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__float__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t_ptr__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAu8pORemoteModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__uint8_t_ptr__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_string__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueASsORemoteModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_string__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__void_ptr__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAvptrORemoteModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__void_ptr__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_char__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueASvcORemoteModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_char__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_std_string__on__RemoteModule__from__uint64_t = (
    errorCheck(
        dll.euEGMT_gcReadPortValueASv_std_stringORemoteModuleFu64,
        "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__std_vector_std_string__on__RemoteModule__from__uint64_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__bool8_t__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAb8ORemoteModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__bool8_t__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__char_ptr__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueAcptrORemoteModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__char_ptr__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__InfoCommandInfo__on__RemoteModule__from__uint64_t = errorCheck(
    dll.euEGMT_gcReadPortValueA_CINFOORemoteModuleFu64,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortValue__as__InfoCommandInfo__on__RemoteModule__from__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__size_t__on__SystemModule__from__uint64_t__size_t = errorCheck(
    dll.euEGMT_gcWritePortValueWsOSystemModuleFu64s,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__size_t__on__SystemModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int8_t__on__SystemModule__from__uint64_t__int8_t = errorCheck(
    dll.euEGMT_gcWritePortValueWi8OSystemModuleFu64i8,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int8_t__on__SystemModule__from__uint64_t__int8_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int16_t__on__SystemModule__from__uint64_t__int16_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWi16OSystemModuleFu64i16,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int16_t__on__SystemModule__from__uint64_t__int16_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int32_t__on__SystemModule__from__uint64_t__int32_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWi32OSystemModuleFu64i32,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int32_t__on__SystemModule__from__uint64_t__int32_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int64_t__on__SystemModule__from__uint64_t__int64_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWi64OSystemModuleFu64i64,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int64_t__on__SystemModule__from__uint64_t__int64_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint8_t__on__SystemModule__from__uint64_t__uint8_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWu8OSystemModuleFu64u8,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint8_t__on__SystemModule__from__uint64_t__uint8_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint16_t__on__SystemModule__from__uint64_t__uint16_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWu16OSystemModuleFu64u16,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint16_t__on__SystemModule__from__uint64_t__uint16_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint32_t__on__SystemModule__from__uint64_t__uint32_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWu32OSystemModuleFu64u32,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint32_t__on__SystemModule__from__uint64_t__uint32_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint64_t__on__SystemModule__from__uint64_t__uint64_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWu64OSystemModuleFu64u64,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint64_t__on__SystemModule__from__uint64_t__uint64_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__double__on__SystemModule__from__uint64_t__double = errorCheck(
    dll.euEGMT_gcWritePortValueWdOSystemModuleFu64d,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__double__on__SystemModule__from__uint64_t__double",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__float__on__SystemModule__from__uint64_t__float = errorCheck(
    dll.euEGMT_gcWritePortValueWfOSystemModuleFu64f,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__float__on__SystemModule__from__uint64_t__float",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__size_t__on__InterfaceModule__from__uint64_t__size_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWsOInterfaceModuleFu64s,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__size_t__on__InterfaceModule__from__uint64_t__size_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int8_t__on__InterfaceModule__from__uint64_t__int8_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWi8OInterfaceModuleFu64i8,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int8_t__on__InterfaceModule__from__uint64_t__int8_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int16_t__on__InterfaceModule__from__uint64_t__int16_t = errorCheck(
    dll.euEGMT_gcWritePortValueWi16OInterfaceModuleFu64i16,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int16_t__on__InterfaceModule__from__uint64_t__int16_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int32_t__on__InterfaceModule__from__uint64_t__int32_t = errorCheck(
    dll.euEGMT_gcWritePortValueWi32OInterfaceModuleFu64i32,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int32_t__on__InterfaceModule__from__uint64_t__int32_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int64_t__on__InterfaceModule__from__uint64_t__int64_t = errorCheck(
    dll.euEGMT_gcWritePortValueWi64OInterfaceModuleFu64i64,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int64_t__on__InterfaceModule__from__uint64_t__int64_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint8_t__on__InterfaceModule__from__uint64_t__uint8_t = errorCheck(
    dll.euEGMT_gcWritePortValueWu8OInterfaceModuleFu64u8,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint8_t__on__InterfaceModule__from__uint64_t__uint8_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint16_t__on__InterfaceModule__from__uint64_t__uint16_t = errorCheck(
    dll.euEGMT_gcWritePortValueWu16OInterfaceModuleFu64u16,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint16_t__on__InterfaceModule__from__uint64_t__uint16_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint32_t__on__InterfaceModule__from__uint64_t__uint32_t = errorCheck(
    dll.euEGMT_gcWritePortValueWu32OInterfaceModuleFu64u32,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint32_t__on__InterfaceModule__from__uint64_t__uint32_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint64_t__on__InterfaceModule__from__uint64_t__uint64_t = errorCheck(
    dll.euEGMT_gcWritePortValueWu64OInterfaceModuleFu64u64,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint64_t__on__InterfaceModule__from__uint64_t__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__double__on__InterfaceModule__from__uint64_t__double = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWdOInterfaceModuleFu64d,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__double__on__InterfaceModule__from__uint64_t__double",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__float__on__InterfaceModule__from__uint64_t__float = errorCheck(
    dll.euEGMT_gcWritePortValueWfOInterfaceModuleFu64f,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__float__on__InterfaceModule__from__uint64_t__float",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__size_t__on__DeviceModule__from__uint64_t__size_t = errorCheck(
    dll.euEGMT_gcWritePortValueWsODeviceModuleFu64s,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__size_t__on__DeviceModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int8_t__on__DeviceModule__from__uint64_t__int8_t = errorCheck(
    dll.euEGMT_gcWritePortValueWi8ODeviceModuleFu64i8,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int8_t__on__DeviceModule__from__uint64_t__int8_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int16_t__on__DeviceModule__from__uint64_t__int16_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWi16ODeviceModuleFu64i16,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int16_t__on__DeviceModule__from__uint64_t__int16_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int32_t__on__DeviceModule__from__uint64_t__int32_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWi32ODeviceModuleFu64i32,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int32_t__on__DeviceModule__from__uint64_t__int32_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int64_t__on__DeviceModule__from__uint64_t__int64_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWi64ODeviceModuleFu64i64,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int64_t__on__DeviceModule__from__uint64_t__int64_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint8_t__on__DeviceModule__from__uint64_t__uint8_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWu8ODeviceModuleFu64u8,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint8_t__on__DeviceModule__from__uint64_t__uint8_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint16_t__on__DeviceModule__from__uint64_t__uint16_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWu16ODeviceModuleFu64u16,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint16_t__on__DeviceModule__from__uint64_t__uint16_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint32_t__on__DeviceModule__from__uint64_t__uint32_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWu32ODeviceModuleFu64u32,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint32_t__on__DeviceModule__from__uint64_t__uint32_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint64_t__on__DeviceModule__from__uint64_t__uint64_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWu64ODeviceModuleFu64u64,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint64_t__on__DeviceModule__from__uint64_t__uint64_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__double__on__DeviceModule__from__uint64_t__double = errorCheck(
    dll.euEGMT_gcWritePortValueWdODeviceModuleFu64d,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__double__on__DeviceModule__from__uint64_t__double",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__float__on__DeviceModule__from__uint64_t__float = errorCheck(
    dll.euEGMT_gcWritePortValueWfODeviceModuleFu64f,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__float__on__DeviceModule__from__uint64_t__float",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__size_t__on__StreamModule__from__uint64_t__size_t = errorCheck(
    dll.euEGMT_gcWritePortValueWsOStreamModuleFu64s,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__size_t__on__StreamModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int8_t__on__StreamModule__from__uint64_t__int8_t = errorCheck(
    dll.euEGMT_gcWritePortValueWi8OStreamModuleFu64i8,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int8_t__on__StreamModule__from__uint64_t__int8_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int16_t__on__StreamModule__from__uint64_t__int16_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWi16OStreamModuleFu64i16,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int16_t__on__StreamModule__from__uint64_t__int16_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int32_t__on__StreamModule__from__uint64_t__int32_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWi32OStreamModuleFu64i32,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int32_t__on__StreamModule__from__uint64_t__int32_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int64_t__on__StreamModule__from__uint64_t__int64_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWi64OStreamModuleFu64i64,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int64_t__on__StreamModule__from__uint64_t__int64_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint8_t__on__StreamModule__from__uint64_t__uint8_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWu8OStreamModuleFu64u8,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint8_t__on__StreamModule__from__uint64_t__uint8_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint16_t__on__StreamModule__from__uint64_t__uint16_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWu16OStreamModuleFu64u16,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint16_t__on__StreamModule__from__uint64_t__uint16_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint32_t__on__StreamModule__from__uint64_t__uint32_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWu32OStreamModuleFu64u32,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint32_t__on__StreamModule__from__uint64_t__uint32_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint64_t__on__StreamModule__from__uint64_t__uint64_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWu64OStreamModuleFu64u64,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint64_t__on__StreamModule__from__uint64_t__uint64_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__double__on__StreamModule__from__uint64_t__double = errorCheck(
    dll.euEGMT_gcWritePortValueWdOStreamModuleFu64d,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__double__on__StreamModule__from__uint64_t__double",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__float__on__StreamModule__from__uint64_t__float = errorCheck(
    dll.euEGMT_gcWritePortValueWfOStreamModuleFu64f,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__float__on__StreamModule__from__uint64_t__float",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__size_t__on__RemoteModule__from__uint64_t__size_t = errorCheck(
    dll.euEGMT_gcWritePortValueWsORemoteModuleFu64s,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__size_t__on__RemoteModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int8_t__on__RemoteModule__from__uint64_t__int8_t = errorCheck(
    dll.euEGMT_gcWritePortValueWi8ORemoteModuleFu64i8,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int8_t__on__RemoteModule__from__uint64_t__int8_t",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int16_t__on__RemoteModule__from__uint64_t__int16_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWi16ORemoteModuleFu64i16,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int16_t__on__RemoteModule__from__uint64_t__int16_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int32_t__on__RemoteModule__from__uint64_t__int32_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWi32ORemoteModuleFu64i32,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int32_t__on__RemoteModule__from__uint64_t__int32_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int64_t__on__RemoteModule__from__uint64_t__int64_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWi64ORemoteModuleFu64i64,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__int64_t__on__RemoteModule__from__uint64_t__int64_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint8_t__on__RemoteModule__from__uint64_t__uint8_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWu8ORemoteModuleFu64u8,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint8_t__on__RemoteModule__from__uint64_t__uint8_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint16_t__on__RemoteModule__from__uint64_t__uint16_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWu16ORemoteModuleFu64u16,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint16_t__on__RemoteModule__from__uint64_t__uint16_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint32_t__on__RemoteModule__from__uint64_t__uint32_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWu32ORemoteModuleFu64u32,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint32_t__on__RemoteModule__from__uint64_t__uint32_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint64_t__on__RemoteModule__from__uint64_t__uint64_t = (
    errorCheck(
        dll.euEGMT_gcWritePortValueWu64ORemoteModuleFu64u64,
        "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__uint64_t__on__RemoteModule__from__uint64_t__uint64_t",
    )
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__double__on__RemoteModule__from__uint64_t__double = errorCheck(
    dll.euEGMT_gcWritePortValueWdORemoteModuleFu64d,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__double__on__RemoteModule__from__uint64_t__double",
)
Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__float__on__RemoteModule__from__uint64_t__float = errorCheck(
    dll.euEGMT_gcWritePortValueWfORemoteModuleFu64f,
    "Eur_EGrabber_CallbackMultiThread_gcWritePortValue__with__float__on__RemoteModule__from__uint64_t__float",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortString__on__SystemModule__from__uint64_t__size_t = errorCheck(
    dll.euEGMT_gcReadPortStringOSystemModuleFu64s,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortString__on__SystemModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortString__on__InterfaceModule__from__uint64_t__size_t = errorCheck(
    dll.euEGMT_gcReadPortStringOInterfaceModuleFu64s,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortString__on__InterfaceModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortString__on__DeviceModule__from__uint64_t__size_t = errorCheck(
    dll.euEGMT_gcReadPortStringODeviceModuleFu64s,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortString__on__DeviceModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortString__on__StreamModule__from__uint64_t__size_t = errorCheck(
    dll.euEGMT_gcReadPortStringOStreamModuleFu64s,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortString__on__StreamModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackMultiThread_gcReadPortString__on__RemoteModule__from__uint64_t__size_t = errorCheck(
    dll.euEGMT_gcReadPortStringORemoteModuleFu64s,
    "Eur_EGrabber_CallbackMultiThread_gcReadPortString__on__RemoteModule__from__uint64_t__size_t",
)
Eur_EGrabber_CallbackMultiThread_getInteger__on__SystemModule__from__const_char_p = errorCheck(
    dll.euEGMT_getIntegerOSystemModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getInteger__on__SystemModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getInteger__on__InterfaceModule__from__const_char_p = errorCheck(
    dll.euEGMT_getIntegerOInterfaceModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getInteger__on__InterfaceModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getInteger__on__DeviceModule__from__const_char_p = errorCheck(
    dll.euEGMT_getIntegerODeviceModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getInteger__on__DeviceModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getInteger__on__StreamModule__from__const_char_p = errorCheck(
    dll.euEGMT_getIntegerOStreamModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getInteger__on__StreamModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getInteger__on__RemoteModule__from__const_char_p = errorCheck(
    dll.euEGMT_getIntegerORemoteModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getInteger__on__RemoteModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getFloat__on__SystemModule__from__const_char_p = errorCheck(
    dll.euEGMT_getFloatOSystemModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getFloat__on__SystemModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getFloat__on__InterfaceModule__from__const_char_p = errorCheck(
    dll.euEGMT_getFloatOInterfaceModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getFloat__on__InterfaceModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getFloat__on__DeviceModule__from__const_char_p = errorCheck(
    dll.euEGMT_getFloatODeviceModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getFloat__on__DeviceModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getFloat__on__StreamModule__from__const_char_p = errorCheck(
    dll.euEGMT_getFloatOStreamModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getFloat__on__StreamModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getFloat__on__RemoteModule__from__const_char_p = errorCheck(
    dll.euEGMT_getFloatORemoteModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getFloat__on__RemoteModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getString__on__SystemModule__from__const_char_p = errorCheck(
    dll.euEGMT_getStringOSystemModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getString__on__SystemModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getString__on__InterfaceModule__from__const_char_p = errorCheck(
    dll.euEGMT_getStringOInterfaceModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getString__on__InterfaceModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getString__on__DeviceModule__from__const_char_p = errorCheck(
    dll.euEGMT_getStringODeviceModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getString__on__DeviceModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getString__on__StreamModule__from__const_char_p = errorCheck(
    dll.euEGMT_getStringOStreamModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getString__on__StreamModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getString__on__RemoteModule__from__const_char_p = errorCheck(
    dll.euEGMT_getStringORemoteModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getString__on__RemoteModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getStringData__on__SystemModule__from__const_char_p__std_vector_char = errorCheck(
    dll.euEGMT_getStringDataOSystemModuleFccpSvc,
    "Eur_EGrabber_CallbackMultiThread_getStringData__on__SystemModule__from__const_char_p__std_vector_char",
)
Eur_EGrabber_CallbackMultiThread_getStringData__on__InterfaceModule__from__const_char_p__std_vector_char = errorCheck(
    dll.euEGMT_getStringDataOInterfaceModuleFccpSvc,
    "Eur_EGrabber_CallbackMultiThread_getStringData__on__InterfaceModule__from__const_char_p__std_vector_char",
)
Eur_EGrabber_CallbackMultiThread_getStringData__on__DeviceModule__from__const_char_p__std_vector_char = errorCheck(
    dll.euEGMT_getStringDataODeviceModuleFccpSvc,
    "Eur_EGrabber_CallbackMultiThread_getStringData__on__DeviceModule__from__const_char_p__std_vector_char",
)
Eur_EGrabber_CallbackMultiThread_getStringData__on__StreamModule__from__const_char_p__std_vector_char = errorCheck(
    dll.euEGMT_getStringDataOStreamModuleFccpSvc,
    "Eur_EGrabber_CallbackMultiThread_getStringData__on__StreamModule__from__const_char_p__std_vector_char",
)
Eur_EGrabber_CallbackMultiThread_getStringData__on__RemoteModule__from__const_char_p__std_vector_char = errorCheck(
    dll.euEGMT_getStringDataORemoteModuleFccpSvc,
    "Eur_EGrabber_CallbackMultiThread_getStringData__on__RemoteModule__from__const_char_p__std_vector_char",
)
Eur_EGrabber_CallbackMultiThread_getStringList__on__SystemModule__from__const_char_p = errorCheck(
    dll.euEGMT_getStringListOSystemModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getStringList__on__SystemModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getStringList__on__InterfaceModule__from__const_char_p = errorCheck(
    dll.euEGMT_getStringListOInterfaceModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getStringList__on__InterfaceModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getStringList__on__DeviceModule__from__const_char_p = errorCheck(
    dll.euEGMT_getStringListODeviceModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getStringList__on__DeviceModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getStringList__on__StreamModule__from__const_char_p = errorCheck(
    dll.euEGMT_getStringListOStreamModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getStringList__on__StreamModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getStringList__on__RemoteModule__from__const_char_p = errorCheck(
    dll.euEGMT_getStringListORemoteModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_getStringList__on__RemoteModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_getRegister__on__SystemModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGMT_getRegisterOSystemModuleFccpvps,
    "Eur_EGrabber_CallbackMultiThread_getRegister__on__SystemModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_getRegister__on__InterfaceModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGMT_getRegisterOInterfaceModuleFccpvps,
    "Eur_EGrabber_CallbackMultiThread_getRegister__on__InterfaceModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_getRegister__on__DeviceModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGMT_getRegisterODeviceModuleFccpvps,
    "Eur_EGrabber_CallbackMultiThread_getRegister__on__DeviceModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_getRegister__on__StreamModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGMT_getRegisterOStreamModuleFccpvps,
    "Eur_EGrabber_CallbackMultiThread_getRegister__on__StreamModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_getRegister__on__RemoteModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGMT_getRegisterORemoteModuleFccpvps,
    "Eur_EGrabber_CallbackMultiThread_getRegister__on__RemoteModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_setInteger__on__SystemModule__from__const_char_p__int64_t = errorCheck(
    dll.euEGMT_setIntegerOSystemModuleFccpi64,
    "Eur_EGrabber_CallbackMultiThread_setInteger__on__SystemModule__from__const_char_p__int64_t",
)
Eur_EGrabber_CallbackMultiThread_setInteger__on__InterfaceModule__from__const_char_p__int64_t = errorCheck(
    dll.euEGMT_setIntegerOInterfaceModuleFccpi64,
    "Eur_EGrabber_CallbackMultiThread_setInteger__on__InterfaceModule__from__const_char_p__int64_t",
)
Eur_EGrabber_CallbackMultiThread_setInteger__on__DeviceModule__from__const_char_p__int64_t = errorCheck(
    dll.euEGMT_setIntegerODeviceModuleFccpi64,
    "Eur_EGrabber_CallbackMultiThread_setInteger__on__DeviceModule__from__const_char_p__int64_t",
)
Eur_EGrabber_CallbackMultiThread_setInteger__on__StreamModule__from__const_char_p__int64_t = errorCheck(
    dll.euEGMT_setIntegerOStreamModuleFccpi64,
    "Eur_EGrabber_CallbackMultiThread_setInteger__on__StreamModule__from__const_char_p__int64_t",
)
Eur_EGrabber_CallbackMultiThread_setInteger__on__RemoteModule__from__const_char_p__int64_t = errorCheck(
    dll.euEGMT_setIntegerORemoteModuleFccpi64,
    "Eur_EGrabber_CallbackMultiThread_setInteger__on__RemoteModule__from__const_char_p__int64_t",
)
Eur_EGrabber_CallbackMultiThread_setFloat__on__SystemModule__from__const_char_p__double = errorCheck(
    dll.euEGMT_setFloatOSystemModuleFccpd,
    "Eur_EGrabber_CallbackMultiThread_setFloat__on__SystemModule__from__const_char_p__double",
)
Eur_EGrabber_CallbackMultiThread_setFloat__on__InterfaceModule__from__const_char_p__double = errorCheck(
    dll.euEGMT_setFloatOInterfaceModuleFccpd,
    "Eur_EGrabber_CallbackMultiThread_setFloat__on__InterfaceModule__from__const_char_p__double",
)
Eur_EGrabber_CallbackMultiThread_setFloat__on__DeviceModule__from__const_char_p__double = errorCheck(
    dll.euEGMT_setFloatODeviceModuleFccpd,
    "Eur_EGrabber_CallbackMultiThread_setFloat__on__DeviceModule__from__const_char_p__double",
)
Eur_EGrabber_CallbackMultiThread_setFloat__on__StreamModule__from__const_char_p__double = errorCheck(
    dll.euEGMT_setFloatOStreamModuleFccpd,
    "Eur_EGrabber_CallbackMultiThread_setFloat__on__StreamModule__from__const_char_p__double",
)
Eur_EGrabber_CallbackMultiThread_setFloat__on__RemoteModule__from__const_char_p__double = errorCheck(
    dll.euEGMT_setFloatORemoteModuleFccpd,
    "Eur_EGrabber_CallbackMultiThread_setFloat__on__RemoteModule__from__const_char_p__double",
)
Eur_EGrabber_CallbackMultiThread_setString__on__SystemModule__from__const_char_p__const_char_p = errorCheck(
    dll.euEGMT_setStringOSystemModuleFccpccp,
    "Eur_EGrabber_CallbackMultiThread_setString__on__SystemModule__from__const_char_p__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_setString__on__InterfaceModule__from__const_char_p__const_char_p = errorCheck(
    dll.euEGMT_setStringOInterfaceModuleFccpccp,
    "Eur_EGrabber_CallbackMultiThread_setString__on__InterfaceModule__from__const_char_p__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_setString__on__DeviceModule__from__const_char_p__const_char_p = errorCheck(
    dll.euEGMT_setStringODeviceModuleFccpccp,
    "Eur_EGrabber_CallbackMultiThread_setString__on__DeviceModule__from__const_char_p__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_setString__on__StreamModule__from__const_char_p__const_char_p = errorCheck(
    dll.euEGMT_setStringOStreamModuleFccpccp,
    "Eur_EGrabber_CallbackMultiThread_setString__on__StreamModule__from__const_char_p__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_setString__on__RemoteModule__from__const_char_p__const_char_p = errorCheck(
    dll.euEGMT_setStringORemoteModuleFccpccp,
    "Eur_EGrabber_CallbackMultiThread_setString__on__RemoteModule__from__const_char_p__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_setRegister__on__SystemModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGMT_setRegisterOSystemModuleFccpvps,
    "Eur_EGrabber_CallbackMultiThread_setRegister__on__SystemModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_setRegister__on__InterfaceModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGMT_setRegisterOInterfaceModuleFccpvps,
    "Eur_EGrabber_CallbackMultiThread_setRegister__on__InterfaceModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_setRegister__on__DeviceModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGMT_setRegisterODeviceModuleFccpvps,
    "Eur_EGrabber_CallbackMultiThread_setRegister__on__DeviceModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_setRegister__on__StreamModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGMT_setRegisterOStreamModuleFccpvps,
    "Eur_EGrabber_CallbackMultiThread_setRegister__on__StreamModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_setRegister__on__RemoteModule__from__const_char_p__void_p__size_t = errorCheck(
    dll.euEGMT_setRegisterORemoteModuleFccpvps,
    "Eur_EGrabber_CallbackMultiThread_setRegister__on__RemoteModule__from__const_char_p__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_execute__on__SystemModule__from__const_char_p = errorCheck(
    dll.euEGMT_executeOSystemModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_execute__on__SystemModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_execute__on__InterfaceModule__from__const_char_p = errorCheck(
    dll.euEGMT_executeOInterfaceModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_execute__on__InterfaceModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_execute__on__DeviceModule__from__const_char_p = errorCheck(
    dll.euEGMT_executeODeviceModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_execute__on__DeviceModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_execute__on__StreamModule__from__const_char_p = errorCheck(
    dll.euEGMT_executeOStreamModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_execute__on__StreamModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_execute__on__RemoteModule__from__const_char_p = errorCheck(
    dll.euEGMT_executeORemoteModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_execute__on__RemoteModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_attachEvent__on__SystemModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGMT_attachEventOSystemModuleFu64vps,
    "Eur_EGrabber_CallbackMultiThread_attachEvent__on__SystemModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_attachEvent__on__InterfaceModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGMT_attachEventOInterfaceModuleFu64vps,
    "Eur_EGrabber_CallbackMultiThread_attachEvent__on__InterfaceModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_attachEvent__on__DeviceModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGMT_attachEventODeviceModuleFu64vps,
    "Eur_EGrabber_CallbackMultiThread_attachEvent__on__DeviceModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_attachEvent__on__StreamModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGMT_attachEventOStreamModuleFu64vps,
    "Eur_EGrabber_CallbackMultiThread_attachEvent__on__StreamModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_attachEvent__on__RemoteModule__from__uint64_t__void_p__size_t = errorCheck(
    dll.euEGMT_attachEventORemoteModuleFu64vps,
    "Eur_EGrabber_CallbackMultiThread_attachEvent__on__RemoteModule__from__uint64_t__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_invalidate__on__SystemModule__from__const_char_p = errorCheck(
    dll.euEGMT_invalidateOSystemModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_invalidate__on__SystemModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_invalidate__on__InterfaceModule__from__const_char_p = errorCheck(
    dll.euEGMT_invalidateOInterfaceModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_invalidate__on__InterfaceModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_invalidate__on__DeviceModule__from__const_char_p = errorCheck(
    dll.euEGMT_invalidateODeviceModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_invalidate__on__DeviceModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_invalidate__on__StreamModule__from__const_char_p = errorCheck(
    dll.euEGMT_invalidateOStreamModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_invalidate__on__StreamModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_invalidate__on__RemoteModule__from__const_char_p = errorCheck(
    dll.euEGMT_invalidateORemoteModuleFccp,
    "Eur_EGrabber_CallbackMultiThread_invalidate__on__RemoteModule__from__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_runScript__from__const_char_p__void_p = errorCheck(
    dll.euEGMT_runScriptFccpvp, "Eur_EGrabber_CallbackMultiThread_runScript__from__const_char_p__void_p"
)
Eur_EGrabber_CallbackMultiThread_runScript__from__const_char_p = errorCheck(
    dll.euEGMT_runScriptFccp, "Eur_EGrabber_CallbackMultiThread_runScript__from__const_char_p"
)
Eur_EGrabber_CallbackMultiThread_interruptScript__from__const_char_p = errorCheck(
    dll.euEGMT_interruptScriptFccp, "Eur_EGrabber_CallbackMultiThread_interruptScript__from__const_char_p"
)
Eur_EGrabber_CallbackMultiThread_onScriptUiCallback__from__const_char_p__void_p__std_map_std_string_std_string__std_string = errorCheck(
    dll.euEGMT_onScriptUiCallbackFccpvpSm_std_string_std_stringSs,
    "Eur_EGrabber_CallbackMultiThread_onScriptUiCallback__from__const_char_p__void_p__std_map_std_string_std_string__std_string",
)
Eur_EGrabber_CallbackMultiThread_memento__from__const_char_p = errorCheck(
    dll.euEGMT_mementoFccp, "Eur_EGrabber_CallbackMultiThread_memento__from__const_char_p"
)
Eur_EGrabber_CallbackMultiThread_memento__from__unsigned_char__unsigned_char__const_char_p = errorCheck(
    dll.euEGMT_mementoFucucccp,
    "Eur_EGrabber_CallbackMultiThread_memento__from__unsigned_char__unsigned_char__const_char_p",
)
Eur_EGrabber_CallbackMultiThread_mementoWaveUp__from__unsigned_char__unsigned_char = errorCheck(
    dll.euEGMT_mementoWaveUpFucuc, "Eur_EGrabber_CallbackMultiThread_mementoWaveUp__from__unsigned_char__unsigned_char"
)
Eur_EGrabber_CallbackMultiThread_mementoWaveDown__from__unsigned_char__unsigned_char = errorCheck(
    dll.euEGMT_mementoWaveDownFucuc,
    "Eur_EGrabber_CallbackMultiThread_mementoWaveDown__from__unsigned_char__unsigned_char",
)
Eur_EGrabber_CallbackMultiThread_mementoWaveReset__from__unsigned_char__unsigned_char = errorCheck(
    dll.euEGMT_mementoWaveResetFucuc,
    "Eur_EGrabber_CallbackMultiThread_mementoWaveReset__from__unsigned_char__unsigned_char",
)
Eur_EGrabber_CallbackMultiThread_mementoWaveValue__from__unsigned_char__unsigned_char__uint64_t = errorCheck(
    dll.euEGMT_mementoWaveValueFucucu64,
    "Eur_EGrabber_CallbackMultiThread_mementoWaveValue__from__unsigned_char__unsigned_char__uint64_t",
)
Eur_EGrabber_CallbackMultiThread_mementoWaveNoValue__from__unsigned_char__unsigned_char = errorCheck(
    dll.euEGMT_mementoWaveNoValueFucuc,
    "Eur_EGrabber_CallbackMultiThread_mementoWaveNoValue__from__unsigned_char__unsigned_char",
)
Eur_EGrabber_CallbackMultiThread_enableEvent__with__NewBufferData = errorCheck(
    dll.euEGMT_enableEventWNewBufferData, "Eur_EGrabber_CallbackMultiThread_enableEvent__with__NewBufferData"
)
Eur_EGrabber_CallbackMultiThread_enableEvent__with__IoToolboxData = errorCheck(
    dll.euEGMT_enableEventWIoToolboxData, "Eur_EGrabber_CallbackMultiThread_enableEvent__with__IoToolboxData"
)
Eur_EGrabber_CallbackMultiThread_enableEvent__with__CicData = errorCheck(
    dll.euEGMT_enableEventWCicData, "Eur_EGrabber_CallbackMultiThread_enableEvent__with__CicData"
)
Eur_EGrabber_CallbackMultiThread_enableEvent__with__DataStreamData = errorCheck(
    dll.euEGMT_enableEventWDataStreamData, "Eur_EGrabber_CallbackMultiThread_enableEvent__with__DataStreamData"
)
Eur_EGrabber_CallbackMultiThread_enableEvent__with__CxpInterfaceData = errorCheck(
    dll.euEGMT_enableEventWCxpInterfaceData, "Eur_EGrabber_CallbackMultiThread_enableEvent__with__CxpInterfaceData"
)
Eur_EGrabber_CallbackMultiThread_enableEvent__with__DeviceErrorData = errorCheck(
    dll.euEGMT_enableEventWDeviceErrorData, "Eur_EGrabber_CallbackMultiThread_enableEvent__with__DeviceErrorData"
)
Eur_EGrabber_CallbackMultiThread_enableEvent__with__CxpDeviceData = errorCheck(
    dll.euEGMT_enableEventWCxpDeviceData, "Eur_EGrabber_CallbackMultiThread_enableEvent__with__CxpDeviceData"
)
Eur_EGrabber_CallbackMultiThread_enableEvent__with__RemoteDeviceData = errorCheck(
    dll.euEGMT_enableEventWRemoteDeviceData, "Eur_EGrabber_CallbackMultiThread_enableEvent__with__RemoteDeviceData"
)
Eur_EGrabber_CallbackMultiThread_enableEvent__with__All = errorCheck(
    dll.euEGMT_enableEventWAll, "Eur_EGrabber_CallbackMultiThread_enableEvent__with__All"
)
Eur_EGrabber_CallbackMultiThread_disableEvent__with__NewBufferData = errorCheck(
    dll.euEGMT_disableEventWNewBufferData, "Eur_EGrabber_CallbackMultiThread_disableEvent__with__NewBufferData"
)
Eur_EGrabber_CallbackMultiThread_disableEvent__with__IoToolboxData = errorCheck(
    dll.euEGMT_disableEventWIoToolboxData, "Eur_EGrabber_CallbackMultiThread_disableEvent__with__IoToolboxData"
)
Eur_EGrabber_CallbackMultiThread_disableEvent__with__CicData = errorCheck(
    dll.euEGMT_disableEventWCicData, "Eur_EGrabber_CallbackMultiThread_disableEvent__with__CicData"
)
Eur_EGrabber_CallbackMultiThread_disableEvent__with__DataStreamData = errorCheck(
    dll.euEGMT_disableEventWDataStreamData, "Eur_EGrabber_CallbackMultiThread_disableEvent__with__DataStreamData"
)
Eur_EGrabber_CallbackMultiThread_disableEvent__with__CxpInterfaceData = errorCheck(
    dll.euEGMT_disableEventWCxpInterfaceData, "Eur_EGrabber_CallbackMultiThread_disableEvent__with__CxpInterfaceData"
)
Eur_EGrabber_CallbackMultiThread_disableEvent__with__DeviceErrorData = errorCheck(
    dll.euEGMT_disableEventWDeviceErrorData, "Eur_EGrabber_CallbackMultiThread_disableEvent__with__DeviceErrorData"
)
Eur_EGrabber_CallbackMultiThread_disableEvent__with__CxpDeviceData = errorCheck(
    dll.euEGMT_disableEventWCxpDeviceData, "Eur_EGrabber_CallbackMultiThread_disableEvent__with__CxpDeviceData"
)
Eur_EGrabber_CallbackMultiThread_disableEvent__with__RemoteDeviceData = errorCheck(
    dll.euEGMT_disableEventWRemoteDeviceData, "Eur_EGrabber_CallbackMultiThread_disableEvent__with__RemoteDeviceData"
)
Eur_EGrabber_CallbackMultiThread_disableEvent__with__All = errorCheck(
    dll.euEGMT_disableEventWAll, "Eur_EGrabber_CallbackMultiThread_disableEvent__with__All"
)
Eur_EGrabber_CallbackMultiThread_flushEvent__with__NewBufferData = errorCheck(
    dll.euEGMT_flushEventWNewBufferData, "Eur_EGrabber_CallbackMultiThread_flushEvent__with__NewBufferData"
)
Eur_EGrabber_CallbackMultiThread_flushEvent__with__IoToolboxData = errorCheck(
    dll.euEGMT_flushEventWIoToolboxData, "Eur_EGrabber_CallbackMultiThread_flushEvent__with__IoToolboxData"
)
Eur_EGrabber_CallbackMultiThread_flushEvent__with__CicData = errorCheck(
    dll.euEGMT_flushEventWCicData, "Eur_EGrabber_CallbackMultiThread_flushEvent__with__CicData"
)
Eur_EGrabber_CallbackMultiThread_flushEvent__with__DataStreamData = errorCheck(
    dll.euEGMT_flushEventWDataStreamData, "Eur_EGrabber_CallbackMultiThread_flushEvent__with__DataStreamData"
)
Eur_EGrabber_CallbackMultiThread_flushEvent__with__CxpInterfaceData = errorCheck(
    dll.euEGMT_flushEventWCxpInterfaceData, "Eur_EGrabber_CallbackMultiThread_flushEvent__with__CxpInterfaceData"
)
Eur_EGrabber_CallbackMultiThread_flushEvent__with__DeviceErrorData = errorCheck(
    dll.euEGMT_flushEventWDeviceErrorData, "Eur_EGrabber_CallbackMultiThread_flushEvent__with__DeviceErrorData"
)
Eur_EGrabber_CallbackMultiThread_flushEvent__with__CxpDeviceData = errorCheck(
    dll.euEGMT_flushEventWCxpDeviceData, "Eur_EGrabber_CallbackMultiThread_flushEvent__with__CxpDeviceData"
)
Eur_EGrabber_CallbackMultiThread_flushEvent__with__RemoteDeviceData = errorCheck(
    dll.euEGMT_flushEventWRemoteDeviceData, "Eur_EGrabber_CallbackMultiThread_flushEvent__with__RemoteDeviceData"
)
Eur_EGrabber_CallbackMultiThread_flushEvent__with__All = errorCheck(
    dll.euEGMT_flushEventWAll, "Eur_EGrabber_CallbackMultiThread_flushEvent__with__All"
)
Eur_EGrabber_CallbackMultiThread_onNewBufferEvent__from__Eur_NewBufferData = errorCheck(
    dll.euEGMT_onNewBufferEventFEur_NewBufferData,
    "Eur_EGrabber_CallbackMultiThread_onNewBufferEvent__from__Eur_NewBufferData",
)
Eur_EGrabber_CallbackMultiThread_onIoToolboxEvent__from__Eur_IoToolboxData = errorCheck(
    dll.euEGMT_onIoToolboxEventFEur_IoToolboxData,
    "Eur_EGrabber_CallbackMultiThread_onIoToolboxEvent__from__Eur_IoToolboxData",
)
Eur_EGrabber_CallbackMultiThread_onCicEvent__from__Eur_CicData = errorCheck(
    dll.euEGMT_onCicEventFEur_CicData, "Eur_EGrabber_CallbackMultiThread_onCicEvent__from__Eur_CicData"
)
Eur_EGrabber_CallbackMultiThread_onDataStreamEvent__from__Eur_DataStreamData = errorCheck(
    dll.euEGMT_onDataStreamEventFEur_DataStreamData,
    "Eur_EGrabber_CallbackMultiThread_onDataStreamEvent__from__Eur_DataStreamData",
)
Eur_EGrabber_CallbackMultiThread_onCxpInterfaceEvent__from__Eur_CxpInterfaceData = errorCheck(
    dll.euEGMT_onCxpInterfaceEventFEur_CxpInterfaceData,
    "Eur_EGrabber_CallbackMultiThread_onCxpInterfaceEvent__from__Eur_CxpInterfaceData",
)
Eur_EGrabber_CallbackMultiThread_onDeviceErrorEvent__from__Eur_DeviceErrorData = errorCheck(
    dll.euEGMT_onDeviceErrorEventFEur_DeviceErrorData,
    "Eur_EGrabber_CallbackMultiThread_onDeviceErrorEvent__from__Eur_DeviceErrorData",
)
Eur_EGrabber_CallbackMultiThread_onCxpDeviceEvent__from__Eur_CxpDeviceData = errorCheck(
    dll.euEGMT_onCxpDeviceEventFEur_CxpDeviceData,
    "Eur_EGrabber_CallbackMultiThread_onCxpDeviceEvent__from__Eur_CxpDeviceData",
)
Eur_EGrabber_CallbackMultiThread_onRemoteDeviceEvent__from__Eur_RemoteDeviceData = errorCheck(
    dll.euEGMT_onRemoteDeviceEventFEur_RemoteDeviceData,
    "Eur_EGrabber_CallbackMultiThread_onRemoteDeviceEvent__from__Eur_RemoteDeviceData",
)
Eur_EGrabber_CallbackMultiThread_getLastEventGrabberIndex = errorCheck(
    dll.euEGMT_getLastEventGrabberIndex, "Eur_EGrabber_CallbackMultiThread_getLastEventGrabberIndex"
)
Eur_EGrabber_CallbackMultiThread_shutdown = errorCheck(dll.euEGMT_shutdown, "Eur_EGrabber_CallbackMultiThread_shutdown")
Eur_EGrabber_CallbackMultiThread_push__from__Eur_NewBufferData = errorCheck(
    dll.euEGMT_pushFEur_NewBufferData, "Eur_EGrabber_CallbackMultiThread_push__from__Eur_NewBufferData"
)
Eur_EGrabber_CallbackMultiThread_announceBusBuffer__from__uint64_t__size_t__void_p = errorCheck(
    dll.euEGMT_announceBusBufferFu64svp,
    "Eur_EGrabber_CallbackMultiThread_announceBusBuffer__from__uint64_t__size_t__void_p",
)
Eur_EGrabber_CallbackMultiThread_announceBusBuffer__from__uint64_t__size_t = errorCheck(
    dll.euEGMT_announceBusBufferFu64s, "Eur_EGrabber_CallbackMultiThread_announceBusBuffer__from__uint64_t__size_t"
)
Eur_EGrabber_CallbackMultiThread_announceNvidiaRdmaBuffer__from__void_p__size_t__void_p = errorCheck(
    dll.euEGMT_announceNvidiaRdmaBufferFvpsvp,
    "Eur_EGrabber_CallbackMultiThread_announceNvidiaRdmaBuffer__from__void_p__size_t__void_p",
)
Eur_EGrabber_CallbackMultiThread_announceNvidiaRdmaBuffer__from__void_p__size_t = errorCheck(
    dll.euEGMT_announceNvidiaRdmaBufferFvps,
    "Eur_EGrabber_CallbackMultiThread_announceNvidiaRdmaBuffer__from__void_p__size_t",
)
Eur_EGrabber_CallbackMultiThread_getSystemPort__from__int = errorCheck(
    dll.euEGMT_getSystemPortFi, "Eur_EGrabber_CallbackMultiThread_getSystemPort__from__int"
)
Eur_EGrabber_CallbackMultiThread_getInterfacePort__from__int = errorCheck(
    dll.euEGMT_getInterfacePortFi, "Eur_EGrabber_CallbackMultiThread_getInterfacePort__from__int"
)
Eur_EGrabber_CallbackMultiThread_getDevicePort__from__int = errorCheck(
    dll.euEGMT_getDevicePortFi, "Eur_EGrabber_CallbackMultiThread_getDevicePort__from__int"
)
Eur_EGrabber_CallbackMultiThread_getStreamPort__from__int = errorCheck(
    dll.euEGMT_getStreamPortFi, "Eur_EGrabber_CallbackMultiThread_getStreamPort__from__int"
)
Eur_EGrabber_CallbackMultiThread_getRemotePort__from__int = errorCheck(
    dll.euEGMT_getRemotePortFi, "Eur_EGrabber_CallbackMultiThread_getRemotePort__from__int"
)
Eur_EGrabber_CallbackMultiThread_destroy = errorCheck(dll.euEGMT_destroy, "Eur_EGrabber_CallbackMultiThread_destroy")
Eur_Buffer_create__from__Eur_NewBufferData = errorCheck(
    dll.euBuffer_createFEur_NewBufferData, "Eur_Buffer_create__from__Eur_NewBufferData"
)
Eur_Buffer_push__from__Eur_EGrabberBase = errorCheck(
    dll.euBuffer_pushFEurEGBase, "Eur_Buffer_push__from__Eur_EGrabberBase"
)
Eur_Buffer_getInfo__as__size_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoAsFEurEGBaseBIC, "Eur_Buffer_getInfo__as__size_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD"
)
Eur_Buffer_getInfo__as__int8_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoAi8FEurEGBaseBIC, "Eur_Buffer_getInfo__as__int8_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD"
)
Eur_Buffer_getInfo__as__int16_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoAi16FEurEGBaseBIC, "Eur_Buffer_getInfo__as__int16_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD"
)
Eur_Buffer_getInfo__as__int32_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoAi32FEurEGBaseBIC, "Eur_Buffer_getInfo__as__int32_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD"
)
Eur_Buffer_getInfo__as__int64_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoAi64FEurEGBaseBIC, "Eur_Buffer_getInfo__as__int64_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD"
)
Eur_Buffer_getInfo__as__uint8_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoAu8FEurEGBaseBIC, "Eur_Buffer_getInfo__as__uint8_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD"
)
Eur_Buffer_getInfo__as__uint16_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoAu16FEurEGBaseBIC, "Eur_Buffer_getInfo__as__uint16_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD"
)
Eur_Buffer_getInfo__as__uint32_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoAu32FEurEGBaseBIC, "Eur_Buffer_getInfo__as__uint32_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD"
)
Eur_Buffer_getInfo__as__uint64_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoAu64FEurEGBaseBIC, "Eur_Buffer_getInfo__as__uint64_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD"
)
Eur_Buffer_getInfo__as__double__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoAdFEurEGBaseBIC, "Eur_Buffer_getInfo__as__double__from__Eur_EGrabberBase__BUFFER_INFO_CMD"
)
Eur_Buffer_getInfo__as__float__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoAfFEurEGBaseBIC, "Eur_Buffer_getInfo__as__float__from__Eur_EGrabberBase__BUFFER_INFO_CMD"
)
Eur_Buffer_getInfo__as__uint8_t_ptr__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoAu8pFEurEGBaseBIC,
    "Eur_Buffer_getInfo__as__uint8_t_ptr__from__Eur_EGrabberBase__BUFFER_INFO_CMD",
)
Eur_Buffer_getInfo__as__std_string__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoASsFEurEGBaseBIC, "Eur_Buffer_getInfo__as__std_string__from__Eur_EGrabberBase__BUFFER_INFO_CMD"
)
Eur_Buffer_getInfo__as__void_ptr__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoAvptrFEurEGBaseBIC, "Eur_Buffer_getInfo__as__void_ptr__from__Eur_EGrabberBase__BUFFER_INFO_CMD"
)
Eur_Buffer_getInfo__as__std_vector_char__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoASvcFEurEGBaseBIC,
    "Eur_Buffer_getInfo__as__std_vector_char__from__Eur_EGrabberBase__BUFFER_INFO_CMD",
)
Eur_Buffer_getInfo__as__std_vector_std_string__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoASv_std_stringFEurEGBaseBIC,
    "Eur_Buffer_getInfo__as__std_vector_std_string__from__Eur_EGrabberBase__BUFFER_INFO_CMD",
)
Eur_Buffer_getInfo__as__bool8_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoAb8FEurEGBaseBIC, "Eur_Buffer_getInfo__as__bool8_t__from__Eur_EGrabberBase__BUFFER_INFO_CMD"
)
Eur_Buffer_getInfo__as__char_ptr__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoAcptrFEurEGBaseBIC, "Eur_Buffer_getInfo__as__char_ptr__from__Eur_EGrabberBase__BUFFER_INFO_CMD"
)
Eur_Buffer_getInfo__as__InfoCommandInfo__from__Eur_EGrabberBase__BUFFER_INFO_CMD = errorCheck(
    dll.euBuffer_getInfoA_CINFOFEurEGBaseBIC,
    "Eur_Buffer_getInfo__as__InfoCommandInfo__from__Eur_EGrabberBase__BUFFER_INFO_CMD",
)
Eur_Buffer_getUserPointer = errorCheck(dll.euBuffer_getUserPointer, "Eur_Buffer_getUserPointer")
Eur_Buffer_saveToDisk__from__Eur_EGrabberBase__const_char_p__int64_t__ImageSaveToDiskParams_p = errorCheck(
    dll.euBuffer_saveToDiskFEurEGBaseccpi64_ISTDP_p,
    "Eur_Buffer_saveToDisk__from__Eur_EGrabberBase__const_char_p__int64_t__ImageSaveToDiskParams_p",
)
Eur_Buffer_saveToDisk__from__Eur_EGrabberBase__const_char_p__int64_t = errorCheck(
    dll.euBuffer_saveToDiskFEurEGBaseccpi64, "Eur_Buffer_saveToDisk__from__Eur_EGrabberBase__const_char_p__int64_t"
)
Eur_Buffer_saveToDisk__from__Eur_EGrabberBase__const_char_p = errorCheck(
    dll.euBuffer_saveToDiskFEurEGBaseccp, "Eur_Buffer_saveToDisk__from__Eur_EGrabberBase__const_char_p"
)
Eur_Buffer_getInfo__from__Eur_EGrabberBase = errorCheck(
    dll.euBuffer_getInfoFEurEGBase, "Eur_Buffer_getInfo__from__Eur_EGrabberBase"
)
Eur_Buffer_destroy = errorCheck(dll.euBuffer_destroy, "Eur_Buffer_destroy")
Eur_cti_loading_error_create__from__const_char_p = errorCheck(
    dll.eucti_loading_error_createFccp, "Eur_cti_loading_error_create__from__const_char_p"
)
Eur_cti_loading_error_destroy = errorCheck(dll.eucti_loading_error_destroy, "Eur_cti_loading_error_destroy")
Eur_missing_gentl_symbol_create__from__const_char_p__const_char_p = errorCheck(
    dll.eumissing_gentl_symbol_createFccpccp, "Eur_missing_gentl_symbol_create__from__const_char_p__const_char_p"
)
Eur_missing_gentl_symbol_destroy = errorCheck(dll.eumissing_gentl_symbol_destroy, "Eur_missing_gentl_symbol_destroy")
Eur_unexpected_data_type_create__from__INFO_DATATYPE = errorCheck(
    dll.euunexpected_data_type_createFID, "Eur_unexpected_data_type_create__from__INFO_DATATYPE"
)
Eur_unexpected_data_type_destroy = errorCheck(dll.euunexpected_data_type_destroy, "Eur_unexpected_data_type_destroy")
Eur_unexpected_data_size_create__from__size_t__size_t = errorCheck(
    dll.euunexpected_data_size_createFss, "Eur_unexpected_data_size_create__from__size_t__size_t"
)
Eur_unexpected_data_size_destroy = errorCheck(dll.euunexpected_data_size_destroy, "Eur_unexpected_data_size_destroy")
Eur_client_error_create__from__const_char_p = errorCheck(
    dll.euclient_error_createFccp, "Eur_client_error_create__from__const_char_p"
)
Eur_client_error_destroy = errorCheck(dll.euclient_error_destroy, "Eur_client_error_destroy")
Eur_gentl_error_create__from__GC_ERROR = errorCheck(
    dll.eugentl_error_createFGE, "Eur_gentl_error_create__from__GC_ERROR"
)
Eur_gentl_error_create__from__GC_ERROR__const_char_p = errorCheck(
    dll.eugentl_error_createFGEccp, "Eur_gentl_error_create__from__GC_ERROR__const_char_p"
)
Eur_gentl_error_destroy = errorCheck(dll.eugentl_error_destroy, "Eur_gentl_error_destroy")
Eur_genapi_error_create__from__GENAPI_ERROR_CODE = errorCheck(
    dll.eugenapi_error_createFGEC, "Eur_genapi_error_create__from__GENAPI_ERROR_CODE"
)
Eur_genapi_error_parameter_count = errorCheck(dll.eugenapi_error_parameter_count, "Eur_genapi_error_parameter_count")
Eur_genapi_error_parameter_type__from__size_t = errorCheck(
    dll.eugenapi_error_parameter_typeFs, "Eur_genapi_error_parameter_type__from__size_t"
)
Eur_genapi_error_string_parameter__from__size_t = errorCheck(
    dll.eugenapi_error_string_parameterFs, "Eur_genapi_error_string_parameter__from__size_t"
)
Eur_genapi_error_integer_parameter__from__size_t = errorCheck(
    dll.eugenapi_error_integer_parameterFs, "Eur_genapi_error_integer_parameter__from__size_t"
)
Eur_genapi_error_float_parameter__from__size_t = errorCheck(
    dll.eugenapi_error_float_parameterFs, "Eur_genapi_error_float_parameter__from__size_t"
)
Eur_genapi_error_add_string_parameter__from__char_p = errorCheck(
    dll.eugenapi_error_add_string_parameterFcp, "Eur_genapi_error_add_string_parameter__from__char_p"
)
Eur_genapi_error_add_integer_parameter__from__int64_t = errorCheck(
    dll.eugenapi_error_add_integer_parameterFi64, "Eur_genapi_error_add_integer_parameter__from__int64_t"
)
Eur_genapi_error_add_float_parameter__from__double = errorCheck(
    dll.eugenapi_error_add_float_parameterFd, "Eur_genapi_error_add_float_parameter__from__double"
)
Eur_genapi_error_destroy = errorCheck(dll.eugenapi_error_destroy, "Eur_genapi_error_destroy")
Eur_thread_error_create__from__const_char_p = errorCheck(
    dll.euthread_error_createFccp, "Eur_thread_error_create__from__const_char_p"
)
Eur_thread_error_destroy = errorCheck(dll.euthread_error_destroy, "Eur_thread_error_destroy")
Eur_internal_error_create = errorCheck(dll.euinternal_error_create, "Eur_internal_error_create")
Eur_internal_error_destroy = errorCheck(dll.euinternal_error_destroy, "Eur_internal_error_destroy")
Eur_not_allowed_create = errorCheck(dll.eunot_allowed_create, "Eur_not_allowed_create")
Eur_not_allowed_destroy = errorCheck(dll.eunot_allowed_destroy, "Eur_not_allowed_destroy")
Eur_OneOfAll_create = errorCheck(dll.euEurOOA_create, "Eur_OneOfAll_create")
Eur_OneOfAll_destroy = errorCheck(dll.euEurOOA_destroy, "Eur_OneOfAll_destroy")
Eur_OneOfAll_at_position_1 = errorCheck(dll.euEurOOA_at_position_1, "Eur_OneOfAll_at_position_1")
Eur_OneOfAll_at_position_2 = errorCheck(dll.euEurOOA_at_position_2, "Eur_OneOfAll_at_position_2")
Eur_OneOfAll_at_position_3 = errorCheck(dll.euEurOOA_at_position_3, "Eur_OneOfAll_at_position_3")
Eur_OneOfAll_at_position_4 = errorCheck(dll.euEurOOA_at_position_4, "Eur_OneOfAll_at_position_4")
Eur_OneOfAll_at_position_5 = errorCheck(dll.euEurOOA_at_position_5, "Eur_OneOfAll_at_position_5")
Eur_OneOfAll_at_position_6 = errorCheck(dll.euEurOOA_at_position_6, "Eur_OneOfAll_at_position_6")
Eur_OneOfAll_at_position_7 = errorCheck(dll.euEurOOA_at_position_7, "Eur_OneOfAll_at_position_7")
Eur_OneOfAll_at_position_8 = errorCheck(dll.euEurOOA_at_position_8, "Eur_OneOfAll_at_position_8")
Eur_getEventFilter__on__NewBufferData = errorCheck(
    dll.eugetEventFilterONewBufferData, "Eur_getEventFilter__on__NewBufferData"
)
Eur_getEventFilter__on__IoToolboxData = errorCheck(
    dll.eugetEventFilterOIoToolboxData, "Eur_getEventFilter__on__IoToolboxData"
)
Eur_getEventFilter__on__CicData = errorCheck(dll.eugetEventFilterOCicData, "Eur_getEventFilter__on__CicData")
Eur_getEventFilter__on__DataStreamData = errorCheck(
    dll.eugetEventFilterODataStreamData, "Eur_getEventFilter__on__DataStreamData"
)
Eur_getEventFilter__on__CxpInterfaceData = errorCheck(
    dll.eugetEventFilterOCxpInterfaceData, "Eur_getEventFilter__on__CxpInterfaceData"
)
Eur_getEventFilter__on__DeviceErrorData = errorCheck(
    dll.eugetEventFilterODeviceErrorData, "Eur_getEventFilter__on__DeviceErrorData"
)
Eur_getEventFilter__on__CxpDeviceData = errorCheck(
    dll.eugetEventFilterOCxpDeviceData, "Eur_getEventFilter__on__CxpDeviceData"
)
Eur_getEventFilter__on__RemoteDeviceData = errorCheck(
    dll.eugetEventFilterORemoteDeviceData, "Eur_getEventFilter__on__RemoteDeviceData"
)
Eur_EGrabberInfo_get_interfaceIndex = errorCheck(
    dll.euEurEGInfo_get_interfaceIndex, "Eur_EGrabberInfo_get_interfaceIndex"
)
Eur_EGrabberInfo_get_deviceIndex = errorCheck(dll.euEurEGInfo_get_deviceIndex, "Eur_EGrabberInfo_get_deviceIndex")
Eur_EGrabberInfo_get_streamIndex = errorCheck(dll.euEurEGInfo_get_streamIndex, "Eur_EGrabberInfo_get_streamIndex")
Eur_EGrabberInfo_get_interfaceID = errorCheck(dll.euEurEGInfo_get_interfaceID, "Eur_EGrabberInfo_get_interfaceID")
Eur_EGrabberInfo_get_deviceID = errorCheck(dll.euEurEGInfo_get_deviceID, "Eur_EGrabberInfo_get_deviceID")
Eur_EGrabberInfo_get_streamID = errorCheck(dll.euEurEGInfo_get_streamID, "Eur_EGrabberInfo_get_streamID")
Eur_EGrabberInfo_get_deviceVendorName = errorCheck(
    dll.euEurEGInfo_get_deviceVendorName, "Eur_EGrabberInfo_get_deviceVendorName"
)
Eur_EGrabberInfo_get_deviceModelName = errorCheck(
    dll.euEurEGInfo_get_deviceModelName, "Eur_EGrabberInfo_get_deviceModelName"
)
Eur_EGrabberInfo_get_deviceDescription = errorCheck(
    dll.euEurEGInfo_get_deviceDescription, "Eur_EGrabberInfo_get_deviceDescription"
)
Eur_EGrabberInfo_get_streamDescription = errorCheck(
    dll.euEurEGInfo_get_streamDescription, "Eur_EGrabberInfo_get_streamDescription"
)
Eur_EGrabberInfo_get_deviceUserID = errorCheck(dll.euEurEGInfo_get_deviceUserID, "Eur_EGrabberInfo_get_deviceUserID")
Eur_EGrabberInfo_get_tlType = errorCheck(dll.euEurEGInfo_get_tlType, "Eur_EGrabberInfo_get_tlType")
Eur_EGrabberInfo_get_firmwareStatus = errorCheck(
    dll.euEurEGInfo_get_firmwareStatus, "Eur_EGrabberInfo_get_firmwareStatus"
)
Eur_EGrabberInfo_get_fanStatus = errorCheck(dll.euEurEGInfo_get_fanStatus, "Eur_EGrabberInfo_get_fanStatus")
Eur_EGrabberInfo_get_licenseStatus = errorCheck(dll.euEurEGInfo_get_licenseStatus, "Eur_EGrabberInfo_get_licenseStatus")
Eur_EGrabberInfo_get_isRemoteAvailable = errorCheck(
    dll.euEurEGInfo_get_isRemoteAvailable, "Eur_EGrabberInfo_get_isRemoteAvailable"
)
Eur_EGrabberInfo_get_isDeviceReadOnly = errorCheck(
    dll.euEurEGInfo_get_isDeviceReadOnly, "Eur_EGrabberInfo_get_isDeviceReadOnly"
)
Eur_EGrabberCameraInfo_grabber_count = errorCheck(
    dll.euEurEGCameraInfo_grabber_count, "Eur_EGrabberCameraInfo_grabber_count"
)
Eur_EGrabberCameraInfo_grabber_at__from__size_t = errorCheck(
    dll.euEurEGCameraInfo_grabber_atFs, "Eur_EGrabberCameraInfo_grabber_at__from__size_t"
)
Eur_EGrabberCameraInfo_grabbers_push_back__from__Eur_EGrabberInfo = errorCheck(
    dll.euEurEGCameraInfo_grabbers_push_backFEurEGInfo,
    "Eur_EGrabberCameraInfo_grabbers_push_back__from__Eur_EGrabberInfo",
)
Eur_EGrabber_CallbackOnDemand_setNewBufferEventCallback__from__Euresys_NewBufferEventCallback__void_p = errorCheck(
    dll.euEGCOD_setNewBufferEventCallbackF_NBECallbackvp,
    "Eur_EGrabber_CallbackOnDemand_setNewBufferEventCallback__from__Euresys_NewBufferEventCallback__void_p",
)
Eur_EGrabber_CallbackOnDemand_setIoToolboxEventCallback__from__Euresys_IoToolboxEventCallback__void_p = errorCheck(
    dll.euEGCOD_setIoToolboxEventCallbackF_ITECallbackvp,
    "Eur_EGrabber_CallbackOnDemand_setIoToolboxEventCallback__from__Euresys_IoToolboxEventCallback__void_p",
)
Eur_EGrabber_CallbackOnDemand_setCicEventCallback__from__Euresys_CicEventCallback__void_p = errorCheck(
    dll.euEGCOD_setCicEventCallbackF_CECallbackvp,
    "Eur_EGrabber_CallbackOnDemand_setCicEventCallback__from__Euresys_CicEventCallback__void_p",
)
Eur_EGrabber_CallbackOnDemand_setDataStreamEventCallback__from__Euresys_DataStreamEventCallback__void_p = errorCheck(
    dll.euEGCOD_setDataStreamEventCallbackF_DSECallbackvp,
    "Eur_EGrabber_CallbackOnDemand_setDataStreamEventCallback__from__Euresys_DataStreamEventCallback__void_p",
)
Eur_EGrabber_CallbackOnDemand_setCxpInterfaceEventCallback__from__Euresys_CxpInterfaceEventCallback__void_p = (
    errorCheck(
        dll.euEGCOD_setCxpInterfaceEventCallbackF_CIECallbackvp,
        "Eur_EGrabber_CallbackOnDemand_setCxpInterfaceEventCallback__from__Euresys_CxpInterfaceEventCallback__void_p",
    )
)
Eur_EGrabber_CallbackOnDemand_setDeviceErrorEventCallback__from__Euresys_DeviceErrorEventCallback__void_p = errorCheck(
    dll.euEGCOD_setDeviceErrorEventCallbackF_DEECallbackvp,
    "Eur_EGrabber_CallbackOnDemand_setDeviceErrorEventCallback__from__Euresys_DeviceErrorEventCallback__void_p",
)
Eur_EGrabber_CallbackOnDemand_setCxpDeviceEventCallback__from__Euresys_CxpDeviceEventCallback__void_p = errorCheck(
    dll.euEGCOD_setCxpDeviceEventCallbackF_CDECallbackvp,
    "Eur_EGrabber_CallbackOnDemand_setCxpDeviceEventCallback__from__Euresys_CxpDeviceEventCallback__void_p",
)
Eur_EGrabber_CallbackOnDemand_setRemoteDeviceEventCallback__from__Euresys_RemoteDeviceEventCallback__void_p = (
    errorCheck(
        dll.euEGCOD_setRemoteDeviceEventCallbackF_RDECallbackvp,
        "Eur_EGrabber_CallbackOnDemand_setRemoteDeviceEventCallback__from__Euresys_RemoteDeviceEventCallback__void_p",
    )
)
Eur_EGrabber_CallbackOnDemand_setScriptUiCallback__from__Euresys_ScriptUiCallback__void_p = errorCheck(
    dll.euEGCOD_setScriptUiCallbackFScriptUiCallbackvp,
    "Eur_EGrabber_CallbackOnDemand_setScriptUiCallback__from__Euresys_ScriptUiCallback__void_p",
)
Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGenTL__TL_HANDLE__IF_HANDLE__DEV_HANDLE__DS_HANDLE = errorCheck(
    dll.euEGCOD_createFEur_EGenTLTHIHDHDH,
    "Eur_EGrabber_CallbackOnDemand_create__from__Eur_EGenTL__TL_HANDLE__IF_HANDLE__DEV_HANDLE__DS_HANDLE",
)
Eur_EGrabber_CallbackSingleThread_setNewBufferEventCallback__from__Euresys_NewBufferEventCallback__void_p = errorCheck(
    dll.euEGST_setNewBufferEventCallbackF_NBECallbackvp,
    "Eur_EGrabber_CallbackSingleThread_setNewBufferEventCallback__from__Euresys_NewBufferEventCallback__void_p",
)
Eur_EGrabber_CallbackSingleThread_setIoToolboxEventCallback__from__Euresys_IoToolboxEventCallback__void_p = errorCheck(
    dll.euEGST_setIoToolboxEventCallbackF_ITECallbackvp,
    "Eur_EGrabber_CallbackSingleThread_setIoToolboxEventCallback__from__Euresys_IoToolboxEventCallback__void_p",
)
Eur_EGrabber_CallbackSingleThread_setCicEventCallback__from__Euresys_CicEventCallback__void_p = errorCheck(
    dll.euEGST_setCicEventCallbackF_CECallbackvp,
    "Eur_EGrabber_CallbackSingleThread_setCicEventCallback__from__Euresys_CicEventCallback__void_p",
)
Eur_EGrabber_CallbackSingleThread_setDataStreamEventCallback__from__Euresys_DataStreamEventCallback__void_p = (
    errorCheck(
        dll.euEGST_setDataStreamEventCallbackF_DSECallbackvp,
        "Eur_EGrabber_CallbackSingleThread_setDataStreamEventCallback__from__Euresys_DataStreamEventCallback__void_p",
    )
)
Eur_EGrabber_CallbackSingleThread_setCxpInterfaceEventCallback__from__Euresys_CxpInterfaceEventCallback__void_p = errorCheck(
    dll.euEGST_setCxpInterfaceEventCallbackF_CIECallbackvp,
    "Eur_EGrabber_CallbackSingleThread_setCxpInterfaceEventCallback__from__Euresys_CxpInterfaceEventCallback__void_p",
)
Eur_EGrabber_CallbackSingleThread_setDeviceErrorEventCallback__from__Euresys_DeviceErrorEventCallback__void_p = (
    errorCheck(
        dll.euEGST_setDeviceErrorEventCallbackF_DEECallbackvp,
        "Eur_EGrabber_CallbackSingleThread_setDeviceErrorEventCallback__from__Euresys_DeviceErrorEventCallback__void_p",
    )
)
Eur_EGrabber_CallbackSingleThread_setCxpDeviceEventCallback__from__Euresys_CxpDeviceEventCallback__void_p = errorCheck(
    dll.euEGST_setCxpDeviceEventCallbackF_CDECallbackvp,
    "Eur_EGrabber_CallbackSingleThread_setCxpDeviceEventCallback__from__Euresys_CxpDeviceEventCallback__void_p",
)
Eur_EGrabber_CallbackSingleThread_setRemoteDeviceEventCallback__from__Euresys_RemoteDeviceEventCallback__void_p = errorCheck(
    dll.euEGST_setRemoteDeviceEventCallbackF_RDECallbackvp,
    "Eur_EGrabber_CallbackSingleThread_setRemoteDeviceEventCallback__from__Euresys_RemoteDeviceEventCallback__void_p",
)
Eur_EGrabber_CallbackSingleThread_setScriptUiCallback__from__Euresys_ScriptUiCallback__void_p = errorCheck(
    dll.euEGST_setScriptUiCallbackFScriptUiCallbackvp,
    "Eur_EGrabber_CallbackSingleThread_setScriptUiCallback__from__Euresys_ScriptUiCallback__void_p",
)
Eur_EGrabber_CallbackSingleThread_setThreadStartCallback__from__Euresys_ThreadStartCallback__void_p = errorCheck(
    dll.euEGST_setThreadStartCallbackF_TStartCvp,
    "Eur_EGrabber_CallbackSingleThread_setThreadStartCallback__from__Euresys_ThreadStartCallback__void_p",
)
Eur_EGrabber_CallbackSingleThread_setThreadStopCallback__from__Euresys_ThreadStopCallback__void_p = errorCheck(
    dll.euEGST_setThreadStopCallbackF_TStopCvp,
    "Eur_EGrabber_CallbackSingleThread_setThreadStopCallback__from__Euresys_ThreadStopCallback__void_p",
)
Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGenTL__TL_HANDLE__IF_HANDLE__DEV_HANDLE__DS_HANDLE = errorCheck(
    dll.euEGST_createFEur_EGenTLTHIHDHDH,
    "Eur_EGrabber_CallbackSingleThread_create__from__Eur_EGenTL__TL_HANDLE__IF_HANDLE__DEV_HANDLE__DS_HANDLE",
)
Eur_EGrabber_CallbackMultiThread_setNewBufferEventCallback__from__Euresys_NewBufferEventCallback__void_p = errorCheck(
    dll.euEGMT_setNewBufferEventCallbackF_NBECallbackvp,
    "Eur_EGrabber_CallbackMultiThread_setNewBufferEventCallback__from__Euresys_NewBufferEventCallback__void_p",
)
Eur_EGrabber_CallbackMultiThread_setIoToolboxEventCallback__from__Euresys_IoToolboxEventCallback__void_p = errorCheck(
    dll.euEGMT_setIoToolboxEventCallbackF_ITECallbackvp,
    "Eur_EGrabber_CallbackMultiThread_setIoToolboxEventCallback__from__Euresys_IoToolboxEventCallback__void_p",
)
Eur_EGrabber_CallbackMultiThread_setCicEventCallback__from__Euresys_CicEventCallback__void_p = errorCheck(
    dll.euEGMT_setCicEventCallbackF_CECallbackvp,
    "Eur_EGrabber_CallbackMultiThread_setCicEventCallback__from__Euresys_CicEventCallback__void_p",
)
Eur_EGrabber_CallbackMultiThread_setDataStreamEventCallback__from__Euresys_DataStreamEventCallback__void_p = errorCheck(
    dll.euEGMT_setDataStreamEventCallbackF_DSECallbackvp,
    "Eur_EGrabber_CallbackMultiThread_setDataStreamEventCallback__from__Euresys_DataStreamEventCallback__void_p",
)
Eur_EGrabber_CallbackMultiThread_setCxpInterfaceEventCallback__from__Euresys_CxpInterfaceEventCallback__void_p = errorCheck(
    dll.euEGMT_setCxpInterfaceEventCallbackF_CIECallbackvp,
    "Eur_EGrabber_CallbackMultiThread_setCxpInterfaceEventCallback__from__Euresys_CxpInterfaceEventCallback__void_p",
)
Eur_EGrabber_CallbackMultiThread_setDeviceErrorEventCallback__from__Euresys_DeviceErrorEventCallback__void_p = (
    errorCheck(
        dll.euEGMT_setDeviceErrorEventCallbackF_DEECallbackvp,
        "Eur_EGrabber_CallbackMultiThread_setDeviceErrorEventCallback__from__Euresys_DeviceErrorEventCallback__void_p",
    )
)
Eur_EGrabber_CallbackMultiThread_setCxpDeviceEventCallback__from__Euresys_CxpDeviceEventCallback__void_p = errorCheck(
    dll.euEGMT_setCxpDeviceEventCallbackF_CDECallbackvp,
    "Eur_EGrabber_CallbackMultiThread_setCxpDeviceEventCallback__from__Euresys_CxpDeviceEventCallback__void_p",
)
Eur_EGrabber_CallbackMultiThread_setRemoteDeviceEventCallback__from__Euresys_RemoteDeviceEventCallback__void_p = errorCheck(
    dll.euEGMT_setRemoteDeviceEventCallbackF_RDECallbackvp,
    "Eur_EGrabber_CallbackMultiThread_setRemoteDeviceEventCallback__from__Euresys_RemoteDeviceEventCallback__void_p",
)
Eur_EGrabber_CallbackMultiThread_setScriptUiCallback__from__Euresys_ScriptUiCallback__void_p = errorCheck(
    dll.euEGMT_setScriptUiCallbackFScriptUiCallbackvp,
    "Eur_EGrabber_CallbackMultiThread_setScriptUiCallback__from__Euresys_ScriptUiCallback__void_p",
)
Eur_EGrabber_CallbackMultiThread_setThreadStartCallback__from__Euresys_ThreadStartCallback__void_p = errorCheck(
    dll.euEGMT_setThreadStartCallbackF_TStartCvp,
    "Eur_EGrabber_CallbackMultiThread_setThreadStartCallback__from__Euresys_ThreadStartCallback__void_p",
)
Eur_EGrabber_CallbackMultiThread_setThreadStopCallback__from__Euresys_ThreadStopCallback__void_p = errorCheck(
    dll.euEGMT_setThreadStopCallbackF_TStopCvp,
    "Eur_EGrabber_CallbackMultiThread_setThreadStopCallback__from__Euresys_ThreadStopCallback__void_p",
)
Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGenTL__TL_HANDLE__IF_HANDLE__DEV_HANDLE__DS_HANDLE = errorCheck(
    dll.euEGMT_createFEur_EGenTLTHIHDHDH,
    "Eur_EGrabber_CallbackMultiThread_create__from__Eur_EGenTL__TL_HANDLE__IF_HANDLE__DEV_HANDLE__DS_HANDLE",
)
Eur_ECameraBufferPush_CallbackOnDemand__from__Eur_NewBufferData = errorCheck(
    dll.euECameraBufferPush_CallbackOnDemandFEur_NewBufferData,
    "Eur_ECameraBufferPush_CallbackOnDemand__from__Eur_NewBufferData",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__size_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandAsFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__size_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__int8_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandAi8FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__int8_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__int16_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandAi16FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__int16_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__int32_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandAi32FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__int32_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__int64_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandAi64FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__int64_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__uint8_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandAu8FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__uint8_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__uint16_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandAu16FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__uint16_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__uint32_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandAu32FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__uint32_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__uint64_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandAu64FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__uint64_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__double__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandAdFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__double__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__float__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandAfFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__float__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__uint8_t_ptr__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandAu8pFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__uint8_t_ptr__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__std_string__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandASsFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__std_string__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__void_ptr__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandAvptrFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__void_ptr__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__std_vector_char__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandASvcFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__std_vector_char__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__std_vector_std_string__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandASv_std_stringFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__std_vector_std_string__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__bool8_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandAb8FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__bool8_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__char_ptr__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandAcptrFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__char_ptr__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__as__InfoCommandInfo__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandA_CINFOFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__as__InfoCommandInfo__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackOnDemand__from__Eur_NewBufferData = errorCheck(
    dll.euECameraBufferGetInfo_CallbackOnDemandFEur_NewBufferData,
    "Eur_ECameraBufferGetInfo_CallbackOnDemand__from__Eur_NewBufferData",
)
Eur_ECameraBufferPush_CallbackSingleThread__from__Eur_NewBufferData = errorCheck(
    dll.euECameraBufferPush_CallbackSingleThreadFEur_NewBufferData,
    "Eur_ECameraBufferPush_CallbackSingleThread__from__Eur_NewBufferData",
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__size_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackSingleThreadAsFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__size_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__int8_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackSingleThreadAi8FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__int8_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__int16_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackSingleThreadAi16FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__int16_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__int32_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackSingleThreadAi32FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__int32_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__int64_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackSingleThreadAi64FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__int64_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__uint8_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackSingleThreadAu8FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__uint8_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__uint16_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackSingleThreadAu16FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__uint16_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__uint32_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackSingleThreadAu32FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__uint32_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__uint64_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackSingleThreadAu64FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__uint64_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__double__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackSingleThreadAdFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__double__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__float__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackSingleThreadAfFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__float__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__uint8_t_ptr__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackSingleThreadAu8pFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__uint8_t_ptr__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__std_string__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackSingleThreadASsFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__std_string__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__void_ptr__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackSingleThreadAvptrFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__void_ptr__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__std_vector_char__from__Eur_NewBufferData__BUFFER_INFO_CMD = (
    errorCheck(
        dll.euECameraBufferGetInfo_CallbackSingleThreadASvcFEur_NewBufferDataBIC,
        "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__std_vector_char__from__Eur_NewBufferData__BUFFER_INFO_CMD",
    )
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__std_vector_std_string__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackSingleThreadASv_std_stringFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__std_vector_std_string__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__bool8_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackSingleThreadAb8FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__bool8_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__char_ptr__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackSingleThreadAcptrFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__char_ptr__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__as__InfoCommandInfo__from__Eur_NewBufferData__BUFFER_INFO_CMD = (
    errorCheck(
        dll.euECameraBufferGetInfo_CallbackSingleThreadA_CINFOFEur_NewBufferDataBIC,
        "Eur_ECameraBufferGetInfo_CallbackSingleThread__as__InfoCommandInfo__from__Eur_NewBufferData__BUFFER_INFO_CMD",
    )
)
Eur_ECameraBufferGetInfo_CallbackSingleThread__from__Eur_NewBufferData = errorCheck(
    dll.euECameraBufferGetInfo_CallbackSingleThreadFEur_NewBufferData,
    "Eur_ECameraBufferGetInfo_CallbackSingleThread__from__Eur_NewBufferData",
)
Eur_ECameraBufferPush_CallbackMultiThread__from__Eur_NewBufferData = errorCheck(
    dll.euECameraBufferPush_CallbackMultiThreadFEur_NewBufferData,
    "Eur_ECameraBufferPush_CallbackMultiThread__from__Eur_NewBufferData",
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__size_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackMultiThreadAsFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__size_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__int8_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackMultiThreadAi8FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__int8_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__int16_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackMultiThreadAi16FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__int16_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__int32_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackMultiThreadAi32FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__int32_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__int64_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackMultiThreadAi64FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__int64_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__uint8_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackMultiThreadAu8FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__uint8_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__uint16_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackMultiThreadAu16FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__uint16_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__uint32_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackMultiThreadAu32FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__uint32_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__uint64_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackMultiThreadAu64FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__uint64_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__double__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackMultiThreadAdFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__double__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__float__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackMultiThreadAfFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__float__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__uint8_t_ptr__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackMultiThreadAu8pFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__uint8_t_ptr__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__std_string__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackMultiThreadASsFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__std_string__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__void_ptr__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackMultiThreadAvptrFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__void_ptr__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__std_vector_char__from__Eur_NewBufferData__BUFFER_INFO_CMD = (
    errorCheck(
        dll.euECameraBufferGetInfo_CallbackMultiThreadASvcFEur_NewBufferDataBIC,
        "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__std_vector_char__from__Eur_NewBufferData__BUFFER_INFO_CMD",
    )
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__std_vector_std_string__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackMultiThreadASv_std_stringFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__std_vector_std_string__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__bool8_t__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackMultiThreadAb8FEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__bool8_t__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__char_ptr__from__Eur_NewBufferData__BUFFER_INFO_CMD = errorCheck(
    dll.euECameraBufferGetInfo_CallbackMultiThreadAcptrFEur_NewBufferDataBIC,
    "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__char_ptr__from__Eur_NewBufferData__BUFFER_INFO_CMD",
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__as__InfoCommandInfo__from__Eur_NewBufferData__BUFFER_INFO_CMD = (
    errorCheck(
        dll.euECameraBufferGetInfo_CallbackMultiThreadA_CINFOFEur_NewBufferDataBIC,
        "Eur_ECameraBufferGetInfo_CallbackMultiThread__as__InfoCommandInfo__from__Eur_NewBufferData__BUFFER_INFO_CMD",
    )
)
Eur_ECameraBufferGetInfo_CallbackMultiThread__from__Eur_NewBufferData = errorCheck(
    dll.euECameraBufferGetInfo_CallbackMultiThreadFEur_NewBufferData,
    "Eur_ECameraBufferGetInfo_CallbackMultiThread__from__Eur_NewBufferData",
)
Eur_action_GenApiActionyBuilder_destroy = errorCheck(
    dll.euaction_GenApiActionyBuilder_destroy, "Eur_action_GenApiActionyBuilder_destroy"
)
Eur_action_GenApiActionBuilder_destroy = errorCheck(
    dll.euaction_GenApiActionBuilder_destroy, "Eur_action_GenApiActionBuilder_destroy"
)
Eur_action_GenApiActionBuilder_string = errorCheck(
    dll.euaction_GenApiActionBuilder_string, "Eur_action_GenApiActionBuilder_string"
)
Eur_query_GenApiQueryBuilder_destroy = errorCheck(
    dll.euquery_GenApiQueryBuilder_destroy, "Eur_query_GenApiQueryBuilder_destroy"
)
Eur_query_GenApiQueryBuilder_string = errorCheck(
    dll.euquery_GenApiQueryBuilder_string, "Eur_query_GenApiQueryBuilder_string"
)
Eur_query_GenApiQueryBuilder_glob__from__const_char_p = errorCheck(
    dll.euquery_GenApiQueryBuilder_globFccp, "Eur_query_GenApiQueryBuilder_glob__from__const_char_p"
)
Eur_query_GenApiQueryBuilder_regex__from__const_char_p = errorCheck(
    dll.euquery_GenApiQueryBuilder_regexFccp, "Eur_query_GenApiQueryBuilder_regex__from__const_char_p"
)
Eur_getEuresysCtiPath = errorCheck(dll.eugetEuresysCtiPath, "Eur_getEuresysCtiPath")
Eur_BufferInfo_destroy = errorCheck(dll.euBufferInfo_destroy, "Eur_BufferInfo_destroy")
from_box_Eur_BufferInfo__from__cBufferInfo_p = errorCheck(
    dll.eufrom_box_Eur_BufferInfoFcBufferInfo_p, "from_box_Eur_BufferInfo__from__cBufferInfo_p"
)
std_string_create = errorCheck(dll.eustd_string_create, "std_string_create")
std_string_destroy = errorCheck(dll.eustd_string_destroy, "std_string_destroy")
std_const_string_create = errorCheck(dll.eustd_const_string_create, "std_const_string_create")
std_const_string_destroy = errorCheck(dll.eustd_const_string_destroy, "std_const_string_destroy")
std_string_c_str = errorCheck(dll.eustd_string_c_str, "std_string_c_str")
std_string_assign__from__const_char_p = errorCheck(dll.eustd_string_assignFccp, "std_string_assign__from__const_char_p")
to_box_std_string__from__const_char_p__size_t = errorCheck(
    dll.euto_box_std_stringFccps, "to_box_std_string__from__const_char_p__size_t"
)
from_box_std_string__from__const_char_pp__size_t_p = errorCheck(
    dll.eufrom_box_std_stringFccppsp, "from_box_std_string__from__const_char_pp__size_t_p"
)
std_string_assign_operator__from__std_string = errorCheck(
    dll.eustd_string_assign_operatorFSs, "std_string_assign_operator__from__std_string"
)
std_vector_char_create = errorCheck(dll.eustd_vector_char_create, "std_vector_char_create")
std_vector_char_size = errorCheck(dll.eustd_vector_char_size, "std_vector_char_size")
std_vector_char_destroy = errorCheck(dll.eustd_vector_char_destroy, "std_vector_char_destroy")
std_vector_char_at__from__size_t = errorCheck(dll.eustd_vector_char_atFs, "std_vector_char_at__from__size_t")
std_vector_char_push_back__from__char = errorCheck(
    dll.eustd_vector_char_push_backFc, "std_vector_char_push_back__from__char"
)
to_box_std_vector_char__from__const_char_p__size_t = errorCheck(
    dll.euto_box_std_vector_charFccps, "to_box_std_vector_char__from__const_char_p__size_t"
)
from_box_std_vector_char__from__const_char_pp__size_t_p = errorCheck(
    dll.eufrom_box_std_vector_charFccppsp, "from_box_std_vector_char__from__const_char_pp__size_t_p"
)
std_vector_std_string_create = errorCheck(dll.eustd_vector_std_string_create, "std_vector_std_string_create")
std_vector_std_string_size = errorCheck(dll.eustd_vector_std_string_size, "std_vector_std_string_size")
std_vector_std_string_destroy = errorCheck(dll.eustd_vector_std_string_destroy, "std_vector_std_string_destroy")
std_vector_std_string_at__from__size_t = errorCheck(
    dll.eustd_vector_std_string_atFs, "std_vector_std_string_at__from__size_t"
)
std_vector_EURESYS_EVENT_GET_DATA_ENTRY_create = errorCheck(
    dll.eustd_vector_EURESYS_EVENT_GET_DATA_ENTRY_create, "std_vector_EURESYS_EVENT_GET_DATA_ENTRY_create"
)
std_vector_EURESYS_EVENT_GET_DATA_ENTRY_size = errorCheck(
    dll.eustd_vector_EURESYS_EVENT_GET_DATA_ENTRY_size, "std_vector_EURESYS_EVENT_GET_DATA_ENTRY_size"
)
std_vector_EURESYS_EVENT_GET_DATA_ENTRY_destroy = errorCheck(
    dll.eustd_vector_EURESYS_EVENT_GET_DATA_ENTRY_destroy, "std_vector_EURESYS_EVENT_GET_DATA_ENTRY_destroy"
)
std_vector_EURESYS_EVENT_GET_DATA_ENTRY_at__from__size_t = errorCheck(
    dll.eustd_vector_EURESYS_EVENT_GET_DATA_ENTRY_atFs, "std_vector_EURESYS_EVENT_GET_DATA_ENTRY_at__from__size_t"
)
std_vector_EURESYS_EVENT_GET_DATA_ENTRY_push_back__from__EURESYS_EVENT_GET_DATA_ENTRY = errorCheck(
    dll.eustd_vector_EEGDE_push_backFEEGDE,
    "std_vector_EURESYS_EVENT_GET_DATA_ENTRY_push_back__from__EURESYS_EVENT_GET_DATA_ENTRY",
)
to_box_std_vector_EURESYS_EVENT_GET_DATA_ENTRY__from__const_EURESYS_EVENT_GET_DATA_ENTRY_p__size_t = errorCheck(
    dll.euto_box_std_vector_EURESYS_EVENT_GET_DATA_ENTRYFconst_EURESYS_EVENT_GET_DATA_ENTRY_ps,
    "to_box_std_vector_EURESYS_EVENT_GET_DATA_ENTRY__from__const_EURESYS_EVENT_GET_DATA_ENTRY_p__size_t",
)
from_box_std_vector_EURESYS_EVENT_GET_DATA_ENTRY__from__const_EURESYS_EVENT_GET_DATA_ENTRY_pp__size_t_p = errorCheck(
    dll.eufrom_box_std_vector_EURESYS_EVENT_GET_DATA_ENTRYFconst_EURESYS_EVENT_GET_DATA_ENTRY_ppsp,
    "from_box_std_vector_EURESYS_EVENT_GET_DATA_ENTRY__from__const_EURESYS_EVENT_GET_DATA_ENTRY_pp__size_t_p",
)
std_vector_BUFFER_HANDLE_create = errorCheck(dll.eustd_vector_BUFFER_HANDLE_create, "std_vector_BUFFER_HANDLE_create")
std_vector_BUFFER_HANDLE_size = errorCheck(dll.eustd_vector_BUFFER_HANDLE_size, "std_vector_BUFFER_HANDLE_size")
std_vector_BUFFER_HANDLE_destroy = errorCheck(
    dll.eustd_vector_BUFFER_HANDLE_destroy, "std_vector_BUFFER_HANDLE_destroy"
)
std_vector_BUFFER_HANDLE_at__from__size_t = errorCheck(
    dll.eustd_vector_BUFFER_HANDLE_atFs, "std_vector_BUFFER_HANDLE_at__from__size_t"
)
std_vector_BUFFER_HANDLE_push_back__from__BUFFER_HANDLE = errorCheck(
    dll.eustd_vector_BH_push_backFBH, "std_vector_BUFFER_HANDLE_push_back__from__BUFFER_HANDLE"
)
to_box_std_vector_BUFFER_HANDLE__from__const_BUFFER_HANDLE_p__size_t = errorCheck(
    dll.euto_box_std_vector_BUFFER_HANDLEFconst_BUFFER_HANDLE_ps,
    "to_box_std_vector_BUFFER_HANDLE__from__const_BUFFER_HANDLE_p__size_t",
)
from_box_std_vector_BUFFER_HANDLE__from__const_BUFFER_HANDLE_pp__size_t_p = errorCheck(
    dll.eufrom_box_std_vector_BUFFER_HANDLEFconst_BUFFER_HANDLE_ppsp,
    "from_box_std_vector_BUFFER_HANDLE__from__const_BUFFER_HANDLE_pp__size_t_p",
)
std_vector_PORT_REGISTER_STACK_ENTRY_create = errorCheck(
    dll.eustd_vector_PORT_REGISTER_STACK_ENTRY_create, "std_vector_PORT_REGISTER_STACK_ENTRY_create"
)
std_vector_PORT_REGISTER_STACK_ENTRY_size = errorCheck(
    dll.eustd_vector_PORT_REGISTER_STACK_ENTRY_size, "std_vector_PORT_REGISTER_STACK_ENTRY_size"
)
std_vector_PORT_REGISTER_STACK_ENTRY_destroy = errorCheck(
    dll.eustd_vector_PORT_REGISTER_STACK_ENTRY_destroy, "std_vector_PORT_REGISTER_STACK_ENTRY_destroy"
)
std_vector_PORT_REGISTER_STACK_ENTRY_at__from__size_t = errorCheck(
    dll.eustd_vector_PORT_REGISTER_STACK_ENTRY_atFs, "std_vector_PORT_REGISTER_STACK_ENTRY_at__from__size_t"
)
std_vector_PORT_REGISTER_STACK_ENTRY_push_back__from__PORT_REGISTER_STACK_ENTRY = errorCheck(
    dll.eustd_vector_PRSE_push_backFPRSE,
    "std_vector_PORT_REGISTER_STACK_ENTRY_push_back__from__PORT_REGISTER_STACK_ENTRY",
)
to_box_std_vector_PORT_REGISTER_STACK_ENTRY__from__const_PORT_REGISTER_STACK_ENTRY_p__size_t = errorCheck(
    dll.euto_box_std_vector_PORT_REGISTER_STACK_ENTRYFconst_PORT_REGISTER_STACK_ENTRY_ps,
    "to_box_std_vector_PORT_REGISTER_STACK_ENTRY__from__const_PORT_REGISTER_STACK_ENTRY_p__size_t",
)
from_box_std_vector_PORT_REGISTER_STACK_ENTRY__from__const_PORT_REGISTER_STACK_ENTRY_pp__size_t_p = errorCheck(
    dll.eufrom_box_std_vector_PORT_REGISTER_STACK_ENTRYFconst_PORT_REGISTER_STACK_ENTRY_ppsp,
    "from_box_std_vector_PORT_REGISTER_STACK_ENTRY__from__const_PORT_REGISTER_STACK_ENTRY_pp__size_t_p",
)
std_vector_PORT_HANDLE_create = errorCheck(dll.eustd_vector_PORT_HANDLE_create, "std_vector_PORT_HANDLE_create")
std_vector_PORT_HANDLE_size = errorCheck(dll.eustd_vector_PORT_HANDLE_size, "std_vector_PORT_HANDLE_size")
std_vector_PORT_HANDLE_destroy = errorCheck(dll.eustd_vector_PORT_HANDLE_destroy, "std_vector_PORT_HANDLE_destroy")
std_vector_PORT_HANDLE_at__from__size_t = errorCheck(
    dll.eustd_vector_PORT_HANDLE_atFs, "std_vector_PORT_HANDLE_at__from__size_t"
)
std_vector_PORT_HANDLE_push_back__from__PORT_HANDLE = errorCheck(
    dll.eustd_vector_PH_push_backFPH, "std_vector_PORT_HANDLE_push_back__from__PORT_HANDLE"
)
to_box_std_vector_PORT_HANDLE__from__const_PORT_HANDLE_p__size_t = errorCheck(
    dll.euto_box_std_vector_PORT_HANDLEFconst_PORT_HANDLE_ps,
    "to_box_std_vector_PORT_HANDLE__from__const_PORT_HANDLE_p__size_t",
)
from_box_std_vector_PORT_HANDLE__from__const_PORT_HANDLE_pp__size_t_p = errorCheck(
    dll.eufrom_box_std_vector_PORT_HANDLEFconst_PORT_HANDLE_ppsp,
    "from_box_std_vector_PORT_HANDLE__from__const_PORT_HANDLE_pp__size_t_p",
)
std_map_std_string_std_string_create = errorCheck(
    dll.eustd_map_std_string_std_string_create, "std_map_std_string_std_string_create"
)
std_map_std_string_std_string_destroy = errorCheck(
    dll.eustd_map_std_string_std_string_destroy, "std_map_std_string_std_string_destroy"
)
std_map_std_string_std_string_size = errorCheck(
    dll.eustd_map_std_string_std_string_size, "std_map_std_string_std_string_size"
)
std_map_std_string_std_string_at__from__std_map_std_string_std_string__std_string = errorCheck(
    dll.eustd_map_std_string_std_string_atFSm_std_string_std_stringSs,
    "std_map_std_string_std_string_at__from__std_map_std_string_std_string__std_string",
)
std_map_std_string_std_string_at__from__std_string = errorCheck(
    dll.eustd_map_std_string_std_string_atFSs, "std_map_std_string_std_string_at__from__std_string"
)
std_map_std_string_std_string_at__from__size_t__std_string_p__std_string_p = errorCheck(
    dll.eustd_map_std_string_std_string_atFsSs_pSs_p,
    "std_map_std_string_std_string_at__from__size_t__std_string_p__std_string_p",
)
std_runtime_error_create__from__const_char_p = errorCheck(
    dll.eustd_runtime_error_createFccp, "std_runtime_error_create__from__const_char_p"
)
std_runtime_error_destroy = errorCheck(dll.eustd_runtime_error_destroy, "std_runtime_error_destroy")
std_runtime_error_what = errorCheck(dll.eustd_runtime_error_what, "std_runtime_error_what")
std_logic_error_create__from__const_char_p = errorCheck(
    dll.eustd_logic_error_createFccp, "std_logic_error_create__from__const_char_p"
)
std_logic_error_destroy = errorCheck(dll.eustd_logic_error_destroy, "std_logic_error_destroy")
std_logic_error_what = errorCheck(dll.eustd_logic_error_what, "std_logic_error_what")
std_exception_create__from__const_char_p = errorCheck(
    dll.eustd_exception_createFccp, "std_exception_create__from__const_char_p"
)
std_exception_destroy = errorCheck(dll.eustd_exception_destroy, "std_exception_destroy")
std_exception_what = errorCheck(dll.eustd_exception_what, "std_exception_what")
from_box_Eur_BufferIndexRange__from__size_t_p__size_t_p__bool8_t_p = errorCheck(
    dll.eufrom_box_Eur_BufferIndexRangeFspspb8_p, "from_box_Eur_BufferIndexRange__from__size_t_p__size_t_p__bool8_t_p"
)
Eur_NewBufferData__as__Euresys_NewBufferData = errorCheck(
    dll.euNewBufferDataANewBufferData, "Eur_NewBufferData__as__Euresys_NewBufferData"
)
Eur_IoToolboxData__as__Euresys_IoToolboxData = errorCheck(
    dll.euIoToolboxDataAIoToolboxData, "Eur_IoToolboxData__as__Euresys_IoToolboxData"
)
Eur_CicData__as__Euresys_CicData = errorCheck(dll.euCicDataACicData, "Eur_CicData__as__Euresys_CicData")
Eur_DataStreamData__as__Euresys_DataStreamData = errorCheck(
    dll.euDataStreamDataADataStreamData, "Eur_DataStreamData__as__Euresys_DataStreamData"
)
Eur_CxpInterfaceData__as__Euresys_CxpInterfaceData = errorCheck(
    dll.euCxpInterfaceDataACxpInterfaceData, "Eur_CxpInterfaceData__as__Euresys_CxpInterfaceData"
)
Eur_DeviceErrorData__as__Euresys_DeviceErrorData = errorCheck(
    dll.euDeviceErrorDataADeviceErrorData, "Eur_DeviceErrorData__as__Euresys_DeviceErrorData"
)
Eur_CxpDeviceData__as__Euresys_CxpDeviceData = errorCheck(
    dll.euCxpDeviceDataACxpDeviceData, "Eur_CxpDeviceData__as__Euresys_CxpDeviceData"
)
Eur_RemoteDeviceData__as__Euresys_RemoteDeviceData = errorCheck(
    dll.euRemoteDeviceDataARemoteDeviceData, "Eur_RemoteDeviceData__as__Euresys_RemoteDeviceData"
)
to_box_Eur_NewBufferData__from__const_struct_Euresys_NewBufferData_s_p = errorCheck(
    dll.euto_box_Eur_NewBufferDataFcst_NewBufferData_s_p,
    "to_box_Eur_NewBufferData__from__const_struct_Euresys_NewBufferData_s_p",
)
to_box_Eur_EGrabberInfo__from__cEGrabberInfo = errorCheck(
    dll.euto_box_EurEGInfoFcEGrabberInfo, "to_box_Eur_EGrabberInfo__from__cEGrabberInfo"
)
from_box_Eur_EGrabberInfo__from__cEGrabberInfo_p = errorCheck(
    dll.eufrom_box_EurEGInfoFcEGrabberInfo_p, "from_box_Eur_EGrabberInfo__from__cEGrabberInfo_p"
)
to_box_Eur_EGrabberInfo__from__cEGrabberInfoExt1_p = errorCheck(
    dll.euto_box_EurEGInfoFcEGrabberInfoExt1_p, "to_box_Eur_EGrabberInfo__from__cEGrabberInfoExt1_p"
)
from_box_Eur_EGrabberInfo__from__cEGrabberInfoExt1_p = errorCheck(
    dll.eufrom_box_EurEGInfoFcEGrabberInfoExt1_p, "from_box_Eur_EGrabberInfo__from__cEGrabberInfoExt1_p"
)
to_box_Eur_EGrabberInfo__from__cEGrabberInfoExt2_p = errorCheck(
    dll.euto_box_EurEGInfoFcEGrabberInfoExt2_p, "to_box_Eur_EGrabberInfo__from__cEGrabberInfoExt2_p"
)
from_box_Eur_EGrabberInfo__from__cEGrabberInfoExt2_p = errorCheck(
    dll.eufrom_box_EurEGInfoFcEGrabberInfoExt2_p, "from_box_Eur_EGrabberInfo__from__cEGrabberInfoExt2_p"
)
Eur_Internal_lastError_get__as__Eur_genapi_error = errorCheck(
    dll.euInternal_lastError_getAEur_genapi_error, "Eur_Internal_lastError_get__as__Eur_genapi_error"
)
Eur_Internal_lastCallbackError_set__from__Eur_genapi_error = errorCheck(
    dll.euInternal_lastCallbackError_setFEur_genapi_error, "Eur_Internal_lastCallbackError_set__from__Eur_genapi_error"
)
Eur_Internal_lastError_get__as__Eur_cti_loading_error = errorCheck(
    dll.euInternal_lastError_getAEur_cti_loading_error, "Eur_Internal_lastError_get__as__Eur_cti_loading_error"
)
Eur_Internal_lastCallbackError_set__from__Eur_cti_loading_error = errorCheck(
    dll.euInternal_lastCallbackError_setFEur_cti_loading_error,
    "Eur_Internal_lastCallbackError_set__from__Eur_cti_loading_error",
)
Eur_Internal_lastError_get__as__Eur_missing_gentl_symbol = errorCheck(
    dll.euInternal_lastError_getAEur_missing_gentl_symbol, "Eur_Internal_lastError_get__as__Eur_missing_gentl_symbol"
)
Eur_Internal_lastCallbackError_set__from__Eur_missing_gentl_symbol = errorCheck(
    dll.euInternal_lastCallbackError_setFEur_missing_gentl_symbol,
    "Eur_Internal_lastCallbackError_set__from__Eur_missing_gentl_symbol",
)
Eur_Internal_lastError_get__as__Eur_unexpected_data_type = errorCheck(
    dll.euInternal_lastError_getAEur_unexpected_data_type, "Eur_Internal_lastError_get__as__Eur_unexpected_data_type"
)
Eur_Internal_lastCallbackError_set__from__Eur_unexpected_data_type = errorCheck(
    dll.euInternal_lastCallbackError_setFEur_unexpected_data_type,
    "Eur_Internal_lastCallbackError_set__from__Eur_unexpected_data_type",
)
Eur_Internal_lastError_get__as__Eur_unexpected_data_size = errorCheck(
    dll.euInternal_lastError_getAEur_unexpected_data_size, "Eur_Internal_lastError_get__as__Eur_unexpected_data_size"
)
Eur_Internal_lastCallbackError_set__from__Eur_unexpected_data_size = errorCheck(
    dll.euInternal_lastCallbackError_setFEur_unexpected_data_size,
    "Eur_Internal_lastCallbackError_set__from__Eur_unexpected_data_size",
)
Eur_Internal_lastError_get__as__Eur_client_error = errorCheck(
    dll.euInternal_lastError_getAEur_client_error, "Eur_Internal_lastError_get__as__Eur_client_error"
)
Eur_Internal_lastCallbackError_set__from__Eur_client_error = errorCheck(
    dll.euInternal_lastCallbackError_setFEur_client_error, "Eur_Internal_lastCallbackError_set__from__Eur_client_error"
)
Eur_Internal_lastError_get__as__Eur_gentl_error = errorCheck(
    dll.euInternal_lastError_getAEur_gentl_error, "Eur_Internal_lastError_get__as__Eur_gentl_error"
)
Eur_Internal_lastCallbackError_set__from__Eur_gentl_error = errorCheck(
    dll.euInternal_lastCallbackError_setFEur_gentl_error, "Eur_Internal_lastCallbackError_set__from__Eur_gentl_error"
)
Eur_Internal_lastError_get__as__Eur_thread_error = errorCheck(
    dll.euInternal_lastError_getAEur_thread_error, "Eur_Internal_lastError_get__as__Eur_thread_error"
)
Eur_Internal_lastCallbackError_set__from__Eur_thread_error = errorCheck(
    dll.euInternal_lastCallbackError_setFEur_thread_error, "Eur_Internal_lastCallbackError_set__from__Eur_thread_error"
)
Eur_Internal_lastError_get__as__Eur_internal_error = errorCheck(
    dll.euInternal_lastError_getAEur_internal_error, "Eur_Internal_lastError_get__as__Eur_internal_error"
)
Eur_Internal_lastCallbackError_set__from__Eur_internal_error = errorCheck(
    dll.euInternal_lastCallbackError_setFEur_internal_error,
    "Eur_Internal_lastCallbackError_set__from__Eur_internal_error",
)
Eur_Internal_lastError_get__as__Eur_not_allowed = errorCheck(
    dll.euInternal_lastError_getAEur_not_allowed, "Eur_Internal_lastError_get__as__Eur_not_allowed"
)
Eur_Internal_lastCallbackError_set__from__Eur_not_allowed = errorCheck(
    dll.euInternal_lastCallbackError_setFEur_not_allowed, "Eur_Internal_lastCallbackError_set__from__Eur_not_allowed"
)
Eur_Internal_lastError_get__as__std_runtime_error = errorCheck(
    dll.euInternal_lastError_getAstd_runtime_error, "Eur_Internal_lastError_get__as__std_runtime_error"
)
Eur_Internal_lastCallbackError_set__from__std_runtime_error = errorCheck(
    dll.euInternal_lastCallbackError_setFstd_runtime_error,
    "Eur_Internal_lastCallbackError_set__from__std_runtime_error",
)
Eur_Internal_lastError_get__as__std_logic_error = errorCheck(
    dll.euInternal_lastError_getAstd_logic_error, "Eur_Internal_lastError_get__as__std_logic_error"
)
Eur_Internal_lastCallbackError_set__from__std_logic_error = errorCheck(
    dll.euInternal_lastCallbackError_setFstd_logic_error, "Eur_Internal_lastCallbackError_set__from__std_logic_error"
)
Eur_Internal_lastError_get__as__std_exception = errorCheck(
    dll.euInternal_lastError_getAstd_exception, "Eur_Internal_lastError_get__as__std_exception"
)
Eur_Internal_lastCallbackError_set__from__std_exception = errorCheck(
    dll.euInternal_lastCallbackError_setFstd_exception, "Eur_Internal_lastCallbackError_set__from__std_exception"
)
Eur_Internal_lastError_getCode = errorCheck(dll.euInternal_lastError_getCode, "Eur_Internal_lastError_getCode")
Eur_Internal_lastCallbackError_setCallbackCriticalError = errorCheck(
    dll.euInternal_lastCallbackError_setCallbackCriticalError, "Eur_Internal_lastCallbackError_setCallbackCriticalError"
)
from_box_Eur_cti_loading_error_path = errorCheck(
    dll.eufrom_box_Eur_cti_loading_error_path, "from_box_Eur_cti_loading_error_path"
)
from_box_Eur_missing_gentl_symbol_path = errorCheck(
    dll.eufrom_box_Eur_missing_gentl_symbol_path, "from_box_Eur_missing_gentl_symbol_path"
)
from_box_Eur_missing_gentl_symbol_symbol = errorCheck(
    dll.eufrom_box_Eur_missing_gentl_symbol_symbol, "from_box_Eur_missing_gentl_symbol_symbol"
)
from_box_Eur_unexpected_data_type = errorCheck(
    dll.eufrom_box_Eur_unexpected_data_type, "from_box_Eur_unexpected_data_type"
)
from_box_Eur_unexpected_data_size__from__size_t_p__size_t_p = errorCheck(
    dll.eufrom_box_Eur_unexpected_data_sizeFspsp, "from_box_Eur_unexpected_data_size__from__size_t_p__size_t_p"
)
from_box_Eur_gentl_error_gc_err = errorCheck(dll.eufrom_box_Eur_gentl_error_gc_err, "from_box_Eur_gentl_error_gc_err")
from_box_Eur_gentl_error_description = errorCheck(
    dll.eufrom_box_Eur_gentl_error_description, "from_box_Eur_gentl_error_description"
)
from_box_Eur_genapi_error = errorCheck(dll.eufrom_box_Eur_genapi_error, "from_box_Eur_genapi_error")
Eur_genapi_error_string_parameter__as__std_string__from__size_t = errorCheck(
    dll.eugenapi_error_string_parameterASsFs, "Eur_genapi_error_string_parameter__as__std_string__from__size_t"
)
checkAllBoxedTypeCount = errorCheck(dll.eucheckAllBoxedTypeCount, "checkAllBoxedTypeCount")


# Structures
class Euresys_NewBufferData(ct.Structure):
    _fields_ = [
        ("dsh", ct.c_void_p),
        ("bh", ct.c_void_p),
        ("userPointer", ct.c_void_p),
        ("timestamp", ct.c_uint64),
        ("_owner", ct.c_void_p),
        ("_ownerType", ct.c_void_p),
        ("_bufferId", ct.c_void_p),
    ]


class Euresys_IoToolboxData(ct.Structure):
    _fields_ = [
        ("timestamp", ct.c_uint64),
        ("numid", ct.c_uint32),
        ("context1", ct.c_uint32),
        ("context2", ct.c_uint32),
        ("context3", ct.c_uint32),
    ]


class Euresys_CicData(ct.Structure):
    _fields_ = [
        ("timestamp", ct.c_uint64),
        ("numid", ct.c_uint32),
        ("context1", ct.c_uint32),
        ("context2", ct.c_uint32),
        ("context3", ct.c_uint32),
    ]


class Euresys_DataStreamData(ct.Structure):
    _fields_ = [
        ("timestamp", ct.c_uint64),
        ("numid", ct.c_uint32),
        ("context1", ct.c_uint32),
        ("context2", ct.c_uint32),
        ("context3", ct.c_uint32),
    ]


class Euresys_CxpInterfaceData(ct.Structure):
    _fields_ = [
        ("timestamp", ct.c_uint64),
        ("numid", ct.c_uint32),
        ("context1", ct.c_uint32),
        ("context2", ct.c_uint32),
        ("context3", ct.c_uint32),
    ]


class Euresys_DeviceErrorData(ct.Structure):
    _fields_ = [
        ("timestamp", ct.c_uint64),
        ("numid", ct.c_uint32),
        ("context1", ct.c_uint32),
        ("context2", ct.c_uint32),
        ("context3", ct.c_uint32),
    ]


class Euresys_CxpDeviceData(ct.Structure):
    _fields_ = [
        ("timestamp", ct.c_uint64),
        ("numid", ct.c_uint32),
        ("context1", ct.c_uint32),
        ("context2", ct.c_uint32),
        ("context3", ct.c_uint32),
    ]


class Euresys_RemoteDeviceData(ct.Structure):
    _fields_ = [
        ("timestamp", ct.c_uint64),
        ("eventNs", ct.c_uint32),
        ("eventId", ct.c_uint32),
        ("size", ct.c_uint32),
        ("data", ct.c_ubyte * 1012),
    ]


# Callbacks
Euresys_NewBufferEventCallback = ct.CFUNCTYPE(
    None, ct.POINTER(Eur_EGrabberBase), ct.POINTER(Euresys_NewBufferData), ct.c_void_p
)
Euresys_IoToolboxEventCallback = ct.CFUNCTYPE(
    None, ct.POINTER(Eur_EGrabberBase), ct.POINTER(Euresys_IoToolboxData), ct.c_void_p
)
Euresys_CicEventCallback = ct.CFUNCTYPE(None, ct.POINTER(Eur_EGrabberBase), ct.POINTER(Euresys_CicData), ct.c_void_p)
Euresys_DataStreamEventCallback = ct.CFUNCTYPE(
    None, ct.POINTER(Eur_EGrabberBase), ct.POINTER(Euresys_DataStreamData), ct.c_void_p
)
Euresys_CxpInterfaceEventCallback = ct.CFUNCTYPE(
    None, ct.POINTER(Eur_EGrabberBase), ct.POINTER(Euresys_CxpInterfaceData), ct.c_void_p
)
Euresys_DeviceErrorEventCallback = ct.CFUNCTYPE(
    None, ct.POINTER(Eur_EGrabberBase), ct.POINTER(Euresys_DeviceErrorData), ct.c_void_p
)
Euresys_CxpDeviceEventCallback = ct.CFUNCTYPE(
    None, ct.POINTER(Eur_EGrabberBase), ct.POINTER(Euresys_CxpDeviceData), ct.c_void_p
)
Euresys_RemoteDeviceEventCallback = ct.CFUNCTYPE(
    None, ct.POINTER(Eur_EGrabberBase), ct.POINTER(Euresys_RemoteDeviceData), ct.c_void_p
)

# All events
Euresys_AllEventNames = [
    "NewBufferData",
    "IoToolboxData",
    "CicData",
    "DataStreamData",
    "CxpInterfaceData",
    "DeviceErrorData",
    "CxpDeviceData",
    "RemoteDeviceData",
]
