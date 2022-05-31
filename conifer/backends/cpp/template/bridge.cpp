#include "conifer.h"
#include "ap_fixed.h"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

// conifer insert typedef

namespace py = pybind11;
PYBIND11_MODULE(conifer_bridge, m){
  py::class_<conifer::BDT<T,U,false>>(m, "BDT")
      .def(py::init<const std::string &>())
      .def("decision_function", &conifer::BDT<T,U,false>::_decision_function_double);
}