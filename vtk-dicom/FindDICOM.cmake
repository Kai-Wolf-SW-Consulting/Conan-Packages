include(FindPackageHandleStandardArgs)

if(NOT DICOM_LIBRARIES AND NOT vtkDICOM)

  find_path(DICOM_INCLUDE_DIR
    NAMES vtkDICOMConfig.h
    PATHS ${CMAKE_CURRENT_LIST_DIR}/include)

  find_library(DICOM_LIBRARY
    NAMES
      ${CMAKE_STATIC_LIBRARY_PREFIX}vtkDICOM-8.2.0${CMAKE_STATIC_LIBRARY_SUFFIX}
    PATHS
      ${CMAKE_CURRENT_LIST_DIR}/lib ${CMAKE_CURRENT_LIST_DIR}/bin)


  set(DICOM_VERSION "0.8.10")
  set(DICOM_VERSION_STRING "0.8.10")
  set(DICOM_VERSION_MAJOR 0)
  set(DICOM_VERSION_MINOR 8)
  set(DICOM_VERSION_PATCH 10)

  find_package_handle_standard_args(DICOM
    DEFAULT_MSG DICOM_LIBRARY DICOM_INCLUDE_DIR)

  if(DICOM_FOUND)
    set(DICOM_LIBRARIES ${DICOM_LIBRARY})
    set(DICOM_INCLUDE_DIRS ${DICOM_INCLUDE_DIR})

    set(_iface_libs "vtkCommonCore;vtkCommonMisc;vtkCommonDataModel;vtkImagingCore;vtkIOCore;vtkIOImage;vtkzlib")
    if(APPLE)
      list(APPEND _iface_libs "sqlite3")
    endif()

    add_library(vtkDICOM STATIC IMPORTED)
    set_target_properties(vtkDICOM PROPERTIES
      IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE CXX
      INTERFACE_INCLUDE_DIRECTORIES ${DICOM_INCLUDE_DIRS}
      IMPORTED_LINK_INTERFACE_LIBRARIES "${_iface_libs}"
      IMPORTED_LOCATION ${DICOM_LIBRARY})
  else()
    if(DICOM_FIND_REQUIRED)
      message(FATAL_ERROR "Could not find DICOM.")
    endif()
  endif()
endif()
